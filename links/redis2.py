import redis, time

'''
##########Redis Namespace##########

fans = "f:"+str(photo_owner_id) // a sorted set
group_attendance = "ga:"+str(group_id)
hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(object_id) #'np' is notification payload, contains notification data
hash_name = "o:"+str(object_type)+":"+str(object_id) #'o' is object, this contains link, photo, group, salat invite, video, etc.
photos_benchmark = "photos_benchmark"
sorted_set = "public_group_rankings"
user_score_hash = "us:"+str(user_id)
sorted_set = "si:"+str(viewer_id) #salat invites sent to viewer_id
sorted_set = "sn:"+str(viewer_id) #'sn' is single notification, for user with viewer_id
single_key = 't:'+str(viewer_id) #'t' stores time of last visit to unseen activity by viewer_id
sorted_set = "ua:"+str(viewer_id) #'ua' is unseen activity, for user with viewer_id
sorted_set = "uar:"+str(viewer_id) #unseen activity resorted (by whether notifs are seen or not)
user_presence = "up:"+str(user_id)+str(group_id)
user_presence = "up:"+str(user_id)+":"+str(group_id)
sorted_set = "whose_online_new"

###################################
'''
# changed connection from TCP port to UNIX socket
POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path='/var/run/redis/redis2.sock', db=0)

# 5,000,000,000 is most important priority wise
PRIORITY={'priv_mehfil':5000000000,'home_jawab':4000000000,'photo_tabsra':3000000000,'public_mehfil':2000000000,'photo_fan':2000000000,'namaz_invite':1000000000}

# Weightage of 'seen' status, used to find notification count for each user
SEEN={True:2000000000,False:4000000000}

FUTURE_EPOCH = 1609406042 #Human time (GMT): Thu, 31 Dec 2020 09:14:02 GMT

THREE_DAYS = 3*24*60*60
HALF_LIFE = THREE_DAYS #used in ranking public groups

# unseen_activity size limit (per user)
UA_LIMIT = 110
UA_TO_TRIM = 20

#######################Notifications#######################

'''
OBJECT types:
	link publicreply = '2'
	photo comment = '0'
	group chat = '3'
	salat invites = '4'
	photo upload = '1' #for fans only
'''

def delete_salat_notification(notif_name, hash_name, viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	# print "notif_name is: %s" % notif_name
	# print "hash_name is: %s" % hash_name
	# print "viewer id is: %s" % viewer_id
	# print "sn contains: %s" % my_server.zrange("sn:"+str(viewer_id), 0, -1)
	my_server.zrem("sn:"+str(viewer_id),notif_name)
	my_server.delete(hash_name)
	my_server.delete(notif_name)

def retrieve_latest_notification(viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "sn:"+str(viewer_id) # this contains the 'single notifications' of the user
	notif = my_server.zrange(sorted_set,-1,-1)
	notification = my_server.hgetall(notif[0])
	parent_object = my_server.hgetall(notification['c'])
	combined = dict(notification,**parent_object)
	return notif[0],notification['c'],combined

def retrieve_unseen_activity(viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "ua:"+str(viewer_id) #the sorted set containing 'unseen activity' notifications
	if my_server.zcard(sorted_set):
		hashes = my_server.zrevrange(sorted_set, 0, -1) #hashes are all notifications for user with id = viewer_id
		list_of_dictionaries = []
		pipeline1 = my_server.pipeline()
		pipeline2 = my_server.pipeline()
		for notification in hashes:
			notification = pipeline1.hgetall(notification)
		result1 = pipeline1.execute()
		# print result1
		for notification in result1:
			parent_object = pipeline2.hgetall(notification['c'])
		result2 = pipeline2.execute()
		# print result2
		for i in range(len(hashes)):
			if 'ot' in result2[i]:
				#i.e. it means object type is defined
				combined = dict(result2[i],**result1[i]) #combining the two dictionaries, using a Guido Von Rossum 'disapproved' hack (but very efficient!)
				list_of_dictionaries.append(combined)
		# print list_of_dictionaries
		return list_of_dictionaries
	else:
		return []

def bulk_update_salat_notifications(viewer_id=None, starting_time=None, seen=None, updated_at=None):
	my_server = redis.Redis(connection_pool=POOL)
	salat_invites_to_update = my_server.zrangebyscore("si:"+str(viewer_id),starting_time,'+inf')
	my_server.zremrangebyscore("si:"+str(viewer_id),starting_time,'+inf')
	for salat_invite in salat_invites_to_update:
		hash_name = "np:"+str(viewer_id)+":4:"+str(salat_invite)
		my_server.hmset(hash_name,{"s":seen,"u":updated_at})
		my_server.zrem("sn:"+str(viewer_id),hash_name)

def viewer_salat_notifications(viewer_id=None, object_id=None, time=None):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "si:"+str(viewer_id) #salat invites sent to viewer_id
	my_server.zadd(sorted_set,object_id,time)

# def create_photo_notification_for_fans():
# 	my_server = redis.Redis(connection_pool=POOL)

def bulk_create_photo_notifications_for_fans(viewer_id_list=None,object_id=None,seen=None,updated_at=None,unseen_activity=None):
	my_server = redis.Redis(connection_pool=POOL)
	increment = 0
	parent_object = "o:0:"+str(object_id) #points to the parent object each notification is related to
	pipeline1 = my_server.pipeline()
	for viewer_id in viewer_id_list:
		notification = "np:"+str(viewer_id)+":0:"+str(object_id)
		mapping = { 's':seen,'u':updated_at,'c':parent_object,'f':True,'nc':True }#'f' means for_fans, 'nc' means no_comment
		pipeline1.hmset(notification, mapping)
		#updating single_notif sorted set
		sorted_set = "sn:"+str(viewer_id) #'sn' is single notification, for user with viewer_id
		score = PRIORITY['photo_fan']+int(updated_at)
		pipeline1.zadd(sorted_set, notification, score) #where updated_at is the score
		#updating unseen_acitivity sorted set, if warranted
		if unseen_activity:
			increment += 1
			sorted_set = "ua:"+str(viewer_id) #'ua' is unseen activity, for user with viewer_id
			pipeline1.zadd(sorted_set, notification, updated_at) #where updated_at is the score
			sorted_set2 = "uar:"+str(viewer_id) #'uar' is unseen activity resorted (by whether notifs are seen or not)
			pipeline1.zadd(sorted_set2,notification,updated_at+SEEN[seen])
	pipeline1.hincrby(parent_object, 'n', amount=increment)
	pipeline1.execute()

def bulk_update_notifications(viewer_id_list=None, object_id=None, object_type=None, seen=None, updated_at=None, single_notif=None, \
	unseen_activity=None, priority=None):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for viewer_id in viewer_id_list:
		hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(object_id)
		pipeline1.exists(hash_name)	#list of all hashes that exist
	result1 = pipeline1.execute()
	count = 0
	pipeline2 = my_server.pipeline()
	for exist in result1:
		hash_name = "np:"+str(viewer_id_list[count])+":"+str(object_type)+":"+str(object_id)
		if exist:
			pipeline2.hset(hash_name, "s", seen) #updating 'seen'
			if updated_at:
				pipeline2.hset(hash_name, "u", updated_at)
			if single_notif is not None:
				sorted_set = "sn:"+str(viewer_id_list[count]) #'sn' is single notification, for user with viewer_id
				if single_notif:
					score = PRIORITY[priority]+int(time.time())
					pipeline2.zadd(sorted_set, hash_name, score)
				else:
					pipeline2.zrem(sorted_set, hash_name)
			if unseen_activity is not None:
				sorted_set = "ua:"+str(viewer_id_list[count]) #'ua' is unseen activity, for user with viewer_id
				sorted_set2 = "uar:"+str(viewer_id_list[count]) #'uar' is unseen activity resorted (by whether notifs are seen or not)
				if unseen_activity:
					#all updates will be bumped in ua: anyway, so no need for 'bump_ua' flag here
					epochtime = time.time()
					pipeline2.zadd(sorted_set, hash_name, epochtime)
					pipeline2.zadd(sorted_set2,hash_name,epochtime+SEEN[seen])
				else:
					pipeline2.zrem(sorted_set, hash_name)
					pipeline2.zrem(sorted_set2, hash_name)
		count += 1
	pipeline2.execute()

def update_notification(viewer_id=None, object_id=None, object_type=None, seen=None, updated_at=None, unseen_activity=None, \
	single_notif=None, priority=None, bump_ua=None, no_comment=None):
	my_server = redis.Redis(connection_pool=POOL)
	hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(object_id)
	if my_server.exists(hash_name):
		my_server.hset(hash_name,"s", seen) #updating 'seen'
		if no_comment is not True:
			my_server.hset(hash_name,"nc",no_comment)
		if updated_at:
			my_server.hset(hash_name, "u", updated_at) #updating 'updated_at' only if value is available
		if single_notif is not None:
			sorted_set = "sn:"+str(viewer_id) #'sn' is single notification, for user with viewer_id
			if single_notif:
				score = PRIORITY[priority]+int(time.time())
				my_server.zadd(sorted_set, hash_name, score)
			else:
				my_server.zrem(sorted_set, hash_name)
		if unseen_activity is not None:
			sorted_set = "ua:"+str(viewer_id) #'ua' is unseen activity, for user with viewer_id
			sorted_set2 = "uar:"+str(viewer_id) #'uar' is unseen activity resorted (by whether notifs are seen or not)
			epochtime = time.time()
			if bump_ua and unseen_activity:
				my_server.zadd(sorted_set, hash_name, epochtime)
				my_server.zadd(sorted_set2, hash_name, epochtime+SEEN[seen])
			elif unseen_activity:
				# only zadd if the member doesn't exist
				if my_server.zrank(sorted_set,hash_name) is None:
					my_server.zadd(sorted_set,hash_name, epochtime)
					my_server.zadd(sorted_set2, hash_name, epochtime+SEEN[seen])
				else:
					#i.e. don't bump up in unseen_activity by just 'viewing', but adjust notification counter
					my_server.zadd(sorted_set2, hash_name, epochtime+SEEN[seen])
					# pass
			else:	
				my_server.zrem(sorted_set, hash_name)
				my_server.zrem(sorted_set2, hash_name)
		return True
	else:
		return False

def create_notification(viewer_id=None, object_id=None, object_type=None, seen=None, updated_at=None, unseen_activity=None, \
	single_notif=None, priority=None, no_comment=None):
	my_server = redis.Redis(connection_pool=POOL)
	hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(object_id)
	composite_id = "o:"+str(object_type)+":"+str(object_id) #points to the parent object this notification is related to
	if my_server.exists(hash_name):
		return False
	else:
		mapping = { 's':seen,'u':updated_at,'c':composite_id,'nc':no_comment }
		my_server.hmset(hash_name, mapping)
		#updating unseen_acitivity sorted set
		if unseen_activity:
			sorted_set = "ua:"+str(viewer_id) #'ua' is unseen activity, for user with viewer_id
			sorted_set2 = "uar:"+str(viewer_id) #'uar' is unseen activity resorted (by whether notifs are seen or not)
			my_server.zadd(sorted_set, hash_name, updated_at) #where updated_at is the score
			my_server.zadd(sorted_set2, hash_name, updated_at+SEEN[seen])
			my_server.hincrby(composite_id, 'n', amount=1) #increment number_of_subscribers in parent_object. This is equivalent to number of unseen_activities the reply shows up in!
		#updating single_notif sorted set
		if single_notif:
			sorted_set = "sn:"+str(viewer_id) #'sn' is single notification, for user with viewer_id
			score = PRIORITY[priority]+int(updated_at)
			my_server.zadd(sorted_set, hash_name, score) #where updated_at is the score
		if my_server.zcard("ua:"+str(viewer_id)) > UA_LIMIT:
			from tasks import delete_notifications
			delete_notifications.delay(viewer_id)
		return True

def update_object(object_id=None, object_type=None, lt_res_time=None,lt_res_avurl=None,lt_res_sub_name=None,lt_res_text=None,\
	res_count=None, vote_score=None,reply_photourl=None, object_desc=None, just_vote=None):
	my_server = redis.Redis(connection_pool=POOL)
	hash_name = "o:"+str(object_type)+":"+str(object_id) #'o' is object, this contains link, photo, group, salat invite, video, etc.
	if object_type == '2':
		mapping={'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'r':res_count}
	elif object_type == '3':
		mapping={'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'rp':reply_photourl,\
		'od':object_desc}
	elif object_type == '0':
		if just_vote is True:
			mapping={'v':vote_score}
		else:
			mapping={'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'r':res_count,\
			'v':vote_score}
	my_server.hmset(hash_name, mapping)

def create_object(object_id=None, object_type=None, object_owner_avurl=None,object_owner_id=None,object_owner_name=None,\
	object_desc=None,lt_res_time=None,lt_res_avurl=None,lt_res_sub_name=None,lt_res_text=None,is_welc=None,res_count=None,\
	is_thnks=None, photourl=None, reply_photourl=None, group_privacy=None,vote_score=None, slug=None):
	my_server = redis.Redis(connection_pool=POOL)
	hash_name = "o:"+str(object_type)+":"+str(object_id) #'o' is object, this contains link, photo, group, salat invite, video, etc
	# print hash_name
	if my_server.exists(hash_name):
		return False
	else:
		if object_type == '2':
			#creating link object, with latest_response
			mapping={'oi':object_id,'ot':object_type,'ooa':object_owner_avurl,'ooi':object_owner_id,'oon':object_owner_name,\
			'od':object_desc,'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'w':is_welc,\
			'r':res_count}
		elif object_type == '3':
			#creating group chat object, with latest_response
			mapping = {'oi':object_id, 'ot':object_type,'ooi':object_owner_id,'od':object_desc,'lrti':lt_res_time,\
			'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'rp':reply_photourl,'g':group_privacy,'l':slug}
		elif object_type == '0':
			#creating photo object, with latest_response
			mapping = {'oi':object_id, 'ot':object_type, 'p':photourl, 'od':object_desc, 'ooa':object_owner_avurl,\
			'ooi':object_owner_id,'oon':object_owner_name,'v':vote_score, 'r':res_count,'lrti':lt_res_time, \
			'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text}
		elif object_type == '4':
			#creating salat_invite object
			mapping = {'oi':object_id,'ot':object_type,'oon':object_owner_name,'ooa':object_owner_avurl,'od':object_desc,\
			'ooi':object_owner_id}
		elif object_type == '1':
			#photo uploaded for fans. Fed from tasks.bulk_create_notifications()
			mapping = {'oi':object_id,'ot':object_type,'ooi':object_owner_id,'p':photourl,'v':vote_score,'l':slug,'t':is_thnks,\
			'r':res_count,'oon':object_owner_name, 'od':object_desc}
		elif object_type == '5':
			#video object
			mapping = {}
		my_server.hmset(hash_name, mapping)
		return True

# find whether a reply is seen or unseen (used in groups page)
def get_replies_with_seen(group_replies=None,viewer_id=None, object_type=None):
	my_server = redis.Redis(connection_pool=POOL)
	replies_list = []
	pipeline1 = my_server.pipeline()
	for reply in group_replies:
		hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(reply.which_group_id)
		pipeline1.hget(hash_name,'s')
	result1 = pipeline1.execute()
	count = 0
	for is_seen in result1:
		replies_list.append((group_replies[count],is_seen))
		count += 1
	return replies_list

def remove_group_object(group_id=None):
	my_server = redis.Redis(connection_pool=POOL)
	group_object = parent_object = "o:3:"+str(group_id)
	my_server.delete(group_object)

def remove_group_notification(user_id=None,group_id=None):
	my_server = redis.Redis(connection_pool=POOL)
	unseen_activity = "ua:"+str(user_id)
	unseen_activity_resorted = "uar:"+str(user_id) #'uar' is unseen activity resorted (by whether notifs are seen or not)
	single_notif = "sn:"+str(user_id)
	notification = "np:"+str(user_id)+":3:"+str(group_id)
	parent_object = "o:3:"+str(group_id)
	my_server.zrem(unseen_activity,notification)
	my_server.zrem(unseen_activity_resorted, notification)
	my_server.zrem(single_notif,notification)
	my_server.delete(notification)
	num_subscribers = my_server.hincrby(parent_object, 'n', amount=-1)

def clean_expired_notifications(viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	unseen_activity = "ua:"+str(viewer_id)
	unseen_activity_resorted = "uar:"+str(viewer_id) #'uar' is unseen activity resorted (by whether notifs are seen or not)
	single_notif = "sn:"+str(viewer_id)
	notif_to_del = my_server.zrevrange(unseen_activity,(UA_LIMIT-UA_TO_TRIM),-1)
	if notif_to_del:
		# sanitize the ua: sorted set, and uar: sorted set
		my_server.zrem(unseen_activity,*notif_to_del)
		my_server.zrem(unseen_activity_resorted,*notif_to_del)
		#sanitize the sn: sorted set
		my_server.zrem(single_notif,*notif_to_del)
		pipeline1 = my_server.pipeline()
		for notif in notif_to_del:
			#delete the notification hash
			pipeline1.delete(notif)
		result1 = pipeline1.execute()
		pipeline2 = my_server.pipeline()
		for notif in notif_to_del:
			object_hash="o:"+notif.split(":",2)[2]
			num_of_subscribers = pipeline2.hincrby(object_hash,"n",amount=-1)
		result2 = pipeline2.execute()
		count = 0
		pipeline3 = my_server.pipeline()
		for result in result2:
			if result < 1:
				#delete the object hash
				object_hash = "o:"+notif_to_del[count].split(":",2)[2]
				# print "hashes to delete are: %s" % object_hash
				pipeline3.delete(object_hash)
			count += 1
		result3 = pipeline3.execute()

def prev_unseen_activity_visit(viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	last_visit = 't:'+str(viewer_id)
	now = time.time()+SEEN[False]
	prev_time = my_server.getset(last_visit,now)
	if prev_time:
		return prev_time
	else:
		return now

def get_notif_count(viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "uar:"+str(viewer_id) #'uar' is unseen activity resorted (by whether notifs are seen or not)
	last_visit = 't:'+str(viewer_id)
	last_visit_time = my_server.get(last_visit) #O(1)
	count = my_server.zcount(sorted_set,'('+str(last_visit_time),'+inf') #O(log(N))
	return count

#####################Public Group Rankings#####################

#get public group's last 15 mins attendance

def get_attendance(group_id):
	my_server = redis.Redis(connection_pool=POOL)
	group_attendance = "ga:"+str(group_id)
	fifteen_mins_ago = time.time() - (15*60)
	return my_server.zrangebyscore(group_attendance, fifteen_mins_ago, '+inf')

#del public group's attendance register

def del_attendance(group_id):
	my_server = redis.Redis(connection_pool=POOL)
	group_attendance = "ga:"+str(group_id)
	my_server.delete(group_attendance)

#save attendance history for each public group

def public_group_attendance(group_id,user_id):
	my_server = redis.Redis(connection_pool=POOL)
	group_attendance = "ga:"+str(group_id)
	my_server.zadd(group_attendance,user_id,time.time())

# sanitize group from rankings if group owner wants to delete it

def del_from_rankings(group_id):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zrem("public_group_rankings", group_id)

#expire bottom feeders among top public groups

def expire_top_groups():
	my_server = redis.Redis(connection_pool=POOL)
	limit = 1000
	size = my_server.zcard("public_group_rankings")
	if size > limit:
		my_server.zremrangebyrank("public_group_rankings", 0, (size-limit-1))

#get public group rankings

def public_group_ranking():
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "public_group_rankings"
	return my_server.zrevrange(sorted_set,0,100,withscores=True) # returning highest 100 groups

#each reply or refresh in a group means the group is voted up!

def public_group_vote_incr(group_id,priority):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "public_group_rankings"
	increment_amount = 2**((time.time()-FUTURE_EPOCH)/HALF_LIFE) # <---- replace in 4 years from 10th Dec, 2016!
	increment_amount = increment_amount * priority #differentiate between refresh and reply, etc.
	my_server.zincrby(name=sorted_set, value=group_id,amount=increment_amount)

#####################Private Group Presence#####################

#saves the user's latest presence, to be used to show green, orange or grey blob
def save_user_presence(user_id,group_id,epochtime):
	my_server = redis.Redis(connection_pool=POOL)
	user_presence = "up:"+str(user_id)+":"+str(group_id)
	my_server.set(user_presence,epochtime)
	my_server.expire(user_presence,100) #expire the key after 100 seconds

#gets the latest presence for all users participating in the most recent 25 replies
def get_latest_presence(group_id, user_id_list):
	my_server = redis.Redis(connection_pool=POOL)
	pres_dict={}
	pipeline1 = my_server.pipeline()
	try:
		for user_id in user_id_list:
			user_presence = "up:"+str(user_id)+":"+str(group_id)
			time_since_last_viewing = pipeline1.get(user_presence) #time since last viewing
		result1 = pipeline1.execute()
		count = 0
		for user_id in user_id_list:
			try:
				pres_dict[user_id] = time.time() - float(result1[count])
			except:
				pres_dict[user_id] = 100.0
			count += 1
	except:
		pass
	return pres_dict

#######################Photo Fans#######################

def remove_from_photo_owner_activity(photo_owner_id,fan_id):
	my_server = redis.Redis(connection_pool=POOL)
	fans = "f:"+str(photo_owner_id)
	my_server.zrem(fans,fan_id)

def add_to_photo_owner_activity(photo_owner_id,fan_id):
	my_server = redis.Redis(connection_pool=POOL)
	fans = "f:"+str(photo_owner_id) # after 30 days, remove .exists() query from tasks.py's photo_tasks function
	my_server.zadd(fans,fan_id,time.time())

def get_active_fans(photo_owner_id, num_of_fans_to_notify):
	my_server = redis.Redis(connection_pool=POOL)
	fans = "f:"+str(photo_owner_id)
	return my_server.zrevrange(fans,0,(num_of_fans_to_notify-1))

#######################Whose Online#######################

def set_whose_online(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "whose_online_new"
	my_server.zadd(sorted_set, user_id, time.time())

def get_latest_online():
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "whose_online_new"
	ten_mins_ago = time.time() - (10*60)
	return my_server.zrangebyscore(sorted_set, ten_mins_ago, '+inf')

def expire_whose_online():
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "whose_online_new"
	ten_mins_ago = time.time() - (10*60)
	my_server.zremrangebyscore(sorted_set,'-inf',ten_mins_ago)

#######################Photos Benchmarking#######################

def set_benchmark(benchmark):
	my_server = redis.Redis(connection_pool=POOL)
	photos_benchmark = "photos_benchmark"
	my_server.delete(photos_benchmark)
	# print benchmark
	my_server.zadd(photos_benchmark,*benchmark)

def set_uploader_score(user_id,benchmark_score):
	my_server = redis.Redis(connection_pool=POOL)
	user_score_hash = "us:"+str(user_id)
	# benchmark_score = 3.1
	mapping = { 'b':benchmark_score }
	# print "user score over his last 5 photos is: %s" % benchmark_score
	my_server.hmset(user_score_hash, mapping)

def get_uploader_percentile(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	user_score_hash = "us:"+str(user_id) 
	user_score = my_server.hget(user_score_hash,'b')# 1.0
	# print "user score over last 5 photos is: %s " % user_score
	try:
		value = my_server.zrevrangebyscore('photos_benchmark','('+str(user_score), '-inf', start=0, num=1)
		if value:
			rank = my_server.zrank('photos_benchmark',value[0])+1 #added 1 because rank is 0 based
			# print "user rank is: %s" % rank
			cardinality = my_server.zcard('photos_benchmark')
			# print "cardinality is: %s" % cardinality
			# the uploader beat the following percentage of users:
			percentile = rank/(cardinality*1.0)
			# print "percentile is: %s" % percentile
		else:
			percentile = 0
			# print "no percentile calculated"
	except:
		percentile = 0
	return percentile

def get_top_100():
	my_server = redis.Redis(connection_pool=POOL)
	photos_benchmark = "photos_benchmark"
	return my_server.zrevrange(photos_benchmark,0,99,withscores=True)

# def get_user_rank(user_id):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	photos_benchmark = "photos_benchmark"
# 	rank = (my_server.zrevrank(photos_benchmark,user_id))
# 	if rank:
# 		return rank+1
# 	else:
# 		return None