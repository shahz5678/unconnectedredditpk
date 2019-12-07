import ujson as json
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
GIBBERISH_PUNISHMENT_MULTIPLIER, SHARE_ORIGIN, NUM_TO_DELETE#, UPVOTE, DOWNVOTE,
# from page_controls import PHOTOS_PER_PAGE
from models import Photo, LatestSalat, Photo, PhotoComment, Link, Publicreply, TotalFanAndPhotos, UserProfile, Logout, \
Video, HotUser, PhotoStream, HellBanList, UserFan
#from order_home_posts import order_home_posts, order_home_posts2, order_home_posts1
from redis3 import add_search_photo, bulk_add_search_photos, log_gibberish_text_writer, get_gibberish_text_writers, retrieve_thumbs, \
queue_punishment_amount, save_used_item_photo, save_single_unfinished_ad, save_consumer_number, get_world_age, \
process_ad_final_deletion, process_ad_expiry, log_detail_click, remove_banned_users_in_bulk, log_404_errors, \
set_world_age, retrieve_random_pin, ratelimit_banner_from_unbanning_target, exact_date, calculate_world_age_discount
from redis5 import trim_personal_group, set_personal_group_image_storage, mark_personal_group_attendance, cache_personal_group_data,\
invalidate_cached_user_data, get_personal_group_anon_state, personal_group_soft_deletion, \
personal_group_hard_deletion, exited_personal_group_hard_deletion, update_personal_group_last_seen, set_uri_metadata_in_personal_group,\
rate_limit_personal_group_sharing, exit_user_from_targets_priv_chat
from redis4 import expire_online_users, get_recent_online, set_online_users, log_input_rate, log_input_text, retrieve_uname, retrieve_avurl, \
retrieve_credentials, invalidate_avurl, log_personal_group_exit_or_delete,log_share, logging_sharing_metrics, cache_photo_share_data, \
retrieve_bulk_unames, save_most_recent_online_users, rate_limit_unfanned_user,sanitize_unused_subscriptions,log_1on1_chat, log_replier_reply_rate
from redis6 import group_attendance, add_to_universal_group_activity, retrieve_single_group_submission, increment_pic_count,\
log_group_chatter, del_overflowing_group_submissions, empty_idle_groups, delete_ghost_groups, rank_mehfil_active_users, remove_inactive_members,\
retrieve_all_member_ids, group_owner_administrative_interest, hide_direct_response_in_group
from redis7 import log_like, retrieve_obj_feed, add_obj_to_home_feed, get_photo_feed, add_photos_to_best_photo_feed, delete_avg_hash, insert_hash,\
retrieve_all_home_text_obj_names, delete_temporarily_saved_content_details, cleanse_inactive_complainers, account_created, set_top_stars, \
add_posts_to_best_posts_feed, add_single_trending_object, trim_expired_user_submissions, select_hand_picked_obj_for_trending,retire_abandoned_topics,\
queue_obj_into_trending, in_defenders, remove_obj_from_trending, calculate_top_trenders, calculate_bayesian_affinity, cleanse_voting_records, \
study_voting_preferences,retrieve_img_obj_scores, add_single_trending_object_in_feed, cache_detailed_voting_data, get_best_home_feed, \
create_sybil_relationship_log, set_best_photo_for_fb_fan_page, can_post_image_on_fb_fan_page, archive_closed_objs_and_votes, \
retrieve_text_obj_scores, hide_inline_direct_response
from redis9 import delete_all_direct_responses_between_two_users, cleanse_direct_response_list, submit_direct_response, set_comment_history, \
delete_single_direct_response, hide_direct_response_in_inbox, modify_direct_response_objs, log_direct_response_metrics, log_location_for_sender,\
delete_direct_responses_upon_obj_deletion, cleanse_replier_data_from_location, cleanse_replier_history_when_pvp_blocked, remove_1on1_direct_responses,\
log_rate_of_reply
from ecomm_tracking import insert_latest_metrics
from links.azurevids.azurevids import uploadvid
from django.contrib.auth.models import User
from facebook_api import photo_poster
from redis3 import log_vote_disc
from redis8 import log_activity
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


def hide_direct_response_in_db(obj_type, reply_id):
	"""
	When a sentence in comments is hidden, are there any "reply of reply" chats associated to it that need to be hidden too on the same page?
	"""
	# Retreive "replies to reply" that have replied to this particular reply_id, and set their addendums to 'hidden'
	if obj_type == '3':
		Publicreply.objects.filter(direct_reply=reply_id).update(direct_reply_tgt_text_prefix='', direct_reply_tgt_text_postfix='')

	# Retreive "replies to reply" that have replied to this particular reply_id, and set their addendums to 'hidden'
	elif obj_type == '4':
		PhotoComment.objects.filter(direct_reply=reply_id).update(direct_reply_tgt_text_prefix='', direct_reply_tgt_text_postfix='')
	
	else:
		pass


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
		fan_ids_to_notify = []#get_active_fans(user_id,int(num_of_fans_to_notify))
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
def private_chat_tasks(own_id, target_id, group_id, posting_time, text, txt_type, own_anon='', target_anon='', blob_id='', idx='', img_url='', \
	own_uname='', own_avurl='',deleted='',hidden='',successful=True, from_dir_rep_list=False, sharing=False):
	if successful:
		mark_personal_group_attendance(own_id, target_id, group_id, posting_time)

		if txt_type == 'exited':
			own_id = str(own_id)
			log_personal_group_exit_or_delete(group_id, exit_by_id=own_id, action_type='exit')
			
			# ensuring both side don't have notifications in their inboxes anymore
			delete_single_direct_response(target_user_id=own_id, obj_type='7', parent_obj_id=group_id, sender_id=target_id)
			delete_single_direct_response(target_user_id=target_id, obj_type='7', parent_obj_id=group_id, sender_id=own_id)

			#ensuring own_id's 'reply activity' doesn't contain any trace of the exited 1on1
			cleanse_replier_data_from_location(obj_type='7', parent_obj_id=group_id, obj_owner_id=target_id, replier_ids=[own_id])
		
		else:
			own_uname, own_avurl = get_credentials(own_id, own_uname, own_avurl)
			target_uname = retrieve_uname(target_id,decode=True)

			# All txt_types are: 'notif','img','img_res','text','text_res','action','reentry','exited','creation','shared_img'
			if txt_type in ('text','img','shared_img','text_res','img_res'):
				set_uri_metadata_in_personal_group(own_id, text, group_id, blob_id, idx, txt_type)#Checks content and turns URLs clickable

			if from_dir_rep_list or sharing:
				update_personal_group_last_seen(own_id, group_id, posting_time)#supposed to update 'seen' of contributer

			########### GENERATE A DIR REP NOTIF ###########
			if own_anon == '1':
				sun = own_uname[:1].upper()
				group_name = '1 on 1 with {}'.format(sun.encode('utf-8'))
			elif own_anon == '0':
				sun = own_uname
				group_name = '1 on 1 with {}'.format(sun.encode('utf-8'))
			else:
				own_anon, target_anon, group_id = get_personal_group_anon_state(own_id,target_id)
				if own_anon:
					sun = own_uname[:1].upper()
					group_name = '1 on 1 with {}'.format(sun.encode('utf-8'))
				else:
					sun = own_uname
					group_name = '1 on 1 with {}'.format(sun.encode('utf-8'))

			# ensure a non-empty blob_id is passed, otherwise the code won't work correctly
			payload = {'tx':text,'tun':target_uname,'t':posting_time,'tid':target_id,'obid':None,\
				'sid':own_id,'dbid':blob_id if blob_id else '0','sun':sun,'ptun':None,'poid':group_id, \
				'ot':'7','idx':idx,'ptx':group_name}

			if img_url:
				payload['iu'] = img_url

			###############################################################
			# generating the actual reply for appearance in the 'direct response list' (in inbox) and the single notification across the website
			submit_direct_response(json_data=json.dumps(payload), time_now=posting_time, sender_id=own_id, target_user_id=target_id, \
				obj_type='7', parent_obj_id=group_id, reply_id=0)# reply_id doesn't matter for 1on1 groups
			
			###############################################################
			# delete the message that was responded to, if it exists in 'direct response list'
			delete_single_direct_response(target_user_id=own_id, obj_type='7', parent_obj_id=group_id, sender_id=target_id)

			###############################################################
			# generate footprint in 'reply history'
			log_location_for_sender(obj_type='7', obj_owner_id=target_id, parent_obj_id=group_id, replier_id=str(own_id),\
				target_uname=target_uname, time_now=posting_time, target_id=target_id)

			################### Logging 1on1 message ###################
			# if txt_type == 'shared_img':
			# 	payload = str(posting_time)+":"+txt_type+":"+img_url[-47:]+":"+str(own_id)+":"+target_id+":"+text
			# else:
			# 	payload = str(posting_time)+":"+txt_type+":"+img_url+":"+str(own_id)+":"+target_id+":"+text
			# log_1on1_chat(payload=payload,oid=own_id,tid=target_id, group_id=group_id, is_creation=True if txt_type == 'creation' else False)
			##############################################################


@celery_app1.task(name='tasks.update_notif_object_anon')
def update_notif_object_anon(value,which_user,which_group):
	pass
	# update_pg_obj_anon(value=value,object_id=which_group,user_id=which_user)


@celery_app1.task(name='tasks.direct_response_tasks')
def direct_response_tasks(action_status, action_type, num_skips=None, parent_obj_id=None, obj_owner_id=None, obj_hash_name=None, \
	obj_type=None, commenter_id=None, time_now=None, log_location=False, target_uname=None, target_id=None, text_len=-1):
	"""
	Tasks to complete when a direct response is sent on a public post (text or image)
	"""
	############################
	if action_type == '1' and obj_type == '7':
		# don't log this metric for 1on1s
		pass
	else:
		# log the metric otherwise
		log_direct_response_metrics(action_status=action_status, action_type=action_type, num_skips=num_skips, obj_type=obj_type)
	
	############################
	if log_location:
		commenter_id = str(commenter_id)
		if (obj_type in ('3','4') and commenter_id == target_id):
			# don't log location when talking on own posts without a reference (since that's essentially talking to 'self')
			pass
		else:
			# otherwise, log the location for 'recent activity'
			log_location_for_sender(obj_type=obj_type, obj_owner_id=obj_owner_id, parent_obj_id=parent_obj_id, replier_id=commenter_id,\
				target_uname=target_uname, time_now=time_now, target_id=target_id)
	
	############################
	# it's a publicreply
	if obj_type == '3':
		# Logging who all visited a user's public posts
		set_comment_history(obj_hash_name=obj_hash_name, obj_owner_id=obj_owner_id, commenter_id=commenter_id, time_now=time_now)
		# Incrementing comment_count
		Link.objects.filter(id=parent_obj_id).update(reply_count=F('reply_count')+1)
		# Logging response rate (for rate limiting reasons)
		log_rate_of_reply(replier_id=commenter_id, text_len=text_len, time_now=time_now)
	
	# it's a photo comment
	elif obj_type == '4':
		# Logging who all visited a user's public posts
		set_comment_history(obj_hash_name=obj_hash_name, obj_owner_id=obj_owner_id, commenter_id=commenter_id, time_now=time_now)
		# Incrementing comment_count
		Photo.objects.filter(id=parent_obj_id).update(comment_count=F('comment_count')+1)
		# Logging response rate (for rate limiting reasons)
		log_rate_of_reply(replier_id=commenter_id, text_len=text_len, time_now=time_now)



@celery_app1.task(name='tasks.hide_associated_direct_responses')
def hide_associated_direct_responses(obj_type,parent_obj_id,reply_id,sender_id,receiver_id,to_hide):
	"""
	Used when comments or chat is hidden in groups or in content comments, etc.
	"""
	hide_direct_response_in_inbox(obj_type=obj_type,parent_obj_id=parent_obj_id,reply_id=reply_id,to_hide=to_hide,sender_id=sender_id,\
	receiver_id=receiver_id)# in redis9
	
	# if the object in question belongs to the 'comments' ecosystem
	if obj_type in ('3','4'):
		# '3' is comment under text post, '4' is comment under img post
		hide_direct_response_in_db(obj_type, reply_id)
		hide_inline_direct_response(obj_type, parent_obj_id, reply_id)
	
	# if the object in question belongs to the 'mehfil' ecosystem
	elif obj_type in ('5','6'):
		# '5' is public, '6' is private
		hide_direct_response_in_group(obj_type, parent_obj_id,reply_id,to_hide)# redis6


@celery_app1.task(name='tasks.private_chat_seen')
def private_chat_seen(own_id, group_id, curr_time):
	"""
	Called every time a private chat is refreshed (or 'seen'). 

	But not called from 'from_unseen' or 'sharing'
	"""
	pass
	# skip_private_chat_notif(own_id, group_id,curr_time, seen=True)


# execute every 3 days
@celery_app1.task(name='tasks.delete_chat_from_idle_personal_group')
def delete_chat_from_idle_personal_group():
	deleted_group_ids_and_participants = personal_group_soft_deletion()
	if deleted_group_ids_and_participants:
		for group_id, user_1, user_2 in deleted_group_ids_and_participants:
			delete_single_direct_response(target_user_id=user_1, obj_type='7', parent_obj_id=group_id, sender_id=user_2)
			delete_single_direct_response(target_user_id=user_2, obj_type='7', parent_obj_id=group_id, sender_id=user_1)


# execute every 6 days
@celery_app1.task(name='tasks.delete_idle_personal_group')
def delete_idle_personal_group():
	deleted_group_ids_and_participants = personal_group_hard_deletion()
	if deleted_group_ids_and_participants:
		for group_id, user_1, user_2 in deleted_group_ids_and_participants:
			delete_single_direct_response(target_user_id=user_1, obj_type='7', parent_obj_id=group_id, sender_id=user_2)
			delete_single_direct_response(target_user_id=user_2, obj_type='7', parent_obj_id=group_id, sender_id=user_1)

# execute daily
@celery_app1.task(name='tasks.delete_exited_personal_group')
def delete_exited_personal_group():
	deleted_group_ids_and_participants = exited_personal_group_hard_deletion()
	if deleted_group_ids_and_participants:
		for group_id, user_1, user_2 in deleted_group_ids_and_participants:
			delete_single_direct_response(target_user_id=user_1, obj_type='7', parent_obj_id=group_id, sender_id=user_2)
			delete_single_direct_response(target_user_id=user_2, obj_type='7', parent_obj_id=group_id, sender_id=user_1)



@celery_app1.task(name='tasks.post_banning_tasks')
def post_banning_tasks(own_id, target_id):
	"""
	Remove's banner's notifications from from the bannee's inbox, also unfans them, and a bunch of other tasks!
	"""
	# unfan (in case was a fan)
	UserFan.objects.filter(fan_id=own_id, star_id=target_id).delete()
	UserFan.objects.filter(fan_id=target_id, star_id=own_id).delete()
	# remove_from_photo_owner_activity(photo_owner_id=own_id, fan_id=target_id)
	# remove_from_photo_owner_activity(photo_owner_id=target_id, fan_id=own_id)
	rate_limit_unfanned_user(own_id=own_id,target_id=target_id)
	################################################################################
	# this ensures they can't 1on1 chat with eachother
	# 1) Exit yourself if group is non-exited
	# 2) If 'target' has already exited group, tell them they can't re-enter because the other party outright blocked them!
	# 3) No notifications will be generated since we already sanitized each user's activity
	group_id, group_exists = exit_user_from_targets_priv_chat(own_id,target_id)
	if group_id:
		remove_1on1_direct_responses(group_id=group_id, first_user_id=target_id, second_user_id=own_id)
	################################################################################
	# remove any direct responses exchanged between the two (except for 1on1, which is handled in the previous step)
	delete_all_direct_responses_between_two_users(first_user_id=target_id, second_user_id=own_id)# order of passing user IDs does not matter
	################################################################################
	# remove locations owned by each other from 'reply history'
	cleanse_replier_history_when_pvp_blocked(replier_id_1=target_id, replier_id_2=own_id)
	################################################################################
	# we did a lot of work, ensure banner didn't ban in vain!
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
	create_sybil_relationship_log()


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


@celery_app1.task(name='tasks.log_user_action')
def log_user_activity(user_id, activity_dict, time_now, which_var=None):
	"""
	Logs user actions for retention analysis
	"""
	log_activity(user_id=user_id, activity_dict=activity_dict, time_now=time_now, which_var=which_var)


@celery_app1.task(name='tasks.log_reply_rate')
def log_reply_rate(replier_id, text, time_now, reply_target, marked_fast):
	"""
	TODO: temp logger that should be removed
	"""
	log_replier_reply_rate(replier_id, text, time_now, reply_target, marked_fast)


# @celery_app1.task(name='tasks.set_section_retention')
# def set_variation_retention(user_id, which_var=None):
# 	"""
# 	Logs users for retention calculation of various cohorts

# 	'which_var' is the name of an experimental variation currently under progress
# 	"""
# 	set_variation_wise_retention(user_id,which_var=which_var)


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
	pass
	# clean_expired_notifications(user_id)

@celery_app1.task(name='tasks.calc_gibberish_punishment')
def calc_gibberish_punishment():
	"""
	Scheduled task to calculate 'like_probs' of voters/likers

	Mislabeled for legacy reasons
	"""
	archive_closed_objs_and_votes()


@celery_app1.task(name='tasks.calc_photo_quality_benchmark')
def calc_photo_quality_benchmark():
	pass


@celery_app1.task(name='tasks.bulk_create_notifications')
def bulk_create_notifications(user_id, photo_id, epochtime, photourl, name, caption):
	pass


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


# @celery_app1.task(name='tasks.sanitize_erroneous_notif')
# def sanitize_erroneous_notif(notif_name, user_id):
# 	remove_erroneous_notif(notif_name, user_id)

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
def update_group_topic(group_id, topic, group_type):
	"""
	Updates group topic in notification object
	"""
	modify_direct_response_objs(parent_obj_type=group_type, parent_obj_id=group_id, modification_type='topic', payload=topic)

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

	deleted_groups = delete_ghost_groups()#redis6
	for group_id, group_type in deleted_groups:
		if group_type == 'public':
			delete_direct_responses_upon_obj_deletion(obj_type='5', obj_id=group_id)# deleting 'direct resposes' given in the group
		elif group_type == 'private':
			delete_direct_responses_upon_obj_deletion(obj_type='6', obj_id=group_id)# deleting 'direct resposes' given in the group
		else:
			pass
	# bulk_remove_multiple_group_notifications(grp_ids_and_members)#redis2
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
		pass
		# own self has seen this, and no need to show a notification to other users
		###############################
		# updated=update_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
		# 	unseen_activity=True,single_notif=False,priority=priority,bump_ua=True)
		# if not updated:
		# 	create_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
		# 		unseen_activity=True, check_parent_obj=True)# matka notif won't be created if original object doesn't exist
	else:
		# if from_unseen:
		# 	# i.e. from unseen_group() in views.py
		# 	update_object(object_id=group_id,object_type='3',lt_res_time=reply_time,lt_res_avurl=poster_url,lt_res_text=reply_text,\
		# 		lt_res_sub_name=poster_username,reply_photourl=image_url,lt_res_wid=sender_id)
		# else:
		# 	created = create_object(object_id=group_id,object_type='3',object_owner_id=group_owner_id,object_desc=topic,\
		# 		lt_res_time=reply_time,lt_res_avurl=poster_url,lt_res_sub_name=poster_username,lt_res_text=reply_text,\
		# 		group_privacy=priv,slug=slug, lt_res_wid=sender_id)
		# 	if not created:
		# 		update_object(object_id=group_id,object_type='3',lt_res_time=reply_time,lt_res_avurl=poster_url,lt_res_text=reply_text,\
		# 			lt_res_sub_name=poster_username,reply_photourl=image_url, lt_res_wid=sender_id)
		# ###############################
		# # updating notification for single target or bulk targets
		# if notify_single_user and single_target_id:
		# 	# notify just a single targeted user (i.e. used in a direct response in mehfils)
		# 	update_notification(viewer_id=single_target_id,object_id=group_id,object_type='3',seen=False,updated_at=reply_time,\
		# 		unseen_activity=True,single_notif=True,priority=priority,bump_ua=True)
		# else:
		# 	all_group_member_ids = retrieve_all_member_ids(group_id)
		# 	all_group_member_ids.remove(str(sender_id))
		# 	if all_group_member_ids:
		# 		# this does NOT update notifications for users whose notification object was deleted (or wasn't created in the first place)
		# 		bulk_update_notifications(viewer_id_list=all_group_member_ids,object_id=group_id,object_type='3',seen=False,
		# 			updated_at=reply_time,single_notif=True,unseen_activity=True,priority=priority)
		# ###############################
		# # updating notification for sender
		# updated = update_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
		# 	unseen_activity=True,single_notif=False,priority=priority,bump_ua=True)
		# if not updated:
		# 	create_notification(viewer_id=sender_id,object_id=group_id,object_type='3',seen=True,updated_at=reply_time,\
		# 		unseen_activity=True)
		if priv == '1':
			log_group_chatter(group_id, sender_id)# redis 6
			if image_url:
				increment_pic_count(group_id, sender_id)#redis 6
	

@celery_app1.task(name='tasks.rank_all_photos')
def rank_all_photos():
	"""
	Used to find the single "best" photo from the current lot, criteria being an image with positive cumulative vote score, and at least 1 downvote

	Can also push hand-picked objects into trending lists (disabled for now)
	Mislabeled task due to legacy reasons
	"""
	time_now = time.time()
	pushed, obj_id = select_hand_picked_obj_for_trending()#push_hand_picked_obj_into_trending()
	if pushed and obj_id:
		cohort_num = int(time_now/604800)#cohort size is 1 week
		Logout.objects.create(logout_user_id=obj_id,pre_logout_score=cohort_num)
		#####################################################
		# Send this to Facebook fan page (every 6 hours)
		if can_post_image_on_fb_fan_page():
			photo = Photo.objects.only('image_file','caption','owner__username').get(id=obj_id)
			photo_poster(image_obj=photo.image_file, image_caption=photo.caption, owner_username=photo.owner.username, \
				photo_id=obj_id)
			set_best_photo_for_fb_fan_page(obj_id)
		#####################################################
	else:
		pass
		# TODO : activate when 'handpicked_prob' has been built
		#####################################################
		# fresh_photo_ids = get_photo_feed(feed_type='fresh_photos')#fresh photos in hash format
		# best_photo_ids = get_photo_feed(feed_type='best_photos')#trending photos in hash format
		# remaining_fresh_photo_ids = [id_ for id_ in fresh_photo_ids if id_ not in best_photo_ids]#unselected photos so far
		# trending_item_hash_name, item_score = extract_trending_obj(remaining_fresh_photo_ids, with_score=True)
		# if trending_item_hash_name:
		# 	highest_ranked_photo = retrieve_obj_feed([trending_item_hash_name])[0]
		# 	highest_ranked_photo['tos'] = time_now
		# 	highest_ranked_photo['like_prob'] = item_score# what probability exists that this content will be liked by at least 1 audience member
		# 	obj_id = trending_item_hash_name.split(":")[1]
		# 	add_single_trending_object(prefix="img:",obj_id=trending_item_hash_name.split(":")[1], obj_hash=highest_ranked_photo)
		# 	pushed = True


@celery_app1.task(name='tasks.rank_all_photos1')
def rank_all_photos1():
	"""
	Sanitize unused notification subscriptions
	"""
	sanitize_unused_subscriptions()


def extract_trending_obj(obj_hash_names, obj_type='img', with_score=False):
	"""
	Given a list of hashes, singles out the hash_obj which tops our score criteria

	Current criteria requires the top most obj to have the highest cumulative_vote_score but with at least one downvote
	"""
	only_liked = []
	if obj_type == 'img':
		obj_list = retrieve_img_obj_scores(obj_hash_names)
		for obj_hash, likes, score in obj_list:
			# ensure that the post is liked and has a positive 'score' (score is the prob it will get 'handpicked')
			
			if likes > 0 and score > 0:
				only_liked.append((obj_hash, score))# using 'score' as a means of ranking images (this is a measure of voter rep)
	elif obj_type == 'tx':
		obj_list = retrieve_text_obj_scores(obj_hash_names)
		for obj_hash, likes, score in obj_list:
			# ensure that the post is liked and has a positive 'score' (we don't have voter reps here yet)
			
			if likes > 0 and score > 0:
				only_liked.append((obj_hash, likes))# using 'likes' as a means of ranking texts

	#########################################
	# run this only when at least 2 posts are competing against one another - otherwise don't push anything into trending!
	if len(only_liked) > 1:

		only_liked.sort(key=itemgetter(1),reverse=True)
		trending_item_hash_name = only_liked[0][0]

		if with_score:
			return trending_item_hash_name, with_score
		else:
			return trending_item_hash_name

	###########################################
	if with_score:
		return '', None
	else:
		return ''


@celery_app1.task(name='tasks.rank_home_posts')
def rank_home_posts():
	"""
	Celery scheduled task used to create a 'best' list of home posts
	
	Currently, it's only an internal listing for us to view
	"""
	# Step 1) Isolate all fresh text posts (only 'text' - no 'img' type objs)
	fresh_obj_hashes = retrieve_all_home_text_obj_names()#get_home_feed()
	
	# Step 2) Isolate all best text posts
	trending_obj_hashes = get_best_home_feed(trending_home=True)
	
	# Step 3) Filter out fresh posts that are already in best
	if trending_obj_hashes:
		remaining_obj_hashes = [obj_hash_name for obj_hash_name in fresh_obj_hashes if obj_hash_name not in trending_obj_hashes]
	else:
		remaining_obj_hashes = fresh_obj_hashes
	
	# Step 4) From the remainder, extract the next 'best' text obj
	trending_item_hash_name = extract_trending_obj(remaining_obj_hashes, obj_type='tx')
	
	# Step 5) If trending obj has been found, push it into best
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
	Calculates voting rep of voters, and expires rep older than 3 months

	Mislabeled due to legacy reasons
	"""
	pass


@celery_app1.task(name='tasks.fans')
def fans():
	"""
	Cleans up expired (i.e. old) direct responses

	Mislabeled due to legacy reasons
	"""
	cleanse_direct_response_list()
	# user_ids = get_top_100()
	# user_ids_and_fan_counts = get_fan_counts_in_bulk(user_ids)
	# user_ids_and_user_objects = User.objects.select_related('userprofile','totalfanandphotos').defer('password','last_login','is_superuser',\
	# 	'first_name','email','is_staff','is_active','date_joined','id','last_name','totalfanandphotos__total_fans','totalfanandphotos__last_updated',\
	# 	'userprofile__bio','userprofile__shadi_shuda','userprofile__previous_retort','userprofile__attractiveness','userprofile__mobilenumber',\
	# 	'userprofile__score','userprofile__avatar','userprofile__streak','userprofile__age','userprofile__gender').in_bulk(user_ids)
	# top_list = []
	# for user_id in user_ids:
	# 	top_list.append({'username':user_ids_and_user_objects[int(user_id)].username,'id':user_id,\
	# 		"photo_count":user_ids_and_user_objects[int(user_id)].totalfanandphotos.total_photos,\
	# 		"media_score":user_ids_and_user_objects[int(user_id)].userprofile.media_score,\
	# 		"av_url":retrieve_avurl(user_id),"fan_count":user_ids_and_fan_counts[user_id]})
	# top_list = retrieve_thumbs(top_list)# add 'rows' key in the dictionary
	# set_top_stars(top_list)


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
	# if number_of_photos:
	# 	pass
	# 	# set_uploader_score(user_id, ((total_score*1.0)/number_of_photos))


@celery_app1.task(name='tasks.unseen_comment_tasks')
def unseen_comment_tasks(user_id, photo_id, epochtime, photocomment_id, count, text, commenter, commenter_av, is_citizen):
	# user = User.objects.get(id=user_id)
	photo = Photo.objects.select_related('owner__userprofile').get(id=photo_id)
	# photo_owner_id = photo.owner_id
	# try:
	# 	owner_url = photo.owner.userprofile.avatar.url
	# except ValueError:
	# 	owner_url = None
	# update_object(object_id=photo_id, object_type='0', lt_res_time=epochtime,lt_res_avurl=commenter_av,lt_res_sub_name=commenter,\
	# 	lt_res_text=text,res_count=(count+1),vote_score=photo.vote_score, lt_res_wid=user_id)
	# if photo_owner_id == user_id:
	# 	is_seen = True
	# 	unseen_activity = True
	# 	single_notif = None
	# 	same_writer = True
	# else:
	# 	is_seen = False
	# 	unseen_activity = True
	# 	single_notif = True
	# 	same_writer = False
	# create_notification(viewer_id=photo_owner_id, object_id=photo_id, object_type='0', seen=is_seen,\
	# 	updated_at=epochtime, unseen_activity=unseen_activity, single_notif=single_notif, priority='photo_tabsra')
	# all_commenter_ids = list(set(PhotoComment.objects.filter(which_photo_id=photo_id).order_by('-id').\
	# 	values_list('submitted_by', flat=True)[:25]))
	# if photo_owner_id not in all_commenter_ids:
	# 	all_commenter_ids.append(photo_owner_id)
	# try:
	# 	all_commenter_ids.remove(user_id)
	# except:
	# 	pass
	# if all_commenter_ids:
	# 	bulk_update_notifications(viewer_id_list=all_commenter_ids, object_id=photo_id, object_type='0',\
	# 		seen=False, updated_at=epochtime, single_notif=True, unseen_activity=True,priority='photo_tabsra') #only update if it existed
	# updated = update_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
	# 	single_notif=False, unseen_activity=True,priority='photo_tabsra', bump_ua=True)
	# if not updated:
	# 	create_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
	# 		unseen_activity=True)
	photo.second_latest_comment = photo.latest_comment
	photo.latest_comment_id = photocomment_id
	photo.comment_count = count+1
	photo.save()
	# if is_fan(photo_owner_id,user_id):
	# 	add_to_photo_owner_activity(photo_owner_id, user_id)


# @celery_app1.task(name='tasks.photo_tasks')
# def photo_tasks(user_id, photo_id, epochtime, photocomment_id, count, text, commenter, commenter_av, is_citizen):
# 	photo = Photo.objects.select_related('owner__userprofile').get(id=photo_id)
# 	photo_owner_id = photo.owner_id
# 	try:
# 		owner_url = photo.owner.userprofile.avatar.url
# 	except:
# 		owner_url = None
# 	created = create_object(object_id=photo_id, object_type='0', object_owner_avurl=owner_url,object_owner_id=photo_owner_id,\
# 		object_owner_name=photo.owner.username,object_desc=photo.caption,lt_res_time=epochtime,lt_res_avurl=commenter_av,\
# 		lt_res_sub_name=commenter,lt_res_text=text,res_count=(count+1),vote_score=photo.vote_score,photourl=photo.image_file.url,\
# 		lt_res_wid=user_id)
# 	if not created:
# 		update_object(object_id=photo_id, object_type='0', lt_res_time=epochtime,lt_res_avurl=commenter_av,\
# 			lt_res_sub_name=commenter,lt_res_text=text,res_count=(count+1),vote_score=photo.vote_score, lt_res_wid=user_id)
# 	if photo_owner_id == user_id:
# 		is_seen = True
# 		unseen_activity = True
# 		single_notif = None
# 		same_writer = True
# 	else:
# 		is_seen = False
# 		unseen_activity = True
# 		single_notif = True
# 		same_writer = False
# 	created_for_parent = create_notification(viewer_id=photo_owner_id, object_id=photo_id, object_type='0', seen=is_seen,\
# 		updated_at=epochtime, unseen_activity=unseen_activity, single_notif=single_notif, priority='photo_tabsra')
# 	all_commenter_ids = list(set(PhotoComment.objects.filter(which_photo_id=photo_id).order_by('-id').\
# 		values_list('submitted_by', flat=True)[:25]))
# 	if photo_owner_id not in all_commenter_ids:
# 		all_commenter_ids.append(photo_owner_id)
# 	try:
# 		all_commenter_ids.remove(user_id)
# 	except:
# 		pass
# 	if created_for_parent and not same_writer:
# 		try:
# 			all_commenter_ids.remove(photo_owner_id)
# 		except:
# 			pass
# 	if all_commenter_ids:
# 		bulk_update_notifications(viewer_id_list=all_commenter_ids, object_id=photo_id, object_type='0',\
# 			seen=False, updated_at=epochtime, single_notif=True, unseen_activity=True,priority='photo_tabsra')
# 	if not created_for_parent or not same_writer:
# 		updated = update_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
# 			single_notif=False, unseen_activity=True,priority='photo_tabsra', bump_ua=True)
# 		if not updated:
# 			create_notification(viewer_id=user_id, object_id=photo_id, object_type='0', seen=True, updated_at=epochtime, \
# 				unseen_activity=True)
# 	photo.second_latest_comment = photo.latest_comment
# 	photo.latest_comment_id = photocomment_id
# 	photo.comment_count = count+1
# 	photo.save()
# 	if is_fan(photo_owner_id,user_id):
# 		add_to_photo_owner_activity(photo_owner_id, user_id)


# @celery_app1.task(name='tasks.video_vote_tasks')
# def video_vote_tasks(video_id, user_id, vote_score_increase, visible_score_increase, media_score_increase, score_increase):
# 	Video.objects.filter(id=video_id).update(vote_score=F('vote_score')+vote_score_increase, visible_score=F('visible_score')+visible_score_increase)
# 	UserProfile.objects.filter(user_id=user_id).update(media_score=F('media_score')+media_score_increase, score=F('score')+score_increase)


@celery_app1.task(name='tasks.cache_voting_history')
def cache_voting_history(user_id, page_num, json_data):
	"""
	Caches voting history
	"""
	cache_detailed_voting_data(json_data=json_data, page_num=page_num, user_id=user_id)


@celery_app1.task(name='tasks.vote_tasks')
def vote_tasks(own_id, target_user_id, target_obj_id, revert_prev, is_pht, time_of_vote, is_editorial_vote):
	"""
	Processes vote on a post by a user

	Handles both textual or photo voting, both like and like-reversion
	"""
	if revert_prev:
		# undo a previous 'like'
		new_net_votes = log_like(obj_id=target_obj_id, own_id=own_id, revert_prev=True, is_pht=is_pht, target_user_id=target_user_id,\
			time_of_vote=time_of_vote, is_editorial_vote=is_editorial_vote)
		if is_pht == '1' and new_net_votes >= 0:
			# is a photo object
			# update_object(object_id=target_obj_id,object_type='0',vote_score=new_net_votes, just_vote=True)# updates vote count attached to notification object of photo
			# if it's a 'like' by a super-defender, handpick the object
			is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
			if is_super_defender:
				remove_obj_from_trending(prefix='img:',obj_id=target_obj_id)
	else:
		# cast a simple 'like' vote
		world_age_discount = calculate_world_age_discount(user_id=own_id)
		new_net_votes = log_like(obj_id=target_obj_id, own_id=own_id, revert_prev=False, is_pht=is_pht, target_user_id=target_user_id,\
			time_of_vote=time_of_vote, world_age_discount=world_age_discount, is_editorial_vote=is_editorial_vote)
		if is_pht == '1' and new_net_votes >= 0:
			# is a photo object
			# update_object(object_id=target_obj_id,object_type='0',vote_score=new_net_votes, just_vote=True)# updates vote count attached to notification object of photo
			# if it's a 'like' by a super-defender, handpick the object
			is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
			if is_super_defender:
				queue_obj_into_trending(prefix='img:',obj_owner_id=target_user_id,obj_id=target_obj_id,picked_by_id=own_id)


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


@celery_app1.task(name='tasks.publicreply_tasks')
def publicreply_tasks(user_id, reply_id, link_id, description, epochtime, is_someone_elses_post, link_writer_id):
	Link.objects.filter(id=link_id).update(reply_count=F('reply_count')+1, latest_reply=reply_id)  #updating comment count and latest_reply for DB link


@celery_app1.task(name='tasks.publicreply_notification_tasks')
def publicreply_notification_tasks(link_id,sender_id,link_submitter_url,link_submitter_id,link_submitter_username,link_desc,\
	reply_time,reply_poster_url,reply_poster_username,reply_desc,is_welc,reply_count,priority,from_unseen):
	pass
	# if from_unseen:
		# update_object(object_id=link_id, object_type='2', lt_res_time=reply_time,lt_res_avurl=reply_poster_url,\
		# 	lt_res_sub_name=reply_poster_username,lt_res_text=reply_desc,res_count=reply_count, lt_res_wid=sender_id)
		# all_reply_ids = list(set(Publicreply.objects.filter(answer_to=link_id).order_by('-id').\
		# 	values_list('submitted_by', flat=True)[:25]))
		# if link_submitter_id not in all_reply_ids:
		# 	all_reply_ids.append(link_submitter_id)
		# try:
		# 	all_reply_ids.remove(sender_id)
		# except:
		# 	pass
		# if all_reply_ids:
		# 	bulk_update_notifications(viewer_id_list=all_reply_ids, object_id=link_id, object_type='2',seen=False, \
		# 		updated_at=reply_time, single_notif=True, unseen_activity=True,priority=priority)
		# updated = update_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, \
		# 	updated_at=reply_time, single_notif=False, unseen_activity=True,priority='home_jawab', bump_ua=True)
		# if not updated:
		# 	create_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, \
		# 		updated_at=reply_time, unseen_activity=True)
	# else:
		# created = create_object(object_id=link_id, object_type='2', object_owner_avurl=link_submitter_url,\
		# 	object_owner_id=link_submitter_id,object_owner_name=link_submitter_username,object_desc=link_desc,lt_res_time=reply_time,\
		# 	lt_res_avurl=reply_poster_url,lt_res_sub_name=reply_poster_username,lt_res_text=reply_desc,is_welc=is_welc,\
		# 	res_count=reply_count, lt_res_wid=sender_id)
		# if not created:
		# 	update_object(object_id=link_id, object_type='2', lt_res_time=reply_time,lt_res_avurl=reply_poster_url,\
		# 		lt_res_sub_name=reply_poster_username,lt_res_text=reply_desc,res_count=reply_count, lt_res_wid=sender_id)
		# if link_submitter_id == sender_id:
		# 	is_seen = True
		# 	unseen_activity = True
		# 	single_notif = None
		# 	same_writer = True
		# else:
		# 	is_seen = False
		# 	unseen_activity = True
		# 	single_notif = True
		# 	same_writer = False
		# created_for_parent = create_notification(viewer_id=link_submitter_id, object_id=link_id, object_type='2', seen=is_seen,\
		# 		updated_at=reply_time, unseen_activity=unseen_activity, single_notif=single_notif,priority=priority)
		# all_reply_ids = list(set(Publicreply.objects.filter(answer_to=link_id).order_by('-id').values_list('submitted_by', flat=True)[:25]))
		# if link_submitter_id not in all_reply_ids:
		# 	all_reply_ids.append(link_submitter_id)
		# try:
		# 	all_reply_ids.remove(sender_id)
		# except:
		# 	pass
		# if created_for_parent and not same_writer:
		# 	try:
		# 		#remove link_submitter_id from all_reply_ids so it doesn't get updated again in 'bulk update notifcations'
		# 		all_reply_ids.remove(link_submitter_id)
		# 	except:
		# 		pass
		# if all_reply_ids:
		# 	bulk_update_notifications(viewer_id_list=all_reply_ids, object_id=link_id, object_type='2',seen=False, \
		# 		updated_at=reply_time, single_notif=True, unseen_activity=True,priority=priority)
		# #create or update notification for self, but not when it's the first-ever reply and that too, by parent obj owner, i.e. not(created_for_parent and same_writer) = (not created_for_parent or not same_writer) - logical operation
		# if not created_for_parent or not same_writer:
		# 	updated = update_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, updated_at=reply_time, \
		# 		single_notif=False, unseen_activity=True, priority=priority, bump_ua=True)
		# 	if not updated:
		# 		create_notification(viewer_id=sender_id, object_id=link_id, object_type='2', seen=True, updated_at=reply_time, \
		# 			unseen_activity=True)

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