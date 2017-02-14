import redis, random
from django.shortcuts import redirect
from target_urls import call_aasan_api
from location import REDLOC1

'''
separate redis modules for ads, so that the namespace doesn't collide with other
redis functions
'''

# POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1)
POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC1, db=1) # changed connection from TCP port to UNIX socket

##########Redis ads namespace##########

'''
Queued for expiry
qad:{ad_id}

Active_location_ads (Set)
la:{location_num}
name: "la:" + str(location) # la is location ads. These are sets that list active ads in each location.

Ad_total_click_counter (String)
ac:{id}
name: "ac:" + str(ad_id). Will use increment on this number. Initially 0.

Ad_location_click_counter (String)
al:{id}:{location_num}
name: "al:" + str(ad_id) +":" + str(location). Will use increment on this number. Initially 0.

Ad_total_impressions_counter (String)
ic:{id}
name: "ic:" + str(ad_id). Will use increment on this number. Initially 0.

Ad_location_impressions_counter (String)
il:{id}:{location_num}
name: "alc:" + str(ad_id) +":" + str(location). Will use increment on this number. Initially 0.

Ad_Details (Hash)
ad:{id}
name: "ad:" + str(ad_id)
{clicks, description, title, link_url, image_url, button_label, status}
{cl, ds, ti, li, im, bt, st}
'''

#############################
# AD_STATUS = (
# 	(0, 'Unapproved'),		# Not Running
# 	(1, 'Approved/Unpaid'),	# Running.
# 	(2, 'Paused'),			# Not Running - 
# 	(3, 'Claimed'),			# Not Running - Claimed by some specific Agent.
# 	(4, 'Closed'),			# Not Running - Awaiting Verification.
# 	(5, 'Running'),			# Running.
# 	(6, 'Stopped'),			# Not Running
# 	(7, 'Expired')
# )
##############################

##############################

#SMS reporting cut-offs
TWENTYFIVE_PERCENT = 0.25
FIFTY_PERCENT = 0.5
NINETY_PERCENT = 0.9

LOCATION = (
	(0, 'Karachi'), 
	(1, 'Rawalpindi'),
	(2, 'Islamabad'), 
	(3, 'Lahore'), 
	(4, 'Quetta'), 
	(5, 'Hyderabad'),
	(6, 'Multan'),
	(7, 'Sukkur'),
	(8, 'Gujrat'),
	(9, 'Peshawer'),
	(10, 'Sialkot'),
	(11, 'Faisalabad'),
	(12, 'Gujranwala'),
	(13, 'Wah'),
	(14, 'Sarghoda'),
	(15, 'Bahwalpur'),
	(16, 'Mardan'),
	(17, 'Abbottabad'),
	(18, 'Swat'),
	(19, 'Gilgit'),
	(20, 'Skardu'),
)

LOCATION_KEYS = dict(LOCATION).keys()
##############################

#write a periodic task that clears this set by correctly expiring all members, and sending final data to api
# i.e. write a job in tasks.py (and set interval in settings.py)
# this job deletes the relevant counters and hash, and then sends the final data to aasan ads (saved in qad:ad_id)
def queue_ad_expiry(ad_id,data):
	my_server = redis.Redis(connection_pool=POOL)
	for loc in ad_locations(ad_id):
		#remove ad from locations
		my_server.srem("la:"+str(loc),ad_id)
	#place ad in queued_for_expiry set
	my_server.sadd("queued_for_expiry",ad_id)
	my_server.hmset("qad:"+ad_id,data) #useful when ad has to be resent

def put_ad(ad):
	my_server = redis.Redis(connection_pool=POOL)
	clicks = ad['clicks']
	pipeline1 = my_server.pipeline()
	ad_mapping = {}
	ad_mapping['cl'] = clicks
	ad_mapping['ds'] = ad['description']#ad.description
	if 'location' in ad:
		ad_mapping['lo'] = ad['location']
	if 'title' in ad:
		ad_mapping['ti'] = ad['title']
	if 'link_url' in ad:
		ad_mapping['li'] = ad['link_url']
	if 'image_url' in ad:
		ad_mapping['im'] = ad['image_url']
	if 'button_label' in ad:
		ad_mapping['bt'] = ad['button_label']
	if 'status' in ad:
		ad_mapping['st'] = ad['status']
	if 'address' in ad:
		ad_mapping['ad'] = ad['address']
	if 'contact_preference' in ad:
		ad_mapping['cp'] = ad['contact_preference']
	if 'only_ladies' in ad:
		ad_mapping['ol'] = ad['only_ladies']
	if 'user_id' in ad and 'user_id' != 'None':
		pipeline1.sadd("ua:"+str(ad['user_id']),ad['tid']) # set containing user's live ads
		ad_mapping['ua'] = ad['user_id']
	pipeline1.hmset("ad:"+str(ad['tid']), ad_mapping) # ad hash
	# Initialize Ad_total_click_counter
	pipeline1.set("ac:"+str(ad['tid']), "0") 
	pipeline1.set("ic:"+str(ad['tid']), "0") #ad impression counter
	
	# Add ad_id to Active_location_ads to redis.
	if 'location' in ad:
		locs = ad['location']# locs is a list of locations
		for loc in locs:
			pipeline1.sadd("la:"+str(loc), ad['tid'])

			# Initialize ad_location_click_counter
			pipeline1.set("al:"+str(ad['tid'])+":" +str(loc), "0")
			pipeline1.set("il:"+str(ad['tid'])+":" +str(loc), "0")

		pipeline1.execute()
	return ad['tid']#True
	
def get_ad(location=None):
	my_server = redis.Redis(connection_pool=POOL)
	if location:
		ad = "la:"+str(location)
		ad_id = my_server.srandmember(ad)
		total_location_impressions = my_server.incr("il:"+ad_id+":"+str(location))
	else:
		#if location doesn't exist, pick random location, and don't update that location's impression counter
		ad = "la:"+str(random.randint(0,20))
		ad_id = my_server.srandmember(ad)
	if ad_id:
		ad_body = my_server.hgetall("ad:"+ad_id)
		ad_clicks = my_server.get("ac:"+ad_id) #remove
		total_impressions = my_server.incr("ic:"+ad_id)
		return ad_body, ad_id, ad_clicks
	else:
		return None, None, None

def send_sms(ad_id,ad_progress):
	my_server = redis.Redis(connection_pool=POOL)
	if ad_progress > NINETY_PERCENT:
		if my_server.hget("ad:"+ad_id,"90r"):
			#SMS already sent
			pass
		else:
			#Send SMS
			data = {'tid':ad_id,'sms':'90'}
			my_server.hset("ad:"+ad_id,"90r",True)
			try:
				response = call_aasan_api(data,'send_sms')
				# print response.content
			except:
				my_server.hdel("ad:"+ad_id,"90r")
	elif ad_progress > FIFTY_PERCENT:
		if my_server.hget("ad:"+ad_id,"50r"):
			#SMS already sent
			pass
		else:
			#Send SMS
			data = {'tid':ad_id,'sms':'50'}
			my_server.hset("ad:"+ad_id,"50r",True)
			try:
				response = call_aasan_api(data,'send_sms')
			except:
				my_server.hdel("ad:"+ad_id,"50r")
	elif ad_progress > TWENTYFIVE_PERCENT:
		if my_server.hget("ad:"+ad_id,"25r"):
			#SMS already sent
			pass
		else:
			#Send SMS
			data = {'tid':ad_id,'sms':'25'}
			my_server.hset("ad:"+ad_id,"25r",True)
			try:
				response = call_aasan_api(data,'send_sms')
				# print response.content
			except:
				my_server.hdel("ad:"+ad_id,"25r")
	else:
		pass

def store_click(ad_id,location=None):
	my_server = redis.Redis(connection_pool=POOL)
	ad_id = str(ad_id)
	# print ad_id
	if location in LOCATION_KEYS:
		# total_location_impressions = my_server.incr("il:"+ad_id)
		# total_impressions = my_server.incr("ic:"+ad_id)
		click_ceiling = my_server.hget("ad:"+ad_id,"cl")
		current_clicks = my_server.get("ac:"+ad_id) 
		if int(current_clicks) < int(click_ceiling):
			total_clicks = my_server.incr("ac:"+ad_id)
			total_location_clicks = my_server.incr("al:"+ad_id+":"+str(location))
			if my_server.hget("ad:"+ad_id,"st") == "5":
				ad_progress = total_clicks/(click_ceiling*1.0)
				send_sms(ad_id, ad_progress)
		else:
			expire_ad(ad_id)
	else:
		# total_impressions = my_server.incr("ic:"+ad_id)
		click_ceiling = my_server.hget("ad:"+ad_id,"cl")
		current_clicks = my_server.get("ac:"+ad_id)
		if int(current_clicks) < int(click_ceiling):
			total_clicks = my_server.incr("ac:"+ad_id)
			if my_server.hget("ad:"+ad_id,"st") == "5":
				ad_progress = int(total_clicks)/(float(click_ceiling))
				send_sms(ad_id,ad_progress)
		else:
			expire_ad(ad_id)

def get_user_ads(user_id):
	# get user's live ads
	my_server = redis.Redis(connection_pool=POOL)
	user_ads = "ua:"+str(user_id)
	ad_ids = my_server.smembers(user_ads)
	ads = []
	if ad_ids:
		for ad_id in ad_ids:
			ads.append(my_server.hgetall("ad:"+ad_id))
	#get user's historical ads
	data={"user_id":user_id}
	try:
		response = call_aasan_api(data,'history')
		return ads, response.content
	except:
		response = []
		return ads,response
	'''
	get running ads
	send api call to request ad history of older ads
	'''

def periodic_update():
	pass

#if ad locations stored as string instead of list, this parses out the list object
def ad_locations(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	ad_loc = my_server.hget("ad:"+str(ad_id),"lo")
	# print ad_loc
	ad_loc = ad_loc[1:-1]
	# print ad_loc
	ad_loc = ad_loc.split(", ")
	# print ad_loc
	return ad_loc

def suspend_ad(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	for loc in ad_locations(ad_id):
		#remove ad from locations
		# print "la:"+str(loc)
		# print my_server.smembers("la:"+str(loc))
		my_server.srem("la:"+str(loc),ad_id)
	#place ad in suspended set
	my_server.sadd("suspended_ads",ad_id)
	#location and general counters are intact till ad is deleted
	return True

def resume_ad(ad_id):
	# the opposite of suspend ad
	my_server = redis.Redis(connection_pool=POOL)
	for loc in ad_locations(ad_id):
		my_server.sadd("la:"+str(loc),ad_id)
	my_server.srem("suspended_ads",ad_id)
	return True

def delete_ad(ad_id,locs=None):
	my_server = redis.Redis(connection_pool=POOL)
	if locs is None:
		locs = ad_locations(ad_id)
	for loc in locs:	
		my_server.delete("il:"+ad_id+":"+str(loc))
		my_server.delete("al:"+ad_id+":"+str(loc))
		my_server.srem("la:"+str(loc),ad_id)
	my_server.delete("ic:"+ad_id)
	my_server.delete("ac:"+ad_id)
	my_server.delete("ad:"+ad_id) #deleting the ad's hash
	return True

def expire_ad(ad_id):
	my_server = redis.Redis(connection_pool=POOL)
	impressions = my_server.get("ic:"+ad_id)
	clicks = my_server.get("ac:"+ad_id)
	click_breakdown = {} #array of hashmaps containing location against clicks
	impression_breakdown = {}#array of hashmaps containing location against impressions
	ad_loc = ad_locations(ad_id)
	for loc in ad_loc:
		click_breakdown[loc] = my_server.get("al:"+ad_id+":"+str(loc))
		impression_breakdown[loc] = my_server.get("il:"+ad_id+":"+str(loc))
	data = {"tid":ad_id, "ad_impressions":impressions, "ad_clicks":clicks, "click_breakdown":click_breakdown,\
	"impression_breakdown":impression_breakdown,"ad_done":True}
	response = call_aasan_api(data,'expire')
	# print response.content
	# try:
	if response.content == "ad updated, saved, expired, deleted":
		# delete ad from set of user's live ads
		user_id = my_server.hget("ad:"+ad_id,"ua")
		my_server.srem("ua:"+user_id,ad_id)
		# delete ad
		delete_ad(ad_id,ad_loc)
		# else:
		# 	pass
	# except:
	# 	queue_ad_expiry(ad_id,data)

def periodic_updates():
	my_server = redis.Redis(connection_pool=POOL)
	'''
	send current counter snapshots to aasan ads
	'''

def get_user_loc(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	user_loc = "ul:"+str(user_id)
	user_loc = my_server.get(user_loc)
	return user_loc


# {'click_breakdown': {'0':3,'1':2,'5':5}, 'ad_clicks': '10', 'ad_done': True, 'ad_impressions': '32', 'ad_id': '24', 'impression_breakdown': {}}