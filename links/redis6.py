import redis
from location import REDLOC6

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC6, db=0)

####################################### TIME CONSTANTS #######################################

FIVE_MINS = 60*5


######################### Caching mehfil popularity data #########################

CACHED_RANKED_GROUPS = 'crg'# key holding cached json object used to populate popular groups page with a list of top 20 public mehfils


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