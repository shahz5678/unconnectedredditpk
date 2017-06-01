# coding=utf-8
import redis
from location import REDLOC3
from score import PHOTOS_WITH_SEARCHED_NICKNAMES
from templatetags.thumbedge import cdnize_target_url
from html_injector import image_thumb_formatting

'''
##########Redis Namespace##########

search_history = "sh:"+str(searcher_id)
user_thumbs = "upt:"+owner_uname

###########
'''

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC3, db=0)

TWO_WEEKS = 2*7*24*60*60

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

#checking whether nick already exists
def nick_already_exists(nickname):
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick = nickname.lower()+"*"
	if not my_server.exists("nicknames"):
		return None
	elif my_server.zrank("nicknames",generic_nick) is None:
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
			pipeline1.zrank("nicknames",nick)
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

#main function resposible for yielding search results
def find_nickname(target_nick, searcher_id):
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
		pipeline1 = my_server.pipeline()
		for uname in similar_nicknames:
			user_thumbs = "upt:"+uname
			pipeline1.get(user_thumbs)
		result1 = pipeline1.execute()
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
		search_history = "sh:"+str(searcher_id)
		pipeline1 = my_server.pipeline()
		for entry in exact:
			pipeline1.zincrby(search_history,entry,amount=1)
		pipeline1.execute()
		pipeline2 = my_server.pipeline()
		for uname in similar_nicknames:
			user_thumbs = "upt:"+uname
			pipeline2.get(user_thumbs)
		result2 = pipeline2.execute()
		similar_with_pics = []
		counter = 0
		for uname in similar_nicknames:
			similar_with_pics.append((uname,result2[counter]))
			counter += 1
		pipeline3 = my_server.pipeline()
		for uname in exact:
			user_thumbs = "upt:"+uname
			pipeline3.get(user_thumbs)
		result3 = pipeline3.execute()
		counter = 0
		for uname in exact:
			exact_with_pics.append((uname,result3[counter]))
			counter += 1
	return nick_found, exact_with_pics, similar_with_pics

#used to bump up scores when user clicks the nick after searching it
def select_nick(nickname, selector_id):
	my_server = redis.Redis(connection_pool=POOL)
	search_history = "sh:"+str(selector_id)
	my_server.zincrby(search_history,nickname,amount=1)

#used to populate search history in search page
def get_search_history(searcher_id):
	my_server = redis.Redis(connection_pool=POOL)
	search_history = "sh:"+str(searcher_id)
	if my_server.exists(search_history):
		my_server.expire(search_history,TWO_WEEKS)
		return my_server.zrevrange(search_history,0,-1)
	else:
		return []

#delete an entry from search history
def del_search_history(searcher_id, nick):
	my_server = redis.Redis(connection_pool=POOL)
	search_history = "sh:"+str(searcher_id)
	my_server.zrem(search_history,nick)

def retrieve_history_with_pics(uname_list):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for uname in uname_list:
		user_thumbs = "upt:"+uname
		pipeline1.get(user_thumbs)
	result1 = pipeline1.execute()
	history = []
	counter = 0
	for uname in uname_list:
		history.append((uname,result1[counter]))
		counter += 1
	return history

def retrieve_thumbs(obj_list):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for obj in obj_list:
		user_thumbs = "upt:"+obj['username']
		pipeline1.get(user_thumbs)
	result1 = pipeline1.execute()
	counter = 0
	users_with_thumbs = {}
	for obj in obj_list:
		obj['thumbs'] = result1[counter]
		counter += 1
	return obj_list

def retrieve_single_thumbs(obj):
	my_server = redis.Redis(connection_pool=POOL)
	user_thumbs = "upt:"+obj
	return my_server.get(user_thumbs)

def search_thumbs_missing(username):
	my_server = redis.Redis(connection_pool=POOL)
	user_thumbs = "upt:"+username
	if my_server.exists(user_thumbs):
		return False
	else:
		return True

#add latest photo to a payload trimmed at 5 photos max
def add_search_photo(img_url,photo_id,owner_uname):
	my_server = redis.Redis(connection_pool=POOL)
	user_thumbs = "upt:"+owner_uname
	new_payload = image_thumb_formatting(cdnize_target_url(img_url),photo_id)
	existing_payload = my_server.get(user_thumbs)
	if existing_payload:
		payload = new_payload+'&nbsp;'+existing_payload
	else:
		payload = new_payload
	breaks = payload.count('&nbsp;')
	if breaks > (PHOTOS_WITH_SEARCHED_NICKNAMES-1):
		#trim from 5th &nbsp; and onwards
		groups = payload.split('&nbsp;')
		payload = '&nbsp;'.join(groups[:PHOTOS_WITH_SEARCHED_NICKNAMES])
	my_server.set(user_thumbs,payload)

#populates uploaded photo thumbs whenever a profile is visited
def bulk_add_search_photos(owner_uname, ids_with_urls):
	my_server = redis.Redis(connection_pool=POOL)
	user_thumbs = "upt:"+owner_uname
	ids_with_thumbs = [(item[0],cdnize_target_url(item[1])) for item in ids_with_urls]
	payload = []
	for obj in ids_with_thumbs:
		payload.append(image_thumb_formatting(obj[1],obj[0]))
	final_payload = '&nbsp;'.join(payload)
	my_server.set(user_thumbs,final_payload)

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

#####################################################

def save_post(text):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.set("optimizely_test",text)

def get_temp_id():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.incr("temp_user_id")

#####################################################

PASSWORD_ERRORS = "likho_errors"#"password_errors"

def log_erroneous_passwords(password,error_string):
	my_server = redis.Redis(connection_pool=POOL)
	password_errors = PASSWORD_ERRORS
	my_server.lpush(password_errors,{'password':password,'error_string':error_string})

def retrieve_erroneous_passwords():
	my_server = redis.Redis(connection_pool=POOL)
	# list_ = my_server.lrange(PASSWORD_ERRORS,0 ,-1)
	# import pandas as pd
	# import ast
	# df = pd.DataFrame(list_)
	# print df
	import csv, ast
	password_errors = PASSWORD_ERRORS
	list_ = my_server.lrange(password_errors,0 ,-1)
	# keys = ['password','error_string']
	with open('likho_errors.csv','wb') as f:
		wtr = csv.writer(f)
		for string in list_:
			dictionary = ast.literal_eval(string)
			to_write = [dictionary["password"].encode('utf-8'),dictionary["error_string"].encode('utf-8')]
			wtr.writerow(to_write)