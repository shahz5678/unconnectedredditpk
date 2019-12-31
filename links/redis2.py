import threading
import redis, time
import ujson as json
from location import REDLOC2
from redis4 import retrieve_bulk_credentials
from models import UserFan, Report, Link, Cooldown
from utilities import beautiful_date, convert_to_epoch
from redis7 import get_obj_owner, change_delete_status_of_obj_hash, trim_expired_user_submissions
from score import PUBLIC_SUBMISSION_TTL, TTL_FOLLOWER_LIST, TTL_FOLLOWER_STRING, RATELIMIT_REMOVED_FOLLOWER, SHORT_RATELIMIT_UNFOLLOWER
from redis9 import change_delete_status_of_direct_responses

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC2, db=0)

TEN_MINS = 600# 10 minutes in seconds
ONE_DAY = 86400# 1 day in seconds
ONE_WEEK = 604800# 1 week in seconds
TWO_WEEKS = 172800# 2 weeks in seconds
THREE_MONTHS = 60*60*24*90

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

LAST_ACTIVE_ON_HOME = 'laoh:'
NEW_FOLLOWERS_NOTIF = 'nfn:'
NO_NEW_FOLLOWERS = 'nnf:'

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
		invalidate_user_last_seen(target_user_id)



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
			invalidate_user_last_seen(target_user_id)
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


def trim_expired_fanouts(submitter_id=None, time_now=None):
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
		expired_fanouts = my_server.zrangebyscore(FOLLOWER_FANOUTS_AND_EXPIRES,'-inf',time_now)
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

######################################### new follower notif ###########################################

def set_user_last_seen(user_id,time_now):
	"""
	"""
	if redis.Redis(connection_pool=POOL).exists(LAST_ACTIVE_ON_HOME+str(user_id)):
		pass
	else:	
		redis.Redis(connection_pool=POOL).setex(LAST_ACTIVE_ON_HOME+str(user_id),time.time(),THREE_MONTHS)


def invalidate_user_last_seen(user_id):
	"""
	"""
	redis.Redis(connection_pool=POOL).execute_command('UNLINK',LAST_ACTIVE_ON_HOME+str(user_id))


def get_user_activity_event_time(user_id):
	"""
	When was the last time user was seen on 'custom home'

	Useful for deciding whether to show a 'new followers' notification to the said user
	"""
	my_server = redis.Redis(connection_pool=POOL)
	last_seen_time = my_server.get(LAST_ACTIVE_ON_HOME+str(user_id))
	if last_seen_time:
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
	if last_seen:
		followers, recent_followers_count = retrieve_follower_data(user_id=user_id, start_idx=0, end_idx=-1, with_follower_count_since_last_seen=last_seen)
		
		# Step 3) Cache and return the results
		if recent_followers_count:
			notif = str(recent_followers_count)+":"+str(last_seen)

			redis.Redis(connection_pool=POOL).setex(NEW_FOLLOWERS_NOTIF+str(user_id),notif,180)
			return recent_followers_count, last_seen
		else:
		# redis.Redis(connection_pool=POOL).setex(NO_NEW_FOLLOWERS+str(user_id),'1',180)
			return None, None	
	else:
		# redis.Redis(connection_pool=POOL).setex(NO_NEW_FOLLOWERS+str(user_id),'1',180)
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
				# in case the object trended and was part of the sitemap, remove it from the sitemap model
				if Cooldown.objects.filter(content_id=obj_id).exists():
					Cooldown.objects.filter(content_id=obj_id).delete()
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
POST_REMOVE_LOGGER = 'prl'

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


def log_remove_data(data):
	"""
	Log where exactly the user pressed the remove button, 
	Log what kind of post is removed
	"""
	redis.Redis(connection_pool=POOL).zadd(POST_REMOVE_LOGGER,json.dumps(data),time.time())