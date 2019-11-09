import json as json_backup
from random import random
import redis, time
import ujson as json
from location import REDLOC9
from score import REPLY_OBJECT_TTL, POST_HISTORY_TTL

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC9, db=0)

DIRECT_RESPONSE_OBJ = 'drobj:'# the object containing the actual details of the direct response (JSON format)

DIRECT_RESPONSE = 'dr:'#sorted set containing all responses received by a particular user (useful for populating "received direct responses" list)
DIRECT_RESPONSE_PARENT = 'drp:'#sorted set containing all responses attached to a particular parent obj (useful in parent obj deletion, or 'hiding'/'unhiding' a reply)
DIRECT_RESPONSE_SENDER_RECEIVER = 'drsr:'#sorted set containing all responses attached to a particular sender:receiver pair (useful in pvp blocking)
GLOBAL_DIRECT_RESPONSE_LOGGER = 'gdrl'# global set containing all direct responses, useful for "clean-up" scheduled tasks (performed later)

POSTER_VISITORS = 'pv:'# visitors who visit certain posts

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
	pipeline1.setex(obj_key,json_data,REPLY_OBJECT_TTL)	
	pipeline1.zadd(dr_key,obj_key,expire_at)
	pipeline1.zadd(dr_po_key,obj_key,reply_id)
	pipeline1.zadd(dr_sr_key,obj_key,expire_at)
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
	"""
	target_user_id = str(target_user_id)
	parent_obj_composite_id = obj_type+":"+parent_obj_id
	dr_key = DIRECT_RESPONSE+target_user_id
	obj_key = DIRECT_RESPONSE_OBJ+parent_obj_composite_id+":"+sender_id+":"+target_user_id
	sr_key = DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+str(target_user_id)# sender receiver key
	my_server = redis.Redis(connection_pool=POOL)
	
	# obj exists - process deletion
	if my_server.zscore(dr_key,obj_key):
		dr_po_key = DIRECT_RESPONSE_PARENT+parent_obj_composite_id
		my_server.execute_command('UNLINK', obj_key)
		my_server.zrem(dr_key,obj_key)
		my_server.zrem(dr_po_key,obj_key)
		my_server.zrem(sr_key,obj_key)
		my_server.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER,obj_key)
		return True
	# obj does not exist
	else:
		return False


def delete_all_direct_responses_between_two_users(first_user_id, second_user_id):
	"""
	Deletes all direct responses exchanged (and outstanding) between the two parties

	Useful when one party blocks another (p-v-p blocking)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	###############################################################
	# direct responses sent by first_user_id to second_user_id
	obj_list1 = my_server.zrange(DIRECT_RESPONSE_SENDER_RECEIVER+str(first_user_id)+":"+str(second_user_id),0,-1)

	if obj_list1:
		pipeline1 = my_server.pipeline()
		for obj_key in obj_list1:
			# an obj_key is made up of: DIRECT_RESPONSE_OBJ+obj_type+":"+parent_obj_id+":"+str(sender_id)+":"+target_user_id
			data = obj_key.split(":")
			obj_type, parent_obj_id, sender_id, target_user_id = data[1], data[2], data[3], data[4]
			
			pipeline1.execute_command('UNLINK', obj_key)# getting rid of the obj hash
			pipeline1.zrem(DIRECT_RESPONSE+target_user_id, obj_key)# removing from direct_response_list
			pipeline1.zrem(DIRECT_RESPONSE_PARENT+obj_type+":"+parent_obj_id, obj_key)# removing from the parent obj list
			pipeline1.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+target_user_id, obj_key)
			pipeline1.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key)
			
		pipeline1.execute()
	###############################################################
	# direct responses sent by second_user_id to first_user_id
	obj_list2 = my_server.zrange(DIRECT_RESPONSE_SENDER_RECEIVER+str(second_user_id)+":"+str(first_user_id),0,-1)
	
	if obj_list2:
		pipeline2 = my_server.pipeline()
		for obj_key in obj_list2:
			# an obj_key is made up of: DIRECT_RESPONSE_OBJ+obj_type+":"+parent_obj_id+":"+str(sender_id)+":"+target_user_id
			data = obj_key.split(":")
			obj_type, parent_obj_id, sender_id, target_user_id = data[1], data[2], data[3], data[4]
			
			pipeline2.execute_command('UNLINK', obj_key)# getting rid of the obj hash
			pipeline2.zrem(DIRECT_RESPONSE+target_user_id, obj_key)# removing from direct_response_list
			pipeline2.zrem(DIRECT_RESPONSE_PARENT+obj_type+":"+parent_obj_id, obj_key)# removing from the parent obj list
			pipeline2.zrem(DIRECT_RESPONSE_SENDER_RECEIVER+sender_id+":"+target_user_id, obj_key)
			pipeline2.zrem(GLOBAL_DIRECT_RESPONSE_LOGGER, obj_key)
			
		pipeline2.execute()
	###############################################################


def delete_direct_responses_upon_obj_deletion(obj_type, obj_id):
	"""
	Delete all associated direct responses if an obj is deleted

	Useful when mehfils or 1on1s are deleted, etc
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

	Biggest use case: when a 'perp' is kicked out of a mehfil
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

	Note: This functionality is tested, but not shipped
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
	# when 'base reply' (i.e. base reply on which a reply came) is to be hidden (never run for obj_type '7' - i.e. 1on1s)
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

	Useful when:
	1) Topic changed in mehfils
	2) Users hide nicknames in 1o1s (unused at the moment)
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


##################### Showing num replies in 'Inbox' #####################


def get_reply_count(user_id):
	"""
	Shows number of outstanding replies in the navbar
	"""
	count = redis.Redis(connection_pool=POOL).zcard(DIRECT_RESPONSE+str(user_id))
	return count if count < 100 else '99+'


##################### Logging basic metrics of direct_reply usage #####################


def log_direct_response_metrics(action_status, action_type, num_skips):
	"""
	Logs basic metrics of direct response usage

	Statistics that can be calculated include:
	- Total replies_of_replies / Total replies (measures what % of replies are in answer to another reply)
	- Total skips / Total replies (measures what % of replies are skipped)

	action_status: True or False
	action_type: '1' (replied) or '3' (skipped)
	"""
	if action_type == '1':
		if action_status:
			redis.Redis(connection_pool=POOL).zincrby(DIRECT_RESPONSE_METRICS,'replies_to_replies',amount=1)
		redis.Redis(connection_pool=POOL).zincrby(DIRECT_RESPONSE_METRICS,'total_replies',amount=1)
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