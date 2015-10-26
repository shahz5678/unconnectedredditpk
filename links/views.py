# Create your views here.
import re, urlmarker, StringIO
from itertools import chain
from collections import OrderedDict
from operator import attrgetter
from django.core.files.uploadedfile import InMemoryUploadedFile
from scraper import read_image
from collections import defaultdict
from django.db.models import Max, Count, Q
from verified import FEMALES
from allowed import ALLOWED
from .models import Link, Vote, UserProfile, UserSettings, Publicreply, Seen, Unseennotification
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from .forms import UserProfileForm, LinkForm, VoteForm, ScoreHelpForm, HistoryHelpForm, UserSettingsForm, HelpForm, WhoseOnlineForm, RegisterHelpForm, VerifyHelpForm, PublicreplyForm, ReportreplyForm, ReportForm, UnseenActivityForm, clean_image_file
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from math import log
from PIL import Image, ImageFile
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import utc

#from django.utils.translation import ugettext_lazy as _
#from registration.backends.simple.views import RegistrationView

def GetNonReplyLinks(user):
	links_with_user_replies=[]
	reply_list = []
	relevant_links = []
	if Publicreply.objects.filter(submitted_by=user).exists(): #check if the user has ever given a reply
		reply_list = Publicreply.objects.filter(submitted_by=user).order_by('-submitted_on').values_list('answer_to',flat=True)[:75]
		if reply_list:
			#Link.objects.filter(submitter=user,Link.pubreply_set.exists())
			relevant_links = list(set(Link.objects.filter(Q(submitter=user,publicreply__isnull=False)|Q(id__in=reply_list)).order_by('-submitted_on')[:150]))
	return relevant_links#list of links

def GetLinks(user):
	links_with_user_replies=[]
	reply_list = []
	relevant_links_ids = []
	if Publicreply.objects.filter(submitted_by=user).exists(): #check if the user has ever given a reply
		reply_list = Publicreply.objects.filter(submitted_by=user).order_by('-submitted_on').values_list('answer_to',flat=True)[:75]
		if reply_list:
			relevant_links_ids = list(set(Link.objects.filter(Q(submitter=user)|Q(id__in=reply_list))\
				.order_by('-submitted_on').values_list('id', flat=True)[:150]))
	return relevant_links_ids#list of relevant link ids

def GetLatestUserInvolvement(user):
	empty_timestamp = []
	relevant_link_ids = []
	replies_list = []
	max_unseen_reply = []
	relevant_link_ids = GetLinks(user) #link ids (containing user replies) in list format
	if relevant_link_ids:
		try:
			max_unseen_reply = Publicreply.objects.filter(answer_to_id__in=relevant_link_ids)\
			.exclude(publicreply_seen_related__seen_user=user).latest('submitted_on') #got latest reply's timestamp posted in these links (and wasn't seen by the user)
			#print "max date of unseen reply is: %s" % max_unseen_replys_timestamp
			return max_unseen_reply
		except:
			#print "max date of unseen reply: %s" % empty_timestamp
			return empty_timestamp
	#print "max date of unseen reply is: %s" % empty_timestamp
	return empty_timestamp

class ScoreHelpView(FormView):
	form_class = ScoreHelpForm
	template_name = "score_help.html"

class HistoryHelpView(FormView):
	form_class = HistoryHelpForm
	template_name = "history_help.html"

class HelpView(FormView):
	form_class = HelpForm
	template_name = "help.html"

class VerifyHelpView(FormView):
	form_class = VerifyHelpForm
	template_name = "verify_help.html"	

class RegisterHelpView(FormView):
	form_class = RegisterHelpForm
	template_name = "register_help.html"

class ReportreplyView(FormView):
	form_class = ReportreplyForm
	template_name = "report_reply.html"

	def get_context_data(self, **kwargs):
		context = super(ReportreplyView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["reply"] = self.kwargs["pk"]
		return context

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
	queryset = Link.objects.order_by('-submitted_on')[:180] #instead of Link.with_votes.all()
	paginate_by = 10
	
	def get_context_data(self, **kwargs):
		context = super(LinkListView, self).get_context_data(**kwargs)
		context["checked"] = FEMALES
		if self.request.user.is_authenticated():
			voted = Vote.objects.filter(voter=self.request.user) #all links the user voted on
			links_in_page = [link.id for link in context["object_list"]]#getting ids of all links in page
			voted = voted.filter(link_id__in=links_in_page)#only
			voted = voted.values_list('link_id', flat=True)
			context["voted"] = voted
			vote_cluster = Vote.objects.all() # all votes
			vote_cluster = vote_cluster.filter(link_id__in=links_in_page) # votes in page
			context["vote_cluster"] = vote_cluster
			context["fresh_users"] = User.objects.order_by('-date_joined')[:3]
			#replies = Publicreply.objects.filter(answer_to_id__in=links_in_page) #all replies in a page
			#context["replies"] = replies
			############
			freshest_reply = GetLatestUserInvolvement(self.request.user)
			try:
				timestamp = freshest_reply.submitted_on
				sender = freshest_reply.submitted_by
			except:
				timestamp = []
				sender = 0
			try:
				user_object = Unseennotification.objects.get(recipient=self.request.user)
			except:
				user_object = 0
			if user_object:
				try: 
					if user_object.timestamp < timestamp:
						context["notification"] = 1
						context["sender"] = sender
					else:
						context["notification"] = 0
						context["sender"] = 0
				except:
					context["notification"] = 0
					context["sender"] = 0
			else: 
				try:
					user_object = Unseennotification.objects.create(recipient=self.request.user,\
						timestamp=(timestamp- datetime.timedelta(0, 900)))
				except:
					user_object = Unseennotification.objects.create(recipient=self.request.user,\
						timestamp=datetime.utcnow().replace(tzinfo=utc))
				try: #timestamp[0] exists
					if user_object.timestamp < timestamp:
						context["notification"] = 1
						context["sender"] = sender.username
					else:
						context["notification"] = 0
						context["sender"] = 0
				except:#timestamp is empty
					context["notification"] = 0
					context["sender"] = 0
		return context

class LinkUpdateView(UpdateView):
	model = Link
	form_class = LinkForm
	paginate_by = 10

class WhoseOnlineView(FormView):
	form_class = WhoseOnlineForm
	template_name = "whose_online.html"
	#paginate_by = 10 # date_based generic views don't support pagination, because by the time you go to the next page, the set would have changed

	def get_context_data(self, **kwargs):
		context = super(WhoseOnlineView, self).get_context_data(**kwargs)
		context["legit"] = FEMALES
		return context

class LinkDeleteView(DeleteView):
	model = Link
	success_url = reverse_lazy("home")

class UserProfileDetailView(DetailView):
	model = get_user_model()
	slug_field = "username"
	template_name = "user_detail.html"

	def get_object(self, queryset=None):
		user = super(UserProfileDetailView, self).get_object(queryset)
		UserProfile.objects.get_or_create(user=user)
		return user

	def get_context_data(self, **kwargs):
		context = super(UserProfileDetailView, self).get_context_data(**kwargs)
		context["ratified"] = FEMALES
		return context

class PublicreplyView(CreateView): #get_queryset doesn't work in CreateView (it's a ListView thing!)
	model = Publicreply
	form_class = PublicreplyForm
	template_name = "reply.html"

	def get_context_data(self, **kwargs):
		context = super(PublicreplyView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			link = Link.objects.get(id=self.kwargs["pk"])
			context["parent"] = link
			context["ensured"] = FEMALES
			replies = Publicreply.objects.filter(answer_to=link).order_by('-submitted_on')[:25]
			context["replies"] = replies
			own_reply = Publicreply.objects.filter(answer_to=link, submitted_by=self.request.user).exists()
			if link.submitter == self.request.user and own_reply==False: #user only wrote parent link
				seen_replies = []
				reply_ids = [reply.id for reply in replies]
				seen_replies = Publicreply.objects.filter(id__in=reply_ids,publicreply_seen_related__seen_user=self.request.user)
				context["seenreplies"] = seen_replies
				for response in replies:
					if response not in seen_replies:
						#creating seen objects for every unseen reply, for that particular user
						Seen.objects.create(seen_user= self.request.user,which_reply=response,seen_status=True)
				#handling exception where own reply makes all earlier replies become "new" (happens when jumping into a new convo):
			elif own_reply: #user wrote a reply too (whether or not they wrote a parent link)
				seen_replies=[]
				latest_own_reply = Publicreply.objects.filter(answer_to=link, submitted_by=self.request.user).latest('submitted_on')
				if latest_own_reply in replies: #i.e. user's latest reply is in the 25 replies shown
					less_than_replies = [reply for reply in replies if reply.submitted_on < latest_own_reply.submitted_on]
					less_than_replies_ids = [reply.id for reply in less_than_replies]
					more_than_replies = [reply for reply in replies if reply.submitted_on >= latest_own_reply.submitted_on]
					more_than_replies_ids = [reply.id for reply in more_than_replies]
					#all seen objects of less than replies and more than replies
					less_than_seen_replies = Publicreply.objects.filter(id__in=less_than_replies_ids,publicreply_seen_related__seen_user=self.request.user)
					more_than_seen_replies = Publicreply.objects.filter(id__in=more_than_replies_ids,publicreply_seen_related__seen_user=self.request.user)
					for reply in less_than_replies:#sweeping unseen replies under the proverbial rug
						if reply not in less_than_seen_replies:
							Seen.objects.create(seen_user= self.request.user,which_reply=reply,seen_status=True)
							seen_replies.append(reply)
						else:
							seen_replies.append(reply)
					for reply in more_than_replies:
						#####################################################
						if reply in more_than_seen_replies:
							seen_replies.append(reply)
				context["seenreplies"] = seen_replies
				for response in replies:
					if response not in seen_replies:
						#creating seen objects for every unseen reply, for that particular user
						Seen.objects.create(seen_user= self.request.user,which_reply=response,seen_status=True)
			else: #user didn't write parent link, nor ever replied
				context["seenreplies"] = replies
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		description = self.request.POST.get("description")
		if description == self.request.user.userprofile.previous_retort:
			try: 
				return redirect(self.request.META.get('HTTP_REFERER')+"#sectionJ")
			except: 
				return redirect("home")#, pk= reply.answer_to.id)
		else:
			self.request.user.userprofile.previous_retort = description
			self.request.user.userprofile.score = self.request.user.userprofile.score + 4
			self.request.user.userprofile.save()
			answer_to = Link.objects.get(id=self.request.POST.get("object_id"))
			reply= Publicreply.objects.create(submitted_by=self.request.user, answer_to=answer_to, description=description, category='1')
			Seen.objects.create(seen_user= self.request.user,which_reply=reply,seen_status=True)#creating seen object for reply created
			try:
				return redirect(self.request.META.get('HTTP_REFERER')+"#sectionJ")
			except:
				#print "redirecting"
				return redirect("reply", pk= reply.answer_to.id)

	def get_success_url(self): #which URL to go back once settings are saved?
		try: 
			return redirect(self.request.META.get('HTTP_REFERER')+"#sectionJ")
		except:
			return redirect("home")#, pk= reply.answer_to.id)

class UnseenActivityView(ListView):
	model = Link
	#form_class = UnseenActivityForm
	slug_field = "username"
	template_name = "user_unseen_activity.html"
	paginate_by = 10

	def get_queryset(self):
		#queryset to return all relevant links (own & others), sorted by unseen links queryset = Link.objects.order_by('-submitted_on')[:180]
		username = self.kwargs['slug']
		user = User.objects.get(username=username)
		all_links = []
		all_links_qset = []
		all_links = GetNonReplyLinks(user) #returns a list, upto 150 links, some of which have zero replies.
		if all_links:
			all_link_ids = [link.id for link in all_links]
			all_links_qset = Link.objects.filter(id__in=all_link_ids)
			all_links_qset = all_links_qset.annotate(date=Max('publicreply__submitted_on')).order_by('-date')
		return all_links_qset

	def get_context_data(self, **kwargs):
		#context data to tell which links have unseen data
		context = super(UnseenActivityView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			user = User.objects.filter(username=self.kwargs['slug'])
			eachlink = defaultdict(list)
			index = 0
			seen_replies = []
			link_ids = [link.id for link in context["object_list"]]
			#latest_replies = [link.publicreply_set.latest('submitted_on') for link in context["object_list"]]
			seen_replies = Publicreply.objects.filter(answer_to_id__in=link_ids,publicreply_seen_related__seen_user = user)#all seen replies to all links in object_list
			#need to get all latest replies for each link in object_list
			for link in context["object_list"]:
				try: #i.e. for only links that have replies, check if latest reply has seen object
					latest_reply = link.publicreply_set.latest('submitted_on')
					if latest_reply in seen_replies:
						#link is seen:
						eachlink[index].append(link) #seen
						eachlink[index].append(latest_reply.submitted_on)#timestamp
						eachlink[index].append(None)#unseen
						index += 1
					else:
						#link is unseen:
						eachlink[index].append(None)#seen
						eachlink[index].append(latest_reply.submitted_on)#timestamp
						eachlink[index].append(link) #unseen
						index += 1
				except:# i.e. there is no reply, this is ignored
					pass
			eachlink.default_factory=None
			context["eachlink"] = dict(eachlink)
			context["verify"] = FEMALES
			try:
				user_object = Unseennotification.objects.get(recipient=self.request.user)
				user_object.timestamp = datetime.utcnow().replace(tzinfo=utc) #time now
				user_object.save()
			except:
				Unseennotification.objects.create(recipient=self.request.user,timestamp=datetime.utcnow().replace(tzinfo=utc))
			#print eachlink
		return context


class UserActivityView(ListView):
	model = Link
	slug_field = "username"
	template_name = "user_activity.html"
	paginate_by = 10

	def get_queryset(self):
		username = self.kwargs['slug']
		user = User.objects.get(username=username)
		return Link.objects.filter(submitter=user).order_by('-submitted_on')# instead of Link.with_votes.filter

	def get_context_data(self, **kwargs):
		context = super(UserActivityView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			links_in_page = [link.id for link in context["object_list"]]#getting ids of all user's links in page
			vote_cluster = Vote.objects.filter(link_id__in=links_in_page) # votes on user's link in page
			context["vote_cluster"] = vote_cluster
			voted = vote_cluster.filter(voter=self.request.user)
			context["voted"] = voted.values_list('link_id', flat=True)
			context["verified"] = FEMALES
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

	def get_context_data(self, **kwargs):
		context = super(LinkCreateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["official"] = FEMALES
			context["allowed"] = ALLOWED
		return context

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
			f.submitter.userprofile.score = f.submitter.userprofile.score + 2 #adding 5 points every time a user submits new content
		else:
			f.submitter = User(id=8) # ALWAYS set this ID to unregistered_bhoot
		#	f.submitter.userprofile.score = f.submitter.userprofile.score + 0
		f.with_votes = 0
		f.category = '1'
		# can we throw in an "are you human" test?
		try:
			if f.description==f.submitter.userprofile.previous_retort:
				return redirect(self.request.META.get('HTTP_REFERER')+"#section0")
		except:
			pass
		f.submitter.userprofile.previous_retort = f.description
		if f.image_file:
			image_file = clean_image_file(f.image_file)
			if image_file:
				f.image_file = image_file
			else: f.image_file = None
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

class ReportView(FormView):
	form_class = ReportForm

	def form_valid(self, form):
		if self.request.method == 'POST':
			report = self.request.POST.get("report")
			if report == 'Haan ye ghair ikhlaaqi hai':
				report = self.request.POST.get("reply")
				reply = get_object_or_404(Publicreply, pk=report)
				reply.abuse = True
				reply.submitted_by.userprofile.score = reply.submitted_by.userprofile.score - 10
				reply.submitted_by.userprofile.save()
				reply.save()
				return redirect("reply", pk=reply.answer_to.id)
			else:
				report = self.request.POST.get("reply")
				reply = get_object_or_404(Publicreply, pk=report)
				return redirect("reply", pk= reply.answer_to.id)

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
				print "this user got a free token to vote: %s" % user.id
			else:
				user = self.request.user
		except:
			user = self.request.user
		section = 0
		if self.request.method == 'POST':
			btn = self.request.POST.get("val")
			section = self.request.POST.get("section_number")
		#if btn == u"\u2714":
		if btn == 'jhappee':
			val = 1
			if not link.submitter.username == 'unregistered_bhoot':
				link.submitter.userprofile.score = link.submitter.userprofile.score + 10 #adding 10 points every time a user's content gets an upvote
				link.submitter.userprofile.save() #this is a server call 
		#elif btn == u"\u2717":
		elif btn == 'chupair':
			val = -1
			if not link.submitter.username == 'unregistered_bhoot':
				link.submitter.userprofile.score = link.submitter.userprofile.score - 8 #subtracting 10 points every time a user's content gets a downvote
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
					link.submitter.userprofile.score = link.submitter.userprofile.score + 8 #add previously subtracted score because of the downvote
					link.submitter.userprofile.save()
			# delete vote
			prev_votes[0].delete() #if user has previously voted, simply delete previous vote
		try:
			if ('?' in self.request.META.get('HTTP_REFERER')) and ('page=' not in self.request.META.get('HTTP_REFERER')):#ensure paginated links aren't split
				url = self.request.META.get('HTTP_REFERER')
				blocks = url.split('?')
				return redirect(blocks[0]+"#section"+section)
			else:
				return redirect(self.request.META.get('HTTP_REFERER')+"#section"+section)
		except:
			return redirect("home") #e.g. if Dorado WAP browser, which doesn't have HTTP_REFERER

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