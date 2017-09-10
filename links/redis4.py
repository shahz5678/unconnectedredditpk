# coding=utf-8
import redis, time, random
from location import REDLOC4

'''
##########Redis Namespace##########

city_shops = "city_shops"
"historical_calcs"
latest_user_ip = "lip:"+str(user_id)
logged_users = "logged_users"
sorted_set = "online_users"
my_server.set("pusk:"+user_id,secret_key) # photo_upload_secret_key
user_ban = "ub:"+str(user_id)
user_times = "user_times:"+str(user_id)

###########
'''

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC4, db=0)

TEN_MINS = 10*60
FIVE_MINS = 5*60


def log_referrer(referrer, loc, user_id):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.lpush("referrer",{'referrer':referrer,'origin':loc, 'user_id':user_id, 'time_stamp':time.time()})

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

def set_photo_upload_key(user_id, secret_key):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.setex("pusk:"+str(user_id),secret_key,TEN_MINS)

def get_and_delete_photo_upload_key(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	secret_key = my_server.get("pusk:"+user_id)
	if secret_key:
		my_server.delete("pusk:"+user_id)
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


#########################################################