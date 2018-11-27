import redis
import ujson as json
from location import REDLOC6

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC6, db=0)

####################################### TIME CONSTANTS #######################################

FIVE_MINS = 60*5
TWO_WEEKS = 60*60*24*7*2

######################### Caching mehfil popularity data #########################

CACHED_RANKED_GROUPS = 'crg'# key holding cached json object used to populate popular groups page with a list of top 20 public mehfils

######################## Caching mehfil messaging data ########################

MEHFIL_CACHED_PAGES = 'mcp:'#contains json serialized data of a user's paginated mehfil list

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

