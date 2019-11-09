# coding=utf-8
from pytz import timezone
from math import log, ceil
import ujson as json
from urllib import quote
from collections import OrderedDict, defaultdict
from operator import attrgetter,itemgetter
import time, datetime
from datetime import datetime, timedelta
import re, urlmarker, StringIO, urlparse, random, string, uuid, pytz, ast
from target_urls import call_aasan_api
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.decorators import method_decorator
from django.middleware import csrf
from django.core.files.uploadedfile import InMemoryUploadedFile
from scraper import read_image
from cricket_score import cricket_scr
from colors import COLOR_GRADIENTS
from page_controls import MAX_ITEMS_PER_PAGE, ITEMS_PER_PAGE, PHOTOS_PER_PAGE, FANS_PER_PAGE, STARS_PER_PAGE, PERSONAL_GROUP_IMG_WIDTH
from score import PUBLIC_GROUP_MESSAGE, PRIVATE_GROUP_MESSAGE, PUBLICREPLY, UPLOAD_PHOTO_REQ, VOTING_DRIVEN_CENSORSHIP, VOTING_DRIVEN_PIXELATION, \
NUM_SUBMISSION_ALLWD_PER_DAY, TRENDER_RANKS_TO_COUNT, SEGMENT_STARTING_USER_ID, ZODIAC, MAX_HOME_REPLY_SIZE
from django.core.cache import get_cache, cache
from django.views.decorators.csrf import csrf_protect
from django.db.models import Max, Count, Q, Sum, F
from verified import FEMALES
# from location import MEMLOC
from django.views.decorators.debug import sensitive_post_parameters
from emoticons.settings import EMOTICONS_LIST
from namaz_timings import namaz_timings, streak_alive
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, CreateView, DeleteView, FormView
from templatetags.s3 import get_s3_object
from templatetags.human_time import human_time
from image_processing import process_public_image, clean_image_file#, clean_image_file_with_hash
from salutations import SALUTATIONS
from forms import getip
from forms import UserProfileForm, DeviceHelpForm, PhotoScoreForm, BaqiPhotosHelpForm, AdFeedbackForm, PhotoTimeForm, \
ChainPhotoTutorialForm, PhotoJawabForm, PhotoReplyForm, UploadPhotoReplyForm, UploadPhotoForm, ContactForm, AboutForm, \
PrivacyPolicyForm, CaptionDecForm, CaptionForm, PhotoHelpForm, PicPasswordForm, CrossNotifForm, EmoticonsHelpForm, UserSMSForm, \
PicHelpForm, DeletePicForm, UserPhoneNumberForm, PicExpiryForm, PicsChatUploadForm, VerifiedForm, LinkForm, SmsInviteForm, \
WelcomeMessageForm, WelcomeForm, PublicreplyMiniForm, LogoutHelpForm, LogoutPenaltyForm, SmsReinviteForm, PhotoCommentForm,\
SearchNicknameForm, UserProfileDetailForm,RegisterLoginForm, ScoreHelpForm, HistoryHelpForm, BestPhotosListForm, TestAdsForm, \
UserSettingsForm, HelpForm, ReauthForm, RegisterHelpForm, VerifyHelpForm, ResetPasswordForm, PhotosListForm, UnseenActivityForm, \
AdImageForm, TopPhotoForm, SalatTutorialForm, SalatInviteForm, ExternalSalatInviteForm,ReportcommentForm, SearchAdFeedbackForm, \
PhotoShareForm, UploadVideoForm, VideoCommentForm, VideoScoreForm, FacesHelpForm, FacesPagesForm, CricketCommentForm, AdAddressForm, \
AdAddressYesNoForm, AdGenderChoiceForm, AdCallPrefForm, AdImageYesNoForm, AdDescriptionForm, AdMobileNumForm, AdTitleYesNoForm, \
AdTitleForm, AdTitleForm, TestReportForm
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from user_sessions.models import Session
#from django.utils import timezone
from django.utils.timezone import utc
from django.views.decorators.cache import cache_page, never_cache, cache_control
from brake.decorators import ratelimit
from tasks import hide_associated_direct_responses, log_404, group_attendance_tasks, publicreply_tasks, photo_upload_tasks, \
video_tasks, group_notification_tasks, publicreply_notification_tasks, fan_recount, log_user_activity, populate_search_thumbs,\
sanitize_erroneous_notif, set_input_rate_and_history, video_vote_tasks#, set_input_history
#from .html_injector import create_gibberish_punishment_text
# from .check_abuse import check_video_abuse # check_photo_abuse
from .models import Link, Cooldown, PhotoStream, TutorialFlag, PhotoVote, Photo, PhotoComment, PhotoCooldown, ChatInbox, \
ChatPic, UserProfile, ChatPicMessage, UserSettings, Publicreply, HellBanList, HotUser, UserFan, Salat, LatestSalat, SalatInvite, \
Logout, Video, VideoComment
from redis4 import get_clones, set_photo_upload_key, get_and_delete_photo_upload_key, set_text_input_key, invalidate_avurl, \
retrieve_user_id, get_most_recent_online_users, retrieve_uname, retrieve_credentials, is_potential_fan_rate_limited,\
rate_limit_unfanned_user, rate_limit_content_sharing, content_sharing_rate_limited, retrieve_avurl, get_cached_photo_dim, \
cache_photo_dim, retrieve_bulk_unames, retrieve_online_cached_data, cache_online_data, set_attribute_change_rate_limit,\
retrieve_image_count, cache_image_count#, log_public_img
from .redis3 import insert_nick_list, get_nick_likeness, find_nickname, get_search_history, select_nick, retrieve_history_with_pics,\
search_thumbs_missing, del_search_history, retrieve_thumbs, retrieve_single_thumbs, get_temp_id, save_advertiser, get_advertisers, \
purge_advertisers, get_gibberish_punishment_amount, export_advertisers, temporarily_save_user_csrf, get_banned_users_count, \
is_already_banned, is_mobile_verified, tutorial_unseen, log_pagination_button_click, set_user_choice, \
log_text_submissions #, log_erroneous_passwords
from .redis2 import remove_erroneous_notif, retrieve_unseen_activity, bulk_update_salat_notifications, viewer_salat_notifications, \
update_notification, create_notification, create_object, remove_group_notification, remove_from_photo_owner_activity, \
add_to_photo_owner_activity, retrieve_latest_notification, get_all_fans,delete_salat_notification, is_fan, bulk_is_fan,\
prev_unseen_activity_visit, SEEN, save_user_presence,get_latest_presence, retrieve_unseen_notifications, get_photo_fan_count,\
retrieve_object_data
from .redisads import get_user_loc, get_ad, store_click, get_user_ads, suspend_ad
from .website_feedback_form import AdvertiseWithUsForm
from redirection_views import return_to_content
from redis6 import invalidate_cached_mehfil_replies, save_group_submission, retrieve_latest_user_owned_mehfils, group_member_exists, \
retrieve_group_reqd_data# invalidate_cached_mehfil_pages
from redis7 import add_text_post, get_home_feed, retrieve_obj_feed, check_votes_on_objs, get_best_photo_feed, get_photo_feed, retrieve_recent_votes,\
add_image_post, insert_hash, is_fbs_user_rate_limited_from_photo_upload, retrieve_photo_feed_index, rate_limit_fbs_public_photo_uploaders, \
check_content_and_voting_ban, save_recent_photo, get_recent_photos, get_best_home_feed,retrieve_top_trenders, invalidate_cached_public_replies, \
retrieve_cached_public_replies, cache_public_replies, retrieve_top_stars, retrieve_home_feed_index, retrieve_trending_photo_ids, \
retrieve_num_trending_photos, retrieve_subscribed_topics, retrieve_photo_feed_latest_mod_time, add_topic_post, get_recent_trending_photos, \
cache_recent_trending_images, get_cached_recent_trending_images, retrieve_last_vote_time, is_image_star, get_all_image_star_ids, \
retreive_trending_rep, log_recent_text, in_defenders
from redis9 import retrieve_latest_direct_reply, get_last_comment_time
from redis8 import retrieve_variation_subset, set_tutorial_seen
from direct_response_forms import DirectResponseForm
from cities import CITY_TUP_LIST, REV_CITY_DICT

# from optimizely_config_manager import OptimizelyConfigManager
# from unconnectedreddit.optimizely_settings import PID

# config_manager = OptimizelyConfigManager(PID)

condemned = HellBanList.objects.values_list('condemned_id', flat=True).distinct()


def retrieve_user_env(user_agent, fbs):
	"""
	Checks whether environment can support JS

	Opera mini (extreme mode) and free basics do not support JS
	"""
	if fbs:
		return False#, True
	elif user_agent:
		if 'Presto' in user_agent and 'Opera Mini' in user_agent:
			return False#, False
		else:
			return True#, False
	else:
		return True#, False


def secs_to_mins(seconds):
	try:
		m, s = divmod(seconds, 60)
		h, m = divmod(m, 60)
		d, h = divmod(h, 24)
		mo, d = divmod(d, 30)
		if mo:
			if mo == 1:
				return "1 month"
			else:
				return "{} months".format(mo)
		elif d:
			if d == 1:
				return "1 day"
			else:
				return "{} days".format(d)
		elif h:
			if h == 1:
				return "1 hour"
			else:
				return "{} hours".format(h)
		elif m:
			if m == 1:
				return "1 min"
			else:
				return "{} mins".format(m)
		elif s:
			if s == 1:
				return "1 sec"
			else:
				return "{} secs".format(s)
		else:
			return ""
	except (NameError,TypeError):
		return ""


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


def get_indices(page_number, obj_allotment):
	"""
	When fed a page_number, returns a start_index and end_index
	"""
	try:
		page_number = int(page_number)
	except (ValueError,TypeError):
		return 0,obj_allotment-1
	objs_per_page = obj_allotment
	index_ceiling = objs_per_page * page_number
	return (index_ceiling)-objs_per_page,index_ceiling-1


def break_text_into_prefix_and_postfix(target_text):
	"""
	Does a reasonable effort at breaking the string along 'space' character
	"""
	STARTING_CHAR_IDX = 43
	postfix_text = target_text[STARTING_CHAR_IDX:]
	if postfix_text:
		# target string is longer than 43 chars - i.e. it's a candidate for break-up
		broken = False
		CEILING = min(len(postfix_text),4) 
		for z in xrange(STARTING_CHAR_IDX-7,STARTING_CHAR_IDX+CEILING,1):
			if target_text[z].isspace():
				# break at this point
				broken = True
				break
			else:
				# break at STARTING_CHAR_IDX
				pass
		if broken:
			prefix = target_text[:z]
			postfix = target_text[z:].strip()
			return prefix, postfix
		else:
			return target_text[:STARTING_CHAR_IDX], postfix_text
	else:
		return target_text, ''


def retrieve_trending_thumbs(user_id):
	"""
	Retreives recent trending thumbs, to be shown for the user at various places in the app
	"""
	json_data = get_cached_recent_trending_images(user_id)
	if json_data:
		return json.loads(json_data)
	else:
		trending_photo_ids = get_recent_trending_photos(user_id)
		if trending_photo_ids:
			img_ids_and_urls = Photo.objects.only('image_file').filter(id__in=trending_photo_ids).values('id','image_file')
			cache_recent_trending_images(user_id,json.dumps(img_ids_and_urls))
			return img_ids_and_urls
		else:
			return []


def create_sorted_invitee_list(username_data, user_ids):
	"""
	Prepares list of alphabetically sorted names (it's a mis-labeled function, inviting is only one of its responsibilities)

	This list is available to:
	- site-wide online listing
	- group inviters (both public and private)
	"""
	user_alpha_data = []#nicks starting with an alpha character
	user_digital_data = []#nicks starting with a digital character
	for online_id in user_ids:
		username = username_data[int(online_id)]
		username_lower = username.lower()
		if username[0].isalpha():
			user_alpha_data.append((online_id,username,username_lower))
		else:
			user_digital_data.append((online_id,username,username_lower))
	user_digital_data.sort(key=itemgetter(2))
	user_alpha_data.sort(key=itemgetter(2))
	user_data = user_alpha_data + user_digital_data
	final_data, previous_lower_username_first_alphabet = [] , ''
	for id_, uname, uname_lower in user_data:
		first_alphabet = uname_lower[0]
		new_alphabet = first_alphabet.upper() if (first_alphabet!=previous_lower_username_first_alphabet) else None
		final_data.append((id_,uname,uname_lower,new_alphabet))
		previous_lower_username_first_alphabet = first_alphabet
	return final_data


def create_sorted_online_list(username_data, user_ids_and_ages):
	"""
	"""
	if username_data and user_ids_and_ages:
		user_alpha_data = defaultdict(list)#nicks starting with an alpha character
		user_nonalpha_data = defaultdict(list)#nicks starting with other character
		for user_id, user_age in user_ids_and_ages:
			username = username_data[int(user_id)]
			username_lower = username.lower()
			first_letter = username[0]
			# rig world age such that everyone has the 'same age' (equal to -1), except when they're really new!
			if first_letter.isalpha():
				user_alpha_data[first_letter.upper()].append((user_id,username,username_lower,user_age if user_age < 5 else -1))#,user_age))
			else:
				user_nonalpha_data[first_letter].append((user_id,username,username_lower,user_age if user_age < 5 else -1))#,user_age))
		#############################
		alpha_list = [(header,users) for (header,users) in user_alpha_data.iteritems()] if user_alpha_data else []
		nonalpha_list = [(header,users) for (header,users) in user_nonalpha_data.iteritems()] if user_nonalpha_data else []
		alpha_with_sorted_elems, nonalpha_with_sorted_elems, sorted_alpha, sorted_nonalpha = [], [], [], []
		if alpha_list:
			for header, elems in alpha_list:
				alpha_with_sorted_elems.append((header,sorted(elems, key=itemgetter(3,2))))
			sorted_alpha = sorted(alpha_with_sorted_elems, key=itemgetter(0))
		if nonalpha_list:
			for header, elems in nonalpha_list:
				nonalpha_with_sorted_elems.append((header,sorted(elems, key=itemgetter(3,2))))
			sorted_nonalpha = sorted(nonalpha_with_sorted_elems, key=itemgetter(0))
		return sorted_alpha + sorted_nonalpha
	else:
		return []


def get_page_obj(page_num,obj_list,items_per_page):
	"""
	Pass list of objects and number of objects to show per page, it does the rest
	"""
	paginator = Paginator(obj_list, items_per_page)
	try:
		return paginator.page(page_num)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		return paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		return paginator.page(paginator.num_pages)


def get_addendum(index, objs_per_page, only_addendum=False):
	"""
	Creates the addendum to be attached as a URL parameter
	"""
	page = (index // objs_per_page)+1 #determining page number
	section = index+1-((page-1)*objs_per_page) #determining section numberhome_redirect
	addendum = '?page='+str(page)+"#section"+str(section) #forming url addendum
	if only_addendum:
		return addendum
	else:
		return page, addendum #returing page and addendum both


def convert_to_epoch(time):
	#time = pytz.utc.localize(time)
	return (time-datetime(1970,1,1)).total_seconds()


def get_price(points):
	"""
	Determines price of anything, in accordance to how many points a user has

	Every user can be taxed a different amount via this mechanism
	"""
	if points < 500:
		price = 400#we over-tax sybils
	elif 500 <= points < 10001:
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
	if not uuid:
		return False
	else:
		regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
		match = regex.match(uuid)
		return bool(match)


def beautiful_date(epoch_time, format_type='1'):
	"""
	Provides human readable date, beautilfully formatted

	Format type is:

	i) '10:23 AM - 30 Nov 2015'
	"""
	if format_type == '1':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%a %I:%M %p - %d %b")# gives "Sun 03:39 PM - 05 May"
	elif format_type == '2':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%Y-%m-%d %I:%M:%S %p")# gives YYYY-MM-DDThh:mm:ssTZD
	elif format_type == '3':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%I:%M %p, %a - %d %b %Y")# gives "03:39 PM, Sun - 05 May 2019"
	elif format_type == '4':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%Y-%m-%dT%I:%M:%S+05:00")# gives YYYY-MM-DDThh:mm:ss+05:00 format
	else:
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%I:%M %p %d-%m-%Y")# gives "05-05-2019 03:39 PM"


def format_post_times(list_of_dictionaries, with_machine_readable_times=False):
	"""
	Injects human readable times in place of epoch times

	"""
	if with_machine_readable_times:
		for obj in list_of_dictionaries:
			epoch_time = obj['t']
			obj['t'] = human_time(epoch_time)
			obj['mt'] = beautiful_date(epoch_time,format_type='2')
	else:
		for obj in list_of_dictionaries:
			obj['t'] = human_time(obj['t'])
	return list_of_dictionaries


# link_id, writer_username, writer_avatar_url, writer_id, link_description
def process_publicreply(request,link_id,text,origin=None,link_writer_id=None):
	try:
		parent = Link.objects.select_related('submitter__userprofile').get(id=link_id)
	except Link.DoesNotExist:
		# return a string you're sure is NOT a username
		return ";"
	if link_writer_id and int(link_writer_id) != parent.submitter_id:
		# return a string you're sure is NOT a username
		return ":"
	parent_username = parent.submitter.username
	user_id = request.user.id
	username = request.user.username
	reply = Publicreply.objects.create(description=text, answer_to=parent, submitted_by_id=user_id)
	invalidate_cached_public_replies(link_id)
	reply_time = convert_to_epoch(reply.submitted_on)
	url = retrieve_avurl(user_id)
	owner_url = retrieve_avurl(parent.submitter_id)
	amnt = update_comment_in_home_link(reply=text,writer=username,reply_id=reply.id,time=reply_time,writer_id=user_id,link_pk=link_id)
	publicreply_tasks.delay(user_id, reply.id, link_id, text, reply_time, True if username != parent_username else False, link_writer_id)
	publicreply_notification_tasks.delay(link_id=link_id,link_submitter_url=owner_url,sender_id=user_id,link_submitter_id=parent.submitter_id,\
		link_submitter_username=parent_username,link_desc=parent.description,reply_time=reply_time,reply_poster_url=url,reply_count=amnt,\
		reply_poster_username=username,reply_desc=text,is_welc=False,priority='home_jawab',from_unseen=(True if origin == 'from_unseen' else False))
	return parent_username

	
def GetLatest(user):
	"""
	Get latest notification that is to appear in the single-notif box
	"""
	notif_name, hash_name, latest_notif = retrieve_latest_notification(user.id)
	try:
		if latest_notif['ot'] == '3':
			# group chat - 'g' is privacy status
			return latest_notif['g'], latest_notif, False, False, True, False, False
		elif latest_notif['ot'] == '5':
			return  '5', latest_notif, False, False, False, False, True
		elif latest_notif['ot'] == '2':
			#home publicreply
			return '2', latest_notif, True, False, False, False, False
		elif latest_notif['ot'] == '0':
			#photo comment
			if latest_notif.get('f'):
				if latest_notif['nc'] == 'True':
					# photo notif for fans
					return '1', latest_notif, False, True, False, False, False
				else:
					# photo comment received by fan
					return '0', latest_notif, False, True, False, False, False  
			else:
				# photo comment received by non-fan
				return '0', latest_notif, False, True, False, False, False
		elif latest_notif['ot'] == '4':
			# salat invites
			delete_salat_notification(notif_name, hash_name, user.id)
			return None, None, False, False, False, False, False
			# time_now = datetime.utcnow()+timedelta(hours=5)
			# cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			# 	'LOCATION': MEMLOC, 'TIMEOUT': 70,
			# })
			# salat_timings = cache_mem.get('salat_timings')
			# if not salat_timings['namaz']:
			# 	#time for namaz has gone
			# 	delete_salat_notification(notif_name, hash_name, user.id)
			# 	return None, None, False, False, False, False, False
			# else:
			# 	starting_time = datetime.combine(time_now.today(), salat_timings['current_namaz_start_time'])
			# 	ending_time = datetime.combine(time_now.today(), salat_timings['current_namaz_end_time'])
			# 	try:
			# 		latest_namaz = LatestSalat.objects.filter(salatee=user).latest('when')
			# 	except:
			# 		#latest_namaz does not exist
			# 		latest_namaz = None
			# 	if (convert_to_epoch(starting_time) <= float(latest_notif['u']) < convert_to_epoch(ending_time)) and not \
			# 	AlreadyPrayed(latest_namaz,time_now):
			# 		return '4',latest_notif, False, False, False, True, False
			# 	else:
			# 		delete_salat_notification(notif_name, hash_name, user.id)           
			# 		return None, None, False, False, False, False, False
	except (KeyError,TypeError):
		if latest_notif and notif_name:
			sanitize_erroneous_notif.delay(notif_name, user.id)
		return None, None, False, False, False, False, False


def csrf_failure(request, reason=""):
	context = {'referrer':request.META.get('HTTP_REFERER',None)}
	return render(request,"CSRF_failure.html", context)


class NeverCacheMixin(object):
	@method_decorator(never_cache)
	def dispatch(self, *args, **kwargs):
		return super(NeverCacheMixin, self).dispatch(*args, **kwargs)

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


class ScoreHelpView(FormView):
	form_class = ScoreHelpForm
	template_name = "score_help.html"


def star_list(request, *args, **kwargs):
	"""
	Renders the list of users the given user is a fan of
	"""
	context = {}
	pk = request.user.id
	ids = UserFan.objects.filter(fan_id=pk).values_list('star_id',flat=True).order_by('-fanning_time')
	if ids:
		page_num = request.GET.get('page', '1')
		page_obj = get_page_obj(page_num,ids,STARS_PER_PAGE)
		users_qset = User.objects.filter(id__in=page_obj.object_list).values('id','username','userprofile__score','userprofile__avatar').annotate(photo_count=Count('photo', distinct=True))
		users = {x['id']:x for x in users_qset}
		users_with_photo_counts = [users[id] for id in page_obj.object_list]
		context["page_obj"] = page_obj
		users_with_photo_thumbs = retrieve_thumbs(users_with_photo_counts)
		context["users"] = users_with_photo_thumbs
		context["stars"] = get_all_image_star_ids()
	else:
		context["page_obj"] = None
		context["users"] = []
		context["fan"] = User.objects.get(id=pk)
	################### Retention activity logging ###################
	if pk > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'Z7' if request.mobile_verified else 'Z7.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=pk, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,"star_list.html",context)


def fan_list(request, pk=None, *args, **kwargs):
	"""
	Renders the fan list of a given user
	"""
	page_num = request.GET.get('page', '1')
	all_fan_ids, total_count, new_fan_ids_and_count = get_all_fans(pk)
	new_fan_ids = new_fan_ids_and_count[0]
	new_count = new_fan_ids_and_count[1]
	star = User.objects.get(id=pk)
	existing_users = [(id,False) for id in all_fan_ids if id not in set(new_fan_ids)]
	new_users = [(id,True) for id in new_fan_ids]
	all_users = new_users + existing_users
	################### Retention activity logging ###################
	own_id = request.user.id
	if own_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'Z6' if request.mobile_verified else 'Z6.u'
		activity_dict = {'m':'GET','act':act,'t':time_now,'tuid':pk}# defines what activity just took place
		log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	if all_users:
		page_obj = get_page_obj(page_num,all_users,FANS_PER_PAGE)
		fan_dict = User.objects.select_related('userprofile').in_bulk(map(itemgetter(0),page_obj.object_list))
		fans = []
		for (user_id,is_new) in page_obj.object_list:
			fans.append((fan_dict[int(user_id)],is_new))
		return render(request,"fan_list.html",{'fans':fans,'star':star, 'count':total_count,'page_obj':page_obj,'girls':FEMALES,'new_count':new_count})
	else:
		return render(request,"fan_list.html",{'fans':None,'star':star, 'count':total_count})


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

class RegisterLoginView(FormView):
	form_class = RegisterLoginForm
	template_name = "register_login.html"

	# def get_context_data(self, **kwargs):
	#   context = super(RegisterLoginView, self).get_context_data(**kwargs)
	#   mp.track(self.request.session.get('new_id',None), 'inside_register_login')
	#   return context


def website_rules(request):
	"""
	Renders website rules
	"""
	################### Retention activity logging ###################
	user_id = request.user.id
	if user_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'Z2' if request.mobile_verified else 'Z2.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,"website_rules.html",{})

class ContactView(FormView):
	form_class = ContactForm
	template_name = "contact.html"

class AboutView(FormView):
	form_class = AboutForm
	template_name = "about.html"

	def get_context_data(self, **kwargs):
		context = super(AboutView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			################### Retention activity logging ###################
			user_id = self.request.user.id
			if user_id > SEGMENT_STARTING_USER_ID:
				time_now = time.time()
				act = 'Z3' if self.request.mobile_verified else 'Z3.u'
				activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			##################################################################
		return context

class PrivacyPolicyView(FormView):
	form_class = PrivacyPolicyForm
	template_name = "privacy_policy.html"


class HelpView(FormView):
	form_class = HelpForm
	template_name = "help.html"

	def get_context_data(self, **kwargs):
		context = super(HelpView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			################### Retention activity logging ###################
			user_id = self.request.user.id
			if user_id > SEGMENT_STARTING_USER_ID:
				time_now = time.time()
				act = 'Z1' if self.request.mobile_verified else 'Z1.u'
				activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			##################################################################
		return context

class VerifyHelpView(FormView):
	form_class = VerifyHelpForm
	template_name = "verify_help.html"  

class RegisterHelpView(FormView):
	form_class = RegisterHelpForm
	template_name = "register_help.html"


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def logout_rules(request):
	if request.method == "POST":
		return render(request,"logout/logout_rules.html",{})
	else:
		return render(request,"logout/logout_tutorial.html",{})


class LogoutPenaltyView(FormView):
	form_class = LogoutPenaltyForm
	template_name = "logout_penalty.html"


def faces_pages(request, *args, **kwargs):
	form = FacesPagesForm()
	oblist = EMOTICONS_LIST
	page_num = request.GET.get('page', '1')
	page_obj = get_page_obj(page_num,oblist,16)
	context = {'object_list': oblist, 'form':form, 'page':page_obj}
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

class SalatRankingView(ListView):
	template_name = "salat_ranking.html"
	model = LatestSalat
	paginate_by = 50

	def get_queryset(self):
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


@csrf_protect
def hide_comment(request,comment_id,photo_id,origin,*args,**kwargs):
	"""
	Processing hiding a 'tabsra' of a photo post
	"""
	if getattr(request, 'limits', False):
		raise Http404("Cannot hide comment")
	elif request.method == "POST":
		slug = request.POST.get("slug",None)
		own_id = request.user.id
		if PhotoComment.objects.filter(pk=comment_id,which_photo_id=photo_id,abuse=False).exists() and \
		Photo.objects.filter(pk=photo_id,owner_id=own_id).exists():
			photocomment_obj = PhotoComment.objects.only('submitted_by','direct_reply').get(id=comment_id)
			submitted_by_id = photocomment_obj.submitted_by_id
			
			# mark as abusive
			PhotoComment.objects.filter(pk=comment_id).update(abuse=True)

			################################################
			# handle direct replies
			direct_reply_id = photocomment_obj.direct_reply_id
			if direct_reply_id:
				target_user_id = PhotoComment.objects.only('submitted_by').get(id=direct_reply_id).submitted_by_id
			else:
				target_user_id = None if submitted_by_id == own_id else own_id# there's no target_user_id if response targeted at self (else self is the target)

			hide_associated_direct_responses.delay(obj_type='4',parent_obj_id=photo_id,reply_id=comment_id,\
				sender_id=submitted_by_id,receiver_id=target_user_id,to_hide=True)
			################################################
			
		# prepare to redirect
		if slug and slug != 'None':
			return redirect("comment_pk", pk=photo_id, origin=origin, ident=slug)
		else:
			return redirect("comment_pk", pk=photo_id, origin=origin)
	else:
		raise Http404("Not a POST request")



@csrf_protect
def hide_jawab(request,publicreply_id,link_id,*args,**kwargs):
	"""
	Processing hiding a 'jawab' of a home post
	"""
	if request.method == "POST":
		own_id = request.user.id
		if Publicreply.objects.filter(pk=publicreply_id,answer_to_id=link_id,abuse=False).exists() and \
		Link.objects.filter(pk=link_id,submitter_id=own_id).exists():
			publicreply_obj = Publicreply.objects.only('submitted_by','direct_reply').get(id=publicreply_id)
			submitted_by_id = publicreply_obj.submitted_by_id

			# mark as abusive
			Publicreply.objects.filter(pk=publicreply_id).update(abuse=True)

			################################################
			# handle direct replies
			direct_reply_id = publicreply_obj.direct_reply_id
			if direct_reply_id:
				target_user_id = Publicreply.objects.only('submitted_by').get(id=direct_reply_id).submitted_by_id
			else:	
				target_user_id = None if submitted_by_id == own_id else own_id# there's no target_user_id if response targeted at self (else self is the target)

			hide_associated_direct_responses.delay(obj_type='3',parent_obj_id=link_id,reply_id=publicreply_id,\
				sender_id=submitted_by_id,receiver_id=target_user_id,to_hide=True)
			################################################

			# invalidate cached replies
			invalidate_cached_public_replies(link_id)
		
		return redirect("publicreply_view",link_id)
	else:
		raise Http404("Not a POST request - cannot hide publicreply")


def display_link_detail(request, link_id):
	"""
	Displays a given Link object in a separate page
	Useful for defender who've banned a 'link' and consequently it's been censored
	"""
	try:
		obj = Link.objects.get(id=link_id)
	except Link.DoesNotExist:
		obj = None
	own_id = request.user.id
	if obj.submitter_id == own_id or in_defenders(own_id):
		pass
	else:
		# do NOT show this detail page to unrelated users
		obj = None
	if obj:
		return render(request,"link_detail.html",{'obj':obj})
	else:
		raise Http404("Object not found")


class PhotoDetailView(DetailView):
	model = Photo
	template_name = "photo_detail.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoDetailView, self).get_context_data(**kwargs)
		context["can_vote"] = False
		context["authenticated"] = False
		pk = self.kwargs.get("pk",None)
		try:
			photo = Photo.objects.get(id=pk)
			context["photo_id"] = pk
			context["photo"] = photo
			context["own_photo"] = False
			img_height, img_width = get_cached_photo_dim(pk)
			if not img_height:
				img_height, img_width = photo.image_file.height, photo.image_file.width
				cache_photo_dim(pk,img_height,img_width)
			context["photo_width"] = img_width
			context["photo_height"] = img_height
		except:
			context["absent"] = True
			return context
		try:
			context["av_url"] = photo.owner.userprofile.avatar.url
		except:
			context["av_url"] = None
		on_fbs = self.request.META.get('HTTP_X_IORG_FBS',False)
		context["is_js_env"] = False
		if on_fbs:
			context["show_copy_prompt"] = True
			context["regular_url"] = "https://damadam.pk"+reverse('photo_detail',kwargs={"pk": pk})
		else:
			is_js_env = retrieve_user_env(user_agent=self.request.META.get('HTTP_USER_AGENT',None), fbs = on_fbs)
			if is_js_env:
				context["is_js_env"] = True
				context["on_opera"] = False
			else:
				context["on_opera"] = True
		context["defender"] = False
		context["is_star"] = is_image_star(user_id=photo.owner_id)
		context["oun"] = retrieve_uname(photo.owner_id,decode=True)
		context["from_cull_queue"] = False
		context["latest_photocomments"] = None
		context["other_photos"] = Photo.objects.filter(owner=photo.owner).exclude(id=pk).order_by('-id').values('image_file','caption','id')[:10] #list of dictionaries
		if self.request.is_feature_phone or self.request.is_phone or self.request.is_mobile:
			context["is_mob"] = True
		if self.request.user.is_authenticated():
			origin = self.kwargs.get("origin",None)
			if origin == '6':
				context["from_cull_queue"] = True
				context["latest_photocomments"] = PhotoComment.objects.select_related('submitted_by').filter(which_photo_id=pk).order_by('-id')[:25]
			context["authenticated"] = True
			if in_defenders(self.request.user.id):
				context["defender"] = True
			if self.request.user == photo.owner:
				context["own_photo"] = True
			################### Retention activity logging ###################
			user_id = self.request.user.id
			if user_id > SEGMENT_STARTING_USER_ID:
				time_now = time.time()
				act = 'Z8' if self.request.mobile_verified else 'Z8.u'
				activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			##################################################################
		return context


############################################################################################################################################################


# @ratelimit(rate='3/s')
# @ratelimit(field='user_id',ip=False,rate='22/38s')
# @ratelimit(field='user_id',ip=False,rate='4/s')
# @csrf_protect
# def home_reply(request,pk=None,*args,**kwargs):
# 	"""
# 	Processes replying to a piece of content from directly underneath it
# 	"""
# 	if request.user_banned:
# 		return redirect("error")
# 	else:
# 		user_id = request.user.id
# 		ipp = ITEMS_PER_PAGE#MAX_ITEMS_PER_PAGE if lang == 'urdu' else ITEMS_PER_PAGE
# 		sort_by_best = False#True if request.POST.get("sort_by",None) == 'best' else False
# 		origin = '3'# pre-setting origin to '3' (to handle the GET request scenario)
# 		notif = "tx:"+pk# appending tx: to pk to match object names in homefeed
# 		if request.method == 'POST':
# 			origin = request.POST.get("origin",'3')
# 			banned, time_remaining, ban_details = check_content_and_voting_ban(user_id, with_details=True)
# 			if banned:
# 				# Cannot submit home_reply if banned
# 				return render(request, 'judgement/cannot_comment.html', {'time_remaining': time_remaining,'ban_details':ban_details,\
# 					'forbidden':True,'own_profile':True,'defender':None,'is_profile_banned':True, 'org':origin,'obid':pk,'lid':notif})
# 			else:
# 				link_writer_id = request.POST.get("lwpk",None)
# 				topic = request.POST.get("tp",None)
# 				if topic:
# 					request.session["origin_topic"] = topic
# 				banned_by, ban_time = is_already_banned(own_id=user_id,target_id=link_writer_id, return_banner=True)
# 				if banned_by:
# 					request.session["banned_by"] = banned_by
# 					request.session["ban_time"] = ban_time
# 					request.session["where_from"] = origin
# 					request.session["obj_id"] = pk
# 					request.session["lid"] = notif
# 					request.session.modified = True
# 					return redirect("ban_underway")
# 				else:
# 					is_verified = request.mobile_verified
# 					time_now = time.time()
# 					form = PublicreplyMiniForm(data=request.POST,user_id=user_id,link_id=pk,mob_verified=is_verified)
# 					if form.is_valid():
# 						text = form.cleaned_data.get("description")
# 						set_input_rate_and_history.delay(section='home_rep',section_id=pk,text=text,user_id=user_id,time_now=time_now)
# 						target = process_publicreply(request=request,link_id=pk,text=text,link_writer_id=link_writer_id)# target is target_username
# 						request.session['home_hash_id'] = notif
# 						################### Retention activity logging ###################
# 						if user_id > SEGMENT_STARTING_USER_ID:
# 							sub_categ = '3' if origin == '3' else '4'# inline home tabsra or inline topic tabsra
# 							parent_text = Link.objects.only('description').get(id=pk).description
# 							activity_dict = {'m':'POST','act':'I'+sub_categ,'t':time_now,'tx':text,'pc':parent_text}# defines what activity just took place
# 							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
# 						##################################################################
# 						if target == ":":
# 							return redirect("ban_underway")
# 						elif target == ';':
# 							remove_erroneous_notif(notif_name="np:"+str(own_id)+":2:"+str(pk), user_id=user_id)
# 							return render(request,"object_deleted.html",{})
# 						else:
# 							return return_to_content(request,origin,pk,notif)
# 					else:
# 						################### Retention activity logging ###################
# 						if user_id > SEGMENT_STARTING_USER_ID:
# 							sub_categ = '3' if origin == '3' else '4'# inline home tabsra or inline topic tabsra
# 							request.session['rd'] = '1'
# 							parent_text = Link.objects.only('description').get(id=pk).description
# 							if not is_verified: 
# 								activity_dict = {'m':'POST','act':'I'+sub_categ+'.u','t':time_now,'tx':request.POST.get('description',None),\
# 								'pc':parent_text}# defines what activity just took place
# 							else:
# 								activity_dict = {'m':'POST','act':'I'+sub_categ+'.i','t':time_now,'tx':request.POST.get('description',None),\
# 								'pc':parent_text}# defines what activity just took place
# 							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
# 						##################################################################
# 						#redirecting to error display position on the page
# 						error_string = form.errors.as_text().split("*")[2]
# 						if origin == '3':
# 							request.session['home_direct_reply_error_string'] = error_string
# 							url = reverse_lazy("home")+'?page=1#error'
# 						else:
# 							request.session['topic_direct_reply_error_string'] = error_string
# 							url = reverse_lazy("topic_page",args=[topic])+'?page=1#error'
# 						return redirect(url)
# 		else:
# 			request.session['home_hash_id'] = notif
# 			return return_to_content(request,origin,pk,notif)


def best_home_page(request):
	"""
	Displays the 'best' home page
	"""
	# if request.user.is_authenticated():
	context = {}
	context["authenticated"] = True
	own_id, page_num = request.user.id, request.GET.get('page', '1')
	start_index, end_index = get_indices(page_num, ITEMS_PER_PAGE)
	############
	obj_list = get_best_home_feed(start_idx=start_index, end_idx=end_index)# has to be written
	############
	list_of_dictionaries = retrieve_obj_feed(obj_list)
	list_of_dictionaries = format_post_times(list_of_dictionaries, with_machine_readable_times=True)
	context["link_list"] = list_of_dictionaries
	context["fanned"] = []#bulk_is_fan(set(str(obj['si']) for obj in list_of_dictionaries),own_id)
	#######################
	replyforms = {}
	for obj in list_of_dictionaries:
		replyforms[obj['h']] = PublicreplyMiniForm() #passing home_hash to forms dictionary
	context["replyforms"] = replyforms
	#######################
	context["on_fbs"] = request.META.get('HTTP_X_IORG_FBS',False)
	num = random.randint(1,4)
	context["random"] = num #determines which message to show at header
	context["newest_user"] = User.objects.latest('id') if num > 2 else None
	# context["score"] = request.user.userprofile.score #own score
	secret_key = str(uuid.uuid4())
	# context["sk"] = secret_key
	# set_text_input_key(user_id=own_id, obj_id='1', obj_type='home', secret_key=secret_key)
	context["can_vote"] = True #allowing user to vote
	context["process_notification"] = False
	context["ident"] = own_id
	return render(request, 'link_list.html', context)


def home_redirect(request, pk=None):
	"""
	Used to redirect to specific spot on home (e.g. after writing or 'liking' something)
	"""
	if pk:
		index = retrieve_home_feed_index(pk)
	else:
		pk = request.session.pop('home_hash_id',None)
		index = retrieve_home_feed_index(pk) if pk else 0
	if index is None:
		url = reverse_lazy("home")+'?page=1#section0'
	else:
		addendum = get_addendum(index,ITEMS_PER_PAGE, only_addendum=True)
		url = reverse_lazy("home")+addendum
	############################################
	############################################
	request.session['rd'] = '1'#used by retention activity loggers in home_page() - remove whenever
	############################################
	############################################
	return redirect(url)


def home_page(request, lang=None):
	"""
	Displays the home page
	"""
	own_id, page_num = request.user.id, request.GET.get('page', '1')
	start_index, end_index = get_indices(page_num, ITEMS_PER_PAGE)
	obj_list, list_total_size = get_home_feed(start_idx=start_index, end_idx=end_index, with_feed_size=True)
	num_pages = list_total_size/ITEMS_PER_PAGE
	max_pages = num_pages if list_total_size % ITEMS_PER_PAGE == 0 else (num_pages+1)
	page_num = int(page_num)
	list_of_dictionaries = retrieve_obj_feed(obj_list, with_colors=True)
	#######################
	# must be done in this line, since the 't' information is lost subsequently
	try:
		oldest_post_time = list_of_dictionaries[-1]['t']
	except:
		oldest_post_time = 0.0
	#######################
	list_of_dictionaries = format_post_times(list_of_dictionaries, with_machine_readable_times=True)
	# replyforms = {}
	# for obj in list_of_dictionaries:
	# 	replyforms[obj['h']] = PublicreplyMiniForm() #passing home_hash to forms dictionary
	#######################
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	is_js_env = retrieve_user_env(user_agent=request.META.get('HTTP_USER_AGENT',None), fbs = on_fbs)
	on_opera = True if (not on_fbs and not is_js_env) else False
	num = random.randint(1,4)
	secret_key = str(uuid.uuid4())
	set_text_input_key(user_id=own_id, obj_id='1', obj_type='home', secret_key=secret_key)
	#######################
	# enrich objs with information that 'own_id' liked them or not
	if retrieve_last_vote_time(voter_id=own_id) > oldest_post_time:
		recent_user_votes = retrieve_recent_votes(voter_id=own_id, oldest_post_time=oldest_post_time)
		# payload in recent_user_votes is voter_id+":"+target_user_id+":"+vote_value+":"+obj_type+":"+target_obj_id
		recent_user_voted_obj_hashes = set(obj.split(":",3)[-1] for obj in recent_user_votes)
		for obj in list_of_dictionaries:
			if obj['h'] in recent_user_voted_obj_hashes:
				obj['v'] = True# user 'liked' this particular object, so mark it

	is_mob_verified = request.mobile_verified

	###################### Retention activity logging ######################
	from_redirect = request.session.pop('rd',None)# remove this too when removing retention activity logger
	if not from_redirect and own_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'H' if page_num == 1 else 'H2'
		act = act if is_mob_verified else act+'.u'
		activity_dict = {'m':'GET','act':act,'t':time_now,'pg':page_num}# defines what activity just took place
		log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
	########################################################################

	context = {'link_list':list_of_dictionaries,'fanned':bulk_is_fan(set(str(obj['si']) for obj in list_of_dictionaries),own_id),\
	'is_auth':True,'on_fbs':on_fbs,'ident':own_id,'newest_user':User.objects.only('username').latest('id') if num > 2 else None,\
	'mobile_verified':is_mob_verified,'random':num, 'sk':secret_key,'newbie_lang':request.session.get("newbie_lang",None),\
	'on_opera':on_opera,'dir_rep_form':DirectResponseForm(with_id=True),'thin_rep_form':DirectResponseForm(thin_strip=True),\
	'latest_dir_rep':retrieve_latest_direct_reply(user_id=own_id),'single_notif_dir_rep_form':DirectResponseForm()}#'process_notification':False,

	context["page"] = {'number':page_num,'has_previous':True if page_num>1 else False,'has_next':True if page_num<max_pages else False,\
	'previous_page_number':page_num-1,'next_page_number':page_num+1}
	
	newbie_flag = request.session.get("newbie_flag",None)
	if newbie_flag:
		context["newbie_flag"] = newbie_flag
		if newbie_flag in ('1','2','3','5','6','7'):
			if newbie_flag == '5':
				context["newbie_tutorial_page"] = 'tutorial5b.html'
			elif newbie_flag == '6':
				context["newbie_tutorial_page"] = 'tutorial6b.html'
			elif newbie_flag == '7':
				context["newbie_tutorial_page"] = 'tutorial7c.html'
			else:
				context["newbie_tutorial_page"] = 'tutorial'+newbie_flag+'.html'
		else:
			context["newbie_tutorial_page"] = 'newbie_rules.html'
	# extraneous
	context["lang"] = 'None'
	context["sort_by"] = 'recent'
	context["max_home_reply_size"] = MAX_HOME_REPLY_SIZE
	#####################
	# context["single_notif_error"] = request.session.pop("single_notif_error",None)
	# if not request.user_banned:
		# context["process_notification"] = True
	context["dir_rep_invalid"] = request.session.pop("dir_rep_invalid"+str(own_id),None)
	return render(request, 'link_list.html', context)


##############################################################################################################################
##############################################################################################################################

def turn_off_newbie(request,origin):
	"""
	Turn off newbie flag so that the tutorial can disappear

	Origin must match that which is defined in return_to_content()
	"""
	request.session.pop("newbie_flag",None)
	if origin == '3':
		return redirect("home")
	elif origin == '2':
		return redirect("photo",list_type='best-list')
	elif origin == '1':
		return redirect("photo",list_type='fresh-list')
	elif origin == '26':
		return redirect('get_ranked_groups')
	elif origin == '27':
		return redirect('topic_listing')
	else:
		return redirect("home")

def new_user_gateway(request,lang=None,*args,**kwargs):
	# set necessary newbie_flags for other parts of damadam too (e.g. for matka: is mein woh sab batien likhi aa jatien hain jin mein tum ne hissa liya (maslan jawab, tabsrey, waghera))
	request.session["newbie_flag"] = True
	request.session.modified = True
	return redirect("first_time_choice", lang=lang)


def first_time_choice(request,lang=None, *args, **kwargs):
	user_id = request.user.id
	if request.method == 'POST':
		request.session["newbie_lang"] = lang if lang else 'eng'
		# new 4-pronged onboarding funnel
		choice = request.POST.get("choice",None)
		if choice in ('1','2','3','4'):
			if choice in ('2','3','4'):
				# these particular variations have subsets too
				choice = retrieve_variation_subset(user_id, choice)
			request.session["newbie_flag"] = choice
			if user_id > SEGMENT_STARTING_USER_ID:
				time_now = time.time()
				request.session['rd'] = '1'
				activity_dict = {'m':'POST','act':'V'+choice,'t':time_now}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now, which_var='var'+choice)
			############################################
			############################################
			if choice == '5':
				return redirect("get_ranked_groups")
			elif choice == '6':
				return redirect("topic_listing")
			elif choice == '7':
				return redirect(reverse_lazy("photo", args=['best-list']))
			else:
				return redirect("home")
		else:
			request.session["redo_tut_selection"+str(user_id)] = '1'
			return redirect("first_time_choice",lang)
	else:
		# new 4-pronged onboarding funnel
		no_choice_selected = True if request.session.pop("redo_tut_selection"+str(user_id),None) == '1' else False
		if lang == 'ur':
			return render(request,"unauth/ftue_choices_ur.html",{'no_choice_selected':no_choice_selected})
		else:
			return render(request,"unauth/ftue_choices.html",{'no_choice_selected':no_choice_selected})


##############################################################################################################################
##############################################################################################################################


def show_online_users(request):
	"""
	Displays online users, sorted by world age, enriched by anchor tags for fast jumping between alphabets
	"""
	cached_data = retrieve_online_cached_data()
	if cached_data:
		try:
			data = json.loads(cached_data)
		except:
			import json as json_backup
			data = json_backup.loads(cached_data)
		final_data, num_online = data['final_data'], data['num_online']
	else:
		user_ids_and_ages = get_most_recent_online_users(with_ages=True)
		if user_ids_and_ages:
			user_ids = [user_id for user_id, user_age in user_ids_and_ages]
			username_data = retrieve_bulk_unames(user_ids, decode=True)
			final_data = create_sorted_online_list(username_data, user_ids_and_ages)
			num_online = len(user_ids)
			cache_online_data(json.dumps({'final_data':final_data,'num_online':num_online}))
		else:
			final_data, num_online = [], 0
	own_id = request.user.id
	################### Retention activity logging ###################
	if own_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'O' if request.mobile_verified else 'O.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,"online_list.html",{'online_data':final_data,'stars':get_all_image_star_ids(), 'num_online':num_online,\
		'own_id':own_id,'bottom':len(final_data),'on_fbs':request.META.get('HTTP_X_IORG_FBS',False)})


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
		return redirect("profile_photos_redirect",slug,'fotos')
		# return redirect("profile", slug, 'fotos')
	else:
		try:
			return redirect("profile", slug, 'fotos')
		except:
			return redirect("profile", request.user.username, 'fotos')


def user_profile_photos_redirect(request, slug, list_type):
	"""
	Used to redirect to specific spot on user_profile_photos (e.g. after returning from viewing own 'likes')
	"""
	own_id = request.user.id
	target_id = request.session.pop("photograph_id",None)
	if target_id:
		owner_id = retrieve_user_id(slug)
		PICS_PER_PAGE = 10
		obj_id_list = Photo.objects.only('id').filter(owner_id=owner_id,category='1').order_by('-id').values_list('id',flat=True)
		if obj_id_list:
			try:
				index = list(obj_id_list).index(int(target_id))
			except:
				index = 0
			addendum = get_addendum(index,PICS_PER_PAGE, only_addendum=True)
			url = reverse_lazy("profile",kwargs={'slug':slug,"type": list_type})+addendum
		else:
			url = reverse_lazy("profile",kwargs={'slug':slug,"type": list_type})+'?page=1#section0'
	else:
		url = reverse_lazy("profile",kwargs={'slug':slug,"type": list_type})+'?page=1#section0'
	############################################
	############################################
	if own_id:
		request.session['rd'] = '1'#used by retention activity loggers in home_page() - remove whenever
	############################################
	############################################
	return redirect(url)


def user_profile_photos(request,slug,type):
	"""
	Renders a user's photo page
	"""
	context = {}
	page_num = request.GET.get('page', '1')
	username, list_type = slug, type
	if username and list_type in ('fotos','trending-fotos'):
		target_id = retrieve_user_id(username)
		if target_id:
			PICS_PER_PAGE = 10
			start_index, end_index = get_indices(page_num, PICS_PER_PAGE)# showing 10 items per page
			if list_type == 'fotos':
				# retrieve latest images uploaded by the user
				obj_list = Photo.objects.only('id','caption','image_file','vote_score','upload_time','comment_count','device').filter(owner_id=target_id,\
					category='1').order_by('-id')[start_index:end_index+1]
				list_total_size = Photo.objects.filter(owner_id=target_id,category='1').count()
			else:
				# retrieve past week's trending images
				photo_ids = retrieve_trending_photo_ids(target_id)
				if photo_ids:
					obj_list = Photo.objects.only('id','caption','image_file','vote_score','upload_time','comment_count').filter(id__in=photo_ids).\
					order_by('-id')[start_index:end_index+1]
					list_total_size = len(photo_ids)
					num_pages = list_total_size/PICS_PER_PAGE
				else:
					obj_list = []
					list_total_size = 0
				
			num_pages = list_total_size/PICS_PER_PAGE
			max_pages = num_pages if list_total_size % PICS_PER_PAGE == 0 else (num_pages+1)
			page_num = int(page_num)
			context['object_list'] = obj_list
		else:
			log_404.delay(type_of_404='1b',time_of_404=time.time())
			raise Http404("This user does not exist")
	else:
		log_404.delay(type_of_404='1a',time_of_404=time.time())
		raise Http404("No username provided or malformed type")
	###############################################################
	try:
		subject = User.objects.only('date_joined').get(id=target_id)
	except User.DoesNotExist:
		log_404.delay(type_of_404='1c',time_of_404=time.time())
		raise Http404("User ID does not compute")
	if list_type == 'trending-fotos':
		context["is_trending"] = True
	context["slug"] = username
	context["is_star"] = is_image_star(user_id=target_id)
	star_id = target_id
	context["num_trending"] = retrieve_num_trending_photos(star_id)
	if request.user:
		user_id = request.user.id
		context["user_id"] = user_id
		context["origin"] = '4'#helps redirect back to this page if a user enters the "report" funnel
		context["authenticated"] = True
		is_defender, is_super_defender = in_defenders(user_id, return_super_status=True)
		if is_super_defender:
			context["manageable"] = True
		own_profile = star_id == user_id
		context["own_profile"] = own_profile
		if not own_profile:
			# someone else's profile AND user is logged in
			context["subject_id"] = star_id
			if is_fan(star_id, user_id):
				context["not_fan"] = False
				context["fanned"] = [str(star_id)]
			else:
				context["not_fan"] = True
				context["fanned"] = []#[] must be passed, otherwise code fails
	else:
		user_id = None
		is_defender = False
		own_profile = False
		context["authenticated"] = False
		context["not_fan"] = True
		context["own_profile"] = False
	context["mobile_verified"] = request.mobile_verified if own_profile else is_mobile_verified(star_id)
	###########
	banned, time_remaining, ban_details = check_content_and_voting_ban(star_id, with_details=True)
	context["ban_detail"] = ban_details
	context["is_profile_banned"] = banned
	context["noindex"] = True if (banned or not context["mobile_verified"]) else False
	context["defender"] = is_defender
	context["time_remaining"] = time_remaining
	###########
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	is_js_env = retrieve_user_env(user_agent=request.META.get('HTTP_USER_AGENT',None), fbs = on_fbs)
	context["on_opera"] = True if (not on_fbs and not is_js_env) else False
	###########
	context["subject"] = subject
	context["star_id"] = star_id
	context["star_av_url"] = retrieve_avurl(star_id)
	total_fans, recent_fans = get_photo_fan_count(star_id)
	if random.random() < 0.33 and context["object_list"] and search_thumbs_missing(star_id):
		ids_with_urls = [(photo.id,photo.image_file.url) for photo in context["object_list"][:5]]
		populate_search_thumbs.delay(star_id,ids_with_urls)
	context["page_obj"] = {'number':page_num,'has_previous':True if page_num>1 else False,'has_next':True if page_num<max_pages else False,\
	'previous_page_number':page_num-1,'next_page_number':page_num+1}
	################### Retention activity logging ###################
	if user_id:
		from_redirect = request.session.pop('rd',None)# remove this too when removing retention activity logger
		if not from_redirect and user_id > SEGMENT_STARTING_USER_ID:
			time_now = time.time()
			if list_type == 'trending-fotos':
				if own_profile:
					act = 'A4' if request.mobile_verified else 'A4.u'
				else:
					act = 'A8' if request.mobile_verified else 'A8.u'
			else:
				if own_profile:
					act = 'A3' if request.mobile_verified else 'A3.u'
				else:
					act = 'A7' if request.mobile_verified else 'A7.u'
			activity_dict = {'m':'GET','act':act,'t':time_now,'tuid':star_id,'pg':page_num}# defines what activity just took place
			log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,"user_detail1.html",context)


class UserProfileDetailView(FormView):
	template_name = "user_detail.html"
	form_class = UserProfileDetailForm

	def get_context_data(self,**kwargs):
		context = super(UserProfileDetailView, self).get_context_data(**kwargs)
		username = self.kwargs["slug"]
		context["username"] = username
		context["image_base_width"] = PERSONAL_GROUP_IMG_WIDTH
		star_id = retrieve_user_id(username)
		try:
			user_obj = User.objects.only('id','date_joined').get(id=star_id)# get required fields only
			user_profile = UserProfile.objects.only('bio','age','gender','shadi_shuda','attractiveness','avatar','streak').get(user_id=star_id)# get required user profile fields
			context["object"] = user_obj
			context["user_profile"] = user_profile
		except User.DoesNotExist:
			raise Http404("User ID does not compute")
		if star_id:
			user_id = self.request.user.id
			context["own_id"] = user_id
			context["star_id"] = star_id
			num_trending_pics = is_image_star(user_id=star_id)
			context["is_star"] = int(num_trending_pics) if num_trending_pics else num_trending_pics
			star_score = retreive_trending_rep(user_id=star_id)
			context["star_score"] = int(star_score) if star_score > 0 else 0
			context["city_name"] = REV_CITY_DICT.get(user_profile.streak,0)
			context["zodiac"] = ZODIAC.get(user_profile.attractiveness,'None')
			user_id = str(user_id) if user_id else None
			is_defender, is_own_profile, ban_detail = in_defenders(user_id), user_id == star_id, None
			banned, time_remaining, ban_detail = check_content_and_voting_ban(star_id, with_details=True)
			context["star_av_url"] = retrieve_avurl(star_id)
			context["is_profile_banned"] = banned
			context["is_own_profile"] = is_own_profile
			context["ban_detail"] = ban_detail
			context["is_defender"] = is_defender
			context["time_remaining"] = time_remaining
			context["origin"] = '10'#helps redirect back to this page if a user enter the "report" funnel
			context["mehfil_creation_ttl"] = self.request.session.pop("mehfil_creation_rate_limited",None)
			context["star_owner_mehfils"] = retrieve_latest_user_owned_mehfils(star_id)
			total_fans, recent_fans = get_photo_fan_count(star_id)
			context["fans"] = total_fans if total_fans else 0
			context["recent_fans"] = recent_fans if recent_fans else 0
			if star_id == user_id:
				context["subscribed_topics"] = retrieve_subscribed_topics(user_id)
				context["stars"] = UserFan.objects.filter(fan_id=user_id).count()
				context["blocked"] = get_banned_users_count(user_id)
				context["mobile_verified"] = self.request.mobile_verified
				context["successfully_unsubscribed"] = self.request.session.pop("successfully_unsubscribed"+str(user_id),'')
			else:
				context["fanned"] = [str(user_obj.id)] if is_fan(star_id, user_id) else []
				context["mobile_verified"] = is_mobile_verified(star_id)
			context["noindex"] = True if (banned or not context["mobile_verified"]) else False
			################### Retention activity logging ###################
			if user_id:
				from_redirect = self.request.session.pop('rd',None)# remove this too when removing retention activity logger
				if not from_redirect and int(user_id) > SEGMENT_STARTING_USER_ID:
					time_now = time.time()
					if is_own_profile:
						act = 'A2' if self.request.mobile_verified else 'A2.u'
					else:
						act = 'A6' if self.request.mobile_verified else 'A6.u'
					activity_dict = {'m':'GET','act':act,'t':time_now,'tuid':star_id}# defines what activity just took place
					log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			##################################################################
		else:
			# user does not exist
			raise Http404("User ID does not exist")
		return context

################################## Permanent redirects ################################################


def comment_pk(request, pk=None, origin=None, ident=None, *args, **kwargs):
	"""
	Permanent redirect to comment page of an image
	"""
	request.session["photo_id"] = pk
	if ident:
		request.session["user_ident"] = ident
	else:
		request.session["user_ident"] = None
	if origin:
		return HttpResponsePermanentRedirect("/comment/{0}/{1}/".format(pk, origin))
	else:
		return HttpResponsePermanentRedirect("/comment/{}/".format(pk))


def profile_pk(request, slug=None, key=None, *args, **kwargs):
	"""
	Permanent redirect to new user profile photos view
	"""
	if key:
		request.session["photograph_id"] = key
	return HttpResponsePermanentRedirect("/user/{}/fotos/".format(slug.encode('utf-8')))


def best_photos_list(request):
	"""
	Permanent redirect to the trending page
	"""
	return HttpResponsePermanentRedirect("/photo/best-list/")


def fresh_photos_list(request):
	"""
	Permanent redirect to the trending page
	"""
	return HttpResponsePermanentRedirect("/photo/fresh-list/")


def redirect_to_profile_photos(request,slug):
	"""
	Permanent redirect to new user profile photos view
	"""
	return HttpResponsePermanentRedirect("/user/{}/fotos/".format(slug.encode('utf-8')))


def redirect_to_search(request):
	"""
	Permanent redirect to search
	"""
	return HttpResponsePermanentRedirect("/search/nickname/")


def redirect_to_mehfil_list(request):
	"""
	Permanent redirect to mehfil joined list
	"""
	return HttpResponsePermanentRedirect("/mehfil/joined/list/")


def redirect_to_1on1_list(request):
	"""
	Permanent redirect to 1on1 friendlist
	"""
	return HttpResponsePermanentRedirect("/1-on-1/friends/")


def perm_redirect_to_home(request,pk=None,origin=None,slug=None):
	"""
	Permanent redirect to new user profile photos view
	"""
	return HttpResponsePermanentRedirect("/")

############################################################################################################


#rate limit this
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def reset_password(request,*args,**kwargs):
	if request.method == 'POST':
		form = ResetPasswordForm(data=request.POST,request=request)
		if form.is_valid():
			form.save()
			password = request.POST.get("password")
			request.session.pop("authentic_password_owner", None)
			request.user.session_set.exclude(session_key=request.session.session_key).delete() # logging the user out of everywhere else
			return render(request,'change_password/new_password.html',{'new_pass':password})
		else:
			allowed = request.session.get('authentic_password_owner',None)
			if allowed == '1':
				context={'form':form,'allowed':True}
			else:
				context={'form':form,'allowed':None}
			return render(request,'change_password/reset_password.html',context)    
	else:
		form = ResetPasswordForm()
		try:
			allowed = request.session.get('authentic_password_owner',None)
			if allowed == '1':
				#can press forward, user is 'allowed'
				return render(request,'change_password/reset_password.html',{'form':form,'allowed':True})
			else:
				#send back for reauth
				return redirect("reauth")
		except:
			#send back for reauth
			return redirect("reauth")

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
@ratelimit(method='POST', rate='25/h')
def reauth(request, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		return render(request, 'change_password/penalty_reauth.html', {'pk':'pk'})
	else:
		user_id = request.user.id
		if tutorial_unseen(user_id=user_id, which_tut='27', renew_lease=True):
			return render(request, 'change_password/password_change_tutorial.html', {'username':retrieve_uname(user_id,decode=True)})
		else:
			if request.method == 'POST':
				form = ReauthForm(data=request.POST,request=request)
				if form.is_valid():
					request.session['authentic_password_owner'] = '1'
					request.session.modified = True
					return redirect("reset_password")
				else:
					return render(request, 'change_password/reauth.html', {'form':form})
			else:
				return render(request, 'change_password/reauth.html', {'form':ReauthForm()})

############################################################################################################

class VerifiedView(ListView):
	model = User
	form_class = VerifiedForm
	template_name = "verified.html"
	paginate_by = 100

	def get_queryset(self):
		global condemned
		return User.objects.filter(username__in=FEMALES).order_by('-userprofile__score')


def photo_top_trenders(request):
	"""
	Renders the top trending users (in terms of photos uploaded)
	"""
	################### Retention activity logging ###################
	user_id = request.user.id
	if user_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'Z9' if request.mobile_verified else 'Z9.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,"top_photo.html",{'object_list':retrieve_top_trenders(),'list_size':TRENDER_RANKS_TO_COUNT})


# class TopView(ListView):
# 	# model = User
# 	form_class = TopForm
# 	template_name = "top.html"

# 	def get_queryset(self):
# 		return UserProfile.objects.only('user__username','score').values('user__username','score').order_by('-score')[:100]

# 	def get_context_data(self, **kwargs):
# 		context = super(TopView, self).get_context_data(**kwargs)
# 		if self.request.user.is_authenticated():
# 			context["verified"] = FEMALES        
# 		return context


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


class PhotostreamView(ListView):
	model = Photo
	#form_class = PhotostreamForm
	template_name = "photostream.html"
	paginate_by = 10

	def get_queryset(self):
		try:
			# ps = PhotoStream.objects.filter(id=self.request.session["photo_photostream_id"])
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
		# context["number"] = PhotoStream.objects.get(id=pk).photo_count
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
			self.request.session.modified = True
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


@ratelimit(rate='3/s')
def reply_to_photo(request, pk=None, ident=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		return redirect("missing_page")
	else:
		if pk.isdigit():
			request.session["photo_id"] = pk
			request.session["related_photostream_id"] = ident
			return redirect("reply_options")
		else:
			return redirect("profile", request.user.username, 'fotos')


@ratelimit(rate='3/s')
def videocomment_pk(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		return redirect("missing_page")
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
		on_fbs = self.request.META.get('HTTP_X_IORG_FBS',False)
		# try:
		#   on_fbs = self.request.META.get('X-IORG-FBS')
		# except:
		#   on_fbs = False
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
				self.request.session.modified = True
				which_video = Video.objects.get(id=pk)
			except:
				user.userprofile.score = user.userprofile.score - 3
				user.userprofile.save()
				return redirect("profile", slug=user.username, type='fotos')
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
					return redirect("profile", slug=user.username, type='fotos')
		else:
			context = {'pk': 'pk'}
			return render(self.request, 'auth_commentpk.html', context)


def display_image_comments(request,pk,origin=None):
	"""
	Render the comments page for image comments
	"""
	user_id = request.user.id
	try:
		photo = Photo.objects.select_related('owner').get(id=pk)
		photo_owner_id = photo.owner_id
	except Photo.DoesNotExist:
		context = {}
		if user_id:
			remove_erroneous_notif(notif_name="np:"+str(user_id)+":0:"+str(pk), user_id=user_id)
			context["obj_deleted"] = True
		else:
			context['target_username'] = 'User'
			context['authorized'] = False
		return context
	###################################################
	secret_key = uuid.uuid4()
	home_hash = 'img:'+pk
	target_username = retrieve_uname(photo_owner_id,decode=True)
	
	comments = PhotoComment.objects.only('abuse','text','id','submitted_by','submitted_on','submitted_by__username',\
		'direct_reply_tgt_uname','direct_reply_tgt_text_prefix','direct_reply_tgt_text_postfix','direct_reply_id').\
	values('abuse','text','id','submitted_by','submitted_on','submitted_by__username','direct_reply_tgt_uname',\
		'direct_reply_tgt_text_prefix','direct_reply_tgt_text_postfix','direct_reply_id').filter(which_photo_id=pk).\
	order_by('-id')[:25]

	for comment in comments:
		comment["submitted_on"] = convert_to_epoch(comment["submitted_on"])

	context = {'feature_phone':True if request.is_feature_phone else False,'lid':home_hash,'photo_id':pk,'obj_deleted':False,\
	'photo':photo,'sk':secret_key,'thumbs':retrieve_trending_thumbs(photo_owner_id),'stars':get_all_image_star_ids(), \
	'is_star':is_image_star(user_id=photo_owner_id),'on_fbs':request.META.get('HTTP_X_IORG_FBS',False),'authorized':True,\
	'random':random.sample(xrange(1,188),15),'VDC':VOTING_DRIVEN_CENSORSHIP+1,'target_username':target_username,\
	'latest_comment_time':comments[0]['submitted_on'] if comments else None,'origin':origin if origin else '3',\
	'comments':comments,'photo_owner_id':photo_owner_id,'user_is_owner':photo_owner_id == user_id}

	if origin == '3':
		# originating from home            
		request.session["target_id"] = home_hash#turn pk into 'home_hash' (for accurate redirects)
		request.session.modified = True

	if user_id:
		set_text_input_key(user_id, pk, 'pht_comm', secret_key)
		time_now = time.time()
		context["dir_rep_form"] = DirectResponseForm(with_id=True)
		context["main_rep_form"] = DirectResponseForm()
		context["is_auth"] = True
		context["mob_verified"] = True
		context["user_id"] = user_id
		if not request.mobile_verified:
			context["mob_verified"] = False
		context["authenticated"] = True
		context["dir_rep_invalid"] = request.session.pop("dir_rep_invalid"+str(user_id),None)
		context["own_username"] = retrieve_uname(user_id,decode=True)
		if comments:	
			# useful for showing  'NEW' tag next to comments
			last_seen_time = get_last_comment_time(commenter_id=user_id, obj_owner_id=photo_owner_id, obj_hash_name=home_hash)
			# useful for showing a 'NEW' tag next to replies
			context["comment_time"] = float(last_seen_time) if last_seen_time else None
		
		################### Retention activity logging ###################
		from_redirect = request.session.pop('rd','')
		if not from_redirect and user_id > SEGMENT_STARTING_USER_ID:
			act = 'C1' if request.mobile_verified else 'C1.u'
			activity_dict = {'m':'GET','act':act,'t':time_now,'pi':photo.image_file.url,'pc':photo.caption}# defines what activity just took place
			log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
		##################################################################
	else:
		context["authenticated"] = False

	return render(request,"comments.html",context)



@ratelimit(rate='3/s')
def see_special_photo_pk(request,pk=None,*args,**kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		return redirect("missing_page")
	else:
		if pk.isdigit():
			request.session["target_special_photo_id"] = pk
			return redirect("see_special_photo")
		else:
			return redirect("see_special_photo")

@ratelimit(rate='3/s')
def special_photo(request, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		return redirect("missing_page")
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


#########################Views for fresh photos#########################

# @ratelimit(rate='3/s')
# @ratelimit(field='user_id',ip=False,rate='4/s')
# @csrf_protect
# def photo_comment(request,pk=None,*args,**kwargs):
# 	"""
# 	Processes comment written directly under a photo via home, top or best photos

# 	'pk' arg is photo_id
# 	"""
# 	if request.user_banned:
# 		return redirect("error")	
# 	elif request.method == 'POST':
# 		home_hash = request.POST.get("home_hash",None)# e.g. typical value is in the form of 'img:1234' where 1234 is photo_id
# 		user_id = request.user.id
# 		origin = request.POST.get("origin",None)
# 		banned, time_remaining, ban_details = check_content_and_voting_ban(user_id, with_details=True)
# 		if banned:
# 			# Cannot submit home_reply if banned
# 			return render(request, 'judgement/cannot_comment.html', {'time_remaining': time_remaining,'ban_details':ban_details,\
# 				'forbidden':True,'own_profile':True,'defender':None,'is_profile_banned':True, 'org':origin,'obid':pk,'lid':home_hash})
# 		else:
# 			photo_owner_id = request.POST.get("popk",None)
# 			banned_by, ban_time = is_already_banned(own_id=user_id,target_id=photo_owner_id, return_banner=True)
# 			if banned_by:
# 				request.session["banned_by"] = banned_by
# 				request.session["ban_time"] = ban_time
# 				if origin in ('1','20'):
# 					request.session["where_from"] = '1'
# 				elif origin in ('2','21'):
# 					request.session["where_from"] = '2'
# 				elif origin in ('3','19'):
# 					request.session["where_from"] = '3'
# 				request.session["obj_id"] = pk
# 				request.session["lid"] = home_hash
# 				request.session.modified = True
# 				return redirect("ban_underway")
# 			else:
# 				time_now = time.time()
# 				is_mob_verified = request.mobile_verified
# 				form = PhotoCommentForm(data=request.POST,user_id=user_id,photo_id=pk,mob_verified=is_mob_verified)
# 				origin = request.POST.get("origin",None)
# 				lang = request.POST.get("lang",None)
# 				sort_by = request.POST.get("sort_by",None)
# 				if form.is_valid():
# 					photo = Photo.objects.only('owner','comment_count').get(id=pk)
# 					if photo.owner_id != int(photo_owner_id):
# 						request.session["where_from"] = '2'
# 						return redirect("ban_underway")
# 					else:
# 						description = form.cleaned_data.get("photo_comment")
# 						set_input_rate_and_history.delay(section='pht_comm',section_id=pk,text=description,user_id=user_id,time_now=time_now)
# 						if request.is_feature_phone:
# 							device = '1'
# 						elif request.is_phone:
# 							device = '2'
# 						elif request.is_tablet:
# 							device = '4'
# 						elif request.is_mobile:
# 							device = '5'
# 						else:
# 							device = '3'
# 						# exists = PhotoComment.objects.filter(which_photo_id=pk, submitted_by=request.user).exists() #i.e. user commented before
# 						photocomment = PhotoComment.objects.create(submitted_by=request.user, which_photo_id=pk, text=description,device=device)
# 						comment_time = convert_to_epoch(photocomment.submitted_on)
# 						commenter_name, url = retrieve_credentials(user_id,decode_uname=True)
# 						add_photo_comment(photo_id=pk,latest_comm_text=description,latest_comm_writer_id=user_id,\
# 							comment_id=photocomment.id,latest_comm_writer_uname=commenter_name, time=comment_time)
# 						unseen_comment_tasks.delay(user_id, pk, comment_time, photocomment.id, photo.comment_count, description, \
# 							commenter_name, url, is_mob_verified)
# 						################### Retention activity logging ###################
# 						if user_id > SEGMENT_STARTING_USER_ID:
# 							if origin == '1':
# 								sub_categ = '7'#inline photocomment in fresh list
# 							elif origin == '2':
# 								sub_categ = '8'#inline photo comment in best list
# 							else:
# 								sub_categ = '6'#inline photo comment on home
# 							activity_dict = {'m':'POST','act':'I'+sub_categ,'t':time_now,'tx':description,'pi':photo.image_file.url,\
# 							'pc':photo.caption}# defines what activity just took place
# 							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
# 						##################################################################
# 						if origin == '3':
# 							request.session["home_hash_id"] = home_hash
# 							request.session.modified = True
# 							return redirect("redirect_to_home")
# 						else:
# 							return return_to_content(request,origin,pk,None,None)
# 				else:
# 					################### Retention activity logging ###################
# 					if user_id > SEGMENT_STARTING_USER_ID:
# 						if origin == '1':
# 							sub_categ = '7'#inline photocomment in fresh list
# 						elif origin == '2':
# 							sub_categ = '8'#inline photo comment in best list
# 						else:
# 							sub_categ = '6'#inline photo comment on home
# 						request.session['rd'] = '1'
# 						photo = Photo.objects.only('image_file','caption').get(id=pk)
# 						if is_mob_verified:
# 							activity_dict = {'m':'POST','act':'I'+sub_categ+'.i','t':time_now,'tx':request.POST.get('photo_comment',None),\
# 							'pi':photo.image_file.url,'pc':photo.caption}# defines what activity just took place
# 						else:
# 							activity_dict = {'m':'POST','act':'I'+sub_categ+'.u','t':time_now,'tx':request.POST.get('photo_comment',None),\
# 							'pi':photo.image_file.url,'pc':photo.caption}# defines what activity just took place
# 						log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
# 					###################################################################
# 					error_string = form.errors.as_text().split("*")[2]
# 					if origin == '3':
# 						request.session['home_direct_reply_error_string'] = error_string
# 						return redirect(reverse_lazy("home")+'?page=1#error')#redirecting to special error section
# 					else:
# 						request.session['photo_direct_reply_error_string'] = error_string
# 						if origin == '1':
# 							return redirect(reverse_lazy("photo", args=['fresh-list'])+'?page=1#error')#redirecting to special error section
# 						elif origin == '2':
# 							return redirect(reverse_lazy("photo", args=['best-list'])+'?page=1#error')#redirecting to special error section
# 						else:
# 							return return_to_content(request,origin,pk,None,None)
# 	else:
# 		return redirect("home")


# def photo_location(request,*args,**kwargs):
# 	photo_id = request.session.pop('target_photo_id',0)
# 	photo_ids = get_photo_feed()
# 	if photo_id == 0:
# 		# there is no indexing to be done, just return to the top of the page
# 		page_num = request.GET.get('page', '1')
# 		page_obj = get_page_obj(page_num,photo_ids,PHOTOS_PER_PAGE)
# 		request.session['photos'] = retrieve_obj_feed(page_obj.object_list)
# 		request.session['photo_page'] = page_obj
# 		return redirect("photo")
# 	else:
# 		# have to return user to a specific anchor
# 		try:
# 			index = photo_ids.index("img:"+photo_id)
# 		except ValueError:
# 			index = 0
# 		page_num, addendum = get_addendum(index,PHOTOS_PER_PAGE)
# 		url = reverse_lazy("photo")+addendum
# 		page_obj = get_page_obj(page_num,photo_ids,PHOTOS_PER_PAGE)
# 		request.session['photos'] = retrieve_obj_feed(page_obj.object_list)
# 		request.session['photo_page'] = page_obj
# 		return redirect(url)


def photo_redirect(request, list_type='best-list', pk=None):
	"""
	Used to redirect to specific spot on photo pages (e.g. after writing something)
	"""
	if list_type == 'best-list':
		feed_type = 'best_photos'
	else:
		feed_type = 'fresh_photos'
	########################################################################
	if pk:
		index = retrieve_photo_feed_index("img:"+str(pk),feed_type=feed_type)
	else:
		pk = request.session.pop('photo_hash_id',None)
		index = retrieve_photo_feed_index("img:"+str(pk),feed_type=feed_type) if pk else 0
	if index is None:
		url = reverse_lazy("photo", args=[list_type])+'?page=1#section0'
	else:
		addendum = get_addendum(index, PHOTOS_PER_PAGE, only_addendum=True)
		url = reverse_lazy("photo", args=[list_type])+addendum
	############################################
	############################################
	request.session['rd'] = '1'#used by retention activity loggers in home_page() - remove whenever
	############################################
	############################################
	return redirect(url)


def photo_page(request,list_type='best-list'):
	"""
	Displays both the latest photos page (sorted by latest first) and the best photos page (sorted by best first)
	"""
	if list_type in ('best-list','fresh-list'):
		own_id, page_num = request.user.id, request.GET.get('page', '1')
		start_index, end_index = get_indices(page_num, PHOTOS_PER_PAGE)
		cached_image_count = retrieve_image_count(list_type=list_type)
		if list_type == 'best-list':
			type_, page_origin, char = 'best_photos', '2', 'B'# 'char' is used in retention activity logging - can be removed
			navbar_type, single_notif_origin = 'best', '21'
			if cached_image_count:
				num_in_last_1_day = cached_image_count
			else:
				one_day_ago = datetime.utcnow()-timedelta(hours=24)
				num_in_last_1_day = Logout.objects.filter(logout_time__gte=one_day_ago).count()
				cache_image_count(num_images=num_in_last_1_day,list_type=list_type)
		else:
			type_, page_origin, char = 'fresh_photos', '1', 'F'# 'char' is used in retention activity logging - can be removed
			navbar_type, single_notif_origin = 'fresh', '20'
			if cached_image_count:
				num_in_last_1_day = cached_image_count
			else:
				one_day_ago = datetime.utcnow()-timedelta(hours=24)
				num_in_last_1_day = Photo.objects.filter(upload_time__gte=one_day_ago).count()
				cache_image_count(num_images=num_in_last_1_day,list_type=list_type)
		obj_list, list_total_size = get_photo_feed(start_idx=start_index, end_idx=end_index, feed_type=type_, with_feed_size=True)
		num_pages = list_total_size/PHOTOS_PER_PAGE
		max_pages = num_pages if list_total_size % PHOTOS_PER_PAGE == 0 else (num_pages+1)
		page_num = int(page_num)
		list_of_dictionaries = retrieve_obj_feed(obj_list)
		#######################
		# must be done in this line, since the 't' information in objs in list_of_dictionaries is lost subsequently
		try:
			oldest_post_time = list_of_dictionaries[-1]['t']
		except:
			oldest_post_time = 0.0
		#######################
		list_of_dictionaries = format_post_times(list_of_dictionaries, with_machine_readable_times=True)
		if own_id:
			is_auth = True
			fanned = bulk_is_fan(set(str(obj['si']) for obj in list_of_dictionaries),own_id)
			secret_key = str(uuid.uuid4())
			set_text_input_key(user_id=own_id, obj_id='1', obj_type=type_, secret_key=secret_key)
			newbie_lang, newbie_flag = request.session.get("newbie_lang",None), request.session.get("newbie_flag",None)
			mobile_verified = request.mobile_verified
			#######################
			# enrich objs with information that 'own_id' liked them or not
			if list_type == 'best-list':
				recent_user_voted_obj_hashes = check_votes_on_objs(obj_list, own_id)
				for obj in list_of_dictionaries:
					if obj['h'] in recent_user_voted_obj_hashes:
						obj['v'] = True# user 'liked' this particular object, so mark it
			else:
				# exploit the fact that the list_of_dictionaries is sorted by time
				if retrieve_last_vote_time(voter_id=own_id) > oldest_post_time:
					recent_user_votes = retrieve_recent_votes(voter_id=own_id, oldest_post_time=oldest_post_time)
					# payload in recent_user_votes is voter_id+":"+target_user_id+":"+vote_value+":"+obj_type+":"+target_obj_id
					recent_user_voted_obj_hashes = set(obj.split(":",3)[-1] for obj in recent_user_votes)
					for obj in list_of_dictionaries:
						if obj['h'] in recent_user_voted_obj_hashes:
							obj['v'] = True# user 'liked' this particular object, so mark it
			
			###################### Retention activity logging ######################
			from_redirect = request.session.pop('rd',None)# remove this too when removing retention activity logger
			if not from_redirect and own_id > SEGMENT_STARTING_USER_ID:
				time_now = time.time()
				char = char if page_num == 1 else char+'2'
				act = char if mobile_verified else char+".u"
				activity_dict = {'m':'GET','act':act,'t':time_now,'pg':page_num}# defines what activity just took place
				log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
			########################################################################

		else:
			is_auth = False
			fanned = []
			secret_key = ''
			newbie_lang, newbie_flag = None, None
			mobile_verified = None
		on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
		is_js_env = retrieve_user_env(user_agent=request.META.get('HTTP_USER_AGENT',None), fbs = on_fbs)
		on_opera = True if (not on_fbs and not is_js_env) else False
		
		context = {'object_list':list_of_dictionaries,'fanned':fanned,'is_auth':is_auth,\
		'ident':own_id, 'newbie_lang':newbie_lang,'newbie_flag':newbie_flag,'single_notif_origin':single_notif_origin,\
		'page_origin':page_origin,'sk':secret_key,"mobile_verified":mobile_verified,\
		'feed_type':type_,'navbar_type':navbar_type,'on_opera':on_opera,'num_in_last_1_day':num_in_last_1_day,\
		'list_type':list_type,'dir_rep_form':DirectResponseForm(with_id=True),'thin_rep_form':DirectResponseForm(thin_strip=True),\
		'latest_dir_rep':retrieve_latest_direct_reply(user_id=own_id),'single_notif_dir_rep_form':DirectResponseForm()}#
		
		next_page_number = page_num+1 if page_num<max_pages else 1
		previous_page_number = page_num-1 if page_num>1 else max_pages
		context["page"] = {'number':page_num,'has_previous':True if page_num>1 else False,'has_next':True if page_num<max_pages else False,\
		'previous_page_number':previous_page_number,'next_page_number':next_page_number,'max_pages':max_pages}
		if newbie_flag:
			if newbie_flag in ('1','2','3','5','6','7'):
				if newbie_flag == '5':
					context["newbie_tutorial_page"] = 'tutorial5b.html'
				elif newbie_flag == '6':
					context["newbie_tutorial_page"] = 'tutorial6b.html'
				elif newbie_flag == '7':
					if page_num == 1:
						context["newbie_tutorial_page"] = 'tutorial7a.html'
					elif page_num >= 2:
						context["newbie_tutorial_page"] = 'tutorial7b.html'
						is_set = set_tutorial_seen(viewer_id=own_id)
						request.session.pop("newbie_flag",None)
					else:
						# what if they paginate even more?
						pass
				else:
					context["newbie_tutorial_page"] = 'tutorial'+newbie_flag+'.html'
			else:
				context["newbie_tutorial_page"] = 'newbie_rules.html'
		# extraneous
		context["lang"] = 'None'
		context["sort_by"] = 'recent'
		#####################
		context["fbs"] = request.META.get('HTTP_X_IORG_FBS',False)
		# context["single_notif_error"] = request.session.pop("single_notif_error",None)
		if own_id:
			# context["process_notification"] = True
			# context["photo_direct_reply_error_string"] = request.session.pop("photo_direct_reply_error_string",None)
			context["dir_rep_invalid"] = request.session.pop("dir_rep_invalid"+str(own_id),None)
		return render(request,"photos_page.html",context)
	else:
		raise Http404("Such a photo listing does not exist")


##################################################################


def public_photo_upload_denied(request):
	"""
	Helper view for upload_public_photo
	"""
	which_msg = request.session.pop("public_photo_upload_denied",None)
	if which_msg == '0':
		ttl = request.session.pop("public_photo_upload_fbs_ttl",None)
		return render(request,'big_photo_fbs.html',{'rate_limited':True,'ttl':ttl})
	elif which_msg == '1':
		return render(request,"dont_click_again_and_again.html",{'from_public_photos':True,'from_ecomm':False})
	elif which_msg == '2':
		return render(request,"verification/unable_to_submit_without_verifying.html",{'upload_public_photo':True})
	elif which_msg in ('3','4'):
		ban_details = request.session.pop('public_photo_upload_denied_details',None)
		time_remaining = request.session.pop("public_photo_upload_denied_time_togo",None)
		return render(request, 'upload_public_photo.html', {'time_remaining': time_remaining,'ban_details':ban_details,'forbidden':True,'defender':None,\
			'own_profile':True})
	elif which_msg == '5':
		time_remaining = request.session.pop("public_photo_upload_rate_limit_ttl",None)
		type_of_rate_limit = request.session.pop("public_photo_upload_rate_limit_torl",None)
		return render(request, 'error_photo.html', {'time':time_remaining,'tp':type_of_rate_limit,'sharing_limit':NUM_SUBMISSION_ALLWD_PER_DAY})
	elif which_msg == '6':
		return render(request,'big_photo_fbs.html',{'pk':'pk'})
	elif which_msg == '7':
		return render(request,'big_photo_regular.html',{'pk':'pk'})
	elif which_msg == '8':
		pk = request.session.pop("public_photo_upload_denied_photo_pk",None)
		if pk:
			try:
				photo = Photo.objects.get(id=int(pk))
				return render(request, 'duplicate_photo.html', {'photo': photo, 'is_star': is_image_star(user_id=photo.owner_id)})
			except Photo.DoesNotExist:
				return render(request, 'big_photo.html', {'photo':'photo'})
		else:
			return redirect("missing_page")
	elif which_msg == '9':
		return render(request, 'mehfil/notify_and_redirect.html',{'is_pub_photo':True,'img_too_big':True})
	elif which_msg == '10':
		return redirect("error")
	elif which_msg == '11':
		return render(request,'big_photo_regular.html',{'too_narrow':True})
	elif which_msg == '12':
		# the photo doesn't have a title
		caption_error = request.session.pop("public_photo_upload_denied_caption_error",None)
		image_error = request.session.pop("public_photo_upload_denied_image_error",None)
		return render(request,'error_pic.html',{'caption_error':caption_error,'image_error':image_error})
	else:
		raise Http404("Unknown photo upload error")



@csrf_protect
def upload_public_photo(request,*args,**kwargs):
	"""
	Responsible for rendering photo upload page and processing the submitted photo
	"""
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	is_ajax = request.is_ajax()
	if request.method == 'POST':
		time_now = time.time()
		user = request.user
		user_id = user.id
		if on_fbs:
			is_fbs_rate_limited, ttl = is_fbs_user_rate_limited_from_photo_upload(user_id)
		else:
			is_fbs_rate_limited, ttl = None, None
		if is_fbs_rate_limited:
			################### Retention activity logging ###################
			if user_id > SEGMENT_STARTING_USER_ID:
				activity_dict = {'m':'POST','act':'P.i','t':time_now}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			##################################################################
			request.session["public_photo_upload_fbs_ttl"] = ttl
			request.session["public_photo_upload_denied"] = '0'
			request.session.modified = True
			if is_ajax:
				return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
			else:
				return redirect('public_photo_upload_denied')
		else:
			mob_verified = request.mobile_verified
			secret_key_from_form, secret_key_from_session = request.POST.get('sk','0'), get_and_delete_photo_upload_key(user_id)
			if str(secret_key_from_form) != str(secret_key_from_session):
				request.session["public_photo_upload_denied"] = '1'
				request.session.modified = True
				if is_ajax:
					return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
				else:
					return redirect('public_photo_upload_denied')
			elif not mob_verified:
				################### Retention activity logging ###################
				if user_id > SEGMENT_STARTING_USER_ID:
					activity_dict = {'m':'POST','act':'P.u','t':time_now}# defines what activity just took place
					log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
				##################################################################
				# only verified users can upload a photo
				request.session["public_photo_upload_denied"] = '2'
				request.session.modified = True
				if is_ajax:
					return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
				else:
					return redirect('public_photo_upload_denied')
			elif request.user_banned:
				request.session["public_photo_upload_denied"] = '10'
				request.session.modified = True
				if is_ajax:
					return HttpResponse(json.dumps({'success':False,'message':reverse('error')}),content_type='application/json',)
				else:
					return redirect("error") #errorbanning
			else:
				ttl, type_of_rate_limit = content_sharing_rate_limited(user_id)
				banned, time_remaining, ban_details = check_content_and_voting_ban(user_id, with_details=True)
				if ttl:
					request.session["public_photo_upload_rate_limit_ttl"] = ttl
					request.session["public_photo_upload_rate_limit_torl"] = type_of_rate_limit
					request.session["public_photo_upload_denied"] = '5'
					request.session.modified = True
					if is_ajax:
						return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
					else:
						return redirect('public_photo_upload_denied')
				elif banned:
					request.session["public_photo_upload_denied_details"] = ban_details
					request.session["public_photo_upload_denied_time_togo"] = time_remaining
					request.session["public_photo_upload_denied"] = '3'
					request.session.modified = True
					if is_ajax:
						return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
					else:
						return redirect('public_photo_upload_denied')
				else:    
					form = UploadPhotoForm(request.POST,request.FILES)
					if form.is_valid():
						image_file = request.FILES['image_file']
					else:
						################### Retention activity logging ###################
						if user_id > SEGMENT_STARTING_USER_ID:
							activity_dict = {'m':'POST','act':'P.i','t':time_now}# defines what activity just took place
							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
						##################################################################
						error_dict = dict(form.errors)
						caption_error = error_dict.get('caption',[])
						image_error = error_dict.get('image_file',[])
						if is_ajax:
							request.session["public_photo_upload_denied"] = '12'
							request.session["public_photo_upload_denied_caption_error"] = caption_error[0] if caption_error else ''
							request.session["public_photo_upload_denied_image_error"] = image_error[0] if image_error else ''
							request.session.modified = True
							return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
						else:
							secret_key = str(uuid.uuid4())
							set_photo_upload_key(user_id, secret_key)
							return render(request,"upload_public_photo.html",{'form':form,'sk':secret_key,'sharing_limit':NUM_SUBMISSION_ALLWD_PER_DAY})
					if image_file:
						if on_fbs:
							if image_file.size > 200000:
								################### Retention activity logging ###################
								if user_id > SEGMENT_STARTING_USER_ID:
									activity_dict = {'m':'POST','act':'P.i','t':time_now}# defines what activity just took place
									log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
								##################################################################
								request.session["public_photo_upload_denied"] = '6'
								request.session.modified = True
								if is_ajax:
									return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
								else:
									return redirect('public_photo_upload_denied')
						else:
							if image_file.size > 10000000:
								################### Retention activity logging ###################
								if user_id > SEGMENT_STARTING_USER_ID:
									activity_dict = {'m':'POST','act':'P.i','t':time_now}# defines what activity just took place
									log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
								##################################################################
								request.session["public_photo_upload_denied"] = '7'
								request.session.modified = True
								if is_ajax:
									return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
								else:
									return redirect('public_photo_upload_denied')
						reoriented = request.POST.get('reoriented',None)
						resized = request.POST.get('resized',None)
						image_file_new, img_height, dup_photo_id, avghash = process_public_image(image=image_file, quality=None if on_fbs else True,already_resized=resized, \
						already_reoriented=reoriented)#, caption=request.POST.get('caption',None))
						if isinstance(dup_photo_id,float):
							################### Retention activity logging ###################
							if user_id > SEGMENT_STARTING_USER_ID:
								activity_dict = {'m':'POST','act':'P.i','t':time_now}# defines what activity just took place
								log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
							##################################################################
							request.session["public_photo_upload_denied"] = '8'
							request.session["public_photo_upload_denied_photo_pk"] = dup_photo_id
							request.session.modified = True
							if is_ajax:
								return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
							else:
								return redirect('public_photo_upload_denied')
						elif img_height == 'too_high':
							################### Retention activity logging ###################
							if user_id > SEGMENT_STARTING_USER_ID:
								activity_dict = {'m':'POST','act':'P.i','t':time_now}# defines what activity just took place
								log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
							##################################################################
							request.session["public_photo_upload_denied"] = '9'
							request.session.modified = True
							if is_ajax:
								return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
							else:
								return redirect('public_photo_upload_denied')
						elif img_height == 'too_narrow':
							################### Retention activity logging ###################
							if user_id > SEGMENT_STARTING_USER_ID:
								activity_dict = {'m':'POST','act':'P.i','t':time_now}# defines what activity just took place
								log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
							##################################################################
							# this image is too narrow, don't upload it since it's probably low quality
							request.session["public_photo_upload_denied"] = '11'
							request.session.modified = True
							if is_ajax:
								return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
							else:
								return redirect('public_photo_upload_denied')
						else:
							image_file = image_file_new if image_file_new else None
					else:
						request.session["public_photo_upload_denied"] = '12'
						request.session.modified = True
						if is_ajax:
							return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
						else:
							return redirect('public_photo_upload_denied')
					invisible_score = set_rank()
					caption = form.cleaned_data.get("caption",None)
					photo = Photo.objects.create(image_file = image_file, owner=user, caption=caption, comment_count=0, avg_hash=avghash, \
						invisible_score=invisible_score)
					photo_id = photo.id
					##########################
					img_height, img_width = photo.image_file.height, photo.image_file.width
					cache_photo_dim(str(photo_id),img_height,img_width)
					# log_public_img(user_id=user_id, on_opera=on_opera, on_fbs=on_fbs, img_width=img_width, img_height=img_height)
					##########################
					datetime_obj = photo.upload_time
					epochtime = convert_to_epoch(datetime_obj)
					banned = '1' if request.user_banned else '0'
					name, owner_url = retrieve_credentials(user_id,decode_uname=True)
					photo_obj = add_image_post(obj_id=photo_id, categ='6', submitter_id=user_id, submitter_av_url=owner_url, submitter_username=name, \
						submitter_score=0, is_star=is_image_star(user_id=user_id),img_url=photo.image_file.url, img_caption=caption,\
						submission_time=epochtime, from_fbs=on_fbs, img_height=img_height, img_width=img_width)
					recent_photo_ids = get_recent_photos(user_id)
					number_of_photos, total_score = 0, 0
					if recent_photo_ids:
						vote_scores = Photo.objects.filter(id__in=recent_photo_ids).values_list('vote_score',flat=True)
						for vote_score in vote_scores:
							total_score += vote_score
						number_of_photos = len(recent_photo_ids)
					photo_upload_tasks.delay(user_id=user_id, photo_id=photo_id, upload_time=epochtime, username=name, temp_photo_obj=photo_obj, \
						number_of_photos=number_of_photos, total_score=total_score)
					insert_hash(photo_id, photo.avg_hash) #perceptual hash of the photo
					save_recent_photo(user_id, photo_id) #saving 5 recent ones
					create_object(object_id=photo_id, object_type='0', object_owner_avurl=owner_url,object_owner_id=user_id,object_owner_name=name,\
						object_desc=caption,photourl=photo.image_file.url,vote_score=0,res_count=0)
					rate_limit_content_sharing(user_id)#rate limiting for 5 mins (and hard limit set at 20 items per day)
					if on_fbs:
						rate_limit_fbs_public_photo_uploaders(user_id)
					# bulk_create_notifications.delay(user_id, photo_id, epochtime,photo.image_file.url, name, caption)
					################### Retention activity logging ###################
					if user_id > SEGMENT_STARTING_USER_ID:
						request.session['rd'] = '1'
						activity_dict = {'m':'POST','act':'P','t':time_now,'pi':photo.image_file.url,'pc':caption}# defines what activity just took place
						log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
					##################################################################
					if is_ajax:
						return HttpResponse(json.dumps({'success':True,'message':reverse('photo',kwargs={"list_type": 'fresh-list'})}),content_type='application/json',)
					else:
						return redirect("photo",list_type='fresh-list')
	else:
		# if it's a GET request
		is_js_env = retrieve_user_env(user_agent=request.META.get('HTTP_USER_AGENT',None), fbs = on_fbs)
		on_opera = True if (not on_fbs and not is_js_env) else False
		if on_opera:
			# disallowing opera mini users from posting public text posts
			# mislabeled template - used to show some generic errors and such to posters
			return render(request, 'error_photo.html', {'opera_detected':True})
		else:
			context, own_id = {}, request.user.id
			banned, time_remaining, ban_details = check_content_and_voting_ban(own_id, with_details=True)
			if banned:
				context["defender"] = None
				context["own_profile"] = True
				context["forbidden"] = True
				context["ban_details"] = ban_details
				context["time_remaining"] = time_remaining
				return render(request,"upload_public_photo.html",context)
			else:
				if on_fbs:
					is_fbs_rate_limited, ttl = is_fbs_user_rate_limited_from_photo_upload(own_id)
				else:
					is_fbs_rate_limited, ttl = None, None
				if is_fbs_rate_limited:
					request.session["public_photo_upload_fbs_ttl"] = ttl
					request.session["public_photo_upload_denied"] = '0'
					request.session.modified = True
					if is_ajax:
						return HttpResponse(json.dumps({'success':False,'message':reverse('public_photo_upload_denied')}),content_type='application/json',)
					else:
						return redirect('public_photo_upload_denied')
				else:
					################### Retention activity logging ###################
					if own_id > SEGMENT_STARTING_USER_ID:
						time_now = time.time()
						if request.mobile_verified:
							activity_dict = {'m':'GET','act':'P1','t':time_now}# defines what activity just took place
						else:
							activity_dict = {'m':'GET','act':'P1.u','t':time_now}# defines what activity just took place
						log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
					##################################################################
					context["show_instructions"] = True if tutorial_unseen(user_id=own_id, which_tut='26', renew_lease=True) else False
					context["form"] = UploadPhotoForm()
					secret_key = str(uuid.uuid4())
					context["sk"] = secret_key
					context["sharing_limit"] = NUM_SUBMISSION_ALLWD_PER_DAY
					set_photo_upload_key(own_id, secret_key)
					return render(request,"upload_public_photo.html",context)


##################################################################


class PhotoShareView(FormView):
	form_class = PhotoShareForm
	template_name = "photo_share_help.html"

	def get_context_data(self, **kwargs):
		context = super(PhotoShareView, self).get_context_data(**kwargs)
		try:
			loc = self.kwargs["loc"]
			context["loc"] = loc
			username = self.kwargs["slug"]
			context["username"] = username
		except:
			loc = '1'
			context["loc"] = loc
			username = None
		try:
			context["no_id"] = False
			pk = self.kwargs["pk"]
			context["ident"] = pk
			context["lid"] = 'img:'+str(pk)
			context["regular_url"] = "https://damadam.pk/photo_detail/"+str(pk)
			#context["freebasics_url"] = "https://https-damadam-pk.0.freebasics.com/photo_detail/"+str(pk)
		except:
			context["no_id"] = True
		if self.request.user.is_authenticated():
			context["authenticated"] = True
		else:
			context["authenticated"] = False
		return context

##################################################################

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
	#   """
	#   Returns the initial data to use for forms on this view.
	#   """
	#   user = self.request.user
	#   if user.is_authenticated():
	#       try:
	#           msg = ChatPicMessage.objects.filter(sender=user).latest('sending_time')
	#           self.initial = {'what_number': msg.what_number} #initial needs to be passed a dictionary
	#           return self.initial
	#       except:
	#           return self.initial
	#   else:#i.e user is not authenticated
	#       return self.initial
	#   return self.initial

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
		on_fbs = self.request.META.get('HTTP_X_IORG_FBS',False)
		# try:
		#   on_fbs = self.request.META.get('X-IORG-FBS')
		# except:
		#   on_fbs = False
		if on_fbs:
				#definitely on a mobile browser, but can't redirect out now, so show the web address they are to send
				return redirect("user_SMS", fbs=1, num=num)
		else:#i.e. not on internet.org, now detect whether mobile browser or desktop browser
				return redirect("user_SMS", fbs=0, num=num)

	# def get_success_url(self): #which URL to go back once settings are saved?
	#   try: 
	#       on_fbs = self.request.META.get('X-IORG-FBS')
	#   except:
	#       on_fbs = False
	#   if on_fbs:
	#       return 
	#       return redirect("home")#, pk= reply.answer_to.id)

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



# @ratelimit(rate='3/s')
# def first_time_cricket_refresh(request, *args, **kwargs):
# 	was_limited = getattr(request, 'limits', False)
# 	if was_limited:
# 		# if request.user.is_authenticated():
# 		#   deduction = 1 * -1
# 		#   request.user.userprofile.score = request.user.userprofile.score + deduction
# 		#   request.user.userprofile.save()
# 		#   return render(request, 'cricket_refresh_penalty.html', {})
# 		# else:
# 		#   return render(request, 'cricket_refresh_penalty.html', {})
# 		return redirect("missing_page")
# 	else:
# 		if first_time_refresher(request.user.id):
# 			add_refresher(request.user.id)
# 			return render(request, 'cricket_refresh.html', {})
# 		else:
# 			return redirect("cricket_comment")


@ratelimit(rate='7/s')
def first_time_unseen_refresh(request, *args, **kwargs):
	if getattr(request, 'limits', False):
		return redirect("missing_page")
	else:
		if tutorial_unseen(user_id=request.user.id, which_tut='14', renew_lease=True):
			return render(request, 'unseen_activity_refresh.html', {'unique': request.user.username})
		else:
			return redirect("unseen_activity", request.user.username)
				

@ratelimit(rate='3/s')
def welcome_pk(request, pk=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		return redirect("missing_page")
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


@csrf_protect
def unseen_group(request, pk=None, *args, **kwargs):
	"""
	Handles replying to a mehfil message from a single notification or from unseen activity
	"""
	if request.user_banned:
		return redirect("error")
	else:
		user_id = request.user.id
		username, own_avurl = retrieve_credentials(user_id,decode_uname=True)
		grp = retrieve_group_reqd_data(group_id=pk,with_group_owner_id=True,with_uuid=True)
		if not group_member_exists(pk, user_id):
			return render(request, 'penalty_unseengroupreply.html', {'uname':username,'not_member':True})
		elif not request.mobile_verified:
			return render(request,'verification/unable_to_submit_without_verifying.html',{'join_public_mehfil':True})
		else:
			if request.method == 'POST':
				origin, lang, sort_by = request.POST.get("origin",None), request.POST.get("lang",None), request.POST.get("sort_by",None)
				banned, time_remaining, ban_details = check_content_and_voting_ban(user_id, with_details=True)
				if banned:
					# Cannot submit unseen_group response if banned
					return render(request, 'judgement/cannot_comment.html', {'time_remaining': time_remaining,'ban_details':ban_details,\
						'forbidden':True,'own_profile':True,'defender':None,'is_profile_banned':True, 'org':origin if origin else '14', \
						'tun':username})
				elif grp["p"] == '1':
					form = UnseenActivityForm(request.POST,user_id=user_id,prv_grp_id=pk,pub_grp_id='',photo_id='',link_id='',per_grp_id='')
				else:
					form = UnseenActivityForm(request.POST,user_id=user_id,prv_grp_id='',pub_grp_id=pk,photo_id='',link_id='',per_grp_id='')
				reply_time = time.time()
				if form.is_valid():
					desc1, desc2 = form.cleaned_data.get("public_group_reply"), form.cleaned_data.get("private_group_reply")
					description = desc1 if desc1 else desc2
					invalidate_cached_mehfil_replies(pk)
					group_attendance_tasks.delay(group_id=pk, user_id=user_id, time_now=reply_time)
					if grp["p"] == '1':
						set_input_rate_and_history.delay(section='prv_grp',section_id=pk,text=description,user_id=user_id,time_now=reply_time)
						priority='priv_mehfil'
						################### Retention activity logging ###################
						if user_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							if origin:
								# this is a single notification
								activity_dict = {'m':'POST','act':'S3','t':reply_time,'tx':description}
							else:
								# this is within the matka
								activity_dict = {'m':'POST','act':'M3','t':reply_time,'tx':description}
							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=reply_time)
						##################################################################
					else:
						set_input_rate_and_history.delay(section='pub_grp',section_id=pk,text=description,user_id=user_id,time_now=reply_time)
						priority='public_mehfil'
						################### Retention activity logging ###################
						if user_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							if origin:
								# this is a single notification
								activity_dict = {'m':'POST','act':'S4','t':reply_time,'tx':description}
								
							else:
								# this is within the matka
								activity_dict = {'m':'POST','act':'M4','t':reply_time,'tx':description}
							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=reply_time)
						##################################################################
					
					save_group_submission(writer_id=user_id, group_id=pk, text=description, chat_image=None, posting_time=reply_time,\
						writer_avurl=get_s3_object(own_avurl,category='thumb'), category='0',writer_uname=username, save_latest_submission=True)
					group_notification_tasks.delay(group_id=pk, sender_id=user_id, group_owner_id=grp["oi"], topic=grp["tp"],\
						reply_time=reply_time, poster_url=own_avurl, poster_username=username, reply_text=description, priv=grp["p"], \
						slug=grp["u"], image_url=None, priority=priority, from_unseen=True)
					if origin:
						return return_to_content(request,origin,pk,None,username)
					else:
						return redirect("unseen_activity", username)
				else:
					################### Retention activity logging ###################
					if user_id > SEGMENT_STARTING_USER_ID:
						if origin:
							# this is a single notification
							if grp['p'] == '1':
								act = 'S3.i'
								tx = request.POST.get("private_group_reply",'')
							else:
								act = 'S4.i'
								tx = request.POST.get("public_group_reply",'')
							activity_dict = {'m':'POST','act':act,'t':reply_time,'tx':tx}
						else:
							# this is within the matka
							request.session['rd'] = '1'
							if grp['p'] == '1':
								act = 'M3.i' 
								tx = request.POST.get("private_group_reply",'')
							else:
								act = 'M4.i'
								tx = request.POST.get("public_group_reply",'')
							activity_dict = {'m':'POST','act':act,'t':reply_time,'tx':tx}
						log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=reply_time)
					##################################################################
					err_string = form.errors.as_text().split("*")[2]
					if origin:
						request.session["single_notif_error"] = err_string
						request.session.modified = True
						return return_to_content(request,origin,pk,None,username)
					else:
						request.session["unseen_error_string"] = err_string
						return redirect(reverse_lazy("unseen_activity", args=[username])+"#error")
			else:
				return redirect("unseen_activity", username)


@csrf_protect
def unseen_comment(request, pk=None, *args, **kwargs):
	"""
	Processes comment under photo from unseen activity (or single notification)
	"""
	if request.user_banned:
		return redirect("error")
	elif not request.mobile_verified:
		################### Retention activity logging ###################
		user_id = request.user.id
		if user_id > SEGMENT_STARTING_USER_ID:
			time_now = time.time()
			act = 'M6.u' if request.POST.get("origin",'14') == '14' else 'S6.u'
			activity_dict = {'m':'POST','act':act,'t':time_now,'tx':request.POST.get("photo_comment",None)}
			log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
		##################################################################
		return render(request, 'verification/unable_to_submit_without_verifying.html', {'comment':True})
	else:
		user_id = request.user.id
		username = retrieve_uname(user_id,decode=True)
		if request.method == 'POST':
			origin = request.POST.get("origin",'14')
			banned, time_remaining, ban_details = check_content_and_voting_ban(user_id, with_details=True)
			if banned:
				# Cannot submit home_reply if banned
				return render(request, 'judgement/cannot_comment.html', {'time_remaining': time_remaining,'ban_details':ban_details,\
					'forbidden':True,'own_profile':True,'defender':None,'is_profile_banned':True, 'org':origin,'tun':username})
			else:
				time_now = time.time()
				photo_owner_id = request.POST.get("popk",None)
				banned_by, ban_time = is_already_banned(own_id=user_id,target_id=photo_owner_id, return_banner=True)
				if banned_by:
					request.session["banned_by"] = banned_by
					request.session["ban_time"] = ban_time
					if origin in ('3','19'):
						request.session["where_from"] = '3'
					elif origin in ('1','20'):
						request.session["where_from"] = '1'
					elif origin in ('2','21'):
						request.session["where_from"] = '2'
					else:
						request.session["where_from"] = origin
					request.session["own_uname"] = username
					request.session.modified = True
					return redirect("ban_underway")
				else:
					lang, sort_by = request.POST.get("lang",None), request.POST.get("sort_by",None)
					form = UnseenActivityForm(request.POST,user_id=user_id,prv_grp_id='',pub_grp_id='',link_id='',photo_id=pk,per_grp_id='')
					if form.is_valid():
						try:
							photo_comment_count = Photo.objects.only('comment_count').get(id=pk).comment_count
						except Photo.DoesNotExist:
							remove_erroneous_notif(notif_name="np:"+str(user_id)+":0:"+str(pk), user_id=user_id)
							return render(request,"object_deleted.html",{})
						description = form.cleaned_data.get("photo_comment")
						set_input_rate_and_history.delay(section='pht_comm',section_id=pk,text=description,user_id=user_id,time_now=time_now)
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
						# exists = PhotoComment.objects.filter(which_photo_id=pk, submitted_by=request.user).exists() #i.e. user commented before
						photocomment = PhotoComment.objects.create(submitted_by_id=user_id, which_photo_id=pk, text=description,device=device)
						comment_time = convert_to_epoch(photocomment.submitted_on)
						try:
							url = request.user.userprofile.avatar.url
						except ValueError:
							url = None
						# add_photo_comment(photo_id=pk,latest_comm_text=description,latest_comm_writer_id=user_id,\
						# 	comment_id=photocomment.id,latest_comm_writer_uname=username, time=comment_time)
						# unseen_comment_tasks.delay(user_id, pk, comment_time, photocomment.id, photo_comment_count, description, \
						# 	username, url, request.mobile_verified)
						################### Retention activity logging ###################
						if user_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							if origin == '14':
								# this is matka
								activity_dict = {'m':'POST','act':'M6','t':time_now,'tx':description}
							else:
								# this is a single notification
								activity_dict = {'m':'POST','act':'S6','t':time_now,'tx':description}
							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
						##################################################################
						return return_to_content(request,origin,pk,None,username)
					else:
						################### Retention activity logging ###################
						if user_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							if origin == '14':
								# this is matka
								activity_dict = {'m':'POST','act':'M6.i','t':time_now,'tx':request.POST.get("photo_comment",None)}
							else:
								# this is a single notification
								activity_dict = {'m':'POST','act':'S6.i','t':time_now,'tx':request.POST.get("photo_comment",None)}
							log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
						##################################################################
						err_string = form.errors.as_text().split("*")[2]
						if origin == '14':
							request.session["unseen_error_string"] = err_string
							return redirect(reverse_lazy("unseen_activity", args=[username])+"#error")
						else:
							request.session["single_notif_error"] = err_string
							request.session.modified = True
							return return_to_content(request,origin,pk,None,username)
		else:
			return redirect("unseen_activity", username)


@csrf_protect
def unseen_reply(request, pk=None, *args, **kwargs):
	"""
	Handles replying as a 'jawab' from a single notification or from unseen activity
	"""
	time_now = time.time()
	if request.user_banned:
		return redirect("error")
	elif not request.mobile_verified:
		################### Retention activity logging ###################
		own_id = request.user.id
		if own_id > SEGMENT_STARTING_USER_ID:
			if request.POST.get("origin",'14') == '14':
				# this is matka
				activity_dict = {'m':'POST','act':'M7.u','t':time_now,'tx':request.POST.get("home_comment",'')}
			else:
				# this is a single notification
				activity_dict = {'m':'POST','act':'S7.u','t':time_now,'tx':request.POST.get("home_comment",'')}
			log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
		##################################################################
		return render(request, 'verification/unable_to_submit_without_verifying.html', {'reply':True})
	else:
		own_id = request.user.id
		own_uname = retrieve_uname(own_id,decode=True)#request.user.username
		if request.method == 'POST':
			origin = request.POST.get("origin",'14')
			banned, time_remaining, ban_details = check_content_and_voting_ban(own_id, with_details=True)
			if banned:
				# Cannot submit home_reply if banned
				return render(request, 'judgement/cannot_comment.html', {'time_remaining': time_remaining,'ban_details':ban_details,\
					'forbidden':True,'own_profile':True,'defender':None,'is_profile_banned':True, 'org':origin,'tun':own_uname})
			else:
				link_writer_id = request.POST.get("lwpk",None)
				banned_by, ban_time = is_already_banned(own_id=own_id,target_id=link_writer_id, return_banner=True)
				if banned_by:
					request.session["banned_by"] = banned_by
					request.session["ban_time"] = ban_time
					if origin in ('3','19'):
						request.session["where_from"] = '3'
					elif origin in ('1','20'):
						request.session["where_from"] = '1'
					elif origin in ('2','21'):
						request.session["where_from"] = '2'
					else:
						request.session["where_from"] = origin
					request.session["own_uname"] = own_uname
					request.session.modified = True
					return redirect("ban_underway")
				else:
					lang, sort_by = request.POST.get("lang",None), request.POST.get("sort_by",None)
					form = UnseenActivityForm(request.POST,user_id=own_id,prv_grp_id='',pub_grp_id='',link_id=pk,photo_id='',per_grp_id='')
					if form.is_valid():
						text = form.cleaned_data.get("home_comment")
						target = process_publicreply(request=request,link_id=pk,text=text,origin=origin if origin else 'from_unseen',\
							link_writer_id=link_writer_id)
						set_input_rate_and_history.delay(section='home_rep',section_id=pk,text=text,user_id=own_id,time_now=time_now)
						################### Retention activity logging ###################
						if own_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							if origin == '14':
								# this is matka
								activity_dict = {'m':'POST','act':'M7','t':time_now,'tx':text}
							else:
								# this is a single notification
								activity_dict = {'m':'POST','act':'S7','t':time_now,'tx':text}
							log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
						##################################################################
						if target == ":":
							return redirect("ban_underway")
						elif target == ';':
							remove_erroneous_notif(notif_name="np:"+str(own_id)+":2:"+str(pk), user_id=own_id)
							return render(request,"object_deleted.html",{})
						else:
							return return_to_content(request,origin,pk,None,own_uname)
					else:
						################### Retention activity logging ###################
						if own_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							if origin == '14':
								# this is matka
								activity_dict = {'m':'POST','act':'M7.i','t':time_now,'tx':request.POST.get("home_comment",'')}
							else:
								# this is a single notification
								activity_dict = {'m':'POST','act':'S7.i','t':time_now,'tx':request.POST.get("home_comment",'')}
							log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
						##################################################################
						err_string = form.errors.as_text().split("*")[2]
						if origin == '14':
							# from inbox
							request.session["unseen_error_string"] = err_string
							return redirect(reverse_lazy("unseen_activity", args=[own_uname])+"#error")
						else:
							# from single notifications
							request.session["single_notif_error"] = err_string
							request.session.modified = True
							return return_to_content(request,origin,pk,None,own_uname)
		else:
			return redirect("unseen_activity", own_uname)


# @ratelimit(rate='22/38s')
# @ratelimit(rate='10/s')
def unseen_activity(request, slug=None, *args, **kwargs):
	"""
	Renders the inbox functionality
	"""
	user_id = request.user.id
	username = retrieve_uname(user_id,decode=True)
	banned, time_remaining, ban_details = check_content_and_voting_ban(user_id, with_details=True)
	if banned:
		# show "user banned" message and redirect them to home
		return render(request,"voting/photovote_disallowed.html",{'is_profile_banned':True,'is_defender':False, 'own_profile':True,\
			'time_remaining':time_remaining,'uname':username,'ban_details':ban_details,'origin':'19'})
	else:
		page_num = request.GET.get('page', '1')
		start_index, end_index = get_indices(page_num, ITEMS_PER_PAGE)
		notifications, list_total_size = retrieve_unseen_notifications(user_id, start_index, end_index, with_feed_size=True)
		oblist = retrieve_unseen_activity(notifications) if notifications else []
		items_in_page = len(oblist) if oblist else 0

		if list_total_size:
			num_pages = list_total_size/ITEMS_PER_PAGE
			max_pages = num_pages if list_total_size % ITEMS_PER_PAGE == 0 else (num_pages+1)
			page_num = int(page_num)

			###################### Retention activity logging ######################
			from_redirect = request.session.pop('rd',None)
			if not from_redirect and user_id > SEGMENT_STARTING_USER_ID:
				time_now = time.time()
				is_mob_verified = request.mobile_verified
				act = 'M' if is_mob_verified else 'M.u'
				activity_dict = {'m':'GET','act':act,'t':time_now,'pg':page_num}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			########################################################################

			if oblist:
				forms = {}
				for obj in oblist:
					forms[obj['oi']] = UnseenActivityForm()
				secret_key = str(uuid.uuid4())
				set_text_input_key(user_id, '1', 'home', secret_key)
				last_visit_time = float(prev_unseen_activity_visit(user_id))-SEEN[False]
				stars = set()
				for notif in oblist:
					if 'p' in notif and 'lrwi' in notif:
						object_owner_id = notif['ooi']
						if object_owner_id != str(user_id):
							stars.add(notif['ooi'])
				fanned = bulk_is_fan(stars,user_id)
				error = request.session.pop('unseen_error_string','')
				context = {'object_list': oblist, 'verify':FEMALES, 'forms':forms,'nickname':username,'sk':secret_key,'user_id':user_id,\
				'last_visit_time':last_visit_time,'VDC':(VOTING_DRIVEN_CENSORSHIP+1),'VDP':(VOTING_DRIVEN_PIXELATION+1),'fanned':fanned,\
				'validation_error_string':error, 'page':{'has_previous':True if page_num>1 else False,'previous_page_number':page_num-1,\
				'next_page_number':page_num+1,'has_next':True if page_num<max_pages else False,'number':page_num},'section':'matka',\
				'stars':get_all_image_star_ids()}
				on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
				is_js_env = retrieve_user_env(user_agent=request.META.get('HTTP_USER_AGENT',None), fbs = on_fbs)
				context["on_opera"] = True if (not on_fbs and not is_js_env) else False
				return render(request, 'user_unseen_activity.html', context)
			else:
				# page turned out to be empty since all notifications have been deleted.
				return render(request,'user_unseen_activity.html',{'page':{'number':page_num,'has_previous':True if page_num>1 else False,\
					'previous_page_number':page_num-1,'next_page_number':page_num+1,'has_next':True if page_num<max_pages else False}, \
					'nickname':username,'user_id':user_id,'object_list':[],'section':'matka'})
		else:
			###################### Retention activity logging ######################
			from_redirect = request.session.pop('rd',None)
			if not from_redirect and user_id > SEGMENT_STARTING_USER_ID:
				time_now = time.time()
				is_mob_verified = request.mobile_verified
				act = 'M' if is_mob_verified else 'M.u'
				activity_dict = {'m':'GET','act':act,'t':time_now,'pg':0}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			########################################################################
			return render(request, 'user_unseen_activity.html', {'object_list': [], 'page':{},'nickname':username,'user_id':user_id,\
				'section':'matka'})


def unseen_help(request,*args,**kwargs):
	context={'nickname':request.user.username}
	return render(request,'photo_for_fans_help.html',context)

def top_photo_help(request,*args,**kwargs):
	"""
	Shows help page regarding how to get into 'trending'
	"""
	################### Retention activity logging ###################
	user_id = request.user.id
	if user_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'Z10' if request.mobile_verified else 'Z10.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,'top_photo_help.html',{'list_size':TRENDER_RANKS_TO_COUNT})

@csrf_protect
def unseen_fans(request,pk=None,*args, **kwargs):
	if request.method == 'POST':
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


def public_reply_view(request,parent_id):
	"""
	Render the comments page for text comments
	"""
	user_id = request.user.id
	try:
		link = Link.objects.values('id','reply_count','description','submitted_on','submitter','net_votes','url','cagtegory').get(id=parent_id)
		link['machine_time'] = link['submitted_on']
		link['submitted_on'] = naturaltime(link['submitted_on'])
	except Link.DoesNotExist:
		# purge single notification and matka of request.user.id
		remove_erroneous_notif(notif_name="np:"+str(user_id)+":2:"+str(parent_id), user_id=user_id)
		return render(request, 'object_deleted.html',{})
	##########################################################
	secret_key = uuid.uuid4()
	set_text_input_key(user_id, parent_id, 'home_rep', secret_key)
	##########################################################
	parent_submitter_id = link['submitter']
	parent_uname, parent_avurl = retrieve_credentials(parent_submitter_id,decode_uname=True)
	##########################################################
	context = {'main_rep_form': DirectResponseForm(),'dir_rep_invalid':request.session.pop("dir_rep_invalid"+str(user_id),None),\
	'dir_rep_form':DirectResponseForm(with_id=True),'is_auth':True,'user_id':user_id,'on_fbs':request.META.get('HTTP_X_IORG_FBS',False),\
	'mob_verified':True if request.mobile_verified else False,'sk':secret_key,'parent_submitter_id':parent_submitter_id,\
	'parent_av_url':parent_avurl,'parent_submitter_username':parent_uname,'is_star':is_image_star(user_id=parent_submitter_id),\
	'stars':get_all_image_star_ids(),'vote_score':link['net_votes'],'feature_phone':True if request.is_feature_phone else False,\
	'random':random.sample(xrange(1,188),15),'parent':link, 'user_is_owner':parent_submitter_id == user_id}
	##########################################################
	if link['url']:
		payload = link['url'].split(":")
		try:
			theme, context['topic_name'], context['topic_url'] = payload[0], payload[1], payload[2]
			color_grads = COLOR_GRADIENTS[theme]
			context["c1"], context["c2"] = color_grads[0], color_grads[1]
		except IndexError:
			pass
	############### Retention activity logging ###############
	from_redirect = request.session.pop('rd','')
	if not from_redirect and user_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'L1' if request.mobile_verified else 'L1.u'
		activity_dict = {'m':'GET','act':act,'t':time_now,'pc':link['description']}# defines what activity just took place
		log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##########################################################
	replies = retrieve_cached_public_replies(parent_id)
	if replies:
		replies_data = json.loads(replies)
	else:
		replies_data = Publicreply.objects.only('submitted_on','description','id','submitted_by','abuse','submitted_by__username',\
			'direct_reply_tgt_uname','direct_reply_tgt_text_prefix','direct_reply_tgt_text_postfix','direct_reply_id').\
		values('submitted_on','description','id','submitted_by','abuse','submitted_by__username','direct_reply_tgt_uname',\
			'direct_reply_tgt_text_prefix','direct_reply_tgt_text_postfix','direct_reply_id').filter(answer_to_id=parent_id).\
		order_by('-id')[:25]
		for reply in replies_data:
			reply["submitted_on"] = convert_to_epoch(reply["submitted_on"])
		cache_public_replies(json.dumps(replies_data),parent_id)
	context["replies"] = replies_data#replies
	##########################################################
	if request.user_banned:
		context["reply_time"] = None
	elif replies_data:
		# useful for showing  'NEW' tag next to comments
		last_seen_time = get_last_comment_time(commenter_id=user_id, obj_owner_id=parent_submitter_id, obj_hash_name='tx:'+str(parent_id))
		# useful for showing a 'NEW' tag next to replies
		context["reply_time"] = float(last_seen_time) if last_seen_time else None
	else:
		context["reply_time"] = None
	##########################################################
	return render(request,"reply.html",context)


class UserActivityView(ListView):
	model = Link
	slug_field = "username"
	template_name = "user_activity.html"
	paginate_by = 20

	def get_queryset(self):
		username = self.kwargs.get('slug',None)
		if username:
			target_id = retrieve_user_id(username)
			if target_id:
				if target_id == str(self.request.user.id):
					data = Link.objects.values('id','description','submitted_on','net_votes','reply_count','url','cagtegory').\
					filter(submitter_id=target_id).order_by('-id')[:200]
				else:
					data = Link.objects.values('id','description','submitted_on','net_votes','reply_count','url','cagtegory').\
					filter(submitter_id=target_id).order_by('-id')[:60]
				return data
			else:
				raise Http404("This user does not exist")
		else:
			raise Http404("No username provided")


	def get_context_data(self, **kwargs):
		context = super(UserActivityView, self).get_context_data(**kwargs)
		username = self.kwargs['slug']
		target_id = retrieve_user_id(username)
		for obj in context["object_list"]:
			obj['machine_time'] = obj['submitted_on']
			obj['submitted_on'] = naturaltime(obj['submitted_on'])
			if obj['url']:
				payload = obj['url'].split(":")
				try:
					theme, obj['topic_name'], obj['url'] = payload[0], payload[1], payload[2]
					color_grads = COLOR_GRADIENTS[theme]
					obj['c1'], obj['c2'] = color_grads[0], color_grads[1]
				except:
					obj['topic_name'], obj['url'] = '', ''
					obj['c1'], obj['c2'] = '', ''
		if target_id:
			context["is_star"] = is_image_star(user_id=target_id)
			context["verified"] = True if username in FEMALES else False
			context["is_profile_banned"] = False
			if self.request.user.is_authenticated():
				own_id = self.request.user.id
				is_defender, is_own_profile, ban_detail = in_defenders(own_id), str(own_id) == target_id, None
				banned, time_remaining, ban_detail = check_content_and_voting_ban(target_id, with_details=True)
				context["is_profile_banned"] = banned
				context["noindex"] = True if banned else False
				context["is_own_profile"] = is_own_profile
				context["ban_detail"] = ban_detail
				context["time_remaining"] = time_remaining
				context["ident"] = own_id
				context["is_defender"] = is_defender
				context["uname"] = username
				context["submitter_id"] = target_id
				context["submitter_av_url"] = retrieve_avurl(target_id)
				################### Retention activity logging ###################
				if own_id > SEGMENT_STARTING_USER_ID:
					time_now = time.time()
					if is_own_profile:
						act = 'A1' if self.request.mobile_verified else 'A1.u'
					else:
						act = 'A5' if self.request.mobile_verified else 'A5.u'
					activity_dict = {'m':'GET','act':act,'t':time_now,'tuid':target_id}# defines what activity just took place
					log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
				##################################################################
			return context
		else:
			raise Http404("This user does not exist!")


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


	def get_initial(self):#initial is a keyword argument to a formfield that enables pre-filling in the formfield
		"""
		Returns the initial data to use for forms on this view.
		"""
		bio = UserProfile.objects.only('bio').get(user_id=self.request.user.id).bio
		context = {}
		context['bio'] = bio if bio else 'I am a Damadamian'
		return context# initial needs to be passed a dictionary

	
	def get_form_kwargs(self):
		"""
		Returns the keyword arguments for instantiating the form.
		"""
		kwargs = super(UserProfileEditView, self).get_form_kwargs()
		kwargs.update({'user': self.request.user,'on_fbs':self.request.META.get('HTTP_X_IORG_FBS',False)})
		return kwargs

	def get_object(self, queryset=None):
		return UserProfile.objects.get_or_create(user=self.request.user)[0]

	def get_context_data(self, **kwargs):
		own_id = self.request.user.id
		context = super(UserProfileEditView, self).get_context_data(**kwargs)
		context["is_own_profile"] = True
		context["cities"] = CITY_TUP_LIST
		context["streak"] =  UserProfile.objects.only('streak').get(user_id=own_id).streak
		context["zodiac"] =  UserProfile.objects.only('attractiveness').get(user_id=own_id).attractiveness
		context["username"] = retrieve_uname(own_id,decode=True)
		################### Retention activity logging ###################
		from_redirect = self.request.session.pop("rd",None)
		if not from_redirect and own_id > SEGMENT_STARTING_USER_ID:
			time_now = time.time()
			act = 'D' if self.request.mobile_verified else 'D.u'
			activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
			log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
		##################################################################
		return context

	def form_invalid(self, form):
		"""
		If the form is invalid, log the data point (if need be)
		"""
		################### Retention activity logging ###################
		user_id = self.request.user.id
		time_now = time.time()
		if user_id > SEGMENT_STARTING_USER_ID:
			self.request.session['rd'] = '1'
			act = 'D.i' if self.request.mobile_verified else 'D.u.i'
			activity_dict = {'m':'POST','act':act,'t':time_now}# defines what activity just took place
			log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
		##################################################################
		return self.render_to_response(self.get_context_data(form=form))

	def form_valid(self, form):
		time_now = time.time()
		user_id = self.request.user.id
		f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
		zodiac_value = f.attractiveness# using 'attractiveness' attribute for legacy reasons
		city_value = f.streak# using 'streak' attribute for legacy reasons
		set_attribute_change_rate_limit(user_id, zodiac_value, city_value, time_now)
		################### Retention activity logging ###################
		if user_id > SEGMENT_STARTING_USER_ID:
			self.request.session['rd'] = '1'
			if f.avatar.name == 'temp.jpg':
				# new avatar uploaded
				act = 'D1' if self.request.mobile_verified else 'D1.u'
				activity_dict = {'m':'POST','act':act,'t':time_now}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
			old_bio = UserProfile.objects.only('bio').get(user_id=user_id).bio
			if f.bio != old_bio:
				# bio has been updated
				act = 'D2' if self.request.mobile_verified else 'D2.u'
				activity_dict = {'m':'POST','act':act,'t':time_now}# defines what activity just took place
				log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
		##################################################################
		return super(UpdateView, self).form_valid(form) # saves automatically


class UserSettingsEditView(UpdateView):
	model = UserSettings
	form_class = UserSettingsForm
	template_name = "edit_settings.html"

	def get_object(self, queryset=None): #loading the current state of settings
		return UserSettings.objects.get_or_create(user=self.request.user)[0]

	def get_success_url(self): #which URL to go back once settings are saved?
		return reverse_lazy("user_profile", kwargs={'slug': self.request.user})

# @ratelimit(rate='7/s')
def sharing_help(request):
	"""
	Renders a page about sharing ettiquette
	"""
	################### Retention activity logging ###################
	own_id = request.user.id
	if own_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'X3' if request.mobile_verified else 'X3.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,"content/share_content_help.html",{})


#@ratelimit(rate='7/s')
def share_content(request):
	"""
	Renders content sharing page, from where would-be sharer can select 'foto' or 'text' type sharing

	Redirects to text or foto sharing pages accordingly
	"""
	################### Retention activity logging ###################
	own_id = request.user.id
	if own_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'X2' if request.mobile_verified else 'X2.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return render(request,"content/share_content.html",{'first_time':True if tutorial_unseen(user_id=request.user.id, which_tut='25',\
	renew_lease=True) else False})


# @ratelimit(rate='7/s')
def link_create_pk(request, *args, **kwargs):
	"""
	Unused
	"""
	request.session["link_create_token"] = str(uuid.uuid4())
	return redirect("link_create")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def submit_text_post(request):
	"""
	Submit public textual post
	"""
	time_now = time.time()
	own_id = request.user.id
	mobile_verified = request.mobile_verified
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	if request.method == "POST":
		banned, time_remaining, ban_details = check_content_and_voting_ban(own_id, with_details=True)
		if banned:
			return render(request, 'links/link_form.html', {'time_remaining': time_remaining,'ban_details':ban_details,'forbidden':True,\
				'own_profile':True,'defender':None,'is_profile_banned':True})
		else:
			ttl, type_of_rate_limit = content_sharing_rate_limited(own_id)
			if not mobile_verified:
				################### Retention activity logging ###################
				if own_id > SEGMENT_STARTING_USER_ID:
					activity_dict = {'m':'POST','act':'X.u','t':time_now,'tx':request.POST.get("description",None)}# defines what activity just took place
					log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
				##################################################################
				return render(request, 'verification/unable_to_submit_without_verifying.html', {'share_on_home':True})
			elif request.user_banned:
				return redirect("error")
			elif ttl:
				return render(request, 'error_photo.html', {'time':ttl,'origin':'1','tp':type_of_rate_limit,\
				'sharing_limit':NUM_SUBMISSION_ALLWD_PER_DAY})# this is wrongly named, but tells the user to wait
			else:
				form = LinkForm(request.POST,user_id=own_id)#, on_fbs=on_fbs, on_opera=on_opera)
				if form.is_valid():
					description = form.cleaned_data['description']
					alignment = form.cleaned_data['alignment']
					topic_payload = form.cleaned_data['tpay']
					if topic_payload:
						obj = Link.objects.create(description=description, submitter_id=own_id, cagtegory=alignment, url=topic_payload)
					else:
						obj = Link.objects.create(description=description, submitter_id=own_id, cagtegory=alignment)
					obj_id = obj.id
					obj_hash = "tx:"+str(obj_id)
					submitter_name, av_url = retrieve_credentials(own_id,decode_uname=True)

					if topic_payload:
						################### Retention activity logging ###################
						if own_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							activity_dict = {'m':'POST','act':'X.t','t':time_now,'tx':description,'url':form.cleaned_data['turl']}# defines what activity just took place
							log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
						##################################################################
						log_text_submissions('topic')#Logs the number of submisions in topic vs number of submissions of regular text posts
						add_topic_post(obj_id=obj_id, obj_hash=obj_hash, categ=alignment, submitter_id=str(own_id), \
							submitter_av_url=av_url, is_star=is_image_star(user_id=own_id), submission_time=time_now, \
							text=description, from_fbs=on_fbs, topic_url=form.cleaned_data['turl'], \
							topic_name= form.cleaned_data['tname'] ,bg_theme=form.cleaned_data['bgt'], add_to_public_feed=True,\
							submitter_username=submitter_name)
					else:
						################### Retention activity logging ###################
						if own_id > SEGMENT_STARTING_USER_ID:
							request.session['rd'] = '1'
							activity_dict = {'m':'POST','act':'X','t':time_now,'tx':description}# defines what activity just took place
							log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
						##################################################################
						log_text_submissions('text')
						add_text_post(obj_id=obj_id, categ=alignment, submitter_id=own_id, submitter_av_url=av_url, \
							submitter_username=submitter_name, submission_time=time_now, add_to_feed=True, \
							is_star=is_image_star(user_id=own_id), text=description, from_fbs=on_fbs)
					rate_limit_content_sharing(own_id)#rate limiting for 5 mins (and hard limit set at 50 submissions per day)
					# set_input_history.delay(section='home',section_id='1',text=description,user_id=own_id)
					##################################
					log_recent_text(user_id=own_id, description=description)# useful for text content rep creation
					##################################
					url = reverse_lazy("home")+"#shared"
					return redirect(url)
				else:
					# form is invalid
					################### Retention activity logging ###################
					if own_id > SEGMENT_STARTING_USER_ID:
						activity_dict = {'m':'POST','act':'X.i','t':time_now,'tx':request.POST.get("description",None)}# defines what activity just took place
						log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
					##################################################################
					secret_key = str(uuid.uuid4())
					set_text_input_key(own_id, '1', 'likho', secret_key)
					return render(request,"links/link_form.html",{'form':form,'sk':secret_key,'sharing_limit':NUM_SUBMISSION_ALLWD_PER_DAY,\
						'random':random.sample(xrange(1,188),15),'subscribed_topics':retrieve_subscribed_topics(str(own_id))})#,'num_fans':get_follower_count(own_id)})
	else:
		is_js_env = retrieve_user_env(user_agent=request.META.get('HTTP_USER_AGENT',None), fbs = on_fbs)
		on_opera = True if (not on_fbs and not is_js_env) else False
		if on_opera:
			# disallowing opera mini users from posting public text posts
			# mislabeled template - used to show some generic errors and such to posters
			return render(request, 'error_photo.html', {'opera_detected':True})
		else:
			banned, time_remaining, ban_details = check_content_and_voting_ban(own_id, with_details=True)
			if banned:
				context = {'time_remaining':time_remaining,'ban_details':ban_details,'forbidden':True, 'own_profile':True, 'defender':None,\
				'is_profile_banned':True}
			else:
				################### Retention activity logging ###################
				if own_id > SEGMENT_STARTING_USER_ID:
					if mobile_verified:
						activity_dict = {'m':'GET','act':'X1','t':time_now}# defines what activity just took place
					else:
						activity_dict = {'m':'GET','act':'X1.u','t':time_now}# defines what activity just took place
					log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
				##################################################################
				secret_key = str(uuid.uuid4())
				set_text_input_key(own_id, '1', 'likho', secret_key)
				context = {'sk':secret_key,'sharing_limit':NUM_SUBMISSION_ALLWD_PER_DAY,'random':random.sample(xrange(1,188),15),\
				'show_instructions':True if tutorial_unseen(user_id=own_id, which_tut='11', renew_lease=True) else False,'form':LinkForm(),\
				'subscribed_topics':retrieve_subscribed_topics(str(own_id))}#,'num_fans':get_follower_count(own_id)}
			return render(request,"links/link_form.html",context)



@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def welcome_reply(request,*args,**kwargs):
	"""
	"""
	if request.user_banned:
		return redirect("error")
	user_id = request.user.id
	username = retrieve_uname(user_id,decode=True)#request.user.username
	banned, time_remaining, ban_details = check_content_and_voting_ban(user_id, with_details=True)
	if banned:
		# Cannot submit welcome reply since user is banned
		return render(request, 'judgement/cannot_comment.html', {'time_remaining': time_remaining,'ban_details':ban_details,\
			'forbidden':True,'own_profile':True,'defender':None,'is_profile_banned':True, 'org':'19','tun':username})
	else:
		if request.method == 'POST':
			pk = request.session.pop("welcome_pk",None)
			try:
				target = User.objects.get(pk=pk)
			except User.DoesNotExist:
				return redirect("user_profile", slug=username)# redirecting to own profile
			current = User.objects.latest('id')
			num = current.id
			if (num-100) <= int(pk) <= (num+100):
				option = request.POST.get("opt")
				message = request.POST.get("msg")
				try:
					av_url = target.userprofile.avatar.url
				except ValueError:
					av_url = None
				if Link.objects.filter(submitter=target).exists():
					parent = Link.objects.filter(submitter=target).latest('id')
					parent.reply_count = parent.reply_count + 1
				else:
					num = random.randint(1,len(SALUTATIONS))
					text = SALUTATIONS[num-1]
					target_username = target.username
					parent = Link.objects.create(description=text, submitter=target, reply_count=1)
					add_text_post(obj_id=parent.id, categ='1', submitter_id=target.id, submitter_av_url=av_url, submitter_username=target_username, \
						is_star=is_image_star(user_id=target.id),submission_time=time.time(),text=text, from_fbs=request.META.get('HTTP_X_IORG_FBS',False),\
						add_to_feed=False)
				if option == '1' and message == 'Barfi khao aur mazay urao!':
					description = target.username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '1' and message == 'Yeh zalim barfi try kar yar!':
					description = target.username+" welcome! Kesey ho? Yeh zalim barfi try kar yar (barfi)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '1' and message == 'Is barfi se mu meetha karo!':
					description = target.username+" assalam-u-alaikum! Is barfi se mu meetha karo (barfi)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '2' and message == 'Aik plate laddu se life set!':
					description = target.username+" Damadam pe welcome! One plate laddu se life set (laddu)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '2' and message == 'Ye saray laddu aap ke liye!':
					description = target.username+" kya haal he? Ye laddu aap ke liye (laddu)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '2' and message == 'Laddu khao, jaan banao yar!':
					description = target.username+" welcum! Life set hei? Laddu khao, jaan banao (laddu)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '3' and message == 'Jalebi khao aur ayashi karo!':
					description = target.username+" welcomeee! Yar kya hal he? Jalebi khao aur ayashi karo (jalebi)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '3' and message == 'Jalebi meri pasandida hai!':
					description = target.username+" kaisey ho? Jalebi meri pasandida hai! Tumhari bhi? (jalebi)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				elif option == '3' and message == 'Is jalebi se mu metha karo!':
					description = target.username+" salam! Is jalebi se mu meetha karo (jalebi)"
					reply = Publicreply.objects.create(submitted_by_id=user_id, answer_to=parent, description=description)
				else:
					return redirect("home")
				parent.latest_reply = reply
				parent.save()
				try:
					url = request.user.userprofile.avatar.url
				except ValueError:
					url = None
				reply_time = convert_to_epoch(reply.submitted_on)
				amnt = update_comment_in_home_link(reply=description,writer=username,reply_id=reply.id,time=reply_time,writer_id=user_id,\
					link_pk=parent.id)
				publicreply_notification_tasks.delay(link_id=parent.id,link_submitter_url=av_url, sender_id=user_id,\
					link_submitter_id=pk,link_submitter_username=target.username, link_desc=parent.description, \
					reply_time=reply_time,reply_poster_url=url,reply_poster_username=username,reply_desc=reply.description,\
					is_welc=False,reply_count=parent.reply_count,priority='home_jawab',from_unseen=False)
				################### Retention activity logging ###################
				if user_id > SEGMENT_STARTING_USER_ID:
					time_now = time.time()
					request.session['rd'] = '1'
					act = 'Q' if request.mobile_verified else 'Q.u'
					activity_dict = {'m':'POST','act':act,'t':time_now,'tuid':pk}# defines what activity just took place
					log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
				##################################################################
				return redirect("home")
			else:
				return render(request,'old_user.html',{'username':target.username})
		else:
			raise Http404("Not a POST request")


def cross_group_notif(request,pk=None, uid=None,from_home=None, lang=None, sort_by=None, *args,**kwargs):
	update_notification(viewer_id=uid,object_id=pk, object_type='3',seen=True,unseen_activity=True, single_notif=False,\
		bump_ua=False)
	################### Retention activity logging ###################
	user_id = request.user.id
	if user_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		request.session['rd'] = '1'
		act = 'Q3' if request.mobile_verified else 'Q3.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return return_to_content(request,from_home,pk,None,None)


def cross_comment_notif(request, pk=None, usr=None, from_home=None, object_type=None, lang=None, sort_by=None, *args, **kwargs):
	update_notification(viewer_id=usr, object_id=pk, object_type='0',seen=True, unseen_activity=True,\
		single_notif=False,bump_ua=False)
	################### Retention activity logging ###################
	user_id = request.user.id
	if user_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		request.session['rd'] = '1'
		act = 'Q2' if request.mobile_verified else 'Q2.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return return_to_content(request,from_home,pk,None,None)


def cross_salat_notif(request, pk=None, user=None, from_home=None, lang=None, sort_by=None, *args, **kwargs):
	notif_name = "np:"+user+":"+pk.split(":",1)[1]
	hash_name = pk
	viewer_id = user
	delete_salat_notification(notif_name,hash_name,viewer_id)
	if from_home == '3':
		return redirect("home")
	elif from_home == '2':
		return redirect("photo",list_type='best-list')
	else:
		return redirect("photo",list_type='fresh-list')


def cross_notif(request, pk=None, user=None, from_home=None, lang=None, sort_by=None, *args, **kwargs):
	update_notification(viewer_id=user, object_id=pk, object_type='2',seen=True, unseen_activity=True,\
		single_notif=False, bump_ua=False)
	################### Retention activity logging ###################
	user_id = request.user.id
	if user_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		request.session['rd'] = '1'
		act = 'Q1' if request.mobile_verified else 'Q1.u'
		activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
	##################################################################
	return return_to_content(request,from_home,pk,None,None)


@csrf_protect
@ratelimit(rate='7/s')
def unfan(request):
	"""
	Unfans target user, provided target is provably a fan of own_id
	"""
	if getattr(request, 'limits', False):
		raise Http404("You cannot unfan this person")
	elif request.method == "POST":
		own_id = request.user.id
		dec = request.POST.get('dec',None)
		target_user_id = request.POST.get('tuid',None)
		if dec == '1':
			if is_fan(own_id, target_user_id):
				#target user is indeed a fan - remove
				UserFan.objects.filter(fan_id=target_user_id, star_id=own_id).delete()
				remove_from_photo_owner_activity(photo_owner_id=target_user_id, fan_id=own_id)
				# remove own fandom as well (debatable)
				UserFan.objects.filter(fan_id=own_id, star_id=target_user_id).delete()
				remove_from_photo_owner_activity(photo_owner_id=own_id, fan_id=target_user_id)
				rate_limit_unfanned_user(own_id=own_id,target_id=target_user_id)
				return redirect("fan_list",pk=own_id)
			else:
				return redirect("fan_list",pk=own_id)
		elif dec == '0':
			return redirect("fan_list",pk=own_id)
		else:
			target_username = request.POST.get('tunm',None)
			return render(request,"unfan.html",{'target_username':target_username,'target_user_id':target_user_id})
	else:
		raise Http404("Not a POST request")


@csrf_protect
def fan(request,*args,**kwargs):
	"""
	Responsible for processing fanning and unfanning request
	"""
	if getattr(request, 'limits', False):
		raise Http404("You cannot fan this person")
	elif request.method == "POST":
		user_id = request.user.id
		origin, object_id, star_id, home_hash = request.POST.get("org",None), request.POST.get("oid",None), request.POST.get("sid_btn",None), None
		if origin in ('3','22'):
			home_hash = request.POST.get("hh",None)# this is home_hash (e.g. tx:1231 or img:4353), in case user originated from 'home'. Helps in accurate redirection
			topic = request.POST.get('tp','')
			if topic:
				request.session['origin_topic'] = topic
		if int(user_id) == int(star_id):
			raise Http404("You cannot fan your own self")
		else:
			star_username = retrieve_uname(star_id,decode=True)
			if UserFan.objects.filter(fan_id=user_id, star_id=star_id).exists():
				################### Retention activity logging ###################
				if user_id > SEGMENT_STARTING_USER_ID:
					time_now = time.time()
					activity_dict = {'m':'POST','act':'N1','t':time_now,'tuid':star_id}# defines what activity just took place
					log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
					if origin in ('4','10','8'):
						# setting 'from_redict' for 'home text history', 'about', 'home photo history', etc
						request.session['rd'] = '1'
				##################################################################
				# allow unfanning even if user unverified
				UserFan.objects.get(fan_id=user_id, star_id=star_id).delete()
				remove_from_photo_owner_activity(star_id, user_id)
			else:
				# fan does not already exist
				if not request.mobile_verified:
					################### Retention activity logging ###################
					if user_id > SEGMENT_STARTING_USER_ID:
						time_now = time.time()
						activity_dict = {'m':'POST','act':'N.u','t':time_now,'tuid':star_id}# defines what activity just took place
						log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
					##################################################################
					return render(request,'verification/unable_to_submit_without_verifying.html', {'fan':True})
				else:
					#if not shown tutorial of what 'fan' is, show tutorial
					if tutorial_unseen(user_id=user_id, which_tut='13', renew_lease=True):
						context = {'star_id': star_id,'obj_id':object_id,'origin':origin,'name':star_username,'home_hash':home_hash}
						return render(request, 'fan_tutorial.html', context)
					else:
						banned_by, ban_time = is_already_banned(own_id=user_id,target_id=star_id, return_banner=True)
						if banned_by:
							request.session["where_from"] = origin
							if banned_by == str(user_id):
								request.session["banned_by_yourself"] = '1'
							request.session["target_username"] = star_username
							request.session["ban_time"] = ban_time
							request.session["obj_id"] = object_id
							request.session["lid"] = home_hash
							request.session.modified = True
							return redirect("ban_underway") 
						elif is_potential_fan_rate_limited(star_id=star_id,own_id=user_id):
							return render(request,'penalty_fan.html',{'rate_limited':True,'star_username':star_username,\
								'origin':origin,'obid':object_id})
						else:
							################### Retention activity logging ###################
							if user_id > SEGMENT_STARTING_USER_ID:
								time_now = time.time()
								activity_dict = {'m':'POST','act':'N','t':time_now,'tuid':star_id}# defines what activity just took place
								log_user_activity.delay(user_id=user_id, activity_dict=activity_dict, time_now=time_now)
								if origin in ('4','10','8'):
									request.session['rd'] = '1'
							##################################################################
							UserFan.objects.create(fan_id=user_id,star_id=star_id,fanning_time=datetime.utcnow()+timedelta(hours=5))
							add_to_photo_owner_activity(star_id, user_id, new=True)
			return return_to_content(request,origin,object_id,home_hash,star_username)
	else:
		raise Http404("Fanning or unfanning doesn't work with GET requests")

######################## HELL BANNING FUNCTIONALITY ########################


@csrf_protect
def hell_ban(request,*args,**kwargs):
	if request.method == "POST":
		ghost_ban = request.POST.get("ghost_ban","")
		if ghost_ban:
			counter = request.POST.get("counter","")
			username = request.POST.get("original_target_username","")
			if counter == '1':
				target = request.POST.get("target1","")
				if HellBanList.objects.filter(condemned_id=target).exists():
					HellBanList.objects.filter(condemned_id=target).delete()
					HellBanList.objects.create(condemned_id=target)
				else:
					HellBanList.objects.create(condemned_id=target)
				return redirect("profile",username,'fotos')
			else:
				try:
					counter = int(counter)
					temp = 1
					target_ids = []
					while temp < (counter+1):
						target_id = request.POST.get("target"+str(temp),"")
						if target_id:
							target_ids.append(target_id)
						temp += 1
					if target_ids:
						hellbanned =[]
						HellBanList.objects.filter(condemned_id__in=target_ids).delete()
						for target_id in target_ids:
							hellbanned.append(HellBanList(condemned_id=target_id))
						HellBanList.objects.bulk_create(hellbanned)
						return redirect("profile",username,'fotos')
					else:
						return redirect("profile",username,'fotos')
				except:
					return redirect("home")
		else:
			target_username = request.POST.get("t_uname")
			target_id = request.POST.get("t_id")
			clone_ids = get_clones(target_id)
			own_id = request.user.id
			if clone_ids:
				if len(clone_ids) > 1:
					targets = User.objects.filter(id__in=clone_ids).values('id','username')
					hellbanned = list(HellBanList.objects.filter(condemned_id__in=clone_ids).values_list('condemned_id',flat=True))
					if hellbanned:
						for target in targets:
							if target['id'] in hellbanned:
								target['banned'] = True
							else:
								target['banned'] = False
					else:
						for target in targets:
							target['banned'] = False
					context = {'offline':False,'own_id':own_id,'targets':targets,'counter':len(clone_ids),'original_target_id':target_id,\
					'original_target_uname':target_username}
					return render(request,'hell_ban.html',context)
				elif len(clone_ids) == 1:
					if HellBanList.objects.filter(condemned_id=target_id).exists():
						targets = [{'id':target_id,'username':target_username,'banned':True}]
					else:
						targets = [{'id':target_id,'username':target_username,'banned':False}]
					context = {'offline':False,'counter':1,'original_target_id':target_id,'own_id':own_id,'targets':targets,\
					'original_target_uname':target_username}
					return render(request,'hell_ban.html',context)
				else:
					if HellBanList.objects.filter(condemned_id=target_id).exists():
						banned = True
					else:
						banned = False
					context={'offline':True,'original_target_id':target_id,'counter':1,'own_id':own_id,'banned':banned,\
					'original_target_uname':target_username}
					return render(request,'hell_ban.html',context)
			else:
				if HellBanList.objects.filter(condemned_id=target_id).exists():
					banned = True
				else:
					banned = False
				context={'offline':True,'original_target_id':target_id,'counter':1,'own_id':own_id,'banned':banned,\
				'original_target_uname':target_username}
				return render(request,'hell_ban.html',context)
	else:
		return render(request,"404.html",{})

@csrf_protect
def show_clones(request,*args,**kwargs):
	if request.method == "POST":
		target_username = request.POST.get("t_uname")
		target_id = request.POST.get("t_id")
		clone_ids = get_clones(target_id)
		if clone_ids:
			usernames = User.objects.filter(id__in=clone_ids).values_list('username',flat=True)
			context={'usernames':usernames,'original_target_id':target_id,'original_target_uname':target_username,\
			'own_id':request.user.id}
			return render(request,"show_clones.html",context)
		else:
			context={'usernames':None,'original_target_id':target_id,'original_target_uname':target_username,\
			'own_id':request.user.id}
			return render(request,"show_clones.html",context)
	else:
		return render(request,"404.html",{})

@csrf_protect
def kick_ban_user(request,*args,**kwargs):
	if request.method == "POST":
		kick_ban = request.POST.get("kick_ban","")
		if kick_ban:
			counter = request.POST.get("counter","")
			username = request.POST.get("original_target_username","")
			if counter == '1':
				target = request.POST.get("target1","")
				Session.objects.filter(user_id=target).delete()
				# BAN IP or USER_ID or BOTH?
				return redirect("profile",username,'fotos')
			else:
				try:
					counter = int(counter)
					temp = 1
					target_ids = []
					while temp < (counter+1):
						target_id = request.POST.get("target"+str(temp),"")
						if target_id:
							target_ids.append(target_id)
						temp += 1
					Session.objects.filter(user_id__in=target_ids).delete()
					return redirect("profile",username,'fotos')
				except:
					return redirect("home")
		else:
			target_username = request.POST.get("t_uname")
			target_id = request.POST.get("t_id")
			clone_ids = get_clones(target_id)
			if clone_ids:
				if len(clone_ids) > 1:
					targets = User.objects.filter(id__in=clone_ids).values('id','username')
					context={'offline':False,'targets':targets,'original_target_id':target_id,'original_target_uname':target_username,\
					'counter':len(clone_ids),'own_id':request.user.id}
					return render(request,'kick_ban_user.html',context)
				elif len(clone_ids) == 1:
					targets = [{'id':target_id,'username':target_username}]
					context={'offline':False,'targets':targets,'original_target_id':target_id,'original_target_uname':target_username,\
					'counter':1,'own_id':request.user.id}
					return render(request,'kick_ban_user.html',context)
				else:
					context={'offline':True,'original_target_uname':target_username,'original_target_id':target_id,'counter':1,\
					'own_id':request.user.id}
					return render(request,'kick_ban_user.html',context)
			else:
				context={'offline':True,'original_target_uname':target_username,'original_target_id':target_id,'counter':1,\
				'own_id':request.user.id}
				return render(request,'kick_ban_user.html',context)
	else:
		return render(request,"404.html",{})

@csrf_protect
def kick_user(request,*args,**kwargs):
	if request.method == "POST":
		kick = request.POST.get("kick","")
		if kick:
			counter = request.POST.get("counter","")
			username = request.POST.get("original_target_username","")
			if counter == '1':
				target = request.POST.get("target1","")
				Session.objects.filter(user_id=target).delete()
				return redirect("profile",username,'fotos')
			else:
				try:
					counter = int(counter)
					temp = 1
					target_ids = []
					while temp < (counter+1):
						target_id = request.POST.get("target"+str(temp),"")
						if target_id:
							target_ids.append(target_id)
						temp += 1
					Session.objects.filter(user_id__in=target_ids).delete()
					return redirect("profile",username,'fotos')
				except:
					return redirect("home")
		else:
			target_username = request.POST.get("t_uname")
			target_id = request.POST.get("t_id")
			clone_ids = get_clones(target_id)
			if clone_ids:
				if len(clone_ids) > 1:
					targets = User.objects.filter(id__in=clone_ids).values('id','username')
					context={'offline':False,'targets':targets,'original_target_id':target_id,'original_target_uname':target_username,\
					'counter':len(clone_ids),'own_id':request.user.id}
					return render(request,'kick_user.html',context)
				elif len(clone_ids) == 1:
					targets = [{'id':target_id,'username':target_username}]
					context={'offline':False,'targets':targets,'original_target_id':target_id,'original_target_uname':target_username,\
					'counter':1,'own_id':request.user.id}
					return render(request,'kick_user.html',context)
				else:
					context={'offline':True,'original_target_uname':target_username,'original_target_id':target_id,'counter':1,\
					'own_id':request.user.id}
					return render(request,'kick_user.html',context)
			else:
				context={'offline':True,'original_target_id':target_id,'counter':1,'own_id':request.user.id,\
				'original_target_uname':target_username}
				return render(request,'kick_user.html',context)
	else:
		return render(request,"404.html",{})

@csrf_protect
def cut_user_score(request,*args,**kwargs):
	if request.method == "POST":
		penalty = request.POST.get("penalty","")
		if penalty:
			target_username = request.POST.get("t_uname")
			target_id = request.POST.get("t_id")
			UserProfile.objects.filter(user_id=target_id).update(score=F('score')-int(penalty))
			return redirect("profile",target_username,'fotos')
		else:
			target_username = request.POST.get("t_uname")
			target_id = request.POST.get("t_id")
			target_score = UserProfile.objects.get(user_id=target_id).score
			penalty1 = get_price(target_score)
			penalty2 = get_price(target_score)*2
			penalty3 = get_price(target_score)*3
			penalty4 = target_score
			context={'target_uname':target_username,'target_scr':target_score,'own_id':request.user.id,\
			'penalty1':penalty1,'penalty2':penalty2,'penalty3':penalty3,'penalty4':penalty4,'t_id':target_id}
			return render(request,'cut_user_score.html',context)
	else:
		return render(request,"404.html",{})

@csrf_protect   
def manage_user(request,*args,**kwargs):
	if request.method == "POST":
		manager_id = request.POST.get("m_id")
		if str(request.user.id) == manager_id:
			request.session["manager_id"] = manager_id
			target_id = request.POST.get("t_id")
			target = User.objects.get(id=target_id)
			context={'target_uname':target.username,'target_id':target_id}
			return render(request,"manage_user.html",context)
		else:
			return render(request,"404.html",{})    
	else:
		return render(request,"404.html",{})

@csrf_protect    
def manage_user_help(request,*args,**kwargs):
	if request.method == "POST":
		help_type = request.POST.get("htype")
		target_uname = request.POST.get("t_uname")
		target_id = request.POST.get("t_id")
		own_id = request.user.id
		context={'target_uname':target_uname,'target_id':target_id,'own_id':own_id,'authorized':True}
		if help_type == 'ctscr':
			return render(request,'cut_score.html',context)
		elif help_type == 'kout':
			return render(request,'kick_out.html',context)
		elif help_type == 'kban':
			return render(request,'kick_ban.html',context)
		elif help_type == 'ghban':
			return render(request,'ghost_ban.html',context)
		elif help_type == 'oclone':
			return render(request,'check_clones.html',context)
		elif help_type == 'sybil':
			return render(request,'check_sybils.html',context)
		elif help_type == 'revsyb':
			return render(request,'check_reverse_sybils.html',context)
		elif help_type == 'vhist':
			return render(request,'check_voting_hist.html',context)
		else:
			return render(request,"404.html",{})    
	else:
		return render(request,"404.html",{})


def missing_page(request,*args,**kwargs):
	"""
	Responsible for giving a 404 HTTP Response
	"""
	raise Http404("The page you requested has gone AWOL")


def error(request):
	"""
	Displays error to hell-banned profiles

	TODO: Provide a more descriptive message
	"""
	return render(request,"500.html",{})

##################################################### Sitemaps #####################################################


def sitemap(request):
	"""
	Renders a sitemap
	"""
	latest_trending_mod_time, latest_fresh_mod_time = retrieve_photo_feed_latest_mod_time(both=True)
	return render(request, 'sitemap/sitemap.xml', {'latest_trending_mod_time': beautiful_date(latest_trending_mod_time,format_type='4'),\
	'latest_fresh_mod_time':beautiful_date(latest_fresh_mod_time,format_type='4')},content_type="application/xml")


def photo_sitemap_of_sitemaps(request):
	"""
	Renders a sitemap of sitemaps for photo_detail pages
	"""
	sitemap_cohorts, latest_obj_trending_time = retrieve_indexable_photo_detail_cohorts()
	return render(request, 'sitemap/photo_sitemap_of_sitemaps.xml', {'latest_obj_trending_time':latest_obj_trending_time,\
		'sitemap_cohorts': sitemap_cohorts},content_type="application/xml")


def photo_sitemap(request, cohort):
	"""
	Renders a sitemap for photo_detail pages falling within a certain time cohort
	"""
	photo_ids_and_times = retrieve_indexable_photo_detail_list(cohort=cohort)
	return render(request, 'sitemap/photo_sitemap.xml', {'photo_ids_and_times': photo_ids_and_times},content_type="application/xml")


def retrieve_indexable_photo_detail_list(cohort):
	"""
	Retreiving all photo_ids belonging to a certain sitemap cohort
	"""
	trending_photo_objs = Logout.objects.filter(pre_logout_score=cohort).values_list('logout_user_id','logout_time')
	final_data = []
	for photo_id, trending_time in trending_photo_objs:
		final_data.append((photo_id,trending_time.strftime("%Y-%m-%dT%I:%M:%S+00:00")))
	return final_data


def retrieve_indexable_photo_detail_cohorts():
	"""
	Retrieves IDs of photos that have trended since 28th June 2019, and creates cohorts of sitemaps out of them
	"""
	latest_obj = Logout.objects.latest('id')
	latest_obj_trending_time = latest_obj.logout_time.strftime("%Y-%m-%dT%I:%M:%S+00:00")
	earliest_obj = Logout.objects.order_by('id')[:1][0]
	latest_cohort = latest_obj.pre_logout_score# this is cohort num
	first_cohort = earliest_obj.pre_logout_score# this is cohort num
	cohorts = range(first_cohort, latest_cohort+1, 1)
	return cohorts, latest_obj_trending_time


####################################################################################################################


@ratelimit(rate='3/s')
def make_ad(request,*args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		# context = {'unique': 'pk'}
		# return render(request, 'make_ad_error.html', context)
		return redirect("missing_page")
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
		if f.image:
			on_fbs = self.request.META.get('HTTP_X_IORG_FBS',False)
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
		if f.image:
			unique = uuid.uuid4()
			if self.request.user.is_authenticated():
				ad_image=ChatPic.objects.create(image=f.image, owner=self.request.user, times_sent=0, unique=unique)
			else:
				ad_image=ChatPic.objects.create(image=f.image, owner_id=1, times_sent=0, unique=unique)
			self.request.session["ad_image"] = ad_image.image.url
		else:
			self.request.session["ad_image"] = None
		self.request.session["ad_gender_token"] = uuid.uuid4()
		self.request.session.modified = True
		return redirect("ad_gender")


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

@ratelimit(rate='3/s')
def ad_finalize(request,*args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		# context = {'unique': 'pk'}
		# return render(request, 'make_ad_error.html', context)
		return redirect("missing_page")
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
			ad_url = 'http://www.damadam.pk/nick/ad/pin_code' # contains preview of advert that got submitted
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

@csrf_protect
def advertise_with_us(request,*args,**kwargs):
	if request.method == 'POST':
		form = AdvertiseWithUsForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data.get("name")
			detail = form.cleaned_data.get("detail")
			mobile = form.cleaned_data.get("mobile")
			loc = form.cleaned_data.get("loc")
			submission_time = time.time()
			username = request.user.username if request.user.is_authenticated() else None
			save_advertiser(name, detail, mobile, loc, submission_time, username)
			return render(request,"thank_advertiser.html",{})
		else:
			return render(request,"advertise_with_us.html",{'form':form})
	else:
		form = AdvertiseWithUsForm()
		return render(request,"advertise_with_us.html",{'form':form})

@csrf_protect
def show_advertisers(request,*args,**kwargs):
	if request.method == 'POST':
		action = request.POST.get('action',None)
		export = None
		if action == 'Delete All':
			purge_advertisers()
		elif action == 'Export & Delete':
			export = export_advertisers()
		if export is not None:
			return render(request,"advertiser_export_status.html",{'export':export})
		else:
			return redirect("show_advertisers")
	else:
		list_ = get_advertisers()
		list_of_advertisers = []
		for elem in list_:
			list_of_advertisers.append(ast.literal_eval(elem))
		return render(request,"show_advertisers.html",{'advertisers':list_of_advertisers,\
			'num':len(list_of_advertisers)})

# Report run on 26/1/2019
#                      relation                     |  size   
# --------------------------------------------------+---------
#  public.user_sessions_session_expire_date         | 13 GB
#  public.links_publicreply                         | 8751 MB
#  public.links_reply                               | 7889 MB
#  public.links_photocomment                        | 5893 MB
#  public.links_reply__which_group_id__submitted_on | 4316 MB
#  public.links_link                                | 4020 MB
#  public.links_link_latest_reply_id_idx            | 3680 MB
#  public.links_reply_writer_id                     | 3051 MB
#  public.user_sessions_session                     | 2999 MB
#  public.links_publicreply_answer_to_id            | 2742 MB
#  public.links_publicreply_submitted_by_id         | 2686 MB
#  public.links_reply_submitted_on                  | 2652 MB
#  public.links_reply_pkey                          | 2652 MB
#  public.links_reply_which_group_id                | 2503 MB
#  public.links_publicreply_pkey                    | 2192 MB
#  public.user_sessions_session_user_id             | 1866 MB
#  public.links_photocomment_which_photo_id         | 1787 MB
#  public.links_photocomment_submitted_by_id        | 1785 MB
#  public.links_photo_latest_comment_id             | 1609 MB
#  public.links_photocomment_pkey                   | 1534 MB



# Report run on 15/3/2018
#             relation             | total_size 
# ---------------------------------+------------
#  public.links_reply              | 14 GB
#  public.links_publicreply        | 8396 MB
#  public.links_photocomment       | 7377 MB
#  public.user_sessions_session    | 6689 MB
#  public.links_link               | 3769 MB
#  public.links_photo              | 1882 MB
#  public.links_photo_which_stream | 429 MB
#  public.links_photostream        | 408 MB
#  public.auth_user                | 294 MB
#  public.links_userprofile        | 239 MB
#  public.links_userfan            | 214 MB
#  public.links_salatinvite        | 152 MB
#  public.links_hotuser            | 43 MB
#  public.links_group              | 42 MB
#  public.links_totalfanandphotos  | 38 MB
#  public.links_salat              | 28 MB
#  public.links_tutorialflag       | 13 MB
#  public.links_cooldown           | 10112 kB
#  public.links_latestsalat        | 6208 kB
#  public.links_groupcaptain       | 6072 kB


# Report run on 18/3/2017
#              Table               |  Size   | External Size 
# ----------------------------------+---------+---------------
#  user_sessions_session            | 8583 MB | 6917 MB
#  links_publicreply                | 5999 MB | 3078 MB
#  links_photocomment               | 2920 MB | 1401 MB
#  links_photo                      | 2527 MB | 2202 MB
#  links_link                       | 1430 MB | 374 MB
#  links_reply                      | 880 MB  | 664 MB
#  links_photo_which_stream         | 237 MB  | 159 MB
#  links_photostream                | 226 MB  | 119 MB
#  links_userprofile                | 131 MB  | 54 MB
#  links_userfan                    | 105 MB  | 67 MB
#  auth_user                        | 99 MB   | 38 MB


# Report run on 15/3/2017
#               Table               |  Size   | External Size 
# ----------------------------------+---------+---------------
#  user_sessions_session            | 8578 MB | 6911 MB
#  links_publicreply                | 5918 MB | 3040 MB
#  links_photocomment               | 2877 MB | 1381 MB
#  links_photo                      | 2505 MB | 2180 MB
#  links_link                       | 1409 MB | 369 MB
#  links_reply                      | 875 MB  | 660 MB
#  links_salatinvite                | 439 MB  | 319 MB
#  links_photo_which_stream         | 234 MB  | 157 MB
#  links_photostream                | 223 MB  | 118 MB
#  links_userprofile                | 130 MB  | 54 MB
#  links_userfan                    | 105 MB  | 66 MB

# Report run on 4/3/2017
#               Table               |  Size   | External Size 
# ----------------------------------+---------+---------------
#  user_sessions_session            | 8578 MB | 6911 MB
#  links_publicreply                | 5636 MB | 2904 MB
#  links_photocomment               | 2717 MB | 1303 MB
#  links_photo                      | 2423 MB | 2098 MB
#  links_link                       | 1334 MB | 352 MB
#  links_reply                      | 873 MB  | 659 MB
#  links_vote                       | 579 MB  | 371 MB
#  links_salatinvite                | 429 MB  | 312 MB
#  links_groupseen                  | 394 MB  | 362 MB
#  links_photo_which_stream         | 225 MB  | 151 MB
#  links_photostream                | 214 MB  | 113 MB
#  links_userprofile                | 129 MB  | 53 MB
#  links_userfan                    | 101 MB  | 63 MB
#  auth_user                        | 96 MB   | 36 MB
#  links_totalfanandphotos          | 82 MB   | 73 MB
#  links_report                     | 82 MB   | 67 MB
#  links_photovote                  | 49 MB   | 49 MB


# Report run on 24/2/2017
#               Table               |  Size   | External Size 
# ----------------------------------+---------+---------------
#  user_sessions_session            | 8578 MB | 6911 MB
#  links_publicreply                | 5453 MB | 2817 MB
#  links_photocomment               | 2604 MB | 1249 MB
#  links_photo                      | 2366 MB | 2040 MB
#  links_link                       | 1277 MB | 338 MB
#  links_reply                      | 868 MB  | 655 MB
#  links_vote                       | 555 MB  | 356 MB
#  links_salatinvite                | 419 MB  | 305 MB
#  links_groupseen                  | 394 MB  | 362 MB
#  links_photo_which_stream         | 218 MB  | 146 MB
#  links_photostream                | 208 MB  | 110 MB
#  links_userprofile                | 129 MB  | 52 MB


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

###################################################
