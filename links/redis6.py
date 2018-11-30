import redis
import ujson as json
from location import REDLOC6
from score import MAX_TIME_BETWEEN_TOPIC_CHANGE_ATTEMPTS, NUM_TOPIC_CHANGE_ATTEMPTS_ALLOWED, EXCESSIVE_ATTEMPTS_TO_CHANGE_TOPIC_RATE_LIMIT,\
TOPIC_SHORT_RATE_LIMIT, TOPIC_LONG_RATE_LIMIT, RULES_CHANGE_RATE_LIMIT, MAX_TIME_BETWEEN_RULE_CHANGE_ATTEMPTS, NUM_RULES_CHANGE_ATTEMPTS_ALLOWED,\
EXCESSIVE_ATTEMPTS_TO_CHANGE_RULES_RATE_LIMIT


POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC6, db=0)

####################################### TIME CONSTANTS #######################################

FIVE_MINS = 60*5
FORTY_MINS = 60*40
ONE_WEEK = 7*24*60*60
TWO_WEEKS = 60*60*24*7*2

######################### Caching mehfil popularity data #########################

CACHED_RANKED_GROUPS = 'crg'# key holding cached json object used to populate popular groups page with a list of top 20 public mehfils

######################## Caching mehfil messaging data ########################

MEHFIL_CACHED_PAGES = 'mcp:'#contains json serialized data of a user's paginated mehfil list

############# Freezing certain functionality of reported mehfils ################

GROUP_TOPIC_CHANGE_FROZEN = 'gtcf:' #key locking the topic change functionality of a public mehfil

############# Freezing certain functionality of reported mehfils ################

GROUP_RULES_CHANGE_FROZEN = 'grcf:' #key locking the rules functionality of a public mehfil

######################## Group creation helper functions ########################

PRIVATE_GROUP_CREATION_RATE_LIMIT_KEY = 'prgcrlk:'#key that rate limits creation of further public groups
PUBLIC_GROUP_CREATION_RATE_LIMIT_KEY = 'pgcrlk:'#key that rate limits creation of further public groups
TEMPORARY_GROUP_CREDENTIALS_STORE = "tgcs:"#temporarily stores group credentials (used when showing user a 'preview')

######################## Rate limiting mehfil topic and rules changes ########################

TOPIC_CHANGE_ATTEMPT = "tca:"#key keeping track of how many mehfil topic changes were attempted by a certain user
USER_ATTEMPT_RATE_LIMITED = 'url:'#key that rate limits topic changes in mehfils
TOPIC_CHANGE_RATE_LIMITED = 'trl:'#key that rate limits topic changes in mehfils
RULES_CHANGE_ATTEMPT = "rca:"#key keeping track of how many mehfil topic changes were attempted by a certain user
RULES_CHANGE_RATE_LIMITED = 'rcrl:'#key that rate limits topic changes in mehfils

############################# Handling officer appointments ############################

GROUP_OFFICER_HASH = 'oh:'#hash containing privilege details of group officer, history of last 10 actions, etc.

######################################### Utilities #########################################

def human_readable_time(future_time_in_seconds):
	try:
		m, s = divmod(future_time_in_seconds, 60)
		h, m = divmod(m, 60)
		d, h = divmod(h, 24)
		mo, d = divmod(d, 30)
		if mo:
			mo = int(mo)
			if mo == 1:
				return "1 month"
			else:
				return "%s months" % mo
		elif d:
			d = int(d)
			if d == 1:
				return "1 day"
			else:
				return "%s days" % d
		elif h:
			h = int(h)
			if h == 1:
				return "1 hour"
			else:
				return "%s hours" % h
		elif m:
			m = int(m)
			if m == 1:
				return "1 min"
			else:
				return "%s mins" % m
		elif s:
			s = int(s)
			if s == 1:
				return "1 sec"
			else:
				return "%s secs" % s
		else:
			return "kuch waqt"
	except (NameError,TypeError):
		return "kuch waqt"

########################### Group creation helper functions ###########################


def rate_limit_group_creation(user_id, which_group):
	"""
	Rate limits creation of public groups
	"""
	if which_group == 'public':
		redis.Redis(connection_pool=POOL).setex(PUBLIC_GROUP_CREATION_RATE_LIMIT_KEY+str(user_id),'1',ONE_WEEK)
	elif which_group == 'private':
		redis.Redis(connection_pool=POOL).setex(PRIVATE_GROUP_CREATION_RATE_LIMIT_KEY+str(user_id),'1',FORTY_MINS)
	else:
		pass


def is_group_creation_rate_limited(user_id, which_group):
	"""
	Checking whether public mehfil creation is rate limited
	"""
	if which_group == 'public':
		ttl = redis.Redis(connection_pool=POOL).ttl(PUBLIC_GROUP_CREATION_RATE_LIMIT_KEY+str(user_id))
	elif which_group == 'private':
		ttl = redis.Redis(connection_pool=POOL).ttl(PRIVATE_GROUP_CREATION_RATE_LIMIT_KEY+str(user_id))
	else:
		ttl = 0
	if ttl > 3:
		return ttl
	else:
		return None

def temporarily_save_group_credentials(user_id, topic, rules, formatted_rules, category, group_id=None):
	"""
	Temporary storage for mehfil credentials

	Useful for showing user preview of mehfil credentials (before finalization of creation)
	"""
	key = TEMPORARY_GROUP_CREDENTIALS_STORE+str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	mapping = {'topic':topic,'rules':rules,'formatted_rules':formatted_rules,'category':category}
	if group_id:
		mapping['gid'] = group_id
	my_server.hmset(key,mapping)
	my_server.expire(key,FORTY_MINS)


def get_temporarily_saved_group_credentials(user_id,only_raw=False):
	"""
	Retrieve temporarily saved mehfil credentials
	"""
	data = redis.Redis(connection_pool=POOL).hgetall(TEMPORARY_GROUP_CREDENTIALS_STORE+str(user_id))
	if data:
		if only_raw:
			# do not return formatted_rules
			data['topic'] = data['topic'].decode('utf-8')
			data['rules'] = data['rules'].decode('utf-8')
			data.pop('formatted_rules', None)
			return data
		else:
			data['topic'] = data['topic'].decode('utf-8')
			data['rules'] = data['rules'].decode('utf-8')
			data['formatted_rules'] = data['formatted_rules'].decode('utf-8')
			return data
	else:
		return None

###################################### Freeze group functionality #####################################

def is_topic_change_frozen(group_id):
	"""
	Retrieve whether group topic change is frozen
	"""
	if redis.Redis(connection_pool=POOL).exists(GROUP_TOPIC_CHANGE_FROZEN+str(group_id)):
		return True
	else:
		return False

def is_rules_change_frozen(group_id):
	"""
	Retrieve whether group ownership transfer is frozen
	"""
	if redis.Redis(connection_pool=POOL).exists(GROUP_RULES_CHANGE_FROZEN+str(group_id)):
		return True
	else:
		return False

###################################### Calculating group active users and ranking #######################################

def cache_ranked_groups(json_data):
	"""
	Caches data displayed in popular groups page
	"""
	redis.Redis(connection_pool=POOL).setex(CACHED_RANKED_GROUPS,json_data,FIVE_MINS)


def retrieve_cached_ranked_groups():
	"""
	Fetches cached ranked groups to be displayed on popular groups page
	"""
	return redis.Redis(connection_pool=POOL).get(CACHED_RANKED_GROUPS)

############################# Handling officer appointments ############################

def can_officer_change_topic(group_id, officer_id):
	"""
	Retrieves whether an officer can change group topic

	Useful when processing group topic changes
	"""
	if redis.Redis(connection_pool=POOL).hget(GROUP_OFFICER_HASH+str(group_id)+":"+str(officer_id),'can_topic') == '1':
		return True
	else:
		return False 

######################## Caching mehfil messaging data ########################

def cache_mehfil_pages(paginated_data,user_id):
	"""
	Micro-caches data shown in a user's mehfil list

	'paginated_data' is a dictionary containing all the page(s) data
	"""
	if paginated_data:
		user_id = str(user_id)
		final_data = {}
		for page_num, page_data in paginated_data.items():
			final_data[page_num] = json.dumps(page_data)
		final_data['tp'] = len(paginated_data)
		key, my_server = MEHFIL_CACHED_PAGES+user_id, redis.Redis(connection_pool=POOL)
		my_server.hmset(key,final_data)
		my_server.expire(key,27)


def retrieve_cached_mehfil_pages(user_id,page_num):
	"""
	Retrieving cached mehfil page data for a certain user
	"""
	page_data, num_pages = redis.Redis(connection_pool=POOL).hmget(MEHFIL_CACHED_PAGES+str(user_id),str(page_num),'tp')
	num_pages = int(num_pages) if num_pages else 0
	return page_data, num_pages


def invalidate_cached_mehfil_pages(user_id):
	"""
	Invalidating cached mehfil list
	"""
	redis.Redis(connection_pool=POOL).delete(MEHFIL_CACHED_PAGES+str(user_id))


######################## Rate limiting mehfil topic and rules changes ########################

def retrieve_topic_and_rules_ttl(group_owner_id,group_uuid, is_public):
	"""
	Returns respective rate limits

	Useful when transferring ownership of mehfils - ensures the user doesn't change topic/rules and immediately transfers ownership to someone else (that can be potentially abusive)
	"""
	group_uuid = str(group_uuid)
	my_server =    redis.Redis(connection_pool=POOL)
	# checking for rate limit on topic changes
	topic_ttl = my_server.ttl(TOPIC_CHANGE_RATE_LIMITED+group_uuid)
	# checking for specific rate limit on rule changes
	rules_ttl = my_server.ttl(RULES_CHANGE_RATE_LIMITED+str(group_owner_id)+":"+group_uuid) if is_public else None
	return topic_ttl, rules_ttl


def invalidate_topic_changing_lock(group_uuid):
	"""
	Invalidates topic changing lock for cases when a group ownership is transferred
	"""
	redis.Redis(connection_pool=POOL).delete(TOPIC_CHANGE_RATE_LIMITED+str(group_uuid))


def log_topic_change(user_id,unique_id,how_long='short'):
	"""
	Rate limit further topic changes if mehfil topic successfully changed (only for this particular mehfil)

	Half an hour if private mehfil
	One day if public mehfil
	"""
	if user_id and unique_id:
		redis.Redis(connection_pool=POOL).setex(TOPIC_CHANGE_RATE_LIMITED+str(unique_id),'1',TOPIC_SHORT_RATE_LIMIT if how_long == 'short' else TOPIC_LONG_RATE_LIMIT)


def log_topic_changing_attempt(user_id):
	"""
	Rate limit user's attempts if user has attempted more than NUM_TOPIC_CHANGE_ATTEMPTS_ALLOWED times within a given time window

	Applies to all topic changing activity of the user - regardless of whether she tries it over various differnet mehfils
	"""
	if user_id:
		user_id = str(user_id)
		key = TOPIC_CHANGE_ATTEMPT+user_id
		my_server = redis.Redis(connection_pool=POOL)
		num_attempts = my_server.incr(key)
		my_server.expire(key,MAX_TIME_BETWEEN_TOPIC_CHANGE_ATTEMPTS)#5 mins
		if num_attempts >= NUM_TOPIC_CHANGE_ATTEMPTS_ALLOWED:
			# rate limit this person if num_attempts >= 3:
			rate_limit_key = USER_ATTEMPT_RATE_LIMITED+user_id
			if my_server.exists(rate_limit_key):
				# if already rate limited, don't interfere with that rate limit
				pass
			else:
				# rate limit the person for 20 mins after excessive attempts
				my_server.setex(rate_limit_key,'1',EXCESSIVE_ATTEMPTS_TO_CHANGE_TOPIC_RATE_LIMIT)
	else:
		pass


def topic_change_rate_limited(user_id,unique_id):
	"""
	Return ttl if topic changing in mehfils is rate limited for a user
	"""
	if user_id and unique_id:
		user_id, unique_id = str(user_id), str(unique_id)
		my_server = redis.Redis(connection_pool=POOL)
		# general rate limit applies to all mehfil topic change attempts, regardless of which mehfil it is (applied after too many topic change attempts)
		general_rate_limit = my_server.ttl(USER_ATTEMPT_RATE_LIMITED+user_id)
		if general_rate_limit > 4:
			return general_rate_limit
		else:
			# specific rate limit only rate limits user from changing a particular mehfil's topic (applied after 1 successful topic change)
			specific_rate_limit = my_server.ttl(TOPIC_CHANGE_RATE_LIMITED+unique_id)
			if specific_rate_limit > 4:
				return specific_rate_limit
			else:
				return 0
	else:
		return None


def log_rules_change(user_id,unique_id):
	"""
	Rate limit further rules changes if mehfil rules successfully changed (only for this particular mehfil)

	This is a specific rate limit only rate limits user from changing this mehfil's rules (applied after 1 successful rule change)
	"""
	if user_id and unique_id:
		redis.Redis(connection_pool=POOL).setex(RULES_CHANGE_RATE_LIMITED+str(user_id)+":"+str(unique_id),'1',RULES_CHANGE_RATE_LIMIT)


def log_rules_changing_attempt(user_id):
	"""
	Rate limit user's attempts if user has attempted more than NUM_RULES_CHANGE_ATTEMPTS_ALLOWED times within a given time window

	Applies to all rules changing activity of the user - regardless of whether she tries it over various differnet mehfils
	"""
	if user_id:
		user_id = str(user_id)
		key = RULES_CHANGE_ATTEMPT+user_id
		my_server = redis.Redis(connection_pool=POOL)
		num_attempts = my_server.incr(key)
		my_server.expire(key,MAX_TIME_BETWEEN_RULE_CHANGE_ATTEMPTS)#5 mins
		if num_attempts >= NUM_RULES_CHANGE_ATTEMPTS_ALLOWED:
			# rate limit this person if num_attempts >= 4:
			rate_limit_key = RULES_CHANGE_RATE_LIMITED+user_id
			if my_server.exists(rate_limit_key):
				# if already rate limited, don't interfere with that rate limit
				pass
			else:
				# rate limit the person for 20 mins after excessive attempts
				my_server.setex(rate_limit_key,'1',EXCESSIVE_ATTEMPTS_TO_CHANGE_RULES_RATE_LIMIT)
	else:
		pass


def rules_change_rate_limited(user_id,unique_id):
	"""
	Return ttl if rules changing in mehfils is rate limited for a user
	"""
	if user_id and unique_id:
		user_id, unique_id = str(user_id), str(unique_id)
		my_server = redis.Redis(connection_pool=POOL)
		# general rate limit applies to all mehfil rule change attempts, regardless of which mehfil it is (applied after too many rule change attempts)
		general_rate_limit = my_server.ttl(RULES_CHANGE_RATE_LIMITED+user_id)
		if general_rate_limit > 4:
			return general_rate_limit
		else:
			# specific rate limit only rate limits user from changing a particular mehfil's rules (applied after 1 successful rule change)
			specific_rate_limit = my_server.ttl(RULES_CHANGE_RATE_LIMITED+user_id+":"+unique_id)
			if specific_rate_limit > 4:
				return specific_rate_limit
			else:
				return 0
	else:
		return None

###################################################
###################################################
BENCHMARK_ID = 1686999

def get_bucket_type(user_id):
	"""
	'NA': New user bucket, with new group view.
	'NC': New user bucket, control group.
	'OA': Old user bucket, with new group view.
	'OC': Old user bucket, control group.
	"""
	if user_id > BENCHMARK_ID:
		# user is either N1 or NC
		if user_id % 2 == 0:
			# even
			bucket_type='NA'
		else:
			# odd
			bucket_type='NC'
	else:
		# user is either O1 or OC
		if user_id % 2 == 0:
			# even
			bucket_type='OA'
		else:
			# odd
			bucket_type = 'OC'
	return bucket_type

def allot_bucket_to_user(user_id):
	bucket = get_bucket_type(user_id)
	redis.Redis(connection_pool = POOL).sadd(bucket,user_id)
	return bucket
		
def log_mehfil_data(user_id,group_id):
	bucket = get_bucket_type(user_id)	
	my_server = redis.Redis(connection_pool = POOL)
	if my_server.sismember(bucket,user_id):
		my_server.zincrby(bucket+"_ms",user_id,amount=1)

		id_pair = str(user_id)+":"+str(group_id)
		key = bucket+"_ia:"+id_pair
		if not my_server.exists(key):
			my_server.zincrby(bucket+"_ia",user_id,amount=1)
			my_server.setex(key,'1',TWO_WEEKS)

###################################################
###################################################
