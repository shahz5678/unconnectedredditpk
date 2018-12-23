"""
TODO:
1) Mehfils' invitations and membership have many legacy functions still being used in Redis 1. Look at the imports from redis1 in mehfil_views.py and in this file
2) These redis1 functions need to be deprecated - all functionality mehfils need should be routed via redis 6
3) Also delete legacy data from redis 1. Keys include:
	i) pgm:<group_id>, a set containing all usernames of members of a particular group 
	ii) lgr:<group_id>, a key containing the ID of the latest reply submitted in a group (useful in populating GroupPageView())
	iii) ipg:<user_id>, a sorted set containing IDs of all groups the user has been invited to (capped at 500 invites). This prevents reinvitation. Use GROUP_INVITE_LOCK in redis6 to replace this.
	iv) ug:<user_id> - a set containing all group ids a given <user_id> is a member of
	v) giu:<group_id><user_id> - a hash containing information about an invite to a group received by a user
	vi) pir:<user_id> - a set containing IDs of all 'active' invites currently outstanding for a given user
4) Likewise, remove all REQUESTOR_ID parameters from functions containing 'retrieve' in their names in this file
5) Group, Reply, GroupBanList, GroupTraffic and GroupCaptain data models also need to be deprecated entirely
6) UNIVERSAL_GROUP_ATTENDANCE_LIST sorted set contains list of active mehfils. All other mehfils are dead - remove their notification objects from redis 2
"""
import ujson as json
import redis, time, random
from datetime import datetime
from collections import defaultdict
from templatetags.s3 import get_s3_object
from score import GROUP_SOFT_DELETION_CUTOFF, GROUP_IDLE_DOT_CUTOFF, MSGS_TO_SHOW_IN_GROUP,NUM_TO_DELETE, MAX_OWNER_INVITES_PER_PUBLIC_GROUP,\
MAX_OFFICER_INVITES_PER_PUBLIC_GROUP, CANCEL_INVITE_AFTER_TIME_PASSAGE, GROUP_HARD_DELETION_CUTOFF, GROUP_GREEN_DOT_CUTOFF, MICRO_CACHE_TTL,\
MAX_MEMBER_INVITES_PER_PRIVATE_GROUP, MAX_OWNER_INVITES_PER_PRIVATE_GROUP, PRIVATE_GROUP_MAX_MEMBERSHIP, INVITE_LOCK_DURATION, EXIT_DISCOUNT,\
KICK_DISCOUNT, GROUP_SIZE_PERCENTILE_CUTOFF, MAX_OFFICER_APPOINTMENTS_ALLWD, NUM_PUBLIC_GROUPS_OWNED_SHOWN_ON_PROFILE, OFFICER_APPLICATION_EXPIRY_TIME,\
OFFICER_APPLICATIONS_RATE_LIMIT, OFFICER_APP_ARCHIVE_EXPIRY_TIME, MAX_ARCHIVED_OFFICER_APPS_PER_GROUP, GROUP_TRANSACTION_RATE_LIMIT,FOLLOW_UP_REQUEST_RATE_LIMIT,\
PUBLIC_GROUP_EXIT_LOCK, PRIVATE_GROUP_EXIT_LOCK, GROUP_REENTRY_LOCK, EXCESSIVE_ATTEMPTS_TO_CHANGE_TOPIC_RATE_LIMIT, MAX_TIME_BETWEEN_TOPIC_CHANGE_ATTEMPTS,\
RULES_CHANGE_RATE_LIMIT, MAX_TIME_BETWEEN_RULE_CHANGE_ATTEMPTS, EXCESSIVE_ATTEMPTS_TO_CHANGE_RULES_RATE_LIMIT, TOPIC_LONG_RATE_LIMIT, TOPIC_SHORT_RATE_LIMIT,\
NUM_RULES_CHANGE_ATTEMPTS_ALLOWED, NUM_TOPIC_CHANGE_ATTEMPTS_ALLOWED, FEEDBACK_TTL, FEEDBACK_RATELIMIT, FEEDBACK_CACHE
from redis4 import retrieve_bulk_unames, retrieve_uname, retrieve_bulk_credentials, retrieve_credentials
from redis1 import remove_group_invite, legacy_mehfil_exit
from redis3 import exact_date
from location import REDLOC6
from models import Group

# changed connection from TCP port to UNIX socket
POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC6, db=0)

####################################### TIME CONSTANTS #######################################

TEN_MINS = 60*10
FIFTEEN_MINS = 60*15
FORTY_MINS = 60*40
THREE_HOURS = 60*60*3
FIFTEEN_HOURS = 60*60*15
ONE_DAY = 60*60*24
THREE_DAYS = 60*60*24*3
FOUR_DAYS = 60*60*24*4
ONE_WEEK = 60*60*24*7
TWO_WEEKS = 60*60*24*7*2
ONE_MONTH = 60*60*24*30
ONE_AND_A_HALF_MONTHS = 60*60*24*45

############################## Group creation and content submission ##############################

GROUPS_OWNED_BY_USER = 'uog:' # sorted set containing group_ids user has created
CACHED_USER_OWNERSHIP_PUBLIC_GROUPS = 'cuowg:'# key holding cached ownership data related to a particular user
GROUP_LIST = "group_list"#sorted set containing all groups created along with creation times
GROUP_SIZE_LIST = "group_size_list"#sorted set containing public groups sorted by the number of their members
SUBMISSION_COUNTER = "sc:"#key that creates reply id for a given reply to be saved for a given group
GROUP_SUBMISSION_HASH = "gh:"#hash containing relevant data regarding a reply in a group
GROUP_SUBMISSION_LIST = "gl:"#sorted set containing all the latest replies submitted into a group
GROUP = "g:"#hash containing group details
GROUP_USER_AGE_LIST = "gual:"#sorted set containing joining dates of all members of a group (in epoch time)
GROUP_UUID_TO_ID_MAPPING = "gui:"#a key that contains a mapping between group's UUID and ID, useful in cases where group is called via uuid
RECENTLY_DELETED_GROUP = 'dg:'#key set to linger deleted group's identity in the system
GROUP_PIC_COUNT = 'gcn:'#sorted set containing counts of pics sent by each member of the private mehfil
GROUP_TOPIC_COUNTER = 'gtc:'# creates topic ids used in logging old topics in private mehfils
GROUP_TOPIC_HASH = 'gth:'#hash containing details about a set group topic
GROUP_TOPIC_LIST = 'gtl:'#sorted set containing last 10 topics set in a private mehfil
CACHED_GROUP_TOPIC_LIST = 'cgtl:'#key containg cached mehfil topic list (for private mehfils)
GROUP_CHATTER = 'gc:'# sorted set containing chatter generated by private mehfil users
CACHED_GROUP_CHATTER = 'cgc:'#key containing cached chatter data for a private mehfil

############################# Handling officer appointments ############################

GROUPS_IN_WHICH_USER_IS_OFFICER = 'uofg:' # sorted set containing group_ids user is an officer in currently
GROUP_OFFICER_LIST = 'mo:'#sorted set containing group/mehfil officer appointments and time of captaining
GROUP_OFFICER_HASH = 'oh:'#hash containing privilege details of group officer, history of last 10 actions, etc.
RATE_LIMIT_OWNER_APPOINTMENTS = 'rloa:'#ratelimit key that cools off group owner from creating more officers

OFFICER_APPLICATIONS_RATE_LIMITED = 'oarl:'# key that rate limits how fast a user can drop applications to become an officer
RATE_LIMIT_APPLIER_FROM_APPLYING_AGAIN = 'oatgrl:'# key that rate limits a user from applying as an officer to a specific group
OFFICER_APPLICATION_COUNTER = 'oc'# key incrementing which produces a counter for officer applications dropped by a user
OFFICER_APPLICATION_DETAIL = 'oad:'# hash that holds the detail of an officer application submitted by a user to a group's owner
OFFICER_APPLICATIONS_SUBMITTED = 'oas:'# sorted set holding all the recent officer applications submitted by a user
CACHED_USER_OFFICER_APPLICATIONS = 'cuoa:'# key holding cached officer applications submitted by a user
OFFICER_APPLICATIONS_RECEIVED = 'oar:'# sorted set holding all the officer applications received by a public group
CACHED_GROUP_OFFICER_APPLICATIONS = 'cgoa:'# key holding cached officer applications received by a group

OFFICER_STATISTICS = 'os:'# hash key that contains statistics of a user's officer applications; this key has no TTL

############################# Tracking mehfil visitors ############################

UNIVERSAL_GROUP_ATTENDANCE_LIST = 'group_attendance'#sorted set containing last touch times of all groups (public and private)
GROUP_VISITORS = "gv:"# set containing visitors of a public or private mehfil
GROUP_ATTENDANCE_CACHE = "gac:"# key containing cached attendance data for a group
GROUP_SHORT_TERM_ATTENDANCE_CACHE = "gsac:"# key containing cached short term attendance data for a group (i.e. last 15 mins)
GROUP_PRESENCE_CACHE = 'gpc:'# key containing cached status data for a group (i.e. whether a user is online, idle or gone)
GROUP_EXIT_TRACKER = 'ge:'# sorted set containing exited members from last 45 days
GROUP_KICK_TRACKER = 'gk:'# sorted set containing kicked members from last 45 days
GROUP_VISITOR_PRUNING_LOCK = 'gvpl:'# key that locks re-pruning of group visitors too soon

######################### Caching mehfil popularity data #########################

GROUP_BIWEEKLY_STICKINESS = 'gbws'# sorted set containing groups alongwith their stickiness values (used for popularity sorting)
CACHED_RANKED_GROUPS = 'crg'# key holding cached json object used to populate popular groups page with a list of top 20 public mehfils

######################### Caching mehfil messaging data #########################

MEHFIL_CACHED_DATA = 'mcd:'#contains json serialized data of mehfil
MEHFIL_CACHED_PAGES = 'mcp:'#contains json serialized data of a user's paginated mehfil list

############# Freezing certain functionality of reported mehfils ################

GROUP_MEMBERSHIP_FROZEN = 'gmf:' #key locking the membership functionality of a public mehfil
GROUP_DELETION_FROZEN = 'gdf:' #key locking the deletion functionality of a public mehfil
GROUP_TOPIC_CHANGE_FROZEN = 'gtcf:' #key locking the topic change functionality of a public mehfil
GROUP_RULES_CHANGE_FROZEN = 'grcf:' #key locking the rules functionality of a public mehfil
GROUP_OWNERSHIP_TRANSFER_FROZEN = 'gotf:' #key locking the ownershipt transfer functionality of a public mehfil

######################## Group creation helper functions ########################

PRIVATE_GROUP_CREATION_RATE_LIMIT_KEY = 'prgcrlk:'#key that rate limits creation of further private groups
PUBLIC_GROUP_CREATION_RATE_LIMIT_KEY = 'pgcrlk:'#key that rate limits creation of further public groups
TEMPORARY_GROUP_CREDENTIALS_STORE = "tgcs:"#temporarily stores group credentials (used when showing user a 'preview')

######################## Handling group membership and invites ########################

PUBLIC_GROUPS_USER_IS_A_MEMBER_OF = 'upubg:' #sorted set containing group_ids of public groups a user is a member of
PRIVATE_GROUPS_USER_IS_A_MEMBER_OF = 'uprvg:' #sorted set containing group_ids of private groups a user is a member of
USER_INVITES = "ui:"#sorted set holding all group ids a user has been invited to
GROUP_INVITES = "gi:"#sorted set holding all user ids invited to a particular group
GROUP_MEMBERS = "gm:"#sorted set holding group members
GROUP_MEMBERSHIP_CACHE = "gmc:"#key holding cached membership data of a group
GROUP_RULES_SIGNATORY = "gr:"#sorted set holding group rules signatories
GROUP_MEMBERSHIP_AND_SIGNATORY_CACHE = 'grs:'#key holding cached data group membership and rules signatory flags for a particular user
GROUP_OFFICER_INVITES = 'goi:'#sorted set containing invites sent by public mehfil officers
GROUP_OWNER_INVITES = 'gowi:'#sorted set containing invites sent by public mehfil owner
PRIVATE_GROUP_MEMBER_INVITES = 'pgmi:'#sorted set containing invites sent by a specific private mehfil member
PRIVATE_GROUP_OWNER_INVITES = 'pgowi:'#sorted set containing invites sent by private mehfil owner
GROUP_INVITE_LOCK = 'giv:'# key that locks further invites to a user from a certain group
GROUP_EXITING_LOCKED = 'gel:'# key used to rate limit users from joining and then abruptly leaving a public mehfil
GROUP_REENTRY_LOCKED = 'grl:'# key used to rate limit users from rejoining a group immediately after exiting

##################################### Punishing group users #####################################

ADMINISTRATION_ACTIVITY_COUNTER = 'gak:'# group administration key used to generate ID of administration activity
KICKED_USERS = 'ku:'# sorted set containing kicked user_ids and the starting time of their punishments
KICKED_HASH = 'kh:'# hash containig data of who kicked the user out, how long the punishment would last, why the punishment was given
GROUP_ADMIN_HISTORY = 'gph:'# a list containing the latest administrative activity in the group
ADMIN_HISTORY_HASH = 'ph:'# hash containing data regarding specific administrative activity
PUNISHER_RATE_LIMITED = 'prl:'# key that rate limits the officer for a few seconds
CACHED_KICKED_LIST = 'ckl:'#key containing cached kicked list of a certain group

################################### Group feedback ###################################

PRAISE_FEEDBACK = 'pf:'# sorted set containing praise sent to open group owners directly by users
COMPLAINT_FEEDBACK = 'cf:'# sorted set containing complaints sent to open group owners directly by users
IDEA_FEEDBACK = 'if:'# sorted set containing ideas sent to open group owners directly by users
FEEDBACK_HASH = 'fh:'# contains details of feedback 
FEEDBACK_RATE_LIMITED = 'frl:'# key that ensures a user cannot submit feedback too often
FEEDBACK_ID = 'fi:'# key that holds an ID counter for feedback related data
CACHE_PRAISE_FEEDBACK = 'cpf:'# cached data
CACHE_COMPLAINT_FEEDBACK = 'ccf:'# cached data
CACHE_IDEA_FEEDBACK = 'cif:'# cached data

################################### Group ownership transfer ###################################

GROUP_OWNERSHIP_REQUEST = 'gor:'#sorted set containing all current requests of ownership
GROUP_OWNERSHIP_HASH = 'goh:'#hash containing data related to group ownership 'requestor'
GROUP_OWNERSHIP_TRANSFER_REQUEST_RATE_LIMIT = 'otrl:'#key that rate limits someone from sending an ownership transfer request again and again
OWNERSHIP_TRANSFER_REQUEST_CACHE = 'otrc:'# key holding cached ownership requests data
GROUP_TRANSACTIONS_RATE_LIMITED = 'gtrl:'#rate limits user from selling or accepting ownership of another group

#################################### Populating and retrieving group info ####################################

CACHED_GROUP_INFO = 'cgi:'# key containing cached group info
CACHED_REPORTED_GROUP_INFO = 'crgi:'# key containing cached group info used when deciding punishments of reported groups

#################################### Group required data caches ####################################

GRP_REQD_DATA_ONE = 'grd1:'# key holding cached mehfil data required to render it/ post to it
GRP_REQD_DATA_TWO = 'grd2:'# key holding cached mehfil data required to render it/ post to it
GRP_REQD_DATA_THREE = 'grd3:'# key holding cached mehfil data required to render it/ post to it
GRP_REQD_DATA_FOUR = 'grd4:'# key holding cached mehfil data required to render it/ post to it
GRP_REQD_DATA_FIVE = 'grd5:'# key holding cached mehfil data required to render it/ post to it
GRP_REQD_DATA_SIX = 'grd6:'# key holding cached mehfil data required to render it/ post to it
GRP_REQD_DATA_SEVEN = 'grd6:'# key holding cached mehfil data required to render it/ post to it
GRP_REQD_DATA_EIGHT = 'grd7:'# key holding cached mehfil data required to render it/ post to it

######################## Rate limiting mehfil topic and rules changes ########################

TOPIC_CHANGE_ATTEMPT = "tca:"#key keeping track of how many mehfil topic changes were attempted by a certain user
USER_ATTEMPT_RATE_LIMITED = 'url:'#key that rate limits topic changes in mehfils
TOPIC_CHANGE_RATE_LIMITED = 'trl:'#key that rate limits topic changes in mehfils
RULES_CHANGE_ATTEMPT = "rca:"#key keeping track of how many mehfil topic changes were attempted by a certain user
RULES_CHANGE_RATE_LIMITED = 'rcrl:'#key that rate limits topic changes in mehfils

######################################### Utilities #########################################

def convert_to_epoch(time):
	#time = pytz.utc.localize(time)
	return (time-datetime(1970,1,1)).total_seconds()

def nickname_strings(culprit_ids, with_list=False):
	"""
	Returns nickname strings when given user ids so that they can be used to populate history of actions
	"""
	culprit_unames = retrieve_bulk_unames(culprit_ids, decode=True)#returns in id-username dictionary format (where id is 'int', username is 'str')
	list_of_unames = list(culprit_unames.values())
	lenth_of_list = len(list_of_unames)
	unames_string, counter = '', 1
	for culprit_uname in list_of_unames:
		if counter == lenth_of_list:
			unames_string += culprit_uname
		else:
			unames_string += culprit_uname+', '
		counter += 1
	if with_list:
		return unames_string, list_of_unames
	else:
		return unames_string


def get_duration(punishment_duration, type_of_punishment, type_of_response="string"):
	"""
	Returns exact time duration of kick when given punishment code (e.g. '1', '2' etc)
	"""
	if type_of_punishment == 'kick' and type_of_response == 'string':
		if punishment_duration == '1':
			return '3 hours'
		elif punishment_duration == '2':
			return '1 day'
		elif punishment_duration == '3':
			return '3 days'
		elif punishment_duration == '4':
			return '1 week'
		elif punishment_duration == '5':
			return '1 month'
		elif punishment_duration == '6':
			return 'Forever'
		else:
			return ''
	elif type_of_punishment == 'kick' and type_of_response == "int":
		if punishment_duration == '1':
			return THREE_HOURS
		elif punishment_duration == '2':
			return ONE_DAY
		elif punishment_duration == '3':
			return THREE_DAYS
		elif punishment_duration == '4':
			return ONE_WEEK
		elif punishment_duration == '5':
			return ONE_MONTH
		elif punishment_duration == '6':
			return None
		else:
			return ''



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

############################## Group creation and content submission ##############################


def create_group_credentials(owner_id,owner_uname,owner_join_time, group_id,privacy,uuid,topic,pics,created_at,grp_categ,rules=None, raw_rules=None):
	"""
	Creates a mapping of group credentials

	Used in private group creation: DirectMessageCreateView(), ClosedGroupCreateView()
	User in public group creation: create_open_group()
	"""
	mapping = {'oi':owner_id,'oun':owner_uname,'gi':group_id,'p':privacy,'u':uuid,'tp':topic,'pics':pics,'ct':created_at,'grp_categ':grp_categ,\
	'r':'','rr':''}
	if rules:
		mapping["r"] = rules
	if raw_rules:
		mapping["rr"] = raw_rules
	my_server = redis.Redis(connection_pool=POOL)
	my_server.hmset(GROUP+str(group_id),mapping)
	my_server.zadd(GROUP_LIST,group_id, created_at)
	my_server.set(GROUP_UUID_TO_ID_MAPPING+str(uuid),group_id)
	my_server.delete(CACHED_USER_OWNERSHIP_PUBLIC_GROUPS+str(owner_id))
	create_group_membership_and_rules_signatory(group_id=group_id, member_id=owner_id, time_now=created_at, member_join_time=owner_join_time, \
		is_public=False if privacy=='1' else True, member_is_owner=True, my_server=my_server)#adding owner as group member and rules signatory
	if privacy == '1':
		# log topic
		log_group_topic_change(group_id, topic, owner_id, created_at, my_server=my_server)


def retrieve_latest_user_owned_mehfils(user_id):
	"""
	Retrieves data of mehfils owned by given user_id

	This is displayed in user profiles
	"""
	user_id = str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(CACHED_USER_OWNERSHIP_PUBLIC_GROUPS+user_id)
	if cached_data:
		return json.loads(cached_data)
	else:
		group_ids_and_ownership_times = my_server.zrevrange(GROUPS_OWNED_BY_USER+str(user_id),0,-1, withscores=True)
		if group_ids_and_ownership_times:
			groups_and_topics, num_grps = [], 0
			# get latest 5 public groups owned by a user
			for group_id, ownership_time in group_ids_and_ownership_times:
				topic, privacy, uuid = my_server.hmget(GROUP+group_id,'tp','p','u')
				if privacy == '0':
					groups_and_topics.append((group_id, uuid, topic, ownership_time))
					num_grps += 1
				if num_grps >= NUM_PUBLIC_GROUPS_OWNED_SHOWN_ON_PROFILE:
					break
			my_server.setex(CACHED_USER_OWNERSHIP_PUBLIC_GROUPS+user_id,json.dumps(groups_and_topics),TEN_MINS)
			return groups_and_topics
		return []


def save_group_topic_and_rules(group_id, topic, rules, raw_rules):
	"""
	Setting topic and rules together

	Used in owner_rejoining_public_group()
	"""
	if group_id:
		key = GROUP+str(group_id)
		my_server = redis.Redis(connection_pool=POOL)
		if my_server.exists(key):
			my_server.hmset(key,{'r':rules,'rr':raw_rules,'tp':topic})
			invalidate_cached_group_reqd_data(group_id, my_server=my_server)
			return True
		else:
			return False
	else:
		return False


def log_group_topic_change(group_id, topic, writer_id, time_now, my_server=None):
	"""
	Documents topics to show topic history in a list (private mehfils only)

	Only used for private mehfils
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	topic_id = my_server.incr(GROUP_TOPIC_COUNTER+group_id)
	topic_list_key = GROUP_TOPIC_LIST+group_id
	my_server.hmset(GROUP_TOPIC_HASH+group_id+":"+str(topic_id),{'tp':topic,'t':time_now, 'sb':writer_id})
	my_server.zadd(topic_list_key,topic_id,time_now)
	my_server.delete(CACHED_GROUP_INFO+group_id)
	my_server.delete(CACHED_GROUP_TOPIC_LIST+group_id)
	if my_server.zcard(topic_list_key) > 13:
		# trim 4 items from list
		topic_ids = my_server.zrange(topic_list_key,0,3)
		if topic_ids:
			pipeline1 = my_server.pipeline()
			for topic_id in topic_ids:
				pipeline1.delete(GROUP_TOPIC_HASH+group_id+":"+topic_id)
			pipeline1.zrem(topic_list_key,*topic_ids)
			pipeline1.execute()


def save_group_topic(group_id, topic, writer_id=None, time_now=None, private=False):
	"""
	Setting new topic in group object
	"""
	key = GROUP+str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(key):
		my_server.hset(key,'tp',topic)
		invalidate_cached_group_reqd_data(group_id, my_server=my_server)
		if private:
			# log last 10 topics
			log_group_topic_change(group_id, topic, writer_id, time_now, my_server)


def save_group_rules(group_id, rules, raw_rules):
	"""
	Setting new rules in group object
	"""
	key = GROUP+str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(key):
		mapping = {'r':rules,'rr':raw_rules}
		my_server.hmset(key,mapping)


def retrieve_group_rules(group_id,raw=False):
	"""
	Returns rules of group (if group exists)
	"""
	if group_id:
		key = 'rr' if raw else 'r'
		rules = redis.Redis(connection_pool=POOL).hget(GROUP+str(group_id),key)
		if rules:
			return rules.decode('utf-8')
		else:
			return ''
	else:
		return ''
	
def invalidate_cached_group_reqd_data(group_id, my_server=None):
	"""
	Invalidate this cached data when group deleted, owner is changed, or topic is changed
	"""
	cache_keys = [GRP_REQD_DATA_ONE+group_id,GRP_REQD_DATA_TWO+group_id,GRP_REQD_DATA_THREE+group_id,GRP_REQD_DATA_FOUR+group_id,GRP_REQD_DATA_FIVE+group_id,\
	GRP_REQD_DATA_SIX+group_id,GRP_REQD_DATA_SEVEN+group_id,GRP_REQD_DATA_EIGHT+group_id]
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for cache_key in cache_keys:
		pipeline1.delete(cache_key)
	pipeline1.execute()


def retrieve_cached_group_reqd_data(group_id, encoding, my_server=None):
	"""
	Retrieving cached data required to render or post to a public/private mehfil

	ENCODING:
	'111' means with_group_owner_id, with_pics_perm and with_uuid
	'110' means with_group_owner_id and with_pics_perm
	'101' means with_group_owner_id and with_uuid
	'011' means with_pics_perm and with_uuid
	'100' means with_group_owner_id
	'010' means with_pics_perm
	'001' means with_uuid
	'000' means with nothing extra!
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if encoding == '111':
		data = my_server.get(GRP_REQD_DATA_ONE+group_id)
	elif encoding == '110':
		data = my_server.get(GRP_REQD_DATA_TWO+group_id)
	elif encoding == '101':
		data = my_server.get(GRP_REQD_DATA_THREE+group_id)
	elif encoding == '011':
		data = my_server.get(GRP_REQD_DATA_FOUR+group_id)
	elif encoding == '100':
		data = my_server.get(GRP_REQD_DATA_FIVE+group_id)
	elif encoding == '010':
		data = my_server.get(GRP_REQD_DATA_SIX+group_id)
	elif encoding == '001':
		data = my_server.get(GRP_REQD_DATA_SEVEN+group_id)
	elif encoding == '000':
		data = my_server.get(GRP_REQD_DATA_EIGHT+group_id)
	else:
		return None
	if data:
		return json.loads(data)
	else:
		return None
	

def cache_group_reqd_data(group_id,data,encoding,my_server = None):
	"""
	Caching data required to render or post to a public/private mehfil

	ENCODING:
	'111' means with_group_owner_id, with_pics_perm and with_uuid
	'110' means with_group_owner_id and with_pics_perm
	'101' means with_group_owner_id and with_uuid
	'011' means with_pics_perm and with_uuid
	'100' means with_group_owner_id
	'010' means with_pics_perm
	'001' means with_uuid
	'000' means with nothing extra!
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if encoding not in ('111','110','101','011','100','010','001','000'):
		return None
	else:
		data = json.dumps(data)
		if encoding == '111':
			my_server.setex(GRP_REQD_DATA_ONE+group_id,data,ONE_DAY)
		elif encoding == '110':
			my_server.setex(GRP_REQD_DATA_TWO+group_id,data,ONE_DAY)
		elif encoding == '101':
			my_server.setex(GRP_REQD_DATA_THREE+group_id,data,ONE_DAY)
		elif encoding == '011':
			my_server.setex(GRP_REQD_DATA_FOUR+group_id,data,ONE_DAY)
		elif encoding == '100':
			my_server.setex(GRP_REQD_DATA_FIVE+group_id,data,ONE_DAY)
		elif encoding == '010':
			my_server.setex(GRP_REQD_DATA_SIX+group_id,data,ONE_DAY)
		elif encoding == '001':
			my_server.setex(GRP_REQD_DATA_SEVEN+group_id,data,ONE_DAY)
		else:
			# encoding is '000'
			my_server.setex(GRP_REQD_DATA_EIGHT+group_id,data,ONE_DAY)



def retrieve_group_uuid(group_id):
	"""
	Returns uuid associated to a group
	"""
	return redis.Redis(connection_pool=POOL).hget(GROUP+str(group_id),'u')


def retrieve_group_category(group_id):
	"""
	Returns the category of the group (e.g. if it's only for pink stars)
	"""
	return redis.Redis(connection_pool=POOL).hget(GROUP+str(group_id),'grp_categ')


def retrieve_group_buying_time_and_price(group_id):
	"""
	Returns group buying time and price
	"""
	return redis.Redis(connection_pool=POOL).hmget(GROUP+str(group_id),'tos','pp')


def retrieve_group_owner_uname(group_id):
	"""
	Returns group's owner's uname
	"""
	owner_uname = redis.Redis(connection_pool=POOL).hget(GROUP+str(group_id),'oun')
	if owner_uname:
		return owner_uname.decode('utf-8')
	else:
		return owner_uname


def retrieve_group_topic_log(group_id):
	"""
	Retrieves all previous topics logged in a group (private mehfils only)
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(CACHED_GROUP_TOPIC_LIST+group_id)
	if cached_data:
		return json.loads(cached_data)
	else:
		topic_ids = my_server.zrevrange(GROUP_TOPIC_LIST+group_id,0,-1)
		pipeline1 = my_server.pipeline()
		for topic_id in topic_ids:
			pipeline1.hgetall(GROUP_TOPIC_HASH+group_id+":"+topic_id)
		result = pipeline1.execute()# list of dicts
		final_data = []
		for dictionary in result:
			writer_uname, writer_avurl = retrieve_credentials(dictionary['sb'],decode_uname=True)
			final_data.append((dictionary['tp'].decode('utf-8'),dictionary['t'],writer_uname,writer_avurl))
		my_server.setex(CACHED_GROUP_TOPIC_LIST+group_id,json.dumps(final_data),ONE_DAY)
		return final_data


def retrieve_group_topic(group_id=None, group_uuid=None,requestor_id=None):
	"""
	Returns group's topic from meta data hash

	Populates the meta data from postgresql 'Group' model object if meta_data doesn't exist in redis6
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(group_uuid)) if group_uuid else group_id
	if group_id:
		group_id = str(group_id)
		topic = my_server.hget(GROUP+group_id,'tp')
		if topic:
			return topic.decode('utf-8')
		else:
			# retrieve group object
			try:
				group_obj = Group.objects.get(id=group_id)
			except Group.DoesNotExist:
				return None
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, delete the user invite (in case it existed) and return Null
				if requestor_id:
					remove_group_invite(requestor_id, group_id)
				return None
			else:
				# populate the source data in redis 6
				created_at = convert_to_epoch(group_obj.created_at)
				group_uuid = group_uuid if group_uuid else group_obj.unique
				topic = group_obj.topic 
				mapping = {'oi':group_obj.owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':group_uuid,'tp':topic,\
				'r':group_obj.rules, 'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+str(group_uuid),group_id)
				return topic
	else:
		if group_uuid:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=group_uuid)
			except Group.DoesNotExist:
				return None
			group_id = str(group_obj.id)
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, delete the user invite (in case it existed) and return Null
				if requestor_id:
					remove_group_invite(requestor_id, group_id)
				return None
			else:
				# populate the source data in redis 6
				created_at = convert_to_epoch(group_obj.created_at)
				topic = group_obj.topic 
				mapping = {'oi':group_obj.owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':group_uuid,\
				'tp':topic,'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+str(group_uuid),group_id)
				return topic
		else:
			return None


def retrieve_group_creation_time(group_id):
	"""
	Returns group's creation time in epoch time format

	Useful when assessing whether a group's ownership can be transferred
	"""
	if group_id:
		creation_time = redis.Redis(connection_pool=POOL).hget(GROUP+str(group_id),'ct')
		if creation_time:
			try:
				return float(creation_time)
			except (ValueError,TypeError,NameError):
				return 0
		else:
			return 0
	else:
		return 0


def retrieve_group_privacy(group_id=None,group_uuid=None,requestor_id=None):
	"""
	Returns group's privacy from meta data hash

	Populates the meta data from postgresql 'Group' model object if meta_data doesn't exist in redis6
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(group_uuid)) if group_uuid else group_id
	if group_id:
		group_id = str(group_id)
		privacy = my_server.hget(GROUP+group_id,'p')
		if privacy:
			return privacy
		else:
			# retrieve group object
			try:
				group_obj = Group.objects.get(id=group_id)
			except Group.DoesNotExist:
				return None
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, delete the user invite (in case it existed) and return Null
				if requestor_id:
					remove_group_invite(requestor_id, group_id)
				return None
			else:
				# populate the source data in redis 6
				created_at = convert_to_epoch(group_obj.created_at)
				group_uuid = group_uuid if group_uuid else group_obj.unique
				mapping = {'oi':group_obj.owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':group_uuid,'tp':group_obj.topic,\
				'r':group_obj.rules, 'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+str(group_uuid),group_id)
				return str(group_obj.private)
	else:
		if group_uuid:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=group_uuid)
			except Group.DoesNotExist:
				return None
			group_id = str(group_obj.id)
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, delete the user invite (in case it existed) and return Null
				if requestor_id:
					remove_group_invite(requestor_id, group_id)
				return None
			else:
				# populate the source data in redis 6
				created_at = convert_to_epoch(group_obj.created_at)
				group_privacy = str(group_obj.private)
				mapping = {'oi':group_obj.owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_privacy,'u':group_uuid,\
				'tp':group_obj.topic ,'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+str(group_uuid),group_id)
				return group_privacy
		else:
			return None



def retrieve_group_owner_id(group_id=None,group_uuid=None,with_group_id=False,with_group_privacy=False):
	"""
	Returns group's owner's ID from meta data hash

	Populates the meta data from postgresql 'Group' model object if meta_data doesn't exist in redis6
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(group_uuid)) if group_uuid else group_id
	if group_id:
		group_id = str(group_id)
		group_key = GROUP+group_id
		if my_server.exists(group_key):
			if with_group_privacy and with_group_id:
				group_owner_id, group_privacy = my_server.hmget(group_key,'oi','p')
				return group_owner_id, group_id, group_privacy
			elif with_group_privacy:
				group_owner_id, group_privacy = my_server.hmget(group_key,'oi','p')
				return group_owner_id, group_privacy
			elif with_group_id:
				return my_server.hget(group_key,'oi'), group_id
			else:
				return my_server.hget(group_key,'oi')
		else:
			# retrieve group object - take counter measures
			try:
				group_obj = Group.objects.get(id=group_id)
			except Group.DoesNotExist:
				if with_group_privacy and with_group_id:
					return None, None, None
				elif with_group_privacy:
					return None, None
				elif with_group_id:
					return None, None
				else:
					return None
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, so don't take counter measures
				if with_group_privacy and with_group_id:
					return None, None, None
				elif with_group_privacy:
					return None, None
				elif with_group_id:
					return None, None
				else:
					return None
			else:
				# populate the source data in redis 6
				created_at = convert_to_epoch(group_obj.created_at)
				group_uuid = group_uuid if group_uuid else group_obj.unique
				group_owner_id = str(group_obj.owner_id)
				group_privacy = group_obj.private
				mapping = {'oi':group_owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_privacy,'u':group_uuid,'tp':group_obj.topic,\
				'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+str(group_uuid),group_id)
				if with_group_privacy and with_group_id:
					return group_owner_id, group_id, group_privacy
				elif with_group_privacy:
					return group_owner_id, group_privacy
				elif with_group_id:
					return group_owner_id, group_id
				else:
					return group_owner_id
	else:
		if group_uuid:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=group_uuid)
			except Group.DoesNotExist:
				if with_group_privacy and with_group_id:
					return None, None, None
				elif with_group_privacy:
					return None, None
				elif with_group_id:
					return None, None
				else:
					return None
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, so don't take counter measures
				if with_group_privacy and with_group_id:
					return None, None, None
				elif with_group_privacy:
					return None, None
				elif with_group_id:
					return None, None
				else:
					return None
			else:
				# populate the source data in redis 6
				group_id = str(group_obj.id)
				group_privacy = str(group_obj.private)
				created_at = convert_to_epoch(group_obj.created_at)
				group_owner_id = str(group_obj.owner_id)
				mapping = {'oi':group_owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_privacy,'u':group_uuid,\
				'tp':group_obj.topic,'r':group_obj.rules,'pics':str(group_obj.pics_ki_ijazat),'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+str(group_uuid),group_id)
				if with_group_privacy and with_group_id:
					return group_owner_id, group_id, group_privacy
				elif with_group_privacy:
					return group_owner_id, group_privacy
				elif with_group_id:
					return group_owner_id, group_id
				else:
					return group_owner_id
		else:
			if with_group_privacy and with_group_id:
				return None, None, None
			elif with_group_privacy:
				return None, None
			elif with_group_id:
				return None, None
			else:
				return None


def retrieve_group_id(group_uuid):
	"""
	Returns group's ID from meta data hash

	Populates the meta data from postgresql 'Group' model object if meta_data doesn't exist in redis6
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if group_uuid:
		group_uuid = str(group_uuid)
		group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+group_uuid)
		if group_id:
			return group_id
		else:
			# retrieve group object
			try:
				group_obj = Group.objects.get(unique=group_uuid)
			except Group.DoesNotExist:
				return None
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, so don't take counter measures
				return None
			else:
				# populate the source data in redis 6
				group_id = str(group_obj.id)
				created_at = convert_to_epoch(group_obj.created_at)
				mapping = {'oi':group_obj.owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':group_uuid,'tp':group_obj.topic,\
				'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+group_uuid,group_id)
				return group_id
	else:
		return None


def retrieve_group_reqd_data(group_id=None, group_uuid=None, with_group_owner_id=False, with_pics_perm=False, with_uuid=False, requestor_id=None):
	"""
	Retrieves only group privacy, group_id, group_topic, group_owner_id (optional), 'pics'(optional), uuid(option) instead of entire group metadata

	This abbreviated data is enough to render a private or public group
	This is the core function used to render or post to mehfils (mehfils' most prolific actions)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(group_uuid)) if group_uuid else group_id
	if group_id:
		group_id = str(group_id)
		group_key = GROUP+group_id
		if my_server.exists(group_key):
			if with_group_owner_id and with_pics_perm and with_uuid:
				data = retrieve_cached_group_reqd_data(group_id, '111', my_server)
				if not data:
					privacy, topic, owner_id, pics_perms, uuid = my_server.hmget(group_key,'p','tp','oi','pics','u')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'pics':pics_perms,'u':uuid}
					cache_group_reqd_data(group_id,data,'111',my_server)
			elif with_group_owner_id and with_pics_perm:
				data = retrieve_cached_group_reqd_data(group_id, '110', my_server)
				if not data:
					privacy, topic, owner_id, pics_perms = my_server.hmget(group_key,'p','tp','oi','pics')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'pics':pics_perms}
					cache_group_reqd_data(group_id,data,'110',my_server)
			elif with_group_owner_id and with_uuid:
				data = retrieve_cached_group_reqd_data(group_id, '101', my_server)
				if not data:
					privacy, topic, owner_id, uuid = my_server.hmget(group_key,'p','tp','oi','u')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'u':uuid}
					cache_group_reqd_data(group_id,data,'101',my_server)
			elif with_pics_perm and with_uuid:
				data = retrieve_cached_group_reqd_data(group_id, '011', my_server)
				if not data:
					privacy, topic, pics_perms, uuid = my_server.hmget(group_key,'p','tp','pics','u')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'pics':pics_perms,'u':uuid}
					cache_group_reqd_data(group_id,data,'011',my_server)
			elif with_group_owner_id:
				data = retrieve_cached_group_reqd_data(group_id, '100', my_server)
				if not data:
					privacy, topic, owner_id = my_server.hmget(group_key,'p','tp','oi')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id}
					cache_group_reqd_data(group_id,data,'100',my_server)
			elif with_pics_perm:
				data = retrieve_cached_group_reqd_data(group_id, '010', my_server)
				if not data:
					privacy, topic, pics_perms = my_server.hmget(group_key,'p','tp','pics')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'pics':pics_perms}
					cache_group_reqd_data(group_id,data,'010',my_server)
			elif with_uuid:
				data = retrieve_cached_group_reqd_data(group_id, '001', my_server)
				if not data:
					privacy, topic, uuid = my_server.hmget(group_key,'p','tp','u')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'u':uuid}
					cache_group_reqd_data(group_id,data,'001',my_server)
			else:
				data = retrieve_cached_group_reqd_data(group_id, '000', my_server)
				if not data:
					privacy, topic = my_server.hmget(group_key,'p','tp')
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8')}
					cache_group_reqd_data(group_id,data,'000',my_server)
			return data
		else:
			# populate the data
			try:
				group_obj = Group.objects.get(id=group_id)
			except Group.DoesNotExist:
				return {}
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, delete the user invite (in case it existed) and return Null
				if requestor_id:
					remove_group_invite(requestor_id, group_id)
				return {}
			else:
				created_at = convert_to_epoch(group_obj.created_at)
				unique_id = str(group_obj.unique)
				privacy = str(group_obj.private)
				topic = group_obj.topic
				owner_id = str(group_obj.owner_id)
				pics_perms = str(group_obj.pics_ki_ijazat)
				mapping = {'oi':owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':privacy,'u':unique_id,'tp':topic,'r':group_obj.rules,\
				'pics':pics_perms,'ct':created_at,'grp_categ':categ}
				my_server.hmset(group_key,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+unique_id,group_id)
				if with_group_owner_id and with_pics_perm and with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'pics':pics_perms,'u':unique_id}
					cache_group_reqd_data(group_id,data,'111',my_server)
				elif with_group_owner_id and with_pics_perm:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'pics':pics_perms}
					cache_group_reqd_data(group_id,data,'110',my_server)
				elif with_group_owner_id and with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'u':unique_id}
					cache_group_reqd_data(group_id,data,'101',my_server)
				elif with_pics_perm and with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'pics':pics_perms,'u':unique_id}
					cache_group_reqd_data(group_id,data,'011',my_server)
				elif with_group_owner_id:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id}
					cache_group_reqd_data(group_id,data,'100',my_server)
				elif with_pics_perm:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'pics':pics_perms}
					cache_group_reqd_data(group_id,data,'010',my_server)
				elif with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'u':unique_id}
					cache_group_reqd_data(group_id,data,'001',my_server)
				else:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8')}
					cache_group_reqd_data(group_id,data,'000',my_server)
				return data
	else:
		if group_uuid:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=group_uuid)
			except Group.DoesNotExist:
				return {}
			group_id = str(group_obj.id)
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, delete the user invite (in case it existed) and return Null
				if requestor_id:
					remove_group_invite(requestor_id, group_id)
				return {}
			else:
				created_at = convert_to_epoch(group_obj.created_at)
				privacy = str(group_obj.private)
				topic = group_obj.topic
				unique_id = str(group_uuid)
				owner_id = str(group_obj.owner_id)
				pics_perms = str(group_obj.pics_ki_ijazat)
				mapping = {'oi':owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':privacy,'u':unique_id,'tp':topic,'r':group_obj.rules,\
				'pics':pics_perms,'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+unique_id,group_id)
				if with_group_owner_id and with_pics_perm and with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'pics':pics_perms,'u':unique_id}
					cache_group_reqd_data(group_id,data,'111',my_server)
				elif with_group_owner_id and with_pics_perm:
					# data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'pics':pics_perms}
					data = {'p':privacy,'gi':group_id,'tp':topic,'oi':owner_id,'pics':pics_perms}
					cache_group_reqd_data(group_id,data,'110',my_server)
				elif with_group_owner_id and with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id,'u':unique_id}
					cache_group_reqd_data(group_id,data,'101',my_server)
				elif with_pics_perm and with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'pics':pics_perms,'u':unique_id}
					cache_group_reqd_data(group_id,data,'011',my_server)
				elif with_group_owner_id:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'oi':owner_id}
					cache_group_reqd_data(group_id,data,'100',my_server)
				elif with_pics_perm:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'pics':pics_perms}
					cache_group_reqd_data(group_id,data,'010',my_server)
				elif with_uuid:
					data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8'),'u':unique_id}
					cache_group_reqd_data(group_id,data,'001',my_server)
				else:
					# data = {'p':privacy,'gi':group_id,'tp':topic.decode('utf-8')}
					data = {'p':privacy,'gi':group_id,'tp':topic}
					cache_group_reqd_data(group_id,data,'000',my_server)
				return data
		else:
			return {}


def retrieve_group_meta_data(group_id=None,group_uuid=None):
	"""
	Returns entire group meta data, retrieved either via group ID or group UUID

	Populates the meta data from postgresql 'Group' model object if meta_data doesn't exist in redis6
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(group_uuid)) if group_uuid else group_id
	if group_id:
		group_id = str(group_id)
		key = GROUP+group_id
		meta_data = my_server.hgetall(key)
		if meta_data:
			meta_data['tp'] = meta_data['tp'].decode('utf-8')
			meta_data['r'] = meta_data['r'].decode('utf-8')
			meta_data['oun'] = meta_data['oun'].decode('utf-8')
			return meta_data
		else:
			# try to retrieve the source data
			try:
				group_obj = Group.objects.get(id=group_id)
			except Group.DoesNotExist:
				return {}
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, don't take counter measures
				return {}
			else:
				# populate the source data in redis 6
				created_at = convert_to_epoch(group_obj.created_at)
				unique_id = str(group_obj.unique)
				mapping = {'oi':str(group_obj.owner_id),'oun':group_obj.owner.username,'gi':group_id,'p':str(group_obj.private),'u':unique_id,\
				'tp':group_obj.topic,'r':group_obj.rules,'pics':str(group_obj.pics_ki_ijazat),'ct':created_at,'grp_categ':categ}
				my_server.hmset(key,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+unique_id,group_id)
				return mapping
	else:
		if group_uuid:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=group_uuid)
			except Group.DoesNotExist:
				return {}
			categ = group_obj.category
			if categ == '99':
				# group was recently deleted, don't take counter measuress
				return {}
			else:
				# populate the source data in redis 6
				group_id = str(group_obj.id)
				created_at = convert_to_epoch(group_obj.created_at)
				mapping = {'oi':str(group_obj.owner_id),'oun':group_obj.owner.username,'gi':group_id,'p':str(group_obj.private),'u':group_uuid,\
				'tp':group_obj.topic,'r':group_obj.rules,'pics':str(group_obj.pics_ki_ijazat),'ct':created_at,'grp_categ':categ}
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+str(group_uuid),group_id)
				return mapping
		else:
			return {}


def retrieve_group_owner_unames_and_uniques_and_topics_in_bulk(group_ids):
	"""
	Bulk retrieves and return owner_unames, unique_ids and group topics (for use by get_ranked_groups())

	Populates the meta data from postgresql 'Group' model object if meta_data doesn't exist in redis6
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if group_ids:
		list_of_group_dicts = []
		pipeline1 = my_server.pipeline()
		for group_id in group_ids:
			key = GROUP+str(group_id)
			pipeline1.hmget(key,'oun','tp','u')
		result1, counter = pipeline1.execute(), 0
		for group_id in group_ids:
			tup = result1[counter]
			if tup[0]:
				group_dict = {'oun':tup[0].decode('utf-8'),'tp':tup[1].decode('utf-8'),'u':tup[2],'gi':group_id}
				list_of_group_dicts.append(group_dict)
			else:
				group_dict = {'oun':None,'tp':None,'u':None,'gi':group_id}
				list_of_group_dicts.append(group_dict)
			counter += 1
		group_ids_to_retrieve = []
		for group_obj in list_of_group_dicts:
			if not group_obj['oun']:
				group_ids_to_retrieve.append(group_obj['gi'])
		if group_ids_to_retrieve:
			retrieved_groups = Group.objects.filter(id__in=group_ids_to_retrieve)
			dict_of_group_dicts = {}
			for group in retrieved_groups:
				created_at = convert_to_epoch(group.created_at)
				unique_id = str(group.unique)
				group_id = str(group.id)
				mapping = {'oi':group.owner_id,'oun':group.owner.username,'gi':group_id,'p':group.private,'u':unique_id,\
				'tp':group.topic,'r':group.rules,'pics':group.pics_ki_ijazat,'ct':created_at,'grp_categ':group.category}
				dict_of_group_dicts[group_id] = mapping
				my_server.hmset(GROUP+group_id,mapping)
				my_server.zadd(GROUP_LIST,group_id, created_at)
				my_server.set(GROUP_UUID_TO_ID_MAPPING+unique_id,group_id)
			for group_obj in list_of_group_dicts:
				if not group_obj['oun']:
					group_dict = dict_of_group_dicts.get(group_obj['gi'],None)
					if group_dict:
						group_obj['oun'] = group_dict['oun']
						group_obj['tp'] = group_dict['tp']
						group_obj['u'] = group_dict['u']
		return list_of_group_dicts
	else:
		return []

def increment_pic_count(group_id, sender_id):
	"""
	Increments a counter keeping track of pic sending in private mehfils
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zincrby(GROUP_PIC_COUNT+group_id,sender_id,amount=1)
	my_server.delete(CACHED_GROUP_INFO+group_id)


def log_group_chatter(group_id, writer_id):
	"""
	Logs who wrote how many times in a private mehfil
	"""
	redis.Redis(connection_pool=POOL).zincrby(GROUP_CHATTER+str(group_id),writer_id,amount=1)


def save_group_submission(writer_id, group_id, text, posting_time, writer_uname,writer_avurl,category,image='',writer_score=None,\
	target_uname=None, target_uid=None, save_latest_submission=False):
	"""
	Saves a reply submitted by a mehfil member

	Works for both private and public mehfils
	"""
	group_id = str(group_id)
	key = GROUP_SUBMISSION_LIST+group_id
	my_server = redis.Redis(connection_pool=POOL)
	submission_id = my_server.incr(SUBMISSION_COUNTER+group_id)
	payload = {'wi':writer_id,'gi':group_id,'si':submission_id,'t':posting_time,'tx':text,'wu':writer_uname,'c':category,'wa':writer_avurl}
	if writer_score:
		payload['ws'] = writer_score
	if image:
		payload['iu'] = image
	if target_uname and target_uid:
		payload['tu'] = target_uname
		payload['tid'] = target_uid
	submission_hash = GROUP_SUBMISSION_HASH+group_id+":"+str(submission_id)
	my_server.hmset(submission_hash,payload)
	my_server.zadd(key,submission_id,posting_time)
	if save_latest_submission:
		# This is useful for populating the "group page" ('reply' and 'invite' submissions ought to be saved, rest are ignored (e.g. 'kick','hide'))
		my_server.hmset(GROUP+group_id,{'lrti':posting_time,'lrau':writer_avurl,'lrsn':writer_uname,'lrtx':text,'rp':image,'lrwi':writer_id,\
			'lrc':category})
	return submission_id, my_server.zcard(key)


def retrieve_group_submissions(group_id,how_many=MSGS_TO_SHOW_IN_GROUP):
	"""
	Retrieves data of latest group submissions for a given group_id

	Works for both public and private mehfils
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	submission_ids = my_server.zrevrange(GROUP_SUBMISSION_LIST+group_id,0,(MSGS_TO_SHOW_IN_GROUP-1))
	reply_hash_names = []
	for submission_id in submission_ids:
		reply_hash_names.append(GROUP_SUBMISSION_HASH+group_id+":"+submission_id)
	pipeline1 = my_server.pipeline()
	for reply_hash in reply_hash_names:
		pipeline1.hgetall(reply_hash)
	result1 = pipeline1.execute()#list of dictionaries is retrieved
	for data in result1:
		data["wu"] = data["wu"].decode('utf-8')
		data["tx"] = data["tx"].decode('utf-8')
		if 'tu' in data:
			data['tu'] = data['tu'].decode('utf-8')
	return result1


def retrieve_single_group_submission(group_id, submission_id, text_only=False, writer_id_only=False):
	"""
	Retrieves a single submission

	One use is for documenting the text of a hidden/unhidden submission (log_in_administrative_activity() in tasks.py)
	"""
	key = GROUP_SUBMISSION_HASH+str(group_id)+":"+str(submission_id)
	if text_only:
		text = redis.Redis(connection_pool=POOL).hget(key,'tx')
		return text.decode('utf-8')
	elif writer_id_only:
		return redis.Redis(connection_pool=POOL).hget(key,'wi')
	else:
		return redis.Redis(connection_pool=POOL).hgetall(key)


def retrieve_group_chatter(group_id):
	"""
	Retrieves which users did how much chatter in a private mehfil
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(CACHED_GROUP_CHATTER+group_id)
	if cached_data:
		return json.loads(cached_data)
	else:
		chatter_key = GROUP_CHATTER+group_id
		if my_server.zcard(chatter_key) > 1:
			# chatter data only makes sense if more than 1 chatterer is logged
			data = my_server.zrevrange(GROUP_CHATTER+group_id,0,-1)
			if data:
				credentials = retrieve_bulk_credentials(data, decode_unames=True)
				final_data = []
				for user_id in data:
					user_id = int(user_id)
					final_data.append((credentials[user_id]['uname'],credentials[user_id]['avurl']))
				my_server.setex(CACHED_GROUP_CHATTER+group_id,json.dumps(final_data),FIFTEEN_MINS)
			return final_data
		else:
			[]


def retrieve_biggest_pic_sharer_in_group(group_id):
	"""
	Retrieves username of most prolific picture sharer in a privte mehfil
	"""
	biggest_pic_sharer_id = redis.Redis(connection_pool=POOL).zrevrange(GROUP_PIC_COUNT+str(group_id),0,0)
	return retrieve_uname(biggest_pic_sharer_id[0], decode=True) if biggest_pic_sharer_id else None


def group_submission_exists(group_id, submission_id):
	"""
	Checking whether a submission into a group exists
	"""
	return redis.Redis(connection_pool=POOL).exists(GROUP_SUBMISSION_HASH+str(group_id)+":"+str(submission_id))


def hide_private_group_submission(group_id, submission_id, unhide=False, action_by=''):
	"""
	Processing group submission hiding for private mehfils

	RULES:
	1) Hide: A regular member can hide their own submission
	2) Hide: The owner can hide any submission
	3) Unhide: A regular member can unhide their submission if it wasn't hidden by the owner
	4) Unhide: The owner can unhide a user's submission only if it was hidden by the owner
	"""
	key = GROUP_SUBMISSION_HASH+str(group_id)+":"+str(submission_id)
	my_server = redis.Redis(connection_pool=POOL)
	current_val, prev_action_by = my_server.hmget(key,'c','ab')
	if unhide:
		# unhide (if allowed by the rules stated in private_group_hide_submission())
		if current_val == '0':
			# already unhidden- take no action
			return False
		else:
			# unhide
			if prev_action_by:
				# someone hid it before - this should ALWAYS be TRUE
				if action_by == 'owner' and prev_action_by == 'writer':
					# cannot take action since writer hid their own submission - group owner can't unhide it
					return False
				elif action_by == 'writer' and prev_action_by == 'owner':
					# cannot take action since owner hid writer's submission - writer can't unhide it
					return False
				else:
					# allowed to unhide
					my_server.hmset(key,{'c':'0','ab':action_by})
					return True
			else:
				my_server.hmset(key,{'c':'0','ab':action_by})
				return True
	else:
		# hide
		if current_val == '3':
			# already hidden - take no action
			return False
		else:
			# can go ahead with hiding it, since it's visible
			my_server.hmset(key,{'c':'3','ab':action_by})
			return True


def hide_group_submission(group_id, submission_id,unhide=False,return_writer_id=True):
	"""
	Hiding a group submission (because it was offensive, etc)

	Return writer ID of submitter by default
	"""
	key = GROUP_SUBMISSION_HASH+str(group_id)+":"+str(submission_id)
	my_server = redis.Redis(connection_pool=POOL)
	# public group hiding
	current_val = my_server.hget(key,'c')
	if unhide:
		if current_val == '3':
			my_server.hset(key,'c','0')
	else:
		if current_val == '0':
			my_server.hset(key,'c','3')#setting category to '3' in order to hide
	if return_writer_id:
		return my_server.hget(key,'wi')



############################# Handling officer appointments ############################


def retrieve_immune_ids(group_id,requestor_id,is_officer=None):
	"""
	Returns all IDs from a groups members that cannot be punished

	Useful when officers or group owner are deciding punishments in a public mehfil
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	owner_id = my_server.hget(GROUP+group_id,'oi')
	is_officer = is_group_officer(group_id,requestor_id, my_server=my_server) if is_officer is None else is_officer# allows us to pass 'is_officer' if already known in the view
	if str(requestor_id) == owner_id:
		# no one is immune except self
		return [requestor_id]
	elif is_officer:
		# is an officer, so all other officers and group owner are immune
		officers_and_appointment_times = retrieve_all_officers(group_id,my_server=my_server)# returns list of tuples of the sort (officer_id, appointment_time)
		return [officer_id for (officer_id, appointment_time) in officers_and_appointment_times]+[owner_id]
	else:
		# is a nobody, so everyone is immune!
		return my_server.zrange(GROUP_MEMBERS+group_id,0,-1)


def group_officer_targeted(group_id, list_of_ids):
	"""
	Returns True if a group officer ID is in list_of_ids provided to the function
	"""
	officers_and_appointment_times = retrieve_all_officers(group_id)
	officer_ids = [officer_id for (officer_id, appointment_time) in officers_and_appointment_times]
	if officer_ids:
		officer_found = False
		for user_id in list_of_ids:
			if str(user_id) in officer_ids:
				officer_found = True
				break
		return officer_found
	else:		
		return False


def is_group_officer(group_id,user_id, my_server=None):
	"""
	Returns confirmation whether a given user_id is an officer in a given group_id
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if my_server.zscore(GROUP_OFFICER_LIST+group_id,user_id):
		return True
	else:
		return False


def can_officer_kick_out(group_id, officer_id):
	"""
	Retrieves whether an officer can kick someone out

	Useful when processing group kicking and unkicking
	"""
	if redis.Redis(connection_pool=POOL).hget(GROUP_OFFICER_HASH+str(group_id)+":"+str(officer_id),'can_kick') == '1':
		return True
	else:
		return False

def can_officer_change_topic(group_id, officer_id):
	"""
	Retrieves whether an officer can change group topic

	Useful when processing group topic changes
	"""
	if redis.Redis(connection_pool=POOL).hget(GROUP_OFFICER_HASH+str(group_id)+":"+str(officer_id),'can_topic') == '1':
		return True
	else:
		return False


def retrieve_group_officer_perms(group_id, officer_id):
	"""
	Retrieves permissions available to an officer
	"""
	can_hide, can_kick, can_topic = redis.Redis(connection_pool=POOL).hmget(GROUP_OFFICER_HASH+str(group_id)+":"+str(officer_id),\
		'can_hide','can_kick','can_topic')
	return can_hide, can_kick, can_topic


def delete_group_officers(group_id, my_server=None):
	"""
	Delete all group officers in bulk (e.g. useful when deleting entire group)
	"""
	group_id = str(group_id)
	officer_list_key = GROUP_OFFICER_LIST+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	officer_ids = my_server.zrange(officer_list_key,0,-1)
	if officer_ids:
		pipeline1 = my_server.pipeline()
		for officer_id in officer_ids:
			pipeline1.delete(GROUP_OFFICER_HASH+group_id+":"+officer_id)
		pipeline1.delete(officer_list_key)
		pipeline1.execute()


def remove_public_mehfil_officers(officer_ids,group_id,num_to_remove,remover_uname,removal_time,my_server=None,no_logging=False):
	"""
	Removes given ids from officer-ship in a given group
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if num_to_remove > 4:
		pipeline1 = my_server.pipeline()
		for officer_id in officer_ids:
			officer_id = str(officer_id)
			pipeline1.zrem(GROUP_OFFICER_LIST+group_id,officer_id)
			pipeline1.delete(GROUP_OFFICER_HASH+group_id+":"+officer_id)
		pipeline1.execute()
	else:
		for officer_id in officer_ids:
			officer_id = str(officer_id)
			my_server.zrem(GROUP_OFFICER_LIST+group_id,officer_id)
			my_server.delete(GROUP_OFFICER_HASH+group_id+":"+officer_id)
	# add group to relevant users' data
	bulk_update_user_officership_set(officer_ids, group_id, remove=True, my_server=my_server)
	# add to administrative activity
	if not no_logging:
		main_sentence = nickname_strings(officer_ids)+" dismissed by "+remover_uname+" at {0}".format(exact_date(removal_time))# avoids ascii problems this way
		add_to_universal_group_activity(group_id, main_sentence, history_type='remove_officer',my_server=my_server)


def retrieve_all_officers(group_id, only_ids=False, with_power_levels=False, my_server=None):
	"""
	Retrieves all officer appointments for a given group
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if only_ids:
		return my_server.zrange(GROUP_OFFICER_LIST+group_id,0,-1)
	else:
		officer_ids_and_times = my_server.zrange(GROUP_OFFICER_LIST+group_id,0,-1,withscores=True)#tuple list
		if with_power_levels:
			officer_ids_times_and_powers = []
			for officer_id, appointment_time in officer_ids_and_times:
				can_hide, can_kick, can_topic = my_server.hmget(GROUP_OFFICER_HASH+group_id+":"+officer_id,'can_hide','can_kick','can_topic')
				officer_ids_times_and_powers.append((officer_id, appointment_time, can_hide, can_kick, can_topic))
			return officer_ids_times_and_powers
		else:
			return officer_ids_and_times


def appoint_public_mehfil_officer(owner_id, group_id, target_user_id, off_app_idx, power_levels, appointment_time, owner_uname):
	"""
	Appointing an officer in a public mehfil
	"""
	group_id, target_user_id = str(group_id), str(target_user_id)
	payload = {'t':appointment_time,'gid':group_id,'can_hide':'1','can_kick':'1' if '2' in power_levels else '0',\
	'can_topic':'1' if '3' in power_levels else '0'}
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zadd(GROUP_OFFICER_LIST+group_id,target_user_id,appointment_time)
	my_server.hmset(GROUP_OFFICER_HASH+group_id+":"+target_user_id,payload)
	# getting rid of user's outstanding officer applications submitted in public group
	rescind_officer_applications(target_user_id, group_id, off_app_idx=off_app_idx, acceptance=True, my_server=my_server)
	# ratelimit further action
	my_server.setex(RATE_LIMIT_OWNER_APPOINTMENTS+group_id+":"+str(owner_id),'1',20)
	# delete group info cache
	my_server.delete(CACHED_GROUP_INFO+group_id)
	# add to administrative activity
	main_sentence = nickname_strings([target_user_id])+" made officer by "+owner_uname+" at {0}".format(exact_date(appointment_time))# avoids ascii problems this way
	add_to_universal_group_activity(group_id, main_sentence, history_type='appoint_officer',my_server=my_server)
	# add group to relevant users' data
	update_user_officership_set(target_user_id, group_id, appointment_time, my_server=my_server)
	################################ Increment officer statistics ################################
	my_server.hincrby(OFFICER_STATISTICS+target_user_id,'ac',amount=1)


def is_officer_appointments_rate_limited(owner_id, group_id):
	"""
	Check if group owner is rate limited from creating more officers
	"""
	ttl = redis.Redis(connection_pool=POOL).ttl(RATE_LIMIT_OWNER_APPOINTMENTS+str(group_id)+":"+str(owner_id))
	if ttl > 2:
		return ttl
	else:
		return None


def officer_appointed_too_many_times(candidate_id):
	"""
	Check if given user is an officer in up to 3 mehfils already (if they are, we'll stop them from taking on another slot)
	"""
	num_appointments_held = redis.Redis(connection_pool=POOL).zcard(GROUPS_IN_WHICH_USER_IS_OFFICER+str(candidate_id))
	if num_appointments_held >= MAX_OFFICER_APPOINTMENTS_ALLWD:
		return candidate_id
	else:
		return None


def remove_group_officer(group_id,target_user_id,my_server=None):
	"""
	Removing a single public mehfil officer (silently, no activity log generated)

	Called when public mehfil is exited by a user
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.zrem(GROUP_OFFICER_LIST+group_id,target_user_id)
	my_server.delete(GROUP_OFFICER_HASH+group_id+":"+str(target_user_id))


def cleanse_all_officer_apps_received_by_group(group_id, with_rate_limits=False, my_server=None):
	"""
	Clears out a group's set of officer applications

	This is useful when group is undergoing full deletion, or when ownership is being transferred
	If 'with_rate_limits' is set to True, applicant's rate-limits are also deleted (so that they can immediately apply again). This is useful when this function is used after ownership transfer of a group.
	"""
	group_officer_app_key = OFFICER_APPLICATIONS_RECEIVED+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if with_rate_limits:
		all_keys = my_server.zrange(group_officer_app_key,0,-1)
		if all_keys:
			for key in all_keys:
				data = key.split(":")
				applier_id = data[1]# data[1] is applier ID
				my_server.delete(OFFICER_APPLICATIONS_RATE_LIMITED+applier_id)# removing the rate-limit so user can apply again
	my_server.delete(CACHED_GROUP_OFFICER_APPLICATIONS+group_id)
	my_server.delete(group_officer_app_key)


def trim_officer_apps_received_by_group(time_now, group_id, app_keys_and_setting_times=None, return_final_apps=False, \
	my_server=None):
	"""
	Trims officer applications received by a public group

	All applications older than OFFICER_APPLICATION_EXPIRY_TIME (3 days) must get truncated
	Called whenever:
	(i) Owner views applications
	(ii) Would-be officer submits an application
	"""
	three_days_ago = time_now - OFFICER_APPLICATION_EXPIRY_TIME# set to 3 days
	keys_to_del, my_server = [], my_server if my_server else redis.Redis(connection_pool=POOL)
	group_officer_app_key = OFFICER_APPLICATIONS_RECEIVED+group_id

	app_keys_and_setting_times = app_keys_and_setting_times if app_keys_and_setting_times else \
	my_server.zrange(group_officer_app_key,0,-1,withscores=True)
	
	if app_keys_and_setting_times:
		app_keys = [app_key for (app_key,setting_time) in app_keys_and_setting_times]
		
		for app_key, setting_time in app_keys_and_setting_times:
			if setting_time < three_days_ago:
				keys_to_del.append(app_key)
		if keys_to_del:
			my_server.zrem(group_officer_app_key,*keys_to_del)
			my_server.delete(CACHED_GROUP_OFFICER_APPLICATIONS+group_id)
			final_applications = [app for app in app_keys if app not in keys_to_del]
		else:
			final_applications = app_keys
		# if list still exists after all of the above, expire it after 2 weeks in any case
		my_server.expire(group_officer_app_key,TWO_WEEKS)
	else:
		# no keys exist to delete in the first place
		final_applications = []
	if return_final_apps:
		return final_applications


def trim_officer_apps_sent_by_user(time_now, user_id, group_id, my_server=None):
	"""
	Trims officer applications sent by a user (to any public group)

	Trimming policies are explained below:
	CLEANSE 1: no longer than 4 month old applications should remain (be it to any mehfil)
	CLEANSE 2: no more than 4 latest applications to a particular mehfil should remain
	"""
	user_id = str(user_id)
	officer_app_submission_list = OFFICER_APPLICATIONS_SUBMITTED + user_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	all_apps_submitted = my_server.zrange(officer_app_submission_list,0,-1, withscores=True)# all current applications
	group_apps, old_apps = [], []
	for app, submission_time in all_apps_submitted:
		app_data = app.split(":")
		if submission_time < (time_now - OFFICER_APP_ARCHIVE_EXPIRY_TIME):
			old_apps.append(app)# all really old apps will be deleted (be they to any group)
		elif app_data[2] == group_id:
			# save the apps dropped by applier to this particular group (we'll only keep latest 4, delete the rest)
			group_apps.append((app,submission_time))
	if old_apps:
		my_server.zrem(officer_app_submission_list,*old_apps)
		my_server.delete(*old_apps)
	if len(group_apps) > MAX_ARCHIVED_OFFICER_APPS_PER_GROUP:
		apps_sorted_by_submission_time = sorted(group_apps,key=lambda tup: int(tup[1]), reverse=True)
		extra_submissions = apps_sorted_by_submission_time[MAX_ARCHIVED_OFFICER_APPS_PER_GROUP:]
		if extra_submissions:
			submissions_to_remove = [i[0] for i in extra_submissions]
			my_server.zrem(officer_app_submission_list,*submissions_to_remove)
			my_server.delete(*submissions_to_remove)
	my_server.expire(officer_app_submission_list,OFFICER_APP_ARCHIVE_EXPIRY_TIME)# this set dies if there is 4 months of inactivity


def save_officer_application(applier_id, group_id, time_now, payload):
	"""
	Saved data of application dropped by a public group member to become an officer

	'payload' is a dictionary
	"""
	applier_id = str(applier_id)
	my_server = redis.Redis(connection_pool=POOL)
	generic_ttl = my_server.ttl(OFFICER_APPLICATIONS_RATE_LIMITED+applier_id)
	if generic_ttl > 3:
		return generic_ttl, 'generic'
	else:
		specific_ttl = my_server.ttl(RATE_LIMIT_APPLIER_FROM_APPLYING_AGAIN+applier_id+":"+group_id)
		if specific_ttl > 3:
			return specific_ttl, 'specific'
		else:
			idx = my_server.incr(OFFICER_APPLICATION_COUNTER)
			key = OFFICER_APPLICATION_DETAIL+applier_id+":"+group_id+":"+str(idx)
			payload['idx'] = idx# know thy idx (needed when retrieving data)
			pipeline1 = my_server.pipeline()
			pipeline1.setex(key,json.dumps(payload),OFFICER_APP_ARCHIVE_EXPIRY_TIME)
			pipeline1.zadd(OFFICER_APPLICATIONS_RECEIVED+group_id,key,time_now)
			pipeline1.zadd(OFFICER_APPLICATIONS_SUBMITTED+applier_id,key,time_now)
			pipeline1.setex(OFFICER_APPLICATIONS_RATE_LIMITED+applier_id,'1',OFFICER_APPLICATIONS_RATE_LIMIT)# rate limit for 4 days
			pipeline1.delete(CACHED_GROUP_OFFICER_APPLICATIONS+group_id)
			pipeline1.delete(CACHED_USER_OFFICER_APPLICATIONS+applier_id)
			pipeline1.execute()
			
			############################# Trim officer apps sent by this user ############################
			trim_officer_apps_sent_by_user(time_now, applier_id, group_id, my_server=my_server)

			############### Trim officer apps received by group that are older than 3 days ###############
			trim_officer_apps_received_by_group(time_now, group_id, app_keys_and_setting_times=None, \
				return_final_apps=False, my_server=my_server)
			
			################################ Increment officer statistics ################################
			my_server.hincrby(OFFICER_STATISTICS+applier_id,'sb',amount=1)

			return None, ''


def rescind_officer_applications(applier_id, group_id, rejection=False, off_app_idx=None, acceptance=False, my_server=None):
	"""
	Rescind officer application(s) that may be still outstanding
	"""
	applier_id = str(applier_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	apps_submitted = my_server.zrange(OFFICER_APPLICATIONS_SUBMITTED+applier_id,0,-1)
	if apps_submitted:
		apps_for_this_group = []
		for app in apps_submitted:
			gid = app.split(":")[2]
			if gid == group_id:
				apps_for_this_group.append(app)
		if apps_for_this_group:
			# indeed at least one officer application was submitted for this group
			my_server.zrem(OFFICER_APPLICATIONS_RECEIVED+group_id,*apps_for_this_group)
			my_server.delete(CACHED_GROUP_OFFICER_APPLICATIONS+group_id)
	if rejection:
		# since the user was rejected, do not let them apply to this public group again (for two weeks)
		my_server.setex(RATE_LIMIT_APPLIER_FROM_APPLYING_AGAIN+applier_id+":"+group_id,'1',TWO_WEEKS)
	elif acceptance:
		key = OFFICER_APPLICATION_DETAIL+applier_id+":"+group_id+":"+str(off_app_idx)
		ttl = my_server.ttl(key)
		if ttl > 0:
			data = my_server.get(key)
			if data:
				data = json.loads(data)
				data['acc'] = '1'
				my_server.setex(key,json.dumps(data),ttl)# resetting ttl
				my_server.delete(CACHED_USER_OFFICER_APPLICATIONS+applier_id)


def bulk_rescind_officer_applications(applier_ids, group_id, my_server=None):
	"""
	Gets rid of officer applications in bulk

	Called when appliers or applicants are being kicked out via invoking kick_users_from_group()
	"""
	applier_ids = map(str,applier_ids)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	all_current_apps = my_server.zrange(OFFICER_APPLICATIONS_RECEIVED+group_id,0,-1)
	if all_current_apps:
		apps_for_this_group = []
		for app in all_current_apps:
			applicant_id = app.split(":")[1]
			if applicant_id in applier_ids:
				apps_for_this_group.append(app)
		if apps_for_this_group:
			my_server.zrem(OFFICER_APPLICATIONS_RECEIVED+group_id,*apps_for_this_group)
			my_server.delete(CACHED_GROUP_OFFICER_APPLICATIONS+group_id)


def retrieve_single_group_application(applier_id, group_id, app_idx):
	"""
	Retrieve application dropped by a group member for group owner's viewing pleasure

	Group owner can decide to make the member an officer, or reject their application
	"""
	data = redis.Redis(connection_pool=POOL).get(OFFICER_APPLICATION_DETAIL+applier_id+":"+group_id+":"+app_idx)
	if data:
		data = json.loads(data)
		if OFFICER_APPLICATION_EXPIRY_TIME < time.time() - float(data['t']):
			return None
		else:
			return data
	else:
		return None


def retrieve_all_current_applications(group_id=None, user_id=None):
	"""
	Retrieves data of all officer applications a public group has received

	Does the retrieval for a certain group, or for a certain user
	If retrieving for a certain group, trims applications older than 3 days
	"""
	if group_id:
		my_server = redis.Redis(connection_pool=POOL)
		cached_data = my_server.get(CACHED_GROUP_OFFICER_APPLICATIONS+group_id)
		if cached_data:
			return json.loads(cached_data)
		else:
			app_keys_and_setting_times = my_server.zrange(OFFICER_APPLICATIONS_RECEIVED+group_id,0,-1,withscores=True)
			if app_keys_and_setting_times:
				#################### Trim officer apps older than 3 days ####################
				final_applications = trim_officer_apps_received_by_group(time.time(), group_id, app_keys_and_setting_times, \
					True, my_server)
				################ Now retrieve application data post-trimming ################
				if final_applications:
					data = my_server.mget(*final_applications)
					all_applications = []
					for application_json_blob in data:
						all_applications.append(json.loads(application_json_blob))
					#### Cache the resulting data ####
					my_server.setex(CACHED_GROUP_OFFICER_APPLICATIONS+group_id,json.dumps(all_applications),THREE_HOURS)
					return all_applications
				else:
					#### nothing left after trimming!
					my_server.setex(CACHED_GROUP_OFFICER_APPLICATIONS+group_id,json.dumps([]),THREE_HOURS)# cache empty list
					return []
			else:
				my_server.setex(CACHED_GROUP_OFFICER_APPLICATIONS+group_id,json.dumps([]),THREE_HOURS)# cache empty list
				return []
	##########################################################################################################################
	elif user_id:
		user_id = str(user_id)
		my_server = redis.Redis(connection_pool=POOL)
		cached_data = my_server.get(CACHED_USER_OFFICER_APPLICATIONS+user_id)
		if cached_data:
			return json.loads(cached_data)
		else:
			app_keys = my_server.zrevrange(OFFICER_APPLICATIONS_SUBMITTED+user_id,0,-1)
			if app_keys:
				data = my_server.mget(*app_keys)
				all_applications = []
				for application in data:
					all_applications.append(json.loads(application))
				my_server.setex(CACHED_USER_OFFICER_APPLICATIONS+user_id,json.dumps(all_applications),THREE_HOURS)
				return all_applications
			else:
				return []
	else:
		return []


def officer_application_exists(group_id, user_id):
	"""
	Confirm that user_id has indeed submitted an application to become an officer of group_id
	"""
	user_id = str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	app_keys = my_server.zrange(OFFICER_APPLICATIONS_RECEIVED+group_id,0,-1)
	for app in app_keys:
		applier_id = app.split(":")[1]
		if user_id == applier_id:
			return True
	return False


def retrieve_officer_stats(user_id, stat_type=None):
	"""
	Retrieves officership related statistics for a given user_id
	"""
	if stat_type == 'apps_submitted':
		data = redis.Redis(connection_pool=POOL).hget(OFFICER_STATISTICS+str(user_id),'sb')
		data = data if data else 0
		return data
	elif stat_type == 'apps_accepted':
		data = redis.Redis(connection_pool=POOL).hget(OFFICER_STATISTICS+str(user_id),'ac')
		data = data if data else 0
		return data
	elif stat_type == 'currently_officer':
		data = redis.Redis(connection_pool=POOL).zcard(GROUPS_IN_WHICH_USER_IS_OFFICER+str(user_id))
		data = data if data else 0
		return data
	else:
		my_server = redis.Redis(connection_pool=POOL)
		apps_submitted, apps_accepted = my_server.hmget(OFFICER_STATISTICS+str(user_id),'sb','ac')
		num_officers = my_server.zcard(GROUPS_IN_WHICH_USER_IS_OFFICER+str(user_id))
		apps_submitted = apps_submitted if apps_submitted else 0
		apps_accepted = apps_accepted if apps_accepted else 0
		num_officers = num_officers if num_officers else 0
		return apps_submitted, apps_accepted, num_officers

############################# Tracking mehfil visitors ############################


def group_attendance(group_id,visitor_id, time_now):
	"""
	Marking attendance in mehfils (public and private both). Called every time the group is refreshed

	Also useful for carrying out automated deletion of idle mehfils
	"""
	group_id = str(group_id)
	key = GROUP_VISITORS+group_id
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zadd(key,visitor_id,time_now)
	my_server.expire(key,ONE_MONTH)
	### use this to delete idle mehfils ###
	my_server.zadd(UNIVERSAL_GROUP_ATTENDANCE_LIST,group_id,time_now)
	#######################################
	if random.random() < 0.0025 and not my_server.exists(GROUP_VISITOR_PRUNING_LOCK+group_id):
		# every now and then, prune the attendance register's size (and kick and exit trackers)
		# but this approach means inactive_users in groups with low (but not zero) activity may never be pruned (i.e. random.random() < 0.0025 may never run)
		one_and_a_half_month_ago = time_now-ONE_AND_A_HALF_MONTHS
		# prune exit and kick trackers of the group as well
		my_server.zremrangebyscore(GROUP_EXIT_TRACKER+group_id,'-inf',one_and_a_half_month_ago)
		my_server.zremrangebyscore(GROUP_KICK_TRACKER+group_id,'-inf',one_and_a_half_month_ago)
		my_server.setex(GROUP_VISITOR_PRUNING_LOCK+group_id,'1',ONE_DAY)
		return my_server.zrangebyscore(key,'-inf',one_and_a_half_month_ago)
	else:
		return []


def get_attendance(group_id, time_ago='fifteen_mins_ago',withscores=False):
	"""
	Retrieve attendance of user from previous 15 mins, or 24 hours
	"""
	# my_server = redis.Redis(connection_pool=POOL)
	if time_ago == 'fifteen_mins_ago':
		fifteen_mins_ago = time.time() - FIFTEEN_MINS
		if withscores:
			return redis.Redis(connection_pool=POOL).zrevrangebyscore(GROUP_VISITORS+str(group_id), '+inf', fifteen_mins_ago,withscores=True)
		else:
			return redis.Redis(connection_pool=POOL).zrevrangebyscore(GROUP_VISITORS+str(group_id), '+inf', fifteen_mins_ago)
	elif time_ago == 'one_day_ago':	
		one_day_ago = time.time() - ONE_DAY
		if withscores:
			return redis.Redis(connection_pool=POOL).zrevrangebyscore(GROUP_VISITORS+str(group_id), '+inf', one_day_ago, withscores=True)
		else:
			return redis.Redis(connection_pool=POOL).zrevrangebyscore(GROUP_VISITORS+str(group_id), '+inf', one_day_ago)


def cache_group_attendance_data(data,group_id,term='long'):
	"""
	Caching attendance data for group

	The 'short' term caches users who are potential targets to be kicked out
	The 'long' term caches online users used in display_group_users_list() and GroupOnlineKonView()
	"""
	if term == 'short':
		redis.Redis(connection_pool=POOL).setex(GROUP_SHORT_TERM_ATTENDANCE_CACHE+str(group_id),data,MICRO_CACHE_TTL)#micro caching only for 15 seconds
	else:
		redis.Redis(connection_pool=POOL).setex(GROUP_ATTENDANCE_CACHE+str(group_id),data,MICRO_CACHE_TTL)#micro caching only for 15 seconds


def retrieve_cached_attendance_data(group_id, term='long'):
	"""
	Retrieves cached attendance data (if key hasn't expired yet)
	"""
	if term == 'short':
		return redis.Redis(connection_pool=POOL).get(GROUP_SHORT_TERM_ATTENDANCE_CACHE+str(group_id))
	else:
		return redis.Redis(connection_pool=POOL).get(GROUP_ATTENDANCE_CACHE+str(group_id))


def get_latest_presence(group_id, user_id_list, time_now):
	"""
	Returns latest seen times of users in given user_id_list

	Used to show online status dots next to usernames in groups
	"""
	group_id = str(group_id)
	presence_cache_key = GROUP_PRESENCE_CACHE+group_id
	my_server = redis.Redis(connection_pool=POOL)
	cached_presence_data = my_server.get(presence_cache_key)
	if cached_presence_data:
		# return micro-cached presence
		return json.loads(cached_presence_data)
	else:
		# reconstruct presence
		pipeline1 = my_server.pipeline()
		for user_id in user_id_list:
			pipeline1.zscore(GROUP_VISITORS+group_id,user_id)
		result1, pres_dict, counter = pipeline1.execute(), {}, 0
		for user_id in user_id_list:
			if result1[counter]:
				how_old = time_now - float(result1[counter])
				if how_old < GROUP_GREEN_DOT_CUTOFF:
					pres_dict[user_id] = 'green'
				elif how_old < GROUP_IDLE_DOT_CUTOFF:
					pres_dict[user_id] = 'idle'
				else:
					pres_dict[user_id] = 'gone'
			else:
				# zscore doesn't exist - GROUP_VISITORS might have been pruned - consider it 'gone'
				pres_dict[user_id] = 'gone'
			counter += 1
		my_server.setex(presence_cache_key,json.dumps(pres_dict),MICRO_CACHE_TTL)#micro caching only for 15 seconds
		return pres_dict


def invalidate_presence(group_id, my_server=None):
	"""
	Useful when writing new reply in group
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.delete(GROUP_PRESENCE_CACHE+str(group_id))


######################## Caching mehfil messaging data ########################


def cache_mehfil_replies(replies_list_of_dict,group_id):
	"""
	Caches replies shown in a mehfil
	"""
	redis.Redis(connection_pool=POOL).setex(MEHFIL_CACHED_DATA+str(group_id),replies_list_of_dict,ONE_DAY)

def retrieve_cached_mehfil_replies(group_id):
	"""
	Retrieving cached mehfil replies (if they exist)
	"""
	return redis.Redis(connection_pool=POOL).get(MEHFIL_CACHED_DATA+str(group_id))

def invalidate_cached_mehfil_replies(group_id,my_server=None):
	"""
	Removes cached replies from mehfil (e.g. when a new user input comes)
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.delete(MEHFIL_CACHED_DATA+str(group_id))


# def cache_mehfil_list(json_data,user_id):
# 	"""
# 	Micro-caches data shown in a user's mehfil list

# 	'paginated_data' is a dictionary containing all the page(s) data
# 	"""
# 	redis.Redis(connection_pool=POOL).setex(MEHFIL_LIST_CACHED_DATA+str(user_id),json_data,25)# micro-caching for 25 seconds


# def retrieve_cached_mehfil_list(user_id):
# 	"""
# 	Retrieving cached mehfil list for a certain user
# 	"""
# 	return redis.Redis(connection_pool=POOL).get(MEHFIL_LIST_CACHED_DATA+str(user_id))


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


######################## Group creation helper functions ########################


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

######################## Handling group membership and invites ########################


def group_member_exists(group_id, user_id, my_server=None):
	"""
	Check if membership exists for a certain group (for a certain user)
	"""
	if group_id and user_id:
		my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
		return my_server.zscore(GROUP_MEMBERS+str(group_id), user_id)
	else:
		return None

def retrieve_group_joining_time(group_id, user_id, my_server=None):
	"""
	Returns epoch time of when a certain user joined a certain group
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	return my_server.zscore(GROUP_MEMBERS+str(group_id),user_id)


def cache_group_membership_data(data,group_id):
	"""
	Caching group membership data
	"""
	redis.Redis(connection_pool=POOL).setex(GROUP_MEMBERSHIP_CACHE+str(group_id),data,ONE_DAY)


def retrieve_cached_membership_data(group_id):
	"""
	Returns cached group membership data
	"""
	return redis.Redis(connection_pool=POOL).get(GROUP_MEMBERSHIP_CACHE+str(group_id))


def invalidate_group_membership_cache(group_id,my_server=None):
	"""
	Deleting group membership cache
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	return my_server.delete(GROUP_MEMBERSHIP_CACHE+str(group_id))


def retrieve_all_member_ids(group_id,start_idx=0, end_idx=-1,with_num_members=False, with_times=False):
	"""
	Returns all user ids that are members of a mehfil
	"""
	if with_num_members:
		my_server, group_id = redis.Redis(connection_pool=POOL), str(group_id)
		key = GROUP_MEMBERS+group_id
		if with_times:
			return my_server.zrevrange(key,start_idx,end_idx,withscores=True), my_server.zcard(key)
		else:
			return my_server.zrevrange(key,start_idx,end_idx), my_server.zcard(key)
	else:
		if with_times:
			return redis.Redis(connection_pool=POOL).zrevrange(GROUP_MEMBERS+str(group_id),start_idx,end_idx,withscores=True)
		else:
			return redis.Redis(connection_pool=POOL).zrevrange(GROUP_MEMBERS+str(group_id),start_idx,end_idx)


def is_group_member_and_rules_signatory(group_id, user_id):
	"""
	Checks whether a user is a group member and rules signatory

	Used in PublicGroupView()
	"""
	group_id, user_id = str(group_id), str(user_id)
	cache_key = GROUP_MEMBERSHIP_AND_SIGNATORY_CACHE+group_id+":"+user_id
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(cache_key)
	if cached_data:
		return json.loads(cached_data)
	else:
		is_mem = my_server.zscore(GROUP_MEMBERS+group_id,user_id)
		is_sig = my_server.zscore(GROUP_RULES_SIGNATORY+group_id,user_id)
		tup = (is_mem,is_sig)
		my_server.setex(cache_key,json.dumps(tup),ONE_DAY)
		return tup


def invalidate_member_and_signatory_cache(group_id,user_id, my_server=None):
	"""
	Invalidating cached data for group membership and rules signatory (for a given user and group)
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.delete(GROUP_MEMBERSHIP_AND_SIGNATORY_CACHE+str(group_id)+":"+str(user_id))


def update_member_and_signatory_cache(group_id, member_id, is_mem, is_sig, my_server=None):
	"""
	Updating membership and rules signatory cache for given member is given group
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.setex(GROUP_MEMBERSHIP_AND_SIGNATORY_CACHE+str(group_id)+":"+str(member_id),json.dumps((is_mem,is_sig)),ONE_DAY)


def invalidate_all_rule_signatories(group_id, owner_id=None, time_now=None, except_owner=True, my_server=None):
	"""
	Invalidating all signatories of rules (except the owner)
	"""
	group_id = str(group_id)
	key = GROUP_RULES_SIGNATORY+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	all_signatory_ids = my_server.zrange(key,0,-1)
	if all_signatory_ids:
		pipeline1 = my_server.pipeline()
		for signatory_id in all_signatory_ids:
			# invaldiating all caches
			pipeline1.delete(GROUP_MEMBERSHIP_AND_SIGNATORY_CACHE+group_id+":"+str(signatory_id))
		my_server.delete(key)
		pipeline1.execute()
		if except_owner:
			# add back the owner
			my_server.zadd(key,owner_id,time_now)


def create_group_membership_and_rules_signatory(group_id, member_id, time_now, member_join_time=None, is_public=False, member_is_owner=False, my_server=None):
	"""
	Adding user as a group member and rules signatory

	This is useful the first time a user joins (or when group is created)
	It works both for 'public' and 'private' groups
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	# if my_server.exists(RECENTLY_DELETED_GROUP+group_id):
	if not my_server.exists(GROUP+group_id):#group does not exist
		return False
	else:
		key = GROUP_MEMBERS+group_id
		if is_public:
			my_server.zadd(key,member_id,time_now)
			my_server.zadd(GROUP_RULES_SIGNATORY+group_id,member_id,time_now)
			############################################################
			num_mems = my_server.zcard(key)
			my_server.zadd(GROUP_SIZE_LIST,group_id,num_mems)
			# my_server.zincrby(GROUP_SIZE_LIST,group_id,amount=1)# ENABLE THIS LINE AGAIN AFTER 17th Dec 2018 (ensure group_size_list scores are correct)
			############################################################
			if member_join_time:
				# when did the member join Damadam
				my_server.zadd(GROUP_USER_AGE_LIST+group_id,member_id,member_join_time)
			my_server.zrem(KICKED_USERS+group_id,member_id)# in case the user was previously kicked out of the group and is rejoining
			update_member_and_signatory_cache(group_id, member_id, is_mem=time_now, is_sig=time_now, my_server=my_server)
			invalidate_group_membership_cache(group_id,my_server=my_server)
			purge_group_invitation(group_id=group_id, member_id=member_id, is_public=True, my_server=my_server)# incase invite existed, get rid of it
			# removing some relevant micro caches
			my_server.delete(GROUP_SHORT_TERM_ATTENDANCE_CACHE+group_id)#used to show kick out targets
			my_server.delete(CACHED_GROUP_INFO+group_id)# shows cached group info
			############### in case the user previously exited or was kicked out ###############
			my_server.zrem(GROUP_EXIT_TRACKER+group_id,member_id)
			my_server.zrem(GROUP_KICK_TRACKER+group_id,member_id)
			####################################################################################
			update_user_membership_set(member_id, group_id, 'public', time_now, my_server=my_server)
			# ensuring user can't abruptly leave the public mehfil
			my_server.setex(GROUP_EXITING_LOCKED+group_id+":"+str(member_id),'1',PUBLIC_GROUP_EXIT_LOCK)# locked for 1 day
		else:
			# add in a private group
			my_server.zadd(key,member_id,time_now)
			############### in case the user previously exited or was kicked out ###############
			my_server.zrem(GROUP_EXIT_TRACKER+group_id,member_id)
			my_server.zrem(GROUP_KICK_TRACKER+group_id,member_id)
			####################################################################################
			my_server.zadd(GROUP_RULES_SIGNATORY+group_id,member_id,time_now)
			my_server.zrem(KICKED_USERS+group_id,member_id)# in case the user was previously kicked out of the group and is rejoining
			my_server.delete(CACHED_GROUP_INFO+group_id)# shows cached group info
			# ensuring user can't abruptly leave the private mehfil
			my_server.setex(GROUP_EXITING_LOCKED+group_id+":"+str(member_id),'1',PRIVATE_GROUP_EXIT_LOCK)# locked for 40 mins
			purge_group_invitation(group_id=group_id, member_id=member_id, is_public=False, my_server=my_server)# incase invite existed, get rid of it
			invalidate_group_membership_cache(group_id,my_server=my_server)
			update_user_membership_set(member_id, group_id, 'private', time_now, my_server=my_server)
		if member_is_owner:
			update_user_ownership_set(member_id, group_id, time_now, my_server=my_server)
		return True


def exit_group(group_id, user_id, time_now, own_uname='', own_avurl='', is_public=False, inactive=False, rescind_apps=True):
	"""
	Called when left_public_group() or left_private_group() are called (i.e. a member is leaving a group)
	"""
	rescind_offer(group_id=group_id, offerer_id=user_id)
	if is_public:
		remove_group_officer(group_id,user_id)
		if rescind_apps:
			# in some rare cases, we don't want to call rescind apps from here, and instead use bulk_rescind_officer_applications()
			rescind_officer_applications(user_id, group_id)
		delete_specific_users_group_feedback(group_id, [user_id])# accepts user_id in list format
		purge_group_membership(group_id=group_id, member_id=user_id, is_public=True, time_now=time_now)
	else:
		save_group_submission(writer_id=user_id, group_id=group_id, text='leaving group',posting_time=time_now,\
			category='10' if inactive else '6', writer_uname=own_uname, writer_avurl=own_avurl)
		invalidate_cached_mehfil_replies(group_id)
		invalidate_presence(group_id)
		purge_group_membership(group_id=group_id, member_id=user_id, is_public=False, time_now=time_now)
		if inactive:
			main_sentence = own_uname+" ko inactive honay ki wajah se nikal dia gya {0}".format(exact_date(time_now))
			add_to_universal_group_activity(group_id, main_sentence, 'inactive')
		else:
			main_sentence = own_uname+" ne mehfil exit ki at {0}".format(exact_date(time_now))
			add_to_universal_group_activity(group_id, main_sentence, 'exit')


def recently_quit_group(group_id, user_id):
	"""
	Check if user recently quit the group

	Useful in blocking reentry for impulsive users who quit and want to rejoin immediately
	"""
	ttl = redis.Redis(connection_pool=POOL).ttl(GROUP_REENTRY_LOCKED+str(group_id)+":"+str(user_id))
	if ttl > 4:
		return True
	else:
		return False


def can_leave_group(group_id, member_id):
	"""
	Retrieving key that hold a rate limit stopping users from continuously joining and exiting a public/private mehfil
	"""
	ttl = redis.Redis(connection_pool=POOL).ttl(GROUP_EXITING_LOCKED+str(group_id)+":"+str(member_id))
	if ttl > 4:
		return ttl
	else:
		return None


def insert_rules_signatory(group_id, member_id, time_now):
	"""
	Adding user as a rules signatory

	Used in quick_accept_open_group_rules()
	"""
	group_id = str(group_id)
	key = GROUP_RULES_SIGNATORY+group_id
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(key):
		if my_server.zscore(key,member_id):
			# already a signatory - do nothing
			pass
		else:
			# make a signatory
			my_server.zadd(key,member_id,time_now)
			invalidate_member_and_signatory_cache(group_id, member_id, my_server)


def purge_group_membership(group_id, member_id, is_public, time_now):
	"""
	Removing member from group

	Used when user leaves a group themselves (kicking is separate)
	"""
	group_id = str(group_id)
	members_key = GROUP_MEMBERS+group_id
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.zscore(members_key, member_id):
		# member exists
		if is_public:
			pipeline1 = my_server.pipeline()
			pipeline1.zrem(members_key,member_id)
			pipeline1.zrem(GROUP_VISITORS+group_id,member_id)# cleansing group visitors
			########### Track this exit for 45 days ###########
			pipeline1.zadd(GROUP_EXIT_TRACKER+group_id,member_id,time.time())
			###################################################
			pipeline1.zrem(GROUP_RULES_SIGNATORY+group_id,member_id)
			pipeline1.zrem(GROUP_USER_AGE_LIST+group_id,member_id)
			pipeline1.delete(CACHED_GROUP_INFO+group_id)# shows cached group info
			pipeline1.zincrby(GROUP_SIZE_LIST, group_id, amount=-1)
			pipeline1.delete(GROUP_SHORT_TERM_ATTENDANCE_CACHE+group_id)#used to show kick out targets
			pipeline1.execute()
			invalidate_member_and_signatory_cache(group_id, member_id, my_server)
			invalidate_group_membership_cache(group_id,my_server=my_server)
			update_user_membership_set(member_id, group_id, 'public', time_now, remove=True, my_server=my_server)
			update_user_officership_set(member_id, group_id, time_now, remove=True, my_server=my_server)
		else:
			# this is a private group
			pipeline1 = my_server.pipeline()
			pipeline1.zrem(members_key,member_id)
			pipeline1.zrem(GROUP_RULES_SIGNATORY+group_id,member_id)
			pipeline1.zrem(GROUP_VISITORS+group_id,member_id)# cleansing group visitors
			########### Track this exit for 45 days ###########
			pipeline1.zadd(GROUP_EXIT_TRACKER+group_id,member_id,time.time())
			###################################################
			pipeline1.zrem(GROUP_CHATTER+group_id,member_id)# cleansing group chatterers
			pipeline1.zrem(GROUP_PIC_COUNT+group_id,member_id)# cleansing group pic submission set
			pipeline1.delete(CACHED_GROUP_INFO+group_id)# shows cached group info
			pipeline1.delete(CACHED_GROUP_CHATTER+group_id)
			pipeline1.delete(GROUP_SHORT_TERM_ATTENDANCE_CACHE+group_id)#used to show attendance in private mehfil (micro cache)
			pipeline1.execute()
			invalidate_group_membership_cache(group_id,my_server=my_server)
			update_user_membership_set(member_id, group_id, 'private', time_now, remove=True, my_server=my_server)
		my_server.setex(GROUP_REENTRY_LOCKED+group_id+":"+str(member_id),'1',GROUP_REENTRY_LOCK)#15 hours lock


def filter_non_members(user_ids, group_id):
	"""
	Given a list of user_ids, only return group member ids
	"""
	if user_ids:
		user_ids = map(str, user_ids)
		all_members = redis.Redis(connection_pool=POOL).zrange(GROUP_MEMBERS+str(group_id),0,-1)
		member_user_ids = []
		for user_id in user_ids:
			if user_id in all_members:
				member_user_ids.append(user_id)
		return member_user_ids
	return []

def filter_non_recents(user_ids,group_id,time_now):
	"""
	Given a list of user_ids, only return recent user_ids
	"""
	if user_ids:
		user_ids = map(str, user_ids)
		fifteen_mins_ago = time_now - FIFTEEN_MINS
		all_recents = redis.Redis(connection_pool=POOL).zrangebyscore(GROUP_VISITORS+str(group_id),fifteen_mins_ago,'+inf')
		recent_ids = []
		for user_id in user_ids:
			if user_id in all_recents:
				recent_ids.append(user_id)
		return recent_ids
	else:
		return []


def retrieve_outstanding_invite_report(group_id):
	"""
	Retrieves all outstanding invites sent out in a group
	"""
	return redis.Redis(connection_pool=POOL).zrevrange(GROUP_INVITES+str(group_id),0,-1,withscores=True)	


def invite_allowed(group_id,inviter,is_public, inviter_id=None):
	"""
	Lets user know whether they're able to send an invite
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	if is_public:
		if inviter == 'owner':
			if MAX_OWNER_INVITES_PER_PUBLIC_GROUP - my_server.zcard(GROUP_OWNER_INVITES+group_id) > 0:
				return True
			else:
				return False
		elif inviter == 'officer':
			if MAX_OFFICER_INVITES_PER_PUBLIC_GROUP - my_server.zcard(GROUP_OFFICER_INVITES+group_id):
				return True
			else:
				return False
		else:
			False
	else:
		if get_num_group_members(group_id, my_server=my_server) >= PRIVATE_GROUP_MAX_MEMBERSHIP:
			return False, 'mem_overflow'
		elif inviter == 'owner':
			if MAX_OWNER_INVITES_PER_PRIVATE_GROUP - my_server.zcard(PRIVATE_GROUP_OWNER_INVITES+group_id) > 0:
				return True, 'allwd'
			else:
				return False, 'ivt_overflow'
		elif inviter == 'member':
			inviter_id = str(inviter_id)
			if MAX_MEMBER_INVITES_PER_PRIVATE_GROUP - my_server.zcard(PRIVATE_GROUP_MEMBER_INVITES+group_id+":"+inviter_id):
				return True, 'allwd'
			else:
				return False, 'ivt_overflow'
		else:
			False, 'gen_error'



def save_group_invite(group_id, target_id, time_now, is_public, sent_by=None, sent_by_id=None):
	"""
	Save a group invite in its respective sorted sets

	Used for both public and private mehfil invites
	"""
	group_id, target_id = str(group_id), str(target_id)
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zadd(GROUP_INVITES+group_id, target_id, time_now)
	my_server.zadd(USER_INVITES+target_id, group_id, time_now)
	if is_public:
		# processing public mehfil invites
		if sent_by == 'owner':
			my_server.zadd(GROUP_OWNER_INVITES+group_id, target_id, time_now)
		elif sent_by == 'officer':
			my_server.zadd(GROUP_OFFICER_INVITES+group_id, target_id, time_now)
	else:
		# processing private mehfil invites
		if sent_by == 'owner':
			my_server.zadd(PRIVATE_GROUP_OWNER_INVITES+group_id, target_id, time_now)
		elif sent_by == 'member':
			sent_by_id = str(sent_by_id)
			my_server.zadd(PRIVATE_GROUP_MEMBER_INVITES+group_id+":"+sent_by_id, target_id, time_now)
	# set this key and use it to disallow reinviting the same user again and again
	my_server.setex(GROUP_INVITE_LOCK+group_id+":"+target_id,'1',INVITE_LOCK_DURATION)


def reinviting(group_id, target_id):
	"""
	Returns ttl of invite lock if user is being 'reinvited' 

	Unused at the moment
	Should be used in process_private_group_invite() and process_public_group_invite()
	"""
	ttl = redis.Redis(connection_pool=POOL).ttl(GROUP_INVITE_LOCK+str(group_id+":"+str(target_id)))
	if ttl > 4:
		return ttl
	else:
		return None


def group_invite_exists(group_id, user_id):
	"""
	Check if invite exists for a certain group (for a certain user)

	Unused at the moment, should be used in left_private_group()
	"""
	return redis.Redis(connection_pool=POOL).zscore(USER_INVITES+str(user_id), group_id)


def cancel_invite(group_id, member_id, is_public, time_now):
	"""
	Invite cancelation triggered by owner of the open (or closed) group
	"""
	if group_id and member_id:
		group_id = str(group_id)
		my_server = redis.Redis(connection_pool=POOL)
		invite_time = my_server.zscore(GROUP_INVITES+group_id,member_id)
		if invite_time:
			# invite actually exists
			time_elapsed = time_now-float(invite_time)
			if time_elapsed > CANCEL_INVITE_AFTER_TIME_PASSAGE:
				# invite is actually cancelable
				purge_group_invitation(group_id, member_id, is_public=is_public, my_server=my_server)
				return True
			else:
				# not cancelable
				return False
		else:
			# invite was never sent
			return False
	else:
		# incomplete parameters
		return False


def purge_group_invitation(group_id, member_id, is_public=None, my_server=None):#public=False, 
	"""
	Removing invitations associated to a group

	Used when user declines public or private mehfil invite
	Also used if open/closed mehfil owner cancels a 'stale' invite
	Also used if an invitee accepts an invite
	"""
	group_id, member_id = str(group_id), str(member_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.zrem(GROUP_INVITES+group_id, member_id)
	my_server.zrem(USER_INVITES+member_id, group_id)
	if is_public:
		# decrement invite from whoever invited's sorted set
		my_server.zrem(GROUP_OWNER_INVITES+group_id, member_id)
		my_server.zrem(GROUP_OFFICER_INVITES+group_id, member_id)
	else:
		my_server.zrem(PRIVATE_GROUP_OWNER_INVITES+group_id, member_id)
		inviter_ids = my_server.zrange(GROUP_MEMBERS+group_id,0,-1)# all member_ids of private group
		if len(inviter_ids) > 4:
			pipeline1 = my_server.pipeline()
			for inviter_id in inviter_ids:
				pipeline1.zrem(PRIVATE_GROUP_MEMBER_INVITES+group_id+":"+inviter_id, member_id)
			pipeline1.execute()
		else:
			for inviter_id in inviter_ids:
				my_server.zrem(PRIVATE_GROUP_MEMBER_INVITES+group_id+":"+inviter_id, member_id)


def invalidate_all_group_invites(group_id, is_public, my_server=None, member_ids=None):
	"""
	Removes all group invites occuring in user sorted sets

	Useful when deleting the entire group
	"""
	invite_key = GROUP_INVITES+group_id
	if not my_server:
		my_server = redis.Redis(connection_pool=POOL)	
	invited_users_who_didnt_accept = my_server.zrange(invite_key,0,-1)
	pipeline1 = my_server.pipeline()
	for user_id in invited_users_who_didnt_accept:
		pipeline1.zrem(USER_INVITES+user_id,group_id)# removing outstanding invites for invitees since group is being deleted
	pipeline1.delete(invite_key)
	if is_public:
		pipeline1.delete(GROUP_OFFICER_INVITES+group_id)
		pipeline1.delete(GROUP_OWNER_INVITES+group_id)
	else:
		for member_id in member_ids:
			pipeline1.delete(PRIVATE_GROUP_MEMBER_INVITES+group_id+":"+member_id)
		pipeline1.delete(PRIVATE_GROUP_OWNER_INVITES+group_id)
	pipeline1.execute()


def retrieve_closed_group_remaining_invites(unique,user_type,inviter_id):
	"""
	Retrieves number of invites remaining in private mehfil
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(unique)) if unique else None
	if group_id:
		if user_type == 'owner':
			max_invites = MAX_OWNER_INVITES_PER_PRIVATE_GROUP
			invites_used = redis.Redis(connection_pool=POOL).zcard(PRIVATE_GROUP_OWNER_INVITES+group_id)
		elif user_type == 'member':
			max_invites = MAX_MEMBER_INVITES_PER_PRIVATE_GROUP
			invites_used = redis.Redis(connection_pool=POOL).zcard(PRIVATE_GROUP_MEMBER_INVITES+group_id+":"+str(inviter_id))
		else:
			return -1
		return max_invites - invites_used
	else:
		if unique:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=unique)
			except Group.DoesNotExist:
				return -1
			# populate the source data in redis 6
			created_at = convert_to_epoch(group_obj.created_at)
			group_id = str(group_obj.id)
			group_owner_id = str(group_obj.owner_id)
			mapping = {'oi':group_owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':unique,'pii':'1',\
			'tp':group_obj.topic,'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':group_obj.category}# pii is private_invite_instructions flag
			my_server.hmset(GROUP+group_id,mapping)
			my_server.zadd(GROUP_LIST,group_id, created_at)
			my_server.set(GROUP_UUID_TO_ID_MAPPING+str(unique),group_id)
			if user_type == 'owner':
				return MAX_OWNER_INVITES_PER_PRIVATE_GROUP
			elif user_type == 'member':
				return MAX_MEMBER_INVITES_PER_PRIVATE_GROUP
		else:
			return -1



def retrieve_open_group_remaining_invites(unique,user_type):
	"""
	Retrieves number of invites remaining in public mehfil
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(unique)) if unique else None
	if group_id:
		if user_type == 'owner':
			max_invites = MAX_OWNER_INVITES_PER_PUBLIC_GROUP
			invites_used = redis.Redis(connection_pool=POOL).zcard(GROUP_OWNER_INVITES+group_id)
		elif user_type == 'officer':
			max_invites = MAX_OFFICER_INVITES_PER_PUBLIC_GROUP
			invites_used = redis.Redis(connection_pool=POOL).zcard(GROUP_OFFICER_INVITES+group_id)
		else:
			return -1
		return max_invites - invites_used
	else:
		if unique:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=unique)
			except Group.DoesNotExist:
				return -1
			# populate the source data in redis 6
			created_at = convert_to_epoch(group_obj.created_at)
			group_id = str(group_obj.id)
			group_owner_id = str(group_obj.owner_id)
			mapping = {'oi':group_owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':unique,'ii':'1',\
			'tp':group_obj.topic,'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':group_obj.category}# ii is invite_instructions flag
			my_server.hmset(GROUP+group_id,mapping)
			my_server.zadd(GROUP_LIST,group_id, created_at)
			my_server.set(GROUP_UUID_TO_ID_MAPPING+str(unique),group_id)
			if user_type == 'owner':
				return MAX_OWNER_INVITES_PER_PUBLIC_GROUP
			elif user_type == 'officer':
				return MAX_OFFICER_INVITES_PER_PUBLIC_GROUP
		else:
			return -1


def show_public_group_invite_instructions(unique,own_id):
	"""
	Should invite related instructions be shown in public group invite page? 
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(unique)) if unique else None
	if group_id:
		group_owner_id, seen_invite_instr = my_server.hmget(GROUP+group_id,'oi','ii')# 'ii' is invite_instructions
		if group_owner_id == str(own_id):
			instr_type = 'owner'
		elif is_group_officer(group_id,own_id, my_server=my_server):
			instr_type = 'officer'
		else:
			instr_type = None
		if seen_invite_instr:
			show_invite_instr = False
		else:
			show_invite_instr = True
			my_server.hmset(GROUP+group_id,{'ii':'1'})
		return show_invite_instr, instr_type
	else:
		if unique:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=unique)
			except Group.DoesNotExist:
				return None, None
			# populate the source data in redis 6
			created_at = convert_to_epoch(group_obj.created_at)
			group_id = str(group_obj.id)
			group_owner_id = str(group_obj.owner_id)
			mapping = {'oi':group_owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':unique,'ii':'1',\
			'tp':group_obj.topic,'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':group_obj.category}# ii is invite_instructions flag
			my_server.hmset(GROUP+group_id,mapping)
			my_server.zadd(GROUP_LIST,group_id, created_at)
			my_server.set(GROUP_UUID_TO_ID_MAPPING+str(unique),group_id)
			if group_owner_id == str(own_id):
				instr_type = 'owner'
			elif is_group_officer(group_id,own_id, my_server=my_server):
				instr_type = 'officer'
			else:
				instr_type = None
			return True, instr_type
		else:
			return None, None


def show_private_group_invite_instructions(unique,own_id):
	"""
	Should invite related instructions be shown in private group invite page? 
	"""
	my_server = redis.Redis(connection_pool=POOL)
	group_id = my_server.get(GROUP_UUID_TO_ID_MAPPING+str(unique)) if unique else None
	if group_id:
		group_owner_id, seen_invite_instr = my_server.hmget(GROUP+group_id,'oi','pii')# 'pii' is private_invite_instructions
		if group_owner_id == str(own_id):
			instr_type = 'owner'
		elif group_member_exists(group_id, own_id, my_server=my_server):
			instr_type = 'member'
		else:
			instr_type = None
		if seen_invite_instr:
			show_invite_instr = False
		else:
			show_invite_instr = True
			my_server.hmset(GROUP+group_id,{'pii':'1'})
		return show_invite_instr, instr_type
	else:
		if unique:
			#take secondary measures
			try:
				group_obj = Group.objects.get(unique=unique)
			except Group.DoesNotExist:
				return None, None
			# populate the source data in redis 6
			created_at = convert_to_epoch(group_obj.created_at)
			group_id = str(group_obj.id)
			group_owner_id = str(group_obj.owner_id)
			mapping = {'oi':group_owner_id,'oun':group_obj.owner.username,'gi':group_id,'p':group_obj.private,'u':unique,'pii':'1',\
			'tp':group_obj.topic,'r':group_obj.rules,'pics':group_obj.pics_ki_ijazat,'ct':created_at,'grp_categ':group_obj.category}# pii is private_invite_instructions flag
			my_server.hmset(GROUP+group_id,mapping)
			my_server.zadd(GROUP_LIST,group_id, created_at)
			my_server.set(GROUP_UUID_TO_ID_MAPPING+str(unique),group_id)
			if group_owner_id == str(own_id):
				instr_type = 'owner'
			elif group_member_exists(group_id, own_id, my_server=my_server):
				instr_type = 'member'
			else:
				instr_type = None
			return True, instr_type
		else:
			return None, None
			

##################################### Kicking or (un)kicking group users #####################################


def banned_from_group(group_id, user_id):
	"""
	Returns 'True' if user is banned from group, 'False' otherwise

	Used to ensure a kicked user cannot rejoin a public mehfil till their ban lasts
	"""
	return redis.Redis(connection_pool=POOL).exists(KICKED_HASH+str(group_id)+":"+str(user_id))
	

def get_ban_details(group_id, user_id):
	"""
	Return details of the ban the user is experiencing in a public mehfil

	Used to show kicked user why they were kicked out (if they try to rejoin a public mehfil)
	"""
	return redis.Redis(connection_pool=POOL).hgetall(KICKED_HASH+str(group_id)+":"+str(user_id))


def retrieve_kicked_user_ids(group_id, with_details=False, prune_list=False):
	"""
	Retrieves all IDs currently in the kicked list of a group

	Know that some of these bans may have expired since - but the users never joined back hence the list wasn't updated (thus the 'prune_list' parameter is useful)
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	if prune_list:
		pruning_kicked_users_list(group_id, my_server=my_server)
	if with_details:
		# retrieve banned_by and ban_lasts_for details too
		cached_data = my_server.get(CACHED_KICKED_LIST+group_id)
		if cached_data:
			return json.loads(cached_data)
		else:
			kicked_user_ids = my_server.zrevrange(KICKED_USERS+group_id,0,-1)
			if kicked_user_ids:
				credentials = retrieve_bulk_credentials(kicked_user_ids, decode_unames=True)#dictionary of dictionaries is returned
				pipeline1 = my_server.pipeline()
				for kicked_id in kicked_user_ids:
					pipeline1.hgetall(KICKED_HASH+group_id+":"+kicked_id)
				counter, result1 = 0, pipeline1.execute()# result1 is a list of dictionaries
				for kicked_user_id in kicked_user_ids:
					kicked_user_id = int(kicked_user_id)
					result1[counter]['kid'] = kicked_user_id
					result1[counter]['kuname'] = credentials[kicked_user_id]['uname']
					result1[counter]['kavurl'] = credentials[kicked_user_id]['avurl']
					if 'kd' in result1[counter]:
						dur = result1[counter]['kd']
						result1[counter]['kd'] = human_readable_time(int(dur))
					else:
						result1[counter]['kd'] = 'Forever'
					counter += 1
				my_server.setex(CACHED_KICKED_LIST+group_id,json.dumps(result1),ONE_DAY)
				return result1
			else:
				return []
	else:
		return my_server.zrange(KICKED_USERS+group_id,0,-1)



def unkick_users_from_group(group_id, target_ids, time_now, unkicked_by_uname, unkicked_by_id):
	"""
	Unbanning users from given group
	"""
	if not target_ids or not group_id:
		return None, None
	else:
		group_id, unkicked_by_id, target_ids = str(group_id), str(unkicked_by_id), map(str,target_ids)
		my_server = redis.Redis(connection_pool=POOL)
		ttl = my_server.ttl(PUNISHER_RATE_LIMITED+group_id+":"+unkicked_by_id)
		if ttl > 0:
			return ttl, None
		else:
			# do not unkick users who are already unkicked!
			pipeline0 = my_server.pipeline()
			for target_id in target_ids:
				pipeline0.exists(KICKED_HASH+group_id+":"+target_id)
			result0 = pipeline0.execute()
			untouched_target_ids, counter = [], 0
			for target_id in target_ids:
				if result0[counter]:
					untouched_target_ids.append(target_id)# only adding those where kicked_hash:<group_id> exists
				counter += 1
			
			if untouched_target_ids:
				kicked_ids = untouched_target_ids
				
				# remove from kicked list
				my_server.zrem(KICKED_USERS+group_id,*kicked_ids)

				# remove kick hashes, and invite locks (if such locks existed) - so they can be reinvited to the group if need be
				if len(kicked_ids) > 4:
					pipeline1 = my_server.pipeline()
					for kicked_id in kicked_ids:
						pipeline1.delete(KICKED_HASH+group_id+":"+kicked_id)
						pipeline1.delete(GROUP_INVITE_LOCK+group_id+":"+kicked_id)
					pipeline1.execute()
				else:
					for kicked_id in kicked_ids:
						my_server.delete(KICKED_HASH+group_id+":"+kicked_id)
						my_server.delete(GROUP_INVITE_LOCK+group_id+":"+kicked_id)
			
				partial_sentence = nickname_strings(kicked_ids)+" unbanned by "+unkicked_by_uname# avoids ascii problems this way
				main_sentence = partial_sentence+' at {0}'.format(exact_date(time_now))

				# add to group universal history
				activity_id = add_to_universal_group_activity(group_id, main_sentence, history_type='unkick',my_server=my_server)

				# rate limit punisher for a few seconds
				my_server.setex(PUNISHER_RATE_LIMITED+group_id+":"+unkicked_by_id,'1',MICRO_CACHE_TTL)#setting a micro rate limit

				# invalidate cached kicked list
				my_server.delete(CACHED_KICKED_LIST+group_id)

				return None, activity_id
			else:
				# no one left to unban (probably another officer took care of the deed)
				return None, None


def kick_users_from_group(group_id, culprit_ids, time_now, kicked_by_uname, kicked_by_id, kick_duration, is_public):
	"""
	Kicking out users from given group
	"""
	if not culprit_ids or not group_id:
		return None, '', '', None
	else:
		group_id, kicked_by_id, culprit_ids = str(group_id), str(kicked_by_id), map(str,culprit_ids)
		my_server = redis.Redis(connection_pool=POOL)
		ttl = my_server.ttl(PUNISHER_RATE_LIMITED+group_id+":"+kicked_by_id)
		if ttl > 0:
			return ttl, '', '', None
		else:
			# do not kick out users who're already banned!
			pipeline0 = my_server.pipeline()
			for culprit_id in culprit_ids:
				pipeline0.exists(KICKED_HASH+group_id+":"+culprit_id)
			result0, counter = pipeline0.execute(), 0
			untouched_culprit_ids = []
			for culprit_id in culprit_ids:
				if not result0[counter]:
					untouched_culprit_ids.append(culprit_id)
				counter += 1 
			if untouched_culprit_ids:
				
				# only banning those culprits who haven't already been banned (e.g. by other officers)
				culprit_ids = untouched_culprit_ids
				
				if is_public:
					# removing group membership and rules acceptance immediately, getting rid of any relevant cached data
					my_server.zrem(GROUP_MEMBERS+group_id,*culprit_ids)
					my_server.zrem(GROUP_RULES_SIGNATORY+group_id,*culprit_ids)
					for culprit_id in culprit_ids:
						my_server.delete(GROUP_MEMBERSHIP_AND_SIGNATORY_CACHE+group_id+":"+culprit_id)

					# prepare data
					num_culprits = len(culprit_ids)
					duration = get_duration(kick_duration, "kick", "int")
					payload = {'kbuname':kicked_by_uname,'kbid':kicked_by_id,'kt':time_now}
					if duration:
						payload['kd'] = duration
					culprits_and_kicking_times = []
					for culprit_id in culprit_ids:
						culprits_and_kicking_times.append(culprit_id)
						culprits_and_kicking_times.append(time_now)

					# add to kicked list
					my_server.zadd(KICKED_USERS+group_id,*culprits_and_kicking_times)
					
					# create kick hashes
					if num_culprits > 4:
						pipeline1 = my_server.pipeline()
						for culprit_id in culprit_ids:
							kicked_key = KICKED_HASH+group_id+":"+culprit_id
							pipeline1.hmset(kicked_key,payload)
							if duration:
								# add expiry if warranted
								pipeline1.expire(kicked_key,duration)
						pipeline1.execute()
					else:
						for culprit_id in culprit_ids:
							kicked_key = KICKED_HASH+group_id+":"+culprit_id
							my_server.hmset(kicked_key,payload)
							if duration:
								# add expiry if warranted
								my_server.expire(kicked_key,duration)

					# remove culprits from officership (if it existed)
					remove_public_mehfil_officers(culprit_ids,group_id,num_culprits,kicked_by_uname,time_now,my_server=my_server,no_logging=True)
					bulk_update_user_officership_set(culprit_ids, group_id, remove=True, my_server=my_server)

					# remove culprits' membership data
					bulk_update_user_membership_set(culprit_ids, group_id, 'public', remove=True, my_server=my_server)

					# add to universal history available for admin to view
					nicknames, nickname_list = nickname_strings(culprit_ids, with_list=True)
					date_now, string_duration = exact_date(time_now), get_duration(kick_duration, "kick", "string")
					main_sentence = nicknames+" kicked by "+kicked_by_uname+" at {0}. Duration: {1}".format(date_now, string_duration)
					activity_id = add_to_universal_group_activity(group_id,main_sentence, history_type='kick',my_server=my_server)

					pipeline2 = my_server.pipeline()

					# invalidate relevant caches
					pipeline2.delete(CACHED_KICKED_LIST+group_id)#used to show kicked users
					pipeline2.delete(GROUP_SHORT_TERM_ATTENDANCE_CACHE+group_id)#used to show kick-out targets (micro cache)
					for culprit_id in culprit_ids:
						pipeline2.delete(GROUP_EXITING_LOCKED+group_id+":"+culprit_id)#key that rate limits users from immediately leaving
						pipeline2.delete(GROUP_OWNERSHIP_HASH+group_id+":"+culprit_id)#hash that contains any ownership transfer offer made by this user
						pipeline2.zrem(GROUP_OWNERSHIP_REQUEST+group_id,culprit_id)#list that contains pointer to any ownership transfer offer made by this user
						pipeline2.zrem(GROUP_USER_AGE_LIST+group_id,culprit_id)
						pipeline2.zrem(GROUP_VISITORS+group_id,culprit_id)
						pipeline2.zrem(GROUP_VISITORS+group_id,culprit_id)
						########### tracking kicked culprits for 45 days ###########
						pipeline2.zadd(GROUP_KICK_TRACKER+group_id,culprit_id,time_now)
						############################################################
					pipeline2.delete(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)#cached ownership transfer requests for this group
					pipeline2.delete(GROUP_MEMBERSHIP_CACHE+group_id)# shows list of group members
					pipeline2.zincrby(GROUP_SIZE_LIST, group_id, amount=(-1*(num_culprits)))#determines where group lies on 'tiny' - 'huge' spectrum
					pipeline2.delete(CACHED_GROUP_INFO+group_id)# cached group info

					# rate limit punisher for a few seconds
					pipeline2.setex(PUNISHER_RATE_LIMITED+group_id+":"+kicked_by_id,'1',MICRO_CACHE_TTL)#setting a micro rate limit

					pipeline2.execute()

					# rescind officer applications (in bulk) in case they exist
					bulk_rescind_officer_applications(culprit_ids, group_id, my_server)

					# deleting kicked culprits feedback from the mehfil
					delete_specific_users_group_feedback(group_id, culprit_ids, my_server)

					return None, nicknames, nickname_list, activity_id
				else:
					# kicking from a private group
					my_server.zrem(GROUP_MEMBERS+group_id,*culprit_ids)
					my_server.zrem(GROUP_RULES_SIGNATORY+group_id,*culprit_ids)

					# prepare data
					num_culprits = len(culprit_ids)
					duration = get_duration(kick_duration, "kick", "int")
					payload = {'kbuname':kicked_by_uname,'kbid':kicked_by_id,'kt':time_now}
					if duration:
						payload['kd'] = duration
					culprits_and_kicking_times = []
					for culprit_id in culprit_ids:
						culprits_and_kicking_times.append(culprit_id)
						culprits_and_kicking_times.append(time_now)

					# add to kicked list
					my_server.zadd(KICKED_USERS+group_id,*culprits_and_kicking_times)
					
					# create kick hashes
					if num_culprits > 4:
						pipeline1 = my_server.pipeline()
						for culprit_id in culprit_ids:
							kicked_key = KICKED_HASH+group_id+":"+culprit_id
							pipeline1.hmset(kicked_key,payload)
							if duration:
								# add expiry if warranted
								pipeline1.expire(kicked_key,duration)
						pipeline1.execute()
					else:
						for culprit_id in culprit_ids:
							kicked_key = KICKED_HASH+group_id+":"+culprit_id
							my_server.hmset(kicked_key,payload)
							if duration:
								# add expiry if warranted
								my_server.expire(kicked_key,duration)

					# remove culprits' membership data
					bulk_update_user_membership_set(culprit_ids, group_id, 'private', remove=True, my_server=my_server)

					# add to universal history available for admin to view
					nicknames, nickname_list = nickname_strings(culprit_ids, with_list=True)
					date_now, string_duration = exact_date(time_now), get_duration(kick_duration, "kick", "string")
					main_sentence = nicknames+" kicked by "+kicked_by_uname+" at {0}. Duration: {1}".format(date_now, string_duration)
					activity_id = add_to_universal_group_activity(group_id,main_sentence, history_type='kick',my_server=my_server)

					pipeline2 = my_server.pipeline()

					# invalidate relevant caches
					pipeline2.delete(CACHED_KICKED_LIST+group_id)#used to show kicked users
					pipeline2.delete(GROUP_SHORT_TERM_ATTENDANCE_CACHE+group_id)#used to show attendance in private mehfil (micro cache)
					for culprit_id in culprit_ids:
						pipeline2.delete(GROUP_EXITING_LOCKED+group_id+":"+culprit_id)#key that rate limits users from immediately leaving
						pipeline2.delete(GROUP_OWNERSHIP_HASH+group_id+":"+culprit_id)#hash that contains any ownership transfer offer made by this user
						pipeline2.zrem(GROUP_OWNERSHIP_REQUEST+group_id,culprit_id)#list that contains pointer to any ownership transfer offer made by this user
						pipeline2.zrem(GROUP_VISITORS+group_id,culprit_id)# cleansing group visitors
						pipeline2.zrem(GROUP_CHATTER+group_id,culprit_id)# cleansing group chatterers
						pipeline2.zrem(GROUP_PIC_COUNT+group_id,culprit_id)# cleansing group pic submission set
						########### tracking kicked culprits for 45 days ###########
						pipeline2.zadd(GROUP_KICK_TRACKER+group_id,culprit_id,time_now)
						############################################################
					pipeline2.delete(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)#cached ownership transfer requests for this group
					pipeline2.delete(GROUP_MEMBERSHIP_CACHE+group_id)# shows list of group members
					pipeline2.delete(CACHED_GROUP_INFO+group_id)# cached group info
					pipeline2.delete(CACHED_GROUP_CHATTER+group_id)

					# rate limit punisher for a few seconds
					pipeline2.setex(PUNISHER_RATE_LIMITED+group_id+":"+kicked_by_id,'1',TEN_MINS)#setting a rate limit so kicker can't go on a spree

					pipeline2.execute()

					return None, nicknames, nickname_list, activity_id
			else:
				# no unbanned culprits found (e.g. another officer simultanously handled the threat if it was a public group)
				return None, '', '', None


def hide_writers_group_messages(group_id,writer_ids):
	"""
	Hides messages written by writer_ids in given mehfil (identified by group_id)

	Used to hide in bulk when users kicked out via kick_out()
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	displayed_submissions = my_server.zrevrange(GROUP_SUBMISSION_LIST+group_id,0,(MSGS_TO_SHOW_IN_GROUP-1))
	submission_hashes = []
	for submission_id in displayed_submissions:
		submission_hashes.append(GROUP_SUBMISSION_HASH+group_id+":"+submission_id)
	pipeline1 = my_server.pipeline()
	for submission_hash in submission_hashes:
		pipeline1.hmget(submission_hash,'wi','si','c')#writer_id, submission_id, status
	result1 = pipeline1.execute()
	submissions_to_hide, counter = [], 0
	for submission_hash in submission_hashes:
		tup = result1[counter]
		writer_id, submission_id, category = tup[0], tup[1], tup[2]
		if writer_id in writer_ids and category == '0':
			submissions_to_hide.append(GROUP_SUBMISSION_HASH+group_id+":"+submission_id)
		counter += 1
	pipeline2 = my_server.pipeline()
	for submission_key in submissions_to_hide:
		pipeline2.hset(submission_key,'c','3')#setting category to '3' in order to hide
	pipeline2.execute()


def pruning_kicked_users_list(group_id, my_server=None):
	"""
	Removing expired 'kickees' from a group's kicked users' list
	"""
	group_id = str(group_id)
	if not my_server:
		my_server = redis.Redis(connection_pool=POOL)
	kicked_user_ids = my_server.zrange(KICKED_USERS+group_id,0,-1)
	pipeline1 = my_server.pipeline()
	for kicked_user_id in kicked_user_ids:
		pipeline1.exists(KICKED_HASH+group_id+":"+kicked_user_id)
	result1, counter = pipeline1.execute(), 0
	successfully_pruned = False
	pipeline2 = my_server.pipeline()
	for kicked_user_id in kicked_user_ids:
		# remove if kicked user's hash is gone (meaning their punishment expired)
		if not result1[counter]:
			pipeline2.zrem(KICKED_USERS+group_id,kicked_user_id)
			successfully_pruned = True
		counter += 1
	pipeline2.execute()
	if successfully_pruned:
		# invalidate the cached kicked_list' data
		my_server.delete(CACHED_KICKED_LIST+group_id)


def add_unkick_feedback(group_id, activity_id, unkick_feedback):
	"""
	Adds 'unkick' (unbanning) feedback so that original kicker(s) can be appeased
	"""
	if group_id and activity_id and unkick_feedback:
		group_id, activity_id = str(group_id), str(activity_id)
		redis.Redis(connection_pool=POOL).hset(ADMIN_HISTORY_HASH+group_id+":"+activity_id,'reason',unkick_feedback)


def add_kick_feedback(group_id, culprit_ids, activity_id, kick_feedback):
	"""
	Adds kick feedback so that offender recidivism can be prevented
	"""
	if group_id and culprit_ids and activity_id and kick_feedback:
		group_id, activity_id = str(group_id), str(activity_id)
		pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
		for culprit_id in culprit_ids:
			# saving reason for kicked users to read
			pipeline1.hset(KICKED_HASH+group_id+":"+str(culprit_id),'kr',kick_feedback)
		pipeline1.hset(ADMIN_HISTORY_HASH+group_id+":"+activity_id,'reason',kick_feedback)
		pipeline1.execute()


def invalidate_all_kicked_data(group_id, my_server=None):
	"""
	Cleanses all kick related data

	Useful when deleting entire group
	"""
	group_id = str(group_id)
	kicked_key = KICKED_USERS+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	kicked_user_ids = my_server.zrange(kicked_key,0,-1)
	pipeline1 = my_server.pipeline()
	for kicked_user_id in kicked_user_ids:
		pipeline1.delete(KICKED_HASH+group_id+":"+kicked_user_id)
	pipeline1.delete(kicked_key)
	pipeline1.delete(CACHED_KICKED_LIST+group_id)
	pipeline1.execute()


################################### Group administrative activity ###################################

def add_to_universal_group_activity(group_id, main_sentence, history_type, my_server=None):
	"""
	Adding to universal activity shown to group's administrator and other authorized members
	
	Returns activity_id in case feedback is to be attached to a produced admin activity (e.g. post kicking or unkicking)
	"""
	group_id = str(group_id)
	if not my_server:
		my_server = redis.Redis(connection_pool=POOL)
	activity_id = my_server.incr(ADMINISTRATION_ACTIVITY_COUNTER+group_id)
	history_key = GROUP_ADMIN_HISTORY+group_id
	my_server.lpush(history_key,activity_id)
	if history_type in ('kick','unkick'):
		my_server.hmset(ADMIN_HISTORY_HASH+group_id+":"+str(activity_id),{'main':main_sentence,'reason':'','type':history_type})
	elif history_type in ('topic','public_invite','appoint_officer','remove_officer','cancel_public_invite','hide','unhide','transferred','join','exit',\
		'create','private_invite','cancel_private_invite','private_ownership_request','public_ownership_request','cancel_private_ownership_request',\
		'cancel_public_ownership_request','inactive'):
		my_server.hmset(ADMIN_HISTORY_HASH+group_id+":"+str(activity_id),{'main':main_sentence,'type':history_type})
	###### clean up (if required) ######
	if my_server.llen(history_key) >= 159:
		old_activity = my_server.lrange(history_key,140,-1)
		pipeline2 = my_server.pipeline()
		for act_id in old_activity:
			# delete extraneous hashes
			pipeline2.delete(ADMIN_HISTORY_HASH+group_id+":"+act_id)
		pipeline2.ltrim(history_key,0,139)
		pipeline2.execute()
	#####################################
	return activity_id


def retrieve_group_administrative_activity(group_id):
	"""
	Returns all administrative activity that a user can view in a public or private mehfil
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	if random.random() < 0.1:
		# every now and then, prune the kicked users' list too
		pruning_kicked_users_list(group_id, my_server=my_server)#cleansing kicked_users_list (since it's an opportune moment)
	activity_ids = my_server.lrange(GROUP_ADMIN_HISTORY+group_id,0,-1)
	pipeline1 = my_server.pipeline()
	for activity_id in activity_ids:
		pipeline1.hgetall(ADMIN_HISTORY_HASH+group_id+":"+activity_id)
	result1 = pipeline1.execute()
	return [x for x in result1 if x is not None]


def invalidate_all_administrative_activity(group_id, my_server=None):
	"""
	Cleanses administrative activity of a group

	Useful when deleting entire group
	"""
	group_id = str(group_id)
	group_admin_history = GROUP_ADMIN_HISTORY+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	activity_ids = my_server.lrange(group_admin_history,0,-1)
	pipeline1 = my_server.pipeline()
	for activity_id in activity_ids:
		pipeline1.delete(ADMIN_HISTORY_HASH+group_id+":"+activity_id)
	pipeline1.delete(group_admin_history)
	pipeline1.delete(ADMINISTRATION_ACTIVITY_COUNTER+group_id)
	pipeline1.execute()


################################### Group feedback ###################################


def log_open_group_feedback(feedback, feedback_type, group_id, own_id, own_uname, own_avurl, time_now):
	"""
	Logs feedback given by users to public mehfil owners
	"""
	group_id, own_id, feedback_type = str(group_id), str(own_id), str(feedback_type)
	rate_limit_key = FEEDBACK_RATE_LIMITED+group_id+":"+own_id
	my_server = redis.Redis(connection_pool=POOL)
	ttl = my_server.ttl(rate_limit_key)
	if ttl > 2:
		return ttl
	else:
		if feedback_type == '1':
			key = PRAISE_FEEDBACK+group_id
			cache_key = CACHE_PRAISE_FEEDBACK+group_id
		elif feedback_type == '2':
			key = COMPLAINT_FEEDBACK+group_id
			cache_key = CACHE_COMPLAINT_FEEDBACK+group_id
		elif feedback_type == '3':
			key = IDEA_FEEDBACK+group_id
			cache_key = CACHE_IDEA_FEEDBACK+group_id
		payload = {'f':feedback,'ft':feedback_type,'gid':group_id,'uid':own_id,'uname':own_uname,'oau':own_avurl,'tt':time_now}
		id_counter = str(my_server.incr(FEEDBACK_ID+group_id))
		feedback_hash_key = FEEDBACK_HASH+group_id+":"+id_counter
		pipeline1 = my_server.pipeline()
		pipeline1.delete(cache_key)
		pipeline1.zadd(key,id_counter,time_now)
		pipeline1.expire(key,FEEDBACK_TTL)
		pipeline1.hmset(feedback_hash_key,payload)
		pipeline1.expire(feedback_hash_key,FEEDBACK_TTL)
		pipeline1.setex(rate_limit_key,'1',FEEDBACK_RATELIMIT)
		pipeline1.execute()
		return None


def retrieve_open_group_feedback(group_id, feedback_type):
	"""
	Retrieves feedback for mehfil owner to see

	Also cleanses feedback that has expired (two weeks expiry time)
	"""
	group_id, feedback_type = str(group_id), str(feedback_type)
	if feedback_type == '1':
		key = PRAISE_FEEDBACK+group_id
		cache_key = CACHE_PRAISE_FEEDBACK+group_id
	elif feedback_type == '2':
		key = COMPLAINT_FEEDBACK+group_id
		cache_key = CACHE_COMPLAINT_FEEDBACK+group_id
	elif feedback_type == '3':
		key = IDEA_FEEDBACK+group_id
		cache_key = CACHE_IDEA_FEEDBACK+group_id
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(cache_key)
	if cached_data:
		return json.loads(cached_data)
	else:
		feedback_ids = my_server.zrevrange(key,0,-1)
		feedback_hashes = []
		for feedback_id in feedback_ids:
			feedback_hashes.append(FEEDBACK_HASH+group_id+":"+feedback_id)
		if feedback_hashes:
			pipeline1 = my_server.pipeline()
			for feedback_hash in feedback_hashes:
				pipeline1.exists(feedback_hash)
			result1, counter = pipeline1.execute(), 0
			final_data = []
			for feedback_hash in feedback_hashes:
				if result1[counter]:
					final_data.append(my_server.hgetall(feedback_hash))
				else:
					# remove the non existent feedback ID
					my_server.zrem(key,feedback_hash.split(":")[2])
				counter+=1
			if final_data:
				my_server.setex(cache_key,json.dumps(final_data),FEEDBACK_CACHE)
				return final_data
			else:
				return []


def delete_all_group_feedback(group_id, my_server=None):
	"""
	Cleanses all feedback related keys 

	Useful when public mehfil deletion occurs
	"""
	group_id = str(group_id)
	praise_key = PRAISE_FEEDBACK+group_id
	complaint_key = COMPLAINT_FEEDBACK+group_id
	idea_key = IDEA_FEEDBACK+group_id
	
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	praise_ids = my_server.zrange(praise_key,0,-1)	
	complaint_ids = my_server.zrange(complaint_key,0,-1)
	idea_ids = my_server.zrange(idea_key,0,-1)	

	pipeline1 = my_server.pipeline()
	for item_id in praise_ids:
		pipeline1.delete(FEEDBACK_HASH+group_id+":"+item_id)
	pipeline1.delete(praise_key)
	for item_id in complaint_ids:
		pipeline1.delete(FEEDBACK_HASH+group_id+":"+item_id)
	pipeline1.delete(complaint_key)
	for item_id in idea_ids:
		pipeline1.delete(FEEDBACK_HASH+group_id+":"+item_id)
	pipeline1.delete(idea_key)
	pipeline1.delete(FEEDBACK_ID+group_id)
	pipeline1.delete(CACHE_PRAISE_FEEDBACK+group_id)
	pipeline1.delete(CACHE_COMPLAINT_FEEDBACK+group_id)
	pipeline1.delete(CACHE_IDEA_FEEDBACK+group_id)
	pipeline1.execute()
	# feedback rate limit keys are left dangling, but they have a relatively short ttl (3 days)


def delete_specific_group_feedback(group_id, feedback_type):
	"""
	Deletes a specific kind of feedback (e.g. praise, complaint or idea)

	Initiated by mehfil owner if they want to clear up the list
	"""
	group_id = str(group_id)
	if feedback_type == '1':
		key = PRAISE_FEEDBACK+group_id
		cache_key = CACHE_PRAISE_FEEDBACK+group_id
	elif feedback_type == '2':
		key = COMPLAINT_FEEDBACK+group_id
		cache_key = CACHE_COMPLAINT_FEEDBACK+group_id
	elif feedback_type == '3':
		key = IDEA_FEEDBACK+group_id
		cache_key = CACHE_IDEA_FEEDBACK+group_id
	else:
		return False
	my_server = redis.Redis(connection_pool=POOL)
	feedback_ids = my_server.zrange(key,0,-1)
	if feedback_ids:
		pipeline1 = my_server.pipeline()
		for item_id in feedback_ids:
			pipeline1.delete(FEEDBACK_HASH+group_id+":"+item_id)
		pipeline1.delete(key)
		pipeline1.execute()
	my_server.delete(cache_key)# not included in pipeline in case the key we're doing 'zrange' on has expired (thus produces []), but the cached key still lives
	return True


def delete_specific_users_group_feedback(group_id, feedback_giver_ids, my_server=None):
	"""
	Removes feedback of specific users, given to a particular public group's owner

	Used when a feedback_giver(s) exit the group or the bulk of them are kicked out
	Accepts feedback_giver_ids in list format
	"""
	group_id, feedback_giver_ids = str(group_id), map(str, feedback_giver_ids)
	praise_key = PRAISE_FEEDBACK+group_id
	complaint_key = COMPLAINT_FEEDBACK+group_id
	idea_key = IDEA_FEEDBACK+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	praise_data = my_server.zrange(praise_key,0,-1)
	complaint_data = my_server.zrange(complaint_key,0,-1)
	idea_data = my_server.zrange(idea_key,0,-1)

	feedback_hash_keys = []
	for praise_counter in praise_data:
		feedback_hash_key = FEEDBACK_HASH+group_id+":"+praise_counter
		feedback_hash_keys.append(feedback_hash_key)
	for complaint_counter in complaint_data:
		feedback_hash_key = FEEDBACK_HASH+group_id+":"+complaint_counter
		feedback_hash_keys.append(feedback_hash_key)
	for idea_counter in idea_data:
		feedback_hash_key = FEEDBACK_HASH+group_id+":"+idea_counter
		feedback_hash_keys.append(feedback_hash_key)

	pipeline1 = my_server.pipeline()
	for feedback_hash_key in feedback_hash_keys:
		pipeline1.hget(feedback_hash_key,'uid')
	result1 = pipeline1.execute()

	counter, feedback_givers_feedback = 0, []

	for praise_counter in praise_data:
		if result1[counter] in feedback_giver_ids:
			feedback_givers_feedback.append(FEEDBACK_HASH+group_id+":"+praise_counter)
		counter += 1
	for complaint_counter in complaint_data:
		if result1[counter] in feedback_giver_ids:
			feedback_givers_feedback.append(FEEDBACK_HASH+group_id+":"+complaint_counter)
		counter += 1
	for idea_counter in idea_data:
		if result1[counter] in feedback_giver_ids:
			feedback_givers_feedback.append(FEEDBACK_HASH+group_id+":"+idea_counter)
		counter += 1

	if feedback_givers_feedback:
		pipeline2 = my_server.pipeline()
		for feedback_key in feedback_givers_feedback:
			pipeline2.delete(feedback_key)
		pipeline2.execute()

		my_server.delete(CACHE_PRAISE_FEEDBACK+group_id)
		my_server.delete(CACHE_COMPLAINT_FEEDBACK+group_id)
		my_server.delete(CACHE_IDEA_FEEDBACK+group_id)


################################### Group ownership transfer ###################################


def submit_group_ownership_request(group_id, submitter_id, submitter_uname, submitter_avurl, time_now, points_offered=0):
	"""
	Submits group ownership request (works both for public and private groups)
	"""
	group_id, submitter_id = str(group_id),str(submitter_id)
	my_server = redis.Redis(connection_pool=POOL)
	st_ttl = my_server.ttl(GROUP_OWNERSHIP_TRANSFER_REQUEST_RATE_LIMIT+group_id+":"+submitter_id)
	if st_ttl:
		# short-term rate limit
		return st_ttl, 'short'
	else:
		lt_ttl = my_server.ttl(GROUP_TRANSACTIONS_RATE_LIMITED+submitter_id)
		if lt_ttl:
			# long-term rate limit
			return lt_ttl, 'long'
		else:
			# process request here (this over-writes a previously sent request - if such a request exists)
			list_key = GROUP_OWNERSHIP_REQUEST+group_id
			hash_key = GROUP_OWNERSHIP_HASH+group_id+":"+submitter_id
			pipeline1 = my_server.pipeline()
			pipeline1.zadd(list_key,submitter_id,time_now)
			pipeline1.hmset(hash_key,{'sid':submitter_id,'suname':submitter_uname,'savurl':submitter_avurl,'t':time_now,'pts':points_offered,'gid':group_id})
			pipeline1.expire(list_key,THREE_DAYS)
			pipeline1.expire(hash_key,THREE_DAYS)
			pipeline1.setex(GROUP_OWNERSHIP_TRANSFER_REQUEST_RATE_LIMIT+group_id+":"+submitter_id,'1',FOLLOW_UP_REQUEST_RATE_LIMIT)
			pipeline1.delete(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)
			pipeline1.execute()
			return None, None


def group_ownership_transfer_blocked_by_rate_limit(group_id, owner_id, requestor_id):
	"""
	Checks if a transaction can be processed 

	Useful when a mehfil members initiates a mehfil transfer request
	Also useful when a mehfil owner accepts a mehfil transfer request
	"""
	group_id, owner_id, requestor_id = str(group_id),str(owner_id),str(requestor_id)
	my_server = redis.Redis(connection_pool=POOL)
	# are the involved parties rate limited in any way?
	owner_ttl = my_server.ttl(GROUP_TRANSACTIONS_RATE_LIMITED+owner_id)
	requestor_ttl = my_server.ttl(GROUP_TRANSACTIONS_RATE_LIMITED+requestor_id)
	if owner_ttl or requestor_ttl:
		# do not allow transaction request to be processed, return the larger TTL to be displayed
		owner_ttl = owner_ttl if owner_ttl else 0
		requestor_ttl = requestor_ttl if requestor_ttl else 0
		if owner_ttl > requestor_ttl:
			return owner_ttl, 'owner'
		else:
			return requestor_ttl, 'requestor'
	else:
		# allow transaction request to be processed
		return None, None


def accept_group_ownership_transfer_request(group_id, group_uuid, owner_id, own_uname, requestor_id, requestor_uname, time_now, points_offered=0, \
	is_public=True):
	"""
	Ownership transfer is processed here (for redis6)
	"""
	group_id, owner_id, requestor_id = str(group_id),str(owner_id),str(requestor_id)
	my_server = redis.Redis(connection_pool=POOL)

	# set new owner id ('oi' is owner id,'oun' is owner_uname,'pp' is points_paid, 'tos' is time_of_sale)
	my_server.hmset(GROUP+group_id,{'oi':requestor_id,'pp':points_offered,'oun':requestor_uname,'tos':time_now})

	# process relevant public mehfil operations
	if is_public:
		main_sentence = own_uname+" sold mehfil ownership to "+requestor_uname+" for {0} points, at {1}".format(points_offered, exact_date(time_now))# avoids ascii problems this way
		# remove any affected officership
		remove_group_officer(group_id,requestor_id,my_server=my_server)
		remove_group_officer(group_id,owner_id,my_server=my_server)
		# remove feedback received by old owner (it might contain personal data)
		delete_all_group_feedback(group_id, my_server=my_server)
	else:
		main_sentence = own_uname+" transferred mehfil ownership to "+requestor_uname+" at {0}".format(exact_date(time_now))

	# add to activity log
	add_to_universal_group_activity(group_id, main_sentence, history_type='transferred',my_server=my_server)

	# allow incoming owner to immediately change topic ('rules' lock would be unapplicable anyway since it's user specific)
	invalidate_topic_changing_lock(group_uuid)

	# delete requestor's rate-limit for requesting ownership for this group. It's not relevant anymore
	my_server.delete(GROUP_OWNERSHIP_TRANSFER_REQUEST_RATE_LIMIT+group_id+":"+requestor_id)

	# cleanse cached 'required' data that helps in rendering and posting to a mehfil
	invalidate_cached_group_reqd_data(group_id, my_server=my_server)

	# cleanse the outstanding ownership requests list
	reject_all_outstanding_requests(group_id, my_server=my_server)

	# cleanse oustanding officership requests (along with rate limits)
	cleanse_all_officer_apps_received_by_group(group_id, with_rate_limits=True, my_server=my_server)

	# update relevant user sets
	update_user_ownership_set(owner_id, group_id, remove=True, my_server=my_server)
	update_user_ownership_set(requestor_id, group_id, time_now, my_server=my_server)
	update_user_officership_set(requestor_id, group_id, time_now, remove=True, my_server=my_server)

	# set relevant rate limits on both owner_id and requester_id
	my_server.setex(GROUP_TRANSACTIONS_RATE_LIMITED+owner_id,'1',GROUP_TRANSACTION_RATE_LIMIT)
	my_server.setex(GROUP_TRANSACTIONS_RATE_LIMITED+requestor_id,'1',GROUP_TRANSACTION_RATE_LIMIT)

	# finally, reset cached group info
	my_server.delete(CACHED_GROUP_INFO+group_id)



def rescind_offer(group_id, offerer_id):
	"""
	Rescind an offer of group transfer placed by offerer_id

	Useful when offerer is kicked out of group, leaves it, or deliberately rescinds offer
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	my_server.delete(GROUP_OWNERSHIP_HASH+group_id+":"+str(offerer_id))
	my_server.zrem(GROUP_OWNERSHIP_REQUEST+group_id,offerer_id)
	my_server.delete(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)


def retrieve_offer_details(group_id, offerer_id):
	"""
	Retrieve a single user's offer

	Useful when finalzing the deal
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	offer = my_server.hgetall(GROUP_OWNERSHIP_HASH+group_id+":"+str(offerer_id))
	if offer:
		return offer
	else:
		# offer hash has probably expired, remove from list
		my_server.zrem(GROUP_OWNERSHIP_REQUEST+group_id,offerer_id)
		my_server.delete(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)
		return None

def get_prev_request(group_id,own_id):
	"""
	Shows the requestor their previous request sent to a certain group
	"""
	return redis.Redis(connection_pool=POOL).hgetall(GROUP_OWNERSHIP_HASH+str(group_id)+":"+str(own_id))


def retrieve_outstanding_requests(group_id):
	"""
	Returns any ownership requests received by a group
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	final_data = my_server.get(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)
	if final_data:
		return json.loads(final_data)
	else:
		list_key, final_data = GROUP_OWNERSHIP_REQUEST+group_id, []
		submitter_ids = my_server.zrevrange(list_key,0,-1)
		if submitter_ids:
			pipeline1, request_dict = my_server.pipeline(), {}
			for submitter_id in submitter_ids:
				request_key = GROUP_OWNERSHIP_HASH+group_id+":"+submitter_id
				pipeline1.exists(request_key)
				request_dict[submitter_id] = request_key 
			result1,counter = pipeline1.execute(),0
			for submitter_id in submitter_ids:
				if result1[counter]:
					# it exists, show it in the final data
					final_data.append(my_server.hgetall(request_dict[submitter_id]))
				else:
					# hash has expire, remove data from the original list
					my_server.zrem(list_key,submitter_id)
				counter += 1
			if final_data:
				my_server.setex(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id,json.dumps(final_data),FORTY_MINS)
		return final_data


def ownership_request_rate_limit(group_id, requestor_id):
	"""
	Rate limits sending another request to this same mehfil owner
	"""
	return redis.Redis(connection_pool=POOL).ttl(GROUP_OWNERSHIP_TRANSFER_REQUEST_RATE_LIMIT+str(group_id)+":"+str(requestor_id))


def is_ownership_request_legit(group_id, requestor_id):
	"""
	Retrieves whether an offer actually exists (i.e. is legit)

	Useful for times the owner is about to make a decision on mehfil transfer
	"""
	if group_id and requestor_id:
		return redis.Redis(connection_pool=POOL).exists(GROUP_OWNERSHIP_HASH+str(group_id)+":"+str(requestor_id))
	else:
		return None


def reject_all_outstanding_requests(group_id, my_server=None):
	"""
	Basically resets the list of outstanding requests (owner driven)

	Used by mehfil owner to purge the list
	Does not delete rate-limits (that's the key difference from delete_ownership_transfer_data())
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	list_key = GROUP_OWNERSHIP_REQUEST+group_id
	all_submitters = my_server.zrange(list_key,0,-1)
	pipeline1 = my_server.pipeline()
	for submitter_id in all_submitters:
		pipeline1.delete(GROUP_OWNERSHIP_HASH+group_id+":"+submitter_id)
	pipeline1.delete(list_key)
	pipeline1.delete(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)
	pipeline1.execute()


def delete_ownership_transfer_data(group_id, my_server=None):
	"""
	Deletes all ownership transfer related data related to a public or private mehfil

	Used in permanently_delete_group()
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	list_key = GROUP_OWNERSHIP_REQUEST+group_id
	all_submitters = my_server.zrange(list_key,0,-1)
	pipeline1 = my_server.pipeline()
	for submitter_id in all_submitters:
		pipeline1.delete(GROUP_OWNERSHIP_HASH+group_id+":"+submitter_id)
		pipeline1.delete(GROUP_OWNERSHIP_TRANSFER_REQUEST_RATE_LIMIT+group_id+":"+submitter_id)
	pipeline1.delete(list_key)
	pipeline1.delete(OWNERSHIP_TRANSFER_REQUEST_CACHE+group_id)
	pipeline1.execute()

#################################### Populating and retrieving group info ####################################


def get_group_size_string(group_id, num_members_in_grp, my_server=None):
	"""
	Returns a size estimate based on num of members in a group and how it compares to other existing groups

	A percentile based technique is employed
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	num_grps = my_server.zcard(GROUP_SIZE_LIST)
	if num_grps > 10:
		# we have meaningful amount of data
		rank = my_server.zrank(GROUP_SIZE_LIST,group_id)
		percentage_of_groups_beaten = (rank*1.0)/num_grps
		if percentage_of_groups_beaten > 0.97 and num_members_in_grp > 300:
			# a 'big' group has to both beat almost all other groups and have more than 300 members to get to "very big"
			return 'huge'
		elif percentage_of_groups_beaten > 0.92 and num_members_in_grp > 155:
			# a group that doesn't have > 155 members will still be medium even if it beats more than 92% of other groups
			return 'big'
		elif percentage_of_groups_beaten > 0.73 and num_members_in_grp > 80:
			# a group with < 80 members will be 'small' even if it beats 73% of other groups
			return 'medium'
		elif percentage_of_groups_beaten > 0.50 and num_members_in_grp > 35:
			# a group > 35 members but beating less than 50% of other groups will still be considered 'tiny'
			return 'small'
		else:
			return 'tiny'
	else:
		# when a small number of groups created, consider all of them "small"
		if num_members_in_grp > 300:
			return 'huge'
		elif num_members_in_grp > 155:
			return 'big'
		elif num_members_in_grp > 80:
			return 'medium'
		elif num_members_in_grp > 35:
			return 'small' 
		else:
			return 'tiny'
	

def get_median_member_age(group_id, my_server=None):
	"""
	Calculates median age of members in a group
	"""
	group_id = str(group_id)
	key = GROUP_USER_AGE_LIST+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	num_ele = my_server.zcard(key)
	if num_ele:
		if num_ele % 2 == 0:
			# even num
			half = num_ele/2
			members_and_values = my_server.zrange(key,half-1,half,withscores=True)
			median = (float(members_and_values[0][1]) + float(members_and_values[1][1]))/2
		else:
			# odd num
			half = (num_ele-1)/2
			median = my_server.zrange(key,half,half,withscores=True)[0][1]
		return median
	else:
		return ''

def get_num_group_members(group_id, my_server=None):
	"""
	Returns number of members in a given group
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	return my_server.zcard(GROUP_MEMBERS+str(group_id))


def get_reported_group_info(group_id):
	"""
	Retrieves group info to be shown when a defender is deciding the punishment of a reported mehfil

	Shows group creation time, num members, size string, popularity rank (if any)
	"""
	if group_id:
		group_id = str(group_id)
		my_server = redis.Redis(connection_pool=POOL)
		data = my_server.get(CACHED_REPORTED_GROUP_INFO+group_id)
		if data:
			return json.loads(data)
		else:
			creation_time = my_server.hget(GROUP+group_id,'ct')
			num_members = get_num_group_members(group_id,my_server)#total group members
			size = get_group_size_string(group_id, num_members, my_server)
			popularity_rank = my_server.zrevrank(GROUP_BIWEEKLY_STICKINESS,group_id)
			data = {'ct':creation_time,'m':num_members,'sz':size}
			if popularity_rank:
				# this group is ranked!
				popularity_rank += 1# add 1 since ranks are zero based
				data['pr'] = popularity_rank
			my_server.setex(CACHED_REPORTED_GROUP_INFO+group_id,json.dumps(data),TEN_MINS)
			return data
	else:
		return None


def get_group_info(group_id, is_public):
	"""
	Retrieves group info (works for both public and private mehfils)
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	data = my_server.get(CACHED_GROUP_INFO+group_id)
	if data:
		return json.loads(data)
	else:
		group_key = GROUP+group_id
		if is_public:
			# getting all the stats

			creation_epoch_time, owner_uname, price_paid, epoch_time_of_buying = my_server.hmget(group_key,'ct','oun','pp','tos')
			num_members = get_num_group_members(group_id,my_server)#total group members
			# new members in the last 7 days
			one_week_ago = time.time() - ONE_WEEK
			last_seven_day_joiners = my_server.zrevrangebyscore(GROUP_MEMBERS+group_id,'+inf', one_week_ago)#ZREVRANGEBYSCORE key max min
			num_last_seven_day_joiners = len(last_seven_day_joiners) if last_seven_day_joiners else 0
			
			# visiting members in the last 24 hours (kicked out or exited ex-members don't show)
			last_one_day_visitors = my_server.zrevrangebyscore(GROUP_VISITORS+group_id,'+inf', time.time() - ONE_DAY)#ZREVRANGEBYSCORE key max min
			num_last_one_day_visitors = len(last_one_day_visitors) if last_one_day_visitors else 0
			# num officers
			num_officers = my_server.zcard(GROUP_OFFICER_LIST+group_id)
			# mehfil size
			size = get_group_size_string(group_id, num_members, my_server)
			# get average signup age of members (in epoch time)
			median_age = get_median_member_age(group_id, my_server)
			# packing all data into a dictionary
			payload = {'ct':creation_epoch_time,'oun':owner_uname.decode('utf-8'),'pp':price_paid,'tos':epoch_time_of_buying,'m':num_members,\
			'24v':num_last_one_day_visitors,'o':num_officers,'tp':my_server.hget(group_key,'tp').decode('utf-8'), 'sz':size,'ma':median_age, \
			'bought':True if price_paid else False,'7nm':num_last_seven_day_joiners}
			
			my_server.setex(CACHED_GROUP_INFO+group_id,json.dumps(payload),TEN_MINS)

		else:
			# private group:
			chatter_key = GROUP_CHATTER+group_id
			# 1) all members, alongwith joining times
			num_members = get_num_group_members(group_id,my_server)#total group members
			# 2) & 3) mehfil creation time & mehfil owner
			creation_epoch_time, owner_uname = my_server.hmget(group_key,'ct','oun')
			# 5) recent topics
			latest_topic_setting_user_and_time = my_server.zrevrange(GROUP_TOPIC_LIST+group_id,0,0,withscores=True)
			latest_topic_setting_time = latest_topic_setting_user_and_time[0][1] if latest_topic_setting_user_and_time else ''
			how_many_chatters = my_server.zcard(chatter_key)
			if how_many_chatters > 1:
				# 6) most silent user
				silent_user_id = my_server.zrange(chatter_key,0, 0)
				silent_uname = retrieve_uname(silent_user_id[0],decode=True) if silent_user_id else None
				# 7) most talkative user
				talkative_user_id = my_server.zrevrange(chatter_key,0,0)
				talkative_uname = retrieve_uname(talkative_user_id[0],decode=True) if talkative_user_id else None
			else:
				silent_uname, talkative_uname = None, None
			# 8) all visitors, alongwith visiting times (kicked out or exited ex-members don't show)
			last_one_day_visitors = my_server.zrevrangebyscore(GROUP_VISITORS+group_id,'+inf', time.time() - ONE_DAY)#ZREVRANGEBYSCORE key max min
			num_last_one_day_visitors = len(last_one_day_visitors) if last_one_day_visitors else 0
			# 9) user sharing most pics
			pic_sharer_uname = retrieve_biggest_pic_sharer_in_group(group_id)

			payload = {'ct':creation_epoch_time,'oun':owner_uname.decode('utf-8'),'m':num_members,'24v':num_last_one_day_visitors,\
			'tun':talkative_uname,'psun':pic_sharer_uname,'tpt':latest_topic_setting_time,'sun':silent_uname}

			my_server.setex(CACHED_GROUP_INFO+group_id,json.dumps(payload),TEN_MINS)

		return payload


###################################### Freeze group functionality #####################################

def is_membership_frozen(group_id):
	"""
	Retrieve whether group deletion is frozen
	"""
	if redis.Redis(connection_pool=POOL).exists(GROUP_MEMBERSHIP_FROZEN+str(group_id)):
		return True
	else:
		return False


def is_deletion_frozen(group_id):
	"""
	Retrieve whether group deletion is frozen
	"""
	if redis.Redis(connection_pool=POOL).exists(GROUP_DELETION_FROZEN+str(group_id)):
		return True
	else:
		return False


def is_ownership_transfer_frozen(group_id):
	"""
	Retrieve whether group ownership transfer is frozen
	"""
	if redis.Redis(connection_pool=POOL).exists(GROUP_OWNERSHIP_TRANSFER_FROZEN+str(group_id)):
		return True
	else:
		return False


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


def unfreeze_deletion(group_id, my_server=None):
	"""
	Unfreeze deletion functionality once group's report is resolved
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	pipeline1.delete(GROUP_DELETION_FROZEN+group_id)
	pipeline1.delete(GROUP_OWNERSHIP_TRANSFER_FROZEN+group_id)
	pipeline1.delete(GROUP_TOPIC_CHANGE_FROZEN+group_id)
	pipeline1.delete(GROUP_RULES_CHANGE_FROZEN+group_id)
	pipeline1.delete(GROUP_MEMBERSHIP_FROZEN+group_id)
	pipeline1.execute()


def freeze_reported_group_functionality(group_id, payload_type):
	"""
	Freezes public group topic change (or rule change), ownership transfer, and delete group functionality

	Useful when a group is reported, and we want to maintain its state so that the evidence isn't erased
	'payload_type' contains 'topic' or 'rules'
	"""
	group_id = str(group_id)
	pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
	pipeline1.setex(GROUP_MEMBERSHIP_FROZEN+group_id,payload_type,TWO_WEEKS)
	pipeline1.setex(GROUP_DELETION_FROZEN+group_id,'1',TWO_WEEKS)
	pipeline1.setex(GROUP_OWNERSHIP_TRANSFER_FROZEN+group_id,'1',TWO_WEEKS)
	pipeline1.setex(GROUP_TOPIC_CHANGE_FROZEN+group_id,'1',TWO_WEEKS)
	pipeline1.setex(GROUP_RULES_CHANGE_FROZEN+group_id,'1',TWO_WEEKS)
	pipeline1.execute()

###################################### Delete group data #####################################


def permanently_delete_group(group_id, group_type, return_member_ids=False):
	"""
	Permanently delete all group data residing in redis6 (including group meta data)
	"""
	group_id = str(group_id)
	group_key = GROUP+group_id
	my_server = redis.Redis(connection_pool=POOL)
	group_uuid, owner_id = my_server.hmget(group_key,'u','oi')#fetching group's uuid and owner_id
	member_ids = my_server.zrange(GROUP_MEMBERS+group_id,0,-1)
	if group_type == 'public':
		# handling deletion for public mehfils
		officer_ids = retrieve_all_officers(group_id,only_ids=True)
		all_submission_ids = my_server.zrange(GROUP_SUBMISSION_LIST+group_id,0,-1)
		pipeline1 = my_server.pipeline()
		for submission_id in all_submission_ids:
			pipeline1.delete(GROUP_SUBMISSION_HASH+group_id+":"+submission_id)
		pipeline1.delete(GROUP_SUBMISSION_LIST+group_id)
		pipeline1.delete(SUBMISSION_COUNTER+group_id)
		pipeline1.delete(GROUP_ATTENDANCE_CACHE+group_id)
		pipeline1.delete(GROUP_SHORT_TERM_ATTENDANCE_CACHE+group_id)
		pipeline1.delete(GROUP_MEMBERS+group_id)
		pipeline1.zrem(GROUP_LIST,group_id)
		pipeline1.zrem(GROUP_SIZE_LIST,group_id)
		pipeline1.zrem(UNIVERSAL_GROUP_ATTENDANCE_LIST,group_id)
		# removing group from stickiness ranking & removing cached ranked groups #
		pipeline1.zrem(GROUP_BIWEEKLY_STICKINESS,group_id)
		##########################################################################
		# pipeline1.zrem(OFFICER_APP_TRIM_TIME_OF_GROUPS,group_id)
		pipeline1.delete(CACHED_USER_OWNERSHIP_PUBLIC_GROUPS+owner_id)
		pipeline1.delete(GROUP_USER_AGE_LIST+group_id)
		pipeline1.delete(CACHED_GROUP_INFO+group_id)
		pipeline1.delete(GROUP_VISITORS+group_id)
		pipeline1.delete(GROUP_KICK_TRACKER+group_id)
		pipeline1.delete(GROUP_EXIT_TRACKER+group_id)
		pipeline1.delete(GROUP_UUID_TO_ID_MAPPING+group_uuid)
		pipeline1.delete(group_key)
		pipeline1.execute()
		invalidate_cached_ranked_groups(my_server=my_server)
		invalidate_group_membership_cache(group_id,my_server=my_server)
		bulk_update_user_membership_set(member_ids, group_id, 'public', remove=True, my_server=my_server)
		bulk_update_user_officership_set(officer_ids, group_id, remove=True, my_server=my_server)
		delete_group_officers(group_id, my_server=my_server)
		cleanse_all_officer_apps_received_by_group(group_id, my_server=my_server)
		update_user_ownership_set(owner_id, group_id, remove=True, my_server=my_server)
		delete_ownership_transfer_data(group_id, my_server=my_server)
		invalidate_all_group_invites(group_id, is_public=True, my_server=my_server)
		invalidate_all_kicked_data(group_id, my_server=my_server)
		invalidate_all_administrative_activity(group_id, my_server=my_server)
		invalidate_cached_mehfil_replies(group_id,my_server=my_server)
		invalidate_all_rule_signatories(group_id, except_owner=False, my_server=my_server)
		invalidate_presence(group_id, my_server=my_server)
		delete_all_group_feedback(group_id, my_server=my_server)
		invalidate_cached_group_reqd_data(group_id, my_server=my_server)
		unfreeze_deletion(group_id, my_server=my_server)
		my_server.setex(RECENTLY_DELETED_GROUP+group_id,'1',ONE_MONTH)
	else:
		# handling deletion for private mehfils
		all_submission_ids = my_server.zrange(GROUP_SUBMISSION_LIST+group_id,0,-1)
		topic_ids = my_server.zrange(GROUP_TOPIC_LIST+group_id,0,-1)#checked
		pipeline1 = my_server.pipeline()
		for submission_id in all_submission_ids:
			pipeline1.delete(GROUP_SUBMISSION_HASH+group_id+":"+submission_id)
		pipeline1.delete(GROUP_SUBMISSION_LIST+group_id)
		pipeline1.delete(SUBMISSION_COUNTER+group_id)
		pipeline1.delete(GROUP_ATTENDANCE_CACHE+group_id)
		pipeline1.delete(GROUP_MEMBERS+group_id)
		pipeline1.zrem(GROUP_LIST,group_id)
		pipeline1.zrem(UNIVERSAL_GROUP_ATTENDANCE_LIST,group_id)
		pipeline1.delete(GROUP_CHATTER+group_id)
		pipeline1.delete(GROUP_PIC_COUNT+group_id)
		pipeline1.delete(GROUP_TOPIC_COUNTER+group_id)
		for topic_id in topic_ids:
			pipeline1.delete(GROUP_TOPIC_HASH+group_id+":"+topic_id)
		pipeline1.delete(GROUP_TOPIC_LIST+group_id)
		pipeline1.delete(CACHED_GROUP_TOPIC_LIST+group_id)
		pipeline1.delete(CACHED_GROUP_CHATTER+group_id)
		pipeline1.delete(CACHED_GROUP_INFO+group_id)
		pipeline1.delete(GROUP_VISITORS+group_id)
		pipeline1.delete(GROUP_KICK_TRACKER+group_id)
		pipeline1.delete(GROUP_EXIT_TRACKER+group_id)
		pipeline1.delete(GROUP_UUID_TO_ID_MAPPING+group_uuid)
		pipeline1.delete(GROUP_RULES_SIGNATORY+group_id)
		pipeline1.delete(group_key)
		pipeline1.execute()
		invalidate_group_membership_cache(group_id,my_server=my_server)
		bulk_update_user_membership_set(member_ids, group_id, 'private', remove=True, my_server=my_server)
		update_user_ownership_set(owner_id, group_id, remove=True, my_server=my_server)
		delete_ownership_transfer_data(group_id, my_server=my_server)
		invalidate_all_group_invites(group_id, is_public=False, my_server=my_server, member_ids=member_ids)
		invalidate_all_kicked_data(group_id, my_server=my_server)
		invalidate_all_administrative_activity(group_id, my_server=my_server)
		invalidate_cached_mehfil_replies(group_id,my_server=my_server)
		invalidate_presence(group_id, my_server=my_server)
		invalidate_cached_group_reqd_data(group_id, my_server=my_server)
		my_server.setex(RECENTLY_DELETED_GROUP+group_id,'1',ONE_MONTH)
	if return_member_ids:
		return member_ids



def empty_idle_groups(group_ids=None):
	"""
	Called by a scheduled task to empty idle group data (every 2 days)

	Idle groups are those that don't have any activity for 7 days (activity includes refreshes!)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if not group_ids:
		seven_days_ago = time.time() - GROUP_SOFT_DELETION_CUTOFF
		# UNIVERSAL_GROUP_ATTENDANCE_LIST is affected by group_attendance(), which is called every time a user refreshes a mehfil
		group_ids = my_server.zrangebyscore(UNIVERSAL_GROUP_ATTENDANCE_LIST,'-inf', seven_days_ago)#ZRANGEBYSCORE key min max
	pipeline1 = my_server.pipeline()
	for group_id in group_ids:
		pipeline1.hget(GROUP+group_id,'p')
	result1, counter = pipeline1.execute(), 0
	groups_to_empty = []
	for group_id in group_ids:
		groups_to_empty.append((group_id, 'private' if result1[counter] == '1' else 'public'))
		counter += 1
	if groups_to_empty:
		for group_id, group_type in groups_to_empty:
			permanently_empty_idle_group_content(group_id, group_type)



def delete_ghost_groups(group_ids=None):
	"""
	Called by scheduled task to auto-delete idle groups (every 6 days)

	Ghost groups are those that haven't seen any activity for 30 days (i.e. when it's been idle for far too long, we call it a 'ghost' group)

	*********Groups' respective redis2 keys ought to be deleted separately!**********
	e.g. try bulk_remove_group_notification(removed_culprit_ids,group_id)# redis 2	

	"""
	my_server = redis.Redis(connection_pool=POOL)
	if not group_ids:
		thirty_days_ago = time.time() - GROUP_HARD_DELETION_CUTOFF
		group_ids = my_server.zrangebyscore(UNIVERSAL_GROUP_ATTENDANCE_LIST,'-inf', thirty_days_ago)#ZRANGEBYSCORE key min max
	pipeline1 = my_server.pipeline()
	for group_id in group_ids:
		pipeline1.hget(GROUP+group_id,'p')
	result1, counter = pipeline1.execute(), 0
	groups_to_delete = []
	for group_id in group_ids:
		# attaching 'group privacy type' since it's useful in group deletion (i.e. in permanently_delete_group())
		groups_to_delete.append((group_id, 'private' if result1[counter] == '1' else 'public'))
		counter += 1
	if groups_to_delete:
		grp_ids_and_members = {}
		for group_id, group_type in groups_to_delete:
			member_ids = permanently_delete_group(group_id, group_type, return_member_ids=True)# redis 1 legacy membership sets are not consulted to get member_ids, delete legacy sets
			grp_ids_and_members[group_id] = member_ids
		return grp_ids_and_members
	else:
		return {}


def permanently_empty_idle_group_content(group_id, group_type):
	"""
	Permanently empties content of idle groups (i.e. keys residing in redis6)

	Doesn't touch any redis-2 notifications related to the idle mehfils, so that they remain in the matka
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	if group_type == 'public:':
		# delete all except for latest 5 replies, also gets rid of cached data (although that should already have expired)
		nearly_all_submission_ids = my_server.zrevrange(GROUP_SUBMISSION_LIST+group_id,5,-1)
		if nearly_all_submission_ids:
			pipeline1 = my_server.pipeline()
			for submission_id in nearly_all_submission_ids:
				pipeline1.delete(GROUP_SUBMISSION_HASH+group_id+":"+submission_id)
			pipeline1.zrem(GROUP_SUBMISSION_LIST+group_id,*nearly_all_submission_ids)
			pipeline1.delete(MEHFIL_CACHED_DATA+group_id)
			pipeline1.execute()
	else:
		# delete all except for latest 5 replies, also empties some caches and the chatter-list related to a private group
		nearly_all_submission_ids = my_server.zrevrange(GROUP_SUBMISSION_LIST+group_id,5,-1)
		if nearly_all_submission_ids:
			pipeline1 = my_server.pipeline()
			for submission_id in nearly_all_submission_ids:
				pipeline1.delete(GROUP_SUBMISSION_HASH+group_id+":"+submission_id)
			pipeline1.zrem(GROUP_SUBMISSION_LIST+group_id,*nearly_all_submission_ids)
			pipeline1.delete(MEHFIL_CACHED_DATA+group_id)
			pipeline1.delete(GROUP_CHATTER+group_id)
			pipeline1.delete(CACHED_GROUP_CHATTER+group_id)
			pipeline1.delete(CACHED_GROUP_INFO+group_id)
			pipeline1.execute()


def remove_inactive_members(user_ids, group_id, time_now):
	"""
	Remove inactive users from given group

	Called by group_attendance() - only when the sole 'if' statement in that function is 'True'
	"""
	group_id = str(group_id)
	my_server = redis.Redis(connection_pool=POOL)
	group_owner_id, group_privacy = retrieve_group_owner_id(group_id=group_id, with_group_privacy=True)
	# Don't make the owner leave the group!
	if group_owner_id:
		user_ids = set(user_ids)
		user_ids.discard(group_owner_id)# removing group_owner_id from inactives set
		if user_ids:
			rescind_apps = False
			list_of_user_ids = list(user_ids)
			for user_id in list_of_user_ids:
				# 'uninstall' the group for these 45-day inactive_users (even if they're officers in a public group)
				own_uname, own_avurl = retrieve_credentials(user_id,decode_uname=True)
				if group_privacy == '1':
					# group is private
					legacy_mehfil_exit(group_id, user_id, own_uname, group_type='private')# legacy redis 1 - please remove
					############################ Redis 6 ###############################
					exit_group(group_id, user_id, time_now, own_uname, get_s3_object(own_avurl,category='thumb'), is_public=False,\
						inactive=True)
					####################################################################
				else:
					# group is public
					legacy_mehfil_exit(group_id, user_id, own_uname, group_type='public')# legacy redis 1 - please remove
					############################ Redis 6 ###############################
					exit_group(group_id, user_id, time_now, is_public=True, inactive=True, rescind_apps=rescind_apps)
					####################################################################
					rescind_apps = True
			if rescind_apps:
				bulk_rescind_officer_applications(list_of_user_ids, group_id, my_server=my_server)

################################## Pruning group submissions #####################################

def del_overflowing_group_submissions(group_id, num_to_del ,my_server=None):
	"""
	Deletes all group replies beyond the latest 70 group replies (DELETION_THRESHOLD=70)
	"""
	group_id = str(group_id)
	group_list_key = GROUP_SUBMISSION_LIST+group_id
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	reply_ids = my_server.zrange(group_list_key,0,(num_to_del-1))
	reply_hash_names = []
	for reply_id in reply_ids:
		reply_hash_names.append(GROUP_SUBMISSION_HASH+group_id+":"+reply_id)
	pipeline1 = my_server.pipeline()
	for reply_hash in reply_hash_names:
		pipeline1.delete(reply_hash)
	pipeline1.zremrangebyrank(group_list_key,0,(num_to_del-1))
	pipeline1.execute()
	if random.random() < 0.1:
		# every now and then, prune the kicked users' list
		pruning_kicked_users_list(group_id, my_server=my_server)


###################################### Calculating group active users and ranking #######################################


def retrieve_active_user_count(group_id, time_now, duration):
	"""
	Retrieves active user count for mehfil with given group_id

	Effective for calculating monthly active user counts, biweekly, weekly, and daily active user counts
	KICK_DISCOUNT is a dampner to lessen the impact of kicked users in the calculated counts (currently at 0.5)
	EXIT_DISCOUNT is a dampner to lessen the impact of exited users in the calculated counts (currently at 1)
	"""
	group_id = str(group_id)
	if duration == 'monthly':
		time_ago = time_now - ONE_MONTH
	elif duration == 'biweekly':
		time_ago = time_now - TWO_WEEKS
	elif duration == 'weekly':
		time_ago = time_now - ONE_WEEK
	elif duration == 'daily':
		time_ago = time_now - ONE_DAY
	else:
		return 0
	my_server = redis.Redis(connection_pool=POOL)
	active_members = my_server.zcount(GROUP_VISITORS+group_id,time_ago,'+inf')
	active_exits = my_server.zcount(GROUP_EXIT_TRACKER+group_id,time_ago,'+inf')
	active_kicks = my_server.zcount(GROUP_KICK_TRACKER+group_id,time_ago,'+inf')
	total = active_members + EXIT_DISCOUNT*(active_exits) + KICK_DISCOUNT*(active_kicks)
	return total


def rank_mehfil_active_users():
	"""
	Ranks all public mehfils via DAU/BWAU

	DAU - Daily active users
	BWAU - Biweekly active users
	Rules:
	1) Only consider mehfils that have been in existence since two weeks (via GROUP_LIST)
	2) Only consider mehfils once their size is above 95th percentile (via GROUP_SIZE_LIST)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	# get groups above size percentile limit
	time_now = time.time()
	num_public_grps = my_server.zcard(GROUP_SIZE_LIST)
	if num_public_grps:
		# get groups beyond creation_time cutoff
		old_enough_group_ids = my_server.zrangebyscore(GROUP_LIST,'-inf',time_now-TWO_WEEKS)# sorted set contains both public and private mehfils
		#retrieve all group_ids from GROUP_SIZE_LIST
		num_groups_to_consider = int((1-(GROUP_SIZE_PERCENTILE_CUTOFF/100))*num_public_grps)
		big_enough_group_ids = my_server.zrevrange(GROUP_SIZE_LIST,0,num_groups_to_consider)# sorted set contains only public mehfils
		# now calculate stickiness of final groups
		if big_enough_group_ids:
			stickiness = []
			for group_id in big_enough_group_ids:
				if group_id in old_enough_group_ids:# the group is old enough, thus qualifies
					BWAU = retrieve_active_user_count(group_id, time_now, duration='biweekly')
					DAU = retrieve_active_user_count(group_id, time_now, duration='daily')
					stickiness.append(group_id)
					if BWAU:
						stickiness.append((DAU*1.0)/BWAU)
					else:
						stickiness.append(-1.0)
			if stickiness:
				my_server.delete(GROUP_BIWEEKLY_STICKINESS)
				my_server.zadd(GROUP_BIWEEKLY_STICKINESS,*stickiness)
				# removed cached data
				my_server.delete(CACHED_RANKED_GROUPS)


def get_ranked_mehfils():
	"""
	Returns groups ranked by their active user counts
	"""
	return redis.Redis(connection_pool=POOL).zrange(GROUP_BIWEEKLY_STICKINESS,0,-1,withscores=True)


def cache_ranked_groups(json_data):
	"""
	Caches data displayed in popular groups page
	"""
	redis.Redis(connection_pool=POOL).setex(CACHED_RANKED_GROUPS,json_data,TEN_MINS)


def retrieve_cached_ranked_groups():
	"""
	Fetches cached ranked groups to be displayed on popular groups page
	"""
	return redis.Redis(connection_pool=POOL).get(CACHED_RANKED_GROUPS)


def invalidate_cached_ranked_groups(my_server=None):
	"""
	Deletes cached ranked groups
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	return my_server.delete(CACHED_RANKED_GROUPS)


######################## Rate limiting mehfil topic and rules changes ########################


def retrieve_topic_and_rules_ttl(group_owner_id,group_uuid, is_public):
	"""
	Returns respective rate limits

	Useful when transferring ownership of mehfils - ensures the user doesn't change topic/rules and immediately transfers ownership to someone else (that can be potentially abusive)
	"""
	group_uuid = str(group_uuid)
	my_server =	redis.Redis(connection_pool=POOL)
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
		my_server.expire(key, MAX_TIME_BETWEEN_TOPIC_CHANGE_ATTEMPTS)#5 mins
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



###################################### Handling user sets #######################################


def retrieve_user_ownership(user_id, with_ownership_start_time=False, my_server=None):
	"""
	Retrieves all groups owned by user_id
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	return my_server.zrange(GROUPS_OWNED_BY_USER+str(user_id),0,-1, withscores=with_ownership_start_time)


def retrieve_user_officership(user_id, with_officership_start_time=False, my_server=None):
	"""
	Retrieves all groups officered by user_id
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	return my_server.zrange(GROUPS_IN_WHICH_USER_IS_OFFICER+str(user_id),0,-1, withscores=with_officership_start_time)



def update_user_membership_set(user_id, group_id, group_type, time_now=None, remove=False, my_server=None):
	"""
	"""
	if remove:
		if group_type == 'public':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			my_server.zrem(PUBLIC_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id)
		elif group_type == 'private':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			my_server.zrem(PRIVATE_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id)
	else:
		if group_type == 'public':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			my_server.zadd(PUBLIC_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id, time_now)
		elif group_type == 'private':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			my_server.zadd(PRIVATE_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id, time_now)


def update_user_ownership_set(user_id, group_id, time_now=None, remove=False, my_server=None):
	"""
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if remove:
		my_server.zrem(GROUPS_OWNED_BY_USER+str(user_id), group_id)
	else:
		my_server.zadd(GROUPS_OWNED_BY_USER+str(user_id), group_id, time_now)


def update_user_officership_set(user_id, group_id, time_now=None, remove=False, my_server=None):
	"""
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if remove:
		my_server.zrem(GROUPS_IN_WHICH_USER_IS_OFFICER+str(user_id), group_id)
	else:
		my_server.zadd(GROUPS_IN_WHICH_USER_IS_OFFICER+str(user_id), group_id, time_now)



def bulk_update_user_membership_set(user_ids, group_id, group_type, time_now=None, remove=False, my_server=None):
	"""
	"""
	if remove:
		if group_type == 'public':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			pipeline1 = my_server.pipeline()
			for user_id in user_ids:
				pipeline1.zrem(PUBLIC_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id)
			pipeline1.execute()
		elif group_type == 'private':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			pipeline1 = my_server.pipeline()
			for user_id in user_ids:
				pipeline1.zrem(PRIVATE_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id)
			pipeline1.execute()
	else:
		if group_type == 'public':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			pipeline1 = my_server.pipeline()
			for user_id in user_ids:
				pipeline1.zadd(PUBLIC_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id, time_now)
			pipeline1.execute()
		elif group_type == 'private':
			my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
			pipeline1 = my_server.pipeline()
			for user_id in user_ids:
				pipeline1.zadd(PRIVATE_GROUPS_USER_IS_A_MEMBER_OF+str(user_id), group_id, time_now)
			pipeline1.execute()



def bulk_update_user_officership_set(user_ids, group_id, time_now=None, remove=False, my_server=None):
	"""
	Add group id to all provided user ids data
	"""
	if user_ids:
		my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
		if remove:
			pipeline1 = my_server.pipeline()
			for user_id in user_ids:
				pipeline1.zrem(GROUPS_IN_WHICH_USER_IS_OFFICER+str(user_id), group_id)
			pipeline1.execute()
		else:
			pipeline1 = my_server.pipeline()
			for user_id in user_ids:
				pipeline1.zadd(GROUPS_IN_WHICH_USER_IS_OFFICER+str(user_id), group_id, time_now)
			pipeline1.execute()