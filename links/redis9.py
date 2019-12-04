import json as json_backup
from random import random
import redis, time
import ujson as json
from location import REDLOC9
from redis5 import retrieve_bulk_group_labels
from redis6 import retrieve_group_topics_in_bulk
from redis4 import retrieve_post_details_in_bulk
from score import REPLY_OBJECT_TTL, POST_HISTORY_TTL, NUM_ACTIVITY_ITEMS_PER_PAGE

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC9, db=0)

TWO_WEEKS = 2*7*24*60*60
ONE_DAY = 24*60*60
ONE_HOUR = 60*60

DIRECT_RESPONSE_OBJ = 'drobj:'# the object containing the actual details of the direct response (JSON format)
DIRECT_RESPONSE = 'dr:'#sorted set containing all responses received by a particular user (useful for populating "received direct responses" list)
DIRECT_RESPONSE_PARENT = 'drp:'#sorted set containing all responses attached to a particular parent obj (useful in parent obj deletion, or 'hiding'/'unhiding' a reply)
DIRECT_RESPONSE_SENDER_RECEIVER = 'drsr:'#sorted set containing all responses attached to a particular sender:receiver pair (useful in pvp blocking)
GLOBAL_DIRECT_RESPONSE_LOGGER = 'gdrl'# global set containing all direct responses, useful for "clean-up" scheduled tasks (performed later)

POSTER_VISITORS = 'pv:'# visitors who visit certain posters' posts

DIRECT_RESPONSE_METRICS = 'drm'# sorted set holding usage rates of direct response feature


def submit_direct_response(json_data, time_now, sender_id, target_user_id, parent_obj_id, obj_type, reply_id):
	"""
	Saves a 'direct response' to a user's object from anywhere in the app

	This is also used to populate an 'inbox' for users containing all 'direct responses'
	"""
	parent_obj_composite_id = obj_type+":"+parent_obj_id
	sender_receiver_id = str(sender_id)+":"+target_user_id
	expire_at = time_now+REPLY_OBJECT_TTL

	obj_key = DIRECT_RESPONSE_OBJ+parent_obj_composite_id+":"+sender_receiver_id# key for direct response 'hash' object
	dr_key = DIRECT_RESPONSE+target_user_id# key to populate target user's received direct responses list
	dr_po_key = DIRECT_RESPONSE_PARENT+parent_obj_composite_id#sorted set containing all responses attached to a particular parent obj (useful in obj deletion)
	dr_sr_key = DIRECT_RESPONSE_SENDER_RECEIVER+sender_receiver_id#sorted set containing all responses attached to a particular sender:receiver pair (useful in pvp blocking)
	
	###############################################################

	pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
	pipeline1.setex(obj_key,json_data,REPLY_OBJECT_TTL)# DIRECT_RESPONSE_OBJ
	pipeline1.zadd(dr_key,obj_key,expire_at)# DIRECT_RESPONSE
	################################################
	if obj_type != '7':
		# no longer generated for a 1on1. Does it hurt the cause?
		pipeline1.zadd(dr_po_key,obj_key,reply_id)# DIRECT_RESPONSE_PARENT
		pipeline1.zadd(dr_sr_key,obj_key,expire_at)# DIRECT_RESPONSE_SENDER_RECEIVER
	################################################
	pipeline1.zadd(GLOBAL_DIRECT_RESPONSE_LOGGER,obj_key,expire_at)# global set containing all direct responses, useful for "clean-up scheduled tasks" (performed later)
	pipeline1.execute()


def retrieve_direct_response_list(user_id, start_idx=0, end_idx=-1, with_feed_size=False, with_obj_list=False):
	"""
	Creates list data to be shown in the inbox
	"""
	direct_response_key = DIRECT_RESPONSE+str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	objs_to_show = my_server.zrevrange(direct_response_key,start_idx,end_idx)
	if objs_to_show:
		json_objs_that_exist = filter(None,my_server.mget(*objs_to_show))# filter() adds almost no overhead at all (benchmarked)
		final_data = []
		for json_obj in json_objs_that_exist:
			try:
				final_data.append(json.loads(json_obj))
			except:
				final_data.append(json_backup.loads(json_obj))
		if with_feed_size and with_obj_list:
			return final_data, my_server.zcard(direct_response_key), objs_to_show
		elif with_feed_size:
			return final_data, my_server.zcard(direct_response_key)
		elif with_obj_list:
			return final_data, objs_to_show
		else:
			return final_data
	else:
		if with_feed_size and with_obj_list:
			return [], 0, []
		elif with_feed_size:
			return [], 0
		elif with_obj_list:
			return [], []
		else:
			return []


def retrieve_latest_direct_reply(user_id):
	"""
	Retrieves the latest direct response received by user_id

	Useful for showing a 'single notification' anywhere in the app
	"""
	if user_id:
		my_server = redis.Redis(connection_pool=POOL)
		latest_direct_response = my_server.zrevrange(DIRECT_RESPONSE+str(user_id),0,0)
		if latest_direct_response:
			json_obj = my_server.get(latest_direct_response[0])
			if json_obj:
				try:
					return json.loads(json_obj)
				except:
					return json_backup.loads(json_obj)
			else:
				return []
		else:
			return []
	else:
		return []


def	direct_response_exists(obj_type, parent_obj_id, sender_id, receiver_id, with_hide_status=True):
	"""
	Does an existence check on direct response objs

	Can also return whether the obj has been 'hidden' or not (useful for stopping users from replying to 'hidden' objs, if warranted)
	"""
	key_name = DIRECT_RESPONSE_OBJ+obj_type+":"+parent_obj_id+":"+sender_id+":"+str(receiver_id)
	json_obj = redis.Redis(connection_pool=POOL).get(key_name)
	if with_hide_status:
		if json_obj:
			try:
				obj = json.loads(json_obj)
			except:
				obj = json_backup.loads(json_obj)
			return True, True if obj.get('hide_rep',None) == '1' else False
		else:
			return False, False
	else:
		if json_obj:
			return True
		else:
			return False


########################### Logging history of locations user replied at ###########################


REPLIER_VISITS = 'rv:'# sorted set containing list of locations visited by a replier
POST_INTERACTIONS = 'pi:'# sorted set containing usernames a replier replied to in a specific location
CACHED_REPLIER_VISITS = 'crv:'# key that holds a json blob of cached replier visits

REPLIER_VISITS_CULL_LOCK = 'rvcl:'# key that locks culling of REPLIER_VISITS sorted set
POST_INTERACTIONS_CULL_LOCK = 'picl:'# key that locks culling of POST_INTERACTIONS sorted set


def retrieve_interacted_unames(replier_id, obj_type, parent_obj_id):
	"""
	Returns a list of usernames that a user has interacted on in a given location
	"""
	return redis.Redis(connection_pool=POOL).zrevrange(POST_INTERACTIONS+obj_type+":"+parent_obj_id+":"+str(replier_id),0,-1, withscores=True)


def display_recent_reply_locations(replier_id, page_num, start_idx=0, end_idx=-1):
	"""
	Retrieve replier history for display
	"""
	replier_id = str(replier_id)
	my_server = redis.Redis(connection_pool=POOL)
	
	cached_data = my_server.get(CACHED_REPLIER_VISITS+replier_id+":"+str(page_num))
	if cached_data:
		try:
			return json.loads(cached_data)
		except:
			return json_backup.loads(cached_data)
	###############################################################################
	else:

		visit_key = REPLIER_VISITS+replier_id
		list_of_visits_and_times = my_server.zrevrange(visit_key,start_idx,end_idx,withscores=True)

		text_post_ids, img_post_ids, public_grps, private_grps, groups_and_friends = [], [], [], [], {}
		for visit, time_of_visit in list_of_visits_and_times:
			data = visit.split(":")
			obj_type, parent_obj_id, obj_owner_id = data[0], data[1], data[2]
			##############################
			if obj_type == '3':
				# this is a text post
				text_post_ids.append(parent_obj_id)
			elif obj_type == '4':
				# this is an image post
				img_post_ids.append(parent_obj_id)
			elif obj_type == '5':
				# this is a public group
				public_grps.append(parent_obj_id)
			elif obj_type == '6':
				# this is a private group
				private_grps.append(parent_obj_id)
			elif obj_type == '7':
				# this is a 1on1s - this requires a 'dictionary', it's a quirk of how the data needs to be fed to redis5
				groups_and_friends[parent_obj_id] = obj_owner_id
			##############################

		if text_post_ids or img_post_ids:
			# handles '3' and '4' (i.e. text and img posts respectively)
			parent_text_data, parent_img_data = retrieve_post_details_in_bulk(txt_post_ids=text_post_ids, img_post_ids=img_post_ids)

		if public_grps or private_grps:
			# handles '5' and '6' (i.e. public and private mehs respectively)
			public_group_topics, private_group_topics = retrieve_group_topics_in_bulk(public_grp_uuids=public_grps, private_grp_uuids=private_grps)

		if groups_and_friends:
			# handles '7' (i.e. 1on1s)
			groups_and_labels = retrieve_bulk_group_labels(groups_and_friends=groups_and_friends, user_id=replier_id)

		############################################################
		final_data, deleted_visit_locs, deleted_interactions = [], [], []
		for visit, time_of_visit in list_of_visits_and_times:
			visit_data, obj_detail = {}, {}
			data = visit.split(":")
			obj_type, parent_obj_id, obj_owner_id = data[0], data[1], data[2]
			post_interactions_key = POST_INTERACTIONS+obj_type+":"+parent_obj_id+":"+replier_id

			if obj_type == '7':
				# this is a 1on1 - we already know who the target_uname is
				list_of_unames = []
				num_unames = 0
			else:
				list_of_unames = my_server.zrevrange(post_interactions_key,0,4)# retrieve latest 4 people replier has talked to
				num_unames = len(list_of_unames)
				list_of_unames = list_of_unames[:3] if num_unames > 3 else list_of_unames

			visit_data['ot'] = obj_type
			visit_data['poid'] = parent_obj_id
			visit_data['tunames'] = list_of_unames
			visit_data['time'] = time_of_visit
			visit_data['ooid'] = obj_owner_id
			visit_data['nu'] = num_unames

			if obj_type == '3':
				data = parent_text_data.get(parent_obj_id,{})
				if data:
					#this data exists
					visit_data['wu'], visit_data['label'] = data['submitter_uname'], data['description']
					final_data.append(visit_data)
				else:
					# this data does not exist
					deleted_visit_locs.append(visit)
					deleted_interactions.append(post_interactions_key)

			elif obj_type == '4':
				data = parent_img_data.get(parent_obj_id,{})
				if data:
					# this data exists
					visit_data['wu'], visit_data['label'], visit_data['iu'] = data['submitter_uname'], data['caption'], data['image_file']
					final_data.append(visit_data)
				else:
					# this data does not exist
					deleted_visit_locs.append(visit)
					deleted_interactions.append(post_interactions_key)
				
			elif obj_type == '5':
				group_topic = public_group_topics.get(parent_obj_id,'')
				if group_topic:
					# this topic exists
					visit_data['label'] = group_topic
					final_data.append(visit_data)
				else:
					# this topic does not exist (group might have been deleted)
					deleted_visit_locs.append(visit)
					deleted_interactions.append(post_interactions_key)

			elif obj_type == '6':
				group_topic = private_group_topics.get(parent_obj_id,'')
				if group_topic:
					# this topic exists
					visit_data['label'] = group_topic
					final_data.append(visit_data)
				else:
					# this topic does not exist (group might have been deleted)
					deleted_visit_locs.append(visit)
					deleted_interactions.append(post_interactions_key)

			elif obj_type == '7':
				data = groups_and_labels.get(parent_obj_id,{})
				if data:
					# this data exists
					visit_data['label'], visit_data['wu'] = data['label'], data['uname']
					final_data.append(visit_data)
				else:
					# this data does not exist
					deleted_visit_locs.append(visit)

		############################################################
		
		# deleting the loc from REPLIER_VISITS+replier_id
		if deleted_visit_locs:
			my_server.zrem(visit_key,*deleted_visit_locs)
		
		# deleting POST_INTERACTIONS+obj_type+":"+parent_obj_id+":"+replier_id
		if deleted_interactions:
			my_server.execute_command('UNLINK',*deleted_interactions)

		# what's the total list size after 'deleted_visit_locs' has been removed?
		total_list_size = my_server.zcard(visit_key)

		# some data exists that can be shown (although this partcular page might have been deleted in entirety - we can't be sure yet)
		if total_list_size:

			# entire page deleted
			if len(deleted_visit_locs) == NUM_ACTIVITY_ITEMS_PER_PAGE:
				return [], True

			# entire page not deleted
			else:
				# determine whether to show the 'next' pagination button or not
				next_page_available = False if (total_list_size <= len(final_data) or (end_idx+1) >= total_list_size) else True

				# result is micro-cached for 3 mins
				my_server.setex(CACHED_REPLIER_VISITS+replier_id+":"+str(page_num),json.dumps((final_data, next_page_available)),180)
				
				return final_data, next_page_available
		
		# no data exists that can be shown
		else:
			return [], False


def log_location_for_sender(obj_type, obj_owner_id, parent_obj_id, replier_id, target_uname, time_now, target_id):
	"""
	When to add these locations?
	1) When 'responding' in a location - no other way

	When to sanitize these locations?
	1) Private/Public mehfil deletion/kicking i.e. delete the location via obj_type+parent_obj_id
	2) 1on1 exit i.e. delete the location via obj_type+parent_obj_id
	3) 2 weeks natural expiry i.e. utilize ttls
	4) PvP blocking i.e. delete all locations owned by the 'other' user i.e. isolate all of target's posts that the culprit visited
	"""
	###############################################
	# should the location be logged for the sender's viewing pleasure?
	obj_owner_id, expire_at = str(obj_owner_id), int(time_now+TWO_WEEKS)
	parent_obj_composite_id = obj_type+":"+parent_obj_id
	data = parent_obj_composite_id+":"+obj_owner_id
	visitations_and_times_key = REPLIER_VISITS+replier_id
	post_interactions_key = POST_INTERACTIONS+parent_obj_composite_id+":"+replier_id

	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	# the following are useful for showing a list of visited locations to sender
	pipeline1.zadd(visitations_and_times_key,data,time_now)
	pipeline1.expireat(visitations_and_times_key,expire_at)
	pipeline1.execute_command('UNLINK',CACHED_REPLIER_VISITS+replier_id+":1")# invalidate cache of the 'first page' of user history

	# the following is useful for showing a list usernames the sender talked to at the visited location
	if obj_type != '7':
		# no need to maintain post interactions for obj_type = '7' (1on1) since we ALWAYS know who the target is
		pipeline1.zadd(post_interactions_key,target_uname,time_now)
		pipeline1.expireat(post_interactions_key,expire_at)
	pipeline1.execute()

	############## Maintenance ##############

	random_num = random()

	# every now and then - trim 'post_interactions_key' so that the list of unames replied to doesn't grow to extremes
	cull_lock_key = POST_INTERACTIONS_CULL_LOCK+parent_obj_composite_id+":"+replier_id
	if obj_type != '7' and random_num < 0.05:
		if not my_server.exists(cull_lock_key):
			my_server.zremrangebyrank(post_interactions_key, 0, -11)# keep top-10 in the sorted set (this operation doesn't affect the TTL of the key)
			my_server.setex(cull_lock_key,'1',ONE_HOUR)
	
	# even more rarely, perform maintenance on 'visitations_and_times_key' too
	cull_lock_key = REPLIER_VISITS_CULL_LOCK+replier_id
	if random_num > 0.99:
		if not my_server.exists(cull_lock_key):
			two_weeks_ago = time_now - TWO_WEEKS
			# not removing related 'post interactions' - those keys have a ttl on them and will expire silently themselves
			my_server.zremrangebyscore(visitations_and_times_key,'-inf',two_weeks_ago)# this operation doesn't affect the TTL of the key
			my_server.setex(cull_lock_key,'1',ONE_DAY)
	
	#########################################


def cleanse_replier_history_when_pvp_blocked(replier_id_1, replier_id_2):
	"""
	Handles PVP blocking, by cleansing relevant visitor data for both users in the blocking stream (regardless of who blocked who)
	"""
	replier_id_1, replier_id_2 = str(replier_id_1), str(replier_id_2)
	user_1_replier_key, user_2_replier_key = REPLIER_VISITS+replier_id_1, REPLIER_VISITS+replier_id_2 

	my_server = redis.Redis(connection_pool=POOL)

	#####################################################################
	# processing the first user
	visits_to_remove, target_unames_to_remove = [], []

	# Step 1) Getting first user's reply activity
	all_visits_by_user_1 = my_server.zrange(user_1_replier_key,0,-1)
	
	# Step 2) Scanning the reply activity and removing visits to locations owned by user_2 (including mehfils)
	for visit in all_visits_by_user_1:
		data = visit.split(":")
		obj_type, parent_obj_id, obj_owner_id = data[0], data[1], data[2]
		if obj_owner_id == replier_id_2:
			# this location is 'owned' by the opposing user - let's remove it from history
			visits_to_remove.append(visit)
			if obj_type != '7':
				target_unames_to_remove.append(POST_INTERACTIONS+obj_type+":"+parent_obj_id+":"+replier_id_1)
	
	# Step 3) The actual removal takes place here
	if visits_to_remove:
		my_server.zrem(user_1_replier_key,*visits_to_remove)
	if target_unames_to_remove:
		my_server.execute_command('UNLINK',*target_unames_to_remove)

	#####################################################################
	# processing the second user
	visits_to_remove, target_unames_to_remove = [], []

	# Step 1) Getting second user's reply activity
	all_visits_by_user_2 = my_server.zrange(user_2_replier_key,0,-1)

	# Step 2) Scanning the reply activity and removing visits to locations owned by user_1 (including mehfils)
	for visit in all_visits_by_user_2:
		data = visit.split(":")
		obj_type, parent_obj_id, obj_owner_id = data[0], data[1], data[2]
		if obj_owner_id == replier_id_1:
			# this location is 'owned' by the opposing user - let's remove it from history
			visits_to_remove.append(visit)
			if obj_type != '7':
				target_unames_to_remove.append(POST_INTERACTIONS+obj_type+":"+parent_obj_id+":"+replier_id_2)
	
	#####################################################################
	# Step 3) The actual removal takes place here
	pipeline1 = my_server.pipeline()
	if visits_to_remove:
		pipeline1.zrem(user_2_replier_key,*visits_to_remove)
	if target_unames_to_remove:
		pipeline1.execute_command('UNLINK',*target_unames_to_remove)
	pipeline1.execute_command('UNLINK',CACHED_REPLIER_VISITS+replier_id_1+":1")# invalidate cache of the 'first page' of user history
	pipeline1.execute_command('UNLINK',CACHED_REPLIER_VISITS+replier_id_2+":1")# invalidate cache of the 'first page' of user history
	pipeline1.execute_command('UNLINK',CACHED_REPLIER_VISITS+replier_id_1+":2")# invalidate cache of the 'second page' of user history
	pipeline1.execute_command('UNLINK',CACHED_REPLIER_VISITS+replier_id_2+":2")# invalidate cache of the 'second page' of user history
	pipeline1.execute()


def cleanse_replier_data_from_location(obj_type, parent_obj_id, obj_owner_id, replier_ids):
	"""
	Remove the conversation from the target repliers' visit history

	Used in cases where:
	- User kicked from private/public group (or exits it)
	- User exits a 1on1
	"""	
	if replier_ids:
		parent_obj_composite_id = obj_type+":"+parent_obj_id
		pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
		for replier_id in replier_ids:
			pipeline1.zrem(REPLIER_VISITS+replier_id,parent_obj_composite_id+":"+obj_owner_id)
			if obj_type != '7':
				pipeline1.execute_command('UNLINK', POST_INTERACTIONS+parent_obj_composite_id+":"+replier_id)
		pipeline1.execute()


def remove_direct_response_activity(replier_id, location, page_num):
	"""
	Removes provided location from a replier's 'reply activity'
	"""
	data = location.split(":")
	try:
		obj_type, parent_obj_id, obj_owner_id = data[0], data[1], data[2]
		replier_id = str(replier_id)
	except:
		return False
	my_server = redis.Redis(connection_pool=POOL)
	removed = my_server.zrem(REPLIER_VISITS+replier_id,location)
	if removed > 0:
		if obj_type != '7':
			my_server.execute_command('UNLINK',POST_INTERACTIONS+obj_type+":"+parent_obj_id+":"+replier_id)
		my_server.execute_command('UNLINK',CACHED_REPLIER_VISITS+replier_id+":"+str(page_num))# invalidate cache
		return True
	else:
		return False


#######################################################################################
############################## Deleting Direct Responses ##############################
#######################################################################################


def cleanse_direct_response_list(target_user_id=None):
	"""
	Scheduled task to clean up expired DIRECT_RESPONSE lists

	Runs once every day
	"""
	my_server = redis.Redis(connection_pool=POOL)
	expired_keys = my_server.zrangebyscore(GLOBAL_DIRECT_RESPONSE_LOGGER,'-inf',time.time())
	if expired_keys:
		pipeline1 = my_server.pipeline()
		for key in expired_keys:
			# a key is made up of: obj_key = DIRECT_RESPONSE_OBJ+parent_obj_composite_id+":"+str(sender_id)+":"+target_user_id
			data = key.split(":")
			pipeline1.zrem(DIRECT_RESPONSE+data[4], key)#'dr:'
			pipeline1.zrem(DIRECT_RESPONSE_PARENT+data[1]+":"+data[2], key)#'drp:'
			pipeline1.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+data[3]+":"+data[4],key)#'drsr:'
		pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER,*expired_keys)#'gdrl'
		# assuming original DIRECT_RESPONSE_OBJs have already been destroyed due to ttls; not going to delete them explicitly
		pipeline1.execute()


def delete_single_direct_response(target_user_id, obj_type, parent_obj_id, sender_id):
	"""
	Deletes a single direct response object

	Explicitly called when a user skips an object, or 'replies' to an object
	Also used when 1on1 is deleted
	"""
	target_user_id, sender_id = str(target_user_id), str(sender_id)
	parent_obj_composite_id = obj_type+":"+parent_obj_id
	dr_key = DIRECT_RESPONSE+target_user_id
	obj_key = DIRECT_RESPONSE_OBJ+parent_obj_composite_id+":"+sender_id+":"+target_user_id
	sr_key = DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+target_user_id# sender receiver key
	my_server = redis.Redis(connection_pool=POOL)
	
	###############################################
	# obj exists - process deletion
	if my_server.zscore(dr_key,obj_key):
		pipeline1 = my_server.pipeline()
		pipeline1.execute_command('UNLINK', obj_key)
		pipeline1.zrem(dr_key,obj_key)
		################################################
		pipeline1.zrem(DIRECT_RESPONSE_PARENT+parent_obj_composite_id,obj_key)# key not generated for a 1on1
		pipeline1.zrem(sr_key,obj_key)# key not generated for a 1on1
		################################################
		pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER,obj_key)
		pipeline1.execute()
		return True
	# obj does not exist
	else:
		return False


def remove_1on1_direct_responses(group_id, first_user_id, second_user_id):
	"""
	Sanitizes footprint of 1on1 from given user_ids

	Sole usecase: when 1on1 is exited because of a pvp block (not applicable in a normal exit)
	"""
	first_user_id, second_user_id = str(first_user_id), str(second_user_id)
	obj_key_1 = DIRECT_RESPONSE_OBJ+'7:'+group_id+":"+second_user_id+":"+first_user_id
	obj_key_2 = DIRECT_RESPONSE_OBJ+'7:'+group_id+":"+first_user_id+":"+second_user_id

	pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
	pipeline1.zrem(DIRECT_RESPONSE+first_user_id, obj_key_1)
	pipeline1.zrem(DIRECT_RESPONSE+second_user_id, obj_key_2)
	pipeline1.execute_command('UNLINK', obj_key_1)
	pipeline1.execute_command('UNLINK', obj_key_2)
	pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key_1)
	pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key_2)
	pipeline1.execute()



def delete_all_direct_responses_between_two_users(first_user_id, second_user_id):
	"""
	Deletes all direct responses exchanged (and outstanding) between the two parties

	Useful when one party blocks another (p-v-p blocking)
	"""
	first_user_id, second_user_id = str(first_user_id), str(second_user_id)
	my_server = redis.Redis(connection_pool=POOL)
	###############################################################
	# direct responses sent by first_user_id to second_user_id
	obj_list1 = my_server.zrange(DIRECT_RESPONSE_SENDER_RECEIVER+first_user_id+":"+second_user_id,0,-1)

	if obj_list1:
		pipeline1 = my_server.pipeline()
		for obj_key in obj_list1:
			# an obj_key is made up of: DIRECT_RESPONSE_OBJ+obj_type+":"+parent_obj_id+":"+str(sender_id)+":"+target_user_id
			data = obj_key.split(":")
			obj_type, parent_obj_id, sender_id, target_user_id = data[1], data[2], data[3], data[4]
			
			pipeline1.execute_command('UNLINK', obj_key)# getting rid of the obj hash
			pipeline1.zrem(DIRECT_RESPONSE+target_user_id, obj_key)# removing from direct_response_list
			######################################
			pipeline1.zrem(DIRECT_RESPONSE_PARENT+obj_type+":"+parent_obj_id, obj_key)# key not generated for a 1on1
			pipeline1.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+target_user_id, obj_key)# key not generated for a 1on1
			######################################
			pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key)
			
		pipeline1.execute()
	###############################################################
	# direct responses sent by second_user_id to first_user_id
	obj_list2 = my_server.zrange(DIRECT_RESPONSE_SENDER_RECEIVER+second_user_id+":"+first_user_id,0,-1)
	
	if obj_list2:
		pipeline2 = my_server.pipeline()
		for obj_key in obj_list2:
			# an obj_key is made up of: DIRECT_RESPONSE_OBJ+obj_type+":"+parent_obj_id+":"+str(sender_id)+":"+target_user_id
			data = obj_key.split(":")
			obj_type, parent_obj_id, sender_id, target_user_id = data[1], data[2], data[3], data[4]
			
			pipeline2.execute_command('UNLINK', obj_key)# getting rid of the obj hash
			pipeline2.zrem(DIRECT_RESPONSE+target_user_id, obj_key)# removing from direct_response_list
			######################################
			pipeline2.zrem(DIRECT_RESPONSE_PARENT+obj_type+":"+parent_obj_id, obj_key)# key not generated for a 1on1
			pipeline2.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+target_user_id, obj_key)# key not generated for a 1on1
			######################################
			pipeline2.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key)
			
		pipeline2.execute()
	###############################################################


def delete_direct_responses_upon_obj_deletion(obj_type, obj_id):
	"""
	Delete all associated direct responses if an obj is deleted

	Used when mehfils are deleted (has nothing to do with other obj's deletion - e.g. 1on1 deletion)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	list_of_responses = my_server.zrange(DIRECT_RESPONSE_PARENT+obj_type+":"+str(obj_id),0,-1)
	if list_of_responses:
		# proceed with deletion
		pipeline1 = my_server.pipeline()
		for obj_key in list_of_responses:
			data = obj_key.split(":")
			obtp, parent_obj_id, sender_id, target_user_id = data[1], data[2], data[3], data[4]
			pipeline1.execute_command('UNLINK', obj_key)
			pipeline1.zrem(DIRECT_RESPONSE+target_user_id, obj_key)
			pipeline1.zrem(DIRECT_RESPONSE_PARENT+obtp+":"+parent_obj_id, obj_key)
			pipeline1.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+target_user_id, obj_key)
			pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key)
		pipeline1.execute()


def delete_direct_responses_linked_to_obj(obj_type, parent_obj_id, target_user_ids):
	"""
	Used when users are removed from a particular 'obj' (and so can't send direct responses to users on the said post)

	The only use case: when a 'perp' is kicked out of a mehfil (public or private)
	"""
	target_user_ids = map(str,target_user_ids)
	my_server = redis.Redis(connection_pool=POOL)
	list_of_responses = my_server.zrange(DIRECT_RESPONSE_PARENT+obj_type+":"+str(parent_obj_id),0,-1)
	if list_of_responses:
		pipeline1 = my_server.pipeline()
		for obj_key in list_of_responses:
			data = obj_key.split(":")
			obtp, poid, sender_id, receiver_id = data[1], data[2], data[3], data[4]
			if sender_id in target_user_ids:

				# getting rid of all direct responses sent by target_users
				pipeline1.execute_command('UNLINK', obj_key)
				pipeline1.zrem(DIRECT_RESPONSE+receiver_id, obj_key)
				pipeline1.zrem(DIRECT_RESPONSE_PARENT+obtp+":"+poid, obj_key)
				pipeline1.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+receiver_id, obj_key)
				pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key)
			
			if receiver_id in target_user_ids:

				# getting rid of all direct responses received by target_users
				pipeline1.execute_command('UNLINK', obj_key)
				pipeline1.zrem(DIRECT_RESPONSE+receiver_id, obj_key)
				pipeline1.zrem(DIRECT_RESPONSE_PARENT+obtp+":"+poid, obj_key)
				pipeline1.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+receiver_id, obj_key)
				pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key)
		
		pipeline1.execute()


def bulk_delete_selective_dir_reps_of_single_user(user_id, dir_rep_list):
	"""
	Delete the provided dir reps in 'dir_rep_list' for the provided user

	Sole use-case: when deleting entire page's worth of reply notifs
	"""
	my_server = redis.Redis(connection_pool=POOL)

	direct_response_key = DIRECT_RESPONSE+str(user_id)
	if user_id and dir_rep_list:
		pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
		for dir_rep_obj_name in dir_rep_list:
			data = dir_rep_obj_name.split(":")
			obtp, poid, sender_id, receiver_id = data[1], data[2], data[3], data[4]

			pipeline1.execute_command('UNLINK', dir_rep_obj_name)
			pipeline1.zrem(DIRECT_RESPONSE+str(user_id),dir_rep_obj_name)
			pipeline1.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+receiver_id, dir_rep_obj_name)
			pipeline1.zrem(DIRECT_RESPONSE_PARENT+obtp+":"+poid, dir_rep_obj_name)
			pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER,dir_rep_obj_name)
		
		pipeline1.execute()


def bulk_delete_user_direct_responses(target_user_ids):
	"""
	Delete all responses received by provided target_user_ids

	It can help clear out inbox in one button press
	Unused function: This functionality is tested, but NOT shipped
	"""
	if target_user_ids:
		keys_to_delete = []
		target_user_ids = map(str,target_user_ids)
		my_server = redis.Redis(connection_pool=POOL)
		pipeline1 = my_server.pipeline()
		for target_user_id in target_user_ids:
			key_name = DIRECT_RESPONSE+target_user_id
			keys_to_delete.append(key_name)
			pipeline1.zrange(key_name,0,-1)
		direct_response_obj_names, counter = pipeline1.execute(), 0

		pipeline2 = my_server.pipeline()
		for target_user_id in target_user_ids: 
			response_list = direct_response_obj_names[counter]
			if response_list:
				for dir_rep_obj_name in response_list:
					data = dir_rep_obj_name.split(":")
					obtp, poid, sender_id, receiver_id = data[1], data[2], data[3], data[4]
					pipeline2.execute_command('UNLINK', dir_rep_obj_name)
					pipeline2.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+receiver_id, dir_rep_obj_name)
					pipeline2.zrem(DIRECT_RESPONSE_PARENT+obtp+":"+poid, dir_rep_obj_name)
					pipeline2.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER,dir_rep_obj_name)
			counter += 1

		if keys_to_delete:
			pipeline2.execute_command('UNLINK', *keys_to_delete)

		pipeline2.execute()


def hide_direct_response_in_inbox(obj_type,parent_obj_id,reply_id, to_hide,sender_id,receiver_id):
	"""
	Useful for 'hiding' replies in 'inbox' (i.e. direct response list)

	Handles both cases: (i) when reply itself is to be hidden, (ii) when 'base reply' (i.e. base reply on which a reply came) is to be hidden
	
	1) obj_type: '3', '4', '5', '6', '7'
	2) parent_obj_id is group id or post id
	3) reply_id: object_id (e.g. publicreply_id, photocomment_id, mehfil_submission_id, or '0' for 1on1 since it's not needed there)
	4) to_hide: True or False
	5) sender_id: ID of user who sent the direct response
	6) receiver_id: ID of user who received the direct response
	"""
	hide_val = '1' if to_hide else '0'
	parent_obj_id = str(parent_obj_id)
	my_server = redis.Redis(connection_pool=POOL)
	
	##############################################
	# when reply itself is to be hidden
	if receiver_id:
		sender_id, receiver_id = str(sender_id), str(receiver_id)
		dr_obj_key = DIRECT_RESPONSE_OBJ+obj_type+":"+parent_obj_id+":"+sender_id+":"+receiver_id
		json_obj = my_server.get(dr_obj_key)
		if json_obj:
			try:
				obj = json.loads(json_obj)
			except:
				obj = json_backup.loads(json_obj)
			obj['hide_rep'] = hide_val
			ttl = my_server.ttl(dr_obj_key)
			my_server.setex(dr_obj_key,json.dumps(obj),ttl)
		else:
			# nothing to hide - this obj does not exist, so do nothing!
			pass
	
	##############################################
	# when 'base reply' (i.e. base reply on which a reply came) is to be hidden (never run this for obj_type '7' - i.e. 1on1s)
	if reply_id:
		parent_obj_composite_id = obj_type+":"+str(parent_obj_id)
		reply_objs = my_server.zrangebyscore(DIRECT_RESPONSE_PARENT+obj_type+":"+parent_obj_id,reply_id,reply_id)
		if reply_objs:
			json_objs = my_server.mget(*reply_objs)
			data = []
			for json_obj in json_objs:
				try:
					data.append(json.loads(json_obj))
				except:
					data.append(json_backup.loads(json_obj))

			for obj in data:
				# enriching data with 'hidden' key
				obj['hide_tgt'] = hide_val

			counter = 0
			for obj in reply_objs:
				json.dumps(data[counter])
				ttl = my_server.ttl(obj)
				my_server.setex(obj,json.dumps(data[counter]),ttl)
				counter += 1
		

def modify_direct_response_objs(parent_obj_type, parent_obj_id, modification_type, payload):
	"""
	Helps modify the direct response objs in lists

	Solely used when: topic changed in mehfils
	"""

	my_server = redis.Redis(connection_pool=POOL)
	parent_obj_related_dir_rep_objs = my_server.zrange(DIRECT_RESPONSE_PARENT+parent_obj_type+":"+parent_obj_id,0,-1)

	if parent_obj_related_dir_rep_objs:
		# it's a mehfil
		if parent_obj_type in ('5','6'):
			if modification_type == 'topic':
				# Alter the topic text in all related direct response objs
				dir_rep_objs, counter = my_server.mget(*parent_obj_related_dir_rep_objs), 0
				
				for dir_rep_obj_name in parent_obj_related_dir_rep_objs:
					json_data = dir_rep_objs[counter]
					try:
						data = json.loads(json_data)
					except:
						data = json_backup.loads(json_data)
					################
					# Setting the topic and saving everything back
					data['gtp'] = payload
					final_json_data = json.dumps(data)
					obj_ttl = my_server.ttl(dir_rep_obj_name)
					my_server.setex(dir_rep_obj_name,final_json_data,obj_ttl)
					################
					counter += 1

		# it's a 1on1 
		# UNUSED - because 1on1 direct responses just over-write eachother so we don't care about being uber-accurate
		# UNUSED - also because 1on1 have no DIRECT_RESPONSE_PARENT object (it was removed post-launch of this feature)
		elif parent_obj_type == '7':
			if modification_type == 'topic':
				# Alter the topic text in all related direct response objs
				dir_rep_objs, counter = my_server.mget(*parent_obj_related_dir_rep_objs), 0

				for dir_rep_obj_name in parent_obj_related_dir_rep_objs:
					json_data = dir_rep_objs[counter]
					try:
						data = json.loads(json_data)
					except:
						data = json_backup.loads(json_data)
					################
					# Setting the topic and saving everything back
					data['ptx'] = payload
					json.dumps(data)
					obj_ttl = my_server.ttl(dir_rep_obj_name)
					my_server.setex(dir_rep_obj_name,final_json_data,obj_ttl)
					################
					counter += 1


########################### Showing num replies in 'Inbox' ###########################


def get_reply_count(user_id):
	"""
	Shows number of outstanding replies in the navbar
	"""
	count = redis.Redis(connection_pool=POOL).zcard(DIRECT_RESPONSE+str(user_id))
	return count if count < 100 else '99+'


##################### Logging basic metrics of direct_reply usage #####################


def log_direct_response_metrics(action_status, action_type, num_skips, obj_type):
	"""
	Logs basic metrics of direct response usage

	Statistics that can be calculated include:
	- Total replies_of_replies / Total replies (measures what % of replies are in answer to another reply)
	- Total skips / Total replies (measures what % of replies are skipped)

	action_status: True or False
	action_type: '1' (replied) or '3' (skipped)
	"""
	if action_type == '1':
		my_server = redis.Redis(connection_pool=POOL)
		if obj_type == '7':
			# this is a 1on1
			if action_status:
				my_server.zincrby(DIRECT_RESPONSE_METRICS,'1on1_rep_to_rep',amount=1)
			my_server.zincrby(DIRECT_RESPONSE_METRICS,'1on1_total_reps',amount=1)
		elif obj_type == '3':
			# this is text post comment
			if action_status:
				my_server.zincrby(DIRECT_RESPONSE_METRICS,'txt_post_rep_to_rep',amount=1)
			my_server.zincrby(DIRECT_RESPONSE_METRICS,'txt_post_total_reps',amount=1)
		elif obj_type == '4':
			# this is an img post comment
			if action_status:
				my_server.zincrby(DIRECT_RESPONSE_METRICS,'img_post_rep_to_rep',amount=1)
			my_server.zincrby(DIRECT_RESPONSE_METRICS,'img_post_total_reps',amount=1)
		elif obj_type == '5':
			# this is a public mehfil
			if action_status:
				my_server.zincrby(DIRECT_RESPONSE_METRICS,'prv_mef_rep_to_rep',amount=1)
			my_server.zincrby(DIRECT_RESPONSE_METRICS,'prv_mef_total_reps',amount=1)
		elif obj_type == '6':
			# this is a private mehfil
			if action_status:
				my_server.zincrby(DIRECT_RESPONSE_METRICS,'pub_mef_rep_to_rep',amount=1)
			my_server.zincrby(DIRECT_RESPONSE_METRICS,'pub_mef_total_reps',amount=1)
		else:
			# these are posts
			pass
	elif action_type == '3':
		redis.Redis(connection_pool=POOL).zincrby(DIRECT_RESPONSE_METRICS,'skips',amount=num_skips)


##################### Maintaining post visitors #####################


def get_last_comment_time(commenter_id, obj_owner_id, obj_hash_name):
	"""
	Retrieve last comment time (if it exists)
	"""
	return redis.Redis(connection_pool=POOL).zscore(POSTER_VISITORS+str(obj_owner_id),obj_hash_name+":"+str(commenter_id))
	

def set_comment_history(obj_hash_name, obj_owner_id, commenter_id, time_now):
	"""
	Logs who all visited a user's posts in the last 3 days
	"""
	if obj_hash_name and obj_owner_id:
		visitation_key = POSTER_VISITORS+str(obj_owner_id)
		payload = obj_hash_name+":"+str(commenter_id)
		my_server = redis.Redis(connection_pool=POOL)

		pipeline1 = my_server.pipeline()
		pipeline1.zadd(visitation_key,payload,time_now)
		pipeline1.expire(visitation_key,POST_HISTORY_TTL)
		pipeline1.execute()

		############################
		if random() < 0.01:
			three_days_ago = time_now - POST_HISTORY_TTL
			my_server.zremrangebyscore(visitation_key,'-inf',three_days_ago)


######################################### Log direct repsonse rate ############################################

REPLY_RATE = 'rr:'

def log_rate_of_reply(replier_id, text_len, time_now):
	"""
	Anti-flood logger

	Used to determine whether a user is flooding
	"""
	reply_rate_key = REPLY_RATE+str(replier_id)
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zadd(reply_rate_key,text_len,time_now)
	my_server.expire(reply_rate_key,30)#expire the data after 30 secs of inactivity


def retrieve_prev_replier_rate(replier_id):
	"""
	Retrieves the rate of last 3 replies (if key hasn't expired yet)
	"""
	return redis.Redis(connection_pool=POOL).zrevrange(REPLY_RATE+str(replier_id),0,2,withscores=True)