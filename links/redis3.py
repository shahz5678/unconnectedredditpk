# coding=utf-8

import redis, time, ast
from pytz import timezone
from location import REDLOC3
from datetime import datetime
from operator import itemgetter
from templatetags.s3 import get_s3_object
from redis4 import retrieve_bulk_unames, retrieve_user_id
# from ecomm_category_mapping import ECOMM_CATEGORY_MAPPING
from send_sms import send_expiry_sms_in_bulk#, process_bulk_sms
from html_injector import image_thumb_formatting#, contacter_string
from score import PHOTOS_WITH_SEARCHED_NICKNAMES, TWILIO_NOTIFY_THRESHOLD,USER_REBAN_ACTION_RATELIMIT, USER_UNBAN_ACTION_RATELIMIT

'''
##########Redis 3 Namespace##########

pipeline1.lpush("aa:"+city,ad_id)
"ad:"+ad_id # hash containing ad details
pipeline1.lpush("aea:"+ad_city,ad_id) # used for city-wide exchange ad view
pipeline1.lpush("afa:"+ad_city,ad_id) # used for city-wide photo ad view
my_server.lpush("ala:"+str(locker_id),ad_id) # agent's locked ads (ala:)
pipeline1.zincrby("at:"+ad_city,ad_town,amount=1) # approved towns within a city
key_name = "b:"+str(low)+":"+str(high) #stores ban data
my_server.zrange("bl:"+str(own_id),0,-1) # a user's block-list
blrl:<own_id>:<target_id> is a rate limiting key set when a user unblocks another user
server.lpush("ecomm_clicks",(user_id, ad_id, time_now)) # recording the click in a list of tuples
pipeline1.sadd("sn:"+ad_id,clicker_id) #saving who all has already seen the seller's number. "sn:" stands for 'seen number'
pipeline1.zincrby("approved_locations",city,amount=1)
my_server.incr("cb:"+closed_by)
pipeline1.zadd('ecomm_verified_users',user_id) # keeping a universal table with all user_ids that have been verified
pipeline1.lpush("global_ads_list",ad_id) # used for global view
pipeline1.lpush("global_exchange_ads_list",ad_id) # used for global view
pipeline1.lpush("global_photo_ads_list",ad_id) # used for global view
pipeline2.zadd("global_expired_ads_list",ad_id,current_time+ONE_MONTH) #global list of expired ads, stays alive for 1 month
my_server.zincrby("global_inter_user_ban_list",target_id, amount=(time_now/1200)) #1200 seconds are worth 4 ban 'votes'
my_server.lpush("rc:"+ad_id,photo_id) # "rc" implies raw classified (i.e. a classified that is being made and isn't final)
temp_ad = "ta:"+user_id #temporary ad
my_server.hmset('tc:'+str(own_id),mapping)
temp_storage = "ts:"+user_id # temporary storage of buyer snapshot (used when certifying new user)
my_server.lpush("unc:"+submitted_data["user_id"]) #unapproved_user_classified (unc:)
pipeline1.lpush("uaa:"+seller_id,ad_hash) # user approved ads
pipeline2.lpush("uea:"+result1[counter][0],ad_id) # used in user_expired_ads
my_server.hgetall("um:"+str(user_id)) # user mobile number data
my_server.zadd("unapproved_ads",ad,ad_id)
"unfinalized_used_item_photos"
my_server.zadd("unfinished_classifieds",ad_id)
"verified_numbers" # sorted set, ensures that once used, a mobile number can't be tied to another ID


my_server.set("epusk:"+user_id,secret_key) # ecomm photo upload secret key

gibberish_writers = 'gibberish_writers'
punishment_text = "pt:"+str(user_id)

###########
'''

USER_THUMBS = "ut:"#key holding a blob of user's most recent fotos
SEARCH_HISTORY = "sch:"#set holding IDs of users a user has search via the search functionality


POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC3, db=0)

TEN_MINS = 10*60
TWENTY_MINS = 20*60
FORTY_FIVE_MINS = 60*45
ONE_HOUR = 60*60
TWO_HOURS = 2*60*60
SIX_HOURS = 6*60*60
ONE_DAY = 24*60*60
ONE_WEEK = 1*7*24*60*60
TWO_WEEKS = 2*7*24*60*60
ONE_MONTH = 30*24*60*60

########################################################################################################
################################### Descriptive next and prev button split test ########################
########################################################################################################

CONTROL_BUCKET = "cbkt"
NEW_BUCKET = "nbkt"
def log_pagination_button_click(user_id,bucket_name):
	my_server = redis.Redis(connection_pool=POOL)
	if bucket_name == "bucket_control":
		my_server.zincrby(CONTROL_BUCKET,user_id,amount=1)
	else:
		my_server.zincrby(NEW_BUCKET,user_id,amount=1)



########################################################################################################
########################################################################################################
########################################################################################################



def string_tokenizer(string):
	return string.replace("_"," ")

def string_joiner(string):
	return string.replace(" ", "_")

def namify(string):
	return " ".join(w.capitalize() for w in string.split())

def currencify(string):
	if string.isdigit():
		formatted = "{:,}".format(int(string))
		return "Rs."+str(formatted)
	else:
		if string[0:3] == 'Rs.':
			return string
		else:
			return "Rs."+string

def first_letter_upper(string):
	first_letter_in_upper_case = string.split()[0][0:1].upper()
	return first_letter_in_upper_case+string[1:]


def exact_date(time_now, in_bulk=False):
	"""
	Returns exact date when given epoch time

	Run from pytz import common_timezones in python shell, then print common_timezones
	"""
	if in_bulk:
		if time_now:
			# time_now is a list of epoch times
			list_of_times = []
			for time_ in time_now:
				list_of_times.append(datetime.fromtimestamp(time_*ONE_DAY, tz=timezone('Asia/Karachi')).strftime("%d-%m-%Y %I:%M %p"))
			return list_of_times
		else:
			return []
	else:
		if time_now:
			return datetime.fromtimestamp(time_now, tz=timezone('Asia/Karachi')).strftime("%d-%m-%Y %I:%M %p")# use %H:%M:%S for 24 hour style clock time
		else:
			return ''
#####################Process Nick#######################

def decode_nick(nickname):
	nick_and_code = nickname.split("**")
	lower_case_nick = nick_and_code[0]
	code = nick_and_code[1]
	upper_case_positions = [int(code[i:i+2]) for i in range(0, len(code), 2)]
	decoded_nick = ''.join(let.upper() if pos in upper_case_positions else let 
							   for pos, let in enumerate(lower_case_nick))
	return decoded_nick

def get_nicknames(raw_nicknames):
	decoded_nicks = []
	encoded_nicks = []
	for nick in raw_nicknames:
		if "**" in nick:
			encoded_nicks.append(nick)
	for nick in encoded_nicks:
		decoded_nicks.append(decode_nick(nick))
	return decoded_nicks

def process_nick(nickname):
	generic_nick = nickname.lower()+"*"
	#############################################
	position = 0
	encoding = "**"
	for l in nickname.encode('utf-8'):
		if l.isupper():
			encoding += "{:0>2}".format(position)
		position += 1
	specific_nick = nickname.lower()+encoding
	#############################################
	return generic_nick, specific_nick

def get_nick_likeness(nickname):
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick, specific_nick = process_nick(nickname)
	rank = my_server.zrank("nicknames",specific_nick)
	if rank is None:
		my_server.zadd("nicknames",generic_nick,0)
		rank = my_server.zrank("nicknames",generic_nick)
		my_server.zrem("nicknames",generic_nick)
	raw_nicknames = my_server.zrange("nicknames",max(rank-5,0),(rank+5))
	nicknames = get_nicknames(raw_nicknames)
	return nicknames

# same as nick_already_exists, but returns a different value if nick's generic form exists, but not specific form
def check_nick_status(nickname):
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick, specific_nick = process_nick(nickname)
	if not my_server.exists("nicknames"):
		return None
	else:
		pipeline1 = my_server.pipeline()
		pipeline1.zscore("nicknames",specific_nick)
		pipeline1.zscore("nicknames",generic_nick)
		result = pipeline1.execute()
		specific, generic = result[0], result[1]
		if specific and generic:
			return True
		elif specific is None and generic is None:
			return False
		elif specific is None:
			return '1' #this means the 'case' of the username is incorrect
		elif generic is None:
			return '0' #this shouldn't happen - the specific form of a nickname can't exist without its generic form in our DB
		
#checking whether nick already exists
def nick_already_exists(nickname, exact=False):
	my_server = redis.Redis(connection_pool=POOL)
	if exact:
		generic_nick, specific_nick = process_nick(nickname)
		if not my_server.exists("nicknames"):
			return None
		elif my_server.zscore("nicknames",specific_nick) is None:
			# the nickname has not been used before
			return False
		else:
			# the nickname has been used before
			return True
	else:
		generic_nick = nickname.lower()+"*"
		if not my_server.exists("nicknames"):
			return None
		elif my_server.zscore("nicknames",generic_nick) is None:
			# the nickname has not been used before
			return False
		else:
			# the nickname has been used before
			return True

#bulk checking whether nicks exist
def bulk_nicks_exist(nickname_list):
	my_server = redis.Redis(connection_pool=POOL)
	if not my_server.exists("nicknames"):
		return [None,None,None]
	else:
		generic_nicks = [nickname.lower()+"*" for nickname in nickname_list]
		pipeline1 = my_server.pipeline()
		for nick in generic_nicks:
			pipeline1.zscore("nicknames",nick)
		result1 = pipeline1.execute()
		nicks = []
		counter = 0
		for exist in result1:
			if exist is None:
				nicks.append((nickname_list[counter],False))
			else:
				nicks.append((nickname_list[counter],True))
			counter += 1
		return nicks


#inserting nickname at the time of registration
def insert_nick(nickname):
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick, specific_nick = process_nick(nickname)
	my_server.zadd("nicknames",generic_nick,0,specific_nick,0)


def find_nickname(target_nick, searcher_id):
	"""
	Main function resposible for yielding search results
	"""
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick, specific_nick = process_nick(target_nick)
	rank = my_server.zrank("nicknames",generic_nick)
	exact_with_pics = []
	if rank is None:
		# no match found
		nick_found = False
		my_server.zadd("nicknames",generic_nick,0)
		rank = my_server.zrank("nicknames",generic_nick)
		my_server.zrem("nicknames",generic_nick)
		raw_nicknames = my_server.zrange("nicknames",max(rank-5,0),(rank+5))
		similar_nicknames = get_nicknames(raw_nicknames)
		result1 = []
		for uname in similar_nicknames:
			user_id = retrieve_user_id(uname)
			if user_id:
				result1.append(my_server.get(USER_THUMBS+user_id))
			else:
				result1.append(None)
		similar_with_pics = []
		counter = 0
		for uname in similar_nicknames:
			similar_with_pics.append((uname,result1[counter]))
			counter += 1
	else:
		# match(es) found
		exact = []
		nick_found = True
		raw_nicknames = my_server.zrange("nicknames",max(rank-5,0),(rank+5))
		similar_nicknames = get_nicknames(raw_nicknames)
		list_copy = list(similar_nicknames)
		for nick in list_copy:
			if nick.lower() == target_nick.encode('utf-8').lower():
				exact.append(nick)
				similar_nicknames.remove(nick)
		search_history = SEARCH_HISTORY+str(searcher_id)
		pipeline1 = my_server.pipeline()
		for entry in exact:
			user_id = retrieve_user_id(entry)
			pipeline1.zincrby(search_history,user_id,amount=1)
		pipeline1.execute()
		pipeline2 = my_server.pipeline()
		for uname in similar_nicknames:
			user_id = retrieve_user_id(uname)
			pipeline2.get(USER_THUMBS+user_id)
		result2 = pipeline2.execute()
		similar_with_pics = []
		counter = 0
		for uname in similar_nicknames:
			similar_with_pics.append((uname,result2[counter]))
			counter += 1
		pipeline3 = my_server.pipeline()
		for uname in exact:
			user_id = retrieve_user_id(uname)
			pipeline3.get(USER_THUMBS+user_id)
		result3 = pipeline3.execute()
		counter = 0
		for uname in exact:
			exact_with_pics.append((uname,result3[counter]))
			counter += 1
	return nick_found, exact_with_pics, similar_with_pics


def select_nick(nickname, selector_id):
	"""
	Used to bump up scores when user clicks the nick after searching it
	"""
	nick_id = retrieve_user_id(nickname)
	if nick_id:
		redis.Redis(connection_pool=POOL).zincrby(SEARCH_HISTORY+str(selector_id),nick_id,amount=1)


def get_search_history(searcher_id):
	"""
	Used to populate a user's search history in 'search' page
	"""
	search_history = SEARCH_HISTORY+str(searcher_id)
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(search_history):
		my_server.expire(search_history,TWO_WEEKS)
		return my_server.zrevrange(search_history,0,-1)
	else:
		return []


def del_search_history(searcher_id, nickname):
	"""
	Delete an entry from search history
	"""
	nick_id = retrieve_user_id(nickname)
	if nick_id:
		redis.Redis(connection_pool=POOL).zrem(SEARCH_HISTORY+str(searcher_id),nick_id)


def retrieve_history_with_pics(user_id_list):
	"""
	Enriches user history with their uploaded photo thumbnails
	"""
	if user_id_list:
		pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
		for user_id in user_id_list:
			pipeline1.get(USER_THUMBS+str(user_id))
		result1 = pipeline1.execute()
		username_dictionary = retrieve_bulk_unames(user_id_list,decode=True)
		history, counter = [], 0
		for user_id in user_id_list:
			history.append((username_dictionary[int(user_id)], result1[counter]))
			counter += 1
		return history


def retrieve_thumbs(obj_list):
	"""
	Retrieves saved user thumbs in bulk
	"""
	pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
	for obj in obj_list:
		user_thumbs = USER_THUMBS+str(obj['id'])
		pipeline1.get(user_thumbs)
	result1, counter = pipeline1.execute(), 0
	for obj in obj_list:
		obj['thumbs'] = result1[counter]
		counter += 1
	return obj_list


def retrieve_single_thumbs(user_id):
	"""
	Retrieves a given user's thumbnail photos (in case they have any)
	"""
	return redis.Redis(connection_pool=POOL).get(USER_THUMBS+str(user_id))


def search_thumbs_missing(user_id):
	"""
	Useful for checking the existence of given user's thumbs
	"""
	if redis.Redis(connection_pool=POOL).exists(USER_THUMBS+str(user_id)):
		return False
	else:
		return True


def add_search_photo(img_url,photo_id,user_id):
	"""
	Add latest photo entry to a payload trimmed at 5 most recent photo-thumbs max
	"""
	user_thumbs = USER_THUMBS+str(user_id)
	new_payload = image_thumb_formatting(img_url=get_s3_object(img_url,category='thumb'),pid=photo_id)
	my_server = redis.Redis(connection_pool=POOL)
	existing_payload = my_server.get(user_thumbs)
	payload = new_payload+'&nbsp;'+existing_payload if existing_payload else new_payload
	num_breaks = payload.count('&nbsp;')
	if num_breaks > (PHOTOS_WITH_SEARCHED_NICKNAMES-1):
		# trim from 5th &nbsp; onward
		groups = payload.split('&nbsp;')
		payload = '&nbsp;'.join(groups[:PHOTOS_WITH_SEARCHED_NICKNAMES])
	my_server.setex(user_thumbs,payload, TWO_WEEKS)


def bulk_add_search_photos(target_id, ids_with_urls):
	"""
	Populates the target's thumbnails for preview

	The thumbs appear as a series of 5 photos in certain parts of the website
	This function is kicked off when a user's profile is visited
	"""
	user_thumbs = USER_THUMBS+str(target_id)
	ids_with_thumbs = [(item[0],get_s3_object(item[1],category='thumb')) for item in ids_with_urls]
	payload = []
	for photo_id, photo_url in ids_with_thumbs:
		payload.append(image_thumb_formatting(photo_url,photo_id))
	final_payload = '&nbsp;'.join(payload)
	redis.Redis(connection_pool=POOL).setex(user_thumbs,final_payload,TWO_WEEKS)


def insert_nick_list(nickname_list):
	my_server = redis.Redis(connection_pool=POOL)
	nicknames = []
	for nickname in nickname_list:
		generic_nick, specific_nick = process_nick(nickname)
		nicknames.append(generic_nick)
		nicknames.append(0)
		nicknames.append(specific_nick)
		nicknames.append(0)
	my_server.zadd("nicknames",*nicknames)

############################################Inter User Banning#########################################

# double checking that ban removal should be allowed
def ensure_removability(own_id, id_list, server):
	all_keys = []
	for target_id in id_list:
		low, high = (own_id, target_id) if int(own_id) < int(target_id) else (target_id, own_id)
		key_name = "b:"+str(low)+":"+str(high)
		all_keys.append(key_name)
	pipeline1 = server.pipeline()
	for key in all_keys:
		pipeline1.get(key)
	who_banned_who = pipeline1.execute()
	list_of_ids_to_unban, counter, own_id = [], 0, str(own_id)
	for target_id in id_list:
		banned_by = who_banned_who[counter]
		if not banned_by or banned_by == own_id:
			list_of_ids_to_unban.append(target_id)
		counter += 1
	return list_of_ids_to_unban


def delete_ban_target_credentials(own_id):
	redis.Redis(connection_pool=POOL).delete('tc:'+str(own_id))


def get_ban_target_credentials(own_id, username_only=False, id_only=False, destroy=False):
	my_server = redis.Redis(connection_pool=POOL)
	key = 'tc:'+str(own_id)
	if destroy:
		if username_only:
			target_username = my_server.hget(key,'target_username')
			my_server.delete(key)
			return target_username
		elif id_only:
			target_id = my_server.hget(key,'target_id')
			my_server.delete(key)
			return target_id
		else:
			credentials = my_server.hgetall(key)
			my_server.delete(key)
			return credentials
	else:
		if username_only:
			return my_server.hget(key,'target_username')
		elif id_only:
			return my_server.hget(key,'target_id')
		else:
			credentials = my_server.hgetall(key)
			return credentials


def save_ban_target_credentials(own_id, target_id, target_username, id_only=False, username_only=False):
	"""
	Temporarily saves credentials of a target a user is intending to ban
	"""
	key = 'tc:'+str(own_id)
	mapping = {'target_id':target_id, 'target_username':target_username}
	my_server = redis.Redis(connection_pool=POOL)
	my_server.hmset(key,mapping)
	my_server.expire(key,FORTY_FIVE_MINS)


def get_banned_users_count(own_id):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.zcard("bl:"+str(own_id))


def get_banned_users(own_id):
	my_server = redis.Redis(connection_pool=POOL)
	all_banned_ids = my_server.zrange("bl:"+str(own_id),0,-1)
	if all_banned_ids == []:
		return []
	else:
		all_keys = []
		for target_id in all_banned_ids:
			low, high = (own_id, target_id) if int(own_id) < int(target_id) else (target_id, own_id)
			key_name = "b:"+str(low)+":"+str(high)
			all_keys.append(key_name)
		pipeline1 = my_server.pipeline()
		for key in all_keys:
			pipeline1.ttl(key)
		all_banned_ids_ttl = pipeline1.execute()
		counter = 0
		all_banned_ids_with_ttl = []
		for target_id in all_banned_ids:
			ttl = all_banned_ids_ttl[counter] if all_banned_ids_ttl[counter] else 0
			all_banned_ids_with_ttl.append((target_id,ttl))
			counter += 1
		# subsequently remove ids with ttl < 2 (from bl:<user_id>)
		return all_banned_ids_with_ttl


def remove_banned_users_in_bulk(own_id, ids_to_remove_from_ban_list):
	my_server = redis.Redis(connection_pool=POOL)
	if ids_to_remove_from_ban_list:
		ids_to_remove_from_ban_list = ensure_removability(own_id, ids_to_remove_from_ban_list, my_server)
		if ids_to_remove_from_ban_list:
			my_server.zrem("bl:"+str(own_id),*ids_to_remove_from_ban_list)


def remove_single_ban(own_id, target_id):
	"""
	Removes blocked user from block list

	Rate limits users from banning said user again
	"""
	my_server = redis.Redis(connection_pool=POOL)
	low, high = (own_id, target_id) if int(own_id) < int(target_id) else (target_id, own_id)
	key_name = "b:"+str(low)+":"+str(high)
	banned_by = my_server.get(key_name)
	own_id = str(own_id)
	if banned_by == own_id:
		# remove ban
		block_rl = "brl:"+str(own_id)+":"+str(target_id)
		ttl = my_server.ttl(block_rl)
		if ttl > 0:
			return False, ttl
		else:
			pipeline1 = my_server.pipeline()
			pipeline1.delete(key_name)
			pipeline1.zrem("bl:"+own_id,target_id)
			pipeline1.setex("blrl:"+own_id+":"+target_id,'1',USER_REBAN_ACTION_RATELIMIT)
			pipeline1.execute()
			return True, None
	else:
		# don't have the right to remove this ban, since you didn't place this ban
		return False, None


def ratelimit_banner_from_unbanning_target(own_id,target_id):
	"""
	Can't unban someone immediately, so that no one bans in vain
	"""
	block_rate_limit = "brl:"+str(own_id)+":"+str(target_id) # set this key so that user can't immediately unblock the blocked target
	redis.Redis(connection_pool=POOL).setex(block_rate_limit,'1',USER_UNBAN_ACTION_RATELIMIT)


def is_already_banned(own_id, target_id, key_name=None, server=None, return_banner=False):
	"""
	Retrieves whether there's a block underway between own_id and target_id

	Can optionally send the ID of the banner
	"""
	if not server:
		server = redis.Redis(connection_pool=POOL)
	if not key_name:
		low, high = (own_id, target_id) if int(own_id) < int(target_id) else (target_id, own_id)
		key_name = "b:"+str(low)+":"+str(high)
	if return_banner:
		pipeline1 = server.pipeline()
		pipeline1.get(key_name)
		pipeline1.ttl(key_name)
		result = pipeline1.execute()
		return result[0], result[1]
	else:
		ttl = server.ttl(key_name)
		if ttl > -1:
			# the expire time, in seconds
			return ttl
		elif ttl < -1:
			# key does not exist
			return None
		else:
			# key exists but has no associated expire time
			return False


def set_inter_user_ban(own_id, target_id, target_username, ttl, time_now, can_unban):
	"""
	Bans a given target user by setting relevant data in redis
	"""
	low, high = (own_id, target_id) if int(own_id) < int(target_id) else (target_id, own_id)
	key_name = "b:"+str(low)+":"+str(high)
	my_server = redis.Redis(connection_pool=POOL)
	cooloff_ttl = my_server.ttl("blrl:"+str(own_id)+":"+target_id)
	if cooloff_ttl > 0:
		return None, cooloff_ttl
	else:
		existing_ttl = is_already_banned(own_id=own_id, target_id=target_id, key_name=key_name, server=my_server)
		if existing_ttl is None or existing_ttl is False or can_unban == '1':
			pipeline1 = my_server.pipeline()
			# a key to help make quick decision on whether an interaction is to be allowed or not
			pipeline1.setex(key_name,own_id,ttl)
			# combined with 'solitary' keys above, this helps populate a list of all banned people for the user to see
			pipeline1.zadd("bl:"+str(own_id),target_id, time_now)
			# only add to the global list if it was NOT a re-ban
			pipeline1.execute()
			return True, None
		else:
			return False, None


# def get_global_ban_leaderboard():
# 	my_server = redis.Redis(connection_pool=POOL)
# 	return my_server.zrange("global_inter_user_ban_list",-50,-1,withscores=True)

########################################################################################################
# def populate_ad_list(which_list="photos"):
#   my_server = redis.Redis(connection_pool=POOL)
#   live_ad_ids = my_server.lrange("global_ads_list",0,-1)
#   if which_list == "photos":
#       pipeline1 = my_server.pipeline()
#       for ad_id in live_ad_ids:
#           pipeline1.hmget("ad:"+ad_id,"photo_count","city")
#       result1 = pipeline1.execute()
#       counter = 0
#       for ad_id in live_ad_ids:
#           if int(result1[counter][0]) > 0:
#               my_server.rpush("global_photo_ads_list",ad_id)
#               my_server.rpush("afa:"+result1[counter][1],ad_id) # used for city-wide photo ad view
#           counter += 1
##########################################Classifieds#################################################


def save_ad_expiry_or_sms_feedback(ad_id, feedback, which_feedback):
	my_server = redis.Redis(connection_pool=POOL)
	if which_feedback == 'expiry':
		sorted_set = 'ad_expiry_feedback'
	elif which_feedback == 'sms':
		sorted_set = 'sms_setting_feedback'
	else:
		return None
	my_server.zadd(sorted_set,feedback, ad_id)

def get_global_verified_users():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.zrange('ecomm_verified_users',0,-1)

def get_SMS_setting(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.hget("ad:"+ad_id,'SMS_setting')


def toggle_SMS_setting(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	original_setting = my_server.hget('ad:'+ad_id,'SMS_setting')
	if original_setting == '1':
		pipeline1 = my_server.pipeline()
		pipeline1.hset('ad:'+ad_id,'SMS_setting','0')
		pipeline1.incr("sms_turned_off")
		pipeline1.execute()
	elif original_setting == '0':
		pipeline1 = my_server.pipeline()
		pipeline1.hset('ad:'+ad_id,'SMS_setting','1')
		pipeline1.decr("sms_turned_off")
		pipeline1.execute()
	return original_setting


def ad_owner_id(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.hget("ad:"+ad_id,"user_id")


# takes care of expired ads' final deletion (auto-run once a day or so)
def process_ad_final_deletion():
	my_server = redis.Redis(connection_pool=POOL)
	current_time = time.time()
	ad_ids = my_server.zrangebyscore("global_expired_ads_list",'-inf', current_time)
	if ad_ids:
		pipeline1 = my_server.pipeline()
		for ad_id in ad_ids:
			pipeline1.hget("ad:"+ad_id,"user_id")
		user_ids = pipeline1.execute()
		counter = 0
		pipeline2 = my_server.pipeline()
		for ad_id in ad_ids:
			user_id = user_ids[counter]
			pipeline2.delete("ad:"+ad_id)
			pipeline2.delete("sn:"+ad_id) # contains ids of all who've already seen the seller's number
			pipeline2.lrem("uea:"+user_id,ad_id,num=-1)
			counter += 1
		pipeline2.execute()
		my_server.zremrangebyscore("global_expired_ads_list",'-inf', current_time)


def process_expiry_sms_in_bulk(user_ids):
	if len(user_ids) <= TWILIO_NOTIFY_THRESHOLD:
		send_expiry_sms_in_bulk(user_ids)
	else:
		chunks = [user_ids[x:x+TWILIO_NOTIFY_THRESHOLD] for x in xrange(0, len(user_ids), TWILIO_NOTIFY_THRESHOLD)]
		for user_id_list in chunks:
			send_expiry_sms_in_bulk(user_id_list)

# moves approved ads into the expired phase (used for both time expiry and click based expiry)
def process_ad_expiry(ad_ids=None, type_list=True):
	my_server = redis.Redis(connection_pool=POOL)
	current_time = time.time()
	if type_list:
		if not ad_ids:
			# used for time-based ad expiry
			ad_ids = my_server.zrangebyscore("ad_expiry_queue",'-inf',current_time)
			if ad_ids:
				pipeline1 = my_server.pipeline()
				for ad_id in ad_ids:
					pipeline1.hmget("ad:"+ad_id,"user_id","city","is_barter","MN_data","photo_count")
				result1 = pipeline1.execute() # result1 will contain a list of lists
				pipeline2 = my_server.pipeline()
				# expired_numbers = []
				user_ids_of_expired_ads = []
				counter = 0
				for ad_id in ad_ids:
					user_id, city, is_barter, MN_data, photo_count = result1[counter][0], string_joiner(result1[counter][1]), result1[counter][2], result1[counter][3], result1[counter][4]
					pipeline2.lrem("global_ads_list",ad_id,num=-1)
					pipeline2.lrem("aa:"+city,ad_id,num=1)
					if is_barter == 'Paisey aur badley mein cheez dono':
						pipeline2.lrem("global_exchange_ads_list",ad_id,num=-1)
						pipeline2.lrem("aea:"+city, ad_id, num=-1)
					if int(photo_count) > 0:
						pipeline2.lrem("global_photo_ads_list",ad_id,num=-1)
						pipeline2.lrem("afa:"+city, ad_id, num=-1)
					pipeline2.lrem("uaa:"+user_id,ad_id)
					pipeline2.zincrby("approved_locations",city,amount=-1)
					pipeline2.lpush("uea:"+user_id,ad_id) # used in user_expired_ads
					pipeline2.zadd("global_expired_ads_list",ad_id,current_time+ONE_MONTH) # global list of expired ads, used to sanitize expired ads after 1 month
					# expired_numbers.append(ast.literal_eval(MN_data)["number"])
					user_ids_of_expired_ads.append(user_id)
					counter += 1
				pipeline2.execute()
				my_server.zremrangebyscore("ad_expiry_queue",'-inf',current_time)
				# process_bulk_sms(expired_numbers)
				process_expiry_sms_in_bulk(user_ids_of_expired_ads)
	else:
		if ad_ids:
			# ad_ids contains a single ad_id
			user_id, city, is_barter, photo_count = my_server.hmget("ad:"+ad_ids,"user_id","city","is_barter","photo_count")
			city = string_joiner(city)
			pipeline1 = my_server.pipeline()
			pipeline1.lrem("global_ads_list",ad_ids,num=-1)
			pipeline1.lrem("aa:"+city,ad_ids,num=1)
			if is_barter == 'Paisey aur badley mein cheez dono':
				pipeline1.lrem("global_exchange_ads_list",ad_ids,num=-1)
				pipeline1.lrem("aea:"+city, ad_ids, num=-1)
			if int(photo_count) > 0:
				pipeline1.lrem("global_photo_ads_list",ad_ids,num=-1)
				pipeline1.lrem("afa:"+city, ad_ids, num=-1)
			pipeline1.lrem("uaa:"+user_id,ad_ids)
			pipeline1.zrem("ad_expiry_queue",ad_ids) # remove ad from ad_expiry_queue
			pipeline1.zincrby("approved_locations",city,amount=-1)
			pipeline1.lpush("uea:"+user_id,ad_ids) # used in user_expired_ads
			pipeline1.zadd("global_expired_ads_list",ad_ids,current_time+ONE_MONTH)
			pipeline1.execute()
		else:
			# do nothing if ad_id wasn't passed, because this is not going to be listed in the ad_expirty_queue
			pass

def log_detail_click(ad_id, clicker_id):
	if clicker_id:
		my_server = redis.Redis(connection_pool=POOL)
		time_now, ad = time.time(), "ad:"+str(float(ad_id))
		unique_detail_clicks, detail_click_details = my_server.hmget(ad,"unique_detail_clicks","detail_click_details")
		if unique_detail_clicks:
			detail_click_details = ast.literal_eval(detail_click_details)
			only_ids = map(itemgetter(0), detail_click_details)
			if clicker_id not in only_ids:
				detail_click_details.append((clicker_id, time_now))
				pipeline1 = my_server.pipeline()
				pipeline1.hincrby(ad,'unique_detail_clicks',amount=1)
				pipeline1.hset(ad,'detail_click_details',detail_click_details)
				pipeline1.execute()
		else:
			mapping = {'unique_detail_clicks':1,"detail_click_details":[(clicker_id,time_now)]}
			my_server.hmset(ad,mapping)

# helper function for get_seller_details
def log_ad_click(server, ad_hash, clicker_id, ad_id, time_now):
	is_unique, clicker_number, expire_ad = False, None, False
	if not server.sismember("sn:"+ad_id,clicker_id):
		click_details, is_unique = [], True
		clicker_number = "0"+ast.literal_eval(server.lrange('um:'+clicker_id,0,-1)[0])["national_number"]
		click_details.append((clicker_number,time_now))
		if 'unique_clicks' in ad_hash:
			ad_hash["unique_clicks"] = int(ad_hash["unique_clicks"]) + 1
		else:
			ad_hash["unique_clicks"] = 1
		#add ad's click information alongwith timestamp
		if "click_details" in ad_hash:
			ad_hash["click_details"] = click_details+ast.literal_eval(ad_hash["click_details"])
		else:
			ad_hash["click_details"] = click_details
		if "expiration_clicks" in ad_hash:
			if int(ad_hash["unique_clicks"]) > int(ad_hash["expiration_clicks"]):
				expire_ad = True
		pipeline1 = server.pipeline()
		pipeline1.hmset("ad:"+ad_id,ad_hash) #saving latest number of clicks
		pipeline1.sadd("sn:"+ad_id,clicker_id) #saving all who've already seen the seller's number
		pipeline1.execute()
		if expire_ad:
			process_ad_expiry(ad_id,type_list=False) # expire ad if enough clicks have happened (only for click-rated ad expiry, not time-related)
	return ad_hash, is_unique, clicker_number, expire_ad


# called when buyer clicks the button to get seller's contact details
def get_seller_details(clicker_id, ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	ad_id, clicker_id, time_now = str(float(ad_id)), str(clicker_id), time.time()
	seller_details = log_ad_click(my_server,my_server.hgetall("ad:"+ad_id), clicker_id, ad_id, time_now)
	my_server.lpush("ecomm_clicks",(clicker_id, ad_id)) # recording the click in a list of tuples, 'is_unique' means a person clicking the same ad twice
	return seller_details


def get_and_reset_daily_ecomm_clicks():
	my_server = redis.Redis(connection_pool=POOL)
	all_clicks = my_server.lrange("ecomm_clicks",0,-1)
	pipeline1 = my_server.pipeline()
	pipeline1.lpush("weekly_ecomm_clicks",all_clicks)
	pipeline1.delete("ecomm_clicks")
	pipeline1.execute()
	return all_clicks


def get_and_reset_weekly_ecomm_clicks():
	my_server = redis.Redis(connection_pool=POOL)
	all_weekly_clicks = my_server.lrange("weekly_ecomm_clicks",0,-1)
	gross_string_clicks = []
	for clicks in all_weekly_clicks:
		clicks = ast.literal_eval(clicks)
		if clicks:
			gross_string_clicks += clicks
	my_server.delete("weekly_ecomm_clicks")
	return gross_string_clicks


def retrieve_mobile_unverified_in_bulk(user_ids):
	"""
	Returns list of users (from given user_ids) which are NOT verified
	"""
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for user_id in user_ids:
		pipeline1.exists("um:"+str(user_id))
	result_list, counter = pipeline1.execute(), 0
	unverified_ids = []
	for user_id in user_ids:
		if not result_list[counter]:
			unverified_ids.append(user_id)
		counter += 1
	return unverified_ids


# return True if user has any number on file
def is_mobile_verified(user_id):
	"""
	return True if user has any number on file
	"""
	return True if redis.Redis(connection_pool=POOL).exists("um:"+str(user_id)) else False

def someone_elses_number(national_number, user_id):
	my_server = redis.Redis(connection_pool=POOL)
	rival_id = my_server.zscore("verified_numbers", national_number)
	if rival_id is None or int(rival_id) == user_id:
		# either own number, or available number, either way NOT someone else's number
		return False
	else:
		# someone else's number
		return True



def get_user_verified_number(user_id,country_code=False):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	numbers = my_server.lrange('um:'+user_id,0,-1)
	if numbers:
		mob_nums = []
		if country_code:
			for number in numbers:
				mob_nums.append(ast.literal_eval(number)["number"])
		else:
			for number in numbers:
				mob_nums.append(ast.literal_eval(number)["national_number"])
		# sending back numbers appended in a list
		return mob_nums
	else:
		return []


def unverify_user_id(user_id):
	"""
	The reverse of save_consumer_number() below
	"""
	numbers_to_remove = []
	if user_id:
		user_id = str(user_id)
		my_server = redis.Redis(connection_pool=POOL)
		user_number_data = my_server.lrange("um:"+user_id,0,-1)
		for data_row in user_number_data:
			numbers_to_remove.append(ast.literal_eval(data_row)["national_number"])
		if numbers_to_remove:
			pipeline1 = my_server.pipeline()
			pipeline1.zrem('ecomm_verified_users', user_id)
			pipeline1.zrem('verified_numbers',*numbers_to_remove)
			pipeline1.delete("um:"+user_id)
			pipeline1.execute()
	return numbers_to_remove


# this mechanism saves up to TWO user numbers, trimming the 3rd
def save_consumer_number(account_kit_id, mobile_data, user_id):
	my_server = redis.Redis(connection_pool=POOL)
	if mobile_data:
		user_id = str(user_id)
		user_mobile = "um:"+user_id
		verif_time = time.time()
		mapping = {'AK_ID':account_kit_id, 'national_number':mobile_data["national_number"],'number':mobile_data["number"],\
		'country_prefix':mobile_data["country_prefix"] ,'verif_time':verif_time}
		pipeline1 = my_server.pipeline()
		pipeline1.lpush(user_mobile, mapping)
		pipeline1.zadd('ecomm_verified_users',user_id, verif_time) # keeping a universal table of all ecomm user_ids that have been verified, might be useful later
		pipeline1.zadd('verified_numbers',mobile_data["national_number"], user_id) # to ensure that once used, a mobile number can't be tied to another ID
		pipeline1.execute()
		if my_server.llen(user_mobile) > 2:
			removed_number = ast.literal_eval(my_server.rpop(user_mobile))["national_number"]
			my_server.zrem("verified_numbers",removed_number) #remove the number from 'verified_numbers' sorted set as well. This frees up the number to be used elsewhere

# retrieves approved ad's item name, to be sent in an SMS to the ad creator
def get_item_name(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.hget("ad:"+str(float(ad_id)),'title')


# helper function for move_to_approved_ads
# incrementing ad agent "closing" score (coffee is for closers)
# def increment_agent_score(server, username):
# 	pipeline1 = server.pipeline()
# 	pipeline1.incr("total_ads_closed") # keeping a count of all ads ever approved
# 	pipeline1.incr("cb:"+username) # incrementing the score of the closing agent
# 	pipeline1.expire("cb:"+username, ONE_WEEK) # score expires in 1 week if agent isn't at work
# 	pipeline1.execute()

# helper function for move_to_approved_ads
def process_ad_approval(server,ad_id, ad_hash, ad_city, ad_town, seller_id):
	pipeline1 = server.pipeline()
	pipeline1.zincrby("approved_locations",ad_city,amount=1) # first get all locations, then all approved ads related to that location, and then all ads' hashes
	pipeline1.zincrby("at:"+ad_city,ad_town,amount=1) # approved towns within a city
	pipeline1.lpush("global_ads_list",ad_id) # used for global view
	pipeline1.lpush("aa:"+ad_city,ad_id) # used for city-wide view
	if ad_hash["is_barter"] == 'Paisey aur badley mein cheez dono':
		pipeline1.lpush("global_exchange_ads_list",ad_id) # used for global view
		pipeline1.lpush("aea:"+ad_city,ad_id) # used for city-wide exchange ad view
	if int(ad_hash["photo_count"]) > 0:
		pipeline1.lpush("global_photo_ads_list",ad_id) # used for global photo ad view
		pipeline1.lpush("afa:"+ad_city,ad_id) # used for city-wide photo ad view
	# if ad_hash["categ"] in ECOMM_CATEGORY_MAPPING:
	#   pipeline1.lpush(ECOMM_CATEGORY_MAPPING[ad_hash["categ"]],ad_id)
	#   pipeline1.lpush(ECOMM_CATEGORY_MAPPING[ad_hash["categ"]]+":"+ad_city,ad_id)
	#   pipeline1.zincrby("top_categories",ECOMM_CATEGORY_MAPPING[ad_hash["categ"]],amount=1)
	pipeline1.hmset("ad:"+ad_id,ad_hash)
	pipeline1.zremrangebyscore("unc:"+str(seller_id),ad_id,ad_id) # sanitizing unapproved ad queue
	pipeline1.lpush("uaa:"+str(seller_id),ad_id) # used for seller's own view
	pipeline1.zadd("classified_categories",ad_hash["categ"],0) # adding the category to its own table, ensuring alphabetical sort
	pipeline1.zadd("ad_expiry_queue",ad_id,ad_hash["expiration_time"]) # queuing the ad for expiry according to its expiration time
	pipeline1.execute()


# main function used by agents to make an ad live after approving it
def move_to_approved_ads(ad_id,expiration_time=None,expiration_clicks=None, closed_by=None, closer_id=None):
	my_server = redis.Redis(connection_pool=POOL)
	ad = ast.literal_eval(my_server.zrangebyscore("unapproved_ads",ad_id, ad_id)[0])
	time_now = time.time()
	if expiration_time:
		ad["expiration_time"] = expiration_time
	elif expiration_clicks:
		ad["expiration_clicks"], ad["expiration_time"] = expiration_clicks, time_now+ONE_MONTH # give it a hard 30 day expiry any way
	ad["SMS_setting"], ad["submission_time"], ad["closed_by"] = '1', time_now, closed_by #renewing submission time (i.e. replacing it with approval time)
	ad.pop("locked_by",None) #removing locked_by field
	process_ad_approval(my_server,ad_id,ad,string_joiner(ad["city"]), string_joiner(ad["town"]), ad["user_id"])
	##############################################################################
	pipeline1 = my_server.pipeline()
	pipeline1.zremrangebyscore("unapproved_ads",ad_id,ad_id)
	pipeline1.lrem("ala:"+closer_id,ad_id)
	pipeline1.execute()
	##############################################################################
	increment_agent_score(my_server, closed_by)
	return ad["MN_data"]["number"]

# helper function for save_basic_ad_data
def cleanup(my_server,ad_id):
	my_server.zrem("unfinalized_used_item_photos",ad_id)
	my_server.delete("rc:"+str(ad_id))

# helper function for process_ad_verification
def get_MN_data(server, user_id, national_number):
	num_list = []
	pre_existing_numbers = server.lrange("um:"+user_id, 0, -1)
	if pre_existing_numbers:
		for num_info in pre_existing_numbers:
			num_info = ast.literal_eval(num_info)
			if num_info["national_number"] == national_number:
				return num_info["AK_ID"], {'national_number':num_info['national_number'],'country_prefix':num_info["country_prefix"],'number':num_info["number"]}, True
			num_list.append(num_info)
		# send something if no number identified - can't leave a listing without a contact number can we?
		return num_list[0]["AK_ID"],{'national_number':num_list[0]["national_number"],'country_prefix':num_list[0]["country_prefix"],'number':num_list[0]["number"]}, False
	else:
		return None, None, False


# helper function for save_basic_ad_data
# saving seller number and ad data right after mobile verification
def process_ad_verification(server, submitted_data):
	user_id = str(submitted_data["user_id"])
	################### Check if pre-existing number is to be used ####################
	national_number = submitted_data["MN_data"] if submitted_data["AK_ID"] == 'just_number' else submitted_data["MN_data"]["national_number"] # 'just_number' value comes from 'post_seller_info' in ecomm.py
	AK_ID, MN_data, already_exists = get_MN_data(server, user_id, national_number)
	if already_exists:
		# no need to save number, just save the ad later. Fill correct values in this step
		submitted_data["AK_ID"], submitted_data["MN_data"] = AK_ID, MN_data
	else:
		# save the number against the user's profile
		save_consumer_number(submitted_data["AK_ID"],submitted_data["MN_data"],submitted_data["user_id"]) #called 'consumer' number, but same as 'seller' number
	##################################### Save AD #####################################
	pipeline1 = server.pipeline()
	pipeline1.zadd("unapproved_ads",submitted_data,submitted_data["ad_id"])
	pipeline1.zadd("unc:"+user_id,submitted_data,submitted_data["ad_id"]) #unapproved_user_classified (unc:)
	pipeline1.delete("ta:"+user_id) # sanitizing temporarily saved user ad
	pipeline1.execute()



def save_basic_ad_data(submitted_data):
	my_server = redis.Redis(connection_pool=POOL)
	photo_ids = my_server.lrange("rc:"+str(submitted_data["ad_id"]),0,-1)
	submitted_data["photo_count"] = 0
	if photo_ids:
		photo_ids = [(photo_id, False) for photo_id in photo_ids]
		photo_ids[0] = (photo_ids[0][0],True)
		submitted_data["photos"] = photo_ids
		submitted_data["photo_count"] = len(photo_ids)
	submitted_data["submission_time"] = time.time()
	process_ad_verification(my_server, submitted_data)
	cleanup(my_server,submitted_data["ad_id"])
	return True


def save_used_item_photo(user_id, ad_id, photo_id):
	my_server = redis.Redis(connection_pool=POOL)
	ad_id = str(ad_id)
	pipeline1 = my_server.pipeline()
	pipeline1.zadd("unfinalized_used_item_photos",ad_id,time.time()) #removed deployed ad_ids from here
	pipeline1.lpush("rc:"+ad_id,photo_id) #remove deployed photo_ids from here
	pipeline1.execute()
	# need to tie photo_ids to the ad (list with ad_id in the name, containing photo_ids)


def temporary_ad_field_mapping(field):
	if field == 'is_new':
		return 'basic_item_new'
	elif field == 'is_barter':
		return 'basic_item_barter'
	elif field == 'desc':
		return 'basic_item_description'
	elif field == 'ask':
		return 'basic_item_ask'
	else:
		return field

def temporarily_save_ad(user_id, description=None, is_new=None, ask=None, is_barter=None, ad_id=None, which_photo_hash=None, photo_id=None, photo_hash=None,\
	photo_number=None, seller_name=None,city=None,town=None,submission_device=None,on_fbs=None,csrf=None, mob_nums=None, uid=None):
	my_server = redis.Redis(connection_pool=POOL)
	temp_ad = "ta:"+user_id
	if description:
		my_server.hset(temp_ad,"basic_item_description",first_letter_upper(description))
	if is_new:
		my_server.hset(temp_ad,"basic_item_new",is_new)
	if ask:
		my_server.hset(temp_ad,"basic_item_ask",currencify(ask))
	if is_barter:
		my_server.hset(temp_ad,"basic_item_barter",is_barter)
	if uid:
		my_server.hset(temp_ad,"user_id",uid)
	if ad_id:
		my_server.hset(temp_ad,"ad_id",ad_id)
	if which_photo_hash and photo_id and photo_hash:
		my_server.hset(temp_ad,which_photo_hash,[photo_id, photo_hash])
	if photo_number:
		my_server.hset(temp_ad,photo_number,'inserted')
	if seller_name:
		my_server.hset(temp_ad,"seller_name",namify(seller_name))
	if city:
		my_server.hset(temp_ad,"city",namify(city))
	if town:
		my_server.hset(temp_ad,"town",namify(town))
	if submission_device:
		my_server.hset(temp_ad,"submission_device",submission_device)
	if on_fbs is not None:
		my_server.hset(temp_ad,"on_fbs",on_fbs)
	if csrf:
		my_server.hset(temp_ad,"csrf",csrf)
	if mob_nums:
		my_server.hset(temp_ad,"mob_nums",mob_nums)
	my_server.expire(temp_ad,SIX_HOURS) # will self-destruct after 6 hours of inactivity


def get_temporarily_saved_ad_data(user_id, id_only=False, all_photo_numbers=False, photo_hashes=False, full_ad=False, half_ad=False, mob_nums=False, only_csrf=False):
	my_server = redis.Redis(connection_pool=POOL)
	if id_only:
		return my_server.hget("ta:"+user_id,"ad_id")
	elif full_ad:
		desc, city, town, seller_name, is_new, ask, is_barter, ad_id, submission_device, on_fbs = my_server.hmget("ta:"+user_id,\
			"basic_item_description", "city", "town", "seller_name", "basic_item_new", "basic_item_ask", "basic_item_barter", "ad_id", "submission_device", "on_fbs")
		return {'desc':desc,'city':city,'user_id':user_id,'town':town,'seller_name':seller_name,'is_new':is_new,'ask':ask,'is_barter':is_barter,\
		'ad_id':ad_id,'submission_device':submission_device,'on_fbs':on_fbs}
	elif half_ad:
		desc, is_new, ask, is_barter, ad_id = my_server.hmget("ta:"+user_id, "basic_item_description", "basic_item_new", "basic_item_ask", "basic_item_barter", "ad_id")
		return {'desc':desc,'is_new':is_new,'ask':ask,'is_barter':is_barter,'ad_id':ad_id}
	elif mob_nums:
		mob_nums = my_server.hget("ta:"+user_id,"mob_nums")
		if mob_nums:
			return ast.literal_eval(mob_nums)
		else:
			return []
	elif only_csrf:
		return my_server.hget("ta:"+user_id,"csrf")
	elif all_photo_numbers:
		photo1 = True if my_server.hget("ta:"+user_id,"photo1") else False
		photo2 = True if my_server.hget("ta:"+user_id,"photo2") else False
		photo3 = True if my_server.hget("ta:"+user_id,"photo3") else False
		return photo1, photo2, photo3
	elif photo_hashes:
		return {'photo1_hash':my_server.hget("ta:"+user_id,"photo1_hash"),'photo2_hash':my_server.hget("ta:"+user_id,"photo2_hash"),\
		'photo3_hash':my_server.hget("ta:"+user_id,"photo3_hash")}



def check_status_of_temporarily_saved_ad(user_id,check_step_one=False,check_step_two=False):
	my_server = redis.Redis(connection_pool=POOL)
	key_name = "ta:"+user_id
	# change these steps if step_one changes
	if check_step_two and check_step_one:
		desc_exists = True if my_server.hget(key_name,"basic_item_description") else False
		is_new_exists = True if my_server.hget(key_name,"basic_item_new") else False
		is_barter_exists = True if my_server.hget(key_name, "basic_item_barter") else False
		ask_exists = True if my_server.hget(key_name,"basic_item_ask") else False
		if desc_exists and is_new_exists and is_barter_exists and ask_exists:
			check_step_one = True
		else:
			check_step_one = False
		photo_exists = True if (my_server.hget(key_name,"photo1_hash") or my_server.hget(key_name,"photo2_hash") or \
			my_server.hget(key_name,"photo3_hash")) else False
		if photo_exists:
			check_step_two = True
		else:
			check_step_two = False
		return check_step_one, check_step_two
	if check_step_one:
		desc_exists = True if my_server.hget(key_name,"basic_item_description") else False
		is_new_exists = True if my_server.hget(key_name,"basic_item_new") else False
		is_barter_exists = True if my_server.hget(key_name, "basic_item_barter") else False
		ask_exists = True if my_server.hget(key_name,"basic_item_ask") else False
		if desc_exists and is_new_exists and is_barter_exists and ask_exists:
			return True
		else:
			return False


def reset_temporarily_saved_ad(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.delete("ta:"+user_id)


def temporarily_save_buyer_snapshot(user_id=None, referrer=None, redirect_to=None, csrf=None, uid=None):
	my_server = redis.Redis(connection_pool=POOL)
	temp_storage = "ts:"+user_id
	if uid:
		my_server.hset(temp_storage,"user_id",uid)
	if referrer:
		my_server.hset(temp_storage,"referrer",referrer)
	if redirect_to:
		my_server.hset(temp_storage,"redirect_to",redirect_to)
	if csrf:
		my_server.hset(temp_storage,"csrf",csrf)
	my_server.expire(temp_storage,TWO_HOURS) # will self-destruct after 2 hours of inactivity

def get_buyer_snapshot(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	temp_storage = "ts:"+user_id
	if my_server.exists(temp_storage):
		return my_server.hgetall("ts:"+user_id)
	else:
		return {}

def temporarily_save_user_csrf(user_id, csrf):
	my_server = redis.Redis(connection_pool=POOL)
	temp_csrf = "csrf:"+user_id
	my_server.setex(temp_csrf,csrf,TWO_HOURS) # will self-destruct after 2 hours of inactivity


def get_user_csrf(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.get("csrf:"+user_id)


def get_approved_places(city='all_cities',withscores=False):
	my_server = redis.Redis(connection_pool=POOL)
	if city == 'all_cities':
		locs = my_server.zrevrange("approved_locations",0,-1,withscores=withscores)
	else:
		locs = my_server.zrevrange("at:"+city,0,-1,withscores=withscores)
	if withscores:
		return [(string_tokenizer(loc),score) for (loc,score) in locs]
	else:
		return [string_tokenizer(loc) for loc in locs]


# used to show total ads' count
def get_all_pakistan_ad_count():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.llen("global_ads_list")

# this is the list of all categories entered by agents for classifieds they approve
def get_classified_categories():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.zrevrange("classified_categories",0,-1)


# keeps track of who visited the classified approval dashboard, in order to avoid agent collisions
def get_and_set_classified_dashboard_visitors(username, withtime=False):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zadd("classified_dashboard_visitors",username,time.time())
	username_and_time = my_server.zrevrange("classified_dashboard_visitors",0,-1,withscores=withtime)
	pipeline1 = my_server.pipeline()
	for username, visit_time in username_and_time:
		pipeline1.get("cb:"+username)
	scores = pipeline1.execute()
	usernames_times_scores = []
	counter = 0
	for item in username_and_time:
		if scores[counter]:
			usernames_times_scores.append((item[0],item[1],scores[counter]))
		else:
			usernames_times_scores.append((item[0],item[1]))
		counter += 1
	return usernames_times_scores



def get_user_unfinished_ad(server,user_id):
	if server.exists("ta:"+user_id):
		unfinished_user_ad = server.hgetall("ta:"+user_id)
		# the following deletes ad hash if it has been wiped
		if not server.zscore("unfinished_classifieds",unfinished_user_ad["ad_id"]):
			server.delete("ta:"+user_id)
			unfinished_user_ad = {}
		return unfinished_user_ad
	else:
		return {}


def get_all_approved_user_ads(server,user_id):
	approved_user_ad_ids = server.lrange("uaa:"+user_id,0,-1)
	pipeline1 = server.pipeline()
	for ad_id in approved_user_ad_ids:
		pipeline1.hgetall("ad:"+ad_id)
	result1 = pipeline1.execute()
	for ad in result1:
		if "click_details" in ad:
			ad["click_details"] = ast.literal_eval(ad["click_details"])
	return result1


def get_all_unapproved_user_ads(server,user_id,withscores):
	unapproved_user_ad_strings = server.zrange("unc:"+user_id,0,-1,withscores=withscores)
	unapproved_ads = []
	for ad in unapproved_user_ad_strings:
		ad = ast.literal_eval(ad)
		ad_id = ad["ad_id"]
		if server.zcount("unapproved_ads",ad_id,ad_id):
			unapproved_ads.append(ad)
		else:
			# delete the entry if it doesn't exist in unapproved_ads
			server.zremrangebyscore("unc:"+user_id,ad_id,ad_id)
	return unapproved_ads


def get_all_expired_user_ads(server, user_id):
	expired_ad_ids = server.lrange("uea:"+user_id,0,-1)
	pipeline1 = server.pipeline()
	for ad_id in expired_ad_ids:
		pipeline1.hgetall("ad:"+ad_id)
	result1 = pipeline1.execute()
	for ad in result1:
		if "click_details" in ad:
			ad["click_details"] = ast.literal_eval(ad["click_details"])
	return result1


def get_all_user_ads(user_id,withscores=False):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	unfinished_user_ad = get_user_unfinished_ad(my_server,user_id)
	unapproved_user_ads = get_all_unapproved_user_ads(my_server, user_id, withscores)
	approved_user_ads = get_all_approved_user_ads(my_server, user_id)
	expired_user_ads = get_all_expired_user_ads(my_server, user_id)
	return unfinished_user_ad, unapproved_user_ads, approved_user_ads, expired_user_ads


# used to show ad details for a single ad (when potential buyer clicks 'contact' in an ad's listing)
def get_single_approved_ad(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.hgetall("ad:"+str(ad_id))

# return entire ad details for all ids passed (used in global and city-wise ad listings)
def get_ad_objects(id_list):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for id in id_list:
		pipeline1.hgetall("ad:"+id)
	return pipeline1.execute()

# used to show all ads in our "global" ad listing page
def get_approved_ad_ids(exchange=False,photos=False):
	my_server = redis.Redis(connection_pool=POOL)
	if photos:
		return my_server.lrange("global_photo_ads_list",0,-1)
	elif exchange:
		return my_server.lrange("global_exchange_ads_list",0,-1)
	# elif mobile:
	#   return my_server.lrange("global_mobile_ads_list",0,-1)
	else:
		return my_server.lrange("global_ads_list",0,-1)


def get_city_ad_ids(city_name, exchange=False, photos=False):
	my_server = redis.Redis(connection_pool=POOL)
	if photos:
		return my_server.lrange("afa:"+city_name, 0, -1) # used for city-wide view
	elif exchange:
		return my_server.lrange("aea:"+city_name, 0, -1) # used for city-wide view
	# elif mobile:
	#   return my_server.lrange("ama:"+city_name, 0, -1) # used for city-wide view
	else:
		return my_server.lrange("aa:"+city_name, 0, -1) # used for city-wide view


def get_basic_item_ad_id():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.incr("basic_item_ad_id")

def who_locked_ad(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	ad_list = my_server.zrangebyscore("unapproved_ads",ad_id,ad_id)
	if ad_list:
		ad = ast.literal_eval(ad_list[0])
		if "locked_by" in ad:
			return ad["locked_by"]
		else:
			return None
	else:
		return None

# used by agents in classified approval process, so that other agents don't erroneously edit the ad
def lock_unapproved_ad(ad_id, username, locker_id):
	my_server = redis.Redis(connection_pool=POOL)
	ad = ast.literal_eval(my_server.zrangebyscore("unapproved_ads",ad_id,ad_id)[0])
	if "locked_by" in ad:
		# already locked
		return False, ad["locked_by"]
	else:
		# lock it
		ad["locked_by"] = username
		my_server.zremrangebyscore("unapproved_ads",ad_id, ad_id)
		my_server.zadd("unapproved_ads",ad,ad_id)
		my_server.lpush("ala:"+str(locker_id),ad_id) # agent's locked ads (ala:)
		return True, username


def unlock_unapproved_ad(ad_id, username, locker_id):
	my_server = redis.Redis(connection_pool=POOL)
	ad = ast.literal_eval(my_server.zrangebyscore("unapproved_ads",ad_id,ad_id)[0])
	if "locked_by" in ad and ad["locked_by"] == username:
		ad.pop("locked_by")
		my_server.zremrangebyscore("unapproved_ads",ad_id, ad_id)
		my_server.zadd("unapproved_ads",ad,ad_id)
		my_server.lrem("ala:"+str(locker_id),ad_id)
		return True, username
	elif "locked_by" not in ad:
		return False, False
	elif ad["locked_by"] != username:
		return False, ad["locked_by"]
	else:
		return False,False


# used to populate the classified approval dashboard for agents
def get_unapproved_ads(user_id, withscores = False, only_locked=False):
	my_server = redis.Redis(connection_pool=POOL)
	if only_locked == '1':
		required_ad_ids = my_server.lrange("ala:"+str(user_id),0,-1)
		pipeline1 = my_server.pipeline()
		for id_ in required_ad_ids:
			pipeline1.zrangebyscore("unapproved_ads",id_,id_)
		result = pipeline1.execute()
		if result:
			if withscores:
				counter = 0
				ads = []
				for ad_body in result:
					ads.append((ad_body[0],float(required_ad_ids[counter])))
					counter += 1
				return ads
			else:
				return result
		else:
			return []
	else:
		return my_server.zrange("unapproved_ads",0,-1,withscores=withscores)

# used when seller himself deletes an ad (of the 'unverified' variety)
def get_unfinished_photo_ids_to_delete(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.lrange("rc:"+ad_id,0,-1)



# used by seller to edit ad fields while it's in an 'unverified' state
def edit_unfinished_ad_field(ad_id,user_id,field,new_text):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	field = temporary_ad_field_mapping(field) # some field names may differ
	if my_server.exists("ta:"+user_id):
		if field == 'basic_item_new':
			if new_text == '1':
				my_server.hset("ta:"+user_id,field,'Istamal shuda')
			elif new_text == '2':
				my_server.hset("ta:"+user_id,field,'Bilkul new')
		elif field == 'basic_item_barter':
			if new_text == '1':
				my_server.hset("ta:"+user_id,field,'Paisey aur badley mein cheez dono')
			elif new_text == '2':
				my_server.hset("ta:"+user_id,field,'Sirf paisey')
		else:
			my_server.hset("ta:"+user_id,field,new_text)
		# update submission time of advert too, so that it doesn't get expired all of a sudden
		my_server.zadd("unfinished_classifieds",ad_id,time.time())



# used by agents to 'clean up' spelling mistakes (etc) in ads before approving them
def edit_single_unapproved_ad(ad_id,field,new_text):
	my_server = redis.Redis(connection_pool=POOL)
	ad = ast.literal_eval(my_server.zrangebyscore("unapproved_ads",ad_id,ad_id)[0])
	if field == 'is_new':
		if new_text == '0':
			ad.pop('is_new',None)
		elif new_text == '1':
			ad['is_new'] = 'Istamal shuda'
		elif new_text == '2':
			ad['is_new'] = 'Bilkul new'
	elif field == 'photos':
		if "photos" in ad:
			counter = 0
			for photo,status in ad["photos"]:
				if photo == new_text:
					ad["photos"][counter] = (photo,True)
				elif status == True:
					ad["photos"][counter] = (photo,False)
				counter += 1
	else:
		ad[field] = new_text
	my_server.zremrangebyscore("unapproved_ads",ad_id, ad_id)
	my_server.zadd("unapproved_ads",ad,ad_id)


# temporarily saving ad that seller hasn't verified mobile number for yet
def save_single_unfinished_ad(context):
	my_server = redis.Redis(connection_pool=POOL)
	ad_id = context["ad_id"]
	photo_ids = my_server.lrange("rc:"+str(ad_id),0,-1)
	if photo_ids:
		my_server.hset("ta:"+str(context["user_id"]),"photos",photo_ids) # adding photos to the unfinished ad
	my_server.zadd("unfinished_classifieds",ad_id,time.time())

# used by agents to delete 'declined' ads from the ad approval dashboard
def del_single_unapproved_ad(ad_id, closer_id):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	pipeline1.zremrangebyscore("unapproved_ads", ad_id, ad_id)
	pipeline1.lrem("ala:"+closer_id,ad_id)
	pipeline1.execute()

# used to delete 'unfinished' (i.e 'unverified') ads, either by the seller herself, or initiated periodically by the system (schedule set in settings.py)
def del_orphaned_classified_photos(time_ago=FORTY_FIVE_MINS,user_id=None,ad_id=None):
	my_server = redis.Redis(connection_pool=POOL)
	if user_id and ad_id:
		pipeline1 = my_server.pipeline()
		pipeline1.delete("ta:"+user_id)
		pipeline1.zrem("unfinished_classifieds",ad_id)
		pipeline1.zrem("unfinalized_used_item_photos",ad_id)
		pipeline1.delete("rc:"+ad_id)
		pipeline1.execute()
	else:
		import operator
		# deleting orphaned ads from 45 mins ago
		cut_off_time = time.time() - time_ago
		ad_ids = my_server.zrangebyscore("unfinished_classifieds",'-inf','('+str(cut_off_time))
		if ad_ids:
			my_server.zrem("unfinished_classifieds",*ad_ids)
		# deleting orphaned photos from 45 mins ago
		ad_ids_with_times = my_server.zrangebyscore("unfinalized_used_item_photos",'-inf','('+str(cut_off_time), withscores=True)
		if ad_ids_with_times:
			score_range = []
			ad_ids = []
			for ad_and_time in ad_ids_with_times:
				ad_ids.append(ad_and_time[0])
				score_range.append(ad_and_time[1])
			pipeline1 = my_server.pipeline()
			for ad_id in ad_ids:
				pipeline1.lrange("rc:"+ad_id,0,-1)
			photo_ids_to_delete = reduce(operator.add, pipeline1.execute())
			pipeline2 = my_server.pipeline()
			for ad_id in ad_ids:
				pipeline2.delete("rc:"+ad_id)
			pipeline2.execute()
			my_server.zremrangebyscore("unfinalized_used_item_photos",min(score_range),max(score_range))
			return photo_ids_to_delete
		else:
			return None

def set_ecomm_photos_secret_key(user_id, secret_key):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	my_server.setex("epusk:"+user_id,secret_key,FORTY_FIVE_MINS)

def get_and_delete_ecomm_photos_secret_key(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	secret_key = my_server.get("epusk:"+user_id)
	if secret_key:
		my_server.delete("epusk:"+user_id)
		return secret_key
	else:
		return '1'

#####################E Commerce#######################

# logging orders by users from cities we aren't servicing
def log_unserviced_city(orderer_id,location,merch):
	my_server = redis.Redis(connection_pool=POOL)
	#add composite_id in sorted set that will lexicographically sort itselfs
	payload = "loc:"+str(location)+":item:"+str(merch)+":uid:"+str(orderer_id)
	my_server.zadd("unserviced_cities",payload,0)

# logging completed orders: mobile num, user_id, name, address, city, order_time, item
def log_completed_orders():
	my_server = redis.Redis(connection_pool=POOL)
	pass

#####################Advertiser!!!###################

def save_advertiser(name, detail, mobile, loc, publishing_time, username):
	my_server = redis.Redis(connection_pool=POOL)
	advertiser_details = "advertiser_details"
	payload = {"name":name,"detail":detail,"mobile":mobile,"city":loc,"publishing_time":publishing_time,"nickname":username}
	my_server.lpush(advertiser_details,str(payload))

def get_advertisers():
	my_server = redis.Redis(connection_pool=POOL)
	advertiser_details = "advertiser_details"
	return my_server.lrange(advertiser_details,0,-1)

def purge_advertisers():
	my_server = redis.Redis(connection_pool=POOL)
	advertiser_details = "advertiser_details"
	my_server.delete(advertiser_details)

def export_advertisers():
	my_server = redis.Redis(connection_pool=POOL)
	advertiser_details = "advertiser_details"
	list_of_dict = my_server.lrange(advertiser_details,0,-1)
	filename = 'advertisers_'+str(int(time.time()))+'.csv'
	if list_of_dict:
		import csv, ast
		with open(filename,'wb') as f:
			wtr = csv.writer(f)
			columns = ["name","nickname","mobile","city","detail","submission_time"]
			wtr.writerow(columns) # writing the columns
			for advertiser in list_of_dict:
				dictionary = ast.literal_eval(advertiser)
				time_string = datetime.fromtimestamp(dictionary["publishing_time"]).strftime("%Y-%m-%d %H:%M:%S")
				name = dictionary["name"].encode('utf-8')
				if dictionary["nickname"] is not None:
					nickname = dictionary["nickname"].encode('utf-8')
				else:
					nickname = dictionary["nickname"]
				mobile = dictionary["mobile"].encode('utf-8')
				city = dictionary["city"].encode('utf-8')
				detail = dictionary["detail"].encode('utf-8')
				to_write = [name,nickname,mobile,city,detail,time_string]
				wtr.writerows([to_write])
		my_server.delete(advertiser_details)
		return True
	else:
		return False

#####################################################

def save_post(text):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.set("optimizely_test",text)

def get_temp_id():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.incr("temp_user_id")

##########Logging Home Gibberish Writers#############


def log_gibberish_text_writer(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	gibberish_writers = 'gibberish_writers'
	my_server.zincrby(gibberish_writers,user_id,amount=1)

def get_gibberish_text_writers():
	my_server = redis.Redis(connection_pool=POOL)
	gibberish_writers = 'gibberish_writers'
	gibberish_writers_and_scores = my_server.zrange(gibberish_writers,0,-1, withscores=True)
	my_server.delete(gibberish_writers)
	return gibberish_writers_and_scores

def queue_punishment_amount(user_id, penalty):
	my_server = redis.Redis(connection_pool=POOL)
	punishment_text = "pt:"+str(user_id)
	try:
		my_server.incrby(punishment_text,amount=int(penalty))
		my_server.expire(punishment_text,ONE_WEEK)
	except:
		pass

def get_gibberish_punishment_amount(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	punishment_text = "pt:"+str(user_id)
	amount = my_server.get(punishment_text)
	if amount:
		return float(amount)
	else:
		return None


#####################################################

PASSWORD_ERRORS = "password_errors"#"likho_errors"

def log_erroneous_passwords(password,error_string):
	my_server = redis.Redis(connection_pool=POOL)
	password_errors = PASSWORD_ERRORS
	my_server.lpush(password_errors,{'password':password,'error_string':error_string})

def retrieve_erroneous_passwords():
	my_server = redis.Redis(connection_pool=POOL)
	# import unicodecsv as ucsv
	import csv, ast
	password_errors = PASSWORD_ERRORS
	list_ = my_server.lrange(password_errors,0 ,-1)
	with open('password_errors.csv','wb') as f:
		wtr = csv.writer(f)
		wtr.writerows([ast.literal_eval(list_[0]).keys()]) # writing the columns
		for string in list_:
			try:
				dictionary = ast.literal_eval(string)
				to_write = [dictionary["password"],dictionary["error_string"].encode('utf-8')]
				wtr.writerows([to_write])
			except:
				pass

#############################################################################################################################
#####################################################Optimizely Experiment###################################################

# def get_user_type(user_id, best=False, algo=False):
#   my_server = redis.Redis(connection_pool=POOL)
#   key_name = "ob:"+str(user_id)
#   if my_server.exists(key_name):
#       if best and algo:
#            data = my_server.hgetall(key_name)
#            if data:
#               return data["best"], data["algo"]
#            else:
#               return None
#       elif best:
#           return my_server.hget(key_name, 'best')
#       elif algo:
#           return my_server.hget(key_name, 'algo')
#   else:
#       return None


# def set_user_type(var_value, user_id, best, algo):
#   my_server = redis.Redis(connection_pool=POOL)
#   key_name = "ob:"+str(user_id)
#   mapping = {'best':best,'algo':algo,'var':var_value}
#   my_server.hmset(key_name,mapping)
#   my_server.expire(key_name,ONE_WEEK)

#############################################################################################################################
#####################################################Notifying Damadam Outage###############################################

def seen_outage_notif(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists("maint:"+str(user_id)):
		return True
	else:
		return False
	

def skip_outage(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.setex("maint:"+str(user_id),'1',TWO_WEEKS)


###########################################################

def add_mobile_customer(user_id,star_ids, type_):
	"""
	"""
	my_server = redis.Redis(connection_pool=POOL)
	set_name = 'mobile_consultancy_'+type_
	my_server.sadd(set_name,user_id)
	all_ids = my_server.smembers(set_name)
	relevant_ids_in_order = []
	for star_id in star_ids:
		if str(star_id) in all_ids:
			relevant_ids_in_order.append(star_id)
	return my_server.scard(set_name), relevant_ids_in_order, all_ids - set(relevant_ids_in_order)

###########################################################

def return_all_ad_data():
	my_server = redis.Redis(connection_pool=POOL)
	ad_ids = my_server.lrange("global_ads_list", 0, -1)
	expired_ad_ids = my_server.zrange("global_expired_ads_list", 0, -1)
	pipeline1 = my_server.pipeline()
	for ad_id in ad_ids:
		pipeline1.hgetall("ad:"+ad_id)
	result1 = pipeline1.execute()
	pipeline2 = my_server.pipeline()
	for ad_id in expired_ad_ids:
		pipeline2.hgetall("ad:"+ad_id)
	result2 = pipeline2.execute()
	return result1, result2


###################### First Time User Tutorials #########################

'0' 'personal group anonymous invite'
'1' 'personal group sms settings'
'2' 'granting permission to save posts'
'3' 'sharing internal photo in personal groups'
'4' 'visiting shared photos listing'

def tutorial_unseen(user_id, which_tut, renew_lease=False):
	"""
	Gives a tutorial if the user is visiting a section for the first time
	
	'0' 'personal group anonymous invite'
	'1' 'personal group sms settings'
	'2' 'granting permission to save posts'
	'3' 'sharing internal photo in personal groups'
	'4' 'visiting shared photos listing'
	'5' 'first time home publicreplier'
	'6' 'first time Damadam defender'
	'7' 'first time object reporter'
	'8' 'first time object culler'
	'9' 'first time banner'
	'10' 'first time user-reported content judger'
	'11' 'first time home sharer'
	'12' 'first time voting judger'
	'13' 'first time fanner'
	'14' 'first time refresher of private mehfil, public mehfil, matka, jawabs'
	'15' 'first time public mehfil online list viewer'
	'16' 'first time private mehfil online list viewer'
	'17' 'first time public mehfil creator'
	'18' 'first time visitor of officer activity in public mehfils'
	'19' 'first time instruction viewer in invited users list'
	'20' 'first time unseen matka'
	'21' 'first time public mehfil feedback viewer'
	'22' 'first time public mehfil feedback giver'
	'23' 'first time instruction viewer in private mehfil invited users list'
	'24' 'first time visitor of member activity in private mehfils'
	'25' 'first time viewer of sharing tutorial'
	'26' 'first time foto sharer'
	'27' 'first time password change'
	'28' 'first time officership applier'
	'29' 'first time officer applications list viewer'
	'30' 'first time officer dashboard viewing'
	"""
	my_server = redis.Redis(connection_pool=POOL)
	key_name = "tk:"+str(user_id)+":"+str(which_tut)
	if my_server.exists(key_name):
		if renew_lease:
			# increase TTL if renew_lease is passed
			my_server.expire(key_name,TWO_WEEKS)
		return False
	else:
		my_server.setex(key_name,1,ONE_MONTH)
		return True

###################### Retrieving all mobile numbers ######################

def retrieve_all_mobile_numbers():
	"""
	Return all mobile numbers and their associated user ids
	"""
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.zrange('verified_numbers',0,-1,withscores=True)

def retrieve_numbers_with_country_codes(list_of_user_ids):
	"""
	"""
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for user_id in list_of_user_ids:
		pipeline1.lrange("um:"+str(user_id), 0, -1)
	return pipeline1.execute()


############################ Unverifying users ############################


def remove_verified_mob(target_user_ids):
	"""
	Removes mobile verification credentials of given list of user ids

	Useful when deprecating a username
	Can also be used to give users the ability to remove their own mobile numbers from file
	"""
	if target_user_ids:
		target_user_ids = map(str, target_user_ids)
		my_server = redis.Redis(connection_pool=POOL)
		pipeline1 = my_server.pipeline()
		for user_id in target_user_ids:
			pipeline1.lrange("um:"+user_id,0,-1)
		result1 = pipeline1.execute()# output is a list of lists
		nums_to_remove, users_to_remove, counter = [], [], 0
		#############################################################
		for verification_data in result1:
			num_tups = len(verification_data)
			if num_tups == 2:
				# this user has 2 numbers on file
				nums_to_remove.append(ast.literal_eval(verification_data[0])['national_number'])
				nums_to_remove.append(ast.literal_eval(verification_data[1])['national_number'])
				users_to_remove.append(target_user_ids[counter])
			elif num_tups == 1:
				# this user has 1 number on file
				nums_to_remove.append(ast.literal_eval(verification_data[0])['national_number'])
				users_to_remove.append(target_user_ids[counter])
			else:
				# this user wasn't verified - hence append nothing in the final lists
				pass
			counter += 1
		if nums_to_remove and users_to_remove:
			pipeline2 = my_server.pipeline()
			#############################################################
			pipeline2.zrem("ecomm_verified_users",*users_to_remove)
			#############################################################
			pipeline2.zrem("verified_numbers",*nums_to_remove)
			#############################################################
			for user_id in users_to_remove:
				pipeline2.delete("um:"+user_id)# can be replaced by 'unlink'
			pipeline2.execute()
		else:
			# no numbers were found - do nothing (e.g. because a list of unverified users was passed to this function)
			pass
	else:
		pass


###################### setting user's world age ######################

def set_world_age(user_id):
	"""
	Increments user's age on the platform

	A hit increments the counter by 1 and the sets a six-hour rate limit
	If user returns after those six hours, the counter goes up again
	This way, a person with age 4 has at least visited the website in 4 different intervals separated by at least 6 hours
	"""
	user_id = str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	if not my_server.exists('warl:'+user_id):
		my_server.zincrby('world_age',user_id,amount=1)
		my_server.zadd('world_age_last_increment',user_id,time.time())
		my_server.setex('warl:'+user_id,'1',SIX_HOURS)


def retrieve_user_world_age(user_id_list, with_highest_age=False):
	"""
	Given a list of user_ids, this retrieves their world age and returns a dictionary

	if 'with_highest_age' is set to 'True', the highest world age is returned as well so that world ages can be normalized
	"""
	if user_id_list:
		my_server = redis.Redis(connection_pool=POOL)
		pipeline1 = my_server.pipeline()
		for user_id in user_id_list:
			pipeline1.zscore('world_age',user_id)
		result1, counter, final_result = pipeline1.execute(), 0, {}
		for user_id in user_id_list:
			user_age = result1[counter]
			final_result[user_id] = user_age if user_age else 1
			counter += 1
		if with_highest_age:
			return final_result, my_server.zrevrange('world_age',0,0,withscores=True)[0][1]
		else:
			return final_result
	else:
		if with_highest_age:
			return {}, None
		else:
			return {}

################################ Self-written mobile verification ################################


def create_random_pool(my_server=None):
	"""
	Create a random pool of 5 digit numbers, append leading 0's, store in a list
	"""
	import random
	pin_codes = []
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	pool_ver = str(my_server.incr("pin_code_pool_ver"))
	for rand_num in random.sample(xrange(1,100001),100000):# generates 100000 random numbers between 1 and 100000
		pin_codes.append("%05d" % rand_num)
	my_server.lpush('pin_codes_pool:'+pool_ver,*pin_codes)
	return pool_ver

def retrieve_random_pin(target_user_id):
	"""
	Generates a random 5 digit pin
	
	If an already-bound pin exists, it returns that, otherwise it generates a new one
	"""
	target_user_id = str(target_user_id)
	my_server = redis.Redis(connection_pool=POOL)
	current_pool_version = str(my_server.get('pin_code_pool_ver'))
	existing_pin = my_server.get('pcb:'+target_user_id)
	pool_exists = my_server.exists("pin_codes_pool:"+current_pool_version)
	if pool_exists:
		if existing_pin:
			data = existing_pin.split(":")
			if data[1] == current_pool_version:
				return data[0]
			else:
				my_server.delete('pcb:'+target_user_id)
		rand_pin = my_server.lpop('pin_codes_pool:'+current_pool_version)
		my_server.setex('pcb:'+target_user_id,rand_pin+":"+current_pool_version,TEN_MINS)
		return rand_pin
	else:
		# pool does not exist
		new_pool_ver = create_random_pool(my_server=my_server)
		rand_pin = my_server.lpop('pin_codes_pool:'+new_pool_ver)
		my_server.setex('pcb:'+target_user_id,rand_pin+":"+new_pool_ver,TEN_MINS)
		return rand_pin

def verify_user_pin(target_user_id, entered_pin_code):
	"""
	Verifies that the entered pin is indeed the one that belongs to the user, i.e. the user is not 'fluking' their way to verification
	"""
	target_user_id = str(target_user_id)
	my_server = redis.Redis(connection_pool=POOL)
	current_pool_version = str(my_server.get('pin_code_pool_ver'))
	pool_exists = my_server.exists("pin_codes_pool:"+current_pool_version)
	if pool_exists:
		data = my_server.get('pcb:'+target_user_id)
		if data:
			try:
				payload = data.split(":")
			except AttributeError:
				return False, 'pin_invalid'
			pin, pool_ver = payload[0], payload[1]
			if str(entered_pin_code) == pin:
				if pool_ver == current_pool_version:
					invalidate_user_pin(target_user_id,my_server)
					return True, 'pin_matched'
				else:
					# pool expired - the pool versions didn't match
					return False, 'pin_invalid'
			else:
				return False, 'pin_incorrect'
		else:
			# pin does not exist, meaning it's too late
			return False, 'pin_expired'
	else:
		# pool doesn't - the pool versions didn't match
		return False, 'pin_invalid'


def is_sms_sending_rate_limited(target_user_id):
	"""
	Retrieves the ttl in case sms sending is rate limited (for verification purposes)
	"""
	ttl = redis.Redis(connection_pool=POOL).ttl('pcb:'+str(target_user_id))
	if ttl > 2:
		return ttl
	else:
		return None


def invalidate_user_pin(user_id, my_server=None):
	"""
	Invalidates (deletes) rate limit on user mobile entry
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.delete('pcb:'+str(user_id))

def log_pin_attempt(user_id):
	"""
	Log the fact that pin is entered - if it happens way too many times, rate-limit the user
	"""
	user_id = str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	# check if user already rate-limited
	ttl = my_server.ttl('rlpa:'+user_id)
	if ttl > 1:
		return False, ttl
	else:
		# log the attempt
		attempts = my_server.incr('pa:'+user_id)
		my_server.expire('pa:'+user_id,TEN_MINS)
		if attempts > 12:
			my_server.setex('rlpa:'+user_id,'1',TWO_HOURS)
			return False, TWO_HOURS
		else:
			return True, None


def set_forgot_password_rate_limit(user_id):
	"""
	Once password has been retrieved via "forgot password", rate-limit user from immediately trying again
	"""
	redis.Redis(connection_pool=POOL).setex("prrl:"+str(user_id),'1',TWO_HOURS)

def is_forgot_password_rate_limited(user_id):
	"""
	Checks if user already recently reset their password, and stops them from doing it again so soon
	"""
	ttl = redis.Redis(connection_pool=POOL).ttl("prrl:"+str(user_id))
	if ttl > 3:
		return ttl
	else:
		return None

########################################  Account Kit User Verification ####################################


ACCOUNT_KIT_SECRET_STORE = 'akss:'#key that stores a temporary token while a user is going through verification flow

def save_user_account_kit_server_secret(identifier, secret, mob_num_as_key=False):
	"""
	This saves a 'secret' uuid key that helps identify users as they jump out to Account Kit and then subsequently return

	'identifier' can either be a user_id (in case of user account verification flow) or a mobile number (in case of forgot pass flow)
	"""
	if mob_num_as_key:
		# existence of 'f:' in key name signifies that this is related to the forgot password flow
		redis.Redis(connection_pool=POOL).setex(ACCOUNT_KIT_SECRET_STORE+"f:"+str(identifier),secret,FORTY_FIVE_MINS)
	else:
		redis.Redis(connection_pool=POOL).setex(ACCOUNT_KIT_SECRET_STORE+str(identifier),secret,FORTY_FIVE_MINS)


def retrieve_user_account_kit_secret(identifier, from_forgot_pass=False):
	"""
	This retrieves the 'secret' uuid key to be used to ascertain whether the same user returned from Account Kit's flow

	'identifier' can either be a user_id (in case of user account verification flow) or a mobile number (in case of forgot pass flow)
	"""
	if from_forgot_pass:
		# existence of 'f:' in key name signifies that this is related to the forgot password flow
		return redis.Redis(connection_pool=POOL).get(ACCOUNT_KIT_SECRET_STORE+"f:"+str(identifier))
	else:
		return redis.Redis(connection_pool=POOL).get(ACCOUNT_KIT_SECRET_STORE+str(identifier))


################################################### Accountkit usage related loggers ###########################

def log_ak_entered():
	"""
	this function logs the number of users funnelled to Accountkit for verification
	"""
	redis.Redis(connection_pool=POOL).incr("entered_ak_count")


def log_ak_user_verification_outcome(reason):
	"""
	this function logs the number of verified users through Accountkit
	"""
	if reason == 'verified':
		redis.Redis(connection_pool=POOL).incr("verified_on_ak_count")
	elif reason == 'pressed_cross':
		redis.Redis(connection_pool=POOL).incr("pressed_x_on_ak_count")
	elif reason == 'number_already_used':
		redis.Redis(connection_pool=POOL).incr("number_already_used_ak_count")
	elif reason == 'verification_failed_reason4':
		redis.Redis(connection_pool=POOL).incr("not_verified_reason4_count")
	elif reason == 'verification_failed_reason5':
		redis.Redis(connection_pool=POOL).incr("not_verified_reason5_count")
	elif reason == 'sms_expired':
		redis.Redis(connection_pool=POOL).incr("sms_expired_count")
	elif reason == 'id_already_verified':
		redis.Redis(connection_pool=POOL).incr("id_already_verified_count")


################################################### Accountkit forgot password related loggers ###################


def log_fp_ak_entered():
	"""
	this function logs the number of Forgot password user funnelled to Accountkit for verification
	"""
	redis.Redis(connection_pool=POOL).incr("entered_fp_ak_count")


def log_fp_ak_user_verification_outcome(reason):
	"""
	this function logs the number of Accountkit errors for users in forgot password funnel
	"""
	pass
	if reason == 'ratelimited_before_ak':
		redis.Redis(connection_pool=POOL).incr("forgetter_ratelimited_before_ak_count")
	elif reason == 'ratelimited_after_ak':
		redis.Redis(connection_pool=POOL).incr("forgetter_ratelimited_after_ak_count")
	elif reason == 'verified':
		redis.Redis(connection_pool=POOL).incr("change_password_success_count")
	elif reason == 'forgetters_userid_missing':
		redis.Redis(connection_pool=POOL).incr("forgetters_userid_missing_count")
	elif reason == 'forgetter_using_someone_elses_number':
		redis.Redis(connection_pool=POOL).incr("forgetter_using_someone_elses_number_count")
	elif reason == 'forgetter_on_setting_pass_screen':
		redis.Redis(connection_pool=POOL).incr("forgetter_on_setting_pass_screen_count")
	elif reason == 'forgetters_number_questionable':
		redis.Redis(connection_pool=POOL).incr("forgetters_number_questionable_count")
	elif reason == 'forgetter_ran_into_unknown_error':
		redis.Redis(connection_pool=POOL).incr("forgetter_ran_into_unknown_error_count")


################################################### Twilio usage related loggers ###########################

def twiliolog_pin_sms_sent(forgot_pass=False):
	"""
	this function logs the number of smses sent out for verification
	"""
	if forgot_pass:
		redis.Redis(connection_pool=POOL).incr("twilio_forgot_pass_sms_count") 
	else:
		redis.Redis(connection_pool=POOL).incr("twilio_sms_count") 


def twiliolog_user_verified(forgot_pass=False):
	"""
	this function logs the number of verified users through twilio
	"""
	if forgot_pass:
		redis.Redis(connection_pool=POOL).incr("twilio_forgot_pass_verified_count")
	else:
		redis.Redis(connection_pool=POOL).incr("twilio_verified_count")


def twiliolog_reverification_pin_sms_sent(forgot_pass=False):
	"""
	This function logs the number of smses sent out for reverification
	"""
	redis.Redis(connection_pool=POOL).incr("twilio_reverified_sms_count") 


def twiliolog_user_reverified(forgot_pass=False):
	"""
	This function logs the number of reverified users through twilio
	"""
	redis.Redis(connection_pool=POOL).incr("twilio_reverified_count")

def log_fbs_please_wait(user_id, expire_at):
	"""
	Logging all users shown a prompt (only does it once for each user_id) 

	verified_on_data_after_being_prompted_on_fbs_before_rl_expiry' / 'prompted_on_fbs_to_wait' yields conversion rate of people who go to paid internet from fbs
	"""
	user_id = str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	was_key_set = my_server.setnx("uvfbs:"+user_id,expire_at)
	if was_key_set:
		my_server.expire("uvfbs:"+user_id,ONE_WEEK)
		my_server.incr("prompted_on_fbs_to_wait") # but not YET told that via "paid" internet, the user can verify right away
	
def log_fbs_user_verification(user_id, on_fbs, time_now):
	"""
	Logging users' mobile verification
	"""
	my_server = redis.Redis(connection_pool=POOL)
	expire_at = my_server.get('uvfbs:'+str(user_id))
	if expire_at:
		# this user was prompted on FBS
		if int(expire_at) > time_now:
			# blocked from verifying on FBS
			if on_fbs:
				my_server.incr('verified_on_fbs_after_being_prompted_on_fbs_before_rl_expiry')# should not happen, should be 0
			else:
				my_server.incr('verified_on_data_after_being_prompted_on_fbs_before_rl_expiry')# these people converted to paid internet from FBS for verification purposes
		else:
			# allowed to verify on FBS (i.e. waited the requisite time)
			if on_fbs:
				my_server.incr('verified_on_fbs_after_being_prompted_on_fbs_after_rl_expiry')
			else:
				# this user chose to verify on data even though they could have verified on FBS
				my_server.incr('verified_on_data_after_being_prompted_on_fbs_after_rl_expiry')# should be a very rare occurence
		# get rid of the key
		my_server.delete('uvfbs:'+str(user_id))
	else:
		# this user was never prompted on FBS
		if on_fbs:
			my_server.incr('verified_on_fbs_after_waiting_one_day_without_prompt')# these users opt to wait a day instead of going on paid internet
		else:
			my_server.incr('verified_on_data_without_prompt')# these users verified on data (and never received the FBS prompt)

#########################################Invalid Nickname Logger##################################

def invalid_nick_logger(banned_word,nick):
	"""
	this function logs the nicks that were filtered by abuse.py

	Works both for new nick creation and forgotten nicks
	"""
	myserver = redis.Redis(connection_pool=POOL)
	myserver.lpush("invalid_nicks",nick+":"+banned_word)
	myserver.ltrim("invalid_nicks",0,999)
	
def log_post_banned_username(username):
	"""
	This function logs a username that has been created after the user has atleast ONCE hit the "abuse" dictionary
	"""
	myserver = redis.Redis(connection_pool=POOL)
	myserver.lpush("post_abuse_nicks",username)
	myserver.ltrim("post_abuse_nicks",0,999)


######################################### First time choice Logger ##################################

USER_FIRST_TIME_CHOICE = 'uftc'

CHOSE_HOME = 'chose_home'
CHOSE_PHOTOS = 'chose_photos'
CHOSE_DEFAULT = 'chose_default'


def set_user_choice(choice,user_id):
	"""
	This function logs the choice taken by a new user between home and photos
	"""
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zincrby(USER_FIRST_TIME_CHOICE,user_id,amount=1)

	if choice =='1':
		my_server.incr(CHOSE_HOME)
	elif choice == '2':
		my_server.incr(CHOSE_PHOTOS)
	else:
		my_server.incr(CHOSE_DEFAULT)



#########################################Invalid Topic & Rules Logger##################################

def invalid_topic_logger(banned_word,topic):
	"""
	This function logs the topics that were filtered by abuse.py
	"""
	myserver = redis.Redis(connection_pool=POOL)
	myserver.lpush("invalid_topics",topic+":"+banned_word)
	myserver.ltrim("invalid_topics",0,999)

def invalid_rules_logger(banned_word,rules):
	"""
	This function logs the topics that were filtered by abuse.py
	"""
	myserver = redis.Redis(connection_pool=POOL)
	myserver.lpush("invalid_rules",rules+":"+banned_word)
	myserver.ltrim("invalid_rules",0,999)	
