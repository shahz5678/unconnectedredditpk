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
TWO_MINS = 2*60


def save_unfinished_ad_processing_error(is_auth, user_id, editor_id, ad_id, next_step, referrer, on_fbs):
	my_server = redis.Redis(connection_pool=POOL)
	data = {'is_auth':is_auth,'user_id':user_id,'editor_id':editor_id,'ad_id':ad_id,'next_step':next_step,'referrer':referrer,'on_fbs':on_fbs}
	my_server.lpush("unfinished_ad_processing_error",data)

def save_seller_number_error(user_id, user_id_type, data):
	my_server = redis.Redis(connection_pool=POOL)
	um_data = {"user_id":user_id, "user_id_type":user_id_type,"um_data":data}
	my_server.lpush("show_seller_number_errors",um_data)

def save_number_verification_error_data(user_id, err_data, err_type=None, on_fbs=None, is_auth=None, which_flow=None):
	my_server = redis.Redis(connection_pool=POOL)
	if which_flow == 'consumer':
		err_data["user_id"], err_data["err_type"], err_data["on_fbs"], err_data["is_auth"] = user_id, err_type, on_fbs, is_auth
		my_server.lpush("consumer_number_errors",err_data)
	else:
		err_data["user_id"], err_data["err_type"], err_data["on_fbs"], err_data["is_auth"] = user_id, err_type, on_fbs, is_auth
		my_server.lpush("seller_number_errors",err_data)

#######################Test Function######################

# def set_test_payload(payload_list):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	try:
# 		return my_server.lpush("my_test",payload_list)
# 	except:
# 		return None

def set_photo_upload_key(user_id, secret_key):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	my_server.set("pusk:"+user_id,secret_key)
	my_server.expire("pusk:"+user_id,TWO_MINS)

def get_and_delete_photo_upload_key(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	if my_server.exists("pusk:"+user_id):
		secret_key = my_server.get("pusk:"+user_id)
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
	user_id = str(user_id)
	latest_user_ip = "lip:"+user_id #latest ip of user with 'user_id'
	my_server.zadd(sorted_set,user_id+":"+str(user_ip),time.time())
	my_server.set(latest_user_ip,user_ip)
	my_server.expire(latest_user_ip,FIVE_MINS)
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
#		print my_server.zrange("careem_applicant_nums",0,-1)
		pipeline1.execute()

		return True

def export_careem_data():
	my_server = redis.Redis(connection_pool=POOL)
	nums = my_server.zrange("careem_applicant_nums",0,-1)
	for num in nums:
		print my_server.hgetall('cad:'+num)


def export_careem_data():
	import csv
	my_server = redis.Redis(connection_pool=POOL)
	nums = my_server.zrange("careem_applicant_nums",0,-1)
	pipeline1 = my_server.pipeline()
	for num in nums:
		pipeline1.hgetall('cad:'+num)
	result1 = pipeline1.execute()
	filename = 'careem_'+str(int(time.time()))+'.csv'
	with open(filename,'wb') as f:
		wtr = csv.writer(f)
		columns = ["Firstname","Lastname","Mobile","City","License","Car Ownership"]
		wtr.writerow(columns)
		for user in result1:
			firstname,lastname,phonenumber,city,license,car=user['firstname'],user['lastname'],user['phonenumber'],\
			user['city'],user['license'],user['car']
			to_write = [firstname,lastname,phonenumber,city,license,car]
			wtr.writerows([to_write])

#########################################################