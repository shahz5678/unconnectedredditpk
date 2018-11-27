import redis
import ujson as json
from location import REDLOC6

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC6, db=0)

####################################### TIME CONSTANTS #######################################

FIVE_MINS = 60*5

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