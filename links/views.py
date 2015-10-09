# Create your views here.
import re, urlmarker, StringIO
#from request.models import Request
from django.core.files.uploadedfile import InMemoryUploadedFile
from scraper import read_image
from .models import Link, Vote, UserProfile, UserSettings
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from .forms import UserProfileForm, LinkForm, VoteForm, ScoreHelpForm, UserSettingsForm, HelpForm, WhoseOnlineForm, clean_image_file
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from math import log
from PIL import Image, ImageFile
from datetime import datetime, timedelta
from django.utils import timezone
#from django.utils.translation import ugettext_lazy as _
#from registration.backends.simple.views import RegistrationView

class ScoreHelpView(FormView):
	form_class = ScoreHelpForm
	template_name = "score_help.html"

class HelpView(FormView):
	form_class = HelpForm
	template_name = "help.html"

class LinkDetailView(DetailView):
	model = Link

	def get_context_data(self, **kwargs):
		context = super(LinkDetailView, self).get_context_data(**kwargs)
		token = '?'+self.object.description.replace(" ", "")[:3]+self.object.submitter.username[:3]#creating a 'token' context comprising the submitter and the link description
		context["token"] = token
		if self.request.user.is_authenticated():
			voted = Vote.objects.filter(voter=self.request.user) #all links user voted on
			link_in_page = self.object.id #the link.id of the link shown on the detailview
			voted = voted.filter(link_id=link_in_page) #is the current link in that list of objects?
			voted = voted.values_list('link_id', flat=True) #strips aways everything other than the id of the link
			context["voted"] = voted #a mapping between "voted" and the link id gotten above is set up, and passed as context to the template
		return context

class LinkListView(ListView):
	model = Link
	queryset = Link.with_votes.all() #by default, query_set was equal to: Link.objects.all(). We're overriding that to call "with_votes defined in models.py"
	paginate_by = 10
	
	def get_context_data(self, **kwargs):
		context = super(LinkListView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			voted = Vote.objects.filter(voter=self.request.user) #all links the user voted on
			links_in_page = [link.id for link in context["object_list"]]#getting ids of all links in page
			voted = voted.filter(link_id__in=links_in_page)#only
			voted = voted.values_list('link_id', flat=True)
			context["voted"] = voted
			####################
			vote_cluster = Vote.objects.all() # all votes
			vote_cluster = vote_cluster.filter(link_id__in=links_in_page) # votes in page
			context["vote_cluster"] = vote_cluster
			#votes_in_page = [vote.link for link in links_in_page] 
			#votes_in_page = [vote.id for link.voted in context["object_list"]] #all vote objects in the page
			#context["votes_in_page"] = votes_in_page
			#all users who voted on a link
		return context

class LinkUpdateView(UpdateView):
	model = Link
	form_class = LinkForm
	paginate_by = 10

class WhoseOnlineView(FormView):
	#model = Request
	form_class = WhoseOnlineForm
	template_name = "whose_online.html"
	#paginate_by = 10 # date_based generic views don't support pagination, because by the time you go to the next page, the set would have changed
	#queryset = Request.objects.active_users(minutes=5) #users online in the last 5 mins

class LinkDeleteView(DeleteView):
	model = Link
	success_url = reverse_lazy("home")

class UserProfileDetailView(DetailView):
	model = get_user_model()
	slug_field = "username"
	template_name = "user_detail.html"

	def get_object(self, queryset=None):
		user = super(UserProfileDetailView, self).get_object(queryset)
		#UserProfile.objects.get_or_create(user=user)
		return user

class UserActivityView(ListView):
	model = Link
	slug_field = "username"
	template_name = "user_activity.html"
	#queryset = Link.with_votes.filter(submitter=request.user)
	paginate_by = 10
	#user = request.user.get_profile()

	def get_queryset(self):
		#user = super(UserActivityView, self).get_queryset()
		username = self.kwargs['slug']
		user = User.objects.filter(username=username)
		return Link.with_votes.filter(submitter=user)#self.request.user)

	def get_context_data(self, **kwargs):
		context = super(UserActivityView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			links_in_page = [link.id for link in context["object_list"]]#getting ids of all user's links in page
			vote_cluster = Vote.objects.filter(link_id__in=links_in_page) # votes on user's link in page
			context["vote_cluster"] = vote_cluster
			voted = vote_cluster.filter(voter=self.request.user)
			context["voted"] = voted.values_list('link_id', flat=True)
		return context

class UserSettingDetailView(DetailView):
	model = get_user_model()
	slug_field = "username"
	template_name = "user_detail.html"

	def get_object(self, queryset=None):
		user = super(UserSettingDetailView, self).get_object(queryset)
		UserSettings.objects.get_or_create(user=user)
		return user

class UserProfileEditView(UpdateView):
	model = UserProfile
	form_class = UserProfileForm
	template_name = "edit_profile.html"

	def get_object(self, queryset=None):
		return UserProfile.objects.get_or_create(user=self.request.user)[0]

	def get_success_url(self):
		return reverse("profile", kwargs={'slug': self.request.user})


class UserSettingsEditView(UpdateView):
	model = UserSettings
	form_class = UserSettingsForm
	template_name = "edit_settings.html"

	def get_object(self, queryset=None): #loading the current state of settings
		return UserSettings.objects.get_or_create(user=self.request.user)[0]

	def get_success_url(self): #which URL to go back once settings are saved?
		return reverse("profile", kwargs={'slug': self.request.user})

class LinkCreateView(CreateView):
	model = Link
	form_class = LinkForm

	#def get_object(self, queryset=None):
		#return Link.objects.get_or_create(user=self.request.user)[0]

	def form_valid(self, form): #this processes the form before it gets saved to the database
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		#Setting rank score
		epoch = datetime(1970, 1, 1).replace(tzinfo=None)
		unaware_submission = datetime.now().replace(tzinfo=None)
		td = unaware_submission - epoch 
		epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
		secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
		f.rank_score = round(0 * 0 + secs / 45000, 8)
		if self.request.user.is_authenticated():
			f.submitter = self.request.user
		#	f.submitter.userprofile.score = f.submitter.userprofile.score + 0 #adding 5 points every time a user submits new content
		else:
			f.submitter = User(id=8) # ALWAYS set this ID to unregistered_bhoot
		#	f.submitter.userprofile.score = f.submitter.userprofile.score + 0
		f.with_votes = 0
		f.category = '1'
		# can we throw in an "are you human" test?
		if f.description==f.submitter.userprofile.previous_retort:
			return redirect(self.request.META.get('HTTP_REFERER')+"#section0")
		f.submitter.userprofile.previous_retort = f.description
		if f.image_file:
			f.image_file = clean_image_file(f.image_file)
		''' removing representative image code
		urls1 = re.findall(urlmarker.URL_REGEX,f.description)
		urls2 = re.findall(urlmarker.URL_REGEX,f.url)
		try:
			if len(urls1)==0:
				if len(urls2)==1:
					#eliminate that urls2[0] is a media site URL
					name, image = read_image(urls2[0])
					if image:
						image_io = StringIO.StringIO()#creating a file-like object
						image.save(image_io, format='JPEG')
						thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
						f.image_file = thumbnail
			elif len(urls1)==1:
				#eliminate that urls1[0] is a media site URL
				name, image = read_image(urls1[0])
				if image:
					image_io = StringIO.StringIO()#creating a file-like object
					image.save(image_io, format='JPEG')
					thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
					f.image_file = thumbnail
			elif len(urls1)>=2:
				#eliminate that urls1[0] is a media site URL
				name, image = read_image(urls1[0])
				if image:
					image_io = StringIO.StringIO()#creating a file-like object
					image.save(image_io, format='JPEG')
					thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
					f.image_file = thumbnail
				else:
					#eliminate that urls1[1] is a media site URL
					name, image = read_image(urls1[1])
					if image:
						image_io = StringIO.StringIO()#creating a file-like object
						image.save(image_io, format='JPEG')
						thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
						f.image_file = thumbnail
			else:
				pass
		except Exception as e:
			print '%s (%s)' % (e.message, type(e))	
			pass			
		'''
		f.save()
		f.submitter.userprofile.save()
		return super(CreateView, self).form_valid(form)

	def get_success_url(self): #which URL to go back once settings are saved?
		return reverse("home")

class VoteFormView(FormView): #corresponding view for the form for Vote we created in forms.py
	form_class = VoteForm

	def form_valid(self, form): #this function is always to be defined in views created for forms
		link = get_object_or_404(Link, pk=form.data["link"]) #this gets the primary key from the form the user submitted
		token = self.request.POST.get("token")
		voter = self.request.POST.get("voter")
		referer = self.request.META.get('HTTP_REFERER')
		try:
			if (token in referer) and (voter == '1'):
				user = User(id=8) #setting user to unregistered_bhoot if a token carrying user, parading as mhb11, got to this point
				print user.id
			else:
				user = self.request.user
		except:
			user = self.request.user
		section = 0
		if self.request.method == 'POST':
			btn = self.request.POST.get("val")
			section = self.request.POST.get("section_number")
		#if btn == u"\u2714":
		if btn == 'jhappee maro':
			val = 1
			if not link.submitter.username == 'unregistered_bhoot':
				link.submitter.userprofile.score = link.submitter.userprofile.score + 10 #adding 10 points every time a user's content gets an upvote
				link.submitter.userprofile.save() #this is a server call 
		#elif btn == u"\u2717":
		elif btn == 'chupair maro':
			val = -1
			if not link.submitter.username == 'unregistered_bhoot':
				link.submitter.userprofile.score = link.submitter.userprofile.score - 10 #subtracting 10 points every time a user's content gets a downvote
				link.submitter.userprofile.save()
		else:
			val = 0
		has_voted = 0 #adding default value for has_voted in case its unregistered_bhoot (i.e. user.id = 8)
		if not user.id == 8: #only checking previous votes for users other than unregistered_bhoot. Bhoot gets a free pass every time.
			print 'user id is %s' % user.id
			prev_votes = Vote.objects.filter(voter=user, link=link) #has the user already voted? If so, we'll find out via this
			has_voted = (prev_votes.count() > 0)
		if not has_voted: #this only works if the user has NOT voted before
			# add vote
			Vote.objects.create(voter=user, link=link, value=val) #if user hasn't voted, add the up or down vote in the DB.
		else:
			if prev_votes[0].value > 0:
				if not link.submitter.username == 'unregistered_bhoot':
					link.submitter.userprofile.score = link.submitter.userprofile.score - 10 #subtract previously added score because of the upvote
					link.submitter.userprofile.save()
			else:
				if not link.submitter.username == 'unregistered_bhoot':
					link.submitter.userprofile.score = link.submitter.userprofile.score + 10 #add previously subtracted score because of the downvote
					link.submitter.userprofile.save()
			# delete vote
			prev_votes[0].delete() #if user has previously voted, simply delete previous vote
		#if page==1:
		if ('?' in self.request.META.get('HTTP_REFERER')) and ('page=' not in self.request.META.get('HTTP_REFERER')):#ensure paginated links aren't split
			url = self.request.META.get('HTTP_REFERER')
			blocks = url.split('?')
			return redirect(blocks[0]+"#section"+section)
		else:
			return redirect(self.request.META.get('HTTP_REFERER')+"#section"+section)

	def form_invalid(self, form): #this function is also always to be defined for views created for forms
		voter = get_object_or_404(Link, pk=form.data["voter"])
		print 'form invalid, voter_id = %s' % voter.id
		return redirect("home")
	

	
def LinkAutoCreate(user, content):   
	link = Link()
	#content = content.replace('#',' ') 
	link.description = content
	link.submitter = user
	#user.userprofile.score = user.userprofile.score + 5 #adding score for content creation
	epoch = datetime(1970, 1, 1).replace(tzinfo=None)
	unaware_submission = datetime.now().replace(tzinfo=None)
	td = unaware_submission - epoch 
	epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
	secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
	link.rank_score = round(0 * 0 + secs / 45000, 8)
	link.with_votes = 0
	link.category = '1' '''
	try:
		urls1 = re.findall(urlmarker.URL_REGEX,link.description)
		if len(urls1)==0:
			pass
		elif len(urls1)==1:
			name, image = read_image(urls1[0])
			if image:
				image_io = StringIO.StringIO()
				image.save(image_io, format='JPEG')
				thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
				link.image_file = thumbnail
		elif len(urls1)>=2:
			name, image = read_image(urls1[0])
			if image:
				image_io = StringIO.StringIO()
				image.save(image_io, format='JPEG')
				thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
				link.image_file = thumbnail
			else:
				name, image = read_image(urls1[1])
				if image:
					image_io = StringIO.StringIO()
					image.save(image_io, format='JPEG')
					thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
					link.image_file = thumbnail
		else:
			pass
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))	
		pass			'''
	link.save()
	user.userprofile.previous_retort = content
	user.userprofile.save()