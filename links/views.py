# Create your views here.
import re, urlmarker, StringIO
from itertools import chain
from collections import OrderedDict
from operator import attrgetter
from django.core.files.uploadedfile import InMemoryUploadedFile
from scraper import read_image
from collections import defaultdict
from django.db.models import Max, Count
from verified import FEMALES
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

def GetLinksWithUserReplies(user):
	links_with_user_replies=[]
	#print "links with user's replies (initially): %s" % links_with_user_replies
	if Publicreply.objects.filter(submitted_by=user).exists(): #check if the user has ever given a reply
		reply_list = Publicreply.objects.filter(submitted_by=user).order_by('-submitted_on')[:75] #up to last 75 replies given by user
		#print "replies given by user are: %s" % reply_list
		if reply_list:
			links_with_user_replies = list(set([reply.answer_to for reply in reply_list])) #a list of unique link.ids user has replied under (own or others)
			#print "links with user's replies (post processing): %s" % links_with_user_replies
	return links_with_user_replies

def GetLinksByUser(user):
	links_user_created_qset = []
	#print "links user created (initially): %s" % links_user_created_qset
	if Link.objects.filter(submitter=user).exists():# if user has ever submitted a link
		links_user_created_qset = list(set(Link.objects.filter(submitter=user).order_by('-submitted_on')[:75])) #up to last 75 links created by user
		#print "links user created (post processing): %s" % links_user_created_qset
	return links_user_created_qset #works correctly

def GetLatestUserInvolvement(user):
	qset_replies = []
	qset_links = []
	latest_timestamp = []
	user_replies_list = []
	user_link_replies_list = []
	qset_replies = GetLinksWithUserReplies(user) #links that contain user replies in list format
	qset_links = GetLinksByUser(user) # links created by the user in list format
	if qset_replies and qset_links:
		every_link = list(set(chain(qset_replies,qset_links))) #uniquely relevant links, no duplicates
	elif qset_replies:
		every_link = list(chain(qset_replies))
	elif qset_links:
		every_link = list(chain(qset_links))
	else:
		every_link = []
	replies_list = []
	if every_link:
		replies_list = list(chain.from_iterable(link.publicreply_set.order_by('-submitted_on')[:1] for link in every_link)) #chain flattens list to detect duplicates later
		#print replies_list
	if not replies_list:
		return replies_list
	#print "all replies are: %s" % replies_list
	for reply in replies_list[:]:#adding [:] ensures a copy of all_replies is made, so that the for loop doesn't get cannibalized as the list dwindles
		if reply.publicreply_seen_related.filter(seen_user=user).exists():
			replies_list.remove(reply)
	#print "all replies made in related links, unseen by the user, are %s" % all_replies
	#if all_replies:
	#	all_replies = filter(None, all_replies)
	#print "cleaned list is %s" % cleaned_list
	if replies_list:
		try:
			dates_in_all_unseen_replies = (reply.submitted_on for reply in replies_list)#[reply.values_list('submitted_on',flat=True) for reply in cleaned_list]
		except:
			dates_in_all_unseen_replies = 0
		#print "dates of all unseen replies are %s" % dates_in_all_unseen_replies
		if dates_in_all_unseen_replies:
			try:
				latest_timestamp = max(dates_in_all_unseen_replies)
				#print "max date of unseen reply is: %s" % latest_timestamp
				return latest_timestamp
			except:
				#latest_timestamp = []
				#print "latest timestamp allotted was []"
				return latest_timestamp
		else:
			#print "latest timestamp is %s:" % latest_timestamp
			return latest_timestamp
	else:
		return latest_timestamp


'''
	def get_queryset(self):
		#queryset to return all relevant links (own and others), bonus: sorted by UNseen links
		username = self.kwargs['slug']
		user = User.objects.get(username=username)
		all_relevant_links_qset = GetLatestUserInvolvement(user)
		all_relevant_links_qset = all_relevant_links_qset.annotate(date=Max('publicreply__submitted_on')).order_by('-date')
		#above gives None values to links without replies, and orders by latest reply, whether new or not
		return all_relevant_links_qset
'''
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
			replies = Publicreply.objects.filter(answer_to_id__in=links_in_page) #all replies in a page
			context["replies"] = replies
			############
			timestamp = GetLatestUserInvolvement(self.request.user)
			if Unseennotification.objects.filter(recipient=self.request.user).exists():
				user_object = Unseennotification.objects.get(recipient=self.request.user)
				try: #timestamp[0] exists
					if user_object.timestamp < timestamp:
						context["notification"] = 1
					else:
						context["notification"] = 0
				except:#timestamp is empty
					context["notification"] = 0
				#try:
					#print "time of UNSEEN post: %s" % timestamp
					#print "last notification time: %s" % user_object.timestamp
					#print "////////////////////////////////////////////////////////////////////////////////"
				#except:
					#print "there is no unseen post"
					#print "last notification time: %s" % user_object.timestamp
					#print "////////////////////////////////////////////////////////////////////////////////"
			else: #i.e. Unseennotification object doesn't exist for the user
				try:
					#print "TAKING THE CLOCK BACK BY 15 MINS"
					user_object = Unseennotification.objects.create(recipient=self.request.user,\
						timestamp=(timestamp- datetime.timedelta(0, 900)))
				except:
					user_object = Unseennotification.objects.create(recipient=self.request.user,\
						timestamp=datetime.utcnow().replace(tzinfo=utc))
				try: #timestamp[0] exists
					if user_object.timestamp < timestamp:
						context["notification"] = 1
					else:
						context["notification"] = 0
				except:#timestamp is empty
					context["notification"] = 0
				#try:
					#print "time of unseen post: %s" % timestamp
					#print "last notification time: %s" % user_object.timestamp
					#print "////////////////////////////////////////////////////////////////////////////////"
				#except:
					#print "time of latest unseen post: N/A (there is no unseen post)"
					#print "last notification time: %s" % user_object.timestamp
					#print "////////////////////////////////////////////////////////////////////////////////"
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
			replies = list(Publicreply.objects.filter(answer_to=link).order_by('-submitted_on')[:25])
			context["replies"] = replies
			own_reply = Publicreply.objects.filter(answer_to=link, submitted_by=self.request.user).exists()
			if link.submitter == self.request.user and own_reply==False: #user only wrote parent link
				seenreplies=[]
				for reply in replies: #replies that have seen objects 
					if Seen.objects.filter(which_reply=reply,seen_user=self.request.user).exists():
						seenreplies.append(reply)
				context["seenreplies"] = seenreplies
				for response in replies:
					if response not in seenreplies:
						#creating seen objects for every unseen reply, for that particular user
						Seen.objects.create(seen_user= self.request.user,which_reply=response,seen_status=True)
				#handling exception where own reply makes all earlier replies become "new" (happens when jumping into a new convo):
			elif own_reply: #user wrote a reply too (whether or not they wrote a parent link)
				seenreplies=[]
				latest_own_reply = Publicreply.objects.filter(answer_to=link, submitted_by=self.request.user).latest('submitted_on')
				if latest_own_reply in replies:
					less_than_replies = [reply for reply in replies if reply.submitted_on < latest_own_reply.submitted_on]
					#print "less_than_replies:%s" % less_than_replies
					more_than_replies = [reply for reply in replies if reply.submitted_on >= latest_own_reply.submitted_on]
					#print "more_than_replies:%s" % more_than_replies
					for reply in less_than_replies:#sweeping unseen replies under the proverbial rug
						if not Seen.objects.filter(which_reply=reply,seen_user=self.request.user).exists():
							Seen.objects.create(seen_user= self.request.user,which_reply=reply,seen_status=True)
							seenreplies.append(reply)
						else:
							seenreplies.append(reply)
					for reply in more_than_replies:
						if Seen.objects.filter(which_reply=reply,seen_user=self.request.user).exists():
							seenreplies.append(reply)
							#####################################################
				context["seenreplies"] = seenreplies
				for response in replies:
					if response not in seenreplies:
						#creating seen objects for every unseen reply, for that particular user
						Seen.objects.create(seen_user= self.request.user,which_reply=response,seen_status=True)
			else: #user didn't write parent link, nor ever replied
				context["seenreplies"] = replies
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		description = self.request.POST.get("description")
		if description == self.request.user.userprofile.previous_retort:
			return redirect(self.request.META.get('HTTP_REFERER')+"#sectionJ")
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
		links_user_created = GetLinksByUser(user) #returns a list
		links_with_user_replies = GetLinksWithUserReplies(user) #returns a list
		if links_with_user_replies and links_user_created:
			all_links = list(set(chain(links_with_user_replies,links_user_created)))
			#print "all replies are: %s" % all_links			
		elif links_with_user_replies:
			all_links = list(chain(links_with_user_replies))
			#print all_links
		elif links_user_created:
			all_links = list(chain(links_user_created))
			#print all_links
		else:
			all_links = []
		all_links_qset = []
		if all_links:
			for link in all_links[:]:#remove this for loop statement when wanting to revert to 10/22/2015 views.py state
				if not link.publicreply_set.exists():
					all_links.remove(link)
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
			'''for index, link in enumerate(context["object_list"]):
				if link.publicreply_set.exists(): #i.e. for only links that have replies, check if latest reply has seen object
					latest_reply = link.publicreply_set.latest('submitted_on')
					if latest_reply in link.publicreply_set.filter(publicreply_seen_related__seen_user = user \
						,publicreply_seen_related__which_reply = latest_reply):
						eachlink[index].append(link) #seen
						eachlink[index].append(latest_reply.submitted_on)#timestamp
						eachlink[index].append(None)#unseen
					else:
						eachlink[index].append(None)#seen
						eachlink[index].append(latest_reply.submitted_on)#timestamp
						eachlink[index].append(link) #unseen
				else:# i.e. there is no reply, so this is 'seen' too
					eachlink[index].append(link)#seen
					eachlink[index].append(None)#timestamp
					eachlink[index].append(None)'''#unseen
			index = 0
			for link in context["object_list"]:
				if link.publicreply_set.exists(): #i.e. for only links that have replies, check if latest reply has seen object
					latest_reply = link.publicreply_set.latest('submitted_on')
					if latest_reply in link.publicreply_set.filter(publicreply_seen_related__seen_user = user \
						,publicreply_seen_related__which_reply = latest_reply):
						eachlink[index].append(link) #seen
						eachlink[index].append(latest_reply.submitted_on)#timestamp
						eachlink[index].append(None)#unseen
						index += 1
						#print index
					else:
						eachlink[index].append(None)#seen
						eachlink[index].append(latest_reply.submitted_on)#timestamp
						eachlink[index].append(link) #unseen
						index += 1
						#print index
				else:# i.e. there is no reply, so this is 'seen' too
					pass
			eachlink.default_factory=None
			#print eachlink
			context["eachlink"] = dict(eachlink)
			context["verify"] = FEMALES
			if Unseennotification.objects.filter(recipient=self.request.user).exists():
				user_object = Unseennotification.objects.get(recipient=self.request.user)
				#print datetime.utcnow().replace(tzinfo=utc)
				user_object.timestamp = datetime.utcnow().replace(tzinfo=utc) #time now
				user_object.save()
			else:
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
			redirect("home")

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