# Create your views here.
import re, urlmarker, StringIO, urlparse, requests, random, string, uuid, pytz, json#, sys
from collections import OrderedDict, defaultdict
from requests.auth import HTTPBasicAuth
from operator import attrgetter,itemgetter
from target_urls import call_aasan_api
from django.utils.decorators import method_decorator
from django.core.files.uploadedfile import InMemoryUploadedFile
from scraper import read_image
from django.db import connection
from django.core.cache import get_cache, cache
from django.db.models import Max, Count, Q, Sum, F
from verified import FEMALES
from emoticons.settings import EMOTICONS_LIST
from namaz_timings import namaz_timings, streak_alive
from .tasks import bulk_create_notifications, photo_tasks, unseen_comment_tasks, publicreply_tasks, report, photo_upload_tasks, \
video_upload_tasks, video_tasks, video_vote_tasks, photo_vote_tasks, calc_photo_quality_benchmark, queue_for_deletion, \
VOTE_WEIGHT, public_group_vote_tasks, public_group_attendance_tasks, group_notification_tasks, publicreply_notification_tasks
from .check_abuse import check_photo_abuse, check_video_abuse
from .models import Link, Vote, Cooldown, PhotoStream, TutorialFlag, PhotoVote, Photo, PhotoComment, PhotoCooldown, ChatInbox, \
ChatPic, UserProfile, ChatPicMessage, UserSettings, Publicreply, GroupBanList, HellBanList, GroupCaptain, \
Unseennotification, GroupTraffic, Group, Reply, GroupInvite, GroupSeen, HotUser, UserFan, Salat, LatestSalat, \
SalatInvite, TotalFanAndPhotos, Logout, Report, Video, VideoComment
#from links.azurevids.azurevids import uploadvid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
# from django.views.generic.list import MultipleObjectMixin
from .redis2 import get_latest_online, set_uploader_score, retrieve_unseen_activity, bulk_update_salat_notifications, \
viewer_salat_notifications, update_notification, create_notification, update_object, create_object, remove_group_notification, \
remove_from_photo_owner_activity, add_to_photo_owner_activity, get_attendance, del_attendance, del_from_rankings, \
public_group_ranking, retrieve_latest_notification, delete_salat_notification, prev_unseen_activity_visit, SEEN, \
save_user_presence,get_latest_presence, get_replies_with_seen, remove_group_object
from .redisads import get_user_loc, get_ad, store_click, get_user_ads, suspend_ad
from .redis1 import insert_hash, document_link_abuse, posting_allowed, document_nick_abuse, remove_key, document_publicreply_abuse, \
publicreply_allowed, document_comment_abuse, comment_allowed, document_group_cyberbullying_abuse, document_report_reason, document_group_obscenity_abuse, \
private_group_posting_allowed, add_group_member, get_group_members, remove_group_member, check_group_member, add_group_invite, \
check_group_invite, remove_group_invite, get_active_invites, add_user_group, get_user_groups, remove_user_group, private_group_posting_allowed, \
all_unfiltered_posts, all_filtered_posts, add_unfiltered_post, add_filtered_post, add_photo, all_photos, all_best_photos, add_photo_to_best, \
all_videos, add_video, video_uploaded_too_soon, add_vote_to_video, voted_for_video, get_video_votes, save_recent_video, save_recent_photo, \
get_recent_photos, get_recent_videos, get_photo_votes, voted_for_photo, add_vote_to_photo, bulk_check_group_membership, first_time_refresher, \
add_refresher, in_defenders, first_time_photo_defender, add_photo_defender_tutorial, add_to_photo_vote_ban, add_to_photo_upload_ban, \
check_photo_upload_ban, check_photo_vote_ban, can_photo_vote, add_home_link, update_cc_in_home_link, update_cc_in_home_photo, \
retrieve_home_links, add_vote_to_home_link, bulk_check_group_invite, first_time_inbox_visitor, add_inbox
from .forms import UserProfileForm, DeviceHelpForm, PhotoScoreForm, BaqiPhotosHelpForm, PhotoQataarHelpForm, PhotoTimeForm, \
ChainPhotoTutorialForm, PhotoJawabForm, PhotoReplyForm, CommentForm, UploadPhotoReplyForm, UploadPhotoForm, ChangeOutsideGroupTopicForm, \
ChangePrivateGroupTopicForm, ReinvitePrivateForm, ContactForm, InvitePrivateForm, AboutForm, PrivacyPolicyForm, CaptionDecForm, \
CaptionForm, PhotoHelpForm, PicPasswordForm, CrossNotifForm, EmoticonsHelpForm, UserSMSForm, PicHelpForm, \
DeletePicForm, UserPhoneNumberForm, PicExpiryForm, PicsChatUploadForm, VerifiedForm, GroupHelpForm, LinkForm, WelcomeReplyForm, \
WelcomeMessageForm, WelcomeForm, NotifHelpForm, MehfilForm, MehfildecisionForm, LogoutHelpForm, LogoutReconfirmForm, LogoutPenaltyForm, \
SmsReinviteForm, OwnerGroupOnlineKonForm, GroupReportForm, AppointCaptainForm, OutsiderGroupForm, SmsInviteForm, InviteForm, \
OutsideMessageCreateForm, OutsideMessageForm, DirectMessageCreateForm, DirectMessageForm, KickForm, PrivateGroupReplyForm, \
PublicGroupReplyForm, ClosedInviteTypeForm, OpenInviteTypeForm, TopForm, LoginWalkthroughForm, RegisterWalkthroughForm, \
RegisterLoginForm, ClosedGroupHelpForm, ChangeGroupRulesForm, ChangeGroupTopicForm, GroupTypeForm, GroupOnlineKonForm, GroupTypeForm, \
GroupListForm, OpenGroupHelpForm, GroupPageForm, ReinviteForm, ScoreHelpForm, HistoryHelpForm, UserSettingsForm, HelpForm, \
WhoseOnlineForm, RegisterHelpForm, VerifyHelpForm, PublicreplyForm, ReportreplyForm, ReportForm, UnseenActivityForm, \
ClosedGroupCreateForm, OpenGroupCreateForm, PhotoOptionTutorialForm, BigPhotoHelpForm, clean_image_file, clean_image_file_with_hash, \
TopPhotoForm, FanListForm, StarListForm, FanTutorialForm, PhotoShareForm, SalatTutorialForm, SalatInviteForm, ExternalSalatInviteForm, \
ReportcommentForm, MehfilCommentForm, SpecialPhotoTutorialForm, ReportNicknameForm, ReportProfileForm, ReportFeedbackForm, \
UploadVideoForm, VideoCommentForm, VideoScoreForm, FacesHelpForm, FacesPagesForm, VoteOrProfForm, AdAddressForm, AdAddressYesNoForm, \
AdGenderChoiceForm, AdCallPrefForm, AdImageYesNoForm, AdDescriptionForm, AdMobileNumForm, AdTitleYesNoForm, AdTitleForm, \
AdTitleForm, AdImageForm, TestAdsForm, TestReportForm, HomeListListForm#, UpvoteForm, DownvoteForm, OutsideMessageRecreateForm, PhotostreamForm, 

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from math import log, ceil
from urllib import quote
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import datetime, time
from datetime import datetime, timedelta
from user_sessions.models import Session
from django.utils import timezone
from django.utils.timezone import utc
from django.views.decorators.cache import cache_page, never_cache
from fuzzywuzzy import fuzz
from brake.decorators import ratelimit

condemned = HellBanList.objects.values_list('condemned_id', flat=True).distinct()

def convert_to_epoch(time):
	#time = pytz.utc.localize(time)
	return (time-datetime(1970,1,1)).total_seconds()

def get_price(points):
	if points < 120:
		price = 30
	elif 120 <= points < 10001:
		x=((((20**(1/2.0))-2)*points)/9880)+1.96997405723 #scaling x between 2 and sqrt(20)
		base = x**2 #squaring x
		price = (((points/base)+9)//10)*10 #roundup the number to nearest 10
	elif 10001 <= points < 500001:
		sqrt1 = 20**(1/2.0)
		sqrt2 = 70**(1/2.0)
		numerator = sqrt2 - sqrt1
		x=((numerator*points)/490000)+4.39265709152 #scaling between sqrt(20) and sqrt(70)
		base = x**2 #squaring x
		price = (((points/base)+9)//10)*10 #roundup the number to nearest 10
	else:
		base = 71
		price = (((points/base)+9)//10)*10 #roundup the number to nearest 10
	return int(price)


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

def add_to_ban(user_id):
	if HellBanList.objects.filter(condemned_id=user_id).exists():
		pass
	else:
		HellBanList.objects.create(condemned_id=user_id)
		UserProfile.objects.filter(user_id=user_id).update(score=random.randint(10,71))

def valid_uuid(uuid):
	regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
	match = regex.match(uuid)
	return bool(match)

def GetLatest(user):
	try:
		notif_name, hash_name, latest_notif = retrieve_latest_notification(user.id)
		# print latest_notif
		if latest_notif['ot'] == '3':
			# group chat
			return latest_notif['g'], latest_notif, False, False, True, False
		elif latest_notif['ot'] == '2':
			#home publicreply
			return '2', latest_notif, True, False, False, False
		elif latest_notif['ot'] == '0':
			#photo comment
			if latest_notif.get('f'):
				if latest_notif['nc'] == 'True':
					# photo notif for fans
					return '1', latest_notif, False, True, False, False
				else:
					# photo comment received by fan
					return '0', latest_notif, False, True, False, False	
			else:
				# photo comment received by non-fan
				return '0', latest_notif, False, True, False, False
		elif latest_notif['ot'] == '4':
			# salat invites
			time_now = datetime.utcnow()+timedelta(hours=5)
			# current_minute = time_now.hour * 60 + time_now.minute
			# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time \
			# = namaz_timings[current_minute]
			cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
				'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
			})
			salat_timings = cache_mem.get('salat_timings')
			if not salat_timings['namaz']:
				#time for namaz has gone
				delete_salat_notification(notif_name, hash_name, user.id)
				return None, None, False, False, False, False
			else:
				starting_time = datetime.combine(time_now.today(), salat_timings['current_namaz_start_time'])
				ending_time = datetime.combine(time_now.today(), salat_timings['current_namaz_end_time'])
				try:
					latest_namaz = LatestSalat.objects.filter(salatee=user).latest('when')
				except:
					#latest_namaz does not exist
					latest_namaz = None
				if (convert_to_epoch(starting_time) <= float(latest_notif['u']) < convert_to_epoch(ending_time)) and not \
				AlreadyPrayed(latest_namaz,time_now):
					# print "showing namaz notification"
					return '4',latest_notif, False, False, False, True
				else:
					# print "didn't clear if statement, deleting namaz notification"
					delete_salat_notification(notif_name, hash_name, user.id)			
					return None, None, False, False, False, False
	except:
		return None, None, False, False, False, False

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

def star_list(request, pk=None, *args, **kwargs):
	if pk.isdigit():
		request.session["star_target_id"] = pk
		return redirect("star_list_view")
	else:
		return redirect("see_photo")

class StarListView(FormView):
	form_class = StarListForm
	template_name = "star_list.html"

	def get_context_data(self, **kwargs):
		context = super(StarListView, self).get_context_data(**kwargs)
		context["allowed"] = False
		if self.request.user.is_authenticated():
			context["girls"] = FEMALES
			pk = self.request.session["star_target_id"]
			if self.request.user.id == int(pk):
				context["allowed"] = True
			else:
				context["allowed"] = False
			context["star_list"] = UserFan.objects.filter(fan_id=pk).order_by('star')
			ids = [star.star.id for star in context["star_list"]]
			users = User.objects.annotate(photo_count=Count('photo', distinct=True)).in_bulk(ids)
			users_photo_count = [(users[id], users[id].photo_count) for id in ids]
			context["users"] = users_photo_count
			context["fan"] = User.objects.get(id=pk)
		return context

def fan_list(request, pk=None, *args, **kwargs):
	if pk.isdigit():
		request.session["fan_target_id"] = pk
		return redirect("fan_list_view")
	else:
		return redirect("see_photo")

class FanListView(FormView):
	form_class = FanListForm
	template_name = "fan_list.html"

	def get_context_data(self, **kwargs):
		context = super(FanListView, self).get_context_data(**kwargs)
		context["girls"] = FEMALES
		try:
			pk = self.request.session["fan_target_id"]
			context["fan_list"] = UserFan.objects.select_related('fan__userprofile').filter(star_id=pk).order_by('fan')
			context["star"] = User.objects.get(id=pk)
			context["error"] = False
		except:
			context["error"] = True
		return context

class ReinvitePrivateView(FormView):
	form_class = ReinvitePrivateForm
	template_name = "reinvite_private.html"

	def get_context_data(self, **kwargs):
		context = super(ReinvitePrivateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.request.session["private_uuid"]
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
			try:
				context["unique"] = unique
				context["sms_url"] = "https://http-damadam-pk.0.freebasics.com/mehfilawami/"+unique
			except:
				context["unique"] = None
				context["sms_url"] = "https://http-damadam-pk.0.freebasics.com"
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

class VoteOrProfView(FormView):
	form_class = VoteOrProfForm
	template_name = "vote_or_profile.html"

	def get_context_data(self, **kwargs):
		context = super(VoteOrProfView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				voter = User.objects.get(username=self.kwargs["slug"])
				vote = Vote.objects.get(link_id=self.kwargs["pk"], voter=voter)
			except:
				# couldn't get vote
				context["self"] = -1
				context["subject"] = None
				context["vote_id"] = None
				context["link_submitter_id"] = None
				return context
			if self.request.user == voter:
				#if person looking at own vote
				context["self"] = 1
				context["subject"] = self.request.user
				context["vote_id"] = vote.id
				context["link_submitter_id"] = self.kwargs["id"]
			elif self.request.user.id == self.kwargs["id"]:
				#if person is the link writer too
				context["self"] = 2
				context["subject"] = voter
				context["vote_id"] = vote.id
				context["link_submitter_id"] = self.kwargs["id"]
			else:
				#if person is nor the link writer, or the voter
				context["self"] = 0
				context["subject"] = voter
				context["vote_id"] = vote.id
				context["link_submitter_id"] = self.kwargs["id"]
		return context

def faces_pages(request, *args, **kwargs):
	form = FacesPagesForm()
	oblist = EMOTICONS_LIST
	paginator = Paginator(oblist, 16)
	page = request.GET.get('page', '1')
	try:
		page = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		page = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		page = paginator.page(paginator.num_pages)
	context = {'object_list': oblist, 'form':form, 'page':page}
	return render(request, 'faces_pages.html', context)

class FacesHelpView(FormView):
	form_class = FacesHelpForm
	template_name = "faces.html"

	def get_context_data(self, **kwargs):
		context = super(FacesHelpView, self).get_context_data(**kwargs)
		if self.request.is_feature_phone:
			context["is_feature_phone"] = True
		else:
			context["is_feature_phone"] = False
		return context

class EmoticonsHelpView(FormView):
	form_class = EmoticonsHelpForm
	template_name = "emoticons_help.html"

	def get_context_data(self, **kwargs):
		context = super(EmoticonsHelpView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["random"] = random.sample(xrange(1,188),15) #select 15 random emoticons out of 188
		return context

class LogoutHelpView(FormView):
	form_class = LogoutHelpForm
	template_name = "logout_help.html"

class BigPhotoHelpView(FormView):
	form_class = BigPhotoHelpForm
	template_name = "big_photo_help.html"

	def get_context_data(self, **kwargs):
		context = super(BigPhotoHelpView, self).get_context_data(**kwargs)
		photo_id = self.kwargs["pk"]
		context["photo"] = Photo.objects.get(id=photo_id)
		return context

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
						user = self.request.user
						Logout.objects.create(logout_user=user, pre_logout_score=user.userprofile.score)
						user.userprofile.score = 10
						user.userprofile.save()
						return redirect("bahirniklo")
					except:
						return redirect("home")
				else:
					return redirect("home")
			else:
				return redirect("score_help")

class ReportFeedbackView(FormView):
	form_class = ReportFeedbackForm
	template_name = "report_feedback.html"

	def get_context_data(self, **kwargs):
		context = super(ReportFeedbackView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				if self.request.session["report_feedback"] == '1':
					context["nick"] = self.kwargs["nick"]
					context["pk"] = self.kwargs["pk"]
					context["uuid"] = self.kwargs["uuid"]
					context["private"] = self.kwargs["private"]
					context["scr"] = self.kwargs["scr"]
				else:
					context["nick"] = None
					context["pk"] = None
					context["uuid"] = None
					context["private"] = None
					context["scr"] = None
			except:
				context["nick"] = None
				context["pk"] = None
				context["uuid"] = None
				context["private"] = None
				context["scr"] = None
		return context

	def form_valid(self, form):
		try:
			rf = self.request.session["report_feedback"]
			self.request.session["report_feedback"] = None
			if self.request.method == 'POST':
				description = self.request.POST.get("description", '')
				nick = self.request.POST.get("nick", '')
				pk = self.request.POST.get("pk", '')
				uuid = self.request.POST.get("uuid", '')
				private = self.request.POST.get("private", '')
				scr = self.request.POST.get("scr", '')
				if pk == self.request.user.id:
					context={'private':private, 'uuid':uuid}
					return render(self.request, 'penalty_nickselfrep.html', context)
				elif pk == '1':
					context={'private':private, 'uuid':uuid}
					return render(self.request, 'penalty_mhb11rep.html', context)
				else:
					cost = get_price(self.request.user.userprofile.score)
					first_time_feedback = document_report_reason(pk, scr, self.request.user.id, cost, description)
					if first_time_feedback:
						UserProfile.objects.filter(user=self.request.user).update(score=F('score')-cost)
						document_group_cyberbullying_abuse(pk, cost)
					else:
						context={'private':private, 'uuid':uuid}
						return render(self.request, 'penalty_nickdoublerep.html', context)
				context={'nickname':nick, 'private':private, 'uuid':uuid}
				return render(self.request, 'reported.html', context)
			else:
				return redirect("profile", self.kwargs["nick"])
		except:
			return redirect("profile", self.kwargs["nick"])

@ratelimit(rate='2/s')
def reprofile(request, pk=None, unique=None, private=None, grp=None, uname=None,*args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 5 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportprofile.html', context)
		except:
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportprofile.html', context)
	else:
		if pk.isdigit() and check_group_member(grp, request.user.username):
			banned, ban_type, time_remaining, warned = private_group_posting_allowed(request.user.id)
			if banned:
				context={'unique':unique, 'private':private}
				return render(request, 'penalty_groupbanned.html', context)
			else:
				try:
					request.session['target_profile_id'] = pk
					request.session['target_profile_username'] = uname
					request.session['target_mehfil_uuid'] = unique
					request.session['target_mehfil_id'] = grp
					request.session['target_mehfil_type'] = private
					return redirect("report_profile")
				except:
					return redirect("home")
		else:
			return redirect("home")

class ReportProfileView(FormView):
	form_class = ReportProfileForm
	template_name = "report_profile.html"

	def get_context_data(self, **kwargs):
		context = super(ReportProfileView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				target_profile_id = self.request.session['target_profile_id']
				target_profile_username = self.request.session['target_profile_username']
				target_mehfil_uuid = self.request.session['target_mehfil_uuid']
				target_mehfil_id = self.request.session['target_mehfil_id']
				target_mehfil_type = self.request.session['target_mehfil_type']
				target_score = UserProfile.objects.get(user_id=target_profile_id).score
				context["target_score"] = target_score
				context["target_username"] = target_profile_username
				context["target_id"] = target_profile_id
				context["mehfil_uuid"] = target_mehfil_uuid
				context["mehfil_type"] = target_mehfil_type
				context["pts"] = get_price(self.request.user.userprofile.score)
				if check_group_member(target_mehfil_id, target_profile_username):
					context["allowed"] = True
				else:
					context["allowed"] = False
				self.request.session['target_profile_id'] = None
				self.request.session['target_profile_username'] = None
				self.request.session['target_mehfil_uuid'] = None
				self.request.session['target_mehfil_id'] = None
				self.request.session['target_mehfil_type'] = None
			except:
				context["allowed"] = False
				context["target_username"] = None
				context["target_id"] = None
				context["target_score"] = None
				context["mehfil_uuid"] = None
				context["mehfil_type"] = None
				context["pts"] = None
		return context

@ratelimit(rate='2/s')
def rep(request, pk=None, num=None, nick=None, uuid=None, priv=None, scr=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	banned_self, ban_type_self, time_remaining_self, warned_self = private_group_posting_allowed(request.user.id)
	banned_target, ban_type_target, time_remaining_target, warned_target = private_group_posting_allowed(pk)
	if was_limited:
		try:
			deduction = 5 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportprofile.html', context)
		except:
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportprofile.html', context)
	elif banned_self:
		context={'unique':uuid, 'private':priv}
		return render(request, 'penalty_groupbanned.html', context)
	elif banned_target:
		m, s = divmod(time_remaining_target, 60)
		h, m = divmod(m, 60)
		d, h = divmod(h, 24)
		if d and h and m:
			time_remaining = "%s days, %s hours and %s minutes" % (int(d), int(h), int(m))
		elif h and m:
			time_remaining = "%s hours and %s minutes" % (int(h), int(m))
		elif m and s:
			time_remaining = "%s minutes and %s seconds" % (int(m), int(s))
		elif s:
			time_remaining = "%s seconds" % int(s)
		else:
			time_remaining = None
		context={'nickname':nick, 'unique':uuid, 'private':priv, 'time_remaining':time_remaining}
		return render(request, 'penalty_alreadyreported.html', context)
	elif request.user.userprofile.score < 121:
		request.user.userprofile.score = request.user.userprofile.score - 120
		request.user.userprofile.save()
		context={'pk':'pk'}
		return render(request, 'penalty_nickreport.html', context)
	elif pk == '1':
		context={'uuid':uuid, 'private':priv}
		return render(request, 'penalty_mhb11rep.html', context)
	else:
		if pk.isdigit() and num.isdigit():
			group = Group.objects.get(unique=uuid)
			if not check_group_member(group.id, nick):
				context={'nickname':nick, 'uuid':uuid, 'private':priv}
				return render(request, 'penalty_groupleft.html', context)
			elif request.user.id == pk:
				context={'uuid':uuid, 'private':priv}
				return render(request, 'penalty_nickselfrep.html', context)
			elif num=='9':
				request.session["report_feedback"] = '1'
				return redirect("report_feedback", pk=pk, nick=nick, uuid=uuid, private=priv, scr=scr)
			else:
				cost = get_price(request.user.userprofile.score)
				first_time_feedback = document_report_reason(pk, scr, request.user.id, cost, num)
				if first_time_feedback:
					UserProfile.objects.filter(user=request.user).update(score=F('score')-cost)
					if num=='1' or num=='4' or num=='7':
						document_group_obscenity_abuse(pk, cost)
					else:
						document_group_cyberbullying_abuse(pk, cost)
					context={'nickname':nick, 'uuid':uuid, 'private':priv}
					return render(request, 'reported.html', context)
				else:
					context={'uuid':uuid, 'private':priv}
					return render(request, 'penalty_nickdoublerep.html', context)

@ratelimit(rate='2/s')
def repnick(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 5 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportreply.html', context)
		except:
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportreply.html', context)
	else:
		if pk.isdigit():
			try:
				request.session['target_nickname_id'] = pk
				return redirect("report_nickname")
			except:
				return redirect("home")
		else:
			return redirect("home")

class ReportNicknameView(FormView):
	form_class = ReportNicknameForm
	template_name = "report_nickname.html"

	def get_context_data(self, **kwargs):
		context = super(ReportNicknameView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				target_id = self.request.session['target_nickname_id']
				target = User.objects.get(id=target_id)
				context["target"] = target
			except:
				context["target"] = None
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			user = self.request.user
			rep = self.request.POST.get("report")
			if rep == 'Haan':
				target_id = self.request.POST.get("target_id")
				target_id_2 = self.request.session['target_nickname_id']
				self.request.session['target_nickname_id'] = None
				if target_id == target_id_2 and user.userprofile.score > 120:
					#check if not self report, and not double reporting
					if user.id == target_id:
						context={'pk':'pk'}
						return render(self.request, 'penalty_nickselfreport.html', context)
					elif target_id == '1':
						context={'pk':'pk'}
						return render(self.request, 'penalty_mhb11report.html', context)
					else:
						latest_user = User.objects.latest('id')
						if int(latest_user.id) - int(target_id) < 50:#it really is a recent user
							reported = document_nick_abuse(target_id, user.id)
							if reported == 'Falz':
								context={'pk':'pk'}
								return render(self.request, 'penalty_nickdoublereport.html', context)
							else:
								UserProfile.objects.filter(user=user.id).update(score=F('score')-10)
								#reported contains current integrity value of target
								if int(reported) < 0:
									add_to_ban(target_id)
									remove_key("nah:"+str(target_id))
									remove_key("nas:"+str(target_id))
								else:
									pass
								context={'pk':'pk'}
								return render(self.request, 'nick_report.html', context)
						else:#it's not a recent user
							context={'pk':'pk'}
							return render(self.request, 'penalty_nickreport.html', context)
				else:
					try:
						UserProfile.objects.filter(user=user.id).update(score=F('score')-120)
						context={'pk':'pk'}
						return render(self.request, 'penalty_nickreport.html', context)
					except:
						context={'pk':'pk'}
						return render(self.request, 'penalty_nickreport.html', context)
			else:
				return redirect("home")

def leave_public_group(request, pk=None, unique=None, private=None, inside_grp=None, *args, **kwargs):
	group = Group.objects.get(id=pk)
	if group.owner == request.user:
		context={'unique':unique, 'pk':pk, 'private':private,'topic':group.topic, 'inside_grp':inside_grp}
		return render(request, 'delete_public_group.html', context)
	else:
		context={'unique':unique, 'pk':pk, 'private':private,'topic':group.topic, 'inside_grp':inside_grp}
		return render(request, 'leave_public_group.html', context)

def left_public_group(request, pk=None, unique=None, private=None, *args, **kwargs):
	if request.is_feature_phone:
		device = '1'
	elif request.is_phone:
		device = '2'
	elif request.is_tablet:
		device = '4'
	elif request.is_mobile:
		device = '5'
	else:
		device = '3'
	if check_group_member(pk, request.user.username):
		remove_group_member(pk, request.user.username)
		remove_user_group(request.user.id, pk)
		remove_group_notification(request.user.id,pk)
	elif check_group_invite(request.user.id, pk):
		remove_group_invite(request.user.id, pk)
		remove_group_notification(request.user.id,pk)
	else:
		pass
	return redirect("group_page")

def del_public_group(request, pk=None, unique=None, private=None, *args, **kwargs):
	if Group.objects.get(id=pk).owner == request.user:
		remove_group_notification(user_id=request.user.id,group_id=pk)
		del_from_rankings(pk)
		del_attendance(pk)
		remove_group_object(pk)
		GroupBanList.objects.filter(which_group_id=pk).delete()
		GroupCaptain.objects.filter(which_group_id=pk).delete()
		Group.objects.get(id=pk).delete()
		return redirect("group_page")
	else:
		context={'private':'0','unique':unique}
		return render(request,'penalty_groupbanned.html', context)

def leave_private_group(request, pk=None, unique=None, private=None, inside_grp=None, *args, **kwargs):
	topic = Group.objects.get(id=pk).topic
	context={'unique':unique, 'pk':pk, 'private':private,'topic':topic, 'inside_grp':inside_grp}
	return render(request, 'leave_private_group.html', context)

def left_private_group(request, pk=None, unique=None, private=None, *args, **kwargs):
	banned, ban_type, time_remaining, warned = private_group_posting_allowed(request.user.id)
	if banned:
		context={'unique':unique, 'private':private}
		return render(request, 'penalty_groupbanned.html', context)
	else:
		if request.is_feature_phone:
			device = '1'
		elif request.is_phone:
			device = '2'
		elif request.is_tablet:
			device = '4'
		elif request.is_mobile:
			device = '5'
		else:
			device = '3'
		if check_group_member(pk, request.user.username):
			memcount = remove_group_member(pk, request.user.username) #group membership is truncated
			remove_user_group(request.user.id, pk) #user's groups are truncated
			remove_group_notification(request.user.id,pk) #group removed from user's notifications
			if memcount < 1:
				remove_group_object(pk)
			reply = Reply.objects.create(which_group_id=pk, writer=request.user, text='leaving group', category='6', device=device)
			GroupSeen.objects.create(seen_user= request.user,which_reply=reply)	
		elif check_group_invite(request.user.id, pk):
			remove_group_invite(request.user.id, pk)
			remove_group_notification(request.user.id,pk)
			reply = Reply.objects.create(which_group_id=pk, writer=request.user, text='unaccepted invite', category='7', device=device)
			GroupSeen.objects.create(seen_user= request.user,which_reply=reply)
		else:
			pass
		return redirect("group_page")

def mehfil_help(request, pk=None, num=None, *args, **kwargs):
	if pk.isdigit() and num.isdigit():
		request.session['user_pk'] = pk
		request.session['link_id'] = num
		return redirect("mehfil_help")
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
			user = self.request.user
			report = self.request.POST.get("decision")
			target = self.request.session['user_pk']
			link_id = self.request.session['link_id']
			self.request.session['link_id'] = None
			self.request.session['user_pk'] = None
			if link_id and report == 'Haan':
				if user.userprofile.score < 500:
					context = {'pk': link_id}
					return render(self.request, 'penalty_linkmehfil.html', context)
				else:
					user.userprofile.score = user.userprofile.score - 500
					target_user = User.objects.get(id=target)
					invitee = target_user.username
					topic = invitee+" se gupshup"
					unique = uuid.uuid4()
					try:
						group = Group.objects.create(topic=topic, rules='', owner=user, private='1', unique=unique)
						user.userprofile.save()
						reply_list = []
						seen_list = []
						reply = Reply.objects.create(text=invitee, category='1', which_group_id=group.id, writer=user)
						#reply_list.append(Reply(text='Aur g kia haal hai?', which_group_id=group.id, writer=user))
						#Reply.objects.bulk_create(reply_list)
						add_group_member(group.id, user.username)
						add_group_invite(target, group.id,reply.id)
						add_user_group(user.id, group.id)
						return redirect("private_group", slug=unique)
					except:
						redirect("reply_pk", pk=link_id)
			else:
				return redirect("home")

class SalatRankingView(ListView):
	template_name = "salat_ranking.html"
	model = LatestSalat
	paginate_by = 50

	def get_queryset(self):
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 120,
		})
		users_fans = cache_mem.get('salat_streaks')
		# print users_fans
		if users_fans:
			return users_fans
		else:
			return []

	def get_context_data(self, **kwargs):
		context=super(SalatRankingView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["girls"] = FEMALES
		return context

class SalatSuccessView(ListView):
	template_name = "salat_success.html"
	model = LatestSalat
	paginate_by = 50

	def get_queryset(self):
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 120,
		})
		users_fans = cache_mem.get('salat_streaks')
		if users_fans:
			return users_fans
		else:
			return []

	def get_context_data(self, **kwargs):
		context=super(SalatSuccessView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			mins = self.kwargs["mins"]
			previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[int(mins)]
			context["namaz"] = namaz
			context["time"] = next_namaz_start_time
			context["weekday"] = self.kwargs["num"]
			if context["weekday"] == '4' and context["namaz"] == 'Zuhr':
				context["namaz"] = 'Jummah'
			context["girls"] = FEMALES
		return context

@ratelimit(rate='2/s')
def reportcomment_pk(request, pk=None, num=None, origin=None, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 5 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk':'pk'}
			return render(request, 'penalty_reportcomment.html', context)
		except:
			context = {'pk':'pk'}
			return render(request, 'penalty_reportcomment.html', context)
	else:
		request.session["reportcomment_pk"] = pk
		request.session["photonum_pk"] = num
		if origin:
			request.session["origin"] = origin
		else:
			request.session["origin"] = None
		if slug:
			request.session["origin_profile"] = slug
		else:
			request.session["origin_profile"] = None
		return redirect("reportcomment")
		
class ReportcommentView(FormView):
	form_class = ReportcommentForm
	template_name = "report_comment.html"

	def get_context_data(self, **kwargs):
		context=super(ReportcommentView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				context["authorized"] = True
				context["comment_pk"] = self.request.session["reportcomment_pk"]
				context["photo_pk"] = self.request.session["photonum_pk"]
				context["origin"] = self.request.session["origin"]
				context["origin_profile"] = self.request.session["origin_profile"]
			except:
				context["authorized"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			if not self.request.user_banned:
				rprt = self.request.POST.get("report")
				if rprt == 'Haan':
					comment_id = self.request.session["reportcomment_pk"]
					photo_id = self.request.session["photonum_pk"]
					slug = self.request.session["origin_profile"]
					origin = self.request.session["origin"]
					# comment_id = self.request.POST.get("comment_pk")
					# photo_id = self.request.POST.get("photo_pk")
					# origin = self.request.POST.get("origin")
					# slug = self.request.session["origin_profile"]
					if PhotoComment.objects.filter(pk=comment_id,which_photo_id=photo_id,abuse=False).exists() and \
					Photo.objects.filter(pk=photo_id,owner=self.request.user).exists():
						comment = get_object_or_404(PhotoComment, pk=comment_id)
						comment.abuse = True
						comment.save()
						comment.submitted_by.userprofile.score = comment.submitted_by.userprofile.score - 3
						comment.submitted_by.userprofile.save()
						self.request.session["reportcomment_pk"] = None
						self.request.session["photonum_pk"] = None
						self.request.session["origin_profile"] = None
						self.request.session["origin"] = None
						pk = comment.submitted_by_id
						ident = self.request.user.id
						if pk != ident:
							document_comment_abuse(pk)
						if slug:
							return redirect("comment_pk", pk=photo_id, origin=origin, ident=slug)
						else:
							return redirect("comment_pk", pk=photo_id, origin=origin)
					else:
						self.request.user.userprofile.score = self.request.user.userprofile.score -3
						self.request.user.userprofile.save()
						return redirect("see_photo")
				else:
					#i.e. user clicked "Nahi"
					# photo_id = self.request.POST.get("photo_pk")
					# origin = self.request.POST.get("origin")
					# slug = self.request.POST.get["origin_profile")
					comment_pk = self.request.session["reportcomment_pk"]
					photo_id = self.request.session["photonum_pk"]
					origin = self.request.session["origin"]
					slug = self.request.session["origin_profile"]
					self.request.session["reportcomment_pk"] = None
					self.request.session["photonum_pk"] = None
					self.request.session["origin"] = None
					self.request.session["origin_profile"] = None
					if slug is not None:
						return redirect("comment_pk", pk=photo_id, origin=origin, ident=slug)
					else:
						return redirect("comment_pk", pk=photo_id, origin=origin)
			else:
				return redirect("score_help")

@ratelimit(rate='2/s')
def reportreply_pk(request, pk=None, num=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 5 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportreply.html', context)
		except:
			context = {'pk': 'pk'}
			return render(request, 'penalty_reportreply.html', context)
	else:
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
				context["reply_id"] = pk
				context["link_id"] = link_id
				context["authorized"] = True
			else:
				context["reply_id"] = None
				context["link_id"] = None
				context["authorized"] = False
		return context

class PhotoDetailView(DetailView):
	model = Photo
	template_name = "photo_detail.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoDetailView, self).get_context_data(**kwargs)
		context["can_vote"] = False
		context["authenticated"] = False
		try:
			pk = self.kwargs["pk"]
			photo = Photo.objects.get(id=pk)
			#stream_id = PhotoStream.objects.get(cover_id=photo.id).id
			context["photo_id"] = pk
			context["photo"] = photo
			context["own_photo"] = False
		except:
			context["absent"] = True
			return context
		if self.request.user.is_authenticated():
			context["authenticated"] = True
			if self.request.user == photo.owner:
				context["own_photo"] = True
			else:
				context["own_photo"] = False
				score = self.request.user.userprofile.score 
				if score > 9:
					context["can_vote"] = True
					if PhotoVote.objects.filter(voter=self.request.user,photo=photo).exists():
						context["voted"] = True
					else:
						context["voted"] = False
				else:
					context["can_vote"] = False
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

def skip_presalat(request, *args, **kwargs):
	# now = datetime.utcnow()+timedelta(hours=5)
	# current_minute = now.hour * 60 + now.minute
	# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
		'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
	})
	salat_timings = cache_mem.get('salat_timings')
	if salat_timings['namaz']:
		#i.e. it's not pre-namaz time
		return redirect("home")
	else:
		if salat_timings['next_namaz'] == 'Fajr':
			salat='5'
		elif salat_timings['next_namaz'] == 'Zuhr':
			salat='1'
		elif salat_timings['next_namaz'] == 'Asr':
			salat='2'
		elif salat_timings['next_namaz'] == 'Maghrib':
			salat='3'
		elif salat_timings['next_namaz'] == 'Isha':
			salat='4'
		else:
			return redirect("home")
		try:
			latest_namaz = LatestSalat.objects.filter(salatee=request.user).latest('when')
			latest_namaz.skipped = True
			latest_namaz.when = now
			latest_namaz.save()
		except:
			LatestSalat.objects.create(salatee=request.user, latest_salat=salat, when=now, skipped=True)
		return redirect("home")


def skip_salat(request, skipped=None, *args, **kwargs):
	if skipped:
		# now = datetime.utcnow()+timedelta(hours=5)
		# current_minute = now.hour * 60 + now.minute
		# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
		})
		salat_timings = cache_mem.get('salat_timings')
		if not salat_timings['namaz']:
			return redirect("home")
		elif skipped != salat_timings['namaz']:
			return redirect("home")
		else:
			if salat_timings['namaz'] == 'Fajr':
				salat='1'
			elif salat_timings['namaz'] == 'Zuhr':
				salat='2'
			elif salat_timings['namaz'] == 'Asr':
				salat='3'
			elif salat_timings['namaz'] == 'Maghrib':
				salat='4'
			elif salat_timings['namaz'] == 'Isha':
				salat='5'
			else:
				return redirect("home")
		try:
			latest_namaz = LatestSalat.objects.filter(salatee=request.user).latest('when')
			latest_namaz.skipped = True
			latest_namaz.latest_salat = salat
			latest_namaz.when = now
			latest_namaz.save()
		except:
			LatestSalat.objects.create(salatee=request.user, latest_salat=salat, when=now, skipped=True)
		request.user.userprofile.streak = 0
		request.user.userprofile.save()
		return redirect("home")
	else:
		return redirect("home")

def salat_tutorial_init(request, offered=None, *args, **kwargs):
	try:
		tut = TutorialFlag.objects.get(user=request.user)
		if tut.seen_salat_option:
			return redirect("process_salat")
		else:
			return redirect("salat_tutorial")
	except:
		TutorialFlag.objects.create(user=request.user)
		return redirect("salat_tutorial")

def AlreadyPrayed(salat, now):
	current_minute = now.hour * 60 + now.minute
	time_now = now.time()
	date_now = now.date()
	if not salat:
		return False
	datetime_of_latest_salat = salat.when
	minute_of_latest_salat = datetime_of_latest_salat.hour * 60 + datetime_of_latest_salat.minute 
	time_of_latest_salat = datetime_of_latest_salat.time()
	date_of_latest_salat = datetime_of_latest_salat.date()
	if date_now != date_of_latest_salat:
		#prayee has not already prayed, in fact they haven't logged any salat today
		#but cater to edge cases and graceful failure
		return False
	elif date_now == date_of_latest_salat:
		#prayee logged a salat today
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
		})
		salat_timings = cache_mem.get('salat_timings')
		# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
		# previous_salat_to_do, next_salat_to_do, salat_to_do, next_salat_to_do_start_time, salat_to_do_start_time, salat_to_do_end_time = namaz_timings[current_minute]
		previous_salat_done, next_salat_done, salat_done, salat_done_next_start_time, salat_done_start_time, salat_done_end_time = namaz_timings[minute_of_latest_salat]
		if not salat_timings['namaz'] and not salat_done:
			#this is some kind of an error, handle it gracefully
			return True
		elif not salat_timings['namaz']:
			#i.e. it's pre-namaz time right now, and the person has already prayed too
			if salat.skipped:
				return 2
			else:
				return True
		elif salat_done == salat_timings['namaz']:#salat_to_do:
			#i.e. the user has already prayed
			if salat.skipped:
				return 2
			else:
				return True
		elif salat_done != salat_timings['namaz']:#salat_to_do:
			return False
		else:
			return True

def process_salat(request, offered=None, *args, **kwargs):
	now = datetime.utcnow()+timedelta(hours=5)
	current_minute = now.hour * 60 + now.minute
	# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
	user = request.user
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
		'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
	})
	salat_timings = cache_mem.get('salat_timings')
	try:
		starting_time = datetime.combine(now.today(), salat_timings['current_namaz_start_time']) #i.e. current namaz start time
	except:
		redirect("home")
	if not salat_timings['namaz']:
		#it's not time for any namaz, ABORT
		return redirect("home")
	else:
		if salat_timings['namaz'] == 'Fajr':
			salat='1'
		elif salat_timings['namaz'] == 'Zuhr':
			salat='2'
		elif salat_timings['namaz'] == 'Asr':
			salat='3'
		elif salat_timings['namaz'] == 'Maghrib':
			salat='4'
		elif salat_timings['namaz'] == 'Isha':
			salat='5'
		else:
			return redirect("home")
		try:
			latest_namaz = LatestSalat.objects.filter(salatee=user).latest('when') #when did user pray most recently?
			if AlreadyPrayed(latest_namaz, now):
				return redirect("home")
			else:
				if streak_alive(latest_namaz,salat,now):
					user.userprofile.streak = user.userprofile.streak + 1
				else:
					user.userprofile.streak = 1
				latest_namaz.when = now
				latest_namaz.latest_salat = salat
				latest_namaz.skipped = False
				latest_namaz.save()
				user.userprofile.save()
		except:
			#the person hasn't prayed before, i.e. streak is at 0
			latest_salat = LatestSalat.objects.create(salatee=user, when=now, latest_salat=salat)
			user.userprofile.streak = 1
			user.userprofile.save()
		Salat.objects.create(prayee=user, timing=now, which_salat=salat)
		time = convert_to_epoch(starting_time)
		epochtime = convert_to_epoch(now)
		bulk_update_salat_notifications(viewer_id=user.id, starting_time=time, seen=True, updated_at=epochtime)
		return redirect("salat_success", current_minute, now.weekday())

def home_location(request, *args, **kwargs):
	try:
		link_id = request.session['target_id']
		request.session['target_id'] = None
	except:
		link_id = 0
	if request.user_banned:
		oblist = all_unfiltered_posts()
	else:
		oblist = all_filtered_posts()
	photo_ids, non_photo_link_ids, list_of_dictionaries = retrieve_home_links(oblist)
	request.session['home_photo_ids'] = photo_ids
	request.session['home_non_photo_link_ids'] = non_photo_link_ids
	request.session['home_list_of_dictionaries'] = list_of_dictionaries
	try:
		index = list(dictionary["l"] for dictionary in list_of_dictionaries).index(str(link_id))
	except:
		index = 0
	if 0 <= index <= 19:
		addendum = '#section'+str(index+1)
	elif 20 <= index <= 39:
		addendum = '?page=2#section'+str(index+1-20)
	elif 40 <= index <= 59:
		addendum = '?page=3#section'+str(index+1-40)
	elif 60 <= index <= 79:
		addendum = '?page=4#section'+str(index+1-60)
	elif 80 <= index <= 99:
		addendum = '?page=5#section'+str(index+1-80)
	elif 100 <= index <= 119:
		addendum = '?page=6#section'+str(index+1-100)
	elif 120 <= index <= 139:
		addendum = '?page=7#section'+str(index+1-120)
	elif 140 <= index <= 159:
		addendum = '?page=8#section'+str(index+1-140)
	elif 160 <= index <= 179:
		addendum = '?page=9#section'+str(index+1-160)
	elif 180 <= index <= 199:
		addendum = '?page=10#section'+str(index+1-180)
	else:
		addendum = '#section0'
	url = reverse_lazy("home")+addendum
	return redirect(url)

def home_link_list(request, *args, **kwargs):
	form = HomeListListForm()
	context = {}
	context["checked"] = FEMALES
	# calc_photo_quality_benchmark()
	context["form"] = form
	context["can_vote"] = False
	context["authenticated"] = False
	try:
		if request.session['home_photo_ids'] and request.session['home_non_photo_link_ids'] and request.session['home_list_of_dictionaries']:
			# kicks in if user redirected from vote page
			photo_ids = request.session['home_photo_ids']
			non_photo_link_ids = request.session['home_non_photo_link_ids']
			list_of_dictionaries = request.session['home_list_of_dictionaries']
			request.session['home_photo_ids'] = None
			request.session['home_non_photo_link_ids'] = None
			request.session['home_list_of_dictionaries'] = None
		else:
			# kicks in if person goes to next page by pressing aagey or wapis, or is coming in from another page (e.g. photos)
			if request.user_banned:
				oblist = all_unfiltered_posts()
			else:
				oblist = all_filtered_posts()
			photo_ids, non_photo_link_ids, list_of_dictionaries = retrieve_home_links(oblist)	
	except:
		# kicks in if user is not logged in
		if request.user_banned:
			oblist = all_unfiltered_posts()
		else:
			oblist = all_filtered_posts()
		photo_ids, non_photo_link_ids, list_of_dictionaries = retrieve_home_links(oblist)
		# ensures goes to 'else' above in next refresh, instead of hitting the expensive 'except' again and again
		request.session['home_photo_ids'] = None
		request.session['home_non_photo_link_ids'] = None
		request.session['home_list_of_dictionaries'] = None
	paginator = Paginator(list_of_dictionaries, 20) #give it a list of objects and number of objects to show per page, it does the rest
	page = request.GET.get('page', '1')
	try:
		page = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		page = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		page = paginator.page(paginator.num_pages)
	context["page"] = page
	############################################ Namaz feature #############################################
	now = datetime.utcnow()+timedelta(hours=5)
	day = now.weekday()
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
		})
	salat_timings = cache_mem.get('salat_timings')
	context["next_namaz_start_time"] = salat_timings['next_namaz_start_time']
	if salat_timings['namaz'] == 'Zuhr' and day == 4: #4 is Friday
		context["current_namaz"] = 'Jummah'
	else:
		context["current_namaz"] = salat_timings['namaz']
	if salat_timings['next_namaz'] == 'Zuhr' and day == 4:#4 if Friday
		context["next_namaz"] = 'Jummah'	
	else:
		context["next_namaz"] = salat_timings['next_namaz']
	if not salat_timings['namaz'] and not salat_timings['next_namaz']:
		# do not show namaz element at all, some error may have occurred
		context["show_current"] = False
		context["show_next"] = False
	elif not salat_timings['namaz']:
		if request.user.is_authenticated():
			try:
				latest_salat = LatestSalat.objects.filter(salatee=request.user).latest('when')
				already_prayed = AlreadyPrayed(latest_salat, now)
				if already_prayed == 2:
					#if user skipped previous namaz, no need to show prompt
					context["show_current"] = False
					context["show_next"] = False
				else:
					context["show_current"] = False
					context["show_next"] = True
			except:
				context["show_current"] = False
				context["show_next"] = True
		else:
			context["show_current"] = False
			context["show_next"] = True
	else:
		if request.user.is_authenticated():
			try:
				latest_salat = LatestSalat.objects.filter(salatee=request.user).latest('when')
				already_prayed = AlreadyPrayed(latest_salat, now)
				if already_prayed:
					if already_prayed == 2:
						context["show_current"] = False
						context["show_next"] = False
					else:
						context["show_current"] = False
						context["show_next"] = True
				else:
					#i.e. show the CURRENT namaz the user has to offer
					context["show_current"] = True
					context["show_next"] = False
			except:
				#never logged a salat in Damadam, i.e. show the CURRENT namaz the user has to offer
				context["show_current"] = True
				context["show_next"] = False
		else:
			context["show_current"] = True
			context["show_next"] = False
	################################################################################################################
	if request.user.is_authenticated():
		num = random.randint(1,4)
		context["random"] = num #determines which message to show at header
		if num > 2:
			context["newest_user"] = User.objects.latest('id') #for unauthenticated users
		else:
			context["newest_user"] = None
		context["authenticated"] = True
		user = request.user
		context["ident"] = user.id #own user id
		context["username"] = user.username #own username
		score = user.userprofile.score
		context["score"] = score #own score
		if score > 9:
			context["can_vote"] = True #allowing user to vote
		global condemned
		if request.user_banned:
			context["notification"] = 0 #hell banned users will never see notifications
			context["sender"] = 0 #hell banned users will never see notifications
		else:
			object_type, freshest_reply, is_link, is_photo, is_groupreply, is_salat = GetLatest(user)
			if not is_link and not is_photo and not is_groupreply and not is_salat:
				context["latest_reply"] = []
				context["notification"] = 0
				context["parent"] = []
				context["parent_pk"] = 0
				context["first_time_user"] = False
			elif not freshest_reply:
				context["latest_reply"] = []
				context["notification"] = 0
				context["parent"] = []
				context["parent_pk"] = 0
				context["first_time_user"] = False
			elif is_groupreply:
				if object_type == '1':
					# private mehfil
					context["type_of_object"] = '3a'
					context["notification"] = 1
					context["banned"] = False
					context["parent"] = freshest_reply
					context["parent_pk"] = freshest_reply['oi'] #group id
				elif object_type == '0':
					# public mehfil
					context["type_of_object"] = '3b'
					context["notification"] = 1
					context["banned"] = False
					context["first_time_user"] = False
					context["parent"] = freshest_reply
					context["parent_pk"] = freshest_reply['oi'] #group id
				else:
					context["latest_reply"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
			elif is_salat:
				salat_invite = freshest_reply
				context["type_of_object"] = '4'
				context["notification"] = 1
				try:
					context["first_time_user"] = UserProfile.objects.get(id=freshest_reply['ooi']).streak
				except:
					context["first_time_user"] = 0
				context["banned"] = False
				context["parent"] = salat_invite
				context["namaz"] = salat_timings['namaz'] 
			elif is_link:
				context["type_of_object"] = '2'
				if freshest_reply:
					parent_link_writer_username = freshest_reply['oon']#parent_link_writer.username
					WELCOME_MESSAGE1 = parent_link_writer_username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
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
					WELCOME_MESSAGES = []
				try:
					context["latest_reply"] = freshest_reply
					context["notification"] = 1
					context["parent"] = freshest_reply
					context["parent_pk"] = freshest_reply['oi']
					if user.username==parent_link_writer_username and any(freshest_reply['lrtx'] in s for s in WELCOME_MESSAGES):
						context["first_time_user"] = True
					else:
						context["first_time_user"] = False
				except:
					context["latest_reply"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
			elif is_photo:
				if object_type == '1':
					# photo = Photo.objects.get(id=freshest_reply)
					context["type_of_object"] = '1'
					context["notification"] = 1
					context["parent"] = freshest_reply
					context["parent_pk"] = freshest_reply['oi']
					context["first_time_user"] = False
					context["banned"] = False
				elif object_type == '0':
					context["latest_comment"] = freshest_reply
					context["type_of_object"] = '0'
					context["notification"] = 1
					context["parent"] = freshest_reply
					context["parent_pk"] = freshest_reply['oi']#.which_photo_id
					context["first_time_user"] = False
					context["banned"] = False						
				else:
					context["latest_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
				return render(request, 'link_list.html', context)
			else:
				return render(request, 'link_list.html', context)
	else:
		# print context
		return render(request, 'link_list.html', context)
	return render(request, 'link_list.html', context)


# class LinkListView(ListView):
# 	model = Link
# 	paginate_by = 20
# 	template_name = "link_list.html"

# 	def get_queryset(self):
# 		if self.request.user_banned:
# 			return all_unfiltered_posts()
# 		else:
# 			return all_filtered_posts()

# 	def get_context_data(self, **kwargs):
# 		context = super(LinkListView, self).get_context_data(**kwargs)
# 		context["checked"] = FEMALES
# 		# calc_photo_quality_benchmark()
# 		context["can_vote"] = False
# 		context["authenticated"] = False
# 		photo_ids, non_photo_link_ids, list_of_dictionaries = retrieve_home_links(context["object_list"])
# 		context["links"] = list_of_dictionaries
# 		###################### Namaz feature #######################################################################
# 		now = datetime.utcnow()+timedelta(hours=5)
# 		day = now.weekday()
# 		current_minute = now.hour * 60 + now.minute
# 		previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
# 		context["next_namaz_start_time"] = next_namaz_start_time
# 		if namaz == 'Zuhr' and day == 4: #4 is Friday
# 			context["current_namaz"] = 'Jummah'
# 		else:
# 			context["current_namaz"] = namaz
# 		if next_namaz == 'Zuhr' and day == 4:#4 if Friday
# 			context["next_namaz"] = 'Jummah'	
# 		else:
# 			context["next_namaz"] = next_namaz
# 		if not namaz and not next_namaz:
# 			# do not show namaz element at all, some error may have occurred
# 			context["show_current"] = False
# 			context["show_next"] = False
# 		elif not namaz:
# 			if self.request.user.is_authenticated():
# 				try:
# 					latest_salat = LatestSalat.objects.filter(salatee=self.request.user).latest('when')
# 					already_prayed = AlreadyPrayed(latest_salat, now)
# 					if already_prayed == 2:
# 						#if user skipped previous namaz, no need to show prompt
# 						context["show_current"] = False
# 						context["show_next"] = False
# 					else:
# 						context["show_current"] = False
# 						context["show_next"] = True
# 				except:
# 					context["show_current"] = False
# 					context["show_next"] = True
# 			else:
# 				context["show_current"] = False
# 				context["show_next"] = True
# 		else:
# 			if self.request.user.is_authenticated():
# 				try:
# 					latest_salat = LatestSalat.objects.filter(salatee=self.request.user).latest('when')
# 					already_prayed = AlreadyPrayed(latest_salat, now)
# 					if already_prayed:
# 						if already_prayed == 2:
# 							context["show_current"] = False
# 							context["show_next"] = False
# 						else:
# 							context["show_current"] = False
# 							context["show_next"] = True
# 					else:
# 						#i.e. show the CURRENT namaz the user has to offer
# 						context["show_current"] = True
# 						context["show_next"] = False
# 				except:
# 					#never logged a salat in Damadam, i.e. show the CURRENT namaz the user has to offer
# 					context["show_current"] = True
# 					context["show_next"] = False
# 			else:
# 				context["show_current"] = True
# 				context["show_next"] = False
# 		################################################################################################################
# 		if self.request.user.is_authenticated():
# 			num = random.randint(1,4)
# 			context["random"] = num #determines which message to show at header
# 			if num > 2:
# 				context["newest_user"] = User.objects.latest('id') #for unauthenticated users
# 			else:
# 				context["newest_user"] = None
# 			context["authenticated"] = True
# 			user = self.request.user
# 			context["ident"] = user.id #own user id
# 			context["username"] = user.username #own username
# 			score = user.userprofile.score
# 			context["score"] = score #own score
# 			if score > 9:
# 				context["can_vote"] = True #allowing user to vote
# 			global condemned
# 			if self.request.user_banned:
# 				context["notification"] = 0 #hell banned users will never see notifications
# 				context["sender"] = 0 #hell banned users will never see notifications
# 			else:
# 				object_type, freshest_reply, is_link, is_photo, is_groupreply, is_salat = GetLatest(user)
# 				if not is_link and not is_photo and not is_groupreply and not is_salat:
# 					context["latest_reply"] = []
# 					context["notification"] = 0
# 					context["parent"] = []
# 					context["parent_pk"] = 0
# 					context["first_time_user"] = False
# 				elif not freshest_reply:
# 					context["latest_reply"] = []
# 					context["notification"] = 0
# 					context["parent"] = []
# 					context["parent_pk"] = 0
# 					context["first_time_user"] = False
# 				elif is_groupreply:
# 					if object_type == '1':
# 						# private mehfil
# 						context["type_of_object"] = '3a'
# 						context["notification"] = 1
# 						context["banned"] = False
# 						context["parent"] = freshest_reply
# 						context["parent_pk"] = freshest_reply['oi'] #group id
# 					elif object_type == '0':
# 						# public mehfil
# 						context["type_of_object"] = '3b'
# 						context["notification"] = 1
# 						context["banned"] = False
# 						context["first_time_user"] = False
# 						context["parent"] = freshest_reply
# 						context["parent_pk"] = freshest_reply['oi'] #group id
# 					else:
# 						context["latest_reply"] = []
# 						context["notification"] = 0
# 						context["parent"] = []
# 						context["parent_pk"] = 0
# 						context["first_time_user"] = False
# 						context["banned"] = False
# 				elif is_salat:
# 					salat_invite = freshest_reply
# 					context["type_of_object"] = '4'
# 					context["notification"] = 1
# 					try:
# 						context["first_time_user"] = UserProfile.objects.get(id=freshest_reply['ooi']).streak
# 					except:
# 						context["first_time_user"] = 0
# 					context["banned"] = False
# 					context["parent"] = salat_invite
# 					context["namaz"] = namaz 
# 				elif is_link:
# 					context["type_of_object"] = '2'
# 					if freshest_reply:
# 						parent_link_writer_username = freshest_reply['oon']#parent_link_writer.username
# 						WELCOME_MESSAGE1 = parent_link_writer_username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
# 						WELCOME_MESSAGE2 = parent_link_writer_username+" welcome! Kesey ho? Yeh zalim barfi try kar yar (barfi)"
# 						WELCOME_MESSAGE3 = parent_link_writer_username+" assalam-u-alaikum! Is barfi se mu meetha karo (barfi)"
# 						WELCOME_MESSAGE4 = parent_link_writer_username+" Damadam pe welcome! One plate laddu se life set (laddu)"
# 						WELCOME_MESSAGE5 = parent_link_writer_username+" kya haal he? Ye laddu aap ke liye (laddu)"
# 						WELCOME_MESSAGE6 = parent_link_writer_username+" welcum! Life set hei? Laddu khao, jaan banao (laddu)"
# 						WELCOME_MESSAGE7 = parent_link_writer_username+" welcomeee! Yar kya hal he? Jalebi khao aur ayashi karo (jalebi)"
# 						WELCOME_MESSAGE8 = parent_link_writer_username+" kaisey ho? Jalebi meri pasandida hai! Tumhari bhi? (jalebi)"
# 						WELCOME_MESSAGE9 = parent_link_writer_username+" salam! Is jalebi se mu meetha karo (jalebi)"
# 						WELCOME_MESSAGES = [WELCOME_MESSAGE1, WELCOME_MESSAGE2, WELCOME_MESSAGE3, WELCOME_MESSAGE4, WELCOME_MESSAGE5,\
# 						WELCOME_MESSAGE6, WELCOME_MESSAGE7, WELCOME_MESSAGE8, WELCOME_MESSAGE9]
# 					else:
# 						parent_link_writer = User()
# 						WELCOME_MESSAGES = []
# 					try:
# 						context["latest_reply"] = freshest_reply
# 						context["notification"] = 1
# 						context["parent"] = freshest_reply
# 						context["parent_pk"] = freshest_reply['oi']
# 						if user.username==parent_link_writer_username and any(freshest_reply['lrtx'] in s for s in WELCOME_MESSAGES):
# 							context["first_time_user"] = True
# 						else:
# 							context["first_time_user"] = False
# 					except:
# 						context["latest_reply"] = []
# 						context["notification"] = 0
# 						context["parent"] = []
# 						context["parent_pk"] = 0
# 						context["first_time_user"] = False
# 				elif is_photo:
# 					if object_type == '1':
# 						# photo = Photo.objects.get(id=freshest_reply)
# 						context["type_of_object"] = '1'
# 						context["notification"] = 1
# 						context["parent"] = freshest_reply
# 						context["parent_pk"] = freshest_reply['oi']
# 						context["first_time_user"] = False
# 						context["banned"] = False
# 					elif object_type == '0':
# 						context["latest_comment"] = freshest_reply
# 						context["type_of_object"] = '0'
# 						context["notification"] = 1
# 						context["parent"] = freshest_reply
# 						context["parent_pk"] = freshest_reply['oi']#.which_photo_id
# 						context["first_time_user"] = False
# 						context["banned"] = False						
# 					else:
# 						context["latest_comment"] = []
# 						context["notification"] = 0
# 						context["parent"] = []
# 						context["parent_pk"] = 0
# 						context["first_time_user"] = False
# 						context["banned"] = False
# 					return context
# 				else:
# 					return context
# 		else:
# 			return context
# 		return context

# 	def get(self, request, *args, **kwargs):
# 		self.object_list = self.get_queryset()
# 		allow_empty = self.get_allow_empty() #Return a boolean specifying whether to display the page if no objects are available. If this method returns False and no objects are available, the view will raise a 404 instead of displaying an empty page. By default, this is True.
# 		if not allow_empty:
# 			# allow_empty is True by default in Django ListView, this this code never executes for us.
# 			# When pagination is enabled and object_list is a queryset,
# 			# it's better to do a cheap query than to load the unpaginated
# 			# queryset in memory.
# 			if (self.get_paginate_by(self.object_list) is not None
# 				and hasattr(self.object_list, 'exists')):
# 				# self.get_paginate_by(self.object_list) returns '20' in our case. It basically returns the number of items to paginate by, or None for no pagination. By default this simply returns the value of 'paginate_by'
# 				# hasattr: The arguments are an object and a string. The result is 'True' if the string is the name of one of the object's attributes, False if not. 
# 				is_empty = not self.object_list.exists()
# 			else:
# 				#this always executes, since hasattr(self.object_list, 'exists') is always False in our case
# 				is_empty = len(self.object_list) == 0 #is_empty is true or false, depending on the outcome
# 			if is_empty:
# 				# ensures empty list is just not displayed
# 				raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
# 						% {'class_name': self.__class__.__name__})
# 		context = self.get_context_data(object_list=self.object_list)
# 		try:
# 			target_id = self.request.session['target_id']
# 			self.request.session['target_id'] = None
# 		except:
# 			target_id = None
# 		if target_id:
# 			try:
# 				index = list(link_id for link_id in self.object_list).index(str(target_id))
# 			except:
# 				index = None
# 			if 0 <= index <= 19:
# 				addendum = '#section'+str(index+1)
# 			elif 20 <= index <= 39:
# 				addendum = '?page=2#section'+str(index+1-20)
# 			elif 40 <= index <= 59:
# 				addendum = '?page=3#section'+str(index+1-40)
# 			elif 60 <= index <= 79:
# 				addendum = '?page=4#section'+str(index+1-60)
# 			elif 80 <= index <= 99:
# 				addendum = '?page=5#section'+str(index+1-80)
# 			elif 100 <= index <= 119:
# 				addendum = '?page=6#section'+str(index+1-100)
# 			else:
# 				addendum = '#section0'
# 			return HttpResponseRedirect(addendum)
# 		else:
# 			return self.render_to_response(context)
# 			# Combines a given template with a given context variable dictionary, and returns an HttpResponse object with that rendered text.
# 			#I.e. just render the template normally, without redirecting to a specific anchor tag.

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
			try:
				user_id = self.request.session["appoint_id"]
				unique_id = self.request.session["public_uuid"]
				decision = self.request.session["appoint_decision"]
				context["authorized"] = True
				context["candidate"] = User.objects.get(id=user_id)
				context["appoint"] = decision
				context["unique"] = unique_id
			except:
				context["authorized"] = False
				context["candidate"] = None
				context["appoint"] = None
				context["unique"] = None
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
			if appoint == '1' and group.owner == self.request.user and not \
			GroupCaptain.objects.filter(which_user_id = candidate, which_group=group).exists():
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
				all_online_ids = get_attendance(group.id)
				visitors = User.objects.select_related('userprofile').filter(id__in=all_online_ids)
				captain_ids = GroupCaptain.objects.filter(which_user_id__in=all_online_ids, which_group=group).values_list("which_user_id",flat=True)
				captains = {captain:captain for captain in captain_ids}
				groupies = []
				for visitor in visitors:
					if visitor.id in captains.keys():
						groupies.append((visitor,visitor.id))
					else:
						groupies.append((visitor,None))
				context["groupies"] = groupies
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
				return context
			if group.private == '0':
				all_online_ids = get_attendance(group.id)
				visitors = User.objects.select_related('userprofile').filter(id__in=all_online_ids)
				captain_ids = GroupCaptain.objects.filter(which_group=group, which_user_id__in=all_online_ids).values_list('which_user_id', flat=True)
				captains = {captain:captain for captain in captain_ids}
				groupies = []
				for visitor in visitors:
					if visitor.id in captains.keys():
						groupies.append((visitor,visitor.id))
					else:
						groupies.append((visitor,None))
				context["groupies"] = groupies
			else:
				context["group"] = None
				context["unauthorized"] = True
				context["groupies"] = []
		return context

#@cache_page(20)
class OnlineKonView(ListView):
	model = Session
	template_name = "online_kon.html"
	paginate_by = 100

	def get_queryset(self):
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 30,
		})
		try:
			user_ids = cache_mem.get('online')
			queryset = User.objects.select_related('userprofile').filter(id__in=user_ids)
		except:
			queryset = []
		return queryset

	def get_context_data(self, **kwargs):
		context = super(OnlineKonView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			if not context["object_list"]:
				context["whose_online"] = False
			else:
				context["whose_online"] = True
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

def user_profile_photo(request, slug=None, photo_pk=None, is_notif=None, *args, **kwargs):
	if is_notif:
		# clicking single notif, for fans
		update_notification(viewer_id=request.user.id, object_id=photo_pk, object_type='0', seen=True, \
			updated_at=time.time(), bump_ua=False, unseen_activity=True, single_notif=False)
	if photo_pk:
		request.session["photograph_id"] = photo_pk
		return redirect("profile", slug)
	else:
		try:
			return redirect("profile", slug)
		except:
			return redirect("profile", request.user.username)

def profile_pk(request, slug=None, key=None, *args, **kwargs):
	request.session["photograph_id"] = key
	return redirect("profile", slug)

class UserProfilePhotosView(ListView):
	model = Photo
	template_name = "user_detail1.html"
	paginate_by = 10

	def get_queryset(self):
		slug = self.kwargs["slug"]
		try:
			user = User.objects.get(username=slug)
			return Photo.objects.select_related('owner__userprofile').filter(owner=user).order_by('-upload_time')
		except:
			return []

	def get_context_data(self, **kwargs):
		context = super(UserProfilePhotosView, self).get_context_data(**kwargs)
		slug = self.kwargs["slug"]
		context["slug"] = slug
		context["error"] = False
		try:
			subject = User.objects.get(username=slug)
		except:
			context["error"] = True
			return context
		star_id = subject.id
		context["subject"] = subject
		context["star_id"] = star_id
		context["legit"] = FEMALES
		try:
			context["fans"] = TotalFanAndPhotos.objects.get(owner_id=star_id).total_fans
		except:
			context["fans"] = 0
		try:
			now = datetime.utcnow()
			context["recent_fans"] = UserFan.objects.filter(star_id=star_id, fanning_time__gte=now).count()
		except:
			context["recent_fans"] = 0
		context["can_vote"] = False
		if self.request.user.is_authenticated():
			username = self.request.user.username
			context["authenticated"] = True
			score = self.request.user.userprofile.score
			context["score"] = score
			if score > 9 and not self.request.user_banned:
				context["can_vote"] = True
			# context["voted"] = [photo.id for photo in context["object_list"] if voted_for_photo(photo.id, username)]
			context["voted"] = voted_for_photo(context["object_list"],username)
			if UserFan.objects.filter(fan=self.request.user,star_id=star_id).exists():
				context["not_fan"] = False
			else:
				context["not_fan"] = True
			if username == slug:
				context["allowed_fan"] = False
				context["own_profile"] = True
				context["stars"] = UserFan.objects.filter(fan=self.request.user).count()
			else:
				context["subject_id"] = star_id
				context["own_profile"] = False
				context["allowed_fan"] = True
		else:
			context["authenticated"] = False
			context["not_fan"] = True
			context["allowed_fan"] = False
			context["own_profile"] = False
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
			target_id = self.request.session["photograph_id"]
			self.request.session["photograph_id"] = None
		except:
			target_id = None
		if target_id:
			try:
				index = list(photo.id for photo in self.object_list).index(int(target_id))
			except:
				index = None
			if 0 <= index <= 9:
				addendum = '#section'+str(index+1)
			elif 10 <= index <= 19:
				addendum = '?page=2#section'+str(index+1-10)
			elif 20 <= index <= 29:
				addendum = '?page=3#section'+str(index+1-20)
			elif 30 <= index <= 39:
				addendum = '?page=4#section'+str(index+1-30)
			elif 40 <= index <= 49:
				addendum = '?page=5#section'+str(index+1-40)
			elif 50 <= index <= 59:
				addendum = '?page=6#section'+str(index+1-50)
			elif 60 <= index <= 69:
				addendum = '?page=7#section'+str(index+1-60)
			elif 70 <= index <= 79:
				addendum = '?page=8#section'+str(index+1-70)
			elif 80 <= index <= 89:
				addendum = '?page=9#section'+str(index+1-80)
			elif 90 <= index <= 99:
				addendum = '?page=10#section'+str(index+1-90)
			elif 100 <= index <= 109:
				addendum = '?page=11#section'+str(index+1-100)
			elif 110 <= index <= 119:
				addendum = '?page=12#section'+str(index+1-110)
			elif 120 <= index <= 129:
				addendum = '?page=13#section'+str(index+1-120)
			elif 130 <= index <= 139:
				addendum = '?page=14#section'+str(index+1-130)
			elif 140 <= index <= 149:
				addendum = '?page=15#section'+str(index+1-140)
			elif 150 <= index <= 159:
				addendum = '?page=16#section'+str(index+1-150)
			elif 160 <= index <= 169:
				addendum = '?page=17#section'+str(index+1-160)
			elif 170 <= index <= 179:
				addendum = '?page=18#section'+str(index+1-170)
			elif 180 <= index <= 189:
				addendum = '?page=19#section'+str(index+1-180)
			elif 190 <= index <= 199:
				addendum = '?page=20#section'+str(index+1-190)
			else:
				addendum = '#section0'		
			return HttpResponseRedirect(addendum)
		else:
			return self.render_to_response(context)

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
				reply = Reply.objects.create(text=invitee, category='1', which_group_id=group.id, writer=self.request.user)
				#reply_list.append(Reply(text='aur g kia haal hai?', which_group_id=group.id, writer=self.request.user))
				#Reply.objects.bulk_create(reply_list)
				add_group_member(group.id, self.request.user.username)
				add_group_invite(pk, group.id,reply.id)
				add_user_group(self.request.user.id, group.id)
				return redirect("private_group", slug=unique)
			except:
				return redirect("profile", slug=invitee)

class ClosedGroupCreateView(CreateView):
	model = Group
	form_class = ClosedGroupCreateForm
	template_name = "new_closed_group.html"

	def form_valid(self, form):
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		user = self.request.user
		f.owner = user
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
		creation_text = 'mein ne new mehfil shuru kar di'
		reply = Reply.objects.create(text=creation_text,which_group=f,writer=user)
		reply_time = convert_to_epoch(reply.submitted_on)
		try:
			url = user.userprofile.avatar.url
		except:
			url = None
		user_id = user.id
		create_object(object_id=f.id, object_type='3',object_owner_id=user_id,object_desc=f.topic,lt_res_time=reply_time,\
			lt_res_avurl=url,lt_res_sub_name=user.username,lt_res_text=creation_text,group_privacy=f.private, slug=f.unique)
		create_notification(viewer_id=user_id,object_id=f.id,object_type='3',seen=True,updated_at=reply_time,unseen_activity=True)
		f.owner.userprofile.save()
		add_group_member(f.id, self.request.user.username)
		add_user_group(self.request.user.id, f.id)
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
			user = self.request.user
			f.owner = user
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
			f.owner.userprofile.save()
			f.save()
			creation_text = 'mein ne new mehfil shuru kar di'
			reply = Reply.objects.create(text=creation_text,which_group=f,writer=user)
			reply_time = convert_to_epoch(reply.submitted_on)
			try:
				url = user.userprofile.avatar.url
			except:
				url = None
			user_id = user.id
			f_id = f.id
			create_object(object_id=f_id, object_type='3',object_owner_id=user_id,object_desc=f.topic,lt_res_time=reply_time,\
				lt_res_avurl=url,lt_res_sub_name=user.username,lt_res_text=creation_text,group_privacy=f.private, slug=f.unique)
			create_notification(viewer_id=user_id,object_id=f_id,object_type='3',seen=True,updated_at=reply_time,unseen_activity=True)
			public_group_vote_tasks.delay(group_id=f_id,priority=2)
			public_group_attendance_tasks.delay(group_id=f_id, user_id=user_id)
			link = Link.objects.create(submitter=user, description=f.topic, cagtegory='2', url=unique)
			try:
				av_url = f.owner.userprofile.avatar.url
			except:
				av_url = None
			add_home_link(link_pk=link.id, categ='2', nick=f.owner.username, av_url=av_url, desc=f.topic, \
				scr=f.owner.userprofile.score, cc=1, writer_pk=f.owner.id, device='1', meh_url=unique)
			if self.request.user_banned:
				extras = add_unfiltered_post(link.id)
				if extras:
					queue_for_deletion.delay(extras)
			else:
				add_filtered_post(link.id)
				extras = add_unfiltered_post(link.id)
				if extras:
					queue_for_deletion.delay(extras)
			add_group_member(f_id, user.username)
			add_user_group(user.id, f_id)
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

def process_private_group_invite(request, uuid=None, pk=None, *args, **kwargs):
	if request.user_banned:
		return redirect("group_page")
	else:
		try:
			group = Group.objects.get(unique=uuid)
			group_id = group.id
		except:
			group_id = -1
		if group_id > -1:
			invitee = User.objects.get(id=pk)
			if check_group_invite(pk, group_id) or check_group_member(group_id, invitee.username):
				return redirect("reinvite_private_help")
			else:#this person ought to be sent an invite
				#send a notification to this person to check out the group
				reply = Reply.objects.create(text=invitee.username, category='1', which_group_id=group_id,writer=request.user)
				add_group_invite(pk, group_id,reply.id)
				GroupSeen.objects.create(seen_user=request.user, which_reply=reply)
		request.session["private_uuid"] = None
		return redirect("invite_private", slug=uuid)

class InviteUsersToPrivateGroupView(ListView):
	model = Session
	template_name = "invite_for_private_group.html"
	paginate_by = 100

	def get_queryset(self):
		if self.request.user_banned:
			return []
		else:
			cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 30,
			})
			global condemned
			try:
				user_ids = cache_mem.get('online')
				group = Group.objects.get(unique=self.request.session["private_uuid"])
				users_purified = [pk for pk in user_ids if pk not in condemned]
				non_invited_online_ids = bulk_check_group_invite(users_purified,group.id)
				non_invited_non_member_online_ids = bulk_check_group_membership(non_invited_online_ids,group.id)
				return User.objects.select_related('userprofile').filter(id__in=non_invited_non_member_online_ids)
			except:
				return []

	def get_context_data(self, **kwargs):
		context = super(InviteUsersToPrivateGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			# print "hello"
			context["legit"] = FEMALES
			try:	
				unique = self.request.session["private_uuid"]
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["authorized"] = True
				context["group"] = group
			except:
				context["authorized"] = False
		return context				

def process_public_group_invite(request, uuid=None, pk=None, *args, **kwargs):
	if request.user_banned:
		return redirect("group_page")
	else:	
		try:
			unique = uuid
			group = Group.objects.get(unique=unique)
			group_id = group.id
		except:
			group_id = -1
		if group_id > -1:
			invitee = User.objects.get(id=pk)
			if check_group_invite(pk, group_id) or check_group_member(group_id, invitee.username):
				return redirect("reinvite_help", slug= unique)
			else:#this person ought to be sent an invite
				#send a notification to this person to check out the group
				#GroupInvite.objects.create(inviter= self.request.user,which_group_id=group_id,invitee_id=invitee.id)
				#GroupInvite.objects.filter(which_group=group ,invitee=self.request.user).exists() to check if an invite already exists
				reply = Reply.objects.create(text=invitee.username, category='1', which_group_id=group_id,writer=request.user)
				add_group_invite(pk, group_id,reply.id)
				GroupSeen.objects.create(seen_user=request.user, which_reply=reply)
		return redirect("invite")

class InviteUsersToGroupView(ListView):
	model = Session
	template_name = "invite_for_groups.html"
	paginate_by = 100
	
	def get_queryset(self):
		if self.request.user_banned:
			return []
		else:
			cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 30,
			})	
			# user_ids = get_latest_online()#get_whose_online()
			global condemned
			try:
				user_ids = cache_mem.get('online')
				group = Group.objects.get(unique=self.request.session["public_uuid"])
				users_purified = [pk for pk in user_ids if pk not in condemned]
				# non_invited_online_ids = [pk for pk in users_purified if not check_group_invite(pk, group.id)] #i.e. ensure not invited to this group
				non_invited_online_ids = bulk_check_group_invite(users_purified,group.id)
				# non_invited_non_member_online_ids = [pk for pk in non_invited_online_ids if not is_member_of_group(group.id, pk)]
				non_invited_non_member_online_ids = bulk_check_group_membership(non_invited_online_ids,group.id)
				return User.objects.select_related('userprofile').filter(id__in=non_invited_non_member_online_ids)
			except:
				return []

	def get_context_data(self, **kwargs):
		context = super(InviteUsersToGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				context["legit"] = FEMALES
				unique = self.request.session["public_uuid"]
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
			except:
				context["group"] = None
		return context

class ExternalSalatInviteView(FormView):
	template_name = "salat_sms.html"
	form_class = ExternalSalatInviteForm

	def get_context_data(self, **kwargs):
		context = super(ExternalSalatInviteView, self).get_context_data(**kwargs)
		# now = datetime.utcnow()+timedelta(hours=5)
		# current_minute = now.hour * 60 + now.minute
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
		})
		salat_timings = cache_mem.get('salat_timings')
		# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
		if salat_timings['namaz']:
			context["namaz_time"] = True
			context["namaz"] = salat_timings['namaz']
			context["freebasics_url"] = "https://https-damadam-pk.0.freebasics.com"
			context["regular_url"] = "https://damadam.pk"
		else:
			context["namaz_time"] = False
		return context

class SalatInviteView(FormView):
	template_name = "salat_invite.html"
	form_class = SalatInviteForm

	def get_context_data(self, **kwargs):
		context = super(SalatInviteView, self).get_context_data(**kwargs)
		# now = datetime.utcnow()+timedelta(hours=5)
		# current_minute = now.hour * 60 + now.minute
		# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
		})
		salat_timings = cache_mem.get('salat_timings')
		if salat_timings['namaz']:
			context["namaz_time"] = True
			context["namaz"] = salat_timings['namaz']
		else:
			context["namaz_time"] = False
		return context

class InternalSalatInviteView(ListView):
	template_name = "internal_salat_invite.html"

	def get_queryset(self):
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 30,
			})
		try:
			user_ids = cache_mem.get('online')
			queryset = User.objects.select_related('userprofile').filter(id__in=user_ids)
		except:
			queryset = None
		return queryset

	def get_context_data(self, **kwargs):
		context = super(InternalSalatInviteView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			#get current namaz start time
			now = datetime.utcnow()+timedelta(hours=5)
			current_minute = now.hour * 60 + now.minute
			previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
			try:
				starting_time = datetime.combine(now.today(), current_namaz_start_time)
			except:
				context["user_list"] = None
				context["unauthorized"] = True #it's not time for any namaz!
				return context
			cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 30,
			})
			user_ids = cache_mem.get('online')
			if namaz:
				context["namaz"] = namaz
				context["unauthorized"] = False
				if namaz == 'Fajr':
					#check which users have been sent an invite for the current namaz, AFTER the current namaz's start time
					invites = SalatInvite.objects.filter(invitee_id__in=user_ids, which_salat='1', sent_at__gte=starting_time).values_list('invitee_id', flat=True)
					already_prayed = LatestSalat.objects.filter(salatee_id__in=user_ids, skipped=False, latest_salat='1',when__gte=starting_time).values_list('salatee_id', flat=True)
					#remove already invited and already prayed users from the object_list:
					context["user_list"] = [user for user in context["object_list"] if user.pk not in set(list(invites) + list(already_prayed))]
					#context["user_list"] = [user for user in context["user_list"] if user.pk not in already_prayed]
				elif namaz == 'Zuhr':
					#check which users have been sent an invite for the current namaz, AFTER the current namaz's start time
					invites = SalatInvite.objects.filter(invitee_id__in=user_ids, which_salat='2', sent_at__gte=starting_time).values_list('invitee_id', flat=True)
					already_prayed = LatestSalat.objects.filter(salatee_id__in=user_ids, skipped=False, latest_salat='2',when__gte=starting_time).values_list('salatee_id', flat=True)
					#remove already invited and already prayed users from the object_list:
					context["user_list"] = [user for user in context["object_list"] if user.pk not in set(list(invites) + list(already_prayed))]
				elif namaz == 'Asr':
					#check which users have been sent an invite for the current namaz, AFTER the current namaz's start time
					invites = SalatInvite.objects.filter(invitee_id__in=user_ids, which_salat='3', sent_at__gte=starting_time).values_list('invitee_id', flat=True)
					already_prayed = LatestSalat.objects.filter(salatee_id__in=user_ids, skipped=False, latest_salat='3',when__gte=starting_time).values_list('salatee_id', flat=True)
					#remove already invited and already prayed users from the object_list:
					context["user_list"] = [user for user in context["object_list"] if user.pk not in set(list(invites) + list(already_prayed))]
				elif namaz == 'Maghrib':
					#check which users have been sent an invite for the current namaz, AFTER the current namaz's start time
					invites = SalatInvite.objects.filter(invitee_id__in=user_ids, which_salat='4', sent_at__gte=starting_time).values_list('invitee_id', flat=True)
					already_prayed = LatestSalat.objects.filter(salatee_id__in=user_ids, skipped=False, latest_salat='4',when__gte=starting_time).values_list('salatee_id', flat=True)
					#remove already invited and already prayed users from the object_list:
					context["user_list"] = [user for user in context["object_list"] if user.pk not in set(list(invites) + list(already_prayed))]
				elif namaz == 'Isha':
					#check which users have been sent an invite for the current namaz, AFTER the current namaz's start time
					invites = SalatInvite.objects.filter(invitee_id__in=user_ids, which_salat='5', sent_at__gte=starting_time).values_list('invitee_id', flat=True)
					already_prayed = LatestSalat.objects.filter(salatee_id__in=user_ids, skipped=False, latest_salat='5',when__gte=starting_time).values_list('salatee_id', flat=True)
					#remove already invited and already prayed users from the object_list:
					context["user_list"] = [user for user in context["object_list"] if user.pk not in set(list(invites) + list(already_prayed))]
				else:
					context["user_list"] = None
					context["unauthorized"] = True #some error must have occurred, abort
			else:
				context["user_list"] = None
				context["unauthorized"] = True #it's not time for any namaz!
			return context
	
class GroupListView(ListView):
	model = Group
	form_class = GroupListForm
	template_name = "group_list.html"
	paginate_by = 25

	def get_queryset(self):
		# allGrps = []
		# date = datetime.now()-timedelta(minutes=60)
		# new_traff = GroupTraffic.objects.filter(time__gte=date,which_group__private='0').distinct('visitor','which_group').values_list('id',flat=True)
		# trendingGrp_ids = GroupTraffic.objects.filter(id__in=new_traff).values('which_group').annotate(total=Count('which_group')).order_by('-total')
		# trendingGrps = [Group.objects.select_related('owner').filter(id=grp['which_group']).extra(select={"views":grp['total']})[0] for grp in trendingGrp_ids]
		# return trendingGrps
		trending_groups = []
		group_ids_list = public_group_ranking()
		group_ids_dict = dict(group_ids_list)
		group_ids = map(itemgetter(0), group_ids_list)
		groups = Group.objects.select_related('owner').filter(id__in=group_ids)
		for group in groups:
			group_id = str(group.id)
			trending_groups.append((group,group_ids_dict[group_id]))
		trending_groups.sort(key=itemgetter(1), reverse=True)
		trending_groups = map(itemgetter(0), trending_groups)
		# trending_groups = [group[0] for group in trending_groups]
		return trending_groups

class VerifiedView(ListView):
	model = User
	form_class = VerifiedForm
	template_name = "verified.html"
	paginate_by = 100

	def get_queryset(self):
		global condemned
		return User.objects.filter(username__in=FEMALES).exclude(id__in=condemned).order_by('-userprofile__score')
		#return User.objects.exclude(id__in=condemned).order_by('-userprofile__score')[:100]

class TopPhotoView(ListView):
	model = User
	form_class = TotalFanAndPhotos
	template_name = "top_photo.html"

	def get_queryset(self):
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 660,
		})
		top_stars = cache_mem.get('fans')
		return top_stars

	def get_context_data(self, **kwargs):
		context = super(TopPhotoView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["verified"] = FEMALES
		return context

class TopView(ListView):
	model = User
	form_class = TopForm
	template_name = "top.html"

	def get_queryset(self):
		if self.request.user_banned:
			return User.objects.order_by('-userprofile__score')[:100]
		else:
			global condemned
			return User.objects.exclude(id__in=condemned).order_by('-userprofile__score').prefetch_related('userprofile')[:100]

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
		group_ids = get_user_groups(user.id)
		replies = Reply.objects.filter(which_group__in=group_ids).values('which_group_id').annotate(Max('id')).\
			values_list('id__max', flat=True)
		invite_reply_ids = get_active_invites(user.id) #contains all current invites
		invite_reply_ids |= set(replies) #doing union of two sets. Gives us all latest reply ids, minus any deleted replies (e.g. if the group object had been deleted)
		replies_qs = Reply.objects.select_related('writer__userprofile','which_group').filter(id__in=invite_reply_ids).\
			order_by('-id')[:60]
		replies = get_replies_with_seen(group_replies=replies_qs,viewer_id=self.request.user.id,object_type='3')
		return replies

	def get_context_data(self, **kwargs):
		context = super(GroupPageView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["verified"] = FEMALES
		return context

class GroupTypeView(FormView):
	form_class = GroupTypeForm
	template_name = "group_type.html"

class PhotoJawabView(FormView):
	form_class = PhotoJawabForm
	template_name = "photo_jawab.html"

class PhotoTimeView(FormView):
	form_class = PhotoTimeForm
	template_name = "photo_time.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoTimeView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			ident = self.kwargs["pk"]
			context["photo_time"] = Photo.objects.get(id=ident).upload_time
		return context

class AuthPicsDisplayView(ListView):
	model = ChatPic
	template_name = "pics_display.html"
	paginate_by = 8

	def get_queryset(self):
		if self.request.user.is_authenticated():
			return ChatPic.objects.filter(owner=self.request.user).exclude(is_visible=False).order_by('-upload_time')
		else:
			return 0

def photostream_pk(request, pk=None, ident=None, *args, **kwargs):
	if pk.isdigit():
		request.session["photo_photostream_id"] = pk
		request.session["photo_stream_id"] = ident
		return redirect("photostream")
	else:
		return redirect("see_photo")

class PhotostreamView(ListView):
	model = Photo
	#form_class = PhotostreamForm
	template_name = "photostream.html"
	paginate_by = 10

	def get_queryset(self):
		try:
			ps = PhotoStream.objects.filter(id=self.request.session["photo_photostream_id"])
			queryset = Photo.objects.filter(which_stream=ps).order_by('-upload_time')[:200]
		except:
			querset = []
		return queryset

	def get_context_data(self, **kwargs):
		context = super(PhotostreamView, self).get_context_data(**kwargs)
		context["girls"] = FEMALES
		if context["object_list"]:
			context["valid"] = True
		else:
			context["valid"] = False
		pk = self.request.session["photo_photostream_id"]
		context["stream_id"] = pk
		context["can_vote"] = False
		context["number"] = PhotoStream.objects.get(id=pk).photo_count
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
			target_id = self.request.session["photo_stream_id"]
			self.request.session["photo_stream_id"] = None
		except:
			target_id = None
		if target_id:
			try:
				index = list(photo.id for photo in self.object_list).index(int(target_id))
			except:
				index = None
			if 0 <= index <= 9:
				addendum = '#section'+str(index+1)
			elif 10 <= index <= 19:
				addendum = '?page=2#section'+str(index+1-10)
			elif 20 <= index <= 29:
				addendum = '?page=3#section'+str(index+1-20)
			elif 30 <= index <= 39:
				addendum = '?page=4#section'+str(index+1-30)
			elif 40 <= index <= 49:
				addendum = '?page=5#section'+str(index+1-40)
			elif 50 <= index <= 59:
				addendum = '?page=6#section'+str(index+1-50)
			elif 60 <= index <= 69:
				addendum = '?page=7#section'+str(index+1-60)
			elif 70 <= index <= 79:
				addendum = '?page=8#section'+str(index+1-70)
			elif 80 <= index <= 89:
				addendum = '?page=9#section'+str(index+1-80)
			elif 90 <= index <= 99:
				addendum = '?page=10#section'+str(index+1-90)
			elif 100 <= index <= 109:
				addendum = '?page=11#section'+str(index+1-100)
			elif 110 <= index <= 119:
				addendum = '?page=12#section'+str(index+1-110)
			elif 120 <= index <= 129:
				addendum = '?page=13#section'+str(index+1-120)
			elif 130 <= index <= 139:
				addendum = '?page=14#section'+str(index+1-130)
			elif 140 <= index <= 149:
				addendum = '?page=15#section'+str(index+1-140)
			elif 150 <= index <= 159:
				addendum = '?page=16#section'+str(index+1-150)
			elif 160 <= index <= 169:
				addendum = '?page=17#section'+str(index+1-160)
			elif 170 <= index <= 179:
				addendum = '?page=18#section'+str(index+1-170)
			elif 180 <= index <= 189:
				addendum = '?page=19#section'+str(index+1-180)
			elif 190 <= index <= 199:
				addendum = '?page=20#section'+str(index+1-190)
			else:
				addendum = '#section0'		
			return HttpResponseRedirect(addendum)
		else:
			return self.render_to_response(context)

class PhotoOptionTutorialView(FormView):
	form_class = PhotoOptionTutorialForm
	template_name = "photo_option_tutorial.html"

	def form_valid(self, form):
		if self.request.session["ftue_photo_option"]:
			self.request.session["ftue_photo_option"] = None
			if self.request.method == 'POST':
				option = self.request.POST.get("choice", '')
				if option == 'samajh gaya':
					if TutorialFlag.objects.filter(user=self.request.user).update(seen_photo_option=True):
						return redirect("link_create_pk")
					else:
						return redirect("home")
				else:
					return redirect("home")
		else:
			return redirect("link_create_pk")

class ChainPhotoTutorialView(FormView):
	form_class = ChainPhotoTutorialForm
	template_name = "chain_photo_tutorial.html"

	def form_valid(self, form):
		if self.request.session["ftue_chain"] and self.request.session["reply_photo_id"]:
			self.request.session["ftue_chain"] = None
			pk = self.request.session["reply_photo_id"]
			self.request.session["reply_photo_id"] = None
			if self.request.user_banned:
				return redirect("see_photo")
			else:
				#which_photo = Photo.objects.get(id=pk)
				if self.request.method == 'POST':
					option = self.request.POST.get("choice",'')
					if option == 'samajh gaya':
						try:
							TutorialFlag.objects.filter(user=self.request.user).update(seen_chain=True)
							return redirect("upload_photo_reply_pk", pk)
						except:
							return redirect("see_photo")
					else:
						return redirect("see_photo")
				else:
					return redirect("see_photo")
		else:
			return redirect("see_photo")

def upload_photo_reply_pk(request, pk=None, *args, **kwargs):
	if pk.isdigit():
		request.session["reply_photo_id"] = pk
		try:
			seen_chain = TutorialFlag.objects.get(user=request.user).seen_chain
			if seen_chain:
				return redirect("upload_photo_reply")
			else:
				request.session["ftue_chain"] = True
				return redirect("chain_photo_tutorial")
		except:
			request.session["ftue_chain"] = True
			TutorialFlag.objects.create(user=request.user)
			return redirect("chain_photo_tutorial")
	else:
		return redirect("see_photo")

class UploadPhotoReplyView(CreateView):
	model = Photo
	form_class = UploadPhotoReplyForm
	template_name = "upload_photo_reply.html"

	def get_context_data(self, **kwargs):
		context = super(UploadPhotoReplyView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				context["authenticated"] = True
				context["photo"] = Photo.objects.get(pk=self.request.session["reply_photo_id"])
			except:
				context["authenticated"] = False
				context["photo"] = None
		return context

	def form_valid(self, form):
		f = form.save(commit=False)
		try:
			pk = self.request.session["reply_photo_id"]
			self.request.session["reply_photo_id"] = None
			target = Photo.objects.get(id=pk)
		except:
			return redirect("see_photo")
		user = self.request.user
		if user.userprofile.score < 15:
			context = {'score': '15'}
			return render(self.request, 'score_photo.html', context)
		else:
			#time_now = datetime.utcnow().replace(tzinfo=utc)
			time_now = timezone.now()
			try:
				photocooldown = PhotoCooldown.objects.filter(which_user=user).latest('time_of_uploading')
				difference = time_now - photocooldown.time_of_uploading 
				seconds = difference.total_seconds()
				if seconds < 60:
					context = {'time': round((60 - seconds),0)}
					return render(self.request, 'error_photo.html', context)
				else:
					photocooldown.time_of_uploading = time_now
					photocooldown.save()
			except:
				PhotoCooldown.objects.create(which_user=user, time_of_uploading=time_now)
			if f.image_file:
				image_file = clean_image_file(f.image_file)
				if image_file:
					f.image_file = image_file
				else:
					f.image_file = None
			else:
				f.image_file = None
			if f.image_file:
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
				try:
					#photo being added to the head of a stream
					photo_stream = PhotoStream.objects.filter(cover=target).latest('creation_time')
					photo = Photo.objects.create(image_file = f.image_file, owner=user, caption=f.caption, comment_count=0, device=device)
					####################################
					try:
						aggregate_object = TotalFanAndPhotos.objects.get(owner=user)
						aggregate_object.total_photos = aggregate_object.total_photos + 1
						aggregate_object.last_updated = datetime.utcnow()+timedelta(hours=5)
						aggregate_object.save()
					except:
						TotalFanAndPhotos.objects.create(owner=user, total_fans=0, total_photos=1, last_updated=datetime.utcnow()+timedelta(hours=5))
					####################################
					photo.which_stream.add(photo_stream)
					photo_stream.cover = photo
					photo_stream.photo_count = photo_stream.photo_count + 1
					photo_stream.show_time = photo.upload_time
					photo_stream.save()
					#photo.save()
				except:
					#photo added anywhere in the middle of the stream, i.e. new stream being made
					photo = Photo.objects.create(image_file = f.image_file, owner=user, caption=f.caption, comment_count=0, device=device)
					####################################
					try:
						aggregate_object = TotalFanAndPhotos.objects.get(owner=user)
						aggregate_object.total_photos = aggregate_object.total_photos + 1
						aggregate_object.last_updated = datetime.utcnow()+timedelta(hours=5)
						aggregate_object.save()
					except:
						TotalFanAndPhotos.objects.create(owner=user, total_fans=0, total_photos=1, last_updated=datetime.utcnow()+timedelta(hours=5))
					####################################
					tail_photos = Photo.objects.filter(which_stream=target.which_stream.latest('creation_time')).exclude(upload_time__gt=target.upload_time).order_by('upload_time')
					tail_photos_count = tail_photos.count()
					stream = PhotoStream.objects.create(cover=photo, show_time=photo.upload_time, photo_count = (tail_photos_count + 1))
					photo.which_stream.add(stream)
					#gives you control of the 'through' model
					through_model = Photo.which_stream.through
					through_model.objects.bulk_create([
						through_model(photo_id=pk, photostream_id = stream.pk) for pk in tail_photos.values_list('pk', flat=True)
						])
				user.userprofile.score = user.userprofile.score - 10
				user.userprofile.save()
				return redirect("see_photo")
			else:
				context = {'photo': 'photo'}
				return render(self.request, 'big_photo.html', context)

def photostream_izzat(request, pk=None, *args, **kwargs):
	if pk.isdigit():
		try:
			stream_object_id = PhotoStream.objects.get(cover_id=pk).id
			return redirect("photo_izzat", stream_object_id)
		except:
			return redirect("see_photo")
	else:
		return redirect("see_photo")

class VideoScoreView(FormView):
	form_class = VideoScoreForm
	template_name = "video_score_breakdown.html"

	def get_context_data(self, **kwargs):
		context = super(VideoScoreView, self).get_context_data(**kwargs)
		key = self.kwargs["pk"]
		context["key"] = key
		if self.request.user.is_authenticated():
			context["authenticated"] = True
		else:
			context["authenticated"] = False
		video = Video.objects.get(id=key)
		context["video"] = video
		usernames_and_votes = get_video_votes(key)
		context["votes"] = usernames_and_votes
		if context["votes"]:
			context["content"] = True
			context["visible_score"] = video.visible_score 
		else:
			context["content"] = False
			context["visible_score"] = video.visible_score
		context["girls"] = FEMALES
		return context


class PhotoScoreView(FormView):
	form_class = PhotoScoreForm
	template_name = "photo_score_breakdown.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoScoreView, self).get_context_data(**kwargs)
		key = self.kwargs["pk"]
		context["origin"] = self.kwargs["origin"]
		context["key"] = key
		if context["origin"] == '3':
			#if originating from user profile
			context["slug"] = self.kwargs["slug"]
		if self.request.user.is_authenticated():
			context["authenticated"] = True
		else:
			context["authenticated"] = False
		cover_photo = Photo.objects.get(id=key)
		context["photo"] = cover_photo
		usernames_and_votes = get_photo_votes(key)
		context["votes"] = usernames_and_votes
		if context["votes"]:
			context["content"] = True
			context["visible_score"] = cover_photo.visible_score 
		else:
			context["content"] = False
			context["visible_score"] = cover_photo.visible_score
		context["girls"] = FEMALES
		return context

@ratelimit(rate='2/s')
def reply_to_photo(request, pk=None, ident=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_photocomment.html', context)
		except:
			context = {'pk': 'pk'}
			return render(request, 'penalty_photocomment.html', context)
	else:
		if pk.isdigit():
			request.session["photo_id"] = pk
			request.session["related_photostream_id"] = ident
			return redirect("reply_options")
		else:
			return redirect("profile", request.user.username )

class PhotoReplyView(FormView):
	form_class = PhotoReplyForm
	template_name = "photo_reply.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoReplyView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				pk = self.request.session["photo_id"]
				if pk:
					context["photo"] = Photo.objects.get(id=pk)
					context["stream_related_id"] = self.request.session["related_photostream_id"]
					context["count"] = PhotoComment.objects.filter(which_photo= pk).count()
					context["comments"] = PhotoComment.objects.filter(which_photo= pk)
					context["authenticated"] = True
				else:
					context["photo"] = None
					context["authenticated"] = False
					context["comments"] = None
					context["count"] = None
			except:
				context["photo"] = None
				context["authenticated"] = False
				context["comments"] = None
				context["count"] = None
			return context

	def form_valid(self, form):
		try:
			pk = self.request.session["photo_id"]
			self.request.session["photo_id"] = None
			which_photo = Photo.objects.get(id=pk)
			if self.request.user_banned:
				return redirect("see_photo")
			else:
				if self.request.method == 'POST':
					option = self.request.POST.get("option")
					if option == 'Photo lagao':
						return redirect("upload_photo_reply_pk", pk)
					else:
						return redirect("comment_pk", pk)
				else:
					return redirect("see_photo")
		except:
			return redirect("see_photo")

@ratelimit(rate='2/s')
def comment_profile_pk(request, pk=None, user_id=None, from_photos=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_commentpk.html', context)
		except:
			context = {'pk': 'pk'}
			return render(request, 'penalty_commentpk.html', context)
	else:
		if pk.isdigit() and user_id.isdigit() and from_photos.isdigit():
			request.session["photo_id"] = pk
			request.session["star_user_id"] = user_id
			return redirect("comment", from_photos)
		else:
			return redirect("see_photo")

@ratelimit(rate='2/s')
def videocomment_pk(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_videocommentpk.html', context)
		except:
			context = {'pk': '10'}
			return render(request, 'penalty_videocommentpk.html', context)
	else:
		if pk.isdigit():
			request.session["video_pk"] = pk
			return redirect("video_comment")
		else:
			return redirect("home")

class VideoCommentView(CreateView):
	model = VideoComment
	form_class = VideoCommentForm
	template_name = "video_comments.html"

	def get_context_data(self, **kwargs):
		context = super(VideoCommentView, self).get_context_data(**kwargs)
		context["verified"] = FEMALES
		try:
			on_fbs = self.request.META.get('X-IORG-FBS')
		except:
			on_fbs = False
		if on_fbs:
			context["on_fbs"] = True
		else:
			context["on_fbs"] = False
		try:
			pk = self.request.session["video_pk"]
			video = Video.objects.select_related('owner').get(id=pk)
			context["video"] = video
			comms = VideoComment.objects.select_related('submitted_by__userprofile').filter(which_video_id=pk)
			context["count"] = comms.count()
			comments = comms.order_by('-id')[:25]
			context["comments"] = comments
		except:
			context["video"] = None
		return context

	def form_valid(self, form):
		if self.request.user.is_authenticated():
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			user = self.request.user
			text = self.request.POST.get("text")
			try:
				pk = self.request.session["video_pk"]
				self.request.session["video_pk"] = None
				which_video = Video.objects.get(id=pk)
			except:
				user.userprofile.score = user.userprofile.score - 3
				user.userprofile.save()
				return redirect("profile", slug=user.username)
			score = fuzz.ratio(text, user.userprofile.previous_retort)
			if score > 86:
				try:
					return redirect("videocomment_pk", pk=pk)
				except:
					user.userprofile.score = user.userprofile.score - 3
					user.userprofile.save()
					return redirect("profile", slug=user.username)
			else:
				if self.request.user_banned:
					return redirect("see_video")
				else:
					exists = VideoComment.objects.filter(which_video=which_video, submitted_by=user).exists()
					comments = which_video.comment_count + 1
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
					videocomment = VideoComment.objects.create(submitted_by=user, which_video=which_video, text=text,device=device)
					time = videocomment.submitted_on
					timestring = time.isoformat()
					video_tasks.delay(self.request.user.id, pk, timestring, videocomment.id, comments, text, exists)
					try:
						return redirect("videocomment_pk", pk=pk)
					except:
						return redirect("profile", slug=user.username)
		else:
			context = {'pk': 'pk'}
			return render(self.request, 'auth_commentpk.html', context)

@ratelimit(rate='2/s')
def comment_chat_pk(request, pk=None, ident=None,*args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_commentpk.html', context)
		except:
			context = {'pk': 'pk'}
			return render(request, 'penalty_commentpk.html', context)
	else:
		try:
			request.session["first_time"] = True
			return redirect("comment_pk",pk,'6',ident)
		except:
			return redirect("see_photo")

@ratelimit(rate='2/s')
def comment_pk(request, pk=None, origin=None, ident=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_commentpk.html', context)
		except:
			context = {'pk': '10'}
			return render(request, 'penalty_commentpk.html', context)
	else:
		if pk.isdigit():
			request.session["photo_id"] = pk
			if ident:
				request.session["user_ident"] = ident
			else:
				request.session["user_ident"] = None
			if origin:
				return redirect("comment", origin)
			else:
				return redirect("comment")
		else:
			return redirect("see_photo")	

class CommentView(CreateView):
	model = PhotoComment
	form_class = CommentForm
	template_name = "comments.html"

	def get_context_data(self, **kwargs):
		context = super(CommentView, self).get_context_data(**kwargs)
		if self.request.is_feature_phone:
			context["feature_phone"] = True
		else:
			context["feature_phone"] = False
		try:
			pk = self.request.session["photo_id"]
			photo = Photo.objects.select_related('owner').get(id=pk)
			context["photo"] = photo
			comms = PhotoComment.objects.select_related('submitted_by__userprofile').filter(which_photo_id=pk)
			context["count"] = comms.count()
			comments = comms.order_by('-id')[:25]
			context["comments"] = comments
			context["verified"] = FEMALES
			context["random"] = random.sample(xrange(1,188),15) #select 15 random emoticons out of 188
			context["authorized"] = True
		except:
			context["authorized"] = False
			context["photo"] = None
			context["count"] = None
			return context
		try:
			origin=self.kwargs["origin"]
			if origin == '1':
				context["origin"] = '1'
				context["photo_id"] = pk
			elif origin == '2':
				context["origin"] = '2'
				context["photo_id"] = pk
			elif origin == '3':
				context["origin"] = '3'
				try:
					star_user_id = self.request.session["user_ident"]
					username = User.objects.get(id=star_user_id).username
					context["username"] = username
				except:
					context["origin"] = '1'
			elif origin == '5':
				context["origin"] = '5'
				context["photo_id"] = pk
			elif origin == '6':
				context["origin"] = '6'
				link_ident = self.request.session["user_ident"]
				if link_ident:
					#if originating from a specific link
					context["link_ident"] = self.request.session["user_ident"]
					self.request.session['target_id'] = self.request.session["user_ident"] #mislabled - actually contains link_id
				else:
					#if originating from a notification
					self.request.session['target_id'] = None
			else:
				context["origin"] = '1'
		except:
			context["origin"] = '1'
		try:
			is_first = self.request.session["first_time"]
			self.request.session["first_time"] = False
			context["is_first"] = is_first
		except:
			context["is_first"] = False
		if self.request.user.is_authenticated():
			banned, time_remaining, warned = comment_allowed(self.request.user.id)			
			context["banned"] = banned
			context["warned"] = warned
			if banned:
				m, s = divmod(time_remaining, 60)
				h, m = divmod(m, 60)
				d, h = divmod(h, 24)
				if d and h and m:
					context["time_remaining"] = "%s days, %s hours and %s minutes" % (int(d), int(h), int(m))
				elif h and m:
					context["time_remaining"] = "%s hours and %s minutes" % (int(h), int(m))
				elif m and s:
					context["time_remaining"] = "%s minutes and %s seconds" % (int(m), int(s))
				elif s:
					context["time_remaining"] = "%s seconds" % int(s)
				else:
					context["time_remaining"] = None
				# return context
			else:
				context["time_remaining"] = None
			context["authenticated"] = True
			try:
				if origin == '4':
					#i.e. user originiated from unseen_activity
					context["origin"] = '4'
					star_user_id = self.request.session["user_ident"]
					context["slug_id"] = star_user_id
					username = User.objects.get(id=star_user_id).username
					context["username"] = username
				else:
					pass
			except:
				context["origin"] = '1'
			updated = update_notification(viewer_id=self.request.user.id, object_id=pk,object_type='0',seen=True,\
					updated_at=time.time(),single_notif=False, unseen_activity=True,priority='photo_tabsra',\
					bump_ua=False,no_comment=True)
			if comments:
				# updated = update_notification(viewer_id=self.request.user.id, object_id=pk,object_type='0',seen=True,\
				# 	updated_at=time.time(),single_notif=False, unseen_activity=True,priority='photo_tabsra',\
				# 	bump_ua=False,no_comment=True)
				if updated:
					context["unseen"] = True
					try:
						#finding latest time user herself commented
						context["comment_time"] = max(comment.submitted_on for comment in comments if comment.submitted_by == self.request.user)
					except:
						context["comment_time"] = None #i.e. it's the first every comment
				else:
					context["unseen"] = False
					context["comment_time"] = None
			else:
				context["unseen"] = False
				context["comment_time"] = None
		else:
			context["authenticated"] = False
		return context


	def form_valid(self, form):
		if self.request.user.is_authenticated():
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			user = self.request.user
			text = self.request.POST.get("text")
			origin = self.request.POST.get("origin")
			star_user_id = None
			link_id = None
			try:
				pk = self.request.session["photo_id"]
				self.request.session["photo_id"] = None
				which_photo = Photo.objects.get(id=pk)
			except:
				user.userprofile.score = user.userprofile.score - 3
				user.userprofile.save()
				return redirect("profile", slug=user.username)
			if origin == '3' or origin == '4':
				try:
					star_user_id = self.request.session["user_ident"]
					self.request.session["user_ident"] = None
				except:
					star_user_id = None
			elif origin == '6':
				link_id = self.request.session["user_ident"]
				self.request.session["user_ident"] = None
				self.request.session["target_id"] = link_id				
			score = fuzz.ratio(text, user.userprofile.previous_retort)
			if score > 86:
				try:
					return redirect("comment_pk", pk=pk)
				except:
					user.userprofile.score = user.userprofile.score - 3
					user.userprofile.save()
					return redirect("profile", slug=user.username)
			else:
				if self.request.user_banned:
					return redirect("see_photo")
				else:
					exists = PhotoComment.objects.filter(which_photo=which_photo, submitted_by=user).exists()
					# which_photo.comment_count = which_photo.comment_count + 1
					update_cc_in_home_photo(which_photo.id)
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
					photocomment = PhotoComment.objects.create(submitted_by=user, which_photo=which_photo, text=text,device=device)
					comment_time = convert_to_epoch(photocomment.submitted_on)
					try:
						url = user.userprofile.avatar.url
					except:
						url = None
					photo_tasks.delay(user.id, which_photo.id, comment_time, photocomment.id, which_photo.comment_count, text, \
						exists, user.username, url)
					if pk and origin and link_id:
						return redirect("comment_pk",pk=pk,origin=origin, ident=link_id)
					elif pk and origin and star_user_id:
						return redirect("comment_pk",pk=pk,origin=origin, ident=star_user_id)
					elif pk and origin:
						return redirect("comment_pk",pk=pk,origin=origin)
					elif pk:
						#fires if user from chat
						return redirect("comment_pk", pk=pk)
					else:
						return redirect("see_photo")
		else:
			context = {'pk': 'pk'}
			return render(self.request, 'auth_commentpk.html', context)

@ratelimit(rate='2/s')
def see_special_photo_pk(request,pk=None,*args,**kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_special.html', context)
		except:
			context = {'pk': '10'}
			return render(request, 'penalty_special.html', context)
	else:
		if pk.isdigit():
			request.session["target_special_photo_id"] = pk
			return redirect("see_special_photo")
		else:
			return redirect("see_special_photo")

@ratelimit(rate='2/s')
def special_photo(request, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_special.html', context)
		except:
			context = {'pk': '10'}
			return render(request, 'penalty_special.html', context)
	else:
		if request.user.is_authenticated() and request.user.userprofile.score > 29:
			try:
				seen_special_photo_option = TutorialFlag.objects.get(user=request.user).seen_special_photo_option
				if seen_special_photo_option:
					request.session["ftue_special_photo_option"] = False
					return redirect("see_special_photo")
				else:
					request.session["ftue_special_photo_option"] = True
					return redirect("special_photo_tutorial")
			except:
				TutorialFlag.objects.create(user=request.user)
				request.session["ftue_special_photo_option"] = True
				return redirect("special_photo_tutorial")
		else:
			return redirect("see_special_photo")

class SpecialPhotoTutorialView(FormView):
	form_class = SpecialPhotoTutorialForm
	template_name = "special_photo_tutorial.html"

	def form_valid(self, form):
		if self.request.method == 'POST':
			try:
				choice = self.request.POST.get("choice")
				if choice == 'samajh gaya':
					flag = TutorialFlag.objects.filter(user=self.request.user).update(seen_special_photo_option=True)
					self.request.session["ftue_special_photo_option"] = None
					return redirect("see_special_photo")
				else:
					return redirect("see_photo")
			except:
				TutorialFlag.objects.filter(user=self.request.user).update(seen_special_photo_option=True)
				return redirect("see_special_photo")
		else:
			TutorialFlag.objects.filter(user=self.request.user).update(seen_special_photo_option=True)
			return redirect("see_special_photo")


class SpecialPhotoView(ListView):
	model = Photo
	template_name = "special_photos.html"
	paginate_by = 10 #i.e. 10 pages in total with a query-set of 200 objects

	def get_queryset(self):
		if self.request.is_feature_phone:
			queryset = Photo.objects.select_related('owner__userprofile', 'cover__latest_comment__submitted_by', 'second_latest_comment__submitted_by').filter(category='7').order_by('-id')[:200]
		else:
			queryset = Photo.objects.select_related('owner__userprofile', 'cover__latest_comment__submitted_by', 'second_latest_comment__submitted_by').filter(category='7').order_by('-id')[:200]
		return queryset

	def get_context_data(self, **kwargs):
		context = super(SpecialPhotoView, self).get_context_data(**kwargs)
		context["girls"] = FEMALES
		context["authenticated"] = False
		context["can_vote"] = False
		context["score"] = None
		if self.request.user.is_authenticated():
			context["authenticated"] = True
			user = self.request.user
			context["score"] = user.userprofile.score
			context["voted"] = []
			if not self.request.user_banned:
				if self.request.user.userprofile.score > 9:
					context["can_vote"] = True
				else:
					context["can_vote"] = False
				photos_in_page = [photo.id for photo in context["object_list"]]
				vote_cluster = PhotoVote.objects.filter(photo_id__in=photos_in_page)
				context["voted"] = vote_cluster.filter(voter=user).values_list('photo_id', flat=True)
				object_type, freshest_reply, is_link, is_photo, is_groupreply, is_salat = GetLatest(user)
				if not is_link and not is_photo and not is_groupreply and not is_salat:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
					return context
				elif not freshest_reply:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
					return context
				elif is_salat:
					# now = datetime.utcnow()+timedelta(hours=5)
					# current_minute = now.hour * 60 + now.minute
					# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
					cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
						'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
					})
					salat_timings = cache_mem.get('salat_timings')
					salat_invite = freshest_reply
					context["type_of_object"] = '4'
					context["notification"] = 1
					context["first_time_user"] = False
					context["banned"] = False
					context["parent"] = salat_invite
					context["namaz"] = salat_timings['namaz'] 
					context["freshest_unseen_comment"] = 1				
				elif is_photo:
					if object_type == '1':
						#i.e. it's a photo a fan ought to see!
						photo = Photo.objects.get(id=freshest_reply)
						context["freshest_unseen_comment"] = None
						context["type_of_object"] = '1'
						context["notification"] = 1
						context["parent"] = photo
						context["parent_pk"] = freshest_reply
						context["first_time_user"] = False
						context["banned"] = False
					elif object_type == '0':
						context["freshest_unseen_comment"] = freshest_reply
						context["type_of_object"] = '0'
						context["notification"] = 1
						context["parent"] = freshest_reply.which_photo
						context["parent_pk"] = freshest_reply.which_photo_id
						context["photostream_id"]=PhotoStream.objects.get(cover_id=context["parent_pk"]).id
						context["first_time_user"] = False
						context["banned"] = False
					else:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
						context["banned"] = False
					return context
				elif is_link:
					context["type_of_object"] = '2'
					context["banned"] = False
					if freshest_reply:
						parent_link = freshest_reply.answer_to
						parent_link_writer = parent_link.submitter
						parent_link_writer_username = parent_link_writer.username
						WELCOME_MESSAGE1 = parent_link_writer_username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
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
						context["freshest_unseen_comment"] = freshest_reply
						context["notification"] = 1
						context["parent"] = parent_link
						context["parent_pk"] = parent_link.pk
						if user==parent_link_writer and any(freshest_reply.description in s for s in WELCOME_MESSAGES):
							context["first_time_user"] = True
						else:
							context["first_time_user"] = False
					except:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
					return context
				elif is_groupreply:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["type_of_object"] = '1'
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
					return context
				else:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["banned"] = False
					context["first_time_user"] = False
					return context
			else:
				context["notification"] = 0
				context["banned"] = True
				context["can_vote"] = False
				context["first_time_user"] = False
				context["type_of_object"] = None
				context["freshest_unseen_comment"] = []
				context["parent"] = []
				context["parent_pk"] = 0
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
			target_id = self.request.session["target_special_photo_id"]
			self.request.session["target_special_photo_id"] = None
		except:
			target_id = None
		if target_id:
			try:
				index = list(photo.id for photo in self.object_list).index(int(target_id))
			except:
				index = None
			if 0 <= index <= 9:
				addendum = '#section'+str(index+1)
			elif 10 <= index <= 19:
				addendum = '?page=2#section'+str(index+1-10)
			elif 20 <= index <= 29:
				addendum = '?page=3#section'+str(index+1-20)
			elif 30 <= index <= 39:
				addendum = '?page=4#section'+str(index+1-30)
			elif 40 <= index <= 49:
				addendum = '?page=5#section'+str(index+1-40)
			elif 50 <= index <= 59:
				addendum = '?page=6#section'+str(index+1-50)
			elif 60 <= index <= 69:
				addendum = '?page=7#section'+str(index+1-60)
			elif 70 <= index <= 79:
				addendum = '?page=8#section'+str(index+1-70)
			elif 80 <= index <= 89:
				addendum = '?page=9#section'+str(index+1-80)
			elif 90 <= index <= 99:
				addendum = '?page=10#section'+str(index+1-90)
			elif 100 <= index <= 109:
				addendum = '?page=11#section'+str(index+1-100)
			elif 110 <= index <= 119:
				addendum = '?page=12#section'+str(index+1-110)
			elif 120 <= index <= 129:
				addendum = '?page=13#section'+str(index+1-120)
			elif 130 <= index <= 139:
				addendum = '?page=14#section'+str(index+1-130)
			elif 140 <= index <= 149:
				addendum = '?page=15#section'+str(index+1-140)
			elif 150 <= index <= 159:
				addendum = '?page=16#section'+str(index+1-150)
			elif 160 <= index <= 169:
				addendum = '?page=17#section'+str(index+1-160)
			elif 170 <= index <= 179:
				addendum = '?page=18#section'+str(index+1-170)
			elif 180 <= index <= 189:
				addendum = '?page=19#section'+str(index+1-180)
			elif 190 <= index <= 199:
				addendum = '?page=20#section'+str(index+1-190)
			else:
				addendum = '#section0'		
			return HttpResponseRedirect(addendum)
		else:
			return self.render_to_response(context)

def see_photo_pk(request,pk=None,*args,**kwargs):
	if pk.isdigit():
		request.session["target_photo_id"] = pk
		return redirect("see_photo")
	else:
		return redirect("see_photo")

def non_fbs_vid(request, pk=None, *args, **kwargs):
	try:
		on_fbs = self.request.META.get('X-IORG-FBS')
	except:
		on_fbs = False
	return redirect("https://damadam.pk/"+"123")

class VideoView(ListView):
	model = Video
	#queryset = Video.objects.filter(id__in=all_videos()).order_by('-id')
	paginate_by = 10
	template_name = "videos.html"

	def get_queryset(self):
		queryset = Video.objects.select_related('owner__userprofile', 'latest_comment__submitted_by', 'second_latest_comment__submitted_by').filter(id__in=all_videos()).order_by('-id')
		return queryset

	def get_context_data(self, **kwargs):
		context = super(VideoView, self).get_context_data(**kwargs)
		context["girls"] = FEMALES
		context["authenticated"] = False
		context["can_vote"] = False
		context["score"] = None
		try:
			on_fbs = self.request.META.get('X-IORG-FBS')
		except:
			on_fbs = False
		if on_fbs:
			context["on_fbs"] = True
		else:
			context["on_fbs"] = True
		if self.request.user.is_authenticated():
			context["authenticated"] = True
			user = self.request.user
			context["score"] = user.userprofile.score
			context["voted"] = []
			if not self.request.user_banned:
				if self.request.user.userprofile.score > 9:
					context["can_vote"] = True
				else:
					context["can_vote"] = False
				#videos_in_page = [video.id for video in context["object_list"]]
				# context["voted"] = [video.id for video in context["object_list"] if voted_for_video(video.id, user.username)]
				context["voted"] = voted_for_video(context["object_list"], user.username)
		return context

class PhotoView(ListView):
	model = Photo
	template_name = "photos.html"
	paginate_by = 10

	def get_queryset(self):
		queryset = Photo.objects.select_related('owner__userprofile','latest_comment','second_latest_comment').filter(id__in=all_photos()).order_by('-id')
		#queryset = Photo.objects.select_related('owner__userprofile','latest_comment__submitted_by','second_latest_comment__submitted_by').order_by('-upload_time')[:200]
		return queryset

	def get_context_data(self, **kwargs):
		context = super(PhotoView, self).get_context_data(**kwargs)
		context["girls"] = FEMALES
		context["authenticated"] = False
		context["can_vote"] = False
		context["score"] = None
		try:
			on_fbs = self.request.META.get('X-IORG-FBS')
		except:
			on_fbs = False
		if on_fbs:
			context["on_fbs"] = True
		else:
			context["on_fbs"] = False
		if self.request.is_feature_phone:
			context["feature_phone"] = True
			context["is_android_phone"] = False
		elif self.request.is_android_phone:
			context["is_android_phone"] = True
			context["feature_phone"] = False
		elif self.request.is_iphone:
			context["is_android_phone"] = True
			context["feature_phone"] = False
		else:
			context["feature_phone"] = False
			context["is_android_phone"] = True
		if self.request.user.is_authenticated():
			context["authenticated"] = True
			user = self.request.user
			context["score"] = user.userprofile.score
			context["voted"] = []
			if not self.request.user_banned:
				if self.request.user.userprofile.score > 9:
					context["can_vote"] = True
				else:
					context["can_vote"] = False
				context["voted"] = voted_for_photo(context["object_list"],user.username)
				object_type, freshest_reply, is_link, is_photo, is_groupreply, is_salat = GetLatest(user)
				if not is_link and not is_photo and not is_groupreply and not is_salat:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
					return context
				elif not freshest_reply:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
					return context
				elif is_groupreply:
					# print freshest_reply
					if object_type == '1':
						# private mehfil
						context["type_of_object"] = '3a'
						context["notification"] = 1
						context["banned"] = False
						context["first_time_user"] = False
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi'] #group id
					elif object_type == '0':
						# public mehfil
						context["type_of_object"] = '3b'
						context["notification"] = 1
						context["banned"] = False
						context["first_time_user"] = False
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi'] #group id
					else:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
						context["banned"] = False
				elif is_salat:
					# now = datetime.utcnow()+timedelta(hours=5)
					# current_minute = now.hour * 60 + now.minute
					# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
					cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
						'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
					})
					salat_timings = cache_mem.get('salat_timings')
					salat_invite = freshest_reply
					context["type_of_object"] = '4'
					context["notification"] = 1
					try:
						context["first_time_user"] = UserProfile.objects.get(id=freshest_reply['ooi']).streak
					except:
						context["first_time_user"] = 0
					context["banned"] = False
					context["parent"] = salat_invite
					context["namaz"] = salat_timings['namaz'] 
					context["freshest_unseen_comment"] = 1				
				elif is_photo:
					if object_type == '1':
						#i.e. it's a photo a fan ought to see!
						#photo = Photo.objects.get(id=freshest_reply)
						context["freshest_unseen_comment"] = None
						context["type_of_object"] = '1'
						context["notification"] = 1
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi']
						context["first_time_user"] = False
						context["banned"] = False
					elif object_type == '0':
						context["freshest_unseen_comment"] = freshest_reply
						context["type_of_object"] = '0'
						context["notification"] = 1
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi']#.which_photo_id
						# context["photostream_id"]=PhotoStream.objects.get(cover_id=context["parent_pk"]).id
						context["first_time_user"] = False
						context["banned"] = False
					else:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
						context["banned"] = False
					return context
				elif is_link:
					context["type_of_object"] = '2'
					context["banned"] = False
					if freshest_reply:
						# parent_link = freshest_reply.answer_to
						# parent_link_writer = parent_link.submitter
						parent_link_writer_username = freshest_reply['oon']#parent_link_writer.username
						WELCOME_MESSAGE1 = parent_link_writer_username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
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
						context["freshest_unseen_comment"] = freshest_reply
						context["notification"] = 1
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi']
						if user.username==parent_link_writer_username and any(freshest_reply['lrtx'] in s for s in WELCOME_MESSAGES):
							context["first_time_user"] = True
						else:
							context["first_time_user"] = False
					except:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
					return context
				else:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["banned"] = False
					context["first_time_user"] = False
					return context
			else:
				context["notification"] = 0
				context["banned"] = True
				context["can_vote"] = False
				context["first_time_user"] = False
				context["type_of_object"] = None
				context["freshest_unseen_comment"] = []
				context["parent"] = []
				context["parent_pk"] = 0
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
			target_id = self.request.session["target_photo_id"]
			self.request.session["target_photo_id"] = None
		except:
			target_id = None
		if target_id:
			try:
				index = list(photo.id for photo in self.object_list).index(int(target_id))
			except:
				index = None
			if 0 <= index <= 9:
				addendum = '#section'+str(index+1)
			elif 10 <= index <= 19:
				addendum = '?page=2#section'+str(index+1-10)
			elif 20 <= index <= 29:
				addendum = '?page=3#section'+str(index+1-20)
			elif 30 <= index <= 39:
				addendum = '?page=4#section'+str(index+1-30)
			elif 40 <= index <= 49:
				addendum = '?page=5#section'+str(index+1-40)
			elif 50 <= index <= 59:
				addendum = '?page=6#section'+str(index+1-50)
			elif 60 <= index <= 69:
				addendum = '?page=7#section'+str(index+1-60)
			elif 70 <= index <= 79:
				addendum = '?page=8#section'+str(index+1-70)
			elif 80 <= index <= 89:
				addendum = '?page=9#section'+str(index+1-80)
			elif 90 <= index <= 99:
				addendum = '?page=10#section'+str(index+1-90)
			elif 100 <= index <= 109:
				addendum = '?page=11#section'+str(index+1-100)
			elif 110 <= index <= 119:
				addendum = '?page=12#section'+str(index+1-110)
			elif 120 <= index <= 129:
				addendum = '?page=13#section'+str(index+1-120)
			elif 130 <= index <= 139:
				addendum = '?page=14#section'+str(index+1-130)
			elif 140 <= index <= 149:
				addendum = '?page=15#section'+str(index+1-140)
			elif 150 <= index <= 159:
				addendum = '?page=16#section'+str(index+1-150)
			elif 160 <= index <= 169:
				addendum = '?page=17#section'+str(index+1-160)
			elif 170 <= index <= 179:
				addendum = '?page=18#section'+str(index+1-170)
			elif 180 <= index <= 189:
				addendum = '?page=19#section'+str(index+1-180)
			elif 190 <= index <= 199:
				addendum = '?page=20#section'+str(index+1-190)
			else:
				addendum = '#section0'		
			return HttpResponseRedirect(addendum)
		else:
			return self.render_to_response(context)

def see_best_photo_pk(request,pk=None,*args,**kwargs):
	if pk.isdigit():
		request.session["target_best_photo_id"] = pk
		return redirect("see_best_photo")
	else:
		return redirect("home")

class BestPhotoView(ListView):
	model = Photo
	template_name = "best_photos.html"
	paginate_by = 10

	def get_queryset(self):
		# queryset = Photo.objects.select_related('owner__userprofile').filter(id__in=all_best_photos()).exclude(vote_score__lte=-1).order_by('-invisible_score')
		# return queryset
		cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 75,
		})
		queryset = cache_mem.get('best_photos')
		# for photo in queryset:
		# 	print photo.invisible_score
		return queryset

	def get_context_data(self, **kwargs):
		context = super(BestPhotoView, self).get_context_data(**kwargs)
		context["girls"] = FEMALES
		context["authenticated"] = False
		context["can_vote"] = False
		context["score"] = None
		if self.request.is_feature_phone:
			context["feature_phone"] = True
		else:
			context["feature_phone"] = False
		if self.request.user.is_authenticated():
			context["authenticated"] = True
			user = self.request.user
			context["ident"] = user.id
			context["score"] = user.userprofile.score
			context["voted"] = []
			if not self.request.user_banned:
				if user.userprofile.score > 9:
					context["can_vote"] = True
				else:
					context["can_vote"] = False
				# context["voted"] = [photo.id for photo in context["object_list"] if voted_for_photo(photo.id, user.username)]
				context["voted"] = voted_for_photo(context["object_list"],user.username)
				object_type, freshest_reply, is_link, is_photo, is_groupreply, is_salat = GetLatest(user)
				if not is_link and not is_photo and not is_groupreply and not is_salat:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
					return context
				elif not freshest_reply:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["first_time_user"] = False
					context["banned"] = False
					return context
				elif is_groupreply:
					if object_type == '1':
						# private mehfil
						context["type_of_object"] = '3a'
						context["notification"] = 1
						context["banned"] = False
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi'] #group id
					elif object_type == '0':
						# public mehfil
						context["type_of_object"] = '3b'
						context["notification"] = 1
						context["banned"] = False
						context["first_time_user"] = False
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi'] #group id
					else:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
						context["banned"] = False
				elif is_salat:
					# now = datetime.utcnow()+timedelta(hours=5)
					# current_minute = now.hour * 60 + now.minute
					# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
					cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
						'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
					})
					salat_timings = cache_mem.get('salat_timings')
					salat_invite = freshest_reply
					context["type_of_object"] = '4'
					context["notification"] = 1
					try:
						context["first_time_user"] = UserProfile.objects.get(id=freshest_reply['ooi']).streak
					except:
						context["first_time_user"] = 0
					context["banned"] = False
					context["parent"] = salat_invite
					context["namaz"] = salat_timings['namaz'] 
					context["freshest_unseen_comment"] = 1		
				elif is_photo:
					if object_type == '1':
						#i.e. it's a photo a fan ought to see!
						# photo = Photo.objects.get(id=freshest_reply)
						context["freshest_unseen_comment"] = None
						context["type_of_object"] = '1'
						context["notification"] = 1
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi']
						context["first_time_user"] = False
						context["banned"] = False
					elif object_type == '0':
						context["freshest_unseen_comment"] = freshest_reply
						context["type_of_object"] = '0'
						context["notification"] = 1
						context["parent"] = freshest_reply#.which_photo
						context["parent_pk"] = freshest_reply['oi']
						# print context["parent_pk"]
						context["first_time_user"] = False
						context["banned"] = False
					else:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
						context["banned"] = False
					return context
				elif is_link:
					context["type_of_object"] = '2'
					context["banned"] = False
					if freshest_reply:
						# parent_link = freshest_reply.answer_to
						# parent_link_writer = parent_link.submitter
						parent_link_writer_username = freshest_reply['oon']#parent_link_writer.username
						WELCOME_MESSAGE1 = parent_link_writer_username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
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
						context["freshest_unseen_comment"] = freshest_reply
						context["notification"] = 1
						context["parent"] = freshest_reply
						context["parent_pk"] = freshest_reply['oi']
						if user.username==parent_link_writer_username and any(freshest_reply['lrtx'] in s for s in WELCOME_MESSAGES):
							context["first_time_user"] = True
						else:
							context["first_time_user"] = False
					except:
						context["freshest_unseen_comment"] = []
						context["notification"] = 0
						context["parent"] = []
						context["parent_pk"] = 0
						context["first_time_user"] = False
					return context
				else:
					context["freshest_unseen_comment"] = []
					context["notification"] = 0
					context["parent"] = []
					context["parent_pk"] = 0
					context["banned"] = False
					context["first_time_user"] = False
					return context
			else:
				context["notification"] = 0
				context["banned"] = True
				context["can_vote"] = False
				context["first_time_user"] = False
				context["type_of_object"] = None
				context["freshest_unseen_comment"] = []
				context["parent"] = []
				context["parent_pk"] = 0
				return context
		return context

	def get(self, request, *args, **kwargs):
		self.object_list = self.get_queryset()
		allow_empty = self.get_allow_empty()
		if not allow_empty:
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
			target_id = self.request.session["target_best_photo_id"]
			self.request.session["target_best_photo_id"] = None
		except:
			target_id = None
		if target_id:
			try:
				index = list(photo.id for photo in self.object_list).index(int(target_id))
			except:
				index = None
			if 0 <= index <= 9:
				addendum = '#section'+str(index+1)
			elif 10 <= index <= 19:
				addendum = '?page=2#section'+str(index+1-10)
			elif 20 <= index <= 29:
				addendum = '?page=3#section'+str(index+1-20)
			elif 30 <= index <= 39:
				addendum = '?page=4#section'+str(index+1-30)
			elif 40 <= index <= 49:
				addendum = '?page=5#section'+str(index+1-40)
			elif 50 <= index <= 59:
				addendum = '?page=6#section'+str(index+1-50)
			elif 60 <= index <= 69:
				addendum = '?page=7#section'+str(index+1-60)
			elif 70 <= index <= 79:
				addendum = '?page=8#section'+str(index+1-70)
			elif 80 <= index <= 89:
				addendum = '?page=9#section'+str(index+1-80)
			elif 90 <= index <= 99:
				addendum = '?page=10#section'+str(index+1-90)
			elif 100 <= index <= 109:
				addendum = '?page=11#section'+str(index+1-100)
			elif 110 <= index <= 119:
				addendum = '?page=12#section'+str(index+1-110)
			elif 120 <= index <= 129:
				addendum = '?page=13#section'+str(index+1-120)
			elif 130 <= index <= 139:
				addendum = '?page=14#section'+str(index+1-130)
			elif 140 <= index <= 149:
				addendum = '?page=15#section'+str(index+1-140)
			elif 150 <= index <= 159:
				addendum = '?page=16#section'+str(index+1-150)
			elif 160 <= index <= 169:
				addendum = '?page=17#section'+str(index+1-160)
			elif 170 <= index <= 179:
				addendum = '?page=18#section'+str(index+1-170)
			elif 180 <= index <= 189:
				addendum = '?page=19#section'+str(index+1-180)
			elif 190 <= index <= 199:
				addendum = '?page=20#section'+str(index+1-190)
			else:
				addendum = '#section0'		
			return HttpResponseRedirect(addendum)
		else:
			return self.render_to_response(context)

def set_rank():
	epoch = datetime(1970, 1, 1).replace(tzinfo=None)
	netvotes = 0
	order = log(max(abs(netvotes), 1), 10) #0.041392685 for zero votes, log 1 = 0
	sign = 1 if netvotes > 0 else -1 if netvotes < 0 else 0
	unaware_submission = datetime.utcnow().replace(tzinfo=None)
	td = unaware_submission - epoch 
	epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
	secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
	invisible_score = round(sign * order + secs / 45000, 8)
	return invisible_score

class UploadVideoView(FormView):
	# model = Video
	form_class = UploadVideoForm
	template_name = "upload_video.html"

	def get_context_data(self, **kwargs):
		context = super(UploadVideoView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			videos = Video.objects.filter(id__in=get_recent_videos(self.request.user.id)).order_by('-id').values_list('vote_score', 'upload_time')
			number_of_videos = videos.count()
			forbidden, time_remaining = check_video_abuse(number_of_videos, videos)
			if forbidden:
				context["score"] = None
				context["forbidden"] = True
				context["time_remaining"] = time_remaining
			else:
				context["score"] = self.request.user.userprofile.score
				context["forbidden"] = False
				context["time_remaining"] = None
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			status, seconds_to_go = video_uploaded_too_soon(self.request.user.id)
			if status:
				m, s = divmod(seconds_to_go, 60)
				if m and s:
					context = {"time_remaining":"%s minutes and %s seconds" % (int(m), int(s))}
				elif s:
					context= {"time_remaining": "%s seconds" % int(s)}
				else:
					context= {"time_remaining": 0}
				return render(self.request,'video_uploaded_too_soon.html',context)
			else:
				videos = Video.objects.filter(id__in=get_recent_videos(self.request.user.id)).order_by('-id').values_list('vote_score', 'upload_time')
				forbidden, time_remaining = check_video_abuse(videos.count(), videos)
				if forbidden:
					context = {'time_remaining':time_remaining}
					return render(self.request,'forbidden_video.html',context)
				caption = self.request.POST.get("caption")
				video = self.request.FILES['video_file']
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
				video = Video.objects.create(owner=self.request.user, video_file=video, device=device, comment_count=0, caption=caption)
				video_upload_tasks.delay(video.video_file.name, video.id, self.request.user.id)
				context = {'pk':'pk'}
				return render(self.request,'video_upload.html',context)

class UploadPhotoView(CreateView):
	model = Photo
	form_class = UploadPhotoForm
	template_name = "upload_photo.html"

	def get_context_data(self, **kwargs):
		context = super(UploadPhotoView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			banned, time_remaining = check_photo_upload_ban(self.request.user.id)
			if banned:
				context["forbidden"] = True
				if time_remaining == '-1':
					to_go = time_remaining
				else:
					to_go = timezone.now()+timedelta(seconds=time_remaining)
				context["time_remaining"] = to_go
			else:
				photos = Photo.objects.filter(id__in=get_recent_photos(self.request.user.id)).order_by('-id').values_list('vote_score','upload_time','visible_score')
				number_of_photos = photos.count()
				forbidden, time_remaining = check_photo_abuse(number_of_photos, photos)
				if forbidden:
					context["forbidden"] = forbidden
					context["time_remaining"] = time_remaining
				else:
					post_big_photo_in_home = True
					if number_of_photos < 5: #must at least have posted 5 photos to have photo appear BIG in home
						post_big_photo_in_home = False
					else:
						for photo in photos:
							if photo[0] < 0: #can't post BIG photo in home if even 1 previous photo had negative score
								post_big_photo_in_home = False
					total_visible_score = sum(photo[2] for photo in photos)
					now = timezone.now()
					hotuser = HotUser.objects.filter(which_user=self.request.user).update(hot_score=total_visible_score, updated_at=now, allowed=post_big_photo_in_home)
					if hotuser:
						pass
					else:
						HotUser.objects.create(which_user=self.request.user, hot_score=total_visible_score, updated_at=now, allowed=post_big_photo_in_home)
					context["score"] = self.request.user.userprofile.score
					return context
				return context
			return context
		return context

	def form_valid(self, form):
		f = form.save(commit=False)
		user = self.request.user
		if user.userprofile.score < 3:#
			context = {'score': '3'}
			return render(self.request, 'score_photo.html', context)
		else:
			banned, time_remaining = check_photo_upload_ban(self.request.user.id)
			if banned:
				if time_remaining == '-1':
					to_go = time_remaining
				else:
					to_go = timezone.now()+timedelta(seconds=time_remaining)
				context={'time_remaining': to_go}
				return render(self.request, 'forbidden_photo.html', context)
			else:
				number_of_photos = 0
				photos = []
				total_score = 0
				photo_ids = get_recent_photos(self.request.user.id)
				photos_qs = Photo.objects.filter(id__in=photo_ids).order_by('-id').annotate(unique_comment_count=Count('photocomment__submitted_by', distinct=True))
				for photo in photos_qs:
					# print photo.vote_score
					total_score += ((VOTE_WEIGHT*photo.vote_score) + photo.unique_comment_count)
					photos.append((photo.vote_score, photo.upload_time, photo.visible_score)) #list of dictionaries
					number_of_photos += 1
				# print total_score
				forbidden, time_remaining = check_photo_abuse(number_of_photos, photos)
				if forbidden:
					context={'time_remaining': time_remaining}
					return render(self.request, 'forbidden_photo.html', context)
			time_now = timezone.now()
			try:
				difference = time_now - photos[0][1]
				seconds = difference.total_seconds()
				if seconds < 60:
					context = {'time': round((60 - seconds),0)}
					return render(self.request, 'error_photo.html', context)
			except:
				pass
			if f.image_file:
				try:
					on_fbs = self.request.META.get('X-IORG-FBS')
				except:
					on_fbs = False
				if on_fbs:
					if f.image_file.size > 200000:
						context = {'pk':'pk'}
						return render(self.request,'big_photo_fbs.html',context)
					else:
						pass
				else:
					if f.image_file.size > 10000000:
						context = {'pk':'pk'}
						return render(self.request,'big_photo_regular.html',context)
					else:
						pass
				image_file, avghash, pk = clean_image_file_with_hash(f.image_file)#, recent_hashes)
				if isinstance(pk,float):
					try:
						photo = Photo.objects.get(id=int(pk))
						context = {'photo': photo, 'females': FEMALES}
						return render(self.request, 'duplicate_photo.html', context)
					except:
						f.image_file = None
				else:
					if image_file:
						f.image_file = image_file
					else:
						f.image_file = None
			else:
				f.image_file = None
			if f.image_file:
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
				invisible_score = set_rank()
				photo = Photo.objects.create(image_file = f.image_file, owner=user, caption=f.caption, comment_count=0, \
					device=device, avg_hash=avghash, invisible_score=invisible_score)
				photo_id = photo.id
				user_id = user.id
				time = photo.upload_time
				epochtime = convert_to_epoch(time)
				timestring = time.isoformat()
				if self.request.user_banned:
					banned = '1'
				else:
					banned = '0'
				photo_upload_tasks.delay(banned, user_id,photo_id, timestring, device)
				insert_hash(photo_id, photo.avg_hash) #perceptual hash of the photo
				add_photo(photo_id) #adding in photo feed
				save_recent_photo(user_id, photo_id) #saving 5 recent ones
				try:
					owner_url = user.userprofile.avatar.url
				except:
					owner_url = None
				name = user.username
				create_object(object_id=photo_id, object_type='0', object_owner_avurl=owner_url,object_owner_id=user_id,\
					object_owner_name=name,object_desc=f.caption,photourl=photo.image_file.url,vote_score=0,res_count=0)
				# create_notification(viewer_id=user_id, object_id=photo_id, object_type='0',seen=True,updated_at=epochtime,\
				# 	unseen_activity=True)
				if number_of_photos:
					set_uploader_score(user_id, ((total_score*1.0)/number_of_photos)) #only from last 5 photos!
				bulk_create_notifications.delay(user_id, photo_id, epochtime,photo.image_file.url, name, f.caption)
				return redirect("see_photo")
			else:
				context = {'photo': 'photo'}
				return render(self.request, 'big_photo.html', context)

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

	# def get_success_url(self): #which URL to go back once settings are saved?
	# 	try: 
	# 		on_fbs = self.request.META.get('X-IORG-FBS')
	# 	except:
	# 		on_fbs = False
	# 	if on_fbs:
	# 		return 
	# 		return redirect("home")#, pk= reply.answer_to.id)

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
				
class PhotoShareView(FormView):
	form_class = PhotoShareForm
	template_name = "photo_share_help.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoShareView, self).get_context_data(**kwargs)
		try:
			loc = self.kwargs["loc"]
			context["loc"] = loc
			if loc == '3':
				username = self.kwargs["slug"]
				context["username"] = username
			else:
				username = None
		except:
			loc = '0'
			context["loc"] = loc
			username = None
		try:
			context["no_id"] = False
			pk = self.kwargs["pk"]
			context["ident"] = pk
			context["freebasics_url"] = "https://https-damadam-pk.0.freebasics.com/photo_detail/"+str(pk)
			context["regular_url"] = "https://damadam.pk/photo_detail/"+str(pk)
		except:
			context["no_id"] = True
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
				#time_now = datetime.utcnow().replace(tzinfo=utc)
				time_now = timezone.now()
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
				#time_now = datetime.utcnow().replace(tzinfo=utc)
				time_now = timezone.now()
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
				#time_now = datetime.utcnow().replace(tzinfo=utc)
				time_now = timezone.now
				context = {'sender':sender, 'refresh_now':True, 'exists':1, 'pic':pic, 'max_time':0,'caption':caption,}
			else:
				#set the seen flag of the message object
				message.seen = True
				#viewing_time = datetime.utcnow().replace(tzinfo=utc)
				viewing_time = timezone.now()
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
			unique = self.request.session["public_uuid"]
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
			unique = self.request.session["public_uuid"]
			group = Group.objects.get(unique=unique)
			if group.private == '0' and group.owner != user:
				return redirect("score_help")
			group.rules = rules
			group.save()
			Reply.objects.create(text=rules ,which_group=group ,writer=user ,category='5')
			return redirect("public_group", slug=unique)

class ChangeOutsideGroupTopicView(CreateView):
	model = Group
	form_class = ChangeOutsideGroupTopicForm
	template_name = "change_outside_group_topic.html"

	def get_context_data(self, **kwargs):
		context = super(ChangeOutsideGroupTopicView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			unique = self.request.session["unique_outsider"]
			if unique:	
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
				if group.private == '0' or group.private == '1':
					context["unauthorized"] = True
					context["group"] = None
					return context
			else:
				context["unauthorized"] = True
				context["group"] = None
				return context
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		user = self.request.user
		if self.request.user_banned:
			return redirect("profile", slug=user.username)
		else:
			topic = self.request.POST.get("topic")
			unique = self.request.session["unique_outsider"]
			group = Group.objects.get(unique=unique)
			group.topic = topic
			group.save()
			Reply.objects.create(text=topic ,which_group=group , writer=user, category='4')
			return redirect("outsider_group", slug=unique)

class ChangePrivateGroupTopicView(CreateView):
	model = Group
	form_class = ChangePrivateGroupTopicForm
	template_name = "change_private_group_topic.html"

	def get_context_data(self, **kwargs):
		context = super(ChangePrivateGroupTopicView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			banned, ban_type, time_remaining, warned = private_group_posting_allowed(self.request.user.id)
			unique = self.request.session["unique_id"]
			if unique and not banned:	
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
				if group.private == '0' or group.private == '2':
					context["unauthorized"] = True
					context["group"] = None
					return context
			else:
				context["unauthorized"] = True
				context["group"] = None
				return context
		return context

	def form_valid(self, form):
		user = self.request.user
		if self.request.user_banned:
			return redirect("profile", slug=user.username)
		else:
			topic = self.request.POST.get("topic")
			unique = self.request.session["unique_id"]
			group = Group.objects.get(unique=unique)
			if (group.private == '0' or group.private == '2') and group.owner != user:
				return redirect("score_help")
			group.topic = topic
			group.save()
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
			Reply.objects.create(text=topic ,which_group=group , writer=user, category='4', device=device)
			return redirect("private_group", slug=unique)

class ChangeGroupTopicView(CreateView):
	model = Group
	form_class = ChangeGroupTopicForm
	template_name = "change_group_topic.html"

	def get_context_data(self, **kwargs):
		context = super(ChangeGroupTopicView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			unique = self.request.session["public_uuid"]
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
			unique = self.request.session['public_uuid']
			group = Group.objects.get(unique=unique)
			if group.private == '0' and group.owner != user:
				return redirect("score_help")
			group.topic = topic
			group.save()
			Reply.objects.create(text=topic ,which_group=group , writer=user, category='4')
			return redirect("public_group", slug=unique)

@ratelimit(rate='2/s')
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

@ratelimit(rate='2/s')
def public_group(request, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		if request.user.is_authenticated():
			deduction = 2 * -2
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'unique': slug}
			return render(request, 'penalty_public.html', context)
		else:
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
			if 'awami' in self.request.path and group.private == '0': 
				group_id = group.id
				context["switching"] = False
				context["group"] = group
				if GroupBanList.objects.filter(which_user_id=self.request.user.id,which_group_id=group_id).exists():
					context["group_banned"]=True
					return context#no need to process more
				if random.random() < 0.5:
					#calling this only 50% of the times, as a server optimization of sorts (also incr priority from 0.14 to 0.25 to compensate)
					public_group_vote_tasks.delay(group_id=group_id,priority=0.25)
				public_group_attendance_tasks.delay(group_id=group_id, user_id=self.request.user.id)
				context["ensured"] = FEMALES
				replies = Reply.objects.select_related('writer__userprofile').filter(which_group_id=group_id).exclude(category='1').order_by('-submitted_on')[:25]#get DB call
				#time_now = datetime.utcnow().replace(tzinfo=utc)
				time_now = timezone.now()
				updated_at = convert_to_epoch(time_now)
				writers_with_times = [(reply,reply.writer,(time_now-reply.submitted_on).total_seconds()) for reply in replies]
				most_recent = {}
				for reply,user,time in writers_with_times:
					most_recent[user] = min(most_recent.get(user,time),time)
				replies_writers_times = [(reply,user,most_recent[user]) for reply,user, _ in writers_with_times]
				context["replies"] = replies_writers_times
				context["unseen"] = False
				if not self.request.user_banned:#do the following ONLY if user isn't hell-banned
					members = get_group_members(group_id)
					if self.request.user.username in members and context["replies"]:
						update_notification(viewer_id=self.request.user.id, object_id=group_id, object_type='3', seen=True, \
							updated_at=updated_at, single_notif=False, unseen_activity=True, priority='public_mehfil', \
							bump_ua=False) #just seeing means notification is updated, but not bumped up in ua:
			else:
				context["switching"] = True
				context["group_banned"] = False
		return context

	def form_valid(self, form): #this processes the public form before it gets saved to the database
		try:
			pk = self.request.session["public_uuid"]
			which_group = Group.objects.get(unique=pk)#
		except:
			return redirect("profile", self.request.user.username )
		if self.request.user_banned or \
		GroupBanList.objects.filter(which_user_id=self.request.user.id, which_group_id=which_group.id).exists():#
			return redirect("group_page")
		else:
			if self.request.user.userprofile.score < -25:#
				HellBanList.objects.create(condemned=self.request.user)
				self.request.user.userprofile.score = random.randint(10,71)
				self.request.user.userprofile.save()
				return redirect("group_page")
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			text = f.text
			score = fuzz.ratio(text, self.request.user.userprofile.previous_retort)
			if score > 87:
				UserProfile.objects.filter(user=self.request.user).update(score=F('score')-5)
				self.request.session["public_uuid"] = None
				return redirect("public_group", slug=pk)
			else:
				UserProfile.objects.filter(user=self.request.user).update(previous_retort=text, score=F('score')+2)
				if f.image:
					try:
						on_fbs = self.request.META.get('X-IORG-FBS')
					except:
						on_fbs = False
					if on_fbs:
						if f.image.size > 200000:
							context = {'pk':'pk'}
							return render(self.request,'big_photo_fbs.html',context)
						else:
							pass
					else:
						if f.image.size > 10000000:
							context = {'pk':'pk'}
							return render(self.request,'big_photo_regular.html',context)
						else:
							pass
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
				which_group_id = which_group.id
				reply = Reply.objects.create(writer=self.request.user, which_group=which_group, text=text, image=f.image, device=device)#
				add_group_member(which_group_id, self.request.user.username)
				remove_group_invite(self.request.user.id, which_group_id)
				add_user_group(self.request.user.id, which_group_id)
				reply_time = convert_to_epoch(reply.submitted_on)
				try:
					url=self.request.user.userprofile.avatar.url
				except:
					url=None
				try:
					image_url = reply.image.url
				except:
					image_url = None
				if random.random() < 0.5:
					#calling this only 50% of the times, as a server optimization of sorts (also incr priority from 1 to 2 to compensate)
					public_group_vote_tasks.delay(group_id=which_group_id,priority=2)
				public_group_attendance_tasks.delay(group_id=which_group_id, user_id=self.request.user.id)
				group_notification_tasks.delay(group_id=which_group_id,sender_id=self.request.user.id,\
					group_owner_id=which_group.owner.id,topic=which_group.topic,reply_time=reply_time,poster_url=url,\
					poster_username=self.request.user.username,reply_text=text,priv=which_group.private,slug=which_group.unique,\
					image_url=image_url,priority='public_mehfil',from_unseen=False)
				self.request.session["public_uuid"] = None
				return redirect("public_group", slug=pk)

@ratelimit(rate='2/s')
def first_time_public_refresh(request, unique=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		if request.user.is_authenticated():
			deduction = 1 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'unique': unique}
			return render(request, 'public_mehfil_refresh_penalty.html', context)
		else:
			context = {'unique': 'none'}
			return render(request, 'public_mehfil_refresh_penalty.html', context)
	else:
		if first_time_refresher(request.user.id):
			add_refresher(request.user.id)
			context = {'unique': unique}
			return render(request, 'public_mehfil_refresh.html', context)
		else:
			return redirect("public_group", unique)

@ratelimit(rate='2/s')
def first_time_refresh(request, unique=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		if request.user.is_authenticated():
			deduction = 1 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'unique': unique}
			return render(request, 'mehfil_refresh_penalty.html', context)
		else:
			context = {'unique': 'none'}
			return render(request, 'mehfil_refresh_penalty.html', context)
	else:
		if first_time_refresher(request.user.id):
			add_refresher(request.user.id)
			context = {'unique': unique}
			return render(request, 'mehfil_refresh.html', context)
		else:
			return redirect("private_group", unique)

@ratelimit(rate='2/s')
def private_group(request, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		if request.user.is_authenticated():
			deduction = 1 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'unique': slug}
			return render(request, 'penalty.html', context)
		else:
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
			try:
				group = Group.objects.get(unique=unique)#get DB call
			except:
				context["switching"] = True
				return context
			context["group"] = group
			if 'private' in self.request.path and group.private=='1':
				banned, ban_type, time_remaining, warned = private_group_posting_allowed(self.request.user.id)			
				context["banned"] = banned
				context["ban_type"] = ban_type
				context["warned"] = warned
				if banned:
					m, s = divmod(time_remaining, 60)
					h, m = divmod(m, 60)
					d, h = divmod(h, 24)
					if d and h and m:
						context["time_remaining"] = "%s days, %s hours and %s minutes" % (int(d), int(h), int(m))
					elif h and m:
						context["time_remaining"] = "%s hours and %s minutes" % (int(h), int(m))
					elif m and s:
						context["time_remaining"] = "%s minutes and %s seconds" % (int(m), int(s))
					elif s:
						context["time_remaining"] = "%s seconds" % int(s)
					else:
						context["time_remaining"] = None
				else:
					context["time_remaining"] = None
				try:
					context["on_fbs"] = self.request.META.get('X-IORG-FBS')
				except:
					context["on_fbs"] = False
				context["switching"] = False
				context["ensured"] = FEMALES
				replies = Reply.objects.select_related('writer__userprofile').filter(which_group=group).order_by('-submitted_on')[:25]
				time_now = timezone.now()
				updated_at = convert_to_epoch(time_now)
				save_user_presence(self.request.user.id,group.id,updated_at)
				pres_dict = get_latest_presence(group.id,set(reply.writer_id for reply in replies))
				context["replies"] = [(reply,reply.writer,pres_dict[reply.writer_id]) for reply in replies]
				context["unseen"] = False
				if not self.request.user_banned:#do the following ONLY if user isn't hell-banned
					members = get_group_members(group.id)
					context["members"] = members #contains members' usernames
					if members and replies and self.request.user.username in members:
						# flip "unseen" notification here
						context["unseen"] = True #i.e. the user is a member and replies exist; the prospect of unseen replies exists
						update_notification(viewer_id=self.request.user.id, object_id=group.id, object_type='3', seen=True, \
							updated_at=updated_at, single_notif=False, unseen_activity=True, priority='priv_mehfil',
							bump_ua=False) #just seeing means notification is updated, but not bumped up in ua:
						try:
							#finding latest time user herself replied
							context["reply_time"] = max(reply.submitted_on for reply in replies if reply.writer == self.request.user)
						except:
							context["reply_time"] = None #i.e. it's the first reply in the last 25 replies (i.e. all were unseen)
					else:
						context["reply_time"] = None
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
			banned, ban_type, time_remaining, warned = private_group_posting_allowed(self.request.user.id)
			if banned:
				return redirect("group_page")
			else:
				f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
				text = f.text #text of the reply
				score = fuzz.ratio(text, self.request.user.userprofile.previous_retort)
				if score > 90:
					return redirect("private_group", self.request.session['unique_id'])#, pk= reply.answer_to.id)
				else:
					self.request.user.userprofile.previous_retort = text
					self.request.user.userprofile.score = self.request.user.userprofile.score + 1
					self.request.user.userprofile.save()
					if f.image:
						try:
							on_fbs = self.request.META.get('X-IORG-FBS')
						except:
							on_fbs = False
						if on_fbs:
							if f.image.size > 200000:
								context = {'pk':'pk'}
								return render(self.request,'big_photo_fbs.html',context)
							else:
								pass
						else:
							if f.image.size > 10000000:
								context = {'pk':'pk'}
								return render(self.request,'big_photo_regular.html',context)
							else:
								pass
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
					which_group_id = which_group.id
					reply = Reply.objects.create(writer=self.request.user, which_group=which_group, text=text, image=f.image, \
						device=device)
					add_group_member(which_group_id, self.request.user.username)
					remove_group_invite(self.request.user.id, which_group_id)
					add_user_group(self.request.user.id, which_group_id)
					reply_time = convert_to_epoch(reply.submitted_on)
					try:
						url=self.request.user.userprofile.avatar.url
					except:
						url=None
					try:
						image_url = reply.image.url
					except:
						image_url = None
					group_notification_tasks.delay(group_id=which_group_id,sender_id=self.request.user.id,\
						group_owner_id=which_group.owner.id,topic=which_group.topic,reply_time=reply_time,poster_url=url,\
						poster_username=self.request.user.username,reply_text=text,priv=which_group.private,\
						slug=which_group.unique,image_url=image_url,priority='priv_mehfil',from_unseen=False)
					self.request.session['unique_id'] = None
					return redirect("private_group", reply.which_group.unique)
	
@ratelimit(rate='2/s')
def welcome_pk(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		if request.user.is_authenticated():
			deduction = 1 * -10
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'unique': pk}
			return render(request, 'penalty_welcome.html', context)
		else:
			context = {'unique': pk}
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
			try:
				target_user = User.objects.get(id=self.request.session["welcome_pk"])
				context["authenticated"] = True
				context["target_user"] = target_user
			except:
				context["authenticated"] = False
				context["target_user"] = []
		return context

class WelcomeMessageView(CreateView):
	model = Publicreply
	form_class = WelcomeMessageForm
	template_name = "welcome_message.html"

	def get_context_data(self, **kwargs):
		context = super(WelcomeMessageView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				pk = self.request.session["welcome_pk"]
				context["target_user"] = User.objects.get(id=pk)
				context["authorized"] = True
				context["option"] = self.kwargs["option"]
			except:
				context["authorized"] = False
				context["target_user"] = None
				context["option"] = None
		return context

def mehfilcomment_pk(request, pk=None, num=None, origin=None, slug=None, *args, **kwargs):
	if pk.isdigit() and num.isdigit():
		request.session['mehfilcomment_pk'] = pk
		request.session['mehfilphoto_pk'] = num
		if origin:
			request.session['mehfilfrom_photos'] = origin
		else:
			request.session['mehfilfrom_photos'] = None
		if slug:
			request.session['mehfil_slug'] = slug
		else:
			request.session['mehfil_slug'] = None
		return redirect("mehfilcomment_help")
	else:
		return redirect("score_help")

class MehfilCommentView(FormView):
	form_class = MehfilCommentForm
	template_name = "mehfilcomment_help.html"

	def get_context_data(self, **kwargs):
		context = super(MehfilCommentView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				target_id = self.request.session['mehfilcomment_pk']
				photo_id = self.request.session['mehfilphoto_pk']
				origin = self.request.session['mehfilfrom_photos']
				slug = self.request.session['mehfil_slug']
				context["target"] = User.objects.get(id=target_id)
				context["photo_id"] = photo_id
				context["origin"] = origin
			except:
				context["target"] = None
				context["photo_id"] = None
				context["origin"] = None
				return context
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			user = self.request.user
			report = self.request.POST.get("decision")
			target_id = self.request.session['mehfilcomment_pk']
			photo_id = self.request.session['mehfilphoto_pk']
			origin = self.request.session['mehfilfrom_photos']
			slug = self.request.session['mehfil_slug']
			self.request.session['mehfilcomment_pk'] = None
			self.request.session['mehfilphoto_pk'] = None
			self.request.session['mehfilfrom_photos'] = None
			if report == 'Haan':
				if user.userprofile.score < 500:
					if photo_id is not None and origin is not None:
						context = {'pk': photo_id, 'origin':origin}
						return render(self.request, 'penalty_mehfil.html', context)
					else:
						return redirect("closed_group_help")
				else:
					target = User.objects.get(id=target_id)
					invitee = target.username
					topic = invitee+" se gupshup"
					unique = uuid.uuid4()
					try:
						group = Group.objects.create(topic=topic, rules='', owner=user, private='1', unique=unique)
						UserProfile.objects.filter(user=self.request.user).update(score=F('score')-500)
						reply_list = []
						seen_list = []
						reply = Reply.objects.create(text=invitee, category='1', which_group_id=group.id, writer=user)
						add_group_member(group.id, user.username)
						add_group_invite(target_id, group.id,reply.id)
						add_user_group(user.id, group.id)
						return redirect("private_group", slug=unique)
					except:
						if photo_id is not None:
							redirect("comment_pk", pk=photo_id)
						else:
							return redirect("profile",slug=self.request.user.username)
			else:
				if slug:
					return redirect("comment_pk", pk=photo_id, origin=origin, ident=slug)
				else:
					return redirect("comment_pk", pk=photo_id, origin=origin)

@ratelimit(rate='2/s')
def unseen_group(request, pk=None, *args, **kwargs):
	was_limited = getattr(request,'limits',False)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'username':request.user.username}
		return render(request,'penalty_unseengroupreply.html',context)
	else:
		if request.method == 'POST':
			form = UnseenActivityForm(request.POST)
			if form.is_valid():
				description = request.POST.get("group_reply")
				if request.is_feature_phone:
					device = '1'
				elif request.is_phone:
					device = '2'
				elif request.is_tablet:
					device = '4'
				elif request.is_mobile:
					device = '5'
				else:
					device = '3'
				groupreply = Reply.objects.create(writer=request.user, which_group_id=pk, text=description,device=device)#,image='')
				reply_time = convert_to_epoch(groupreply.submitted_on)
				try:
					url = request.user.userprofile.avatar.url
				except:
					url = None
				try:
					image_url = groupreply.image.url
				except:
					image_url = None
				grp = Group.objects.get(id=pk)
				if grp.private == '1':
					priority='priv_mehfil'
				else:
					priority='public_mehfil'
				group_notification_tasks.delay(group_id=pk,sender_id=request.user.id,\
					group_owner_id=grp.owner.id,topic=grp.topic,reply_time=reply_time,poster_url=url,\
					poster_username=request.user.username,reply_text=description,priv=grp.private,\
					slug=grp.unique,image_url=image_url,priority=priority,from_unseen=True)
				return redirect("unseen_activity", request.user.username)
			else:
				return redirect("unseen_activity", request.user.username)
		else:
			return redirect("score_help")

#called when replying from unseen_activity
@ratelimit(rate='2/s')
def unseen_comment(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': 'pk'}
			return render(request, 'penalty_commentpk.html', context)
		except:
			context = {'pk': '10'}
			return render(request, 'penalty_commentpk.html', context)
	else:
		if request.method == 'POST':
			form = UnseenActivityForm(request.POST)
			if form.is_valid():
				description = request.POST.get("comment")
				if request.is_feature_phone:
					device = '1'
				elif request.is_phone:
					device = '2'
				elif request.is_tablet:
					device = '4'
				elif request.is_mobile:
					device = '5'
				else:
					device = '3'
				photocomment = PhotoComment.objects.create(submitted_by=request.user, which_photo_id=pk, text=description,device=device)
				# Photo.objects.filter(id=pk).update(comment_count=F('comment_count')+1)
				update_cc_in_home_photo(pk)
				photo = Photo.objects.get(id=pk)
				exists = PhotoComment.objects.filter(which_photo=photo, submitted_by=request.user).exists() #i.e. user commented before
				comment_time = convert_to_epoch(photocomment.submitted_on)
				try:
					url = request.user.userprofile.avatar.url
				except:
					url = None
				unseen_comment_tasks.delay(request.user.id, pk, comment_time, photocomment.id, photo.comment_count, description, exists, \
					request.user.username, url)
				return redirect("unseen_activity", request.user.username)
			else:
				return redirect("unseen_activity", request.user.username)
		else:
			return redirect("score_help")	

def unseen_activity(request, slug=None, *args, **kwargs):
	if first_time_inbox_visitor(request.user.id):
		add_inbox(request.user.id)
		context={'username':request.user.username}
		return render(request, 'inbox_tutorial.html', context)
	else:
		form = UnseenActivityForm()
		oblist = retrieve_unseen_activity(request.user.id) # this is a list of dictionaries
		last_visit_time = float(prev_unseen_activity_visit(request.user.id))-SEEN[False]
		paginator = Paginator(oblist, 20) #give it a list of objects and number of objects to show per page, it does the rest
		page = request.GET.get('page', '1')
		try:
			page = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			page = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			page = paginator.page(paginator.num_pages)
		context = {'object_list': oblist, 'verify':FEMALES, 'form':form, 'page':page,'nickname':request.user.username,\
		'last_visit_time':last_visit_time}
		return render(request, 'user_unseen_activity.html', context)

def unseen_help(request,*args,**kwargs):
	context={'nickname':request.user.username}
	return render(request,'photo_for_fans_help.html',context)

def top_photo_help(request,*args,**kwargs):
	context={'rank':None}
	return render(request,'top_photo_help.html',context)

def unseen_fans(request,pk=None,*args, **kwargs):
	if request.method == 'POST':
		form = UnseenActivityForm(request.POST)
		if form.is_valid():
			photo_url = request.POST.get("photo_url")
			fan_num = request.POST.get("fan_num")
			fan_list = request.POST.get("fan_list")
			fan_list = fan_list[1:-1] #removing '[' and ']' from the result
			fan_list = fan_list.split(", ") #tokenzing values from remaining string
			fan_list = User.objects.select_related('userprofile').filter(id__in=fan_list)
			context={'fan_list':fan_list,'photo_url':photo_url,'fan_num':fan_num,'nickname':request.user.username}
			return render(request,'which_fans.html',context)
	else:
		return redirect("unseen_activity",request.user.username)

#called when replying from unseen_activity
@ratelimit(rate='2/s')
def unseen_reply(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		if request.user.is_authenticated():
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': pk}
			return render(request, 'penalty_publicreply.html', context)
		else:
			context = {'pk': pk}
			return render(request, 'penalty_publicreply.html', context)
	else:
		if request.method == 'POST':
			form = UnseenActivityForm(request.POST)
			if form.is_valid():
				description = request.POST.get("comment")
				if request.is_feature_phone:
					device = '1'
				elif request.is_phone:
					device = '2'
				elif request.is_tablet:
					device = '4'
				elif request.is_mobile:
					device = '5'
				else:
					device = '3'
				parent = Link.objects.select_related('submitter__userprofile').get(id=pk)
				reply = Publicreply.objects.create(description=description, answer_to=parent, submitted_by=request.user, device=device)
				reply_time = convert_to_epoch(reply.submitted_on)
				amnt = update_cc_in_home_link(parent.id)
				try:
					url = request.user.userprofile.avatar.url
				except:
					url = None
				try:
					owner_url = parent.submitter.userprofile.avatar.url
				except:
					owner_url = None
				publicreply_tasks.delay(request.user.id, reply.id, pk, description)
				publicreply_notification_tasks.delay(link_id=pk,link_submitter_url=owner_url,sender_id=request.user.id,\
					link_submitter_id=parent.submitter_id,link_submitter_username=parent.submitter.username,\
					link_desc=parent.description,reply_time=reply_time,reply_poster_url=url,\
					reply_poster_username=request.user.username,reply_desc=description,is_welc=False,reply_count=amnt,\
					priority='home_jawab',from_unseen=True)
				return redirect("unseen_activity", request.user.username)
			else:
				return redirect("score_help")				
		else:
			return redirect("score_help")

@ratelimit(rate='2/s')
def reply_pk(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		if request.user.is_authenticated():
			deduction = 3 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'pk': pk}
			return render(request, 'penalty_publicreply.html', context)
		else:
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
		if self.request.is_feature_phone:
			context["feature_phone"] = True
		else:
			context["feature_phone"] = False
		if self.request.user.is_authenticated():
			banned, time_remaining, warned = publicreply_allowed(self.request.user.id)			
			context["banned"] = banned
			context["warned"] = warned
			if banned:
				m, s = divmod(time_remaining, 60)
				h, m = divmod(m, 60)
				d, h = divmod(h, 24)
				if d and h and m:
					context["time_remaining"] = "%s days, %s hours and %s minutes" % (int(d), int(h), int(m))
				elif h and m:
					context["time_remaining"] = "%s hours and %s minutes" % (int(h), int(m))
				elif m and s:
					context["time_remaining"] = "%s minutes and %s seconds" % (int(m), int(s))
				elif s:
					context["time_remaining"] = "%s seconds" % int(s)
				else:
					context["time_remaining"] = None
				# return context
			else:
				context["time_remaining"] = None
			context["authenticated"] = True
			score = self.request.user.userprofile.score
			context["score"] = score
			try:
				link = Link.objects.select_related('submitter__userprofile').get(id=self.request.session["link_pk"])
			except:
				context["error"] = True
				return context
			#is_notification = self.kwargs["is_notif"]
			context["error"] = False
			context["parent"] = link #the parent link
			context["ensured"] = FEMALES
			context["random"] = random.sample(xrange(1,188),15) #select 15 random emoticons out of 188
			#replies = Publicreply.objects.select_related('submitted_by__userprofile','answer_to').filter(id__in=get_publicreplies(self.request.session["link_pk"])).order_by('-id')
			replies = Publicreply.objects.select_related('submitted_by__userprofile','answer_to').filter(answer_to=link).order_by('-id')[:25]
			context["replies"] = replies
			if self.request.user_banned:
				context["unseen"] = False
				context["reply_time"] = None
			elif replies:
				updated = update_notification(viewer_id=self.request.user.id, object_id=link.id, object_type='2', seen=True, \
					updated_at=time.time(), single_notif=False, unseen_activity=True,priority='home_jawab',bump_ua=False)
				if updated:
					context["unseen"] = True
					try:
						context["reply_time"] = max(reply.submitted_on for reply in replies if reply.submitted_by == self.request.user)
					except:
						context["reply_time"] = None
				else:
					context["unseen"] = False
					context["reply_time"] = None
			else:
				context["unseen"] = False
				context["reply_time"] = None
			return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		pk = self.request.session["link_pk"]
		self.request.session["link_pk"] = None
		banned, time_remaining, warned = publicreply_allowed(self.request.user.id)
		if banned:
			return redirect("reply_pk", pk=pk)
		else:
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			description = self.request.POST.get("description")
			try:
				answer_to = Link.objects.select_related('submitter__userprofile').get(id=pk)
			except:
				UserProfile.objects.filter(user=self.request.user).update(score=F('score')-2)
				return redirect("profile", slug=self.request.user.username)
			score = fuzz.ratio(description, self.request.user.userprofile.previous_retort)
			if score > 85:
				try:
					return redirect("reply_pk", pk=pk)#, pk= reply.answer_to.id)
				except:
					UserProfile.objects.filter(user=self.request.user).update(score=F('score')-2)
					return redirect("profile", slug=self.request.user.username)
			else:
				if self.request.user_banned:
					return redirect("see_photo")
				else:
					user = self.request.user
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
					reply= Publicreply.objects.create(submitted_by=user, answer_to=answer_to, description=description, category='1', device=device)
					reply_time = convert_to_epoch(reply.submitted_on)
					amnt = update_cc_in_home_link(pk) #updating comment count for home link
					try:
						url = user.userprofile.avatar.url
					except:
						url = None
					try:
						owner_url = answer_to.submitter.userprofile.avatar.url
					except:
						owner_url = None
					publicreply_tasks.delay(user.id, reply.id, pk, description)
					publicreply_notification_tasks.delay(link_id=pk,link_submitter_url=owner_url,sender_id=user.id,\
						link_submitter_id=answer_to.submitter_id,link_submitter_username=answer_to.submitter.username,\
						link_desc=answer_to.description,reply_time=reply_time,reply_poster_url=url,\
						reply_poster_username=user.username,reply_desc=description,is_welc=False,\
						reply_count=answer_to.reply_count,priority='home_jawab',from_unseen=False)
					try:
						return redirect("reply_pk", pk=pk)
					except:
						UserProfile.objects.filter(user=user).update(score=F('score')-2)
						return redirect("profile", slug=user.username)

class UserActivityView(ListView):
	model = Link
	slug_field = "username"
	template_name = "user_activity.html"
	paginate_by = 15

	def get_queryset(self):
		username = self.kwargs['slug']
		user = User.objects.get(username=username)
		return Link.objects.select_related('submitter__userprofile').filter(submitter=user).order_by('-id')[:30]# instead of Link.with_votes.filter

	def get_context_data(self, **kwargs):
		context = super(UserActivityView, self).get_context_data(**kwargs)
		context["can_vote"] = False
		if self.request.user.is_authenticated():
			if self.request.user_banned and (self.request.user.username ==  self.kwargs['slug']):
				return redirect("score_help")
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

@ratelimit(rate='2/s')
def link_create_pk(request, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		try:
			deduction = 2 * -1
			request.user.userprofile.score = request.user.userprofile.score + deduction
			request.user.userprofile.save()
			context = {'unique': 'ID'}
			return render(request, 'penalty_linkcreate.html', context)
		except:
			context = {'unique': 'ID'}
			return render(request, 'penalty_linkcreate.html', context)
	else:
		try:
			score = UserProfile.objects.get(user=request.user).score
			if score < 30:
				request.session["link_create_token"] = uuid.uuid4()
				return redirect("link_create")
			else:
				try:
					seen_photo_option = TutorialFlag.objects.get(user=request.user).seen_photo_option
					if seen_photo_option:
						request.session["link_create_token"] = uuid.uuid4()
						return redirect("link_create")
					else:
						request.session["ftue_photo_option"] = True
						return redirect("photo_option_tutorial")
				except:
					request.session["ftue_photo_option"] = True
					TutorialFlag.objects.create(user=request.user)
					return redirect("photo_option_tutorial")
		except:
			request.session["link_create_token"] = uuid.uuid4()
			return redirect("link_create")


class LinkCreateView(CreateView):
	model = Link
	form_class = LinkForm

	def get_context_data(self, **kwargs):
		context = super(LinkCreateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["random"] = random.sample(xrange(1,188),15) #select 15 random emoticons out of 188		
			banned, time_remaining, warned = posting_allowed(self.request.user.id)
			context["banned"] = banned
			context["warned"] = warned
			if self.request.is_feature_phone:
				context["feature_phone"] = True
			else:
				context["feature_phone"] = False
			if banned:
				m, s = divmod(time_remaining, 60)
				h, m = divmod(m, 60)
				d, h = divmod(h, 24)
				if d and h and m:
					context["time_remaining"] = "%s days, %s hours and %s minutes" % (int(d), int(h), int(m))
				elif h and m:
					context["time_remaining"] = "%s hours and %s minutes" % (int(h), int(m))
				elif m and s:
					context["time_remaining"] = "%s minutes and %s seconds" % (int(m), int(s))
				elif s:
					context["time_remaining"] = "%s seconds" % int(s)
				else:
					context["time_remaining"] = None
			else:
				context["time_remaining"] = None
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		banned, time_remaining, warned = posting_allowed(self.request.user.id)
		if not banned:
			try:
				token = self.request.session["link_create_token"]
			except:
				return redirect("profile", slug=self.request.user.username)
			self.request.session["link_create_token"] = None
			try:
				if valid_uuid(str(token)):
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
						f.submitter.userprofile.score = f.submitter.userprofile.score + 1 #adding 2 points every time a user submits new content
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
						score = fuzz.ratio(f.description, f.submitter.userprofile.previous_retort)
						if score > 86:
							return redirect("link_create_pk")
						else:
							pass
					except:
						pass
					f.submitter.userprofile.previous_retort = f.description
					f.save()
					try:
						av_url = user.userprofile.avatar.url
					except:
						av_url = None
					add_home_link(link_pk=f.id, categ='1', nick=user.username, av_url=av_url, desc=f.description, \
						scr=f.submitter.userprofile.score, cc=0, writer_pk=user.id, device=f.device)
					if self.request.user_banned:
						extras = add_unfiltered_post(f.id)
						if extras:
							queue_for_deletion.delay(extras)
					else:
						add_filtered_post(f.id)
						extras = add_unfiltered_post(f.id)
						if extras:
							queue_for_deletion.delay(extras)
					f.submitter.userprofile.save()
					return super(CreateView, self).form_valid(form)
				else:
					return redirect("score_help")
			except:
				return redirect("score_help")
		else:
			return redirect("score_help")

	def get_success_url(self): #which URL to go back once settings are saved?
		return reverse_lazy("home")

@ratelimit(rate='2/s')
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
			try:
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
			except:
				context["unauthorized"] = True
				context["unique"] = None
				# group = None
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
				try:
					unique = self.request.session["kick_slug"]
					self.request.session["kick_slug"] = None
					group = Group.objects.get(unique=unique)
				except:
					return redirect("profile", self.request.user.username)
				if group.private == '0':
					if group.owner != self.request.user:
						return redirect("public_group", slug=unique)
					else:
						pk = self.request.session["kick_pk"]
						self.request.session["kick_pk"] = None
						culprit = User.objects.get(id=pk)
						group_id = group.id
						if GroupBanList.objects.filter(which_user=culprit, which_group_id=group_id).exists():# already kicked and banned
							return redirect("public_group", slug=unique)
						else:
							GroupBanList.objects.create(which_user_id=pk,which_group_id=group_id)#placing the person in ban list
							try:
								GroupCaptain.objects.get(which_user_id=pk, which_group_id=group_id).delete()
							except:
								pass
							culprit.userprofile.score = culprit.userprofile.score - 50 #cutting 50 points
							culprit.userprofile.save()
							remove_group_notification(user_id=pk,group_id=group_id) #removing culprit's matka notification
							remove_group_member(group_id=group_id, username=culprit.username)
							remove_user_group(user_id=pk, group_id=group_id)
							text = culprit.username
							reply = Reply.objects.create(text=text, which_group_id=group_id, writer=self.request.user, \
								category='2')
							return redirect("public_group", slug=unique)
				else:
					return redirect("score_help")

@ratelimit(rate='2/s')
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

class PhotoQataarHelpView(FormView):
	form_class = PhotoQataarHelpForm
	template_name = "photo_qataar.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoQataarHelpView, self).get_context_data(**kwargs)
		context["key"] = self.kwargs["pk"]
		return context

class BaqiPhotosHelpView(FormView):
	form_class = BaqiPhotosHelpForm
	template_name = "baqi_photos_help.html"

	def get_context_data(self, **kwargs):
		context = super(BaqiPhotosHelpView, self).get_context_data(**kwargs)
		context["key"] = self.kwargs["pk"]
		return context

class GroupReportView(FormView):
	form_class = GroupReportForm
	template_name = "group_report.html"

	def get_context_data(self, **kwargs):
		context = super(GroupReportView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				unique = self.request.session["groupreport_slug"]
				context["unique"] = unique
				reply_id = self.request.session["groupreport_pk"]
				group = Group.objects.get(unique=unique)
			except:
				context["captain"] = False
				context["unique"] = None
				context["reply"] = None
				return context
			if GroupCaptain.objects.filter(which_user=self.request.user, which_group=group).exists() and Reply.objects.filter(pk=reply_id, which_group=group).exists():
				context["captain"] = True
				reply = Reply.objects.get(id=reply_id)
				context["reply"] = reply
			else:
				context["captain"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			try:
				unique = Group.objects.get(unique=self.request.session["groupreport_slug"])
				self.request.session["groupreport_slug"] = None
			except:
				return redirect("home")
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
						return redirect("public_group", slug=unique.unique)
					else: #i.e. the person requesting this is a group captain
						reply.category = '3'
						reply.text = self.request.user.username
						reply.writer.userprofile.score = reply.writer.userprofile.score - 5
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
				rprt = self.request.POST.get("report")
				if rprt == 'Haan':
					reply_id = self.request.POST.get("reply")
					link_id = self.request.POST.get("link")
					if Publicreply.objects.filter(pk=reply_id,answer_to=link_id, abuse=False).exists() and \
					Link.objects.filter(pk=link_id,submitter=self.request.user).exists():
						reply = get_object_or_404(Publicreply, pk=reply_id)
						reply.abuse = True
						reply.save()
						pk = reply.submitted_by_id
						UserProfile.objects.filter(user_id=pk).update(score=F('score')-3)
						self.request.session["report_pk"] = None
						self.request.session["linkreport_pk"] = None
						ident = self.request.user.id
						if pk != ident:
							document_publicreply_abuse(pk)
							#report.delay(target_id=pk, reporter_id=ident, report_origin='2', which_publicreply_id=reply_id)
						return redirect("reply_pk", pk=reply.answer_to.id)
					else:
						UserProfile.objects.filter(user=self.request.user).update(score=F('score')-3)
						return redirect("home")
				else:
					link_id = self.request.POST.get("link")
					link = get_object_or_404(Link, pk=link_id)
					self.request.session["report_pk"] = None
					self.request.session["linkreport_pk"] = None
					return redirect("reply_pk", pk= link.id)
			else:
				return redirect("score_help")

class WelcomeReplyView(FormView):
	form_class = WelcomeReplyForm

	def form_valid(self, form):
		if self.request.method == 'POST':
			if self.request.user_banned:
				return redirect("score_help")
			else:
				try:
					pk = self.request.session["welcome_pk"]
					self.request.session["welcome_pk"] = None
					target = User.objects.get(pk=pk)
				except:
					return redirect("profile", slug=self.request.user.username)
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
					try:
						av_url = target.userprofile.avatar.url
					except:
						av_url = None
					if Link.objects.filter(submitter=target).exists():
						parent = Link.objects.filter(submitter=target).latest('id')
						parent.reply_count = parent.reply_count + 1
						update_cc_in_home_link(parent.id)
					else:
						num = random.randint(1,5)
						if num == 1:
							parent = Link.objects.create(description='I am new', submitter=target, reply_count=1, device=device)
							add_home_link(link_pk=parent.id, categ='1', nick=target.username, av_url=av_url, desc='I am new', \
								scr=target.userprofile.score, cc=1, writer_pk=target.id, device=device)
						elif num == 2:
							parent = Link.objects.create(description='Salam, Im new', submitter=target, reply_count=1, device=device)
							add_home_link(link_pk=parent.id, categ='1', nick=target.username, av_url=av_url, desc='Salam, Im new', \
								scr=target.userprofile.score, cc=1, writer_pk=target.id, device=device)
						elif num == 3:
							parent = Link.objects.create(description='mein new hun', submitter=target, reply_count=1, device=device)
							add_home_link(link_pk=parent.id, categ='1', nick=target.username, av_url=av_url, desc='mein new hun', \
								scr=target.userprofile.score, cc=1, writer_pk=target.id, device=device)
						elif num == 4:
							parent = Link.objects.create(description='hi every1', submitter=target, reply_count=1, device=device)
							add_home_link(link_pk=parent.id, categ='1', nick=target.username, av_url=av_url, desc='hi every1', \
								scr=target.userprofile.score, cc=1, writer_pk=target.id, device=device)
						else:
							parent = Link.objects.create(description='damadam mast qalander', submitter=target, reply_count=1, device=device)
							add_home_link(link_pk=parent.id, categ='1', nick=target.username, av_url=av_url, desc='damadam mast qalander', \
								scr=target.userprofile.score, cc=1, writer_pk=target.id, device=device)
						add_filtered_post(parent.id)
						extras = add_unfiltered_post(parent.id)
						if extras:
							queue_for_deletion.delay(extras)
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
					parent.latest_reply = reply
					parent.save()
					try:
						url = self.request.user.userprofile.avatar.url
					except:
						url = None
					time = convert_to_epoch(reply.submitted_on)
					publicreply_notification_tasks.delay(link_id=parent.id,link_submitter_url=av_url,\
						sender_id=self.request.user.id,link_submitter_id=pk,link_submitter_username=target.username,\
						link_desc=parent.description,reply_time=time,reply_poster_url=url,\
						reply_poster_username=self.request.user.username,reply_desc=reply.description,is_welc=False,\
						reply_count=parent.reply_count,priority='home_jawab',from_unseen=False)
					return redirect("home")
				else:
					return redirect("score_help")

def cross_group_notif(request,pk=None, uid=None,from_home=None,*args,**kwargs):
	update_notification(viewer_id=uid,object_id=pk, object_type='3',seen=True,unseen_activity=True, single_notif=False,\
		bump_ua=False)
	if from_home == '1':
		return redirect("home")
	elif from_home == '2':
		return redirect("see_best_photo")
	elif from_home == '5':
		return redirect("see_special_photo")
	else:
		return redirect("see_photo")

def cross_comment_notif(request, pk=None, usr=None, from_home=None, object_type=None, *args, **kwargs):
	update_notification(viewer_id=usr, object_id=pk, object_type='0',seen=True, unseen_activity=True,\
		single_notif=False,bump_ua=False)
	if from_home == '1':
		return redirect("home")
	elif from_home == '2':
		return redirect("see_best_photo")
	elif from_home == '5':
		return redirect("see_special_photo")
	else:
		return redirect("see_photo")

def cross_salat_notif(request, pk=None, user=None, from_home=None, *args, **kwargs):
	notif_name = "np:"+user+":"+pk.split(":",1)[1]
	hash_name = pk
	viewer_id = user
	delete_salat_notification(notif_name,hash_name,viewer_id)
	if from_home == '1':
		return redirect("home")
	elif from_home == '2':
		return redirect("see_best_photo")
	elif from_home == '5':
		return redirect("see_special_photo")
	else:
		return redirect("see_photo")

def cross_notif(request, pk=None, user=None, from_home=None, *args, **kwargs):
	update_notification(viewer_id=user, object_id=pk, object_type='2',seen=True, unseen_activity=True,\
		single_notif=False, bump_ua=False)
	if from_home == '1':
		return redirect("home")
	elif from_home == '2':
		return redirect("see_best_photo")
	elif from_home == '5':
		return redirect("see_special_photo")
	else:
		return redirect("see_photo")

@ratelimit(rate='2/s')
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
					link = Link.objects.filter(submitter_id=target_id).latest('id')
					if value == 1:
						if not Vote.objects.filter(voter=request.user,link=link):
							Vote.objects.create(voter=request.user, link=link, value=value)
							add_vote_to_home_link(link.id, value, request.user.username)
							target.userprofile.score = target.userprofile.score + 3
							target.userprofile.save()
						else:
							pass
					elif value == 0:
						value = -1
						if not Vote.objects.filter(voter=request.user,link=link):
							Vote.objects.create(voter=request.user, link=link, value=value)
							add_vote_to_home_link(link.id, value, request.user.username)
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
						try:
							av_url = target.userprofile.avatar.url
						except:
							av_url = None
						add_home_link(link_pk=link.id, categ='1', nick=target.username, av_url=av_url, desc='mein idher hu', \
								scr=target.userprofile.score, cc=0, writer_pk=target.id, device='1')
						add_filtered_post(link.id)
						extras = add_unfiltered_post(link.id)
						if extras:
							queue_for_deletion.delay(extras)
						Vote.objects.create(voter=request.user, link=link, value=value)
						add_vote_to_home_link(link.id, value, request.user.username)
						target.userprofile.score = target.userprofile.score + 3
						target.userprofile.save()
						return redirect("home")
					elif value == 0:
						value = -1
						link = Link.objects.create(description='mein idher hu', submitter=target)
						try:
							av_url = target.userprofile.avatar.url
						except:
							av_url = None
						add_home_link(link_pk=link.id, categ='1', nick=target.username, av_url=av_url, desc='mein idher hu', \
								scr=target.userprofile.score, cc=0, writer_pk=target.id, device='1')
						add_filtered_post(link.id)
						extras = add_unfiltered_post(link.id)
						if extras:
							queue_for_deletion.delay(extras)
						Vote.objects.create(voter=request.user, link=link, value=value)
						add_vote_to_home_link(link.id, value, request.user.username)
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

def process_photo_vote(pk, ident, val, voter_id):
	if int(val) > 0:
		vote_score_increase = 1
		visible_score_increase = 1
		media_score_increase = 1
		score_increase = 1
		photo_vote_tasks.delay(pk, ident, vote_score_increase, visible_score_increase, media_score_increase, score_increase, voter_id)
	else:
		vote_score_increase = -1
		visible_score_increase = -1
		media_score_increase = -1
		score_increase = -1
		photo_vote_tasks.delay(pk, ident, vote_score_increase, visible_score_increase, media_score_increase, score_increase, voter_id)

@ratelimit(rate='2/s')
def photo_vote(request, pk=None, val=None, origin=None, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.media_score = request.user.userprofile.media_score + deduction
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': pk}
		return render(request, 'penalty_photovote.html', context)
	else:
		photo = Photo.objects.get(id=pk)
		ident = photo.owner_id
		vote_score = photo.vote_score
		banned_from_voting,time_remaining = check_photo_vote_ban(request.user.id)
		if request.user.id == ident: #can't vote your own video
			context = {'unique': pk}
			return render(request, 'already_photovoted.html', context)
		elif banned_from_voting:
			if time_remaining == '-1':
				to_go = time_remaining
			else:
				to_go = timezone.now()+timedelta(seconds=time_remaining)
			context = {'time_remaining':to_go,'origin':origin, 'pk':pk, 'slug':slug}
			return render(request, 'photovote_disallowed.html', context)
		else:
			defender = in_defenders(request.user.id)
			# print defender
			if not defender:
				can_vote, time_remaining = can_photo_vote(request.user.id)
				if not can_vote:
					time_remaining = timezone.now()+timedelta(seconds=time_remaining)
					context={'time_remaining':time_remaining, 'origin':origin, 'pk':pk, 'slug':slug}
					return render(request, 'photovote_cooldown.html', context)
			added = add_vote_to_photo(pk, request.user.username, val)
			if added:
				if defender:
				#this person can kick extra butt; she's a defender!
					# ensure correct link_id is passed forward if origin is 'home'
					if origin == '3':
						link_id = slug
					else:
						link_id = '0'
					uname = photo.owner.username
					if first_time_photo_defender(request.user.id):
						#show the tutorial
						context = {'photo_id':pk,'uname':uname, 'ident':ident, 'origin':origin, 'link_id':link_id, \
						'val':int(val)}
						return render(request, 'photo_defender_tutorial.html', context)
					else:
						if int(val) == 1 and vote_score < -2:
							# i.e. the photo is a candidate to be unbanned
							context = {'pk':pk, 'photo_owner':uname, 'ident':ident,'photo_url':photo.image_file.url,'origin':origin, 'link_id':link_id}
							return render(request, 'resurrect_photo.html',context)
						elif int(val) == 0 and vote_score > -3:
							# i.e. the photo is a candidate to be banned
							# ensure if user is already banned, the defender can see that information on her screen
							banned, time_remaining = check_photo_upload_ban(ident)
							if banned:
								if time_remaining == '-1':
									to_go = '-1'
								else:
									to_go = timezone.now()+timedelta(seconds=time_remaining)
							else:
								to_go = '0'
							# remove the photo and ban the person from photo-uploading and photo-voting 
							context = {'photo_id': pk, 'photo_owner':uname, 'owner_id':ident, 'val':int(val),\
							'photo_url':photo.image_file.url, 'origin': origin, 'link_id':link_id, 'already_banned':to_go}
							return render(request, 'ban_photo.html', context)
						else:
							process_photo_vote(pk, ident, int(val), request.user.id)
				else:
					process_photo_vote(pk, ident, int(val), request.user.id)
				if origin == '1':
					# originated from taza photos page
					request.session["target_photo_id"] = pk
					return redirect("see_photo")
				elif origin == '2':
					# originated from best photos page
					request.session["target_best_photo_id"] = pk
					return redirect("see_best_photo")
				elif origin == '3':
					request.session["target_id"] = slug
					return redirect("home_loc")
				elif origin == '4':
					request.session["photograph_id"] = pk
					return redirect("profile", slug)
				else:
					request.session["target_photo_id"] = pk
					return redirect("see_photo")
			else:
				context = {'unique': pk}
				return render(request, 'already_photovoted.html', context)

@ratelimit(rate='2/s')
def ban_photo_uploader(request, pk=None, uname=None, ident=None, duration=None, origin=None,link_id=None, val=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		context = {'pk': 'pk'}
		return render(request, 'penalty_defender.html', context)
	else:
		if in_defenders(request.user.id):
			if duration == '1':
				#i.e. ban for 24 hrs
				photo = Photo.objects.filter(id=pk).update(vote_score = -100) #to censor the photo from the list
				update_object(object_id=pk,object_type='0',vote_score=-100)
				add_to_photo_upload_ban(ident, '1') #to impede from adding more photos
				add_to_photo_vote_ban(ident, '1') #to impede from voting on other photos
			elif duration == '2':
				#i.e. ban for 1 week
				photo = Photo.objects.filter(id=pk).update(vote_score = -100) #to censor the photo from the list
				update_object(object_id=pk,object_type='0',vote_score=-100)
				add_to_photo_upload_ban(ident, '7') #to impede from adding more photos
				add_to_photo_vote_ban(ident, '7') #to impede from voting on other photos
			elif duration == '3':
				#i.e. ban forever
				photo = Photo.objects.filter(id=pk).update(vote_score = -100) #to censor the photo from the list
				update_object(object_id=pk,object_type='0',vote_score=-100)
				add_to_photo_upload_ban(ident, '-1') #to impede from adding more photos
				add_to_photo_vote_ban(ident, '-1') #to impede from voting on other photos
			else:
				#the person changed their mind, so don't ban the photo, just regularly downvote it
				process_photo_vote(pk, ident, val, request.user.id)
				if origin == '1':
					request.session["target_photo_id"] = pk
					return redirect("see_photo")
				elif origin == '2':
					request.session["target_best_photo_id"] = pk
					return redirect("see_best_photo")
				elif origin == '3':
					request.session["target_id"] = link_id
					return redirect("home_loc")
				elif origin == '4':
					request.session["photograph_id"] = pk
					return redirect("profile", uname)
				else:
					request.session["target_photo_id"] = pk
					return redirect("see_photo")
			photovote_usernames_and_values = get_photo_votes(pk)
			uname_list = [k for (k,v) in photovote_usernames_and_values if int(v) > 0 ] #extract all usernames who upvoted this filth!
			if uname_list:
				#i.e. this kicks in if the photo has been voted
				number_of_voters = len(uname_list)
				request.session["target_unames"] = uname_list
				context = {'pk':pk, 'owner_name': uname,'unames':uname_list, 'origin':origin, 'link_id':link_id,\
				 'num':number_of_voters, 'type':'ban'}
				return render(request, 'ban_photo_voter.html',context)
			else:
				#i.e. if the photo has not garnered any votes
				if origin == '1':
					request.session["target_photo_id"] = pk
					return redirect("see_photo")
				elif origin == '2':
					request.session["target_best_photo_id"] = pk
					return redirect("see_best_photo")
				elif origin == '3':
					request.session["target_id"] = link_id
					return redirect("home_loc")
				elif origin == '4':
					request.session["photograph_id"] = pk
					return redirect("profile", uname)
				else:
					request.session["target_photo_id"] = pk
					return redirect("see_photo")
		else:
			context = {'pk': 'pk'}
			return render(request, 'not_defender.html', context)

def redirect_ban_or_resurrect_page(request, pk=None, uname=None, ident=None, origin=None, link_id=None, val=None, *args, **kwargs):
	photo = Photo.objects.get(id=pk)
	photo_url = photo.image_file.url
	score = photo.vote_score
	add_photo_defender_tutorial(request.user.id)
	if int(val) == 0 and score > -3:
		#photo is to be banned
		banned, time_remaining = check_photo_upload_ban(ident)
		if banned:
			if time_remaining == '-1':
				to_go = '-1'
			else:
				to_go = timezone.now()+timedelta(seconds=time_remaining)
		else:
			to_go = '0'
		context = {'photo_id': pk, 'photo_owner':uname, 'owner_id':ident, 'photo_url':photo_url, 'origin': origin, 'link_id':link_id, \
		'val':val, 'already_banned':to_go}
		return render(request, 'ban_photo.html', context)
	elif int(val) == 1 and score < -2:
		#photo is to be unbanned
		context = {'pk':pk, 'photo_owner':uname, 'ident':ident,'photo_url':photo_url,'origin':origin, 'link_id':link_id}
		return render(request, 'resurrect_photo.html',context)
	else:
		#photo is neither to be banned or unbanned
		if origin == '1':
			request.session["target_photo_id"] = pk
			return redirect("see_photo")
		elif origin == '2':
			request.session["target_best_photo_id"] = pk
			return redirect("see_best_photo")
		elif origin == '3':
			request.session["target_id"] = link_id
			return redirect("home_loc")
		elif origin == '4':
			request.session["photograph_id"] = pk
			return redirect("profile", uname)
		else:
			request.session["target_photo_id"] = pk
			return redirect("see_photo")

def resurrect_photo(request, pk=None, ident=None, dec=None, uname=None, origin=None, link_id=None, *args, **kwargs):
	if dec == '1' and in_defenders(request.user.id):
		#ressurect photo
		Photo.objects.filter(id=pk).update(vote_score=0, visible_score=0)
		update_object(object_id=pk,object_type='0',vote_score=0)
		photovote_usernames_and_values = get_photo_votes(pk)
		uname_list = [k for (k,v) in photovote_usernames_and_values if int(v) == 0 ] #extract all usernames who downvoted this gem!
		if uname_list:
			#i.e. this kicks in if the photo has been voted
			number_of_voters = len(uname_list)
			request.session["target_unames"] = uname_list
			context = {'pk':pk, 'owner_name': uname,'unames':uname_list, 'origin':origin, 'link_id':link_id,\
			 'num':number_of_voters,'type':'unban'}
			return render(request, 'ban_photo_voter.html',context)
	else:
		#don't resurrect photo, just return with a simple upvote
		process_photo_vote(pk, ident, 1, request.user.id)
	if origin == '1':
		request.session["target_photo_id"] = pk
		return redirect("see_photo")
	elif origin == '2':
		request.session["target_best_photo_id"] = pk
		return redirect("see_best_photo")
	elif origin == '3':
		request.session["target_id"] = link_id
		return redirect("home_loc")
	elif origin == '4':
		request.session["photograph_id"] = pk
		return redirect("profile", owner_name)
	else:
		request.session["target_photo_id"] = pk
		return redirect("see_photo")

def ban_photo_voter(request, pk=None, owner_name = None, duration=None, origin=None, link_id = None, *args, **kwargs):
	uname_list = request.session["target_unames"]
	request.session["target_unames"] = None
	targets = User.objects.filter(username__in=uname_list).values_list('id',flat=True)
	if duration == '1':
			add_to_photo_vote_ban(targets, '0.1')
	elif duration == '2':
			add_to_photo_vote_ban(targets, '3')
	elif duration == '3':
			add_to_photo_vote_ban(targets, '7')
	elif duration == '4':
			add_to_photo_vote_ban(targets, '-1')
	else:
		pass
	if origin == '1':
		request.session["target_photo_id"] = pk
		return redirect("see_photo")
	elif origin == '2':
		request.session["target_best_photo_id"] = pk
		return redirect("see_best_photo")
	elif origin == '3':
		request.session["target_id"] = link_id
		return redirect("home_loc")
	elif origin == '4':
		request.session["photograph_id"] = pk
		return redirect("profile", owner_name)
	else:
		request.session["target_photo_id"] = pk
		return redirect("see_photo")


@ratelimit(rate='2/s')
def video_vote(request, pk=None, val=None, usr=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.media_score = request.user.userprofile.media_score + deduction
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': pk}
		return render(request, 'penalty_videovote.html', context)
	else:
		video = Video.objects.get(id=pk)
		ident = video.owner.id
		if request.user.id == ident: #can't vote your own video
			context = {'unique': pk}
			return render(request, 'already_videovoted.html', context)
		else:
			added = add_vote_to_video(pk, request.user.username, val)
			if added:
				if int(val) > 0:
					vote_score_increase = 1
					visible_score_increase = 1
					media_score_increase = 1
					score_increase = 1
					video_vote_tasks.delay(pk, ident, vote_score_increase, visible_score_increase, media_score_increase, score_increase)
				else:
					vote_score_increase = -1
					visible_score_increase = -1
					media_score_increase = -1
					score_increase = -1
					video_vote_tasks.delay(pk, ident, vote_score_increase, visible_score_increase, media_score_increase, score_increase)
				return redirect("see_video")
			else:
				context = {'unique': pk}
				return render(request, 'already_videovoted.html', context)

def photostream_vote(request, pk=None, val=None, from_best=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.media_score = request.user.userprofile.media_score + deduction
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': pk}
		return render(request, 'penalty_photovote.html', context)
	else:
		if pk.isdigit() and val.isdigit():
			if from_best == '5':
				ident = pk
				photo = Photo.objects.get(id=ident)
			else:
				stream = PhotoStream.objects.get(id=pk)
				ident = stream.cover_id
				photo = Photo.objects.get(id=ident)
			if PhotoVote.objects.filter(voter=request.user, photo_id=ident).exists() or request.user == photo.owner:
				if from_best == '5':
					return redirect("see_photo_pk", ident)
				else:
					return redirect("see_photo_pk", ident)
			else:
				if val == '1':
						if request.user_banned:
							return redirect("score_help")
						else:
							# photo = Photo.objects.get(id=ident)
							PhotoVote.objects.create(voter=request.user, photo=photo, photo_owner=photo.owner, value=1)
							photo.visible_score = photo.visible_score + 1
							photo.vote_score = photo.vote_score + 1
							photo.owner.userprofile.media_score = photo.owner.userprofile.media_score + 1
							photo.owner.userprofile.score = photo.owner.userprofile.score + 1
							photo.owner.userprofile.save()
							photo.save()
				elif val == '0':
						if request.user_banned:
							return redirect("score_help")
						else:
							# photo = Photo.objects.get(id=ident)
							PhotoVote.objects.create(voter=request.user, photo=photo, photo_owner=photo.owner, value=-1)
							photo.visible_score = photo.visible_score - 1
							photo.vote_score = photo.vote_score -1
							photo.owner.userprofile.media_score = photo.owner.userprofile.media_score - 1
							photo.owner.userprofile.score = photo.owner.userprofile.score - 1
							photo.owner.userprofile.save()
							photo.save()
				else:
					if from_best == '1':
						return redirect("see_best_photo_pk", ident)
					elif from_best == '0':
						return redirect("see_photo_pk", ident)
					elif from_best == '5':
						return redirect("see_special_photo_pk", ident)
					else:
						request.session['target_id'] = int(from_best)
						return redirect("home_loc")
				if from_best == '1':
					return redirect("see_best_photo_pk", ident)
				elif from_best == '0':
					return redirect("see_photo_pk", ident)
				elif from_best == '5':
					return redirect("see_special_photo_pk", ident)
				else:
					request.session['target_id'] = int(from_best)
					return redirect("home_loc")
		else:
			if from_best == '1':
				return redirect("see_best_photo_pk", ident)
			elif from_best == '0':
				return redirect("see_photo_pk", ident)
			elif from_best == '5':
				return redirect("see_special_photo_pk", ident)
			else:
				request.session['target_id'] = int(from_best)
				return redirect("home_loc")

def salat_notification(request, pk=None, *args, **kwargs):
	now = datetime.utcnow()+timedelta(hours=5)
	epochtime = convert_to_epoch(now)
	# current_minute = now.hour * 60 + now.minute
	# previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
		'LOCATION': 'unix:/var/run/memcached/memcached.sock', 'TIMEOUT': 70,
	})
	salat_timings = cache_mem.get('salat_timings')
	try:
		starting_time = datetime.combine(now.today(), salat_timings['current_namaz_start_time'])
	except:
		return redirect("salat_invite")
	if salat_timings['namaz'] =='Fajr':
		salat = '1'
	elif salat_timings['namaz'] =='Zuhr':
		salat = '2'
	elif salat_timings['namaz'] == 'Asr':
		salat = '3'
	elif salat_timings['namaz'] == 'Maghrib':
		salat = '4'
	elif salat_timings['namaz'] == 'Isha':
		salat = '5'
	else:
		return redirect("internal_salat_invite")
	try:
		latest_namaz = LatestSalat.objects.filter(salatee_id=pk).latest('when') #when did this person pray?
	except:
		#latest_namaz does not exist
		latest_namaz = None
	if pk.isdigit() and not SalatInvite.objects.filter(invitee_id=pk, which_salat=salat, sent_at__gte=starting_time).exists() and not AlreadyPrayed(latest_namaz,now):
		salat_object = SalatInvite.objects.create(inviter=request.user, invitee_id=pk, which_salat=salat, sent_at=now)
		salat_object_id = salat_object.id
		try:
			owner_url = request.user.userprofile.avatar.url
		except:
			owner_url = None
		create_object(object_id=salat_object_id,object_type='4',object_owner_name=request.user.username,\
			object_owner_avurl=owner_url,object_desc=salat_timings['namaz'], object_owner_id=request.user.id)
		create_notification(object_id=salat_object_id,object_type='4',viewer_id=pk,seen=False,updated_at=epochtime,\
			single_notif=True,priority='namaz_invite')
		viewer_salat_notifications(viewer_id=pk,object_id=salat_object_id, time=epochtime)
		return redirect("internal_salat_invite")
	else:
		user = User.objects.get(id=pk)
		context = {'invitee':user, 'namaz':salat_timings['namaz']}
		return render(request, 'salat_invite_error.html', context)

@ratelimit(rate='2/s')
def fan(request, pk=None, from_profile=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 5 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		return redirect("see_photo")
	else:
		if pk.isdigit() and (Photo.objects.filter(owner=request.user).exists() or request.user.userprofile.score > 30):
			try:
				user = User.objects.get(id=pk)
				if request.user == user:
					request.user.userprofile.score = request.user.userprofile.score - 5
					request.user.userprofile.save()
					context = {'unique': user}
					return render(request, 'penalty_fan.html', context)
			except:
				return redirect("see_photo")
			try:
				UserFan.objects.get(fan=request.user, star=user).delete()
				remove_from_photo_owner_activity(user.id, request.user.id)
				try:
					aggregate_object = TotalFanAndPhotos.objects.get(owner=user)
					aggregate_object.total_fans = aggregate_object.total_fans - 1
					aggregate_object.last_updated = datetime.utcnow()+timedelta(hours=5)
					aggregate_object.save()
				except:
					pass
				if from_profile == '1':
					return redirect("profile", user.username)
				elif from_profile == '2':
					return redirect("star_list", request.user.id)
				else:
					return redirect("profile", user.username)
			except:
				try:
					seen_fan_option = TutorialFlag.objects.filter(user=request.user).latest('id').seen_fan_option
					if seen_fan_option:
						if not UserFan.objects.filter(fan=request.user, star=user).exists(): #adding extra check
							UserFan.objects.create(fan=request.user, star=user, fanning_time=datetime.utcnow()+timedelta(hours=5))
							add_to_photo_owner_activity(pk, request.user.id)
							try:
								aggregate_object = TotalFanAndPhotos.objects.get(owner=user)
								aggregate_object.total_fans = aggregate_object.total_fans + 1
								aggregate_object.last_updated = datetime.utcnow()+timedelta(hours=5)
								aggregate_object.save()
							except:
								TotalFanAndPhotos.objects.create(owner=user, total_fans=1, total_photos=0, last_updated=datetime.utcnow()+timedelta(hours=5))
						else:
							if from_profile == '1':
								return redirect("profile", user.username)
							elif from_profile == '2':
								return redirect("star_list", request.user.id)
							else:
								return redirect("profile", user.username)
						if from_profile == '1':
							return redirect("profile", user.username)
						elif from_profile == '2':
							return redirect("star_list", request.user.id)
						else:
							return redirect("profile", user.username)
					else:
						#no seen fan tutorial
						request.session["ftue_fan_option"] = True
						request.session["ftue_fan_user"] = user
						return redirect("fan_tutorial")
				except:
					#the tutorial object didn't exist, has to be created now
					TutorialFlag.objects.create(user=request.user)
					request.session["ftue_fan_option"] = True
					request.session["ftue_fan_user"] = user
					return redirect("fan_tutorial")
			if from_profile == '1':
				return redirect("profile", user.username)
			elif from_profile == '2':
				return redirect("star_list", request.user.id)
			else:
				return redirect("profile", user.username)
		else:
			try:
				user = User.objects.get(id=pk)
				if request.user == user:
					request.user.userprofile.score = request.user.userprofile.score - 5
					request.user.userprofile.save()
					context = {'unique': user}
					return render(request, 'penalty_fan.html', context)
			except:
				return redirect("see_photo")
			context = {'unique': user.username}
			return render(request, 'fan_requirement.html', context)
		return redirect("see_photo")

class SalatTutorialView(FormView):
	form_class = SalatTutorialForm
	template_name = "salat_tutorial.html"

	def form_valid(self, form):
		if self.request.method == 'POST':
			try:
				choice = self.request.POST.get("choice")
				if choice == 'samajh gaya':
					TutorialFlag.objects.filter(user=self.request.user).update(seen_salat_option=True)
					return redirect("process_salat")
				else:
					return redirect("home")
			except:
				TutorialFlag.objects.filter(user=self.request.user).update(seen_salat_option=True)
				return redirect("process_salat")
		else:
			TutorialFlag.objects.filter(user=self.request.user).update(seen_salat_option=True)
			return redirect("home")

class FanTutorialView(FormView):
	form_class = FanTutorialForm
	template_name = "fan_tutorial.html"

	def get_context_data(self, **kwargs):
		context = super(FanTutorialView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				user = self.request.session["ftue_fan_user"]
				context["name"] = user.username
				context["skip"] = False
			except:
				context["skip"] = True
		return context

	def form_valid(self, form):
		try:
			if self.request.session["ftue_fan_option"] and self.request.session["ftue_fan_user"]:
				self.request.session["ftue_fan_option"] = None
				user = self.request.session["ftue_fan_user"]
				self.request.session["ftue_fan_user"] = None
				if self.request.method == 'POST':
					option = self.request.POST.get("choice", '')
					if option == 'samajh gaya':
						if TutorialFlag.objects.filter(user=self.request.user).update(seen_fan_option=True) \
						and not UserFan.objects.filter(fan=self.request.user, star=user).exists():
							UserFan.objects.create(fan=self.request.user, star=user, fanning_time=datetime.utcnow()+timedelta(hours=5))
							add_to_photo_owner_activity(user.id, self.request.user.id)
							try:
								aggregate_object = TotalFanAndPhotos.objects.get(owner=user)
								aggregate_object.total_fans = aggregate_object.total_fans + 1
								aggregate_object.last_updated = datetime.utcnow()+timedelta(hours=5)
								aggregate_object.save()
							except:
								TotalFanAndPhotos.objects.create(owner=user, total_fans=1, total_photos=0, last_updated=datetime.utcnow()+timedelta(hours=5))
							return redirect("profile", user.username)
						else:
							return redirect("profile", user.username)
					else:
						return redirect("profile", user.username)
			else:
				try:
					flag = TutorialFlag.objects.get(user=self.request.user)
					flag.seen_fan_option = True
					flag.save()
				except:
					TutorialFlag.objects.create(user=self.request.user, seen_fan_option=True)
				return redirect("top_photo")
		except:
			try:
				flag = TutorialFlag.objects.get(user=self.request.user)
				flag.seen_fan_option = True
				flag.save()
			except:
				TutorialFlag.objects.create(user=self.request.user, seen_fan_option=True)
			return redirect("top_photo")

def update_cooldown(obj):
	#time_now = datetime.utcnow().replace(tzinfo=utc)
	time_now = timezone.now()
	time_passed = obj.time_of_casting
	difference = time_now - time_passed
	difference_in_mins = difference.total_seconds() / 60
	interval = int(difference_in_mins / 4) # control the interval length from here
	obj.hot_score = obj.hot_score + interval
	if obj.hot_score > 10:
		obj.hot_score = 10
	return obj

def find_time(obj):
	time_passed = obj.time_of_casting
	target_time = time_passed + timedelta(minutes=4) # control the interval length from here
	difference = target_time - timezone.now()#datetime.utcnow().replace(tzinfo=utc)
	return difference

@ratelimit(rate='2/s')
def vote(request, pk=None, usr=None, loc=None, val=None, *args, **kwargs):
	#PERIODS = (1,5*1,10*1,)
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		deduction = 3 * -1
		request.user.userprofile.score = request.user.userprofile.score + deduction
		request.user.userprofile.save()
		context = {'unique': pk}
		return render(request, 'penalty_vote.html', context)
	else:
		if pk.isdigit() and usr.isdigit() and loc.isdigit() and val.isdigit():
			try:
				cooldown = Cooldown.objects.filter(voter=request.user).latest('id')#
			except:
				cooldown = Cooldown.objects.create(voter=request.user, hot_score=10, time_of_casting=timezone.now())
			c_pk = cooldown.pk
			obj = update_cooldown(cooldown)
			obj.save()
			if int(obj.hot_score) < 1:
				time_remaining = find_time(obj)
				#time_stamp = datetime.utcnow().replace(tzinfo=utc) + time_remaining
				time_stamp = timezone.now() + time_remaining
				context = {'time_remaining': time_stamp}
				return render(request, 'cooldown.html', context)
			try:
				link = Link.objects.select_related('submitter__userprofile').get(pk=int(pk))#
			except:
				return redirect("link_create_pk")
			if request.user == link.submitter:
				return redirect("home")
			section = str(loc)
			value = int(val)
			if not Vote.objects.filter(voter=request.user, link=link).exists():#
				#only if user never voted on this link
				if value == 1:
					if request.user_banned:
						return redirect("score_help")
					else:
						UserProfile.objects.filter(user=link.submitter).update(score=F('score')+3)
						Link.objects.filter(pk=int(pk)).update(net_votes=F('net_votes')+1)
						num = random.randint(1,4)
						if num > 2: # don't always reduce hot_score, give jhappees some love
							Cooldown.objects.filter(id=c_pk).update(hot_score=F('hot_score')-1, time_of_casting=timezone.now())
						else:
							Cooldown.objects.filter(id=c_pk).update(time_of_casting=timezone.now())
				elif value == 2:
					if request.user_banned or request.user.username not in FEMALES:
						return redirect("score_help")
					else:
						if link.submitter.userprofile.score < -25:
							if not HellBanList.objects.filter(condemned=link.submitter).exists(): #only insert user in hell-ban list if she isn't there already
								HellBanList.objects.create(condemned=link.submitter) #adding user to hell-ban list
								UserProfile.objects.filter(user=link.submitter).update(score=random.randint(10,71))
						else:
							UserProfile.objects.filter(user=link.submitter).update(score=F('score')+50)
						#link.net_votes = link.net_votes + 1
						Link.objects.filter(pk=int(pk)).update(net_votes=F('net_votes')+1)
						Cooldown.objects.filter(id=c_pk).update(hot_score=F('hot_score')-1, time_of_casting=timezone.now())
				elif value == 0:
					if request.user_banned:
						return redirect("score_help")
					else:
						UserProfile.objects.filter(user=link.submitter).update(score=F('score')-3)
						if link.submitter.userprofile.score < -25:
							if not HellBanList.objects.filter(condemned=link.submitter).exists(): #only insert user in hell-ban list if she isn't there already
								HellBanList.objects.create(condemned=link.submitter) #adding user to hell-ban list
								UserProfile.objects.filter(user=link.submitter).update(score=random.randint(10,71))
						Link.objects.filter(pk=int(pk)).update(net_votes=F('net_votes')-1)
						Cooldown.objects.filter(id=c_pk).update(hot_score=F('hot_score')-1, time_of_casting=timezone.now())
					value = -1
				elif value == 3:
					if request.user_banned or request.user.username not in FEMALES:
						return redirect("score_help")
					else:
						UserProfile.objects.filter(user=link.submitter).update(score=F('score')-50)
						if link.submitter.userprofile.score < -25:
							if not HellBanList.objects.filter(condemned=link.submitter).exists(): #only insert user in hellban list if she isn't there already
								HellBanList.objects.create(condemned=link.submitter) #adding user to hell-ban list
								UserProfile.objects.filter(user=link.submitter).update(score=random.randint(10,71))
						Link.objects.filter(pk=int(pk)).update(net_votes=F('net_votes')-1)
						Cooldown.objects.filter(id=c_pk).update(hot_score=F('hot_score')-3, time_of_casting=timezone.now())
					value = -2
				else:
					value = 0
					return redirect("link_create_pk")
				try:
					Vote.objects.create(voter=request.user, link=link, value=value) #DB call #add the up or down vote in the DB.
					add_vote_to_home_link(link.id, value, request.user.username)
					if value < 0:
						document_link_abuse(link.submitter_id)
						#report.delay(target_id=link.submitter_id, reporter_id=request.user.id, report_origin='1', which_link_id=link.id)
				except:#if vote object can't be created, just redirect the user, no harm done
					return redirect("link_create_pk")
				try:
					request.session['target_id'] = link.id
					return redirect("home_loc")
				except:
					return redirect("home") #e.g. if Dorado WAP browser, which doesn't have HTTP_REFERER	
			else:
				try:
					return redirect(request.META.get('HTTP_REFERER')+"#section"+section)
				except:
					return redirect("home") #e.g. if Dorado WAP browser, which doesn't have HTTP_REFERER
		else:
			return redirect("link_create_pk")
	
# def LinkAutoCreate(user, content):   
# 	link = Link()
# 	#content = content.replace('#',' ') 
# 	link.description = content
# 	link.submitter = user
# 	#user.userprofile.score = user.userprofile.score + 5 #adding score for content creation
# 	epoch = datetime(1970, 1, 1).replace(tzinfo=None)
# 	unaware_submission = datetime.now().replace(tzinfo=None)
# 	td = unaware_submission - epoch 
# 	epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
# 	secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
# 	link.rank_score = round(0 * 0 + secs / 45000, 8)
# 	link.with_votes = 0
# 	link.category = '1' '''
# 	try:
# 		urls1 = re.findall(urlmarker.URL_REGEX,link.description)
# 		if len(urls1)==0:
# 			pass
# 		elif len(urls1)==1:
# 			name, image = read_image(urls1[0])
# 			if image:
# 				image_io = StringIO.StringIO()
# 				image.save(image_io, format='JPEG')
# 				thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
# 				link.image_file = thumbnail
# 		elif len(urls1)>=2:
# 			name, image = read_image(urls1[0])
# 			if image:
# 				image_io = StringIO.StringIO()
# 				image.save(image_io, format='JPEG')
# 				thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
# 				link.image_file = thumbnail
# 			else:
# 				name, image = read_image(urls1[1])
# 				if image:
# 					image_io = StringIO.StringIO()
# 					image.save(image_io, format='JPEG')
# 					thumbnail = InMemoryUploadedFile(image_io, None, name, 'image/jpeg', image_io.len, None)
# 					link.image_file = thumbnail
# 		else:
# 			pass
# 	except Exception as e:
# 		print '%s (%s)' % (e.message, type(e))	
# 		pass			'''
# 	link.save()
# 	user.userprofile.previous_retort = content
# 	user.userprofile.save()

######################### Advertising #########################

@ratelimit(rate='2/s')
def make_ad(request,*args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		context = {'unique': 'pk'}
		return render(request, 'make_ad_error.html', context)
	else:
		request.session["ad_description_token"] = uuid.uuid4()
		return redirect("ad_description")

class AdDescriptionView(FormView):
	form_class = AdDescriptionForm
	template_name = "ad_description.html"

	def get_initial(self):#initial is a keyword argument to a formfield that enables pre-filling in the formfield
		"""
		Returns the initial data to use for forms on this view.
		"""
		user = self.request.user
		try:
			desc = self.request.session["ad_description"]
			self.initial = {'description': desc} #initial needs to be passed a dictionary
			return self.initial
		except:
			return self.initial

	def get_context_data(self, **kwargs):
		context = super(AdDescriptionView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_description_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			ad_description = self.request.POST.get("description")
			self.request.session["ad_description"] = ad_description
			self.request.session["ad_mobile_num_token"] = uuid.uuid4()
			return redirect("ad_mobile_num")
		else:
			return redirect("home")

class AdMobileNumView(FormView):
	form_class = AdMobileNumForm
	template_name = "ad_mobile_num.html"

	def get_initial(self):#initial is a keyword argument to a formfield that enables pre-filling in the formfield
		"""
		Returns the initial data to use for forms on this view.
		"""
		user = self.request.user
		try:
			num = self.request.session["ad_mobile_num"]
			self.initial = {'mobile_number': num} #initial needs to be passed a dictionary
			return self.initial
		except:
			return self.initial

	def get_context_data(self, **kwargs):
		context = super(AdMobileNumView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_mobile_num_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			mobile_number = self.request.POST.get("mobile_number")
			self.request.session["ad_mobile_num"] = mobile_number
			self.request.session["ad_call_pref_token"] = uuid.uuid4()
			return redirect("ad_call_pref")
		else:
			return redirect("home")

class AdCallPrefView(FormView):
	form_class = AdCallPrefForm
	template_name = "ad_call_pref.html"

	def get_context_data(self, **kwargs):
		context = super(AdCallPrefView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_call_pref_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False	
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			call = self.request.POST.get("call",None)
			sms = self.request.POST.get("sms",None)
			callsms = self.request.POST.get("callsms",None)
			if call:
				self.request.session["ad_call_pref"] = '0'
			elif sms:
				self.request.session["ad_call_pref"] = '1'
			elif callsms:
				self.request.session["ad_call_pref"] = '2'
			else:
				return redirect("home")
			self.request.session["ad_title_yesno_token"] = uuid.uuid4()
			return redirect("ad_title_yesno")
		else:
			return redirect("home")

#'Yes' or 'No'
class AdTitleYesNoView(FormView):
	form_class = AdTitleYesNoForm
	template_name = "ad_title_yesno.html"

	def get_context_data(self, **kwargs):
		context = super(AdTitleYesNoView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_title_yesno_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			yes = self.request.POST.get("yes",None)
			no = self.request.POST.get("no",None)
			if yes:
				self.request.session["ad_title_token"] = uuid.uuid4()
				return redirect("ad_title")
			elif no:
				self.request.session["ad_image_yesno_token"] = uuid.uuid4()
				return redirect("ad_image_yesno")
			else:
				return redirect("home")
		else:
			return redirect("home")

class AdTitleView(FormView):
	form_class = AdTitleForm
	template_name = "ad_title.html"

	def get_initial(self):#initial is a keyword argument to a formfield that enables pre-filling in the formfield
		"""
		Returns the initial data to use for forms on this view.
		"""
		user = self.request.user
		try:
			title = self.request.session["ad_title"]
			self.initial = {'title': title} #initial needs to be passed a dictionary
			return self.initial
		except:
			return self.initial

	def get_context_data(self, **kwargs):
		context = super(AdTitleView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_title_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			title = self.request.POST.get("title")
			self.request.session["ad_title"] = title
			self.request.session["ad_image_yesno_token"] = uuid.uuid4()
			return redirect("ad_image_yesno")
		else:
			return redirect("home")

#'Yes' or 'No'
class AdImageYesNoView(FormView):
	form_class = AdImageYesNoForm
	template_name = "ad_image_yesno.html"

	def get_context_data(self, **kwargs):
		context = super(AdImageYesNoView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_image_yesno_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			yes = self.request.POST.get("yes",None)
			no = self.request.POST.get("no",None)
			if yes:
				self.request.session["ad_image_token"] = uuid.uuid4()
				return redirect("ad_image")
			elif no:
				self.request.session["ad_gender_token"] = uuid.uuid4()
				self.request.session["ad_image"] = None
				return redirect("ad_gender")
			else:
				return redirect("home")
		else:
			return redirect("home")

class AdImageView(CreateView):
	model = ChatPic
	form_class = AdImageForm
	template_name = "ad_image.html"

	def get_context_data(self, **kwargs):
		context = super(AdImageView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_image_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		f = form.save(commit=False)
		if f.image_file:
			try:
				on_fbs = self.request.META.get('X-IORG-FBS')
			except:
				on_fbs = False
			if on_fbs:
				if f.image_file.size > 200000:
					context = {'pk':'pk'}
					return render(self.request,'big_photo_fbs.html',context)
				else:
					pass
			else:
				if f.image_file.size > 10000000:
					context = {'pk':'pk'}
					return render(self.request,'big_photo_regular.html',context)
				else:
					pass
			image_file = clean_image_file(f.image)
			if image_file:
				f.image = image_file
			else:
				f.image = None
		if f.image_file:
			unique = uuid.uuid4()
			if self.request.user.is_authenticated():
				ad_image=ChatPic.objects.create(image=f.image, owner=request.user, times_sent=0, unique=unique)
			else:
				ad_image=ChatPic.objects.create(image=f.image, owner_id=1, times_sent=0, unique=unique)
			self.request.session["ad_image"] = ad_image.image.url
		else:
			self.request.session["ad_image"] = None
		self.request.session["ad_gender_token"] = uuid.uuid4()
		return redirect("ad_gender")

# class AdLinkURLView(FormView):
# 	form_class = AdLinkURLForm
# 	template_name = "ad_url.html"

# 	def get_context_data(self, **kwargs):
# 		context = super(AdLinkURLView, self).get_context_data(**kwargs)
# 		if valid_uuid(str(self.request.session["ad_link_url_token"])):
# 			context["authentic"] = True
# 		else:
# 			context["authentic"] = False
# 		return context

# 	def form_valid(self, form):

class AdGenderChoiceView(FormView):
	form_class = AdGenderChoiceForm
	template_name = "ad_gender.html"

	def get_context_data(self, **kwargs):
		context = super(AdGenderChoiceView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_gender_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			yes = self.request.POST.get("yes",None)
			no = self.request.POST.get("no",None)
			if yes:
				self.request.session["ad_gender"] = True
			elif no:
				self.request.session["ad_gender"] = False
			else:
				return redirect("home")
			self.request.session["ad_address_yesno_token"] = uuid.uuid4()
			return redirect("ad_address_yesno")
		else:
			return redirect("home")

#'Yes' or 'No'
class AdAddressYesNoView(FormView):
	form_class = AdAddressYesNoForm
	template_name = "ad_address_yesno.html"

	def get_context_data(self, **kwargs):
		context = super(AdAddressYesNoView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_address_yesno_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			yes = self.request.POST.get("yes",None)
			no = self.request.POST.get("no",None)
			if yes:
				self.request.session["ad_address_token"] = uuid.uuid4()
				return redirect("ad_address")
			elif no:
				self.request.session["ad_finalize_token"] = uuid.uuid4()
				return redirect("ad_finalize")
			else:
				return redirect("home")
		else:
			return redirect("home")

class AdAddressView(FormView):
	form_class = AdAddressForm
	template_name = "ad_address.html"

	def get_initial(self):#initial is a keyword argument to a formfield that enables pre-filling in the formfield
		"""
		Returns the initial data to use for forms on this view.
		"""
		user = self.request.user
		try:
			address = self.request.session["ad_address"]
			self.initial = {'address': address} #initial needs to be passed a dictionary
			return self.initial
		except:
			return self.initial

	def get_context_data(self, **kwargs):
		context = super(AdAddressView, self).get_context_data(**kwargs)
		if valid_uuid(str(self.request.session["ad_address_token"])):
			context["authentic"] = True
		else:
			context["authentic"] = False
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			address = self.request.POST.get("address")
			self.request.session["ad_address"] = address
			self.request.session["ad_finalize"] = uuid.uuid4()
			return redirect("ad_finalize")
		else:
			return redirect("home")

@ratelimit(rate='2/s')
def ad_finalize(request,*args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		context = {'unique': 'pk'}
		return render(request, 'make_ad_error.html', context)
	else:
		if valid_uuid(str(request.session["ad_finalize"])):
			description = request.session["ad_description"]
			# request.session["ad_description"] = None
			mobnum = request.session["ad_mobile_num"]
			# request.session["ad_mobile_num"] = None
			callpref = request.session["ad_call_pref"]
			# request.session["ad_call_pref"] = None
			title = request.session["ad_title"]
			# request.session["ad_title"] = None
			image = request.session["ad_image"]
			# request.session["ad_image"] = None
			address = request.session["ad_address"]
			# request.session["ad_address"] = None
			gender_based = request.session["ad_gender"]
			# request.session["ad_gender"] = None
			locations = ['0','1','2','3','4', '5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20']
			ad_url = 'http://damadam.pk/nick/ad/pin_code' # contains preview of advert that got submitted
			if request.user.is_authenticated():
				user_id = request.user.id
			else:
				user_id = None
			data = {"description":description, "phone_number":mobnum,
					"contact_preference":callpref, "title":title,
					"image_url":image,"address":address,
					"only_ladies":gender_based, "location":locations,
					"app_code":"1","user_id":user_id,"ad_url":ad_url}
			response = call_aasan_api(data,'create')
			print response.json()
			print response.text
			return HttpResponse('Ad sent to aasanads')
		else:
			return redirect("home")
###############################################################

def suspend(request, ad_id, *args, **kwargs):
	suspend_ad(str(ad_id))
	return redirect("test_ad")

class TestAdsView(FormView):
	form_class = TestAdsForm
	template_name = "test_ads.html"

	def get_context_data(self, **kwargs):
		context = super(TestAdsView, self).get_context_data(**kwargs)
		user_loc = get_user_loc(self.request.user)
		ad,ad_id, clicks = get_ad(user_loc)
		if ad and ad_id:
			context["ad"] = ad
			context["ad_id"] = ad_id
			context["title"] = ad["ti"] 
			context["description"] = ad["ds"]
			context["clicks"] = clicks
		else:
			context["ad"] = None
			context["ad_id"] = None
			context["title"] = None
			context["description"] = None
		return context

class TestReportView(FormView):
	form_class = TestReportForm
	template_name = "test_report.html"

	def get_context_data(self, **kwargs):
		context = super(TestReportView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			running,historical = get_user_ads(self.request.user.id)
		else:
			pass
		return context
		'''
		this only works for authenticated users. 
		'''

def click_ad(request, ad_id=None, *args,**kwargs):
	store_click(ad_id, get_user_loc(request.user))
	return redirect("test_ad")


###############################################################


# public.user_sessions_session_expire_date            | 3972 MB
#  public.user_sessions_session                        | 1749 MB
#  public.links_publicreply                            | 1552 MB
#  public.user_sessions_session_user_id                | 1300 MB
#  public.links_photocomment                           | 745 MB
#  public.links_publicreply_answer_to_id               | 644 MB
#  public.links_publicreply_submitted_by_id            | 614 MB
#  public.links_photoobjectsubscription_which_photo_id | 574 MB
#  public.links_link                                   | 530 MB
#  public.links_photo_latest_comment_id                | 530 MB
#  public.links_photoobjectsubscription_seen           | 492 MB
#  public.links_publicreply_pkey                       | 489 MB
#  public.links_grouptraffic_visitor_id                | 474 MB
#  public.links_grouptraffic_which_group_id            | 464 MB
#  public.links_photo_second_latest_comment_id         | 458 MB
#  public.links_photoobjectsubscription_viewer_id      | 423 MB
#  public.links_grouptraffic_pkey                      | 393 MB
#  public.links_grouptraffic_time                      | 393 MB
#  public.links_photoobjectsubscription_pkey           | 353 MB

# Report run on 12/10/2016
#              Table               |  Size   | External Size 
# ----------------------------------+---------+---------------
#  user_sessions_session            | 8204 MB | 6455 MB
#  links_publicreply                | 3622 MB | 1901 MB
#  links_photoobjectsubscription    | 2619 MB | 2250 MB
#  links_photo                      | 1814 MB | 1489 MB
#  links_grouptraffic               | 1784 MB | 1724 MB
#  links_photocomment               | 1554 MB | 742 MB
#  links_link                       | 787 MB  | 214 MB
#  links_reply                      | 542 MB  | 411 MB
#  links_groupseen                  | 454 MB  | 362 MB
#  links_vote                       | 360 MB  | 233 MB
#  links_seen                       | 351 MB  | 351 MB
#  links_salatinvite                | 311 MB  | 226 MB
#  links_groupinvite                | 164 MB  | 125 MB
#  links_photo_which_stream         | 146 MB  | 98 MB
#  links_photostream                | 139 MB  | 73 MB
#  links_userprofile                | 119 MB  | 42 MB


# Report run on 12/11/2016
#               Table               |  Size   | External Size 
# ----------------------------------+---------+---------------
#  user_sessions_session            | 8214 MB | 6464 MB
#  links_publicreply                | 3666 MB | 1923 MB
#  links_photoobjectsubscription    | 2627 MB | 2251 MB
#  links_photo                      | 1822 MB | 1497 MB
#  links_grouptraffic               | 1756 MB | 1724 MB
#  links_photocomment               | 1569 MB | 749 MB
#  links_link                       | 795 MB  | 216 MB
#  links_reply                      | 544 MB  | 413 MB
#  links_groupseen                  | 454 MB  | 362 MB
#  links_vote                       | 363 MB  | 235 MB
#  links_seen                       | 351 MB  | 351 MB
#  links_salatinvite                | 314 MB  | 228 MB
#  links_groupinvite                | 164 MB  | 125 MB
#  links_photo_which_stream         | 147 MB  | 99 MB
#  links_photostream                | 140 MB  | 74 MB
#  links_userprofile                | 119 MB  | 43 MB

# Setting up new redis instance

# sudo cp redis.conf /etc/redis/redis-2.conf
# 	Inside the conf:
# pidfile /var/run/redis/redis2-server.pid
# port 6380
# logfile /var/log/redis/redis2-server.log
# dir /var/lib/redis2
# port 0
# unixsocket /var/run/redis/redis2.sock
# unixsocketperm 775
#	Outside the conf:
#sudo mkdir /var/lib/redis2
#sudo chown -R redis:redis /var/lib/redis2
#	Create a cope of redis-server file at /etc/init.d
# change DAEMON_ARGS, NAME, DESC, and PIDFILE
# exit file and do:
# sudo chmod 755 redis2-server
# sudo update-rc.d redis2-server defaults
# sudo /etc/init.d/redis2-server start
# TO CONNECT TO REDIS CLI:
# sudo redis-cli -s /var/run/redis/redis2.sock
