import os, time, datetime, random, ast#, math
from collections import defaultdict, Counter
from operator import itemgetter
#from location import MEMLOC
from unconnectedreddit import celery_app1
from django.core.cache import get_cache, cache
from django.db.models import Count, Q, F, Sum
from datetime import datetime, timedelta
from django.utils import timezone
from cricket_score import cricket_scr
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from send_sms import process_sms, bind_user_to_twilio_notify_service, process_buyer_sms, send_personal_group_sms,\
process_user_pin_sms
from score import PUBLIC_GROUP_MESSAGE, PRIVATE_GROUP_MESSAGE, PUBLICREPLY, PHOTO_HOT_SCORE_REQ,\
GIBBERISH_PUNISHMENT_MULTIPLIER, SHARE_ORIGIN, NUM_TO_DELETE,SEGMENT_STARTING_TIME#, UPVOTE, DOWNVOTE,
# from page_controls import PHOTOS_PER_PAGE
from models import Photo, LatestSalat, Photo, PhotoComment, Link, Publicreply, TotalFanAndPhotos, UserProfile, Logout, \
Video, HotUser, PhotoStream, HellBanList, UserFan
#from order_home_posts import order_home_posts, order_home_posts2, order_home_posts1
from redis3 import add_search_photo, bulk_add_search_photos, log_gibberish_text_writer, get_gibberish_text_writers, retrieve_thumbs, \
queue_punishment_amount, save_used_item_photo, save_single_unfinished_ad, save_consumer_number, get_world_age, \
process_ad_final_deletion, process_ad_expiry, log_detail_click, remove_banned_users_in_bulk, log_404_errors, \
set_world_age, retrieve_random_pin, ratelimit_banner_from_unbanning_target, exact_date, calculate_world_age_discount
from redis5 import trim_personal_group, set_personal_group_image_storage, mark_personal_group_attendance, cache_personal_group_data,\
invalidate_cached_user_data, update_pg_obj_notif_after_bulk_deletion, get_personal_group_anon_state, personal_group_soft_deletion, \
personal_group_hard_deletion, exited_personal_group_hard_deletion, update_personal_group_last_seen, set_uri_metadata_in_personal_group,\
rate_limit_personal_group_sharing, exit_user_from_targets_priv_chat
from redis4 import expire_online_users, get_recent_online, set_online_users, log_input_rate, log_input_text, retrieve_uname, retrieve_avurl, \
retrieve_credentials, invalidate_avurl, log_personal_group_exit_or_delete,\
log_share, logging_sharing_metrics, cache_photo_share_data, retrieve_bulk_unames, save_most_recent_online_users, rate_limit_unfanned_user,\
sanitize_unused_subscriptions,log_1on1_chat#, log_photo_attention_from_fresh
from redis2 import set_benchmark, get_uploader_percentile, bulk_create_photo_notifications_for_fans, remove_erroneous_notif,\
bulk_update_notifications, update_notification, create_notification, update_object, create_object, add_to_photo_owner_activity,\
get_active_fans, skip_private_chat_notif, clean_expired_notifications, get_top_100,get_fan_counts_in_bulk, get_all_fans, is_fan, \
remove_from_photo_owner_activity, update_pg_obj_anon, update_pg_obj_del, update_pg_obj_hide, sanitize_eachothers_unseen_activities,\
update_private_chat_notif_object, update_private_chat_notifications, set_uploader_score, bulk_remove_multiple_group_notifications, \
update_group_topic_in_obj
# photo_link_mapping,get_photo_link_mapping, add_home_rating_ingredients, add_home_link,
from redis6 import group_attendance, add_to_universal_group_activity, retrieve_single_group_submission, increment_pic_count,\
log_group_chatter, del_overflowing_group_submissions, empty_idle_groups, delete_ghost_groups, rank_mehfil_active_users, remove_inactive_members,\
retrieve_all_member_ids, group_owner_administrative_interest
from redis7 import record_vote, retrieve_obj_feed, add_obj_to_home_feed, get_photo_feed, add_photos_to_best_photo_feed, delete_avg_hash, insert_hash,\
cleanse_all_feeds_of_user_content, delete_temporarily_saved_content_details, cleanse_inactive_complainers, account_created, set_top_stars, get_home_feed,\
add_posts_to_best_posts_feed, get_world_age_weighted_vote_score, add_single_trending_object, trim_expired_user_submissions, push_hand_picked_obj_into_trending,\
queue_obj_into_trending, in_defenders, remove_obj_from_trending, calculate_top_trenders, calculate_bayesian_affinity, cleanse_voting_records, \
study_voting_preferences, retrieve_voting_affinity,retrieve_obj_scores, add_single_trending_object_in_feed, get_best_home_feed, retire_abandoned_topics,\
cache_detailed_voting_data, log_vote_for_ab_test
from redis8 import set_section_wise_retention, log_segment_action
from redis3 import log_vote_disc
from ecomm_tracking import insert_latest_metrics
from links.azurevids.azurevids import uploadvid
from namaz_timings import namaz_timings, streak_alive
from django.contrib.auth.models import User
from facebook_api import photo_poster
from math import log

# from mixpanel import Mixpanel
# from unconnectedreddit.settings import MIXPANEL_TOKEN

# mp = Mixpanel(MIXPANEL_TOKEN)

VOTE_WEIGHT = 1.5 # used for calculating daily benchmark
FLOOR_PERCENTILE = 0.5
CEILING_PERCENTILE = 0.9 # (inclusive)
MIN_FANS_TARGETED = 0.1 # 10%
MAX_FANS_TARGETED = 0.95 # 95%



# def get_page(index,objs_per_page):
# 	page = (index // objs_per_page)+1 #determining page number
# 	return page


# def get_page_obj(page_num,obj_list,items_per_page):
# 	# pass list of objects and number of objects to show per page, it does the rest
# 	paginator = Paginator(obj_list, items_per_page)
# 	try:
# 		return paginator.page(page_num)
# 	except PageNotAnInteger:
# 		# If page is not an integer, deliver first page.
# 		return paginator.page(1)
# 	except EmptyPage:
# 		# If page is out of range (e.g. 9999), deliver last page of results.
# 		return paginator.page(paginator.num_pages)

def get_credentials(user_id, uname=None, avurl=None):
	if not uname and not avurl:
		# both dont exist
		uname, avurl = retrieve_credentials(user_id, decode_uname=True)
	elif avurl:
		# uname doesnt exist
		uname = retrieve_uname(user_id,decode=True)
	elif uname:
		# avurl desn't exist
		avurl = retrieve_avurl(user_id)
	else:
		# both exist, do nothing
		pass
	return uname, avurl


def convert_to_epoch(time):
	return (time-datetime(1970,1,1)).total_seconds()


def set_rank(netvotes, upload_time):
	"""
	Based on reddit ranking algo at https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9
	"""
	# if netvotes is None:
	#     netvotes = 0
	# order = log(max(abs(netvotes), 1), 10)
	# if netvotes > 0:
	#     sign = 1
	# else:
	#     sign = -1
	# secs = upload_time - 1432201843 # Thu, 21 May 2015 09:50:43 GMT coverted to epoch time
	# return round(sign * order + secs / 45000, 8)
	##############################################################################
	"""
	Added a time factor to ensure 'newer' photos are given more preference all else equal
	"""
	secs = upload_time - 1432201843 # Thu, 21 May 2015 09:50:43 GMT coverted to epoch time
	return round(netvotes+secs/45000,8)


def fans_targeted(current_percentile):
	overall_range = CEILING_PERCENTILE - FLOOR_PERCENTILE
	current_range = current_percentile - FLOOR_PERCENTILE
	proportion = (current_range*1.0)/overall_range
	fans_targeted_delta = MAX_FANS_TARGETED - MIN_FANS_TARGETED
	percentage_to_target = (proportion * fans_targeted_delta * 1.0) + MIN_FANS_TARGETED
	return percentage_to_target

def fans_to_notify_in_ua(user_id, percentage_of_fans_to_notify,fan_ids_list):
	num_of_fans_to_notify = len(fan_ids_list) * percentage_of_fans_to_notify
	if num_of_fans_to_notify:
		fan_ids_to_notify = get_active_fans(user_id,int(num_of_fans_to_notify))
	try:
		fan_ids_to_notify = map(int, fan_ids_to_notify)
		remaining_fan_ids = set(fan_ids_list) - set(fan_ids_to_notify)
		return remaining_fan_ids, fan_ids_to_notify
	except:
		return fan_ids_list,0

def punish_gibberish_writers(dict_of_targets):
	for user_id, score_penalty in dict_of_targets.items():
		UserProfile.objects.filter(user_id=user_id).update(score=F('score')-score_penalty)
		queue_punishment_amount(user_id,score_penalty)


@celery_app1.task(name='tasks.cache_photo_shares')
def cache_photo_shares(json_photo_data, user_id):
	cache_photo_share_data(json_photo_data, user_id)

@celery_app1.task(name='tasks.invalidate_avatar_url')
def invalidate_avatar_url(user_id,set_rate_limit=False):
	invalidate_avurl(user_id, set_rate_limit)
	invalidate_cached_user_data(user_id)

@celery_app1.task(name='tasks.photo_sharing_metrics_and_rate_limit')
def photo_sharing_metrics_and_rate_limit(sharer_id, photo_id, photo_owner_id, num_shares, sharing_time, group_ids):
	#rate limiting sharing
	rate_limit_personal_group_sharing(sharer_id)
	#logging metrics
	logging_sharing_metrics(sharer_id, photo_id, photo_owner_id, num_shares, sharing_time, group_ids)


@celery_app1.task(name='tasks.add_image_to_personal_group_storage')
def add_image_to_personal_group_storage(img_url, img_id, img_wid, hw_ratio, img_quality, blob_id, index, own_id, group_id, is_shared=False, op=None):
	if is_shared:
		set_personal_group_image_storage(img_url, img_id, img_wid, hw_ratio, img_quality, blob_id, index, own_id, group_id, True, op)
	else:
		set_personal_group_image_storage(img_url, img_id, img_wid, hw_ratio, img_quality, blob_id, index, own_id, group_id)


@celery_app1.task(name='tasks.personal_group_trimming_task')
def personal_group_trimming_task(group_id, object_count):
	trim_personal_group(group_id,object_count)


# @celery_app1.task(name='tasks.queue_personal_group_invitational_sms')
# def queue_personal_group_invitational_sms(mobile_number, sms_text, own_id, target_id, sending_time):
# 	send_personal_group_sms(mobile_number, sms_text)
# 	track_p2p_sms(own_id, target_id, sending_time)

@celery_app1.task(name='tasks.cache_personal_group')
def cache_personal_group(pg_data, group_id):
	cache_personal_group_data(pg_data,group_id)


@celery_app1.task(name='tasks.private_chat_tasks')
def private_chat_tasks(own_id, target_id, group_id, posting_time, text, txt_type, own_anon='', target_anon='', blob_id='', idx='', img_url='', own_uname='', \
	own_avurl='',deleted='',hidden='',successful=True, from_unseen=False, sharing=False):
	if successful:
		mark_personal_group_attendance(own_id, target_id, group_id, posting_time)
		own_uname, own_avurl = get_credentials(own_id, own_uname, own_avurl)
		pgh, index = "pgh:"+group_id+":"+blob_id if blob_id else '', idx if (idx and int(idx) > 0) else ''
		updated = update_private_chat_notif_object(group_id=group_id,lt_res_wid=own_id,lt_res_sub_name=own_uname,lt_res_avurl=own_avurl,\
			lt_res_time=posting_time,lt_res_text=text,reply_photourl=img_url,res_count=index,object_desc=txt_type,lt_pgh=pgh,deleted=deleted,\
			hidden=hidden,update=True)
		if not updated:
			own_anon, target_anon, group_id = get_personal_group_anon_state(own_id,target_id)
			their_uname, their_avurl = get_credentials(target_id)
			update_private_chat_notif_object(group_id=group_id,lt_res_wid=own_id,lt_res_sub_name=own_uname,lt_res_avurl=own_avurl,hidden=hidden,\
			lt_res_time=posting_time,lt_res_text=text,reply_photourl=img_url,res_count=index,object_desc=txt_type,lt_pgh=pgh,deleted=deleted,\
			anon1=own_id if own_anon else '',anon2=target_id if target_anon else '',target_uname=their_uname,target_avurl=their_avurl, \
			target_id=target_id)
		update_private_chat_notifications(sender_id=own_id, receiver_id=target_id, group_id=group_id, sender_seen=True, receiver_seen=False,\
			updated_at=posting_time,sender_ua=True,receiver_ua=True,sender_sn=False,receiver_sn=True,sender_bump_ua=True,receiver_bump_ua=True)
		if from_unseen or sharing:
			update_personal_group_last_seen(own_id, group_id, posting_time)#supposed to update 'seen' of contributer
		# All txt_types are: 'notif','img','img_res','text','text_res','action','reentry','exited','creation','shared_img'
		if txt_type in ('text','text_res','img_res','img','shared_img'):
			set_uri_metadata_in_personal_group(own_id, text, group_id, blob_id, idx, txt_type)#Checks content and turns URLs clickable
		elif txt_type == 'exited':
			log_personal_group_exit_or_delete(group_id, exit_by_id=str(own_id), action_type='exit')
		################### Logging 1on1 message ###################
		# if txt_type == 'shared_img':
		# 	payload = str(posting_time)+":"+txt_type+":"+img_url[-47:]+":"+str(own_id)+":"+target_id+":"+text
		# else:
		# 	payload = str(posting_time)+":"+txt_type+":"+img_url+":"+str(own_id)+":"+target_id+":"+text
		# log_1on1_chat(payload=payload,oid=own_id,tid=target_id, group_id=group_id)
		
		##############################################################

@celery_app1.task(name='tasks.update_notif_object_anon')
def update_notif_object_anon(value,which_user,which_group):
	update_pg_obj_anon(value=value,object_id=which_group,user_id=which_user)

@celery_app1.task(name='tasks.update_notif_object_del')
def update_notif_object_del(group_id, action=None, blob_id=None,idx=None,bulk_deletion=False):
	if bulk_deletion:
		# bulk deletion was called in personal group, handle notif object accordingly
		update_pg_obj_notif_after_bulk_deletion(group_id)
	else:
		update_pg_obj_del(action,blob_id,idx,group_id)

@celery_app1.task(name='tasks.update_notif_object_hide')
def update_notif_object_hide(action,blob_id,idx,group_id):
	update_pg_obj_hide(action,blob_id,idx,group_id)


@celery_app1.task(name='tasks.private_chat_seen')
def private_chat_seen(own_id, group_id, curr_time):
	"""
	Called every time a private chat is refreshed (or 'seen'). 

	But not called from 'from_unseen' or 'sharing'
	"""
	skip_private_chat_notif(own_id, group_id,curr_time, seen=True)


# execute every 3 days
@celery_app1.task(name='tasks.delete_chat_from_idle_personal_group')
def delete_chat_from_idle_personal_group():
	personal_group_soft_deletion()

# execute every 6 days
@celery_app1.task(name='tasks.delete_idle_personal_group')
def delete_idle_personal_group():
	personal_group_hard_deletion()


# execute daily
@celery_app1.task(name='tasks.delete_exited_personal_group')
def delete_exited_personal_group():
	exited_personal_group_hard_deletion()


@celery_app1.task(name='tasks.post_banning_tasks')
def post_banning_tasks(own_id, target_id):
	"""
	Remove's banner's notification from from the bannee's matka, also unfans them.

	It's a good-to-have task, not mission critical (and can be improved).
	Problems include: 
	1) If bannee wanted to eavesdrop on banner's posts, they could do so in myriad of ways
	2) In fact, much better to design a new matka which includes the '@' functionality, deprecate this prototypical one.
	"""
	# unfan (in case was a fan)
	UserFan.objects.filter(fan_id=own_id, star_id=target_id).delete()
	UserFan.objects.filter(fan_id=target_id, star_id=own_id).delete()
	remove_from_photo_owner_activity(photo_owner_id=own_id, fan_id=target_id)
	remove_from_photo_owner_activity(photo_owner_id=target_id, fan_id=own_id)
	rate_limit_unfanned_user(own_id=own_id,target_id=target_id)
	################################################################################
	# this ensures all posts of eachothers are deleted from the matka
	sanitize_eachothers_unseen_activities(user1_id=own_id, user2_id=target_id)
	################################################################################
	# 1) Exit yourself if group is non-exited
	# 2) If 'target' has already exited group, tell them they can't re-enter because the other party outright blocked them!
	# 3) No notifications will be generated since we already sanitized each user's activity
	# this ensures they can't private chat with eachother
	exit_user_from_targets_priv_chat(own_id,target_id)
	################################################################################
	# we did a LOT of work, ensure banner didn't ban in vain!
	ratelimit_banner_from_unbanning_target(own_id,target_id)
	################################################################################


@celery_app1.task(name='tasks.sanitize_expired_bans')
def sanitize_expired_bans(own_id, banned_ids_to_unban):
	remove_banned_users_in_bulk(own_id, banned_ids_to_unban)


@celery_app1.task(name='tasks.increase_user_points')
def increase_user_points(user_id, increment):
	UserProfile.objects.filter(user_id=user_id).update(score=F('score')+increment)

@celery_app1.task(name='tasks.save_consumer_credentials')
def save_consumer_credentials(account_kit_id, mobile_data, user_id):
	save_consumer_number(account_kit_id=account_kit_id, mobile_data=mobile_data, user_id=user_id)

@celery_app1.task(name='tasks.save_unfinished_ad')
def save_unfinished_ad(context):
	save_single_unfinished_ad(context)

@celery_app1.task(name='tasks.save_ecomm_photo_hash')
def save_ecomm_photo_hash(photo1_payload, photo2_payload, photo3_payload):
	if photo1_payload:
		photo1_payload = ast.literal_eval(photo1_payload)
		insert_hash(photo1_payload[0],photo1_payload[1],'ecomm') #perceptual hash of item photo 1
	if photo2_payload:
		photo2_payload = ast.literal_eval(photo2_payload)
		insert_hash(photo2_payload[0],photo2_payload[1],'ecomm') #perceptual hash of item photo 2
	if photo3_payload:
		photo3_payload = ast.literal_eval(photo3_payload)
		insert_hash(photo3_payload[0],photo3_payload[1],'ecomm') #perceptual hash of item photo 3

@celery_app1.task(name='tasks.upload_ecomm_photo')
def upload_ecomm_photo(photo_id, user_id, ad_id):
	# insert_hash(photo_id, avghash, 'ecomm') #perceptual hash of the item photo
	save_used_item_photo(user_id, ad_id, photo_id)

@celery_app1.task(name='tasks.sanitize_unused_ecomm_photos')
def sanitize_unused_ecomm_photos():
	"""
	Scans all votes given by users and calculates sybil affinities via a Bayesian calculation

	Scheduled to run every 6 hours
	Mislabelled for legacy reasons
	"""
	study_voting_preferences()


@celery_app1.task(name='tasks.set_user_binding_with_twilio_notify_service')
def set_user_binding_with_twilio_notify_service(user_id,phone_number):
	bind_user_to_twilio_notify_service(user_id,phone_number)

# execute every 55 mins
@celery_app1.task(name='tasks.expire_classifieds')
def expire_classifieds():
	process_ad_expiry()

# execute every 2 days
@celery_app1.task(name='tasks.delete_expired_classifieds')
def delete_expired_classifieds():
	process_ad_final_deletion()

# execute every 24 hours
@celery_app1.task(name='tasks.calc_ecomm_metrics')
def calc_ecomm_metrics():
	insert_latest_metrics()


# @celery_app1.task(name='tasks.log_gibberish_writer')
# def log_gibberish_writer(user_id,text,length_of_text):
# 	if length_of_text > 10 and ' ' not in text:
# 		log_gibberish_text_writer(user_id)
# 		# log_spam_text_writer(user_id, text)
# 	else:
# 		tokens = text[:12].split()
# 		if len(tokens) > 1:
# 			first_word = tokens[0]
# 			len_first_word = len(first_word)
# 			offset = text[len_first_word:].find(first_word)
# 			if offset > -1:
# 				first_start = len_first_word+offset
# 				first_end = first_start+len_first_word
# 				first_repetition = text[first_start:first_end]
# 				if first_word == first_repetition:
# 					second_start = first_end + offset
# 					second_end = second_start+len_first_word
# 					second_repetition = text[second_start:second_end]
# 					if first_repetition == second_repetition:
# 						third_start = second_end + offset
# 						third_end = third_start + len_first_word
# 						third_repetition = text[third_start:third_end]
# 						if third_repetition == second_repetition:
# 							log_gibberish_text_writer(user_id)
# 							# log_spam_text_writer(user_id, text)


@celery_app1.task(name='tasks.log_action')
def log_action(user_id, action_categ, action_sub_categ, action_liq, time_of_action):
	"""
	Logs user action for segment analysis
	"""
	hours_since_start_of_segment = int((time_of_action - SEGMENT_STARTING_TIME)/3600.0)
	log_segment_action(user_id, hours_since_start_of_segment, action_categ, action_sub_categ, action_liq, time_of_action)

# @celery_app1.task(name='tasks.set_section_retention')
# def set_section_retention(which_section, user_id):
# 	"""
# 	Logs users for retention calculation of various sections of the app

# 	Sections include 'private_mehfil', 'public_mehfil', 'private_chat' currently
# 	"""
# 	set_section_wise_retention(which_section, user_id)

@celery_app1.task(name='tasks.set_user_age')
def set_user_age(user_id):
	"""
	Task that increments user's age in the world
	"""
	set_world_age(user_id)


@celery_app1.task(name='tasks.log_404')
def log_404(type_of_404, time_of_404, type_of_url=None):
	"""
	Logs 404 errors seen throughout the website

	Currently only logging 404 errors emanating from UserProfilePhotosView()
	"""
	log_404_errors(type_of_404, time_of_404, type_of_url)

########################### priv chat split test ########


# @celery_app1.task(name='tasks.priv_msg_sent_logger')
# def priv_msg_sent_logger(user_id, group_id):
# 	"""
# 	Increment chat for group in A/B test
# 	"""
# 	log_message_sent(user_id,group_id)

# @celery_app1.task(name='tasks.priv_invite_accepted_logger')
# def priv_invite_accepted_logger(user_id, group_id):
# 	"""
# 	Logging group for A/B test
# 	"""
# 	log_invite_accepted(user_id, group_id)

######################################################


@celery_app1.task(name='tasks.save_online_user')
def save_online_user(user_id,user_ip):
	set_online_users(str(user_id),str(user_ip),get_world_age(user_id))


@celery_app1.task(name='tasks.whoseonline')
def whoseonline():
	"""
	Periodically assesses who all is online (to be shown to users in a global online page)
	"""
	user_ids_and_ages = get_recent_online()
	save_most_recent_online_users(user_ids_and_ages)


@celery_app1.task(name='tasks.detail_click_logger')
def detail_click_logger(ad_id, clicker_id):
	log_detail_click(ad_id, clicker_id)


# @celery_app1.task(name='tasks.log_organic_attention')
# def log_organic_attention(photo_id,att_giver,photo_owner_id, action, vote_value=None):
# 	log_photo_attention_from_fresh(photo_id, att_giver, photo_owner_id, action, vote_value)



@celery_app1.task(name='tasks.enqueue_sms')
def enqueue_sms(mobile_number, ad_id, status=None, buyer_number=None, item_name=None):
	process_sms(mobile_number,ad_id,status, buyer_number, item_name)

# @celery_app1.task(name='tasks.enqueue_buyer_sms')
# def enqueue_buyer_sms(mobile_number, ad_id, order_data, buyer_number=None):
# 	cleansed_data = "Name="+str(order_data['firstname'])+",City="+ str(order_data['address'])+",Phone="+str(order_data['phonenumber'])+",Order#="+ str(order_data['order_id'])+",Model="+str(order_data['model'])
# 	process_buyer_sms(mobile_number,ad_id,str(cleansed_data), buyer_number)

@celery_app1.task(name='tasks.enqueue_buyer_sms')
def enqueue_buyer_sms(mobile_number, ad_id, order_data, buyer_number=None):
	cleansed_data = "Name="+str(order_data['firstname'])+",City="+ str(order_data['address'])+",Phone=+92"+str(order_data['phonenumber'][1:])+",Order#="+ str(order_data['order_id'])+",Model="+str(order_data['model'])
	process_buyer_sms(mobile_number,ad_id,str(cleansed_data), buyer_number)


@celery_app1.task(name='tasks.enqueue_orderer_sms')
def enqueue_orderer_sms(mobile_number, ad_id, order_data, buyer_number=None):
	cleansed_data = "Assalam-o-Alikum! Apka "+str(order_data['model'])+" ka order hamarey pas agya hai. Mobile shop ka numainda apko jald call keray ga. Shukriya :-)"
	process_buyer_sms(mobile_number,ad_id,str(cleansed_data), buyer_number)

@celery_app1.task(name='tasks.send_orderer_pin')
def send_orderer_pin(mobile_number, pin, order_data, buyer_number=None):
	cleansed_data = "Aap ka pin code hai '"+str(pin)+"'. Iss pin ko mobile shop ki confirm order ki screen per dalien aur apna "+str(order_data)+" ghar mangaien."
	cleansed_data2 = "Pin code: '"+str(pin)+"' Mob# "+str(mobile_number)+"' Phone model: "+str(order_data)
	mobile_number2 = '+923491058364'
	process_buyer_sms(mobile_number,pin,str(cleansed_data), buyer_number)
	process_buyer_sms(mobile_number2,pin,str(cleansed_data2), buyer_number)

@celery_app1.task(name='tasks.send_user_pin')
def send_user_pin(sender_id, mobile_number):
	"""
	This function sends the pin code to user (for home-grown verification purposes)
	"""
	pin = retrieve_random_pin(sender_id)
	payload = "Salam! %s apka Damadam pin code hai. Isko pin code wali screen mein enter karein. Have a nice day & enjoy Damadam.pk :-)" % (pin)
	process_user_pin_sms(mobile_number,payload)

@celery_app1.task(name='tasks.enqueue_query_sms')
def enqueue_query_sms(mobile_number, ad_id, order_data, buyer_number=None):
	cleansed_data = "Assalam-o-Alikum! Apko 03105430851 se Damadam Mobile Shop ka numainda rabta kare ga. Ap khud bhi is number per rabta kr sakte hein. Shukriya :-)"
	process_buyer_sms(mobile_number,ad_id,str(cleansed_data), buyer_number)

@celery_app1.task(name='tasks.delete_notifications')
def delete_notifications(user_id):
	clean_expired_notifications(user_id)

@celery_app1.task(name='tasks.calc_gibberish_punishment')
def calc_gibberish_punishment():
	all_gibberish_writers = get_gibberish_text_writers()
	if all_gibberish_writers:
		all_gibberish_writers_above_threshold = {k:v for k,v in all_gibberish_writers if v>3}
		if all_gibberish_writers_above_threshold:
			gibberish_punishment = {}
			for k in all_gibberish_writers_above_threshold.keys():
				all_gibberish_writers_above_threshold[k] *= GIBBERISH_PUNISHMENT_MULTIPLIER
			punish_gibberish_writers(all_gibberish_writers_above_threshold)


@celery_app1.task(name='tasks.calc_photo_quality_benchmark')
def calc_photo_quality_benchmark():
	two_days = datetime.utcnow()-timedelta(hours=24*2)
	photos_total_score_list = Photo.objects.filter(upload_time__gte=two_days).values_list('owner_id','vote_score')#list of tuples
	# print photos_total_score_list
	if photos_total_score_list:
		total_photos_per_user = Counter(elem[0] for elem in photos_total_score_list) #dictionary, e.g. Counter({2: 8, 1: 7})
		# print "total photos per user: %s" % total_photos_per_user
		total_scores_per_user = defaultdict(int)# a python dictionary that doesn't give KeyError if key doesn't exist when dict is accessed
		for key,val in photos_total_score_list:
			total_scores_per_user[key] += val #ends with with {owner_id:total_photo_score}
		# print "total scores per user: %s" % total_scores_per_user
		uploader_scores = []
		for key,val in total_scores_per_user.items():
			uploader_scores.append(key)
			uploader_scores.append(float(val)/total_photos_per_user[key])#avg score per photo
		# print uploader_scores
		set_benchmark(uploader_scores)# sets own_ids and avg score per photo in a huge sorted set called photos_benchmark

@celery_app1.task(name='tasks.bulk_create_notifications')
def bulk_create_notifications(user_id, photo_id, epochtime, photourl, name, caption):
	fan_ids_list, total_fans, recent_fans = get_all_fans(user_id)
	if fan_ids_list:
		fans_notified_in_ua = 0
		percentage_of_users_beaten = get_uploader_percentile(user_id)
		if 0 <= percentage_of_users_beaten < FLOOR_PERCENTILE:
			notify_in_ua = []
			fans_notified_in_ua = 0
			percentage_of_fans_to_notify = 0
			bulk_create_photo_notifications_for_fans(viewer_id_list=fan_ids_list,object_id=photo_id,seen=False,updated_at=epochtime,\
				unseen_activity=False)
		elif FLOOR_PERCENTILE <= percentage_of_users_beaten <= CEILING_PERCENTILE:
			percentage_of_fans_to_notify = fans_targeted(percentage_of_users_beaten)
			remaining_ids, notify_in_ua = fans_to_notify_in_ua(user_id, percentage_of_fans_to_notify, fan_ids_list)
			if notify_in_ua:
				bulk_create_photo_notifications_for_fans(viewer_id_list=notify_in_ua,object_id=photo_id,seen=False,\
					updated_at=epochtime,unseen_activity=True)
				fans_notified_in_ua = len(notify_in_ua)
			else:
				fans_notified_in_ua = 0
			bulk_create_photo_notifications_for_fans(viewer_id_list=remaining_ids,object_id=photo_id,seen=False,\
				updated_at=epochtime,unseen_activity=False)
		elif CEILING_PERCENTILE < percentage_of_users_beaten <= 1:
			fans_notified_in_ua = len(fan_ids_list)
			notify_in_ua = fan_ids_list
			percentage_of_fans_to_notify = 1
			bulk_create_photo_notifications_for_fans(viewer_id_list=fan_ids_list,object_id=photo_id,seen=False,updated_at=epochtime,\
				unseen_activity=True)
		else:
			notify_in_ua = 0
			fans_notified_in_ua = 0
			percentage_of_fans_to_notify = 0
			bulk_create_photo_notifications_for_fans(viewer_id_list=fan_ids_list,object_id=photo_id,seen=False,updated_at=epochtime,\
				unseen_activity=False)
		# object and notification for self, that reports how many fans we reached out to!
		create_object(object_id=photo_id, object_type='1',object_owner_id=user_id,photourl=photourl, vote_score=total_fans, \
			slug=fans_notified_in_ua, res_count=notify_in_ua,is_thnks=percentage_of_fans_to_notify,object_owner_name=name, \
			object_desc=caption)
		create_notification(viewer_id=user_id,object_id=photo_id,object_type='1',seen=False, updated_at=epochtime,\
			unseen_activity=True)

@celery_app1.task(name='tasks.trim_top_group_rankings')
def trim_top_group_rankings():
	"""
	Periodically trim the global sets containing all public submissions flowing into Damadam

	Mislabeled for legacy reasons
	"""
	trim_expired_user_submissions()

@celery_app1.task(name='tasks.trim_whose_online')
def trim_whose_online():
	expire_online_users()


@celery_app1.task(name='tasks.remove_target_users_posts_from_all_feeds')
def remove_target_users_posts_from_all_feeds(target_user_id, cleanse_feeds):
	"""
	If defender bans a user, remove said users' content from all current feeds
	"""
	trim_expired_user_submissions(submitter_id=target_user_id, cleanse_feeds=cleanse_feeds)



@celery_app1.task(name='tasks.delete_temporarily_saved_content_data')
def delete_temporarily_saved_content_data(own_id):
	"""
	Delete temporarily saved data
	"""
	delete_temporarily_saved_content_details(own_id)


#paying back points spent by photo reporters
@celery_app1.task(name='tasks.process_reporter_payables')
def process_reporter_payables(payables):
	"""
	Paying back points spent by reporters (currently points paid are set to 0)
	"""
	if payables:
		for user_id,payable_score in payables:
			if payable_score:
				UserProfile.objects.filter(user_id=user_id).update(score=F('score')+payable_score)


@celery_app1.task(name='tasks.populate_search_thumbs')
def populate_search_thumbs(user_id,ids_with_urls):
	"""
	Auto-populating photo thumbs in search results, end of photo comments, etc

	Triggered whenever a user profile is visited
	"""
	bulk_add_search_photos(user_id,ids_with_urls)


@celery_app1.task(name='tasks.sanitize_erroneous_notif')
def sanitize_erroneous_notif(notif_name, user_id):
	remove_erroneous_notif(notif_name, user_id)

@celery_app1.task(name='tasks.document_administrative_activity')
def document_administrative_activity(group_id, main_sentence, history_type):
	"""
	Logs an action in a mehfil's administrative activity

	Moreover, acts as a helper function for construct_administrative_activity()
	"""
	add_to_universal_group_activity(group_id, main_sentence, history_type)

@celery_app1.task(name='tasks.construct_administrative_activity')
def construct_administrative_activity(punisher_id, target_id, time_now, group_id, history_type, reply_id=None):
	"""
	Logs 'hide' and 'unhide' activity in publc mehfil administrative history

	A more involved version of document_administrative_activity() since it constructs the main sentence itself
	In the end, it calls document_administrative_activity() to get the job done
	"""    
	username_dictionary = retrieve_bulk_unames([punisher_id,target_id],decode=True)
	text = retrieve_single_group_submission(group_id, reply_id, text_only=True)
	if history_type == 'hide':
		partial_sentence = username_dictionary[punisher_id]+" ne "+username_dictionary[int(target_id)]+\
		" ki baat hide ki at {0}".format(exact_date(time_now))
	elif history_type == 'unhide':
		partial_sentence = username_dictionary[punisher_id]+" ne "+username_dictionary[int(target_id)]+\
		" ki baat unhide ki at {0}".format(exact_date(time_now))
	main_sentence = partial_sentence+". Text: "+text if text else partial_sentence
	document_administrative_activity(group_id, main_sentence, history_type)


#used to calculate group ranking
# @celery_app1.task(name='tasks.public_group_vote_tasks')
# def public_group_vote_tasks(group_id,priority):
# 	public_group_vote_incr(group_id,priority)

@celery_app1.task(name='tasks.cleanse_complainers')
def cleanse_complainers():
	cleanse_inactive_complainers()


@celery_app1.task(name='tasks.rank_mehfils')
def rank_mehfils():
	rank_mehfil_active_users()


@celery_app1.task(name='tasks.public_group_ranking_clean_up_task')
def public_group_ranking_clean_up_task():
	"""
	Calculates top list of photo-uploaders who have highest contributions to trending photos in a specific time period

	Mislabeled task due to legacy reasons
	"""
	calculate_top_trenders()


@celery_app1.task(name='tasks.log_group_owner_interaction')
def log_group_owner_interaction(group_id, time_now):
	"""
	Logs the last 'seen' time of when a group owner did something meaninful in their public group
	"""
	group_owner_administrative_interest(group_id, time_now)


@celery_app1.task(name='tasks.group_attendance_tasks')
def group_attendance_tasks(group_id,user_id, time_now):#, private=False):
	"""
	Tracking user presence in a group so that we can show online users in a group or show their 'online' dots
	"""
	inactive_user_ids = group_attendance(group_id,user_id, time_now)
	if inactive_user_ids:
		remove_inactive_members(inactive_user_ids, group_id, time_now)

@celery_app1.task(name='tasks.update_group_topic')
def update_group_topic(group_id, topic):
	"""
	Updates group topic in notification object
	"""
	update_group_topic_in_obj(group_id, topic)

#####################################################################################################

# execute every 2 days
@celery_app1.task(name='tasks.empty_idle_public_and_private_groups')
def empty_idle_public_and_private_groups():
	"""
	Deletes all chat within an 'empty' group

	Idle groups are those that don't have any activity for 7 days (activity includes refreshes!)
	"""
	empty_idle_groups()


# execute every 4 days
@celery_app1.task(name='tasks.delete_idle_public_and_private_groups')
def delete_idle_public_and_private_groups():
	"""
	Deleting 'ghost' groups for good (when it's been idle for 30 days, we call it a 'ghost' group)
	"""
	# grp_ids_and_members is a dict of the sort { group_id:[member_ids] }

	grp_ids_and_members = delete_ghost_groups()#redis6
	bulk_remove_multiple_group_notifications(grp_ids_and_members)#redis2
	# cleanse_public_and_private_groups_data(grp_ids_and_members)#redis1 (DEPRECATE THIS ENTIRE FUNCTIONALITY)
	# marking postgresql Group object as deleted (deprecate this later)
	# group_ids = grp_ids_and_members.keys()
	# if group_ids:
	# 	Group.objects.filter(id__in=group_ids).update(category='99')#'99' implies deleted


@celery_app1.task(name='tasks.trim_group_submissions')
def trim_group_submissions(group_id):
	"""
	Trims down mehfil submissions once it attains a certain size
	"""
	del_overflowing_group_submissions(group_id,NUM_TO_DELETE)


@celery_app1.task(name='tasks.group_notification_tasks')
def group_notification_tasks(group_id,sender_id,group_owner_id,topic,reply_time,poster_url,poster_username,reply_text,priv,\
	image_url,priority,from_unseen, slug=None, txt_type=None, notify_single_user=False, single_target_id=None):
	if txt_type == 'join':
		# own self has seen this, and no need to show a notification to other users
		###############################
		updated=update_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
			unseen_activity=True,single_notif=False,priority=priority,bump_ua=True)
		if not updated:
			create_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
				unseen_activity=True, check_parent_obj=True)# matka notif won't be created if original object doesn't exist
	else:
		if from_unseen:
			# i.e. from unseen_group() in views.py
			update_object(object_id=group_id,object_type='3',lt_res_time=reply_time,lt_res_avurl=poster_url,lt_res_text=reply_text,\
				lt_res_sub_name=poster_username,reply_photourl=image_url,lt_res_wid=sender_id)
		else:
			created = create_object(object_id=group_id,object_type='3',object_owner_id=group_owner_id,object_desc=topic,\
				lt_res_time=reply_time,lt_res_avurl=poster_url,lt_res_sub_name=poster_username,lt_res_text=reply_text,\
				group_privacy=priv,slug=slug, lt_res_wid=sender_id)
			if not created:
				update_object(object_id=group_id,object_type='3',lt_res_time=reply_time,lt_res_avurl=poster_url,lt_res_text=reply_text,\
					lt_res_sub_name=poster_username,reply_photourl=image_url, lt_res_wid=sender_id)
		###############################
		# updating notification for single target or bulk targets
		if notify_single_user and single_target_id:
			# notify just a single targeted user (i.e. used in a direct response in mehfils)
			update_notification(viewer_id=single_target_id,object_id=group_id,object_type='3',seen=False,updated_at=reply_time,\
				unseen_activity=True,single_notif=True,priority=priority,bump_ua=True)
		else:
			all_group_member_ids = retrieve_all_member_ids(group_id)
			all_group_member_ids.remove(str(sender_id))
			if all_group_member_ids:
				# this does NOT update notifications for users whose notification object was deleted (or wasn't created in the first place)
				bulk_update_notifications(viewer_id_list=all_group_member_ids,object_id=group_id,object_type='3',seen=False,
					updated_at=reply_time,single_notif=True,unseen_activity=True,priority=priority)
		###############################
		# updating notification for sender
		updated = update_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
			unseen_activity=True,single_notif=False,priority=priority,bump_ua=True)
		if not updated:
			create_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
				unseen_activity=True)
		if priv == '1':
			log_group_chatter(group_id, sender_id)# redis 6
			if image_url:
				increment_pic_count(group_id, sender_id)#redis 6


# @celery_app1.task(name='tasks.log_private_mehfil_session')
# def log_private_mehfil_session(group_id,user_id):# called every time a private mehfil is refreshed
# 	increment_session(str(group_id), user_id, group_type='pm')
	

@celery_app1.task(name='tasks.rank_all_photos')
def rank_all_photos():
	"""
	Used to find the single "best" foto from the current lot, criteria being an image with positive cumulative vote score, and at least 1 downvote

	Can also push hand-picked objects into trending lists
	Mislabeled task due to legacy reasons
	"""
	time_now = time.time()
	pushed, obj_id = push_hand_picked_obj_into_trending()
	if pushed:
		# TODO: send this to Facebook fan page
		pass
	else:
		fresh_photo_ids = get_photo_feed(feed_type='fresh_photos')#fresh photos in hash format
		best_photo_ids = get_photo_feed(feed_type='best_photos')#trending photos in hash format
		remaining_fresh_photo_ids = [id_ for id_ in fresh_photo_ids if id_ not in best_photo_ids]#unselected photos so far
		trending_item_hash_name, item_score = extract_trending_obj(remaining_fresh_photo_ids, with_score=True)
		if trending_item_hash_name:
			highest_ranked_photo = retrieve_obj_feed([trending_item_hash_name])[0]
			highest_ranked_photo['tos'] = time_now
			highest_ranked_photo['rank_scr'] = item_score
			obj_id = trending_item_hash_name.split(":")[1]
			add_single_trending_object(prefix="img:",obj_id=trending_item_hash_name.split(":")[1], obj_hash=highest_ranked_photo)
			pushed = True
	###############################
	if pushed and obj_id:
		cohort_num = int(time_now/604800)#cohort size is 1 week
		Logout.objects.create(logout_user_id=obj_id,pre_logout_score=cohort_num)


@celery_app1.task(name='tasks.rank_all_photos1')
def rank_all_photos1():
	"""
	Sanitize unused notification subscriptions
	"""
	sanitize_unused_subscriptions()


def extract_trending_obj(obj_hash_names, with_score=False):
	"""
	Given a list of hashes, singles out the hash_obj which tops our score criteria

	Current criteria requires the top most obj to have the highest cumulative_vote_score but with at least one downvote
	"""
	obj_list = retrieve_obj_scores(obj_hash_names, with_downvotes=True)
	only_downvoted = []
	for obj_hash, score, downvotes in obj_list:
		# ensure that the post is downvoted, but has a positive cumulative score
		if downvotes > 0 and score > 0:
			only_downvoted.append((obj_hash, score))
	if only_downvoted:
		only_downvoted.sort(key=itemgetter(1),reverse=True)
		trending_item_hash_name = only_downvoted[0][0]
		if with_score:
			return trending_item_hash_name, with_score
		else:
			return trending_item_hash_name
	else:
		if with_score:
			return '', None
		else:
			return ''


@celery_app1.task(name='tasks.rank_home_posts')
def rank_home_posts():
	"""
	Celery scheduled task used to sort home posts
	
	Only posts with at least 1 downvote (but the highest cumulative_vote_score) make the cut
	"""
	fresh_obj_hashes = get_home_feed()
	trending_obj_hashes = get_best_home_feed(trending_home=True)
	remaining_obj_hashes = [hash_ for hash_ in fresh_obj_hashes if hash_ not in trending_obj_hashes]
	trending_item_hash_name = extract_trending_obj(remaining_obj_hashes)
	if trending_item_hash_name:
		add_single_trending_object_in_feed(trending_item_hash_name, time.time())


@celery_app1.task(name='tasks.set_input_history')
def set_input_history(section,section_id,text,user_id):
	"""
	Keeps check of writing histories to rate limit repeated posting
	"""
	log_input_text(section,section_id,text,user_id)


@celery_app1.task(name='tasks.set_input_rate_and_history')
def set_input_rate_and_history(section,section_id,text,user_id,time_now):
	"""
	Keeps check of writing rates to rate limit abusive users
	"""
	log_input_text(section, section_id,text,user_id)
	log_input_rate(section,user_id,time_now)


@celery_app1.task(name='tasks.rank_photos')
def rank_photos():
	"""
	Runs every 12 mins from settings.py
	"""
	pass
	# fresh_photo_ids = get_photo_feed(feed_type='fresh_photos')#fresh photos in hash format
	# best_photo_ids = get_photo_feed(feed_type='best_photos')#trending photos in hash format
	# remaining_fresh_photo_ids = [id_ for id_ in fresh_photo_ids if id_ not in best_photo_ids]#unselected photos so far
	# trending_item_hash_name, item_score = extract_trending_obj(remaining_fresh_photo_ids, with_score=True)
	# if trending_item_hash_name:
	# 	highest_ranked_photo = retrieve_obj_feed([trending_item_hash_name])[0]
	# 	highest_ranked_photo['tos'] = time.time()
	# 	highest_ranked_photo['rank_scr'] = item_score
	# 	add_single_trending_object(prefix="img:",obj_id=trending_item.split(":")[1], obj_hash=highest_ranked_photo)


@celery_app1.task(name='tasks.fans')
def fans():
	user_ids = get_top_100()
	user_ids_and_fan_counts = get_fan_counts_in_bulk(user_ids)
	user_ids_and_user_objects = User.objects.select_related('userprofile','totalfanandphotos').defer('password','last_login','is_superuser',\
		'first_name','email','is_staff','is_active','date_joined','id','last_name','totalfanandphotos__total_fans','totalfanandphotos__last_updated',\
		'userprofile__bio','userprofile__shadi_shuda','userprofile__previous_retort','userprofile__attractiveness','userprofile__mobilenumber',\
		'userprofile__score','userprofile__avatar','userprofile__streak','userprofile__age','userprofile__gender').in_bulk(user_ids)
	top_list = []
	for user_id in user_ids:
		top_list.append({'username':user_ids_and_user_objects[int(user_id)].username,'id':user_id,\
			"photo_count":user_ids_and_user_objects[int(user_id)].totalfanandphotos.total_photos,\
			"media_score":user_ids_and_user_objects[int(user_id)].userprofile.media_score,\
			"av_url":retrieve_avurl(user_id),"fan_count":user_ids_and_fan_counts[user_id]})
	top_list = retrieve_thumbs(top_list)# add 'rows' key in the dictionary
	set_top_stars(top_list)


@celery_app1.task(name='tasks.salat_info')
def salat_info():
	"""
	deletes topics that are not getting any traffic

	Mislabeled due to legacy reasons
	"""
	retire_abandoned_topics()


@celery_app1.task(name='tasks.salat_streaks')
def salat_streaks():
	"""
	Cleans up user voting records saved in Redis

	Mislabeled due to legacy reasons
	"""
	cleanse_voting_records()

# @celery_app1.task(name='tasks.queue_for_deletion')
# def queue_for_deletion(link_id_list):
# 	llen = add_to_deletion_queue(link_id_list)
# 	if llen > 200:
# 		delete_queue()


@celery_app1.task(name='tasks.photo_upload_tasks')
def photo_upload_tasks(user_id, photo_id, upload_time, username, temp_photo_obj,number_of_photos, total_score):
	"""
	Tasks fired when a photo is uploaded in the photos section (for public viewing)
	"""
	photo_img_file = Photo.objects.only('image_file').get(id=photo_id).image_file
	updated = TotalFanAndPhotos.objects.filter(owner_id=user_id).update(last_updated=datetime.utcnow()+timedelta(hours=5), total_photos=F('total_photos')+1)
	if not updated:
		TotalFanAndPhotos.objects.create(owner_id=user_id, total_fans=0, total_photos=1, last_updated=datetime.utcnow()+timedelta(hours=5))
	# UserProfile.objects.filter(user_id=user_id).update(score=F('score')-3)
	add_search_photo(photo_img_file, photo_id,user_id)
	if total_score > PHOTO_HOT_SCORE_REQ:
		add_obj_to_home_feed(user_id, upload_time, temp_photo_obj)
	if number_of_photos:
		set_uploader_score(user_id, ((total_score*1.0)/number_of_photos))


@celery_app1.task(name='tasks.unseen_comment_tasks')
def unseen_comment_tasks(user_id, photo_id, epochtime, photocomment_id, count, text, it_exists, commenter, commenter_av, is_citizen):
	user = User.objects.get(id=user_id)
	photo = Photo.objects.select_related('owner__userprofile').get(id=photo_id)
	photo_owner_id = photo.owner_id
	try:
		owner_url = photo.owner.userprofile.avatar.url
	except ValueError:
		owner_url = None
	update_object(object_id=photo_id, object_type='0', lt_res_time=epochtime,lt_res_avurl=commenter_av,lt_res_sub_name=commenter,\
		lt_res_text=text,res_count=(count+1),vote_score=photo.vote_score, lt_res_wid=user_id)
	if photo_owner_id == user_id:
		is_seen = True
		unseen_activity = True
		single_notif = None
		same_writer = True
	else:
		is_seen = False
		unseen_activity = True
		single_notif = True
		same_writer = False
	create_notification(viewer_id=photo_owner_id, object_id=photo_id, object_type='0', seen=is_seen,\
		updated_at=epochtime, unseen_activity=unseen_activity, single_notif=single_notif, priority='photo_tabsra')
	all_commenter_ids = list(set(PhotoComment.objects.filter(which_photo_id=photo_id).order_by('-id').\
		values_list('submitted_by', flat=True)[:25]))
	if photo_owner_id not in all_commenter_ids:
		all_commenter_ids.append(photo_owner_id)
	try:
		all_commenter_ids.remove(user_id)
	except:
		pass
	if all_commenter_ids:
		bulk_update_notifications(viewer_id_list=all_commenter_ids, object_id=photo_id, object_type='0',\
			seen=False, updated_at=epochtime, single_notif=True, unseen_activity=True,priority='photo_tabsra') #only update if it existed
	updated = update_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
		single_notif=False, unseen_activity=True,priority='photo_tabsra', bump_ua=True)
	if not updated:
		create_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
			unseen_activity=True)
	photo.second_latest_comment = photo.latest_comment
	photo.latest_comment_id = photocomment_id
	photo.comment_count = count+1
	photo.save()
	if is_fan(photo_owner_id,user_id):
		add_to_photo_owner_activity(photo_owner_id, user_id)


@celery_app1.task(name='tasks.photo_tasks')
def photo_tasks(user_id, photo_id, epochtime, photocomment_id, count, text, it_exists, commenter, commenter_av, is_citizen):
	photo = Photo.objects.select_related('owner__userprofile').get(id=photo_id)
	photo_owner_id = photo.owner_id
	try:
		owner_url = photo.owner.userprofile.avatar.url
	except:
		owner_url = None
	created = create_object(object_id=photo_id, object_type='0', object_owner_avurl=owner_url,object_owner_id=photo_owner_id,\
		object_owner_name=photo.owner.username,object_desc=photo.caption,lt_res_time=epochtime,lt_res_avurl=commenter_av,\
		lt_res_sub_name=commenter,lt_res_text=text,res_count=(count+1),vote_score=photo.vote_score,photourl=photo.image_file.url,\
		lt_res_wid=user_id)
	if not created:
		update_object(object_id=photo_id, object_type='0', lt_res_time=epochtime,lt_res_avurl=commenter_av,\
			lt_res_sub_name=commenter,lt_res_text=text,res_count=(count+1),vote_score=photo.vote_score, lt_res_wid=user_id)
	if photo_owner_id == user_id:
		is_seen = True
		unseen_activity = True
		single_notif = None
		same_writer = True
	else:
		is_seen = False
		unseen_activity = True
		single_notif = True
		same_writer = False
	created_for_parent = create_notification(viewer_id=photo_owner_id, object_id=photo_id, object_type='0', seen=is_seen,\
		updated_at=epochtime, unseen_activity=unseen_activity, single_notif=single_notif, priority='photo_tabsra')
	all_commenter_ids = list(set(PhotoComment.objects.filter(which_photo_id=photo_id).order_by('-id').\
		values_list('submitted_by', flat=True)[:25]))
	if photo_owner_id not in all_commenter_ids:
		all_commenter_ids.append(photo_owner_id)
	try:
		all_commenter_ids.remove(user_id)
	except:
		pass
	if created_for_parent and not same_writer:
		try:
			all_commenter_ids.remove(photo_owner_id)
		except:
			pass
	if all_commenter_ids:
		bulk_update_notifications(viewer_id_list=all_commenter_ids, object_id=photo_id, object_type='0',\
			seen=False, updated_at=epochtime, single_notif=True, unseen_activity=True,priority='photo_tabsra')
	if not created_for_parent or not same_writer:
		updated = update_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
			single_notif=False, unseen_activity=True,priority='photo_tabsra', bump_ua=True)
		if not updated:
			create_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
				unseen_activity=True)
	photo.second_latest_comment = photo.latest_comment
	photo.latest_comment_id = photocomment_id
	photo.comment_count = count+1
	photo.save()
	if is_fan(photo_owner_id,user_id):
		add_to_photo_owner_activity(photo_owner_id, user_id)


@celery_app1.task(name='tasks.video_vote_tasks')
def video_vote_tasks(video_id, user_id, vote_score_increase, visible_score_increase, media_score_increase, score_increase):
	Video.objects.filter(id=video_id).update(vote_score=F('vote_score')+vote_score_increase, visible_score=F('visible_score')+visible_score_increase)
	UserProfile.objects.filter(user_id=user_id).update(media_score=F('media_score')+media_score_increase, score=F('score')+score_increase)


@celery_app1.task(name='tasks.cache_voting_history')
def cache_voting_history(user_id, page_num, json_data):
	"""
	Caches voting history
	"""
	cache_detailed_voting_data(json_data=json_data, page_num=page_num, user_id=user_id)


@celery_app1.task(name='tasks.vote_tasks')
def vote_tasks(own_id,target_user_id,target_obj_id,vote_value,is_pinkstar,own_name,revert_prev,is_pht,time_of_vote):
	"""
	Processes vote on a post by a user

	Handles both textual or photo voting
	"""
	target_userprofile_score = UserProfile.objects.only('score').get(user_id=target_user_id).score
	old_net_votes = Photo.objects.only('vote_score').get(id=target_obj_id).vote_score if is_pht == '1' \
	else Link.objects.only('net_votes').get(id=target_obj_id).net_votes
	#simply hellban the user in case their score is too low, and that's all
	if target_userprofile_score < -25:
		if not HellBanList.objects.filter(condemned_id=target_user_id).exists(): #only insert user in hell-ban list if she isn't there already
			HellBanList.objects.create(condemned_id=target_user_id) #adding user to hell-ban list
			UserProfile.objects.filter(user_id=target_user_id).update(score=random.randint(10,71))
	# elif target_userprofile_score > 0:
	else:
		if vote_value == '1':
			# is an upvote
			if revert_prev:
				world_age_discount_multiplier, affinity_discount_multiplier = 1, 1# these values don't matter since discounts aren't used at all in reverting
			else:
				# world_age_discount_multiplier applied on cast vote is world_age_discount_multiplier
				world_age_discount_multiplier = calculate_world_age_discount(user_id=own_id)
				# affinity_discount_multiplier applied on cast vote is (1-affinity_discount_multiplier)
				vote_affinity_discount = retrieve_voting_affinity(voter_id=own_id, target_user_id=target_user_id, vote_type=vote_value)
				##############################################################################
				######################## Vote Discount logger ################################
				##############################################################################
				if vote_affinity_discount == 1:
					if int(is_pht) == 1:
						log_vote_disc(vote_type='discounted',item_type='photo')
					else:
						log_vote_disc(vote_type='discounted',item_type='text')
				else:
					if int(is_pht) == 1:
						log_vote_disc(vote_type='regular',item_type='photo')
					else:
						log_vote_disc(vote_type='regular',item_type='text')
				##############################################################################
				##############################################################################
				##############################################################################
				affinity_discount_multiplier = (1-vote_affinity_discount)

			net_votes = old_net_votes + 1
			added = record_vote(target_obj_id,net_votes,vote_value,is_pinkstar,own_name, own_id, revert_prev, is_pht,time_of_vote,\
				target_user_id, world_age_discount_multiplier, affinity_discount_multiplier)
			if added:
				# vote added
				if is_pht == '1':
					# is a photo object
					# UserProfile.objects.filter(user_id=target_user_id).update(media_score=F('media_score')+UPVOTE)
					Photo.objects.filter(id=target_obj_id).update(vote_score=net_votes)
					update_object(object_id=target_obj_id,object_type='0',vote_score=net_votes, just_vote=True)# updates vote count attached to notification object of photo
					if revert_prev:
						# it's a reversion of a downvote - do nothing
						pass
					else:
						# it's a genuine upvote - not just a reversion of the previous step
						is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
						if is_super_defender:
							queue_obj_into_trending(prefix='img:',obj_owner_id=target_user_id,obj_id=target_obj_id,picked_by_id=own_id)
				else:
					# is a link object
					# UserProfile.objects.filter(user_id=target_user_id).update(score=F('score')+UPVOTE)
					Link.objects.filter(id=target_obj_id).update(net_votes=net_votes)
			else:
				# vote not added, do nothing
				pass
		elif vote_value == '0':
			# is a downvote
			if revert_prev:
				world_age_discount_multiplier, affinity_discount_multiplier = 1, 1
			else:
				# world_age_discount_multiplier applied on cast vote is world_age_discount_multiplier
				world_age_discount_multiplier = calculate_world_age_discount(user_id=own_id)
				# affinity_discount_multiplier applied on cast vote is (1-affinity_discount_multiplier)
				vote_affinity_discount = retrieve_voting_affinity(voter_id=own_id, target_user_id=target_user_id, vote_type=vote_value)
				##############################################################################
				######################## Vote Discount logger ################################
				##############################################################################
				if vote_affinity_discount == 1:
					if int(is_pht) == 1:
						log_vote_disc(vote_type='discounted',item_type='photo', downvote=True)
					else:
						log_vote_disc(vote_type='discounted',item_type='text', downvote=True)
				else:
					if int(is_pht) == 1:
						log_vote_disc(vote_type='regular',item_type='photo', downvote=True)
					else:
						log_vote_disc(vote_type='regular',item_type='text', downvote=True)
				##############################################################################
				##############################################################################
				##############################################################################
				affinity_discount_multiplier = (1-vote_affinity_discount)
			
			net_votes = old_net_votes - 1
			added = record_vote(target_obj_id,net_votes,vote_value,is_pinkstar,own_name, own_id, revert_prev, is_pht, time_of_vote,\
				target_user_id, world_age_discount_multiplier, affinity_discount_multiplier)
			if added:
				# vote added
				if is_pht == '1':
					# is a photo object
					# UserProfile.objects.filter(user_id=target_user_id).update(media_score=F('media_score')+DOWNVOTE)
					Photo.objects.filter(id=target_obj_id).update(vote_score=net_votes)
					update_object(object_id=target_obj_id,object_type='0',vote_score=net_votes, just_vote=True)# updates vote count attached to notification object of photo
					is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
					if revert_prev:
						# it's the reversion of an upvote - we have no confidence in this pic
						if is_super_defender:
							remove_obj_from_trending(prefix='img:',obj_id=target_obj_id)
					else:
						# it's a genuine downvote - not just a reversion of the previous step
						if is_super_defender:
							remove_obj_from_trending(prefix='img:',obj_id=target_obj_id)
				else:
					# is a link object
					# UserProfile.objects.filter(user_id=target_user_id).update(score=F('score')+DOWNVOTE)
					Link.objects.filter(id=target_obj_id).update(net_votes=net_votes)
			else:
				# vote not added, do nothing
				pass
		else:
			# neither an upvote nor a downvote, do nothing
			pass
		#################### A/B test logger ####################
		log_vote_for_ab_test(voter_id=own_id,vote_value=vote_value)


@celery_app1.task(name='tasks.registration_task')
def registration_task(ip,username):
	account_created(ip,username)

@celery_app1.task(name='tasks.log_sharing_click')
def log_sharing_click(photo_id, photo_owner_id, sharer_id, share_type, origin_key):
	try:
		origin = SHARE_ORIGIN[origin_key]
	except KeyError:
		origin = None
	log_share(photo_id, photo_owner_id, sharer_id, share_type, origin)

@celery_app1.task(name='tasks.video_tasks')
def video_tasks(user_id, video_id, timestring, videocomment_id, count, text, it_exists):
	user = User.objects.get(id=user_id)
	video = Video.objects.get(id=video_id)
	video.second_latest_comment = video.latest_comment
	video.latest_comment_id = videocomment_id
	video.comment_count = count
	# set_prev_retort(user_id,text)
	if user_id != video.owner_id and not it_exists:
		user.userprofile.score = user.userprofile.score + 2 #giving score to the commenter
		video.owner.userprofile.media_score = video.owner.userprofile.media_score + 2 #giving media score to the video poster
		video.owner.userprofile.score = video.owner.userprofile.score + 2 # giving score to the video poster
		video.visible_score = video.visible_score + 2
		video.owner.userprofile.save()
	video.save()
	user.userprofile.save()


@celery_app1.task(name='tasks.publicreply_tasks')
def publicreply_tasks(user_id, reply_id, link_id, description, epochtime, is_someone_elses_post, link_writer_id):
	Link.objects.filter(id=link_id).update(reply_count=F('reply_count')+1, latest_reply=reply_id)  #updating comment count and latest_reply for DB link


@celery_app1.task(name='tasks.publicreply_notification_tasks')
def publicreply_notification_tasks(link_id,sender_id,link_submitter_url,link_submitter_id,link_submitter_username,link_desc,\
	reply_time,reply_poster_url,reply_poster_username,reply_desc,is_welc,reply_count,priority,from_unseen):
	if from_unseen:
		update_object(object_id=link_id, object_type='2', lt_res_time=reply_time,lt_res_avurl=reply_poster_url,\
			lt_res_sub_name=reply_poster_username,lt_res_text=reply_desc,res_count=reply_count, lt_res_wid=sender_id)
		all_reply_ids = list(set(Publicreply.objects.filter(answer_to=link_id).order_by('-id').\
			values_list('submitted_by', flat=True)[:25]))
		if link_submitter_id not in all_reply_ids:
			all_reply_ids.append(link_submitter_id)
		try:
			all_reply_ids.remove(sender_id)
		except:
			pass
		if all_reply_ids:
			bulk_update_notifications(viewer_id_list=all_reply_ids, object_id=link_id, object_type='2',seen=False, \
				updated_at=reply_time, single_notif=True, unseen_activity=True,priority=priority)
		updated = update_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, \
			updated_at=reply_time, single_notif=False, unseen_activity=True,priority='home_jawab', bump_ua=True)
		if not updated:
			create_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, \
				updated_at=reply_time, unseen_activity=True)
	else:
		created = create_object(object_id=link_id, object_type='2', object_owner_avurl=link_submitter_url,\
			object_owner_id=link_submitter_id,object_owner_name=link_submitter_username,object_desc=link_desc,lt_res_time=reply_time,\
			lt_res_avurl=reply_poster_url,lt_res_sub_name=reply_poster_username,lt_res_text=reply_desc,is_welc=is_welc,\
			res_count=reply_count, lt_res_wid=sender_id)
		if not created:
			update_object(object_id=link_id, object_type='2', lt_res_time=reply_time,lt_res_avurl=reply_poster_url,\
				lt_res_sub_name=reply_poster_username,lt_res_text=reply_desc,res_count=reply_count, lt_res_wid=sender_id)
		if link_submitter_id == sender_id:
			is_seen = True
			unseen_activity = True
			single_notif = None
			same_writer = True
		else:
			is_seen = False
			unseen_activity = True
			single_notif = True
			same_writer = False
		created_for_parent = create_notification(viewer_id=link_submitter_id, object_id=link_id, object_type='2', seen=is_seen,\
				updated_at=reply_time, unseen_activity=unseen_activity, single_notif=single_notif,priority=priority)
		all_reply_ids = list(set(Publicreply.objects.filter(answer_to=link_id).order_by('-id').values_list('submitted_by', flat=True)[:25]))
		if link_submitter_id not in all_reply_ids:
			all_reply_ids.append(link_submitter_id)
		try:
			all_reply_ids.remove(sender_id)
		except:
			pass
		if created_for_parent and not same_writer:
			try:
				#remove link_submitter_id from all_reply_ids so it doesn't get updated again in 'bulk update notifcations'
				all_reply_ids.remove(link_submitter_id)
			except:
				pass
		if all_reply_ids:
			bulk_update_notifications(viewer_id_list=all_reply_ids, object_id=link_id, object_type='2',seen=False, \
				updated_at=reply_time, single_notif=True, unseen_activity=True,priority=priority)
		#create or update notification for self, but not when it's the first-ever reply and that too, by parent obj owner, i.e. not(created_for_parent and same_writer) = (not created_for_parent or not same_writer) - logical operation
		if not created_for_parent or not same_writer:
			updated = update_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, updated_at=reply_time, \
				single_notif=False, unseen_activity=True, priority=priority, bump_ua=True)
			if not updated:
				create_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, updated_at=reply_time, \
					unseen_activity=True)

# @celery_app1.task(name='tasks.report')
# def report(reporter_id, target_id, report_origin=None, report_reason=None, which_link_id=None, which_publicreply_id=None, which_photo_id=None, which_photocomment_id=None, which_group_id=None, which_reply_id=None, nickname=None):
# 	if report_origin == '1':
# 		#origin:chupair
# 		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason='Chupair', report_origin=report_origin, which_link_id=which_link_id)
# 	elif report_origin == '2':
# 		#origin:publicreply
# 		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason='Publicreply', report_origin=report_origin, which_publicreply_id=which_publicreply_id)
# 	elif report_origin == '7':
# 		#origin:photocomment
# 		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason='PhotoComment', report_origin=report_origin, which_photocomment_id=which_photocomment_id, which_photo_id=which_photo_id)
# 	elif report_origin == '3':
# 		#origin:nickname
# 		userprofile = UserProfile.objects.get(user_id=reporter_id)
# 		target = User.objects.get(id=target_id)
# 		latest_user = User.objects.latest('id')
# 		userprofile.score = userprofile.score - 10
# 		userprofile.save()
# 		if int(latest_user.id) - int(target_id) < 50:
# 			Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason=target.username, report_origin=report_origin)
# 		else:
# 			# i.e. do nothing if it's an old id
# 			pass
# 	elif report_origin == '4':
# 		#origin:profile
# 		if report_reason == '1':
# 			reason = 'gali di'
# 		elif report_reason == '2':
# 			reason = 'dhamki di'
# 		elif report_reason == '3':
# 			reason = 'fake profile'
# 		elif report_reason == '4':
# 			reason = 'gandi baat'
# 		elif report_reason == '5':
# 			reason = 'password manga'
# 		elif report_reason == '6':
# 			reason = 'firqa wariyat'
# 		elif report_reason == '7':
# 			reason = 'gandi photo'
# 		elif report_reason == '8':
# 			reason = 'fake admin'
# 		else:
# 			reason = report_reason
# 		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_origin=report_origin, report_reason=reason)

# @celery_app1.task(name='tasks.video_upload_tasks')
# def video_upload_tasks(video_name, video_id, user_id):
# 	lst = uploadvid(video_name)
# 	low_res_thumb = "//"+lst[0].partition('://')[2]
# 	small_thumb = "//"+lst[1].partition('://')[2]
# 	low_res_video = "//"+lst[2].partition('://')[2]
# 	high_res_video = "//"+lst[3].partition('://')[2]
# 	video = Video.objects.filter(id=video_id).update(low_res_thumb=low_res_thumb, small_thumb=small_thumb, low_res_video=low_res_video, high_res_video=high_res_video, processed=True)
# 	if video:
# 		add_video(video_id)
# 		save_recent_video(user_id, video_id)
# 		UserProfile.objects.filter(user_id=user_id).update(score=F('score')-5)
# 	else:
# 		pass

@celery_app1.task(name='tasks.fan_recount')
def fan_recount(owner_id,fan_increment,fan_decrement):
	if fan_decrement:
		TotalFanAndPhotos.objects.filter(owner_id=owner_id).update(total_fans=F('total_fans')-1,last_updated=datetime.utcnow()+timedelta(hours=5))
	elif fan_increment:
		updated = TotalFanAndPhotos.objects.filter(owner_id=owner_id).update(total_fans=F('total_fans')+1,last_updated=datetime.utcnow()+timedelta(hours=5)) #move to tasks
		if not updated:
			TotalFanAndPhotos.objects.create(owner_id=star_id, total_fans=1, total_photos=0, last_updated=datetime.utcnow()+timedelta(hours=5))
	else:
		pass

#obj1 = locals()['salat_info']
# obj2 = locals()['rank_photos']
#obj1.run()
# obj2.run()