# coding=utf-8
import redis, time
from datetime import datetime
from location import REDLOC3
from score import PHOTOS_WITH_SEARCHED_NICKNAMES
from templatetags.thumbedge import cdnize_target_url
from html_injector import image_thumb_formatting

'''
##########Redis Namespace##########

gibberish_writers = 'gibberish_writers'
punishment_text = "pt:"+str(user_id)
my_server.lpush("rc:"+ad_id,photo_id) # "rc" implies raw classified (i.e. a classified that is being made and isn't final)
search_history = "sh:"+str(searcher_id)
user_thumbs = "upt:"+owner_uname
"unfinalized_used_item_ads"

###########
'''

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC3, db=0)

FORTY_FIVE_MINS = 60*45
ONE_WEEK = 1*7*24*60*60
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

def retrieve_thumbs(obj_list,tuple_list=False):
	my_server = redis.Redis(connection_pool=POOL)
	if tuple_list:
		pipeline1 = my_server.pipeline()
		for user_obj, photo_count in obj_list:
			user_thumbs = "upt:"+user_obj.username
			pipeline1.get(user_thumbs)
		result1 = pipeline1.execute()
		obj_list_with_thumbs = []
		counter = 0
		for user_obj, photo_count in obj_list:
			obj_list_with_thumbs.append((user_obj,photo_count,result1[counter]))
			counter += 1
		return obj_list_with_thumbs
	else:
		pipeline1 = my_server.pipeline()
		for obj in obj_list:
			user_thumbs = "upt:"+obj['username']
			pipeline1.get(user_thumbs)
		result1 = pipeline1.execute()
		counter = 0
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

###############Saving User Mobile Data#################

# def save_seller_credentials(account_kit_user_id, mobile_data):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	# print account_kit_user_id #connected to a mobile number, time of phone number verification
# 	# print mobile_data {'national_number': '3335196812', 'number': '+923335196812', 'country_prefix': '92'}
# 	# need to tie running ad's ad_id to the user (list containing ad_id, user_id pairs as values)
# 	return True

# def save_new_user_credentials(account_kit_user_id, mobile_data):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	# create a table(hash??) of user_id and complete_mobile_num (hash will allow multiple numbers, e.g. if seller's personal number and seller number are different)
# 	# create hash tables headlined by phone numbers, containing other features
# 	# 	including: nick, gender, account_kit_id, user_id,  

#####################Classifieds#######################

def cleanup(my_server,ad_id):
	my_server.zrem("unfinalized_used_item_ads",ad_id)
	my_server.delete("rc:"+str(ad_id))

def save_basic_ad_data(submitted_data):
	my_server = redis.Redis(connection_pool=POOL)
	photo_ids = my_server.lrange("rc:"+str(submitted_data["ad_id"]),0,-1)
	if photo_ids:
		submitted_data["photos"] = photo_ids
	my_server.lpush("unapproved_ads",submitted_data)
	cleanup(my_server,submitted_data["ad_id"])
	return True

def pre_add_used_item_photo(user_id, ad_id, photo_id):
	my_server = redis.Redis(connection_pool=POOL)
	ad_id = str(ad_id)
	pipeline1 = my_server.pipeline()
	pipeline1.zadd("unfinalized_used_item_ads",ad_id,time.time()) #removed deployed ad_ids from here
	pipeline1.lpush("rc:"+ad_id,photo_id) #remove deployed photo_ids from here
	pipeline1.execute()
	# need to tie photo_ids to the ad (list with ad_id in the name, containing photo_ids)

# def get_used_item_photos(user_id,ad_id):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	# str(user_id)+":"+str(ad_id)

def get_basic_item_ad_id():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.incr("basic_item_ad_id")

def del_orphaned_classified_photos():
	import operator
	my_server = redis.Redis(connection_pool=POOL)
	# deleting orphaned photos from 45 mins ago
	ad_ids_with_times = my_server.zrangebyscore("unfinalized_used_item_ads",'-inf','('+str(time.time()-FORTY_FIVE_MINS), withscores=True)
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
		my_server.zremrangebyscore("unfinalized_used_item_ads",min(score_range),max(score_range))
		return photo_ids_to_delete
	else:
		return None


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

def retire_gibberish_punishment_amount(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	punishment_text = "pt:"+str(user_id)
	my_server.delete(punishment_text)

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