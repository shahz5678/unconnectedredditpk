# Create your views here.
import re, urlmarker, StringIO
from itertools import chain
import urlparse
from collections import OrderedDict
from operator import attrgetter
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import InMemoryUploadedFile
from scraper import read_image
from collections import defaultdict
from django.db.models import Max, Count, Q, Sum
from verified import FEMALES
from allowed import ALLOWED
from .models import Link, Vote, Cooldown, ChatInbox, ChatPic, UserProfile, ChatPicMessage, UserSettings, Publicreply, GroupBanList, HellBanList, Seen, GroupCaptain, Unseennotification, GroupTraffic, Group, Reply, GroupInvite, GroupSeen
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from .forms import UserProfileForm, DeviceHelpForm, ReinvitePrivateForm, ContactForm, InvitePrivateForm, AboutForm, PrivacyPolicyForm, CaptionDecForm, CaptionForm, PhotoHelpForm, PicPasswordForm, CrossNotifForm, VoteOrProfileForm, EmoticonsHelpForm, UserSMSForm, PicHelpForm, DeletePicForm, UserPhoneNumberForm, PicExpiryForm, PicsChatUploadForm, VerifiedForm, GroupHelpForm, LinkForm, WelcomeReplyForm, WelcomeMessageForm, WelcomeForm, NotifHelpForm, MehfilForm, MehfildecisionForm, LogoutHelpForm, LogoutReconfirmForm, LogoutPenaltyForm, SmsReinviteForm, OwnerGroupOnlineKonForm, GroupReportForm, AppointCaptainForm, OutsiderGroupForm, SmsInviteForm, InviteForm, OutsideMessageCreateForm, OutsideMessageForm, DirectMessageCreateForm, DirectMessageForm, KickForm, PrivateGroupReplyForm, PublicGroupReplyForm, ClosedInviteTypeForm, OpenInviteTypeForm, TopForm, LoginWalkthroughForm, RegisterWalkthroughForm, RegisterLoginForm, ClosedGroupHelpForm, ChangeGroupRulesForm, ChangeGroupTopicForm, GroupTypeForm, GroupOnlineKonForm, GroupTypeForm, GroupListForm, OpenGroupHelpForm, GroupPageForm, ReinviteForm, ScoreHelpForm, HistoryHelpForm, UserSettingsForm, HelpForm, WhoseOnlineForm, RegisterHelpForm, VerifyHelpForm, PublicreplyForm, ReportreplyForm, ReportForm, UnseenActivityForm, ClosedGroupCreateForm, OpenGroupCreateForm, clean_image_file#, UpvoteForm, DownvoteForm, OutsideMessageRecreateForm, 
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from math import log
from urllib import quote
from PIL import Image, ImageFile
from datetime import datetime, timedelta
from user_sessions.models import Session
from django.utils import timezone
from django.utils.timezone import utc
from django.views.decorators.cache import cache_page, never_cache
import random, string
import uuid
from fuzzywuzzy import fuzz
from brake.decorators import ratelimit
#from throttle.decorators import throttle

#from django.utils.translation import ugettext_lazy as _
#from registration.backends.simple.views import RegistrationView

condemned = HellBanList.objects.values('condemned_id').distinct()

def valid_passcode(user,num):
	if user.is_authenticated():
		if ChatPicMessage.objects.filter(sender=user,what_number=num).exists():
			return False
		else:
			return True
	else:
		if ChatPicMessage.objects.filter(sender_id=1,what_number=num).exists():
			return False
		else:
			return True


def valid_uuid(uuid):
	regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
	match = regex.match(uuid)
	#print bool(match)
	return bool(match)

def GetNonReplyLinks(user):
	#links_with_user_replies=[]
	#reply_list = []
	#relevant_links = []
	'''
	if Publicreply.objects.filter(submitted_by=user).exists() or Link.objects.filter(submitter=user).exists(): #user has replied and linked both
		reply_list = Publicreply.objects.filter(submitted_by=user).order_by('-submitted_on').values_list('answer_to',flat=True)[:75]
		if reply_list:
			relevant_links = list(set(Link.objects.filter(Q(submitter=user,publicreply__isnull=False)|Q(id__in=reply_list)).\
				order_by('-submitted_on')[:150]))
	'''
	try:
		now = datetime.utcnow().replace(tzinfo=utc)
		timestamp = now - timedelta(minutes=60*48)
		global condemned
		relevant_links = Link.objects.filter(Q(submitter=user,publicreply__isnull=False, submitted_on__gte=timestamp)|Q(publicreply__submitted_by=user, publicreply__submitted_on__gte=timestamp)).exclude(submitter_id__in=condemned).distinct().order_by('-id')[:10]
	except:
		#print "no relevant links"
		relevant_links = []
	return relevant_links

def GetLinks(user):
	try: 
		now = datetime.utcnow().replace(tzinfo=utc)
		timestamp = now - timedelta(minutes=30)
		global condemned
		relevant_links_ids = list(set(Link.objects.filter(Q(submitter=user,publicreply__isnull=False, submitted_on__gte=timestamp)|Q(publicreply__submitted_by=user, publicreply__submitted_on__gte=timestamp)).exclude(submitter_id__in=condemned).order_by('-id').values_list('id', flat=True)[:10]))
		#relevant_links_ids = list(set(Link.objects.filter(Q(submitter=user,publicreply__isnull=False)|Q(publicreply__submitted_by=user)).exclude(submitter_id__in=condemned).order_by('-id').values_list('id', flat=True)[:90]))
		#print "relevant link ids are: %s" % relevant_links_ids
	except:
		relevant_links_ids = []
	return relevant_links_ids

def GetLatestUserInvolvement(user):
	empty_timestamp = []
	max_unseen_reply = []
	relevant_link_ids = GetLinks(user)
	global condemned
	if relevant_link_ids:
		try:
			max_unseen_reply = Publicreply.objects.filter(answer_to_id__in=relevant_link_ids).exclude(publicreply_seen_related__seen_status=True,publicreply_seen_related__seen_user=user).exclude(submitted_by_id__in=condemned).latest('id')
			#print "max unseen reply is %s" % max_unseen_reply
			return max_unseen_reply 
		except:
			return empty_timestamp
	return empty_timestamp		

class NeverCacheMixin(object):
	@method_decorator(never_cache)
	def dispatch(self, *args, **kwargs):
		return super(NeverCacheMixin, self).dispatch(*args, **kwargs)

class OutsideMessageView(FormView):
	form_class = OutsideMessageForm
	template_name = "outside_message_help.html"

class DeviceHelpView(FormView):
	form_class = DeviceHelpForm
	template_name = "device_help.html"

	def get_context_data(self, **kwargs):
		context = super(DeviceHelpView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			device = self.kwargs.get("pk")
			if device == '1':
				context["device"] = '1'
			elif device == '2':
				context["device"] = '2'
			elif device == '3':
				context["device"] = '3'
			elif device == '4':
				context["device"] = '4'
			elif device == '5':
				context["device"] = '5'
			else:
				context["device"] = None
		return context

class GroupHelpView(FormView):
	form_class = GroupHelpForm
	template_name = "group_help.html"

class ScoreHelpView(FormView):
	form_class = ScoreHelpForm
	template_name = "score_help.html"

class ReinvitePrivateView(FormView):
	form_class = ReinvitePrivateForm
	template_name = "reinvite_private.html"

	def get_context_data(self, **kwargs):
		context = super(ReinvitePrivateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = request.sesion["private_uuid"]
			context["unique"] = unique
		return context

class ReinviteView(FormView):
	form_class = ReinviteForm
	template_name = "reinvite.html"

	def get_context_data(self, **kwargs):
		context = super(ReinviteView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.kwargs.get("slug")
			context["unique"] = unique
		return context

class HistoryHelpView(FormView):
	form_class = HistoryHelpForm
	template_name = "history_help.html"

class PhotosHelpView(FormView):
	form_class = PhotoHelpForm
	template_name = "photos_help.html"

	def get_context_data(self, **kwargs):
		context = super(PhotosHelpView, self).get_context_data(**kwargs)
		context["unique"] = self.kwargs.get("slug")
		context["decision"] = self.kwargs.get("pk")
		return context

class NotifHelpView(FormView):
	form_class = NotifHelpForm
	template_name = "notif_help.html"

	def get_context_data(self, **kwargs):
		context = super(NotifHelpView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["link_pk"] = self.kwargs.get("pk")
			#context["unique"] = link_pk
		return context

class RegisterWalkthroughView(FormView):
	form_class = RegisterWalkthroughForm
	template_name = "register_walkthrough.html"

class LoginWalkthroughView(FormView):	
	form_class = LoginWalkthroughForm
	template_name = "login_walkthrough.html"

class SmsReinviteView(FormView):
	form_class = SmsReinviteForm
	template_name = "sms_reinvite.html"

	def get_context_data(self, **kwargs):
		context = super(SmsReinviteView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.request.session["unique_outsider"]#self.kwargs["slug"]
			context["number"] = '03450000000'
			context["sms_url"] = "https://http-damadam-pk.0.freebasics.com/mehfil/"+unique+"/bahir/"
			#context["group"] = Group.objects.get(unique=unique)
		return context

class SmsInviteView(FormView):
	form_class = SmsInviteForm
	template_name = "sms_invite.html"

	def get_context_data(self, **kwargs):
		context = super(SmsInviteView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.kwargs["slug"]
			number = self.kwargs["num"]
			name = self.kwargs["name"]
			context["name"] = name
			context["number"] = number
			context["sms_url"] = "https://http-damadam-pk.0.freebasics.com/mehfil/"+unique+"/bahir/"
		return context

class ClosedInviteTypeView(FormView):
	form_class = ClosedInviteTypeForm
	template_name = "closed_invite_type.html"

	def get_context_data(self, **kwargs):
		context = super(ClosedInviteTypeView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.request.session["private_uuid"]
			context["unique"] = unique
			context["sms_url"] = "https://http-damadam-pk.0.freebasics.com/mehfil/"+unique
		return context

class OpenInviteTypeView(FormView):
	form_class = OpenInviteTypeForm
	template_name = "open_invite_type.html"

	def get_context_data(self, **kwargs):
		context = super(OpenInviteTypeView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.request.session["public_uuid"]
			context["unique"] = unique
			context["sms_url"] = "https://http-damadam-pk.0.freebasics.com/mehfilawami/"+unique
		return context

class RegisterLoginView(FormView):
	form_class = RegisterLoginForm
	template_name = "register_login.html"

class OpenGroupHelpView(FormView):
	form_class = OpenGroupHelpForm
	template_name = "open_group_help.html"

class ContactView(FormView):
	form_class = ContactForm
	template_name = "contact.html"

class AboutView(FormView):
	form_class = AboutForm
	template_name = "about.html"

class PrivacyPolicyView(FormView):
	form_class = PrivacyPolicyForm
	template_name = "privacy_policy.html"

class ClosedGroupHelpView(FormView):
	form_class = ClosedGroupHelpForm
	template_name = "closed_group_help.html"	

class HelpView(FormView):
	form_class = HelpForm
	template_name = "help.html"

class VerifyHelpView(FormView):
	form_class = VerifyHelpForm
	template_name = "verify_help.html"	

class RegisterHelpView(FormView):
	form_class = RegisterHelpForm
	template_name = "register_help.html"

class LogoutPenaltyView(FormView):
	form_class = LogoutPenaltyForm
	template_name = "logout_penalty.html"

class VoteOrProfileView(FormView):
	form_class = VoteOrProfileForm
	template_name = "vote_or_profile.html"

	def get_context_data(self, **kwargs):
		context = super(VoteOrProfileView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			link_submitter_id = self.kwargs["num"] # the link submitter who was voted on
			vote_id = self.kwargs["id"] #the vote that was cast
			user_id = self.kwargs["pk"] #person who voted
			try:
				vote = Vote.objects.get(pk=vote_id)
			except:
				context["self"] = -1
				context["subject"] = self.request.user
				context["vote_id"] = vote_id
				context["link_submitter_id"] = link_submitter_id
				return context
			if vote.voter.id == int(user_id): #confirming voter
				if self.request.user.id == int(user_id): #if person looking at own vote
					context["self"] = 1
					context["subject"] = self.request.user
					context["vote_id"] = vote_id
					context["link_submitter_id"] = link_submitter_id
				elif self.request.user.id == int(link_submitter_id): #if link_submitter wants to take revenge
					context["self"] = 2
					context["subject"] = User.objects.get(pk=user_id)
					context["vote_id"] = vote_id
					context["link_submitter_id"] = self.request.user.id
				else:
					context["self"] = 0
					context["subject"] = User.objects.get(pk=user_id)
					context["vote_id"] = vote_id
					context["link_submitter_id"] = link_submitter_id
			else: #maliciously called
				context["self"] = -1
				context["subject"] = self.request.user
				context["vote_id"] = vote_id
				context["link_submitter_id"] = link_submitter_id
		return context

class EmoticonsHelpView(FormView):
	form_class = EmoticonsHelpForm
	template_name = "emoticons_help.html"

	def get_context_data(self, **kwargs):
		context = super(EmoticonsHelpView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["random"] = random.sample(xrange(1,52),10) #select 10 random emoticons out of 52
		return context

class LogoutHelpView(FormView):
	form_class = LogoutHelpForm
	template_name = "logout_help.html"


class LogoutReconfirmView(FormView):
	form_class = LogoutReconfirmForm
	template_name = "logout_reconfirm.html"

	def form_valid(self, form):
		if self.request.user_banned:
			return redirect("score_help") #you can come in any time you like, you can never leave!
		else:
			if self.request.method == 'POST':
				decision = self.request.POST.get("decision")
				if decision == 'Khuda Hafiz':
					try:
						self.request.user.userprofile.score = 10
						self.request.user.userprofile.save()
						return redirect("bahirniklo")
					except:
						return redirect("home")
				else:
					return redirect("home")
			else:
				return redirect("score_help")

class MehfilView(FormView):
	form_class = MehfilForm
	template_name = "mehfil_help.html"

	def get_context_data(self, **kwargs):
		context = super(MehfilView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				target_id = self.request.session['user_pk']
				link_id = self.request.session['link_id']
				context["target"] = User.objects.get(id=target_id)
				context["link_id"] = link_id
			except:
				context["target"] = None
				context["link_id"] = None
				return context
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			report = self.request.POST.get("decision")
			target = self.request.session['user_pk']
			link_id = self.request.session['link_id']
			self.request.session['link_id'] = None
			self.request.session['user_pk'] = None
			try:
				if report == 'Haan':
					return redirect("direct_message", pk=target)
				else:
					return redirect("reply_pk", pk=link_id)
			except:
				return redirect("profile", self.request.user.username)

def reportreply_pk(request, pk=None, num=None, *args, **kwargs):
	if pk.isdigit() and num.isdigit():
		request.session["report_pk"] = pk
		request.session["linkreport_pk"] = num
		return redirect("reportreply")
	else:
		return redirect("score_help")

class ReportreplyView(FormView):
	form_class = ReportreplyForm
	template_name = "report_reply.html"

	def get_context_data(self, **kwargs):
		context = super(ReportreplyView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			pk = self.request.session["report_pk"]
			link_id = self.request.session["linkreport_pk"]
			if Publicreply.objects.filter(pk=pk,answer_to=link_id).exists() and Link.objects.filter(pk=link_id,submitter=self.request.user).exists():
				context["reply"] = pk
				context["authorized"] = True
			else:
				context["reply"] = None
				context["authorized"] = False
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
	paginate_by = 20

	def get_queryset(self):
		if self.request.user_banned:#if user is hell-banned
			return Link.objects.order_by('-id')[:120]
		else:#if user is not hell-banned
			global condemned
			return Link.objects.order_by('-id').exclude(submitter_id__in=condemned)[:120]

	def get_context_data(self, **kwargs):
		context = super(LinkListView, self).get_context_data(**kwargs)
		context["checked"] = FEMALES
		context["can_vote"] = False
		context["authenticated"] = False
		if self.request.user.is_authenticated():
			num = random.randint(1,3)
			context["random"] = num
			if num > 1:
				context["newest_user"] = User.objects.latest('id') #for unauthenticated users
			else:
				context["newest_user"] = None
			context["authenticated"] = True
			user = self.request.user
			context["ident"] = user.id
			context["username"] = user.username
			score = user.userprofile.score
			context["score"] = score
			if score > 10:
				context["can_vote"] = True
			links_in_page = [link.id for link in context["object_list"]]#getting ids of all links in page
			votes_in_page = Vote.objects.filter(link_id__in=links_in_page)
			voted = votes_in_page.filter(voter=user) #all votes the user cast
			voted = voted.values_list('link_id', flat=True) #link ids of all votes the user voted on
			context["voted"] = voted #voted is used to check which links the user has already voted on
			global condemned
			if self.request.user_banned:
				context["vote_cluster"] = votes_in_page # all votes in the page
				context["notification"] = 0 #hell banned users will never see notifications
				context["sender"] = 0 #hell banned users will never see notifications
			else:
				context["vote_cluster"] = votes_in_page.exclude(voter_id__in=condemned) # all votes in the page, sans condemned
				#context["fresh_users"] = User.objects.order_by('-id').exclude(id__in=condemned)[:3]
				freshest_reply = GetLatestUserInvolvement(user)
				#print freshest_reply
				if freshest_reply:
					parent_link = freshest_reply.answer_to
					parent_link_writer = parent_link.submitter
					parent_link_writer_username = parent_link_writer.username
					#print parent_link_writer_username
					WELCOME_MESSAGE1 = parent_link_writer_username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
					#print WELCOME_MESSAGE1
					WELCOME_MESSAGE2 = parent_link_writer_username+" welcome! Kesey ho? Yeh zalim barfi try kar yar (barfi)"
					WELCOME_MESSAGE3 = parent_link_writer_username+" assalam-u-alaikum! Is barfi se mu meetha karo (barfi)"
					WELCOME_MESSAGE4 = parent_link_writer_username+" Damadam pe welcome! One plate laddu se life set (laddu)"
					WELCOME_MESSAGE5 = parent_link_writer_username+" kya haal he? Ye laddu aap ke liye (laddu)"
					WELCOME_MESSAGE6 = parent_link_writer_username+" welcum! Life set hei? Laddu khao, jaan banao (laddu)"
					WELCOME_MESSAGE7 = parent_link_writer_username+" welcomeee! Yar kya hal he? Jalebi khao aur ayashi karo (jalebi)"
					WELCOME_MESSAGE8 = parent_link_writer_username+" kaisey ho? Jalebi meri pasandida hai! Tumhari bhi? (jalebi)"
					WELCOME_MESSAGE9 = parent_link_writer_username+" salam! Is jalebi se mu meetha karo (jalebi)"
					WELCOME_MESSAGES = [WELCOME_MESSAGE1, WELCOME_MESSAGE2, WELCOME_MESSAGE3, WELCOME_MESSAGE4, WELCOME_MESSAGE5,\
					WELCOME_MESSAGE6, WELCOME_MESSAGE7, WELCOME_MESSAGE8, WELCOME_MESSAGE9]
				else:
					parent_link_writer = User()
					#parent_link.submitter = 0
					WELCOME_MESSAGES = []
				try:
					if freshest_reply:
						context["latest_reply"] = freshest_reply
						context["notification"] = 1
						context["parent_link"] = parent_link
						context["parent_link_pk"] = parent_link.pk
						if user==parent_link_writer and any(freshest_reply.description in s for s in WELCOME_MESSAGES):
							#print "first time user"
							context["first_time_user"] = True
						else:
							#print "not first time user"
							context["first_time_user"] = False
					else:
						context["latest_reply"] = []
						context["notification"] = 0
						context["parent_link"] = []
						context["parent_link_pk"] = 0
						context["first_time_user"] = False
						#print "freshest reply didn't exist"
				except:
					context["latest_reply"] = []
					context["notification"] = 0
					context["parent_link"] = []
					context["parent_link_pk"] = 0
					context["first_time_user"] = False
					#print "freshest reply didn't exist"
		else:
			return context
		return context

	def get(self, request, *args, **kwargs):
		self.object_list = self.get_queryset()
		allow_empty = self.get_allow_empty()
		if not allow_empty:
			# When pagination is enabled and object_list is a queryset,
			# it's better to do a cheap query than to load the unpaginated
			# queryset in memory.
			if (self.get_paginate_by(self.object_list) is not None
				and hasattr(self.object_list, 'exists')):
				is_empty = not self.object_list.exists()
			else:
				is_empty = len(self.object_list) == 0
			if is_empty:
				raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
						% {'class_name': self.__class__.__name__})
		context = self.get_context_data(object_list=self.object_list)
		try:
			target_id = self.request.session['target_id']
			self.request.session['target_id'] = None
		except:
			target_id = None
		if target_id:
			try:
				index = list(link.id for link in self.object_list).index(target_id)
				#print index
			except:
				#print "error"
				index = None
			if 0 <= index <= 19:
				addendum = '#section'+str(index+1)
				#print addendum
			elif 20 <= index <= 39:
				addendum = '?page=2#section'+str(index+1-20)
				#print addendum
			elif 40 <= index <= 59:
				addendum = '?page=3#section'+str(index+1-40)
				#print addendum
			elif 60 <= index <= 79:
				addendum = '?page=4#section'+str(index+1-60)
				#print addendum
			elif 80 <= index <= 99:
				addendum = '?page=5#section'+str(index+1-80)
				#print addendum
			elif 100 <= index <= 119:
				addendum = '?page=6#section'+str(index+1-100)
				#print addendum
			else:
				addendum = '#section0'
			#return self.render_to_response(context)
			return HttpResponseRedirect(addendum)
		else:
			return self.render_to_response(context)

class LinkUpdateView(UpdateView):
	model = Link
	form_class = LinkForm
	#paginate_by = 10

def appoint_pk(request, pk=None, app=None, *args, **kwargs):
	if pk.isdigit() and app.isdigit():
		request.session["appoint_id"] = pk
		request.session["appoint_decision"] = app
		return redirect("appoint")
	else:
		return redirect("score_help")

class AppointCaptainView(FormView):
	form_class = AppointCaptainForm
	template_name = "appoint_captain.html"

	def get_context_data(self, **kwargs):
		context = super(AppointCaptainView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			user_id = self.request.session["appoint_id"]
			unique_id = self.request.session["public_uuid"]
			decision = self.request.session["appoint_decision"]
			context["appoint"] = decision
			context["candidate"] = User.objects.get(id=user_id)
			context["unique"] = unique_id
		return context

	def form_valid(self, form):
		#f = form.save(commit=False)
		if self.request.user_banned:
			return redirect("group_page") #errorbanning
		else:
			candidate = self.request.session["appoint_id"]
			self.request.session["appoint_id"] = None
			unique = self.request.session["public_uuid"]
			group = Group.objects.get(unique=unique)
			appoint = self.request.session["appoint_decision"]
			self.request.session["appoint_decision"] = None
			#print appoint
			if appoint == '1' and group.owner == self.request.user and not GroupCaptain.objects.filter(which_user_id = candidate, which_group=group).exists():
				GroupCaptain.objects.create(which_user_id=candidate,which_group=group)
			elif appoint == '0' and group.owner == self.request.user:
				try:
					GroupCaptain.objects.get(which_user_id=candidate,which_group=group).delete()
				except:
					return redirect("owner_group_online_kon")
			else:
				self.request.session["public_uuid"] = None
				return redirect("public_group", slug=unique)
			return redirect("owner_group_online_kon")

class OwnerGroupOnlineKonView(ListView):
	model = GroupTraffic
	form_class = OwnerGroupOnlineKonForm
	template_name = "owner_group_online_kon.html"

	def get_context_data(self, **kwargs):
		context = super(OwnerGroupOnlineKonView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			global condemned
			context["unauthorized"] = False
			context["legit"] = FEMALES
			unique = self.request.session["public_uuid"]
			context["unique"] = unique
			try:
				group = Group.objects.get(unique=unique)
				context["group"] = group
			except:
				context["group"] = None
				context["unauthorized"] = True
				context["groupies"] = []
				return context
			if group.owner == self.request.user and group.private == '0':
				total_traffic = GroupTraffic.objects.filter(which_group = group, time__gte=(timezone.now()-timedelta(minutes=15))).exclude(visitor_id__in=condemned).distinct('visitor')
				online_ids = total_traffic.values_list('visitor_id',flat=True)
				captains = GroupCaptain.objects.filter(which_user_id__in=online_ids, which_group=group)
				captains = {captain.which_user_id: captain for captain in captains}
				helpers = [(traffic,captains.get(traffic.visitor.pk)) for traffic in total_traffic]
				context["groupies"] = helpers
			else:
				context["groupies"] = []
				context["unauthorized"] = True
		return context

class GroupOnlineKonView(ListView):
	model = GroupTraffic
	form_class = GroupOnlineKonForm
	template_name = "group_online_kon.html"
	paginate_by = 75

	def get_context_data(self, **kwargs):
		context = super(GroupOnlineKonView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			global condemned
			context["unauthorized"] = False
			context["legit"] = FEMALES
			unique = self.request.session["public_uuid"]
			context["unique"] = unique
			try:
				group = Group.objects.get(unique=unique)
				context["group"] = group
			except:
				context["group"] = None
				context["unauthorized"] = True
				context["groupies"] = []
				context["officers"] = []
				return context
			if group.private == '0':
				total_traffic = GroupTraffic.objects.filter(which_group = group, time__gte=(timezone.now()-timedelta(minutes=15))).exclude(visitor_id__in=condemned).distinct('visitor')
				total_traffic_ids = total_traffic.values_list('visitor_id', flat=True)
				context["groupies"] = total_traffic 
				captains = GroupCaptain.objects.filter(which_group=group, which_user__in=total_traffic_ids).values_list('which_user_id', flat=True)
				context["officers"] = User.objects.filter(id__in=captains)
			else:
				context["group"] = None
				context["unauthorized"] = True
				context["groupies"] = []
				context["officers"] = []
		return context

#@cache_page(20)
class OnlineKonView(ListView):
	model = Session
	template_name = "online_kon.html"
	#paginate_by = 75

	def get_queryset(self):
		global condemned
		unique_user_sessions = Session.objects.filter(last_activity__gte=(timezone.now()-timedelta(minutes=5))).only('user').distinct('user')
		users = [session.user for session in unique_user_sessions]
		users = [user for user in users if user is not None]
		if self.request.user_banned:
			return users
		else:
			user_ids = [user.pk for user in users]
			users = User.objects.filter(id__in=user_ids).exclude(id__in=condemned)
			return users


	def get_context_data(self, **kwargs):
		context = super(OnlineKonView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["legit"] = FEMALES
		return context

class WhoseOnlineView(FormView):
	form_class = WhoseOnlineForm
	template_name = "whose_online.html"

	def get_context_data(self, **kwargs):
		context = super(WhoseOnlineView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
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

# class OutsideMessageRecreateView(FormView):
# 	model = Group
# 	form_class = OutsideMessageRecreateForm
# 	template_name = "outside_message_recreate.html"

# 	def get_context_data(self, **kwargs):
# 		context = super(OutsideMessageRecreateView, self).get_context_data(**kwargs)
# 		if self.request.user.is_authenticated():
# 			context["unique"] = self.kwargs["slug"]
# 		return context

# 	def form_valid(self, form):
# 		if self.request.user_banned:
# 			return redirect("group_page") #errorbanning
# 		else:
# 			number = self.request.POST.get("mobile_number")
# 			unique = self.request.POST.get("unique")
# 			#print "hello"
# 			return redirect("sms_reinvite", slug=unique, num=number)

class OutsideMessageCreateView(FormView):
	model = Group
	form_class = OutsideMessageCreateForm
	template_name = "outside_message_create.html"

	def form_valid(self, form):
		try:
			nickname = self.request.POST.get("full_name")
			number = self.request.POST.get("mobile_number")
		except:
			nickname = "Dost"
			number = "0345"
		try:
			unique = self.kwargs["slug"]
		except:
			unique = 0
		topic = nickname+" se gupshup"
		unique = uuid.uuid4()
		group = Group.objects.create(topic=topic, rules='', owner=self.request.user, private ='2', unique=unique)
		reply = Reply.objects.create(text='kuch likho taakey hamari chat shuru ho jaye',which_group=group,writer=self.request.user)
		GroupSeen.objects.create(seen_user=self.request.user,which_reply=reply)
		nickname = nickname.split(' ',1)[0]
		return redirect("sms_invite", slug=unique, num=number, name=nickname)

class DirectMessageCreateView(FormView):
	model = Group
	form_class = DirectMessageCreateForm
	#template_name = "create_direct_message.html"

	def form_valid(self, form):
		if self.request.method == 'POST':
			self.request.user.userprofile.score = self.request.user.userprofile.score - 500
			pk = self.kwargs["pk"]
			user = User.objects.get(id=pk)
			invitee = user.username
			topic = invitee+" se gupshup"
			unique = uuid.uuid4()
			try:
				group = Group.objects.create(topic=topic, rules='', owner=self.request.user, private ='1', unique=unique)
				self.request.user.userprofile.save()
				reply_list=[]
				seen_list=[]
				reply_list.append(Reply(text=invitee, category='1', which_group_id=group.id, writer=self.request.user))
				reply_list.append(Reply(text='ao baat karein', which_group_id=group.id, writer=self.request.user))
				Reply.objects.bulk_create(reply_list)
				return redirect("private_group", slug=unique)
			except:
				return redirect("profile", slug=invitee)

class ClosedGroupCreateView(CreateView):
	model = Group
	form_class = ClosedGroupCreateForm
	template_name = "new_closed_group.html"

	def form_valid(self, form):
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		f.owner = self.request.user
		f.private = 1
		unique = uuid.uuid4()
		f.unique = unique
		f.rules = ''
		f.category = '1'
		try:
			if f.topic==f.owner.userprofile.previous_retort:
				return redirect(self.request.META.get('HTTP_REFERER')+"#section0")
		except:
			pass
		f.owner.userprofile.previous_retort = f.topic
		f.owner.userprofile.score = f.owner.userprofile.score - 500
		f.save()
		reply = Reply.objects.create(text='mein ne new mehfil shuru kar di',which_group=f,writer=self.request.user)
		GroupSeen.objects.create(seen_user=self.request.user,which_reply=reply)
		f.owner.userprofile.save()
		try: 
			return redirect("invite_private", slug=unique)
		except:
			return redirect("private_group", slug=unique)

class OpenGroupCreateView(CreateView):
	model = Group
	form_class = OpenGroupCreateForm
	template_name = "new_open_group.html"

	def form_valid(self, form):
		if self.request.user.userprofile.score > 4999:
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			# if self.request.user_banned:
			# 	return redirect("group_page") #errorbanning
			f.owner = self.request.user
			f.private = 0
			unique = uuid.uuid4()
			f.unique = unique
			try:
				if f.topic==f.owner.userprofile.previous_retort:
					return redirect(self.request.META.get('HTTP_REFERER')+"#section0")
			except:
				pass
			f.owner.userprofile.previous_retort = f.topic
			f.owner.userprofile.score = f.owner.userprofile.score - 5000
			f.save()
			reply = Reply.objects.create(text='mein ne new mehfil shuru kar di',which_group=f,writer=self.request.user)
			GroupTraffic.objects.create(visitor=self.request.user, which_group=f)
			Link.objects.create(submitter=self.request.user, description=f.topic, cagtegory='2', url=unique)
			f.owner.userprofile.save()
			try: 
				return redirect("invite", slug=unique)
			except:
				return redirect("public_group", slug=unique)
		else:
			return redirect("group_page")

def direct_message(request, pk=None, *args, **kwargs):
	if pk.isdigit():
		request.session["dm"] = pk
		return redirect("direct_message_help")
	else:
		return redirect("score_help")

class DirectMessageView(FormView):
	form_class = DirectMessageForm
	template_name = "direct_message_help.html"

	def get_context_data(self, **kwargs):
		context = super(DirectMessageView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["nopk"] = False
			try:
				pk = self.request.session["dm"]
				self.request.session["dm"] = None
			except:
				context["nopk"] = True
				context["target"] = None
				return context
			if pk:
				target = User.objects.get(id=pk)
				context["target"] = target
			else:
				context["nopk"] = True
				context["target"] = None
				return context
		return context

def invite_private(request, slug=None, *args, **kwargs):
	if valid_uuid(slug):
		request.session["private_uuid"] = slug
		return redirect("invite_private_group")
	else:
		return redirect("score_help")

class InviteUsersToPrivateGroupView(FormView):
	model = Session
	template_name = "invite_for_private_group.html"
	paginate_by = 70
	form_class = InvitePrivateForm

	def get_context_data(self, **kwargs):
		context = super(InviteUsersToPrivateGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["legit"] = FEMALES
			unique = self.request.session["private_uuid"]
			context["unique"] = unique
			group = Group.objects.get(unique=unique)
			context["group"] = group
			if self.request.user_banned:
				context ["visitors"] = [] # there are no visitors to invite for hellbanned users
			else:
				invites = []
				user_sessions = Session.objects.filter(last_activity__gte=(timezone.now()-timedelta(minutes=15))).only('user').distinct('user')
				users = [session.user for session in user_sessions]#all users that are online
				users = [user for user in users if user is not None] #sanitizing any NONE values that may exist in shared devices
				user_ids = [user.id for user in users]
				online_invited_replied_users = \
				User.objects.filter(~Q(invitee__which_group=group),~Q(reply__which_group=group),id__in=user_ids).distinct()
				context ["visitors"] = online_invited_replied_users
		return context				

	def form_valid(self, form):
		uuid = self.request.session["private_uuid"]
		if self.request.user_banned:
			return redirect("group_page")
		else:
			if self.request.method == 'POST':
				try:
					group = Group.objects.get(unique=uuid)
					invitee = self.request.POST.get('invitee')
					group_id = group.id
				except:
					group_id = -1
				if group_id > -1:
					if GroupInvite.objects.filter(which_group_id=group_id, invitee_id=invitee).exists() or \
					Reply.objects.filter(which_group_id=group_id, writer_id=invitee).exists():
						return redirect("reinvite_private_help")
					else:#this person ought to be sent an invite
						#send a notification to this person to check out the group
						GroupInvite.objects.create(inviter= self.request.user,which_group_id=group_id,invitee_id=invitee)
						invitee = User.objects.get(id=invitee)
						reply = Reply.objects.create(text=invitee.username, category='1', which_group_id=group_id,writer=self.request.user)
						GroupSeen.objects.create(seen_user=self.request.user, which_reply=reply)
			self.request.session["private_uuid"] = None
			return redirect("invite_private", slug=uuid)

class InviteUsersToGroupView(FormView):
	model = Session
	template_name = "invite_for_groups.html"
	paginate_by = 70
	form_class = InviteForm
	
	def get_context_data(self, **kwargs):
		context = super(InviteUsersToGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["legit"] = FEMALES
			unique = self.request.session["public_uuid"]
			context["unique"] = unique
			group = Group.objects.get(unique=unique)
			context["group"] = group
			if self.request.user_banned:
				context ["visitors"] = [] # there are no visitors to invite for hellbanned users
			else:	
				invites = []
				user_sessions = Session.objects.filter(last_activity__gte=(timezone.now()-timedelta(minutes=15))).only('user').distinct('user')
				users = [session.user for session in user_sessions]#all users that are online
				users = [user for user in users if user is not None] #sanitizing any NONE values that may exist in shared devices
				user_ids = [user.id for user in users]
				online_invited_replied_users = \
				User.objects.filter(~Q(invitee__which_group=group),~Q(reply__which_group=group),id__in=user_ids).distinct()
				context ["visitors"] = online_invited_replied_users
			#######################
		return context

	def form_valid(self, form):
		uuid = self.request.session["public_uuid"]
		if self.request.user_banned:
			return redirect("group_page")
		else:
			if self.request.method == 'POST':
				try:
					unique = uuid
					group = Group.objects.get(unique=unique)
					invitee = self.request.POST.get('invitee')
					group_id = group.id
				except:
					group_id = -1
				if group_id > -1:
					if GroupInvite.objects.filter(which_group_id=group_id, invitee_id=invitee).exists() or \
					Reply.objects.filter(which_group_id=group_id, writer_id=invitee).exists():
						return redirect("reinvite_help", slug = unique)
					else:#this person ought to be sent an invite
						#send a notification to this person to check out the group
						GroupInvite.objects.create(inviter= self.request.user,which_group_id=group_id,invitee_id=invitee)
						#GroupInvite.objects.filter(which_group=group ,invitee=self.request.user).exists() to check if an invite already exists
						invitee = User.objects.get(id=invitee)
						reply = Reply.objects.create(text=invitee.username, category='1', which_group_id=group_id,writer=self.request.user)
						GroupSeen.objects.create(seen_user=self.request.user, which_reply=reply)
			return redirect("invite")
	
class GroupListView(ListView):
	model = Group
	form_class = GroupListForm
	template_name = "group_list.html"
	paginate_by = 25

	def get_queryset(self):
		allGrps = []
		date = datetime.now()-timedelta(minutes=60)
		new_traff = GroupTraffic.objects.filter(time__gte=date,which_group__private='0').distinct('visitor','which_group').values_list('id',flat=True)
		trendingGrp_ids = GroupTraffic.objects.filter(id__in=new_traff).values('which_group').annotate(total=Count('which_group')).order_by('-total')
		trendingGrps = [Group.objects.filter(id=grp['which_group']).extra(select={"views":grp['total']})[0] for grp in trendingGrp_ids]
		#trendids = [grp['which_group'] for grp in trendingGrp_ids]
		#nonTrendingGrps = Group.objects.filter(private='0').exclude(id__in=trendids).extra(select={"views":0})
		#allGrps = trendingGrps.append(nonTrendingGrps)
		#return allGrps
		return trendingGrps

class VerifiedView(ListView):
	model = User
	form_class = VerifiedForm
	template_name = "verified.html"
	paginate_by = 100

	def get_queryset(self):
		global condemned
		return User.objects.filter(username__in=FEMALES).exclude(id__in=condemned).order_by('-userprofile__score')
		#return User.objects.exclude(id__in=condemned).order_by('-userprofile__score')[:100]

class TopView(ListView):
	model = User
	form_class = TopForm
	template_name = "top.html"

	def get_queryset(self):
		if self.request.user_banned:
			return User.objects.order_by('-userprofile__score')[:100]
		else:
			global condemned
			return User.objects.exclude(id__in=condemned).order_by('-userprofile__score')[:100]

	def get_context_data(self, **kwargs):
		context = super(TopView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["verified"] = FEMALES
		return context

class GroupPageView(ListView):
	model = Reply
	form_class = GroupPageForm
	template_name = "group.html"
	paginate_by = 15

	def get_queryset(self):
		groups = []
		replies = []
		user = self.request.user
		groups = Group.objects.filter(Q(owner=user)|Q(reply__writer=user)).distinct().values_list('id', flat=True)
		replies = Reply.objects.filter(Q(which_group__in=groups)|Q(category='1',text=user.username)).\
		exclude(category='1',writer=user).values('which_group_id').annotate(Max('id')).values_list('id__max', flat=True)
		replies_qs = Reply.objects.filter(id__in=replies).order_by('-id')[:60]
		seen_for = {groupseen.which_reply_id: groupseen for groupseen in GroupSeen.objects.filter(seen_user=user)}
		replies = [(reply, seen_for.get(reply.pk))for reply in replies_qs]
		return replies

	def get_context_data(self, **kwargs):
		context = super(GroupPageView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["verified"] = FEMALES
		return context


class GroupTypeView(FormView):
	form_class = GroupTypeForm
	template_name = "group_type.html"

class AuthPicsDisplayView(ListView):
	model = ChatPic
	template_name = "pics_display.html"
	paginate_by = 8

	def get_queryset(self):
		if self.request.user.is_authenticated():
			return ChatPic.objects.filter(owner=self.request.user).exclude(is_visible=False).order_by('-upload_time')
		else:
			return 0

class PicsChatUploadView(CreateView):
	model = ChatPic
	form_class = PicsChatUploadForm
	template_name = "pics_chat_upload.html"

	def form_valid(self, form): #this processes the form before it gets saved to the database
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		#image = f.image
		if f.image:
			image_file = clean_image_file(f.image)
			if image_file:
				f.image = image_file
			else:
				f.image = None
		else: 
			f.image = None
		unique = uuid.uuid4()
		user = self.request.user
		if user.is_authenticated():
			if f.image:
				ChatPic.objects.create(image=f.image, owner=user, times_sent=0, unique=unique)
			else:
				context = {'unique': unique}
				return render(self.request, 'error_pic.html', context)
		else:
			if f.image:
				ChatPic.objects.create(image=f.image, owner_id=1, times_sent=0, unique=unique)
			else:
				context = {'unique': unique}
				return render(self.request, 'error_pic.html', context)
		return redirect("pic_expiry", slug=unique)

class PicExpiryView(FormView):
	form_class = PicExpiryForm
	template_name = "pic_expiry_form.html"

	def get_context_data(self, **kwargs):
		context = super(PicExpiryView, self).get_context_data(**kwargs)
		unique = self.kwargs["slug"]
		context["unique"] = unique
		if self.request.user.is_authenticated():
			context["is_authenticated"] = True
		else:
			context["is_authenticated"] = False
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		unique = self.request.POST.get("unique")
		decision = self.request.POST.get("decision")
		if decision == 'sirf aik bar' and valid_uuid(unique):
			num = 1
		elif decision == 'kayee bar' and valid_uuid(unique):
			num = 2
		else:
			return redirect("pic_expiry", slug=unique)
		return redirect("captionview", num=num, slug=unique)

class CaptionView(CreateView):
	model = ChatPicMessage
	form_class = CaptionForm
	template_name = "caption.html"

	def get_context_data(self, **kwargs):
		context = super(CaptionView, self).get_context_data(**kwargs)
		unique = self.kwargs["slug"]
		num = self.kwargs["num"]
		err = self.kwargs["err"]
		context["unique"] = unique
		context["num"] = num
		context["err"] = err
		return context

	def form_valid(self,form):
		if self.request.method == 'POST':
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			user = self.request.user
			caption = f.caption
			unique = self.kwargs["slug"]
			num = self.kwargs["num"]
			if len(caption) > 149:
				return redirect("caption", num=num, slug=unique, err=1)
			which_pic = ChatPic.objects.get(unique=unique)
			if user.is_authenticated():
				message = ChatPicMessage.objects.create(which_pic=which_pic, sender=user, caption=caption, expiry_interval=num)
			else:
				message = ChatPicMessage.objects.create(which_pic=which_pic, sender_id=1, caption=caption, expiry_interval=num)
			#print "message id is: %s" % message.id
			return redirect("user_phonenumber", slug=unique, num=num, err=0, id=message.id)

class CaptionDecView(FormView):
	form_class = CaptionDecForm
	template_name = "caption_form.html"

	def get_context_data(self, **kwargs):
		context = super(CaptionDecView, self).get_context_data(**kwargs)
		unique = self.kwargs["slug"]
		num = self.kwargs["num"]
		context["unique"] = unique
		context["num"] = num
		return context

	def form_valid(self,form):
		unique = self.kwargs["slug"]
		num = self.kwargs["num"]
		dec = self.request.POST.get("dec")
		if dec == 'Haan':
			return redirect("caption", num=num, slug=unique, err=0)
		elif dec == 'Nahi':
			return redirect("user_phonenumber", slug=unique, num=num, err=0, id=0)		
		else:
			return redirect("captionview", num=num, slug=unique)

class UserPhoneNumberView(CreateView):
	model = ChatPicMessage
	form_class = UserPhoneNumberForm
	template_name = "get_user_phonenumber.html"

	# def get_initial(self):#initial is a keyword argument to a formfield that enables pre-filling in the formfield
	# 	"""
	# 	Returns the initial data to use for forms on this view.
	# 	"""
	# 	user = self.request.user
	# 	if user.is_authenticated():
	# 		try:
	# 			msg = ChatPicMessage.objects.filter(sender=user).latest('sending_time')
	# 			self.initial = {'what_number': msg.what_number} #initial needs to be passed a dictionary
	# 			return self.initial
	# 		except:
	# 			return self.initial
	# 	else:#i.e user is not authenticated
	# 		return self.initial
	# 	return self.initial

	def get_context_data(self, **kwargs):
		context = super(UserPhoneNumberView, self).get_context_data(**kwargs)
		unique = self.kwargs["slug"]
		ident = self.kwargs["id"]
		context["unique"] = unique
		num = self.kwargs["num"]
		context["decision"] = num
		context["id"] = ident
		err = self.kwargs["err"]
		context["err"] = err
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		num = f.what_number
		user = self.request.user
		unique = self.kwargs["slug"]
		ident = self.kwargs["id"]
		decision = self.kwargs["num"]
		if not num.isdigit():
			return redirect("user_phonenumber", slug=unique, num=decision, err=1, id=ident)		
		if not valid_uuid(unique):
			return redirect("user_phonenumber", slug=unique, num=decision, err=3, id=ident)
		if not valid_passcode(user=user, num=num):
			return redirect("user_phonenumber", slug=unique, num=decision, err=2, id=ident)
		if not (decision == '1' or '2'):
			return redirect("pic_expiry", slug=unique)
		which_image = ChatPic.objects.get(unique=unique)
		which_image.times_sent = which_image.times_sent + 1
		which_image.save()
		if int(ident):#i.e. it is not zero
			try:
				messageobject = ChatPicMessage.objects.get(pk=ident)
				messageobject.what_number = num
				messageobject.save()
			except:
				return redirect("user_phonenumber", slug=unique, num=decision, err=3, id=ident)
		else:#i.e. it is 0; no caption was set
			if user.is_authenticated():
				ChatPicMessage.objects.create(which_pic=which_image, sender=user, expiry_interval=decision, what_number=num)
			elif not user.is_authenticated():
				ChatPicMessage.objects.create(which_pic=which_image, sender_id=1, expiry_interval=decision, what_number=num)
			else:
				return redirect("user_phonenumber", slug=unique, num=decision, err=2, id=ident)
		try:
			on_fbs = self.request.META.get('X-IORG-FBS')
		except:
			on_fbs = False
		if on_fbs:
				#definitely on a mobile browser, but can't redirect out now, so show the web address they are to send
				return redirect("user_SMS", fbs=1, num=num)
		else:#i.e. not on internet.org, now detect whether mobile browser or desktop browser
				return redirect("user_SMS", fbs=0, num=num)

class UserSMSView(FormView):
	form_class = UserSMSForm
	template_name = "user_sms.html"

	def get_context_data(self, **kwargs):
		context = super(UserSMSView, self).get_context_data(**kwargs)
		#send_sms = str(self.kwargs["sms"])
		num = str(self.kwargs["num"])
		fbs = str(self.kwargs["fbs"])
		if (fbs == '1' or '0') and num.isdigit():
			context["legit"] = True
			context["num"] = num
			context["fbs"] = fbs
			if self.request.is_feature_phone:
				context["device"] = '1'
			elif self.request.is_phone:
				context["device"] = '2'
			elif self.request.is_tablet:
				context["device"] = '4'
			elif self.request.is_mobile:
				context["device"] = '5'
			else:
				context["device"] = '3'
			user = self.request.user
			if user.is_authenticated():
				try:
					inbox = ChatInbox.objects.filter(owner=user).latest('id')
				except:
					inbox = ChatInbox.objects.create(owner=user)#.latest('id')
				addr = inbox.pin_code
				context["addr"] = addr
				#context["authenticated"] = True
			elif not user.is_authenticated():
				inbox = ChatInbox.objects.create(owner_id=1)
				addr = inbox.pin_code
				context["addr"] = addr
				#context["authenticated"] = False
			else:
				context["legit"] = False
				#context["dev"] = None
				context["num"] = None
				context["fbs"] = None
				context["addr"] = None
				#context["send_sms"] = None
				#context["authenticated"] = None
				#context["sentence"] = None								
		else:
			context["legit"] = False
			#context["dev"] = None
			context["num"] = None
			context["fbs"] = None
			context["addr"] = None
			context["device"] = '0'
			#context["send_sms"] = None
			#context["authenticated"] = None
			#context["sentence"] = None
		return context

class DeletePicView(FormView):
	form_class = DeletePicForm
	template_name = "delete_pic.html"	

	def get_context_data(self, **kwargs):
		context = super(DeletePicView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.kwargs["slug"]
			context["unique"] = unique
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		if self.request.method == 'POST':
			unique = self.request.POST.get("ident")
			decision = self.request.POST.get("decision")
			if decision == 'Haan':
				pic = ChatPic.objects.get(unique=unique)
				if self.request.user == pic.owner:
					pic.is_visible = False
					pic.save()
				else:
					pass
			elif decision == 'Nahi':
				pass
			else:
				pass
			return redirect("auth_pics_display")
		else:
			return redirect("score_help")

class PicHelpView(FormView):
	form_class = PicHelpForm
	template_name = "pic_help.html"		

class PicPasswordView(NeverCacheMixin,FormView):
	form_class = PicPasswordForm
	template_name = "pic_password.html"

	def get_context_data(self, **kwargs):
		context = super(PicPasswordView, self).get_context_data(**kwargs)
		code = str(self.kwargs["code"])
		if code.isdigit():
			context["code"] = code
		else:
			context["code"] = None
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		mobile = self.request.POST.get("mobile_number")
		code = self.kwargs["code"]
		try:
			inbox = ChatInbox.objects.get(pin_code=code)
			user = inbox.owner #mhb11 is selected if unauthenticated user
			message = ChatPicMessage.objects.filter(what_number=mobile, sender=user).latest('sending_time')
			sender = message.sender
			caption = message.caption
			expiry_interval = message.expiry_interval
			pic = message.which_pic #the picture to be shown
			is_visible = pic.is_visible
		except:
			context = {'sender':None, 'refresh_now':False, 'exists':0, 'pic':2, 'max_time':0,'caption':None,}
			return render(self.request, 'pic.html', context)
		if message.seen:
			#i.e. the message was already seen
			if expiry_interval == '1':
				#the viewer has refreshed, so disappear the image FOREVER, but determine which error message to show
				time_now = datetime.utcnow().replace(tzinfo=utc)
				viewing_time = message.viewing_time
				difference = time_now - viewing_time
				if difference.total_seconds() < 60 and is_visible:
					#pic:3 Ye photo dekh li gaye hai. 1 minute wali photo aik dafa se ziyada nahi dekhi jaa sakti. 
					context = {'sender':sender, 'refresh_now':True, 'exists':0, 'pic':3, 'max_times':0,'caption':None,}
				elif difference.total_seconds() < 60 and not is_visible:
					#pic:-1 Ye photo bhejnay waley ne mita di hai
					context = {'sender':sender, 'refresh_now':True, 'exists':0, 'pic':-1, 'max_time':0,'caption':None,}
				elif difference.total_seconds() > 60 and is_visible:
					#pic:0 Is photo ka waqt khatam ho gaya, <b>{{ max_time|naturaltime }}</b>
					context = {'sender':sender, 'refresh_now':True, 'exists':0, 'pic':0, 'max_time':viewing_time + timedelta(minutes = 1),'caption':None,}
				else:
					#pic:1 Is photo ka time khatam ho gaya, <b>{{ max_time|naturaltime }}</b>
					context = {'sender':sender, 'refresh_now':True, 'exists':0, 'pic':1, 'max_time':viewing_time + timedelta(minutes = 1),'caption':None,}
			elif expiry_interval == '2':
				#the user has refreshed, but it was a day-long image
				time_now = datetime.utcnow().replace(tzinfo=utc)
				viewing_time = message.viewing_time
				difference = time_now - viewing_time
				if difference.total_seconds() < (60*60*24) and is_visible:
					context = {'sender':sender, 'refresh_now':False, 'exists':1, 'pic':pic, 'max_time':'kayee','caption':caption,}
				elif difference.total_seconds() < (60*60*24) and not is_visible:
					#pic:-1 Ye photo bhejnay waley ne mita di hai
					context = {'sender':sender, 'refresh_now':False, 'exists':0, 'pic':-1, 'max_time':0,'caption':None,}
				elif difference.total_seconds() > (60*60*24) and is_visible:
					#pic:0 Is photo ka waqt khatam ho gaya, <b>{{ max_time|naturaltime }}</b>
					context = {'sender':sender, 'refresh_now':False, 'exists':0, 'pic':0, 'max_time':viewing_time + timedelta(minutes = 1440),'caption':None,}
				else:
					#pic:1 Is photo ka time khatam ho gaya, <b>{{ max_time|naturaltime }}</b>
					context = {'sender':sender, 'refresh_now':False, 'exists':0, 'pic':1, 'max_time':viewing_time + timedelta(minutes = 1440),'caption':None,}
			else:# the expiry_interval was not set: ABORT
				#pic:2 Yahan dekney ke liye kuch nahi hai
				context = {'sender':sender, 'refresh_now':False, 'exists':0, 'pic':2, 'max_time':0,'caption':None,}
			return render(self.request, 'pic.html', context)
		else:
			#the message object is being opened for the first time
			if self.request.user.is_authenticated() and self.request.user == sender:
				#if the person opening it is the same person who sent the photo
				time_now = datetime.utcnow().replace(tzinfo=utc)
				context = {'sender':sender, 'refresh_now':True, 'exists':1, 'pic':pic, 'max_time':0,'caption':caption,}
			else:
				#set the seen flag of the message object
				message.seen = True
				viewing_time = datetime.utcnow().replace(tzinfo=utc)
				message.viewing_time = viewing_time
				message.save()
				if expiry_interval == '1' and is_visible:
					context = {'sender':sender, 'refresh_now':True, 'exists':1, 'pic':pic, 'max_time':'aik','caption':caption,}
				elif expiry_interval == '1' and not is_visible:
					context = {'sender':sender, 'refresh_now':False, 'exists':0, 'pic':-1, 'max_time':0,'caption':None,}
				elif expiry_interval == '2' and is_visible:
					context = {'sender':sender, 'refresh_now':False, 'exists':1, 'pic':pic, 'max_time':'kayee','caption':caption,}
				elif expiry_interval == '2' and not is_visible:
					context = {'sender':sender, 'refresh_now':False, 'exists':0, 'pic':-1, 'max_time':0,'caption':None,}
				else:
					#Yahan dekhney ke liye kuch nahi hai
					context = {'sender':sender, 'refresh_now':False, 'exists':0, 'pic':2, 'max_time':0,'caption':None,}
			return render(self.request, 'pic.html', context)

class ChangeGroupRulesView(CreateView):
	model = Group
	form_class = ChangeGroupRulesForm
	template_name = "change_group_rules.html"

	def get_context_data(self, **kwargs):
		context = super(ChangeGroupRulesView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			unique = self.kwargs["slug"]
			context["unique"] = unique
			group = Group.objects.get(unique=unique)
			context["group"] = group
			if group.private == '0':
				if not group.owner == user:
					context["unauthorized"] = True
				else:
					context["unauthorized"] = False
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		user = self.request.user
		if self.request.user_banned:
			return redirect("profile", slug=user.username)
		else:
			rules = self.request.POST.get("rules")
			unique = self.request.POST.get("unique")
			group = Group.objects.get(unique=unique)
			if group.private == '0' and group.owner != user:
				return redirect("score_help")
			group.rules = rules
			group.save()
			Reply.objects.create(text=rules ,which_group=group ,writer=user ,category='5')
			return redirect("public_group", slug=unique)

class ChangeGroupTopicView(CreateView):
	model = Group
	form_class = ChangeGroupTopicForm
	template_name = "change_group_topic.html"

	def get_context_data(self, **kwargs):
		context = super(ChangeGroupTopicView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			unique = self.kwargs["slug"]
			if not valid_uuid(unique):
				unique = self.request.session['unique_id']
			if unique:	
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
				if group.private == '0':
					if not group.owner == user:
						context["unauthorized"] = True
					else:
						context["unauthorized"] = False
			else:
				context["unauthorized"] = True
				return context
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		user = self.request.user
		if self.request.user_banned:
			return redirect("profile", slug=user.username)
		else:
			topic = self.request.POST.get("topic")
			unique = self.request.POST.get("unique")
			group = Group.objects.get(unique=unique)
			if group.private == '0' and group.owner != user:
				return redirect("score_help")
			group.topic = topic
			group.save()
			Reply.objects.create(text=topic ,which_group=group , writer=user, category='4')
			if group.private == '1':
				return redirect("private_group", slug=unique)
			elif group.private == '0':
				return redirect("public_group", slug=unique)
			else:
				return redirect("outsider_group", slug=unique)

@ratelimit(rate='1/s')
def outsider_group(request, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 1 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': slug}
		return render(request, 'penalty_outsider.html', context)
	else:
		if valid_uuid(slug):
			request.session["unique_outsider"] = slug
			#request.session["outsider_path"] = 'outsider'
			return redirect("outsider_group_reply")
		else:
			return redirect("profile", request.user.username)

class OutsiderGroupView(CreateView):
	model = Reply
	form_class = OutsiderGroupForm
	template_name = "outsider_group_reply.html"

	def get_context_data(self, **kwargs):
		context = super(OutsiderGroupView, self).get_context_data(**kwargs)
		unique = self.request.session["unique_outsider"]
		context["unique"] = unique
		group = Group.objects.get(unique=unique)
		if 'mehfilbahir' in self.request.path and group.private == '2':
			context["switching"] = False
			context["group"] = group
			replies = Reply.objects.filter(which_group_id=group.id).order_by('-submitted_on')[:25]#get DB call
			context["replies"] = replies
			context["sms_url"] = "https://http-damadam-pk.0.freebasics.com/mehfil/"+unique+"/bahir/"
			if self.request.user.is_authenticated():
				context["ensured"] = FEMALES
				context["members"] = User.objects.filter(reply__which_group=group).distinct()#get DB call
				own_reply = Reply.objects.filter(which_group_id=group.id, writer_id=self.request.user.id).exists()#get DB call
				if own_reply: #user wrote a reply too (whether or not they are group admin)
					seen_replies=[]
					latest_own_reply = Reply.objects.filter(which_group=group, writer=self.request.user).latest('submitted_on')
					if latest_own_reply in replies: #i.e. user's latest reply is in the 25 replies shown
						#print "inside"
						less_than_replies = [reply for reply in replies if reply.submitted_on < latest_own_reply.submitted_on]
						less_than_replies_ids = [reply.id for reply in less_than_replies]
						more_than_replies = [reply for reply in replies if reply.submitted_on >= latest_own_reply.submitted_on]
						more_than_replies_ids = [reply.id for reply in more_than_replies]
						#all seen objects of less than replies and more than replies
						less_than_seen_replies = Reply.objects.filter(id__in=less_than_replies_ids,groupseen__seen_user=self.request.user)
						more_than_seen_replies = Reply.objects.filter(id__in=more_than_replies_ids,groupseen__seen_user=self.request.user)
						insert_list = []
						for reply in less_than_replies:#sweeping unseen replies under the proverbial rug
							if reply not in less_than_seen_replies:
								#kicks in when a user jumps into the middle of a conversation.
								insert_list.append(GroupSeen(seen_user= self.request.user,which_reply=reply))
								seen_replies.append(reply)
								#print "inside"
							else:
								seen_replies.append(reply)
								#print seen_replies
						GroupSeen.objects.bulk_create(insert_list)
						for reply in more_than_replies:
							#####################################################
							if reply in more_than_seen_replies:
								seen_replies.append(reply)
					context["seenreplies"] = seen_replies
					object_list = []
					for response in replies:
						if response not in seen_replies:
							#bulk creating seen objects for every unseen reply, for that particular user
							object_list.append(GroupSeen(seen_user= self.request.user,which_reply=response))
					GroupSeen.objects.bulk_create(object_list)
				else: #user didn't create group, or replied. User is visiting
					context["seenreplies"] = replies
			else:
				host = group.owner.username
				context["host"] = host
				context["number"] = group.owner.userprofile.mobilenumber
		else:
			context["switching"] = True
		return context

	def form_valid(self, form): #this processes the public form before it gets saved to the database
		if self.request.user_banned:
			return redirect("group_page")
		else:
			if self.request.user.is_authenticated():
				if self.request.user.userprofile.score < -25:
					HellBanList.objects.create(condemned=self.request.user)
					self.request.user.userprofile.score = random.randint(10,71)
					self.request.user.userprofile.save()
					return redirect("group_page")
				f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
				text = f.text
				#if text == self.request.user.userprofile.previous_retort:
				score = fuzz.ratio(text, self.request.user.userprofile.previous_retort)
				if score > 90:
					self.request.session["unique_outsider"] = None
					return redirect("group_page")#, pk= reply.answer_to.id)
				else:
					self.request.user.userprofile.previous_retort = text
					#self.request.user.userprofile.score = self.request.user.userprofile.score + 2
					self.request.user.userprofile.save()
					#print "image: %s" % f.image
					if f.image:
						image_file = clean_image_file(f.image)
						if image_file:
							f.image = image_file
						else:
							f.image = None
					else: 
						f.image = None
					if self.request.is_feature_phone:
						device = '1'
					elif self.request.is_phone:
						device = '2'
					elif self.request.is_tablet:
						device = '4'
					elif self.request.is_mobile:
						device = '5'
					else:
						device = '3'
					unique = self.request.session["unique_outsider"]
					which_group = Group.objects.get(unique=unique)
					self.request.session["unique_outsider"] = None
					reply = Reply.objects.create(writer=self.request.user, which_group=which_group, text=text, image=f.image, device=device)
					GroupSeen.objects.create(seen_user= self.request.user,which_reply=reply)#creating seen object for reply created
					return redirect("outsider_group", slug=unique)
			else:
				f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
				if f.image:
					image_file = clean_image_file(f.image)
					if image_file:
						f.image = image_file
					else:
						f.image = None
				else: 
					f.image = None
				writer = User(id=8) # ALWAYS set this ID to unregistered_bhoot
				unique = self.request.session["unique_outsider"]
				group = Group.objects.get(unique=unique)
				if self.request.is_feature_phone:
					device = '1'
				elif self.request.is_phone:
					device = '2'
				elif self.request.is_tablet:
					device = '4'
				elif self.request.is_mobile:
					device = '5'
				else:
					device = '3'
				Reply.objects.create(text=f.text,which_group=group,writer=writer, image=f.image, device=device)
				self.request.session["unique_outsider"] = None
				return redirect("outsider_group", slug=unique)

@ratelimit(rate='1/s')
def public_group(request, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 2 * -2
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': slug}
		return render(request, 'penalty_public.html', context)
	else:
		if valid_uuid(slug):
			request.session["public_uuid"] = slug
			return redirect("public_group_reply")
		else:
			return redirect("score_help")

class PublicGroupView(CreateView):
	model = Reply
	form_class = PublicGroupReplyForm
	template_name = "public_group_reply.html"

	def get_context_data(self, **kwargs):
		context = super(PublicGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				unique = self.request.session["public_uuid"]	
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
			except:
				context["switching"] = True
				context["group_banned"] = False
				return context
			#print self.request.path
			if 'awami' in self.request.path and group.private == '0': 
				context["switching"] = False
				context["group"] = group
				if GroupBanList.objects.filter(which_user_id=self.request.user.id,which_group_id=group.id).exists():
					context["group_banned"]=True
					return context#no need to process more
				GroupTraffic.objects.create(visitor_id=self.request.user.id,which_group_id=group.id)#create DB call
				context["ensured"] = FEMALES
				replies = Reply.objects.filter(which_group_id=group.id).exclude(category='1').order_by('-submitted_on')[:25]#get DB call
				time_now = datetime.utcnow().replace(tzinfo=utc)
				writers_with_times = [(reply,reply.writer,(time_now-reply.submitted_on).total_seconds()) for reply in replies]
				most_recent = {}
				for reply,user,time in writers_with_times:
					most_recent[user] = min(most_recent.get(user,time),time)
				replies_writers_times = [(reply,user,most_recent[user]) for reply,user, _ in writers_with_times]
				#print "REPLIES WITH MIN TIMES %s" % newList
				context["replies"] = replies_writers_times
				#context["replies"] = replies
			else:
				#print "outside"
				context["switching"] = True
				context["group_banned"] = False
		return context

	def form_valid(self, form): #this processes the public form before it gets saved to the database
		pk = self.request.session["public_uuid"]
		try:
			which_group = Group.objects.get(unique=pk)
		except:
			return redirect("profile", self.request.user.username )
		if self.request.user_banned or GroupBanList.objects.filter(which_user_id=self.request.user.id, which_group_id=which_group.id).exists():
			return redirect("group_page")
		else:
			if self.request.user.userprofile.score < -25:
				HellBanList.objects.create(condemned=self.request.user)
				self.request.user.userprofile.score = random.randint(10,71)
				self.request.user.userprofile.save()
				return redirect("group_page")
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			text = f.text
			score = fuzz.ratio(text, self.request.user.userprofile.previous_retort)
			if score > 87:
				self.request.user.userprofile.score = self.request.user.userprofile.score - 10
				self.request.user.userprofile.save()
				self.request.session["public_uuid"] = None
				return redirect("public_group", slug=pk)
			else:
				self.request.user.userprofile.previous_retort = text
				self.request.user.userprofile.score = self.request.user.userprofile.score + 2
				self.request.user.userprofile.save()
				#print "image: %s" % f.image
				if f.image:
					image_file = clean_image_file(f.image)
					if image_file:
						f.image = image_file
					else:
						f.image = None
				else: 
					f.image = None
				if self.request.is_feature_phone:
					device = '1'
				elif self.request.is_phone:
					device = '2'
				elif self.request.is_tablet:
					device = '4'
				elif self.request.is_mobile:
					device = '5'
				else:
					device = '3'
				reply = Reply.objects.create(writer=self.request.user, which_group=which_group, text=text, image=f.image, device=device)
				self.request.session["public_uuid"] = None
				return redirect("public_group", slug=pk)

@ratelimit(rate='1/s')
def private_group(request, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	#print "The remote ip of the requester is: %s" % request.META.get('REMOTE_ADDR', None)
	if was_limited:
		deduction = 1 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': slug}
		return render(request, 'penalty.html', context)
	else:
		if valid_uuid(slug):
			request.session['unique_id'] = slug
			request.session["private_uuid"] = slug
		else:
			return redirect("score_help")
		return redirect("private_group_reply")
	

class PrivateGroupView(CreateView): #get_queryset doesn't work in CreateView (it's a ListView thing!)
	model = Reply
	form_class = PrivateGroupReplyForm		
	template_name = "private_group_reply.html"

	def get_context_data(self, **kwargs):
		context = super(PrivateGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				unique = self.request.session['unique_id']
			except:
				context["switching"] = True
				return context
			if unique:
				context["unique"] = unique
			else:
				context["switching"] = True
				return context
			group = Group.objects.get(unique=unique)#get DB call
			context["group"] = group
			if 'private' in self.request.path and group.private=='1':
				context["switching"] = False
				GroupTraffic.objects.create(visitor=self.request.user,which_group=group)
				context["ensured"] = FEMALES
				replies = Reply.objects.filter(which_group=group).order_by('-submitted_on')[:25]#get DB call
				time_now = datetime.utcnow().replace(tzinfo=utc)
				writers_with_times = [(reply,reply.writer,(time_now-reply.submitted_on).total_seconds()) for reply in replies]
				most_recent = {}
				for reply,user,time in writers_with_times:
					most_recent[user] = min(most_recent.get(user,time),time)
				replies_writers_times = [(reply,user,most_recent[user]) for reply,user, _ in writers_with_times]
				#print "REPLIES WITH MIN TIMES %s" % newList
				context["replies"] = replies_writers_times
				#context["time"] = min_time
				if not self.request.user_banned:#do the following ONLY if user isn't hell-banned
					members = User.objects.filter(reply__which_group=group).distinct()#get DB call
					context["members"] = members
					own_reply = Reply.objects.filter(which_group_id=group.id, writer_id=self.request.user.id).exists()#get DB call
					if own_reply: #user wrote a reply too (whether or not they are group admin)
						seen_replies=[]
						latest_own_reply = Reply.objects.filter(which_group=group, writer=self.request.user).latest('submitted_on')
						#print latest_own_reply
						if latest_own_reply in replies: #i.e. user's latest reply is in the 25 replies shown
							less_than_replies = [reply for reply in replies if reply.submitted_on < latest_own_reply.submitted_on]
							#print less_than_replies
							less_than_replies_ids = [reply.id for reply in less_than_replies]
							more_than_replies = [reply for reply in replies if reply.submitted_on >= latest_own_reply.submitted_on]
							#print more_than_replies
							more_than_replies_ids = [reply.id for reply in more_than_replies]
							#all seen objects of less than replies and more than replies
							less_than_seen_replies = Reply.objects.filter(id__in=less_than_replies_ids,groupseen__seen_user=self.request.user)
							more_than_seen_replies = Reply.objects.filter(id__in=more_than_replies_ids,groupseen__seen_user=self.request.user)
							insert_list = []
							for reply in less_than_replies:#sweeping unseen replies under the proverbial rug
								if reply not in less_than_seen_replies:
									#this case kicks in when a user jumps into the middle of a conversation
									insert_list.append(GroupSeen(seen_user= self.request.user,which_reply=reply))
									seen_replies.append(reply)
								else:
									seen_replies.append(reply)
							GroupSeen.objects.bulk_create(insert_list)
							for reply in more_than_replies:
								#####################################################
								if reply in more_than_seen_replies:
									seen_replies.append(reply)
						context["seenreplies"] = seen_replies
						object_list = []
						for response in replies:
							if response not in seen_replies:
								#bulk creating seen objects for every unseen reply, for that particular user
								object_list.append(GroupSeen(seen_user= self.request.user,which_reply=response))
						GroupSeen.objects.bulk_create(object_list)
					else: #user didn't create group, or replied. User is visiting
						context["seenreplies"] = replies
						#return context
			else:
				context["switching"] = True
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		if self.request.user_banned:
			return redirect("group_page")
		else:
			if self.request.user.userprofile.score < -25:
				HellBanList.objects.create(condemned=self.request.user)
				self.request.user.userprofile.score = random.randint(10,71)
				self.request.user.userprofile.save()
				return redirect("group_page")
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			text = f.text
			score = fuzz.ratio(text, self.request.user.userprofile.previous_retort)
			if score > 90:
				return redirect("private_group", self.request.session['unique_id'])#, pk= reply.answer_to.id)
			else:
				self.request.user.userprofile.previous_retort = text
				self.request.user.userprofile.score = self.request.user.userprofile.score + 1
				self.request.user.userprofile.save()
				#print "image: %s" % f.image
				if f.image:
					image_file = clean_image_file(f.image)
					if image_file:
						f.image = image_file
					else:
						f.image = None
				else: 
					f.image = None
				if self.request.is_feature_phone:
					device = '1'
				elif self.request.is_phone:
					device = '2'
				elif self.request.is_tablet:
					device = '4'
				elif self.request.is_mobile:
					device = '5'
				else:
					device = '3'
				which_group = Group.objects.get(unique=self.request.POST.get("unique"))
				reply = Reply.objects.create(writer=self.request.user, which_group=which_group, text=text, image=f.image, device=device)
				GroupSeen.objects.create(seen_user= self.request.user,which_reply=reply)#creating seen object for reply created
				self.request.session['unique_id'] = None
				return redirect("private_group", reply.which_group.unique)
	
@ratelimit(rate='1/s')
def welcome_pk(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 1 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': slug}
		return render(request, 'penalty_welcome.html', context)
	else:
		if pk.isdigit():
			request.session["welcome_pk"] = pk
			return redirect("welcome")
		else:
			return redirect("group_help")

class WelcomeView(FormView):
	form_class = WelcomeForm
	template_name = "welcome.html"

	def get_context_data(self, **kwargs):
		context = super(WelcomeView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["target_user"] = User.objects.get(id=self.request.session["welcome_pk"])
		return context

class WelcomeMessageView(CreateView):
	model = Publicreply
	form_class = WelcomeMessageForm
	template_name = "welcome_message.html"

	def get_context_data(self, **kwargs):
		context = super(WelcomeMessageView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["target_user"] = User.objects.get(id=self.request.session["welcome_pk"])
			context["option"] = self.kwargs["option"]
		return context

def mehfil_help(request, pk=None, num=None, *args, **kwargs):
	if pk.isdigit() and num.isdigit():
		request.session['user_pk'] = pk
		request.session['link_id'] = num
		return redirect("mehfil_help")
	else:
		return redirect("score_help")

@ratelimit(rate='1/s')
def reply_pk(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'pk': pk}
		return render(request, 'penalty_publicreply.html', context)
	else:
		if pk.isdigit():
			request.session["link_pk"] = pk
			return redirect("reply")
		else:
			return redirect("score_help")

class PublicreplyView(CreateView): #get_queryset doesn't work in CreateView (it's a ListView thing!)
	model = Publicreply
	form_class = PublicreplyForm
	template_name = "reply.html"

	def get_context_data(self, **kwargs):
		context = super(PublicreplyView, self).get_context_data(**kwargs)
		context["authenticated"] = False
		if self.request.user.is_authenticated():
			context["authenticated"] = True
			score = self.request.user.userprofile.score
			context["score"] = score
			try:
				link = Link.objects.get(id=self.request.session["link_pk"])
			except:
				context["error"] = True
				return context
			#is_notification = self.kwargs["is_notif"]
			context["error"] = False
			context["parent"] = link #the parent link
			context["ensured"] = FEMALES
			context["random"] = random.sample(xrange(1,52),10) #select 10 random emoticons out of 52
			if self.request.user_banned:
				replies = Publicreply.objects.filter(answer_to=link).order_by('-id')[:25]
				context["replies"] = replies
				context["seenreplies"] = context["replies"]#i.e. all replies are seen for hell-banned person, none are *new*
			else:
				#global condemned
				replies = Publicreply.objects.filter(answer_to=link).order_by('-id')[:25]
				context["replies"] = replies #latest replies, sans condemned
				own_reply = Publicreply.objects.filter(answer_to=link, submitted_by=self.request.user).exists()
				if link.submitter == self.request.user and own_reply==False: #user only wrote parent link, and has never replied under it
					seen_replies = []
					reply_ids = [reply.id for reply in replies] #the ids of the latest 25 replies
					seen_replies = Publicreply.objects.filter(id__in=reply_ids,publicreply_seen_related__seen_user=self.request.user)
					context["seenreplies"] = seen_replies #all replies, from the latest 25, that were seen by the user
					insert_list=[]
					for response in replies:
						if response not in seen_replies:
							#creating seen objects for every unseen reply, for that particular user
							#Seen.objects.create(seen_user= self.request.user,which_reply=response,seen_status=True)
							insert_list.append(Seen(seen_user=self.request.user,which_reply=response,seen_status=True))
					Seen.objects.bulk_create(insert_list)
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
						insert_list=[]
						for reply in less_than_replies:#sweeping unseen replies under the proverbial rug
							if reply not in less_than_seen_replies:
								#Seen.objects.create(seen_user= self.request.user,which_reply=reply,seen_status=True)
								insert_list.append(Seen(seen_user= self.request.user,which_reply=reply,seen_status=True))
								seen_replies.append(reply)
							else:
								seen_replies.append(reply)
						Seen.objects.bulk_create(insert_list)
						for reply in more_than_replies:
							#####################################################
							if reply in more_than_seen_replies:
								seen_replies.append(reply)
					context["seenreplies"] = seen_replies
					object_list=[]
					for response in replies:
						if response not in seen_replies:
							#creating seen objects for every unseen reply, for that particular user
							#Seen.objects.create(seen_user= self.request.user,which_reply=response,seen_status=True)
							object_list.append(Seen(seen_user= self.request.user,which_reply=response,seen_status=True))
					Seen.objects.bulk_create(object_list)
				else: #user didn't write parent link, nor ever replied
					context["seenreplies"] = replies
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		description = self.request.POST.get("description")
		pk = self.request.session["link_pk"]
		self.request.session["link_pk"] = None
		score = fuzz.ratio(description, self.request.user.userprofile.previous_retort)
		if score > 85:
			try:
				return redirect("reply_pk", pk=pk)#, pk= reply.answer_to.id)
			except:
				self.request.user.userprofile.score = self.request.user.userprofile.score - 3
				self.request.user.userprofile.save()
				return redirect("profile", slug=self.request.user.username)
		else:
			if self.request.user_banned:
				return redirect("score_help")
			else:
				self.request.user.userprofile.previous_retort = description
				self.request.user.userprofile.score = self.request.user.userprofile.score + 3
				self.request.user.userprofile.save()
				answer_to = Link.objects.get(id=self.request.POST.get("object_id"))
				answer_to.reply_count = answer_to.reply_count + 1
				if self.request.is_feature_phone:
					device = '1'
				elif self.request.is_phone:
					device = '2'
				elif self.request.is_tablet:
					device = '4'
				elif self.request.is_mobile:
					device = '5'
				else:
					device = '3'
				reply= Publicreply.objects.create(submitted_by=self.request.user, answer_to=answer_to, description=description, category='1', device=device)
				Seen.objects.create(seen_user= self.request.user,which_reply=reply,seen_status=True)#creating seen object for reply created
				answer_to.save()
				try:
					return redirect("reply_pk", pk=pk)
				except:
					self.request.user.userprofile.score = self.request.user.userprofile.score - 3
					self.request.user.userprofile.save()
					return redirect("profile", slug=self.request.user.username)

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
	paginate_by = 15

	def get_queryset(self):
		#queryset to return all relevant links (own & others), sorted by unseen links queryset = Link.objects.order_by('-submitted_on')[:180]
		all_links = []
		all_links_qset = []
		all_links = GetNonReplyLinks(self.request.user) #returns a list, upto 90 links
		if all_links:
			all_link_ids = [link.id for link in all_links]
			all_links_qset = Link.objects.filter(id__in=all_link_ids)
			all_links_qset = all_links_qset.annotate(date=Max('publicreply__submitted_on')).order_by('-date')
			return all_links_qset
		return all_links_qset

	def get_context_data(self, **kwargs):
		context = super(UnseenActivityView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			#user = User.objects.filter(username=self.kwargs['slug'])
			global condemned
			eachlink = defaultdict(list)
			index = 0
			seen_replies = []
			context["verify"] = FEMALES
			link_ids = [link.id for link in context["object_list"]]
			#latest_replies = Publicreply.objects.filter(answer_to_id__in=link_ids).order_by('answer_to','-submitted_on').distinct('answer_to')
			seen_replies = Publicreply.objects.filter(answer_to_id__in=link_ids,publicreply_seen_related__seen_user = self.request.user)#all seen replies to all links in object_list
			#self.request.user_banned should not be part of eachlink at all (for unbanned user)
			for link in context["object_list"]:
				try: #i.e. for only links that have replies, check if latest reply has seen object
					if self.request.user_banned:
						latest_reply = link.publicreply_set.latest('submitted_on')
					else:
						latest_reply = link.publicreply_set.exclude(submitted_by_id__in=condemned).latest('submitted_on')
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
			# try:
			# 	user_object = Unseennotification.objects.get(recipient=self.request.user)
			# 	user_object.timestamp = datetime.utcnow().replace(tzinfo=utc) #time now
			# 	user_object.save()
			# except:
			# 	Unseennotification.objects.create(recipient=self.request.user,timestamp=datetime.utcnow().replace(tzinfo=utc))
			#print eachlink
		return context


class UserActivityView(ListView):
	model = Link
	slug_field = "username"
	template_name = "user_activity.html"
	paginate_by = 15

	def get_queryset(self):
		username = self.kwargs['slug']
		user = User.objects.get(username=username)
		return Link.objects.filter(submitter=user).order_by('-id')[:30]# instead of Link.with_votes.filter

	def get_context_data(self, **kwargs):
		context = super(UserActivityView, self).get_context_data(**kwargs)
		context["can_vote"] = False
		if self.request.user.is_authenticated():
			if self.request.user_banned and (self.request.user.username ==  self.kwargs['slug']):
					return redirect("error")
			else:
				global condemned
				if self.request.user.userprofile.score > 9:
					context["can_vote"] = True
				links_in_page = [link.id for link in context["object_list"]]#getting ids of all user's links in page
				if self.request.user_banned:
					vote_cluster = Vote.objects.filter(link_id__in=links_in_page) # votes on user's link in page
				else:
					vote_cluster = Vote.objects.filter(link_id__in=links_in_page).exclude(voter_id__in=condemned) # votes on user's link in page
				context["vote_cluster"] = vote_cluster
				voted = vote_cluster.filter(voter=self.request.user)
				context["voted"] = voted.values_list('link_id', flat=True)
				context["verified"] = FEMALES
			return context
		else:
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

	def get_form_kwargs(self):
		"""
		Returns the keyword arguments for instantiating the form.
		"""
		kwargs = super(UserProfileEditView, self).get_form_kwargs()
		kwargs.update({'user': self.request.user})
		return kwargs

	def get_object(self, queryset=None):
		return UserProfile.objects.get_or_create(user=self.request.user)[0]

	def get_success_url(self):
		return reverse_lazy("profile", kwargs={'slug': self.request.user})


class UserSettingsEditView(UpdateView):
	model = UserSettings
	form_class = UserSettingsForm
	template_name = "edit_settings.html"

	def get_object(self, queryset=None): #loading the current state of settings
		return UserSettings.objects.get_or_create(user=self.request.user)[0]

	def get_success_url(self): #which URL to go back once settings are saved?
		return reverse_lazy("profile", kwargs={'slug': self.request.user})

@ratelimit(rate='1/s')
def link_create_pk(request, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 2 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': 'ID'}
		return render(request, 'penalty_linkcreate.html', context)
	else:
		return redirect("link_create")

class LinkCreateView(CreateView):
	model = Link
	form_class = LinkForm

	def get_context_data(self, **kwargs):
		context = super(LinkCreateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["official"] = FEMALES
			context["allowed"] = ALLOWED
			context["random"] = random.sample(xrange(1,52),10) #select 10 random emoticons out of 52
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		user = self.request.user
		f.rank_score = 10.1#round(0 * 0 + secs / 45000, 8)
		if user.userprofile.score < -25:
			if not HellBanList.objects.filter(condemned=user).exists(): #only insert user in hell-ban list if she isn't there already
				HellBanList.objects.create(condemned=user) #adding user to hell-ban list
				user.userprofile.score = random.randint(10,71)
				user.userprofile.save()
				f.submitter = user
			else:
				f.submitter = user # ALWAYS set this ID to unregistered_bhoot
		else:
			f.submitter = user
			f.submitter.userprofile.score = f.submitter.userprofile.score + 2 #adding 2 points every time a user submits new content
		f.with_votes = 0
		f.category = '1'
		if self.request.is_feature_phone:
			f.device = '1'
		elif self.request.is_phone:
			f.device = '2'
		elif self.request.is_tablet:
			f.device = '4'
		elif self.request.is_mobile:
			f.device = '5'
		else:
			f.device = '3'
		try:
			#if f.description==f.submitter.userprofile.previous_retort:
			score = fuzz.ratio(f.description, f.submitter.userprofile.previous_retort)
			if score > 88:
				return redirect("link_create_pk")
			else:
				pass
		except:
			pass
		f.submitter.userprofile.previous_retort = f.description
		if f.image_file:
			image_file = clean_image_file(f.image_file)
			if image_file:
				f.image_file = image_file
			else: f.image_file = None
		f.save()
		f.submitter.userprofile.save()
		return super(CreateView, self).form_valid(form)

	def get_success_url(self): #which URL to go back once settings are saved?
		return reverse_lazy("home")

@ratelimit(rate='1/s')
def kick_pk(request, pk=None, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 50 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': slug}
		return render(request, 'penalty_kick.html', context)
	else:
		if pk.isdigit() and valid_uuid(slug):
			request.session["kick_pk"] = pk
			request.session["kick_slug"] = slug
			return redirect("kick")
		else:
			return redirect("score_help")

class KickView(FormView):
	form_class = KickForm
	template_name = "kick.html"

	def get_context_data(self, **kwargs):
		context = super(KickView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.request.session["kick_slug"]
			context["unique"] = unique
			group = Group.objects.get(unique=unique)
			context["unauthorized"] = False
			if group.private != '0':
				context["unauthorized"] = True
			context["owner"] = group.owner
			if group.owner != self.request.user:
				context["culprit"] = self.request.user
			else:
				culprit_id = self.request.session["kick_pk"]
				if Reply.objects.filter(writer_id=culprit_id,which_group=group).exists():
					culprit = User.objects.get(id=culprit_id)
					context["culprit"] = culprit
				else:
					context["unauthorized"] = True
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			if self.request.user_banned:
				return redirect("group_page")
			elif self.request.user.userprofile.score < -25:
				HellBanList.objects.create(condemned=self.request.user)
				self.request.user.userprofile.score = random.randint(10,71)
				self.request.user.userprofile.save()
				return redirect("group_page")
			else:
				unique = self.request.session["kick_slug"]
				self.request.session["kick_slug"] = None
				group = Group.objects.get(unique=unique)
				if group.private == '0':
					if group.owner != self.request.user:
						return redirect("public_group", slug=unique)
					else:
						pk = self.request.session["kick_pk"]
						self.request.session["kick_pk"] = None
						culprit = User.objects.get(id=pk)
						if GroupBanList.objects.filter(which_user=culprit, which_group=group).exists():# already kicked and banned
							return redirect("public_group", slug=unique)
						else:
							GroupBanList.objects.create(which_user_id=pk,which_group_id=group.id)#placing the person in ban list
							culprit.userprofile.score = culprit.userprofile.score - 50 #cutting 50 points
							culprit.userprofile.save()
							text = culprit.username
							reply = Reply.objects.create(text=text, which_group_id=group.id, writer=self.request.user, category='2')
							return redirect("public_group", slug=unique)
				else:
					return redirect("score_help")

@ratelimit(rate='1/s')
def groupreport_pk(request, slug=None, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 10 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': slug}
		return render(request, 'penalty_groupreport.html', context)
	else:	
		if pk.isdigit() and valid_uuid(slug):
			request.session["groupreport_slug"] = slug
			request.session["groupreport_pk"] = pk
			return redirect("group_report")
		else:
			return redirect("about")

class GroupReportView(FormView):
	form_class = GroupReportForm
	template_name = "group_report.html"

	def get_context_data(self, **kwargs):
		context = super(GroupReportView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.request.session["groupreport_slug"]
			context["unique"] = unique
			reply_id = self.request.session["groupreport_pk"]
			group = Group.objects.get(unique=unique)
			if GroupCaptain.objects.filter(which_user=self.request.user, which_group=group).exists() and Reply.objects.filter(pk=reply_id, which_group=group).exists():
				#print GroupCaptain.objects.filter(which_user=self.request.user).exists()
				context["captain"] = True
				reply = Reply.objects.get(id=reply_id)
				context["reply"] = reply
			else:
				context["captain"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			unique = Group.objects.get(unique=self.request.session["groupreport_slug"])
			self.request.session["groupreport_slug"] = None
			if unique.private != '0':
				return redirect("score_help")
			if self.request.user_banned or GroupBanList.objects.filter(which_user_id=self.request.user.id, which_group=unique).exists():
				return redirect("group_page")
			elif self.request.user.userprofile.score < -25:
				HellBanList.objects.create(condemned=self.request.user)
				self.request.user.userprofile.score = random.randint(10,71)
				self.request.user.userprofile.save()
				return redirect("group_page")
			else:
				report = self.request.POST.get("report")
				if report == 'Haan mita do':
					reply_id = self.request.session["groupreport_pk"]
					self.request.session["groupreport_pk"] = None
					reply = get_object_or_404(Reply, pk=reply_id)
					if not GroupCaptain.objects.filter(which_user=self.request.user, which_group=unique).exists():
						#print GroupCaptain.objects.filter(which_user=self.request.user, which_group=Group.objects.get(unique=unique)).exists()
						return redirect("public_group", slug=unique.unique)
					else: #i.e. the person requesting this is a group captain
						reply.category = '3'
						reply.text = self.request.user.username
						reply.writer.userprofile.score = reply.writer.userprofile.score - 10
						reply.writer.userprofile.save()
						reply.save()
						return redirect("public_group", slug=unique.unique)
				else:
					return redirect("public_group", slug= unique.unique)

class ReportView(FormView):
	form_class = ReportForm

	def form_valid(self, form):
		if self.request.method == 'POST':
			if not self.request.user_banned:
				report = self.request.POST.get("report")
				if report == 'Haan ye gher ikhlaqi hai':
					report = self.request.POST.get("reply")
					reply = get_object_or_404(Publicreply, pk=report)
					reply.abuse = True
					reply.submitted_by.userprofile.score = reply.submitted_by.userprofile.score - 3
					reply.submitted_by.userprofile.save()
					reply.save()
					self.request.session["report_pk"] = None
					self.request.session["linkreport_pk"] = None
					return redirect("reply_pk", pk=reply.answer_to.id)
				else:
					report = self.request.POST.get("reply")
					reply = get_object_or_404(Publicreply, pk=report)
					self.request.session["report_pk"] = None
					self.request.session["linkreport_pk"] = None
					return redirect("reply_pk", pk= reply.answer_to.id)
			else:
				return redirect("score_help")

class WelcomeReplyView(FormView):
	form_class = WelcomeReplyForm

	def form_valid(self, form):
		if self.request.method == 'POST':
			if self.request.user_banned:
				return redirect("score_help")
			else:
				pk = self.request.session["welcome_pk"]
				target = User.objects.get(pk=pk)
				current = User.objects.latest('id')
				num = current.id
				if (num-100) <= int(pk) <= (num+100):
					option = self.request.POST.get("opt")
					message = self.request.POST.get("msg")
					if self.request.is_feature_phone:
						device = '1'
					elif self.request.is_phone:
						device = '2'
					elif self.request.is_tablet:
						device = '4'
					elif self.request.is_mobile:
						device = '5'
					else:
						device = '3'
					self.request.user.userprofile.score = self.request.user.userprofile.score + 1
					self.request.user.userprofile.save()
					if Link.objects.filter(submitter=target).exists():
						parent = Link.objects.filter(submitter=target).latest('id')
						parent.reply_count = parent.reply_count + 1
						parent.save()
					else:
						num = random.randint(1,5)
						if num == 1:
							parent = Link.objects.create(description='I am new', submitter=target, reply_count=1, device=device)
						elif num == 2:
							parent = Link.objects.create(description='Salam, Im new', submitter=target, reply_count=1, device=device)
						elif num == 3:
							parent = Link.objects.create(description='mein new hun', submitter=target, reply_count=1, device=device)
						elif num == 4:
							parent = Link.objects.create(description='hi every1', submitter=target, reply_count=1, device=device)
						else:
							parent = Link.objects.create(description='damadam mast qalander', submitter=target, reply_count=1, device=device)						
					#print "PARENT IS: %s" % parent
					if option == '1' and message == 'Barfi khao aur mazay urao!':
						description = target.username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '1' and message == 'Yeh zalim barfi try kar yar!':
						description = target.username+" welcome! Kesey ho? Yeh zalim barfi try kar yar (barfi)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '1' and message == 'Is barfi se mu meetha karo!':
						description = target.username+" assalam-u-alaikum! Is barfi se mu meetha karo (barfi)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '2' and message == 'Aik plate laddu se life set!':
						description = target.username+" Damadam pe welcome! One plate laddu se life set (laddu)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '2' and message == 'Ye saray laddu aap ke liye!':
						description = target.username+" kya haal he? Ye laddu aap ke liye (laddu)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '2' and message == 'Laddu khao, jaan banao yar!':
						description = target.username+" welcum! Life set hei? Laddu khao, jaan banao (laddu)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '3' and message == 'Jalebi khao aur ayashi karo!':
						description = target.username+" welcomeee! Yar kya hal he? Jalebi khao aur ayashi karo (jalebi)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '3' and message == 'Jalebi meri pasandida hai!':
						description = target.username+" kaisey ho? Jalebi meri pasandida hai! Tumhari bhi? (jalebi)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					elif option == '3' and message == 'Is jalebi se mu metha karo!':
						description = target.username+" salam! Is jalebi se mu meetha karo (jalebi)"
						reply = Publicreply.objects.create(submitted_by=self.request.user, answer_to=parent, description=description, device=device)
					else:
						return redirect("score_help")
					global condemned
					replies = list(Publicreply.objects.filter(answer_to=parent, submitted_on__lte=reply.submitted_on).exclude(submitted_by_id__in=condemned).order_by('-id')[:25])
					#print "THESE ARE REPLIES: %s" % replies
					relevant_ids = [rply.id for rply in replies]
					seen_replies = list(Publicreply.objects.filter(id__in=relevant_ids, publicreply_seen_related__seen_user=self.request.user))
					unseen_replies = [x for x in replies if x not in seen_replies]
					#print "THESE ARE UNSEEN REPLIES: %s" % unseen_replies
					seen_list = []
					for rpy in unseen_replies:
						seen_list.append(Seen(seen_user=self.request.user,which_reply=rpy,seen_status=True))
					#print seen_list
					Seen.objects.bulk_create(seen_list)
					#print "ALL YOUR UNSEEN REPLY BELONG TO US"
					return redirect("home")
				else:
					return redirect("score_help")

def cross_notif(request, pk=None, ident=None, user=None, *args, **kwargs):
	try:
		link = Link.objects.get(pk=pk)
		notif_reply = Publicreply.objects.get(pk=ident)
		user = User.objects.get(pk=user)
	except:
		return redirect("home")
	#get all unseen replies before 'reply'
	global condemned
	if user.pk in condemned:
		return redirect("logout_help")
	else:
		replies = Publicreply.objects.filter(answer_to=link).exclude(submitted_by_id__in=condemned).order_by('-id')[:25]
		relevant_list=[]
		for reply in replies:
			if reply.submitted_on > notif_reply.submitted_on:
				pass
			else:
				relevant_list.append(reply)
		relevant_ids = [reply.id for reply in relevant_list]
		seen_replies = list(Publicreply.objects.filter(id__in=relevant_ids, publicreply_seen_related__seen_user=user))
		#print "relevant list is %s" % relevant_list
		#print "seen replies are %s" % seen_replies
		unseen_replies = [x for x in relevant_list if x not in seen_replies]
		#print "unseen_replies are %s" % unseen_replies
		seen_list = []
		for reply in unseen_replies:
				seen_list.append(Seen(seen_user= user,which_reply=reply,seen_status=True))
		Seen.objects.bulk_create(seen_list)
		return redirect("home")

@ratelimit(rate='1/s')
def vote_on_vote(request, vote_id=None, target_id=None, link_submitter_id=None, val=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': vote_id}
		return render(request, 'penalty_vote_on_vote.html', context)
	else:	
		if vote_id.isdigit() and target_id.isdigit() and link_submitter_id.isdigit() and val.isdigit():
			if request.user_banned:
				return redirect("score_help")
			if request.user.id == link_submitter_id:
				return redirect("score_help")
			try:
				vote = Vote.objects.get(pk=vote_id)
			except:
				return redirect("score_help")	
			if target_id:
				try:
					target = User.objects.get(pk=target_id)
				except:
					return redirect("home")
			else:
				return redirect("home")
			value = int(val)
			if vote.voter.id == int(target_id): #target is indeed the user who's vote was identified
				try:
					if value == 1:
						if not Vote.objects.filter(voter=request.user,link=Link.objects.filter(submitter_id=target_id).latest('id')):
							Vote.objects.create(voter=request.user, link=Link.objects.filter(submitter_id=target_id).latest('id'), value=value)
							target.userprofile.score = target.userprofile.score + 2
							target.userprofile.save()
						else:
							pass
					elif value == 0:
						value = -1
						if not Vote.objects.filter(voter=request.user,link=Link.objects.filter(submitter_id=target_id).latest('id')):
							Vote.objects.create(voter=request.user, link=Link.objects.filter(submitter_id=target_id).latest('id'), value=value)
							target.userprofile.score = target.userprofile.score - 3
							if target.userprofile.score < -25:
								if not HellBanList.objects.filter(condemned_id=target_id).exists(): #only insert target in hell-ban list if she isn't there already
									HellBanList.objects.create(condemned=target) #adding target to hell-ban list
									target.userprofile.score = random.randint(10,71) #assigning random score to banned user
								else:
									pass
							else:
								pass
							target.userprofile.save()
					else:
						return redirect("score_help")
				except:
					if value == 1:
						link = Link.objects.create(description='mein idher hu', submitter=target)
						Vote.objects.create(voter=request.user, link=link, value=value)
						target.userprofile.score = target.userprofile.score + 2
						target.userprofile.save()
						return redirect("home")
					elif value == -1:
						link = Link.objects.create(description='mein idher hu', submitter=target)
						Vote.objects.create(voter=request.user, link=link, value=value)
						target.userprofile.score = target.userprofile.score - 3
						if target.userprofile.score < -25:
							if not HellBanList.objects.filter(condemned_id=target_id).exists(): #only insert target in hell-ban list if she isn't there already
								HellBanList.objects.create(condemned=target) #adding target to hell-ban list
								target.userprofile.score = random.randint(10,71) #assigning random score to banned user
							else:
								pass
						target.userprofile.save()
						return redirect("home")
					else:
						return redirect("home")
			else:
				return redirect("link_create_pk")
			return redirect("home")
		else:
			return redirect("link_create_pk")

def update_cooldown(obj):
	time_now = datetime.utcnow().replace(tzinfo=utc)
	#print time_now
	time_passed = obj.time_of_casting
	#print time_passed
	difference = time_now - time_passed
	#print difference.total_seconds()
	difference_in_mins = difference.total_seconds() / 60
	#print difference_in_mins
	interval = int(difference_in_mins / 6) # control the interval length from here
	#print "interval: %s" % interval
	obj.hot_score = obj.hot_score + interval
	if obj.hot_score > 10:
		obj.hot_score = 10
	return obj

def find_time(obj):
	time_passed = obj.time_of_casting
	target_time = time_passed + timedelta(minutes=6) # control the interval length from here
	difference = target_time - datetime.utcnow().replace(tzinfo=utc)
	return difference

@ratelimit(rate='1/s')
def vote(request, pk=None, usr=None, loc=None, val=None, *args, **kwargs):
	#PERIODS = (1,5*1,10*1,)
	was_limited = getattr(request, 'limits', False)
	#print "The remote ip of the requester is: %s" % request.META.get('REMOTE_ADDR', None)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': pk}
		return render(request, 'penalty_vote.html', context)
	else:
		if pk.isdigit() and usr.isdigit() and loc.isdigit() and val.isdigit():
			try:
				cooldown = Cooldown.objects.filter(voter=request.user).latest('id')
			except:
				cooldown = Cooldown.objects.create(voter=request.user, hot_score=10, time_of_casting=datetime.utcnow().replace(tzinfo=utc))
			#print cooldown.pk
			#print "score before update: %s" % cooldown.hot_score
			obj = update_cooldown(cooldown)
			#print "score after update %s" % obj.hot_score
			if int(obj.hot_score) < 1:
				time_remaining = find_time(obj)
				time_stamp = datetime.utcnow().replace(tzinfo=utc) + time_remaining
				#print "time_remaining: %s" % time_remaining
				context = {'time_remaining': time_stamp}
				return render(request, 'cooldown.html', context)
			try:
				link = Link.objects.get(pk=int(pk))
			except:
				return redirect("link_create_pk")
			section = str(loc)
			if usr:
				if request.user.id != int(usr):
					# the user sending this request is trying to vote with someone else's ID
					return redirect("link_create_pk")
			else:
				return redirect("link_create_pk")	
			value = int(val)
			if not Vote.objects.filter(voter=request.user, link=link).exists():
				#only if user never voted on this link
				if value == 1:
					if request.user_banned:
						return redirect("score_help")
					else:
						link.submitter.userprofile.score = link.submitter.userprofile.score + 2
						link.submitter.userprofile.save()
						cooldown.hot_score = cooldown.hot_score - 1
						cooldown.time_of_casting = datetime.utcnow().replace(tzinfo=utc)
				elif value == 2:
					if request.user_banned or request.user.username not in FEMALES:
						return redirect("score_help")
					else:
						link.submitter.userprofile.score = link.submitter.userprofile.score + 50
						if link.submitter.userprofile.score < -25:
							if not HellBanList.objects.filter(condemned=link.submitter).exists(): #only insert user in hell-ban list if she isn't there already
								HellBanList.objects.create(condemned=link.submitter) #adding user to hell-ban list
								link.submitter.userprofile.score = random.randint(10,71) #assigning random score to banned user
						link.submitter.userprofile.save()
						cooldown.hot_score = cooldown.hot_score - 3
						cooldown.time_of_casting = datetime.utcnow().replace(tzinfo=utc)
				elif value == 0:
					if request.user_banned:
						return redirect("score_help")
					else:
						link.submitter.userprofile.score = link.submitter.userprofile.score - 3
						if link.submitter.userprofile.score < -25:
							if not HellBanList.objects.filter(condemned=link.submitter).exists(): #only insert user in hell-ban list if she isn't there already
								HellBanList.objects.create(condemned=link.submitter) #adding user to hell-ban list
								link.submitter.userprofile.score = random.randint(10,71) #assigning random score to banned user
						link.submitter.userprofile.save()
						cooldown.hot_score = cooldown.hot_score - 1
						cooldown.time_of_casting = datetime.utcnow().replace(tzinfo=utc)
					value = -1
				elif value == 3:
					if request.user_banned or request.user.username not in FEMALES:
						return redirect("score_help")
					else:
						link.submitter.userprofile.score = link.submitter.userprofile.score -300
						if link.submitter.userprofile.score < -25:
							if not HellBanList.objects.filter(condemned=link.submitter).exists(): #only insert user in hellban list if she isn't there already
								HellBanList.objects.create(condemned=link.submitter) #adding user to hell-ban list
								link.submitter.userprofile.score = random.randint(10,71) #assigning random score to banned user
						link.submitter.userprofile.save()
						cooldown.hot_score = cooldown.hot_score - 3
						cooldown.time_of_casting = datetime.utcnow().replace(tzinfo=utc)
					value = -2
				else:
					value = 0
					return redirect("link_create_pk")
				try:
					Vote.objects.create(voter=request.user, link=link, value=value) #add the up or down vote in the DB.
					cooldown.save()
				except:#if vote object can't be created, just redirect the user, no harm done
					return redirect("link_create_pk")
				try:
					request.session['target_id'] = link.id
					return redirect("home")
				except:
					return redirect("home") #e.g. if Dorado WAP browser, which doesn't have HTTP_REFERER	
			else:
				try:
					return redirect(request.META.get('HTTP_REFERER')+"#section"+section)
				except:
					return redirect("home") #e.g. if Dorado WAP browser, which doesn't have HTTP_REFERER
		else:
			return redirect("link_create_pk")
	
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