import json as json_backup
from random import random
import redis, time
import ujson as json
from location import REDLOC9
from redis5 import retrieve_bulk_group_labels
from redis6 import retrieve_group_topics_in_bulk
from redis4 import retrieve_post_details_in_bulk
from score import REPLY_OBJECT_TTL, POST_HISTORY_TTL, NUM_ACTIVITY_ITEMS_PER_PAGE

from models import UserFan, Report, Link
from redis4 import retrieve_bulk_credentials
from utilities import beautiful_date, convert_to_epoch
from redis7 import get_obj_owner, change_delete_status_of_obj_hash, trim_expired_user_submissions
from score import PUBLIC_SUBMISSION_TTL, TTL_FOLLOWER_LIST, TTL_FOLLOWER_STRING, RATELIMIT_REMOVED_FOLLOWER, SHORT_RATELIMIT_UNFOLLOWER
import threading

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC9, db=0)

TEN_MINS = 600# 10 minutes in seconds
ONE_HOUR = 3600# 1 hour in seconds
ONE_DAY = 86400# 1 day in seconds
ONE_WEEK = 604800# 1 week in seconds
TWO_WEEKS = 172800# 2 weeks in seconds

######################## TO DO ############################
# FOLLOWING_LIST = "fgl:"#a sorted set of all the user_ids that a given user follows, sorted by the time of subscription

FOLLOWERS_LIST = "fsl:"#a sorted set containing all subscriber ids of a given target user id, sorted by time of subscription
FOLLOWER_STRING = "fs:"#a key that contains a concatenated list of a given user's fans
NUM_VERIFIED_FOLLOWERS = "nvf:" #a key that stores the number of verified followers a given user has
NUM_ALL_FOLLOWERS = "naf:" #a key that stores the number of followers a given user has
NO_FOLLOWERS = "nof:" # a key that is set for a user who has zero followers (verified and unverified)
USER_FEED = "uf:" # a key that keeps all the posts by all the people you follow
SHORT_LIVED_CONTENT_EXPIRE_TIMES = "slcet:" # a key that keeps short-lived posts from all the people you follow sorted by expiry times, useful for culling expired items in a user's feed

RATE_LIMIT_FOLLOWER = "rlf:" #a key that stores ratelimit ttl of a target_id user after removing target as a follower or when a user unfollowes another user
FOLLOWER_FANOUTS_AND_EXPIRES = 'ffe'# global sorted set containing all fan-outs and their fan-out times (useful for data expiry)
FOLLOWER_FANOUTS_AND_SUBMITTERS = 'ffu'# global sorted set containing all fan-outs and their submitter IDs (useful for data expiry)
TEMP_ALL_FOLLOWERS = 'taf:' # a set containing all IDs that a post was shared with
FOLLOWING_COUNT = 'fgc:' # a key that stores the count of people a user is following 
CACHED_PRIVATE_FEED_HISTORY = 'cprvfh:'
CACHED_LIMITED_FEED_HISTORY = 'climfh:'
CACHED_PUBLIC_FEED_HISTORY = 'cpubfh:'

LAST_SELECTED_FOLLOWERS = 'lsf:' # contains a list of followers selected for a private fanout

############################# Retrieving data shown in a user's follower feed #############################


def retrieve_custom_feed_index(user_id, obj_hash):
	"""
	Returns exact index an object is stored at in USER_FEED+user_id

	Useful when needing to redirect to precise object after interacting with a post
	"""
	return redis.Redis(connection_pool=POOL).zrevrank(USER_FEED+str(user_id),obj_hash)


def get_custom_feed(user_id, start_idx=0,end_idx=-1, with_feed_size=False):
	"""
	Retrieve given user's feed populated by people user follows
	"""
	user_id=str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	if with_feed_size:
		expired_items = my_server.zrangebyscore(SHORT_LIVED_CONTENT_EXPIRE_TIMES+user_id,'-inf',time.time())
		if expired_items:
			my_server.zrem(USER_FEED+user_id,*expired_items)
			my_server.zrem(SHORT_LIVED_CONTENT_EXPIRE_TIMES+user_id,*expired_items)
		obj_list = my_server.zrevrange(USER_FEED+user_id, start_idx, end_idx), my_server.zcard(USER_FEED+user_id)
		return obj_list

	else:
		expired_items = my_server.zrangebyscore(SHORT_LIVED_CONTENT_EXPIRE_TIMES+user_id,'-inf',time.time())
		if expired_items:
			my_server.zrem(USER_FEED+user_id,*expired_items)
			my_server.zrem(SHORT_LIVED_CONTENT_EXPIRE_TIMES+user_id,*expired_items)
		obj_list = my_server.zrevrange(USER_FEED+user_id, start_idx, end_idx)
		return obj_list


############################# Fan button state helper funcs #############################


def filter_following(user_list,own_id):
	"""
	This returns IDs of 'stars' who may have posted in a given time window

	Useful for displaying toggle-able fan buttons under posts in all global feeds (e.g. Home, Topics, Fotos, etc)
	"""
	# Method1:
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()

	for user_id in user_list:
		pipeline1.zscore(FOLLOWERS_LIST+user_id,own_id)
	result1 = pipeline1.execute()

	counter, ids_you_are_following = 0, set()
	for user_id in user_list:
		if result1[counter]:
			ids_you_are_following.add(user_id)
		else:
			if my_server.exists(NO_FOLLOWERS+user_id):
				pass
			elif UserFan.objects.filter(star_id=user_id, fan_id=own_id).exists():
				ids_you_are_following.add(user_id)
		counter += 1
	return ids_you_are_following


def check_if_follower(user_id, target_user_id, with_db_lookup=False):
	"""
	Checks if 'user_id' is subscribed to 'target_user_id'

	Useful in showing the correct state of the 'follow' button when visiting profiles
	Does not check whether user_id and target_user_id are one and the same person
	"""
	if user_id:
		if with_db_lookup:
			if redis.Redis(connection_pool=POOL).zscore(FOLLOWERS_LIST+str(target_user_id),user_id):
				return True
			else:
				# if time_of_following is None, it might be that the keys have expired from redis - fall back to the DB
				return UserFan.objects.filter(star_id=target_user_id, fan_id=user_id).exists()
		else:
			if redis.Redis(connection_pool=POOL).zscore(FOLLOWERS_LIST+str(target_user_id),user_id):
				return True
			else:
				return False
	return False

############################# Add/Remove fans #############################


def recreate_fan_signature_in_redis(target_user_id, my_server):
	"""
	This function pulls follower Ids and fanning times from postgres and creates a redis object for it
	"""
	fan_payload, fan_ids = [], []
	target_fan_ids_and_fanning_times = UserFan.objects.filter(star_id=target_user_id).values_list('fan_id','fanning_time')
	target_user_id = str(target_user_id)
	for target_fan_id, fanning_time in target_fan_ids_and_fanning_times:
		###################################
		fan_ids.append(target_fan_id)
		###################################
		fan_payload.append(target_fan_id)
		fan_payload.append(convert_to_epoch(fanning_time))
	if fan_payload:
		my_server.zadd(FOLLOWERS_LIST+target_user_id,*fan_payload)
		my_server.expire(FOLLOWERS_LIST+target_user_id,TTL_FOLLOWER_LIST)
		###################################
		follower_string = ":"
		for target_fan_id in fan_ids:
			follower_string += str(target_fan_id)+":"
		my_server.setex(FOLLOWER_STRING+target_user_id,follower_string,TTL_FOLLOWER_STRING)
		my_server.execute_command('UNLINK', NO_FOLLOWERS+target_user_id)
	else:
		# no followers exist - hence setting the requisite key
		my_server.setex(NO_FOLLOWERS+target_user_id,'1',ONE_DAY)	


def add_to_follower_string(lock, my_server, user_id,target_user_id):
	"""
	Helper function of add_follower()
	"""
	follower_string = FOLLOWER_STRING+target_user_id
	lock.acquire()
	string = my_server.get(follower_string)
	if string:
		string = string + user_id + ":"
		my_server.setex(follower_string,string,TTL_FOLLOWER_STRING)
	else: 
		# 'string' does not exist - maybe something went wrong - don't take a chance, just attempt to recreate everything via the DB
		recreate_fan_signature_in_redis(target_user_id,my_server)
	lock.release()



def add_follower(user_id, target_user_id, verification_status, time_now):
	"""
	Add user_id as a subscriber to target_user_id
	"""
	user_id, target_user_id = str(user_id), str(target_user_id)
	followers_list = FOLLOWERS_LIST+target_user_id
	delete_new_follower_notif(target_user_id)
	# adding follower to relevant postgresql table
	UserFan.objects.create(star_id=target_user_id, fan_id=user_id, fan_verification_status=verification_status, fanning_time=beautiful_date(time_now, format_type='4'))

	my_server = redis.Redis(connection_pool=POOL)

	# invalidate cached follower count since follower count just changed
	if verification_status == '1':
		invalidate_verif_follower_count(target_user_id)
	
	invalidate_following_count(user_id)# invalidate following count (star count) whether verified or not		

	if my_server.exists(followers_list):
		# adding to the relevant sorted sets
		my_server.zadd(followers_list, user_id, time_now)
		# update expiry of the list
		my_server.expire(followers_list,TTL_FOLLOWER_LIST)
		# adding the new addition to the target's 'follower string' (a mechanism that makes fan-outs faster) 
		lock = threading.Lock()
		t = threading.Thread(target = add_to_follower_string, args = (lock,my_server,user_id,target_user_id))
		t.start()
		t.join()

	elif my_server.exists(FOLLOWER_STRING+target_user_id):		
		# just adding the new addition to the target's 'follower string' (a mechanism that makes fan-outs faster) 
		lock = threading.Lock()
		u = threading.Thread(target = add_to_follower_string, args = (lock,my_server,user_id,target_user_id))
		u.start()
		u.join()

	else:
		# this person has 0 fans for sure. Set the key (but no need to add anything else to redis)
		my_server.delete(NO_FOLLOWERS+target_user_id)


def change_verification_status(user_id,type_of_operation):
	if type_of_operation == 'verified':
		UserFan.objects.filter(fan_id=user_id).update(fan_verification_status='1')
	
	else:
		UserFan.objects.filter(fan_id=user_id).update(fan_verification_status='0')

	
def remove_from_follower_string(lock, my_server, user_id,target_user_id):
	"""
	Helper function of remove_follower()
	"""
	follower_string_key = FOLLOWER_STRING+target_user_id
	lock.acquire()
	follower_string_payload = my_server.get(follower_string_key)
	if follower_string_payload:
		split_follower_string = follower_string_payload.split(":"+user_id+":")# divides the string into two parts, at the point where user_id existed in the string
		if split_follower_string[0] or split_follower_string[1]:
			follower_string_payload = ":".join(split_follower_string)
			my_server.setex(follower_string_key,follower_string_payload,TTL_FOLLOWER_STRING)
		else:
			# this target_user_id doesn't have any fans anymore - user_id was the last fan and just got removed
			
			my_server.setex(NO_FOLLOWERS+target_user_id,'1',ONE_DAY)
			# just remove the follower string
			my_server.execute_command('UNLINK', follower_string_key)
	lock.release()	



def remove_follower(follower_id, star_id, follower_verification_status):
	"""
	Remove follower_id as a follower from star_id
	
	Useful when:
	(i) Follower unfollows the star
	(ii) Star forcibly removes the follower
	(iii) Once pvp banning is enforced, we remove the follower automatically
	"""
	follower_id, star_id = str(follower_id), str(star_id)
	followers_list_key = FOLLOWERS_LIST+star_id

	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(followers_list_key):
		if my_server.zscore(followers_list_key, follower_id):
			# remove this subscriber/follower
			delete_new_follower_notif(star_id)

			# remove from POSTGRESQL table
			UserFan.objects.filter(star_id=star_id, fan_id=follower_id).delete()

			# invalidate cached follower count since follower count just changed
			if follower_verification_status == '1':
				invalidate_verif_follower_count(star_id)
			
			# invalidate following count (star count) whether verified or not
			invalidate_following_count(follower_id)

			# remove the follower from redis (follower-list)
			my_server.zrem(followers_list_key, follower_id)

			# update expiry of the list
			my_server.expire(followers_list_key, TTL_FOLLOWER_LIST)

			# remove the follower from redis (follower-string), but in a way that avoids race conditions (i.e. atomic operation)
			lock = threading.Lock()
			u = threading.Thread(target = remove_from_follower_string, args = (lock,my_server,follower_id,star_id))
			u.start()
			u.join()

		else:
			# do nothing, since the user is not following star_id
			pass
	elif my_server.exists(FOLLOWER_STRING+star_id):
		
		# remove from POSTGRESQL table
		UserFan.objects.filter(star_id=star_id, fan_id=follower_id).delete()
		delete_new_follower_notif(star_id)
		
		# invalidate cached follower count since follower count just changed
		if follower_verification_status == '1':
			invalidate_verif_follower_count(star_id)

		# invalidate following count (star count) whether verified or not
		invalidate_following_count(follower_id)
		
		# remove the follower_id from the follower_string without race condition
		lock = threading.Lock()
		u = threading.Thread(target = remove_from_follower_string, args = (lock,my_server,follower_id,star_id))
		u.start()
		u.join()

	else:
		# look up the target's postgres follower table, and simply remove from that (no need to manipulate redis lists since they've expired already)
		UserFan.objects.filter(star_id=star_id, fan_id=follower_id).delete()
		delete_new_follower_notif(star_id)
		
		# invalidate cached follower count since follower count just changed
		if follower_verification_status == '1':
			invalidate_verif_follower_count(star_id)

		# invalidate following count (star count) whether verified or not
		invalidate_following_count(follower_id)


################################## Fan out to followers ##################################

def fan_out_to_followers(user_id, obj_hash, time_now, expire_at=None, follower_list=None): #modify to take fan_ids
	"""
	Fans out to a user's followers

	Can potentially include 'reach count' in obj_hash before zadding it to various followers' lists
	Called by tasks.py
	"""
	user_id = str(user_id)
	
	# redis hash obj of the content will exist for at least 1 week (only if it's not limited by time)
	add_to_short_lived_item_expireat_feed = True
	if expire_at is None:# case of no-expiry - can potentially live forever
		add_to_short_lived_item_expireat_feed = False
		expire_at = time_now+PUBLIC_SUBMISSION_TTL#setting ttl of 'forever' content to 1 week for memory optimization reasons

	################################################
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	
	# CASE 1) This case caters to fanning out to a subset of followers (input via 'follower_list')
	if follower_list:
		save_last_post_selected_followers(followers=follower_list,poster_id=user_id)
		follower_list.append(int(user_id))# appending own self to populate own feed as well
		set_temp_post_selected_followers(obj_hash_name=obj_hash,followers=follower_list,expire_at=expire_at)# temporarily save user_ids for a time-limited post (including poster ID)
		
		follower_string = ':'

		list_of_db_objs = []

		for follower_id in follower_list:
			############ if follower_id not in muted_follower_ids: # if we choose to add a mute status ############
			
			# concatenating user_id with obj hash to support toggle-able fan buttons
			pipeline1.zadd(USER_FEED+str(follower_id),obj_hash,time_now)# fanning out to the selected follower
			if add_to_short_lived_item_expireat_feed:
				pipeline1.zadd(SHORT_LIVED_CONTENT_EXPIRE_TIMES+str(follower_id),obj_hash,expire_at)
			follower_string = follower_string+str(follower_id)+':'# constructing a custom follower string for this 'selective' case
			######################
			# Create list of Postgresql entries for selected followers
			data = obj_hash.partition(":")
			obj_type, obj_id = data[0], data[-1]
			# if obj_type == 'tx':
			list_of_db_objs.append(Report(reporter_id=user_id,which_link_id=obj_id,target_id=follower_id))
			# else:
			# 	list_of_db_objs.append(Report(reporter_id=user_id,which_photo_id=obj_id,target_id=follower_id))

		# Create Postgresql DB entries in bulk
		if list_of_db_objs:
			Report.objects.bulk_create(list_of_db_objs)
	else:
		
		# CASE 2) this case caters to fanning out to only oneself (because no followers exist)
		if my_server.exists(NO_FOLLOWERS+user_id):
			# this person has no fan - short-circuit fanning out (but do add to poster's feed)
			pipeline1.zadd(USER_FEED+user_id,obj_hash,time_now)# no fans, just add to poster's feed
			if add_to_short_lived_item_expireat_feed:
				pipeline1.zadd(SHORT_LIVED_CONTENT_EXPIRE_TIMES+user_id,obj_hash,expire_at)
			follower_string = ":"+user_id+":"# follower string is solely poster's ID 

		else:
			# CASE 3) this case caters to fanning out to all followers	
			follower_string = my_server.get(FOLLOWER_STRING+user_id)# overriding follower_string via redis (preset in the first line of the func)
			if follower_string:
				# fan out to followers
				follower_list = follower_string[1:-1].split(":")	
				follower_list.append(user_id)# appending poster ID, to populate poster feed as well			
				for follower_id in follower_list:
					# concatenating user_id with obj hash to support toggle-able fan buttons
					pipeline1.zadd(USER_FEED+str(follower_id),obj_hash,time_now)
					if add_to_short_lived_item_expireat_feed:
						pipeline1.zadd(SHORT_LIVED_CONTENT_EXPIRE_TIMES+str(follower_id),obj_hash,expire_at)
				follower_string = follower_string+user_id+":"# concatenating poster ID into follower string

			else:
				# follower_string does not exist; reconstruct fan-string and then fan-out to followers
				recreate_fan_signature_in_redis(user_id, my_server)
				follower_string = my_server.get(FOLLOWER_STRING+user_id)

				if follower_string:	
					# fan out to followers
					follower_list = follower_string[1:-1].split(":")
					follower_list.append(user_id)# appending poster ID, to populate poster feed as well	
					for follower_id in follower_list:
						# concatenating user_id with obj hash to support toggle-able fan buttons
						pipeline1.zadd(USER_FEED+str(follower_id),obj_hash,time_now)
						if add_to_short_lived_item_expireat_feed:
							pipeline1.zadd(SHORT_LIVED_CONTENT_EXPIRE_TIMES+str(follower_id),obj_hash,expire_at)
					follower_string = follower_string+user_id+":"# concatenating poster ID into follower string
				
				else:
					# probably never happens - but nevertheless, fan-out to poster ID (since no followers found)
					pipeline1.zadd(USER_FEED+user_id,obj_hash,time_now)# no fans, just add to poster feed
					if add_to_short_lived_item_expireat_feed:
						pipeline1.zadd(SHORT_LIVED_CONTENT_EXPIRE_TIMES+user_id,obj_hash,expire_at)
					follower_string = ":"+user_id+":"# follower string is solely poster's ID 

	pipeline1.execute()
	log_follower_fanout(follower_string=follower_string, obj_hash=obj_hash, submitter_id=user_id, time_now=time_now)	
						

######################################### Logging Subscriber Fanouts ####################################


def log_follower_fanout(follower_string, obj_hash, submitter_id, time_now):
	"""
	Logs the targeted feeds and the submitted object in a global sorted set

	This is useful for periodic truncation of expired items and/or handling banned users whose feeds are to be eliminated
	"""
	if follower_string:
		payload = follower_string+"*"+obj_hash
		expire_at = int(time_now+PUBLIC_SUBMISSION_TTL)
		my_server = redis.Redis(connection_pool=POOL)
		my_server.zadd(FOLLOWER_FANOUTS_AND_EXPIRES, payload, expire_at)
		my_server.zadd(FOLLOWER_FANOUTS_AND_SUBMITTERS, payload, submitter_id)


def trim_expired_fanouts(submitter_id=None):
	"""
	Scheduled task that trims user feeds so that redis memory is released

	The policy is to keep objects around that are younger than 1 week (trim everything else)
	Called every 6 hours from tasks.py
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if submitter_id:
		fanned_out_objs = set()
		submitter_id = float(submitter_id)
		user_fanouts = my_server.zrangebyscore(FOLLOWER_FANOUTS_AND_SUBMITTERS,submitter_id,submitter_id)
		if user_fanouts:
			pipeline1 = my_server.pipeline()
			for submission in user_fanouts:
				data = submission.rpartition("*")
				obj_hash, follower_string = data[2], data[0]
				follower_ids = follower_string[1:-1].split(":")

				for follower_id in follower_ids:
					pipeline1.zrem(USER_FEED+follower_id,obj_hash)
					pipeline1.zrem(SHORT_LIVED_CONTENT_EXPIRE_TIMES+follower_id,obj_hash)
				# run the following statement in redis7 since obj_hash exists there
				# my_server.execute_command('UNLINK', obj_hash)
				fanned_out_objs.add(obj_hash)
			pipeline1.zrem(FOLLOWER_FANOUTS_AND_EXPIRES,*user_fanouts)
			pipeline1.zrem(FOLLOWER_FANOUTS_AND_SUBMITTERS,*user_fanouts)
			pipeline1.execute()
		return fanned_out_objs

	else:
		expired_fanouts = my_server.zrangebyscore(FOLLOWER_FANOUTS_AND_EXPIRES,'-inf',time.time())
		if expired_fanouts:
			pipeline1 = my_server.pipeline()
			for expired_fanout in expired_fanouts:
				data = expired_fanout.rpartition("*")
				obj_hash, follower_string = data[2], data[0]
				follower_ids = follower_string[1:-1].split(":")

				for follower_id in follower_ids:
					pipeline1.zrem(USER_FEED+follower_id,obj_hash)
					pipeline1.zrem(SHORT_LIVED_CONTENT_EXPIRE_TIMES+follower_id,obj_hash)

			pipeline1.zrem(FOLLOWER_FANOUTS_AND_EXPIRES, *expired_fanouts)
			pipeline1.zrem(FOLLOWER_FANOUTS_AND_SUBMITTERS, *expired_fanouts)
			pipeline1.execute()
		return []

################################## Displaying follower counts or IDs ##################################

def get_verified_follower_count(user_id):
	"""
	Returns how many followers user_id has

	Useful when number of followers are to be shown in the user's profile (About page, etc)
	"""
	user_id = str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(NO_FOLLOWERS+user_id):
		return 0
	else:
		follower_count = my_server.get(NUM_VERIFIED_FOLLOWERS+user_id)#retrieve follower count from redis if it exists
		# retrieve follower count from DB and cache it
		if follower_count:
			return follower_count
		else:
			follower_count = UserFan.objects.filter(star_id=user_id,fan_verification_status='1').count()
			my_server.setex(NUM_VERIFIED_FOLLOWERS+user_id,follower_count,ONE_DAY)#delete this at fan removal or addition
			return follower_count


def get_all_follower_count(user_id):
	"""
	Returns how many followers user_id has

	ONLY USER FOR LOGGERS
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(NO_FOLLOWERS+str(user_id)):
		return 0
	else:
		return UserFan.objects.filter(star_id=user_id,fan_verification_status='1').count()

		
def followers_exist(user_id):
	"""
	Returns whether followers exist
	"""
	return UserFan.objects.filter(star_id=user_id).exists()
	

def invalidate_verif_follower_count(user_id):
	"""
	Deletes the cached 'follower count' attributed to a given user_id
	"""
	redis.Redis(connection_pool=POOL).execute_command('UNLINK', NUM_VERIFIED_FOLLOWERS+str(user_id))


def retrieve_follower_data(user_id, start_idx=0, end_idx=-1, with_follower_count=False, with_follower_count_since_last_seen=None):
	"""
	Returns list of follower_IDs, following_times, follower_unames, follower_avurls, new status (following the given user_id)

	Can optionally also return:
	'Total follower' counts (e.g. when showing the total count in the user's follower listing)
	'New follower' counts (e.g. when showing a 'new followers' notification on custom home)
	"""
	user_id = str(user_id)
	follower_key = FOLLOWERS_LIST+user_id

	###########################
	# Step 1) Determine the most recent time a user viewed their fans - this enables us to attach a 'new' status alongwith new fan data (useful in a bunch of scenarios)
	if with_follower_count_since_last_seen:
		only_count_recent_followers = True# user has viewed the 'custom home' page, which is responsible for generating a 'new followers' notification
		most_recent_skip_time = with_follower_count_since_last_seen# this flag contains the most recent time of viewing 'custom home' by user_id
	else:
		only_count_recent_followers = False# user has never viewed the 'custom home' page
		most_recent_skip_time = get_user_activity_event_time(user_id)# no need to convert to float, a float value is returned by the function anyway
	############################
	# Step 2) Retreive follower ids and times of either all the fans to be shown in a fan page, or just new fans (to be shown in a new fan notification)
	my_server = redis.Redis(connection_pool=POOL)
	
	if with_follower_count_since_last_seen:	
		# only retrieve recent followers that lie within the given time window
		follower_ids_and_times = my_server.zrevrangebyscore(follower_key,'+inf', most_recent_skip_time, withscores=True)
	else:
		# retrieve all followers to be shown on the page
		follower_ids_and_times = my_server.zrevrange(follower_key, start_idx, end_idx, withscores=True)

	################################################################
	# Step 3)
	if not follower_ids_and_times:
		# use the DB to populate followers
		recreate_fan_signature_in_redis(user_id, my_server)
		if my_server.exists(NO_FOLLOWERS+user_id):
			if with_follower_count or with_follower_count_since_last_seen:
				return [], 0# sending empty [] at this point
			else:
				return []# sending empty [] at this point
		else:
			if with_follower_count_since_last_seen:
				# only retrieve recent followers that lie within the given time window
				follower_ids_and_times = my_server.zrevrangebyscore(follower_key, '+inf', most_recent_skip_time, withscores=True)
			
			else:
				# retrieve all followers that lie within the gives indices (for a paginated view)
				follower_ids_and_times = my_server.zrevrange(follower_key, start_idx, end_idx, withscores=True)

	################################################################
	# Step 4)
	follower_unames_and_avurls = retrieve_bulk_credentials([follower_id for follower_id, following_time in follower_ids_and_times])
	
	num_recent_followers, final_result = 0, []
	for follower_id, following_time in follower_ids_and_times:
		follower_id = int(follower_id)
		
		if following_time > most_recent_skip_time:
			final_result.append((follower_id, following_time, follower_unames_and_avurls[follower_id]['uname'], \
				follower_unames_and_avurls[follower_id]['avurl'],1))
			num_recent_followers += 1
		else:
			if not only_count_recent_followers:
				final_result.append((follower_id, following_time, follower_unames_and_avurls[follower_id]['uname'], \
					follower_unames_and_avurls[follower_id]['avurl'],0))

	################################################################
	if with_follower_count_since_last_seen:
		return final_result, num_recent_followers
	elif with_follower_count:
		return final_result, my_server.zcard(follower_key)
	else:
		return final_result


def retrieve_following_ids(user_id, start_idx, end_idx, with_follower_count=False):
	"""
	Returns list of IDs that a user is following, followingID_unames and followingID_avurls
	"""
	following_ids = UserFan.objects.filter(fan_id=user_id).values_list('star_id',flat=True).order_by('-fanning_time')
	count = len(following_ids)
	following_ids = following_ids[start_idx:end_idx+1]
	follower_unames_and_avurls = retrieve_bulk_credentials(following_ids)
	final_result = []
	for follower_id in following_ids:
		follower_id = int(follower_id)
		final_result.append([follower_id, follower_unames_and_avurls[follower_id]['uname'], \
			follower_unames_and_avurls[follower_id]['avurl']])
	if with_follower_count:
		return final_result, count
	else:
		return final_result


def get_following_count(user_id):
	"""
	Returns how many followers user_id has
	"""
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	count = my_server.get(FOLLOWING_COUNT+user_id)
	if not count:
		following_ids = UserFan.objects.filter(fan_id=user_id).values_list('star_id',flat=True).order_by('-fanning_time')
		count = len(following_ids)
		my_server.setex(FOLLOWING_COUNT+user_id,count,ONE_WEEK)
	return count


def invalidate_following_count(user_id):
	"""
	Deletes the cached 'following count' (star count) attributed to a given user_id
	"""
	redis.Redis(connection_pool=POOL).execute_command('UNLINK', FOLLOWING_COUNT+str(user_id))

	
LAST_ACTIVE_ON_HOME = 'laoh:'
NEW_FOLLOWERS_NOTIF = 'nfn:'
NO_NEW_FOLLOWERS = 'nnf:'


THREE_MONTHS = 60*60*24*90


def set_user_last_seen(user_id):
	"""
	"""
	redis.Redis(connection_pool=POOL).setex(LAST_ACTIVE_ON_HOME+str(user_id),time.time(),300)


def get_user_activity_event_time(user_id):
	"""
	When was the last time user was seen on 'custom home'

	Useful for deciding whether to show a 'new followers' notification to the said user
	"""
	my_server = redis.Redis(connection_pool=POOL)
	last_seen_time = my_server.get(LAST_ACTIVE_ON_HOME+str(user_id))
	if last_seen_time is None:
		# setting the time to 1 week ago for a brand new user (or resurrected user)
		one_week_ago = time.time()#-ONE_WEEK
		my_server.setex(LAST_ACTIVE_ON_HOME+str(user_id),one_week_ago,THREE_MONTHS)
		return one_week_ago
	else:
		return float(last_seen_time)


def update_user_activity_event_time(user_id):
	"""
	Recording the very moment a user viewed their custom home

	Useful for displaying a "new followers" message
	"""
	redis.Redis(connection_pool=POOL).setex(LAST_ACTIVE_ON_HOME+str(user_id),time.time(),THREE_MONTHS)
	delete_new_follower_notif(user_id)


def delete_new_follower_notif(user_id):
	"""
	Remove the new follower notif from redis
	"""
	redis.Redis(connection_pool=POOL).delete(NEW_FOLLOWERS_NOTIF+str(user_id))


def retrieve_cached_new_follower_notif(user_id):
	"""
	Retrieves the cached 'new follower' string for a particular user_id

	Useful when displaying a 'new followers' notification to the user on their home page
	"""
	return redis.Redis(connection_pool=POOL).get(NEW_FOLLOWERS_NOTIF+str(user_id))


def retrieve_and_cache_new_followers_notif(user_id):
	"""
	This retrieves 'new follower' data for a given user_id, caches it and returns the values for populating a notification on the user's home
	"""

	# Step 1) When was the last time user viewed their home? That determines the cut-off time for counting 'new followers'
	last_seen = get_user_activity_event_time(user_id)
	# Step 2) Retreive the data and count of new followers (since 'last_seen' time)
	followers, recent_followers_count = retrieve_follower_data(user_id=user_id, start_idx=0, end_idx=-1, with_follower_count_since_last_seen=last_seen)
	# Step 3) Cache and return the results
	if recent_followers_count:
		notif = str(recent_followers_count)+":"+str(last_seen)

		redis.Redis(connection_pool=POOL).setex(NEW_FOLLOWERS_NOTIF+str(user_id),notif,180)
		return recent_followers_count, last_seen
	else:
		redis.Redis(connection_pool=POOL).setex(NO_NEW_FOLLOWERS+str(user_id),'1',180)
		return None, None


#Start with implementing this
# how_many_users_im_a_follower_of = UserFan.objects.filter(fan_id=user_id).count()
# how_many_users_are_following_me = UserFan.objects.filter(star_id=user_id).count()

################################## Ratelimit user followers ##################################

def rate_limit_removed_follower(follower_id,star_id):
	"""
	Rate limit to ensure unfanned user doesn't refan the star immediately after
	"""
	redis.Redis(connection_pool=POOL).setex(RATE_LIMIT_FOLLOWER+str(follower_id)+":"+str(star_id),'1',RATELIMIT_REMOVED_FOLLOWER)

def rate_limit_unfollower(follower_id,star_id):
	"""
	Rate limit to ensure unfanned user doesn't refan the star immediately after
	"""
	redis.Redis(connection_pool=POOL).setex(RATE_LIMIT_FOLLOWER+str(follower_id)+":"+str(star_id),'1',SHORT_RATELIMIT_UNFOLLOWER)	


def is_potential_follower_rate_limited(follower_id, star_id,):
	"""
	Checking if allowed to fan the star, or is rate-limited due to a previous unfanning event
	"""
	return redis.Redis(connection_pool=POOL).exists('rlf:'+str(follower_id)+":"+str(star_id))

#################################################################################################

def set_temp_post_selected_followers(obj_hash_name,followers,expire_at):
	"""
	Temporarily save user_ids for a limited post, includes poster ID
	"""
	my_server = redis.Redis(connection_pool=POOL)
	my_server.sadd(TEMP_ALL_FOLLOWERS+obj_hash_name,*followers)
	my_server.expireat(TEMP_ALL_FOLLOWERS+obj_hash_name,int(expire_at))


def save_last_post_selected_followers(followers,poster_id):
	pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
	pipeline1.delete(LAST_SELECTED_FOLLOWERS+poster_id)
	pipeline1.sadd(LAST_SELECTED_FOLLOWERS+poster_id,*followers)
	pipeline1.expire(LAST_SELECTED_FOLLOWERS+poster_id,TWO_WEEKS)
	pipeline1.execute()	


def get_last_post_selected_followers(poster_id):
	"""
	"""
	return redis.Redis(connection_pool=POOL).smembers(LAST_SELECTED_FOLLOWERS+str(poster_id))	


def can_follower_view_post(user_id,obj_hash_name):
	"""
	Temporarily save user_ids for a limited post
	"""
	can_view_post = redis.Redis(connection_pool=POOL).sismember(TEMP_ALL_FOLLOWERS+obj_hash_name,user_id)
	if can_view_post:
		return can_view_post
	else:
		# try a DB look up in case permission list has expired
		permission_list = retrieve_permitted_ids(obj_hash_name)
		if permission_list:
			set_temp_post_selected_followers(obj_hash_name=obj_hash_name, followers=permission_list, expire_at=time.time()+ONE_DAY)
		return redis.Redis(connection_pool=POOL).sismember(TEMP_ALL_FOLLOWERS+obj_hash_name,user_id)
		
###################################### selective removal of posts #########################################


def remove_single_post_from_custom_feed(obj_hash, own_id):
	"""
	Used to remove a single post from own feed (for consumers)
	Also used to delete a post from OP's history 
	"""
	if obj_hash:
		own_id=str(own_id)
		link_data = obj_hash.partition(':')
		obj_id, obj_prefix = link_data[2], link_data[0]

		##############################
		# is own_id OP of the post?
		owner_id = get_obj_owner(obj_id,obj_prefix)
		if owner_id == '':
			is_op = Link.objects.filter(id=obj_id, submitter_id=own_id).exists()
		else:
			is_op = str(owner_id) == own_id

		############################################################
		if is_op:
			# remover is OP

			if Link.objects.only('audience').get(id=obj_id).audience == 'p':
				# only remove post from global feeds in redis7 if it's audience type was 'public' (i.e. 'p')
				removed, ttl = trim_expired_user_submissions(submitter_id=own_id, target_obj_hash_name=obj_hash)
			else:
				# for all other audience types, only remove post from user history and OP's feed
				removed, ttl = True, None

			if removed:
				Link.objects.filter(id=obj_id).update(delete_status='1')
				changed = change_delete_status_of_obj_hash(obj_hash_name=obj_hash)# called in redis7
				if changed:
					change_delete_status_of_direct_responses(obj_type='3' if obj_prefix == 'tx' else '4', obj_id=obj_id)# called in redis9
			
				my_server = redis.Redis(connection_pool=POOL)
				my_server.zrem(USER_FEED+own_id,obj_hash)# remove post from own feed
				my_server.zrem(SHORT_LIVED_CONTENT_EXPIRE_TIMES+own_id,obj_hash)# remove post from list of limited items

		############################################################
		else:
			# remover is not OP

			my_server = redis.Redis(connection_pool=POOL)
			my_server.zrem(USER_FEED+own_id,obj_hash)# remove post from own feed
			my_server.zrem(SHORT_LIVED_CONTENT_EXPIRE_TIMES+own_id,obj_hash)# remove post from list of limited items
			removed, ttl = True, None

		return removed, ttl, is_op
	
	else:
		return False, None, None


def sanitize_posts_after_pvp_ban(follower_id, user_id):
	"""
	Remove all posts of user_id from follower_id's custom feed
	
	Used in pvp banning (i.e. when one users bans another)
	"""
	fanout_list = []
	my_server = redis.Redis(connection_pool=POOL)
	if user_id:
		user_id = float(user_id)
		user_fanouts = my_server.zrangebyscore(FOLLOWER_FANOUTS_AND_SUBMITTERS,user_id,user_id)
		if user_fanouts:
			for fanout in user_fanouts:
				data = fanout.rpartition("*")# data = [follower_string, '*', obj_hash]
				fanout_list.append(data[2])
			follower_id = str(follower_id)
			if fanout_list:
				pipeline1 = my_server.pipeline()
				pipeline1.zrem(USER_FEED+follower_id,*fanout_list)
				pipeline1.zrem(SHORT_LIVED_CONTENT_EXPIRE_TIMES+follower_id,*fanout_list)
				pipeline1.execute()
		remove_permission_of_single_follower(poster_id=user_id,follower_id=follower_id,with_redis_cleansing=True)	


######################################### Postgresql helper funcs #########################################


def invalidate_permission_string(obj_hash_names):
	"""
	"""
	if obj_hash_names:
		final_keys_to_delete = []
		for obj_hash_name in obj_hash_names:
			final_keys_to_delete.append(TEMP_ALL_FOLLOWERS+obj_hash_name)
		if final_keys_to_delete:
			redis.Redis(connection_pool=POOL).execute_command('UNLINK', *final_keys_to_delete)


def retrieve_permitted_ids(obj_hash_name):
	"""
	Helps in recreating the 'permission string' of audience limited posts (useful in cases where the post lives 'forever')
	"""
	if obj_hash_name:
		data = obj_hash_name.partition(":")
		obj_type, obj_id = data[0], data[-1]
		if obj_type in ('tx','img'):
			# text or img type obj
			return Report.objects.filter(which_link_id=obj_id).values_list('target',flat=True)
		else:
			# obj type is unknown
			return []


def remove_permission_of_single_follower_on_specific_object(obj_hash_name, follower_id):
	"""
	Helps in removing a single follower's access permission on an object

	Useful when follower 'removes' object from feed	
	"""
	if obj_hash_name:
		data = obj_hash_name.partition(":")
		obj_type, obj_id = data[0], data[-1]
		if obj_type in ('tx','img'):
			Report.objects.filter(which_link_id=obj_id,target_id=follower_id).delete()
			invalidate_permission_string([obj_hash_name])# invalidate the currently existing permission string in redis
		else:
			pass

def remove_permission_of_single_follower(poster_id, follower_id, with_redis_cleansing=False):
	"""
	Revokes all permissions granted to a follower on any 'limited' object posted by the poster

	Useful in pvp banning
	"""
	if with_redis_cleansing:
		obj_hash_names = []
		objs = Report.objects.only('which_link','which_link__type_of_content').filter(reporter_id=poster_id, target_id=follower_id).\
		values('which_link_id','which_link__type_of_content')
		if objs:
			for obj in objs:

				if obj['which_link__type_of_content'] == 't':
					obj_hash_names.append("tx:"+str(obj['which_link_id']))
				elif obj['which_link__type_of_content'] == 'g':
					obj_hash_names.append("img:"+str(obj['which_link_id']))
			invalidate_permission_string(obj_hash_names)# removing redis 'permission strings' related to removed objs
			Report.objects.filter(reporter_id=poster_id, target_id=follower_id).delete()
		
	else:
		# solely get rid of DB perms
		Report.objects.filter(reporter_id=poster_id, target_id=follower_id).delete()


def remove_permission_of_bulk_followers(poster_id):
	"""
	Useful when a poster is banned "forever" etc
	"""
	Report.objects.filter(reporter_id=poster_id).delete()


######################################### Caching feed history in redis #########################################


def cache_user_feed_history(user_id, json_payload,page_num, hist_type):
	"""
	Caching user feed history pages (one page at a time)
	"""
	if hist_type == 'private':
		key_name = CACHED_PRIVATE_FEED_HISTORY+str(user_id)
	elif hist_type == 'limited':
		key_name = CACHED_LIMITED_FEED_HISTORY+str(user_id)
	elif hist_type == 'public':
		key_name = CACHED_PUBLIC_FEED_HISTORY+str(user_id)
	else:
		key_name = ''
	if key_name:
		my_server = redis.Redis(connection_pool=POOL)
		my_server.hset(key_name,page_num,json_payload)
		my_server.expire(key_name,TEN_MINS)


def retrieve_cached_user_feed_history(user_id, page_num, hist_type):
	"""
	Retrieve cached user feed history (in case of multiple quick visits occur in user history)
	"""
	if hist_type == 'private':
		key_name = CACHED_PRIVATE_FEED_HISTORY+str(user_id)
	elif hist_type == 'limited':
		key_name = CACHED_LIMITED_FEED_HISTORY+str(user_id)
	elif hist_type == 'public':
		key_name = CACHED_PUBLIC_FEED_HISTORY+str(user_id)
	else:
		key_name = ''
	if key_name:
		return redis.Redis(connection_pool=POOL).hget(key_name,str(page_num))


def invalidate_cached_user_feed_history(user_id, hist_type):
	"""
	Invalidate cached feed history (e.g. when poster submits new post)
	"""
	if hist_type == 'private':
		key_name = CACHED_PRIVATE_FEED_HISTORY+str(user_id)
	elif hist_type == 'limited':
		key_name = CACHED_LIMITED_FEED_HISTORY+str(user_id)
	elif hist_type == 'public':
		key_name = CACHED_PUBLIC_FEED_HISTORY+str(user_id)
	else:
		key_name = ''
	if key_name:
		redis.Redis(connection_pool=POOL).execute_command('UNLINK', key_name)


##################### Loggers for follow feature ####################
#####################################################################

POST_DATA_LOGGER = 'pdl'
POST_FOLLOW_LOGGER = 'pfl'

def logging_post_data(data):
	"""
	used to log post related data
	"""
	redis.Redis(connection_pool=POOL).zadd(POST_DATA_LOGGER,json.dumps(data),time.time())

def logging_follow_data(data):
	"""
	Check where the user pressed follow or unfollow button
	"""
	redis.Redis(connection_pool=POOL).zadd(POST_FOLLOW_LOGGER,json.dumps(data),time.time())


def log_remove_data():
	"""
	Log where exactly the user pressed the remove button, 
	Log what kind of post is removed
	Log which users are getting most removed and what kind of posts 
	"""
	pass

def avg_number_of_posts_to_get_followers():
	"""
	Log number of posts per user and also log how many posts per user 
	Can we measure where users are getting most followers
	"""
	pass

def log_users_and_number_of_followers():
	"""
	Log number of posts per user and also log how many posts per user 
	Can we measure where users are getting most followers
	"""
	pass



#####################################################################################################################################################################
#####################################################################################################################################################################
#####################################################################################################################################################################
#####################################################################################################################################################################
#####################################################################################################################################################################


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
	objs_to_show = my_server.zrevrange(direct_response_key,start_idx,end_idx)# produces list of 'drobj' hash names

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
					visit_data['wu'], visit_data['label'], visit_data['ds'], visit_data['et'] = data['submitter_uname'], data['description'], \
					data['delete_status'], data['expire_at']
					final_data.append(visit_data)
				else:
					# this data does not exist
					deleted_visit_locs.append(visit)
					deleted_interactions.append(post_interactions_key)

			elif obj_type == '4':
				data = parent_img_data.get(parent_obj_id,{})
				if data:
					# this data exists
					visit_data['wu'], visit_data['label'], visit_data['iu'], visit_data['ds'], visit_data['et'] = data['submitter_uname'], \
					data['description'], data['image_file'],data['delete_status'], data['expire_at']
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


def change_delete_status_of_direct_responses(obj_type, obj_id):
	"""
	Change 'delete_status' of all related drobjs to '1'

	This specifically enables all affected inboxes to show 'removed' upon rendering
	"""
	my_server = redis.Redis(connection_pool=POOL)
	list_of_responses = my_server.zrange(DIRECT_RESPONSE_PARENT+obj_type+":"+str(obj_id),0,-1)
	if list_of_responses:
		# proceed with deletion
		json_obj_hash_data = my_server.mget(*list_of_responses)
		counter = 0

		for json_obj_hash_datum in json_obj_hash_data:
			obj_hash_name = list_of_responses[counter]
			if json_obj_hash_datum:
				obj_ttl = my_server.ttl(obj_hash_name)
				obj = json.loads(json_obj_hash_datum)
				obj['ds'] = '1'
				my_server.setex(obj_hash_name, json.dumps(obj), obj_ttl)
			counter += 1


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
				my_server.zincrby(DIRECT_RESPONSE_METRICS,'pub_mef_rep_to_rep',amount=1)
			my_server.zincrby(DIRECT_RESPONSE_METRICS,'pub_mef_total_reps',amount=1)
		elif obj_type == '6':
			# this is a private mehfil
			if action_status:
				my_server.zincrby(DIRECT_RESPONSE_METRICS,'prv_mef_rep_to_rep',amount=1)
			my_server.zincrby(DIRECT_RESPONSE_METRICS,'prv_mef_total_reps',amount=1)
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


FLOOD_COUNTER = 'fcn:'# counts how many times a given user has flooded in the recent seconds
RATE_LIMIT_KEY = 'rk:'# rate limit key set for users who are flooding numerous times in a short time window
LONG_TERM_RATE_LIMIT_KEY = 'ltrk:'# freqent rate-limiters are rate limited for ever increasing times via this key
REPLY_RATE = 'rt:'# temp key that holds recent replies to determine speed of replying (useful for imposing rate limits for flooders)


def log_rate_of_reply(replier_id, text_len, time_now):
	"""
	Anti-flood logger

	Used to determine whether a user is flooding
	"""
	reply_rate_key = REPLY_RATE+str(replier_id)
	my_server = redis.Redis(connection_pool=POOL)
	my_server.lpush(reply_rate_key,str(text_len)+":"+str(time_now))
	my_server.expire(reply_rate_key,15)#expire the data after 15 secs of inactivity


def retrieve_prev_replier_rate(replier_id):
	"""
	Retrieves the rate of last 3 replies (if key hasn't expired yet)
	"""
	return redis.Redis(connection_pool=POOL).lrange(REPLY_RATE+str(replier_id),0,2)


def impose_reply_rate_limit(replier_id):
	"""
	Impose rate limit on 'flooders' (if warranted)
	"""
	replier_id = str(replier_id)
	flood_key_name = FLOOD_COUNTER+replier_id

	my_server = redis.Redis(connection_pool=POOL)
	new_value = my_server.incr(flood_key_name)
	
	# caught flooding thrice - rate-limit them!
	if new_value >= 3:
		rate_limit_key = RATE_LIMIT_KEY+replier_id
		long_term_rate_limit_key = LONG_TERM_RATE_LIMIT_KEY+replier_id
		
		# Step 1: determine how long to rate limit the replier, given how many times they've been rate limited previously
		num_times_recently_limited = my_server.get(long_term_rate_limit_key)
		limit_length = 900*(int(num_times_recently_limited)+2) if num_times_recently_limited is not None else 900
		
		# Step 2: 
		pipeline1 = my_server.pipeline()
		pipeline1.incr(rate_limit_key)
		pipeline1.expire(rate_limit_key,limit_length)# rate limited for multiples of 15 mins
		pipeline1.incr(long_term_rate_limit_key)
		pipeline1.expire(long_term_rate_limit_key,864000)# long term key's expiry is set for 10 days
		pipeline1.execute()
		
		return True, limit_length
	
	# don't ban
	else:
		my_server.expire(flood_key_name,26)
		return False, None


def is_rate_limited(replier_id):
	"""
	Checks if user is rate-limited
	"""
	time_remaining = redis.Redis(connection_pool=POOL).ttl(RATE_LIMIT_KEY+str(replier_id))
	if time_remaining > 1:
		return True, time_remaining
	else:
		return False, None	