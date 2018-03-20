
# coding=utf-8
import redis, time, random
from location import REDLOC4
from score import BAN_REASON, RATELIMIT_TTL, SUPER_FLOODING_THRESHOLD, FLOODING_THRESHOLD, LAZY_FLOODING_THRESHOLD, SHORT_MESSAGES_ALWD

'''
##########Redis Namespace##########

city_shops = "city_shops"
"historical_calcs"
latest_user_ip = "lip:"+str(user_id)
logged_users = "logged_users"
sorted_set = "online_users"
user_ban = "ub:"+str(user_id)
user_times = "user_times:"+str(user_id)

pusk:<user_id>:<secret_key> # photo_upload_secret_key
tisk:<user_id>:<obj_type>:<obj_id> # text input secret_key

rlfh:<user_id> - rate limited from home (e.g. because of abusive reasons)
rlfpg:<user_id> - rate limited from public group (e.g. because of spammy behavior)
rlfpvg:<user_id> - rate limited from private group (e.g. because of spammy behavior)
rlfpc:<user_id> - rate limited from photo comments (e.g. because of spammy behavior)
rlfhr:<user_id> - rate limited from home replies (e.g. because of spammy behavior)

hir:<user_id> - home input rate (list holding times of posting on home for a specific user)
pgir:<user_id> - public group input rate (list holding times of posting in public group for a specific user)
pvgir:<user_id> - private group input rate (list holding times of posting in public group for a specific user)
pcir:<user_id> - photo comment input rate (list holding times of posting on photo comments for a specific user)
hrir:<user_id> - home reply input rate (list holding times of posting in home replies)

hit:<user_id> - home input text (list holding previous text of home posting for a specific user)
pgit:<user_id> - public group input text (list holding text of public group posting for a specific user in a specific group)
pvgit:<user_id> - private group input rate (list holding times of posting in private group for a specific user)
pcit:<user_id> - photo comment input text (list holding text of photo comments for a specific user and a specific photo)
hrit:<user_id> - home reply input text (list holding text of home replies for a specific user under a specific home sentence)

sm:<user_id>:<section>:<obj_id> - counter to count short messages sent on home objects

###########
'''

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC4, db=0)

ONE_HOUR = 60*60
TWELVE_HOURS = 60*60*12
TWENTY_MINS = 20*60
TEN_MINS = 10*60
SEVEN_MINS = 7*60
FIVE_MINS = 5*60
THREE_MINS = 3*60
ONE_MIN = 60



def save_deprecated_photo_ids_and_filenames(deprecated_photos):
	my_server = redis.Redis(connection_pool=POOL)
	final_list = []
	for filename, photo_id in deprecated_photos:
		filename = filename.split('photos/')[1]
		final_list.append(filename)
		final_list.append(photo_id)
	my_server.zadd("deprecated_photos",*final_list)


# def log_pic_uploader_status(user_id, is_verified):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	verified = '1' if is_verified else '0'
# 	my_server.lpush('uploaded_pics',verified+":"+str(user_id))

# def save_user_choice(user_id, choice):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	my_server.lpush("new_user_choice",{'user_id':user_id,'user_choice':choice})

# def log_referrer(referrer, loc, user_id):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	my_server.lpush("referrer",{'referrer':referrer,'origin':loc, 'user_id':user_id, 'time_stamp':time.time()})

def return_referrer_logs(log_name):
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.lrange(log_name,0,-1)


# def error_logger(obj_creator_reported_id, object_creator_actual_id,actual_object_attributes, reported_link_attributes, from_loc, is_post_request,referrer):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	my_server.lpush("block_error",{'obj_creator_reported_id':obj_creator_reported_id,'object_creator_actual_id':object_creator_actual_id,\
# 		'actual_object_attributes':actual_object_attributes, 'reported_link_attributes':reported_link_attributes,'where_from':from_loc, \
# 		'is_post_request':is_post_request,'referrer':referrer})


# def log_html_error(obj_list, forms, page, nickname, referrer):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	my_server.lpush("matka_error",{'obj_list':obj_list,'forms':forms, 'page':page, 'username':nickname,'referrer':referrer ,'time':time.time()})

# def log_button_error(target_user_id, id_type,target_username,own_id, object_id,referrer):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	my_server.lpush("button_error",{'target_user_id':target_user_id,'id_type':id_type, 'target_username':target_username,'own_id':own_id, \
# 		'object_id':object_id,'referrer':referrer,'time':time.time()})


# def save_number_verification_error_data(user_id, err_data, err_type=None, on_fbs=None, is_auth=None, which_flow=None):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	if which_flow == 'consumer':
# 		err_data["user_id"], err_data["err_type"], err_data["on_fbs"], err_data["is_auth"] = user_id, err_type, on_fbs, is_auth
# 		my_server.lpush("consumer_number_errors",err_data)
# 	else:
# 		err_data["user_id"], err_data["err_type"], err_data["on_fbs"], err_data["is_auth"] = user_id, err_type, on_fbs, is_auth
# 		my_server.lpush("seller_number_errors",err_data)

#######################Ecomm Metrics######################

def log_ecomm_user_visit(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.lpush("ecomm_visits",user_id)

def get_and_reset_daily_ecomm_visits():
	my_server = redis.Redis(connection_pool=POOL)
	all_visits = my_server.lrange("ecomm_visits",0,-1)
	pipeline1 = my_server.pipeline()
	pipeline1.lpush("weekly_ecomm_visits",all_visits)
	pipeline1.delete("ecomm_visits")
	pipeline1.execute()
	return all_visits, my_server.llen("weekly_ecomm_visits")

def get_and_reset_weekly_ecomm_visits():
	import ast
	my_server = redis.Redis(connection_pool=POOL)
	weekly_visits = my_server.lrange("weekly_ecomm_visits",0,-1)
	weekly_gross_visits = []
	for daily_visits in weekly_visits:
		weekly_gross_visits += ast.literal_eval(daily_visits)
	my_server.delete("weekly_ecomm_visits")
	return weekly_gross_visits


def insert_metrics(ecomm_metrics, reporting_time, period=None):
	my_server = redis.Redis(connection_pool=POOL)
	if period == 'daily':
		mapping = {'entry_time':reporting_time, 'unique_clicks_per_unique_visitor':ecomm_metrics[0], 'unique_clicks_per_unique_clicker':ecomm_metrics[1], \
		'proportion_of_clickers_to_visitors':ecomm_metrics[2], 'unique_new_clickers_per_unique_new_visitors':ecomm_metrics[3], \
		'unique_new_clicks_per_unique_new_visitor':ecomm_metrics[4], 'total_unique_visitors':ecomm_metrics[5], 'total_unique_clicks':ecomm_metrics[6]}
		my_server.lpush("ecomm_metrics",mapping)
	if period == 'weekly':
		mapping = {'entry_time':reporting_time, 'weekly_unique_clicks_per_unique_visitor':ecomm_metrics[0], 'weekly_unique_clicks_per_unique_clicker':ecomm_metrics[1], \
		'weekly_proportion_of_clickers_to_visitors':ecomm_metrics[2], 'weekly_unique_visitors':ecomm_metrics[3], \
		'weekly_unique_clicks':ecomm_metrics[4]}
		my_server.lpush("weekly_ecomm_metrics",mapping)



def return_all_metrics_data():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.lrange("ecomm_metrics", 0, -1), my_server.lrange("weekly_ecomm_metrics", 0, -1)

#######################Photo Secret Key######################

def set_photo_upload_key(user_id, secret_key, group_id=None):
	"""
	Used to prevent double form submission when uploading photos (public photos or personal group photos)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	sec_key = "pusk:"+str(user_id)+":"+group_id if group_id else "pusk:"+str(user_id)
	my_server.setex(sec_key,secret_key,TWENTY_MINS)


def get_and_delete_photo_upload_key(user_id, group_id=None):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	sec_key = "pusk:"+user_id+":"+group_id if group_id else "pusk:"+user_id
	secret_key = my_server.get(sec_key)
	if secret_key:
		my_server.delete(sec_key)
		return secret_key
	else:
		return '1'


def set_text_input_key(user_id, obj_id, obj_type, secret_key):
	"""
	Used to prevent double form submission
	"""
	my_server = redis.Redis(connection_pool=POOL)
	sec_key = "tisk:"+str(user_id)+":"+obj_type+":"+str(obj_id)
	my_server.setex(sec_key,secret_key,TWENTY_MINS)


def get_and_delete_text_input_key(user_id, obj_id, obj_type):
	"""
	Checks if secret key exists and returns an appropriate response
	"""
	my_server = redis.Redis(connection_pool=POOL)
	sec_key = "tisk:"+str(user_id)+":"+obj_type+":"+str(obj_id)
	secret_key = my_server.get(sec_key)
	if secret_key:
		my_server.delete(sec_key)
		return secret_key
	else:
		return '1'

#####################Retention Logger#####################
def log_retention(server_instance, user_id):
	time_now = time.time()
	if server_instance.exists("user_times:"+user_id):
		if time_now - float(server_instance.lrange("user_times:"+user_id,0,0)[0]) > TEN_MINS:
			server_instance.lpush("user_times:"+user_id,time_now)
			server_instance.sadd("logged_users",user_id)
	else:
		# contains a user's times of browsing Damadam
		server_instance.lpush("user_times:"+user_id,time_now)
		# contains all user_ids that have ever been logged
		server_instance.sadd("logged_users",user_id)

def retrieve_retention_ids():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.smembers("logged_users")

def retrieve_retention_data(user_ids):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for id_ in user_ids:
		pipeline1.lrange("user_times:"+id_,0,-1)
	result1 = pipeline1.execute()
	user_times = []
	counter = 0
	for id_ in user_ids:
		user_times.append((id_,result1[counter]))
		counter += 1
	return user_times

# def reduce_retention_data():
	"""
	to delete, get ids of really old "last_active"
	dates from session table in DB (to ensure it's 
	an old user). Then delete those "user_times"+str(user_id)
	"""

#######################Whose Online#######################

#expires online_users from tasks.py
def expire_online_users():
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "online_users"
	my_server.zremrangebyscore(sorted_set,'-inf','('+str(time.time()-TEN_MINS))

#invoked from WhoseOnline.py middleware
def set_online_users(user_id,user_ip):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "online_users"
	latest_user_ip = "lip:"+user_id #latest ip of user with 'user_id'
	pipeline1 = my_server.pipeline()
	pipeline1.zadd(sorted_set,user_id+":"+user_ip,time.time())
	pipeline1.setex(latest_user_ip,user_ip,FIVE_MINS)
	pipeline1.execute()
	############ logging user retention ############
	# if random.random() < 0.45:
	# 	log_retention(my_server,user_id)

# invoked by tasks.py to show whoever is online in OnlineKon
def get_recent_online():
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "online_users"
	ten_mins_ago = time.time() - TEN_MINS
	online_users = my_server.zrangebyscore(sorted_set,ten_mins_ago,'+inf')
	online_ids = []
	for user in online_users:
		online_ids.append(user.split(":",1)[0])
	return online_ids

# invoked in views.py to show possible clones of users
def get_clones(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "online_users"
	latest_user_ip = "lip:"+str(user_id) #latest ip of user with 'user_id'
	user_ip = my_server.get(latest_user_ip)
	if user_ip:
		clones = []
		five_mins_ago = time.time() - FIVE_MINS
		online_users = my_server.zrangebyscore(sorted_set,five_mins_ago,'+inf')
		for user in online_users:
			if user_ip == user.split(":",1)[1]:
				clones.append(user.split(":",1)[0])
		return clones
	else:
		return None

# def set_site_ban(user_id):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	user_ban = "ub:"+str(user_id) # banning user's ip from logging into website
# 	my_server.set(user_ban,1)
# 	my_server.expire(user_ban,ONE_HOUR)

#########################################################

# def get_city_shop_listing(city):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	city_shops = "city_shops"
# 	shop_ids = my_server.smembers(city_shops)
# 	pipeline1 = my_server.pipeline()
# 	for shop_id in shop_ids:
# 		shop_detail = "sd:"+str(shop_id)
# 		pipeline1.hgetall(shop_detail)
# 	return pipeline1.execute()

# def initialize_shop(information):
# 	my_server = redis.Redis(connection_pool=POOL)

#########################################################

#calculating installment amount for mobile devices
def get_historical_calcs(base_price=None, time_period_in_months=None, monthly_installment=None, ending_value=None):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	if base_price is None:
		id_ = my_server.get("historical_calcs")
		if id_ is not None:
			for x in range(1,(int(id_)+1)):
				pipeline1.hgetall("cd:"+str(x))
			return pipeline1.execute()
		else:
			return None
	else:
		id_ = my_server.incr("historical_calcs")
		calc_details = "cd:"+str(id_)
		mapping = {'id':id_,'bp':base_price,'tpim':time_period_in_months,'mi':monthly_installment,'ev':ending_value, 't':time.time()}
		my_server.hmset(calc_details,mapping)
		for x in range(1,(id_+1)):
			pipeline1.hgetall("cd:"+str(x))
		return pipeline1.execute()

#########################################################

def save_ad_desc(text, price, user_id,username):
	my_server = redis.Redis(connection_pool=POOL)
	mapping = {'uid':user_id, 'nick':username, 'desc':text,'price':price}
	my_server.lpush("ad_desc",mapping)

#########################################################

def save_careem_data(careem_data):
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.zscore("careem_applicant_nums",careem_data["phonenumber"]):
		# it already exists
		return False
	else:
		# it does not exist
		pipeline1 = my_server.pipeline()
		pipeline1.hmset("cad:"+str(careem_data['phonenumber']),careem_data)
		pipeline1.zadd('careem_applicant_nums',careem_data['phonenumber'],time.time())
		pipeline1.zadd('careem_applicant_nums_live',careem_data['phonenumber'],time.time())
		pipeline1.execute()

		return True

def export_careem_data():
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	user = my_server.zcard("careem_applicant_nums_live")
	if user == 0:
		return False
	else:
		nums = my_server.zrange("careem_applicant_nums_live",0,-1)
		pipeline1 = my_server.pipeline()
		for num in nums:
			pipeline1.hgetall('cad:'+num)
		result1 = pipeline1.execute()
		return result1

def del_careem_data():
	my_server = redis.Redis(connection_pool=POOL)
	my_server.delete("careem_applicant_nums_live")


##################################################Mobile_Shop


def log_buyer_form_err(error_data):
	my_server = redis.Redis(connection_pool=POOL)
	error_id = get_error_id()
	key_name = "error_data:"+str(error_id)
	pipeline1 = my_server.pipeline()
	pipeline1.hmset(key_name,error_data)
	#pipeline1.expire(key_name,TWELVE_HOURS)
	pipeline1.execute()
	return True

def get_error_id():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.incr("ms_error_id")

def save_order_data(order_data):
	my_server = redis.Redis(connection_pool=POOL)
	key_name = "order_data:"+str(order_data['user_id'])
	pipeline1 = my_server.pipeline()
	pipeline1.hmset(key_name,order_data)
	pipeline1.expire(key_name,TWELVE_HOURS)
	pipeline1.execute()
	return True

def save_query_data(query_data):
	my_server = redis.Redis(connection_pool=POOL)
	key_name = "querydata:"+str(query_data['user_id'])
	pipeline1 = my_server.pipeline()
	pipeline1.hmset(key_name,query_data)
	pipeline1.sadd('queryusers',query_data['user_id'])
#	pipeline1.expire(key_name,TWELVE_HOURS)
	pipeline1.execute()
	return True

def delete_query(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	my_server.srem("queryusers",user_id)
	my_server.delete("querydata:"+str(user_id))
	pipeline1.execute()
	return {}


def place_order(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	order_data = False
	order_data = get_temp_order_data(user_id)
	order_id = get_order_id()
	order_data['order_id'] = order_id
	pipeline1.zadd('ordersinprocess',user_id,order_id)
	# after a few months, export this to excel and clean the list (it takes up needless space)
	pipeline1.hmset("placedorders:"+str(order_id),order_data)
	pipeline1.execute()
	return order_data

def delete_order(order_id,user_id):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	# after a few months, export this to excel and clean the list (it takes up needless space)
	my_server.zrem("ordersinprocess",user_id)
	my_server.delete("placedorders:"+str(order_id))
	pipeline1.execute()
	return {}





def get_temp_order_data(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	temp_storage = "order_data:"+str(user_id)
	if my_server.exists(temp_storage):
		order_details = my_server.hgetall("order_data:"+str(user_id))
#		my_server.delete("order_data:"+str(user_id))
		return order_details
	else:
		return {}

def check_orders_processing(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	user = my_server.zscore('ordersinprocess',user_id)
	if user == None:
		return False
	else:
		return True

def get_order_id():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.incr("order_id")

def get_total_orders():
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.get("order_id")

def show_new_orders():
	total_orders = get_total_orders()
	if total_orders <1:
		return False
	else:
		my_server = redis.Redis(connection_pool=POOL)
		pipeline1 = my_server.pipeline()
		num = 0
		
		while num <= int(total_orders):
			temp_storage = "placedorders:"+str(num)
			if my_server.exists(temp_storage):
				pipeline1.hgetall('placedorders:'+str(num))
			num = num + 1
		orders = pipeline1.execute()
		return orders


def show_new_queries():
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	users = my_server.smembers("queryusers")
	if users == 0:
		return []
	else:
		pipeline1 = my_server.pipeline()
		for obj in users:
			pipeline1.hgetall('querydata:'+obj)
		result1 = pipeline1.execute()
		return result1



'''
####################
M_S Deprecated Key Names
query_data now querydata
query_users now queryusers
orders_in_process now ordersinprocess
placed_orders now placedorders

####################
'''

############ Rate limiting flooding and spamming ############

def is_limited(user_id, section, with_reason = False):
	"""
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if section == 'home':
		key = "rlfh:"+str(user_id)
	elif section == 'pub_grp':
		key = "rlfpg:"+str(user_id)
	elif section == 'prv_grp':
		key = "rlfpvg:"+str(user_id)
	elif section == 'pht_comm':
		key = "rlfpc:"+str(user_id)
	elif section == 'home_rep':
		key = "rlfhr:"+str(user_id)
	else:
		return False
	if with_reason:
		ttl = my_server.ttl(key)
		if ttl > 0:
			reason = my_server.get(key)
			return ttl, reason
		else:
			return 0, None
	else:
		return my_server.ttl(key)

def rate_limit_user(user_id,section,level,ban_reason,my_server=None):
	"""
	Setting blocking rate limits on abusive users on a section of the website

	Level relates to severity of block limit
	1 - lowest (7 mins)
	2 - low (30 mins)
	3 - medium (2 hours)
	4 - med-high (8 hours)
	5 - high (24 hours)
	6 - severe (3 days)
	7 - hardcore (7 days)
	8 - jackpot (30 days)
	"""
	if not my_server:
		my_server = redis.Redis(connection_pool=POOL)
	if section == 'home':
		rate_limit_key = "rlfh:"+str(user_id)
	elif section == 'pub_grp':
		rate_limit_key = "rlfpg:"+str(user_id)
	elif section == 'prv_grp':
		rate_limit_key = "rlfpvg:"+str(user_id)
	elif section == 'pht_comm':
		rate_limit_key = "rlfpc:"+str(user_id)
	elif section == 'home_rep':
		rate_limit_key = "rlfhr:"+str(user_id)
	try:
		my_server.setex(rate_limit_key,ban_reason,RATELIMIT_TTL[level])
		return True
	except KeyError:
		my_server.setex(rate_limit_key,ban_reason,TWENTY_MINS)
		return False

# 1) revert log_input_rate in tasks.py (done)
# 2) revert function definition of log_input_rate in redis4 (done)
# 3) remove pipeline1.execute(key+":logger",text) from log_input_rate (done)
# 4) remove log_rate_limited_conversation() from log_input_rate (done)
# 5) remove function for log_rate_limited_conversation() in redis4 (done)
# 6) remove function called report_rate_limited_conversation() in redis4 (done)
# 7) remove logger url (and view import) from urls_maint.py (done)
# 8) remove reporting view (called rate_limit_logging_report) from end of maint_views (done)
# 9) remove the import for report_rate_limited_conversation() from maint_views (done)
# 10) remove get_section_string() from redis4 (done)

# def report_rate_limited_conversation():
# 	"""
# 	Extracts all rate limited conversations
# 	"""
# 	import csv,ast
# 	my_server = redis.Redis(connection_pool=POOL)
# 	super_ = my_server.lrange("rate_limited_convos:super",0,-1)
# 	normal_ = my_server.lrange("rate_limited_convos:normal",0,-1)
# 	lazy_ = my_server.lrange("rate_limited_convos:lazy",0,-1)
# 	result = [(super_,'super_'),(normal_,'normal_'),(lazy_,'lazy_')]
# 	for logs,log_type in result:
# 		filename = 'ratelimited_convos_'+log_type+str(int(time.time()))+'.csv'
# 		with open(filename,'wb') as f:
# 			wtr = csv.writer(f)
# 			columns = ["Type","Section","#","Conversation"]
# 			wtr.writerow(columns) # writing the columns
# 			num = 0
# 			for payload in logs:
# 				num += 1
# 				payload = ast.literal_eval(payload)
# 				which_section = payload[0]
# 				for string in payload[1]:
# 					type_=log_type
# 					sec=which_section
# 					conv_num=num
# 					conversation=string
# 					to_write = [type_,sec,conv_num,conversation]	
# 					wtr.writerows([to_write])


# def get_section_string(key):
# 	try:
# 		string = key[:2]
# 	except TypeError:
# 		string = 'undef'
# 	if string == 'hi':
# 		return 'home_post'
# 	elif string == 'pg':
# 		return 'public_group'
# 	elif string == 'pv':
# 		return 'private_group'
# 	elif string == 'pc':
# 		return 'photo_comment'
# 	elif string == 'hr':
# 		return 'home_reply'
# 	else:
# 		return 'undefined'	

# def log_rate_limited_conversation(convo_key, severity):
# 	"""
# 	logger for rate limited conversation strings
# 	"""
# 	my_server = redis.Redis(connection_pool=POOL)
# 	which_section = get_section_string(convo_key)
# 	if severity == 'super':
# 		my_server.lpush("rate_limited_convos:super",[which_section,my_server.lrange(convo_key,0,-1)])
# 	elif severity == 'normal':
# 		my_server.lpush("rate_limited_convos:normal",[which_section,my_server.lrange(convo_key,0,-1)])
# 	else:
# 		my_server.lpush("rate_limited_convos:lazy",[which_section,my_server.lrange(convo_key,0,-1)])


# def log_input_rate(section,user_id,time_now):
def log_input_rate(section,user_id,time_now,text=None):
	"""
	Keeps check of writing rates to rate limit abusive users
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if section == 'home':
		key = "hir:"+str(user_id)
	elif section == 'pub_grp':
		key = "pgir:"+str(user_id)	
	elif section == 'prv_grp':
		key = "pvgir:"+str(user_id)
	elif section == 'pht_comm':
		key = "pcir:"+str(user_id)
	elif section == 'home_rep':
		key = "hrir:"+str(user_id)	
	pipeline1 = my_server.pipeline()
	pipeline1.lpush(key,time_now)
	pipeline1.expire(key,ONE_MIN)
	#### remove ####
	# pipeline1.lpush(key+":logger",text)
	# pipeline1.expire(key+":logger",ONE_MIN)
	#### remove ####
	pipeline1.execute()
	####################################
	all_str_values = my_server.lrange(key,0,-1)
	total_inputs = len(all_str_values)
	if total_inputs > 7:
		all_values = map(float, all_str_values)
		sum_of_differences = 0
		for s, t in zip(all_values, all_values[1:]):
			sum_of_differences += t - s
		avg_time_taken_between_sentences = abs(sum_of_differences)/(total_inputs-1)
		if avg_time_taken_between_sentences < SUPER_FLOODING_THRESHOLD:
			rate_limit_user(user_id=user_id,section=section,level='2',ban_reason=BAN_REASON['flooding'],my_server=my_server)
			# log_rate_limited_conversation(key+":logger",'super')
		elif avg_time_taken_between_sentences < FLOODING_THRESHOLD:
			rate_limit_user(user_id=user_id,section=section,level='1',ban_reason=BAN_REASON['flooding'],my_server=my_server)
			# log_rate_limited_conversation(key+":logger",'normal')
		elif avg_time_taken_between_sentences < LAZY_FLOODING_THRESHOLD:
			rate_limit_user(user_id=user_id,section=section,level='0',ban_reason=BAN_REASON['flooding'],my_server=my_server)
			# log_rate_limited_conversation(key+":logger",'lazy')
		else:
			my_server.ltrim(key,0,6)
			#### remove ####
			# my_server.ltrim(key+":logger",0,6)

def log_input_text(section, section_id,text,user_id):
	"""
	Logs previous 4 sentences of each section
	"""
	my_server = redis.Redis(connection_pool=POOL)
	if section == 'home':
		key = "hit:"+str(user_id)+":"+str(section_id)
	elif section == 'pub_grp':
		key = "pgit:"+str(user_id)+":"+str(section_id)	
	elif section == 'prv_grp':
		key = "pvgit:"+str(user_id)+":"+str(section_id)	
	elif section == 'pht_comm':
		key = "pcit:"+str(user_id)+":"+str(section_id)
	elif section == 'home_rep':
		key = "hrit:"+str(user_id)+":"+str(section_id)
	my_server.lpush(key,text)
	my_server.ltrim(key,0,3) # keeping previous 4 sentences
	my_server.expire(key,TEN_MINS)

def retrieve_previous_msgs(section, section_id,user_id):
	"""
	retrieve previous messages stored for a certain section_id
	"""	
	my_server = redis.Redis(connection_pool=POOL)
	if section == 'home':
		key = "hit:"+str(user_id)+":"+str(section_id)
	elif section == 'pub_grp':
		key = "pgit:"+str(user_id)+":"+str(section_id)	
	elif section == 'prv_grp':
		key = "pvgit:"+str(user_id)+":"+str(section_id)	
	elif section == 'pht_comm':
		key = "pcit:"+str(user_id)+":"+str(section_id)
	elif section == 'home_rep':
		key = "hrit:"+str(user_id)+":"+str(section_id)
	return my_server.lrange(key,0,-1)

############################ Ratelimiting short messages ###############################

def log_short_message(user_id,section,obj_id):
	my_server = redis.Redis(connection_pool=POOL)
	short_message = "sm:"+str(user_id)+":"+section+":"+str(obj_id)
	my_server.incr(short_message)
	my_server.expire(short_message,THREE_MINS)

def many_short_messages(user_id,section,obj_id):
	"""
	Confirms if trail of short messages have already been left by the user on the given object
	"""
	my_server = redis.Redis(connection_pool=POOL)
	short_message = "sm:"+str(user_id)+":"+section+":"+str(obj_id)
	short_messages_so_far = my_server.get(short_message)
	if short_messages_so_far:
		if int(short_messages_so_far) > SHORT_MESSAGES_ALWD:
			my_server.expire(short_message,SEVEN_MINS) #renew block short messages for 7 mins
			return True
		else:
			False
	else:
		return False