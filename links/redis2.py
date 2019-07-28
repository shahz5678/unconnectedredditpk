import redis, time
from location import REDLOC2
# from lua_scripts import storelogin, getlatestlogins, cleanselogins, retrieveclones

'''
##########Redis Namespace##########

fans = "f:"+str(photo_owner_id) // a sorted set
group_attendance = "ga:"+str(group_id)
latest_user_ip = "lip:"+str(user_id) #latest ip of user with 'user_id'
hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(object_id) #'np' is notification payload, contains notification data
hash_name = "o:"+str(object_type)+":"+str(object_id) #'o' is object, this contains link, photo, group, salat invite, video, etc.
photos_benchmark = "photos_benchmark"
sorted_set = "public_group_rankings"
recent_fans = "rf:"+photo_owner_id
user_score_hash = "us:"+str(user_id)
sorted_set = "si:"+str(viewer_id) #salat invites sent to viewer_id
sorted_set = "sn:"+str(viewer_id) #'sn' is single notification, for user with viewer_id
single_key = 't:'+str(viewer_id) #'t' stores time of last visit to unseen activity by viewer_id
sorted_set = "ua:"+str(viewer_id) #'ua' is unseen activity, for user with viewer_id
sorted_set = "uar:"+str(viewer_id) #unseen activity resorted (by whether notifs are seen or not)
user_ban = "ub:"+str(user_id)
user_presence = "up:"+str(user_id)+str(group_id)
user_presence = "up:"+str(user_id)+":"+str(group_id)
sorted_set = "whose_online_new"

###################################
'''
# changed connection from TCP port to UNIX socket
POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC2, db=0)

# 6,000,000,000 is most important priority wise
#PRIORITY={'personal_group':6000000000,'priv_mehfil':5000000000,'home_jawab':4000000000,'photo_tabsra':3000000000,'public_mehfil':2000000000,'photo_fan':2000000000,'namaz_invite':1000000000}
PRIORITY={'personal_group':6000000000,'priv_mehfil':5000000000,'home_jawab':5000000000,'photo_tabsra':5000000000,'public_mehfil':5000000000,'photo_fan':5000000000,'namaz_invite':1000000000}
# Weightage of 'seen' status, used to find notification count for each user
SEEN={True:2000000000,False:4000000000}

FUTURE_EPOCH = 1609406042 #Human time (GMT): Thu, 31 Dec 2020 09:14:02 GMT

TEN_MINS = 10*60
ONE_HOUR = 60*60
ONE_DAY = 1*24*60*60
THREE_DAYS = 3*24*60*60
HALF_LIFE = THREE_DAYS #used in ranking public groups

# unseen_activity size limit (per user)
UA_LIMIT = 70
UA_TO_TRIM = 20

#######################Notifications#######################

'''
OBJECT types:
	personal groups = '5'
	link publicreply = '2'
	photo comment = '0'
	group chat = '3'
	salat invites = '4'
	photo upload = '1' #for fans only
'''

def retrieve_object_data(obj_id,obj_type):
	my_server = redis.Redis(connection_pool=POOL)
	obj_name = "o:"+obj_type+":"+str(obj_id)
	return my_server.hgetall(obj_name)


# populates the single notification on the screen
def retrieve_latest_notification(viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	sorted_set = "sn:"+str(viewer_id) # this contains the 'single notifications' of the user
	notif = my_server.zrange(sorted_set,-1,-1)
	if notif:
		notification = my_server.hgetall(notif[0])
		try:
			parent_object = my_server.hgetall(notification['c'])
		except KeyError:
			remove_erroneous_notif(notif[0],viewer_id) #this notif was not associated to any object, as in group, photo etc
			return None, None, None
		if not parent_object:
			remove_erroneous_notif(notif[0],viewer_id) #this notif was not associated to an existing object
			return None, None, None
		else:
			combined = dict(notification,**parent_object)
			return notif[0],notification['c'],combined
	else:
		return None, None, None


def retrieve_unseen_notifications(viewer_id, start_idx=0, end_idx=-1, with_feed_size=False):
	"""
	Retrieves notifications to be shown in matka
	"""
	if with_feed_size:
		key = "ua:"+str(viewer_id)
		my_server = redis.Redis(connection_pool=POOL)
		return my_server.zrevrange(key, start_idx, end_idx), my_server.zcard(key)
	else:
		return redis.Redis(connection_pool=POOL).zrevrange("ua:"+str(viewer_id), start_idx, end_idx)


def retrieve_unseen_activity(notifications):
	"""
	Retrieves all information contained within notifications+objects, rendering the final form of the matka
	"""
	my_server = redis.Redis(connection_pool=POOL)
	list_of_dictionaries = []
	pipeline1 = my_server.pipeline()
	for notification in notifications:
		notif = pipeline1.hgetall(notification)
		associated_obj = pipeline1.hgetall("o:"+notification.split(":",2)[2])
	result = pipeline1.execute()
	i = 0
	while i < len(result):
		if 'c' in result[i] and 'ot' in result[i+1]:
			combined = dict(result[i],**result[i+1])
			if "lrsn" in combined:
				combined["lrsn"] = combined["lrsn"].decode('utf-8')
			if "uname1" in combined:
				combined["uname1"] = combined["uname1"].decode('utf-8')
			if "uname2" in combined:
				combined["uname2"] = combined["uname2"].decode('utf-8')
			list_of_dictionaries.append(combined)
		i += 2
	return list_of_dictionaries

################################################## Namaz Notifications ########################################################


def delete_salat_notification(notif_name, hash_name, viewer_id):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zrem("sn:"+str(viewer_id),notif_name)
	my_server.delete(hash_name)
	my_server.delete(notif_name)

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


###############################################################################################################################

def update_group_topic_in_obj(group_id, topic):
	"""
	Updates the topic field in a mehfil related object
	"""
	redis.Redis(connection_pool=POOL).hset("o:3:"+str(group_id), 'od', topic)

	
def update_object(object_id=None, object_type=None, lt_res_time=None,lt_res_avurl=None,lt_res_sub_name=None,lt_res_text=None,\
	res_count=None, vote_score=None,reply_photourl=None, object_desc=None, just_vote=None, lt_res_wid=None, slug=None):
	"""
	Updating already created notification object
	"""
	hash_name = "o:"+str(object_type)+":"+str(object_id) #'o' is object, this contains link, photo, group, salat invite, video, etc.
	if object_type == '2':
		mapping={'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'r':res_count, 'lrwi':lt_res_wid}
	elif object_type == '3':
		mapping={'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'rp':reply_photourl,'lrwi':lt_res_wid}
	elif object_type == '0':
		mapping={'v':vote_score} if just_vote else {'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,\
		'r':res_count,'v':vote_score, 'lrwi':lt_res_wid}
	redis.Redis(connection_pool=POOL).hmset(hash_name, mapping)


def create_object(object_id=None, object_type=None, object_owner_avurl=None,object_owner_id=None,object_owner_name=None,\
	object_desc=None,lt_res_time=None,lt_res_avurl=None,lt_res_sub_name=None,lt_res_text=None,is_welc=None,res_count=None,\
	is_thnks=None, photourl=None, reply_photourl=None, group_privacy=None,vote_score=None, slug=None, lt_res_wid=None):
	"""
	Creating a notification object that saves an element's latest state (e.g. a group object would be created, and it would contain its latest msgs)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	hash_name = "o:"+str(object_type)+":"+str(object_id) #'o' is object, this contains link, photo, group, salat invite, video, etc
	if my_server.exists(hash_name):
		return False
	else:
		if object_type == '2':
			#creating link object, with latest_response
			mapping={'oi':object_id,'ot':object_type,'ooa':object_owner_avurl,'ooi':object_owner_id,'oon':object_owner_name,\
			'od':object_desc,'lrti':lt_res_time,'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'w':is_welc,\
			'r':res_count,'lrwi':lt_res_wid}
		elif object_type == '3':
			#creating group chat object, with latest_response
			mapping = {'oi':object_id, 'ot':object_type,'ooi':object_owner_id,'od':object_desc,'lrti':lt_res_time,\
			'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'rp':reply_photourl,'g':group_privacy,'l':slug,\
			'lrwi':lt_res_wid}
		elif object_type == '0':
			#creating photo object, with latest_response
			mapping = {'oi':object_id, 'ot':object_type, 'p':photourl, 'od':object_desc, 'ooa':object_owner_avurl,\
			'ooi':object_owner_id,'oon':object_owner_name,'v':vote_score, 'r':res_count,'lrti':lt_res_time, \
			'lrau':lt_res_avurl,'lrsn':lt_res_sub_name,'lrtx':lt_res_text,'lrwi':lt_res_wid}
		elif object_type == '4':
			#creating salat_invite object
			mapping = {'oi':object_id,'ot':object_type,'oon':object_owner_name,'ooa':object_owner_avurl,'od':object_desc,\
			'ooi':object_owner_id}
		elif object_type == '1':
			#photo uploaded for fans. Fed from tasks.bulk_create_notifications()
			mapping = {'oi':object_id,'ot':object_type,'ooi':object_owner_id,'p':photourl,'v':vote_score,'l':slug,'t':is_thnks,\
			'r':res_count,'oon':object_owner_name, 'od':object_desc}
		elif object_type == '5':
			#new private chat object, functionality moved to update_private_chat_notif_object()
			mapping = {}
		my_server.hmset(hash_name, mapping)
		return True

# find whether a reply is seen or unseen (used in groups page)
def get_replies_with_seen(group_replies=None,viewer_id=None, object_type=None):
	my_server = redis.Redis(connection_pool=POOL)
	replies_list = []
	pipeline1 = my_server.pipeline()
	for reply in group_replies:
		hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(reply["which_group"])
		pipeline1.hget(hash_name,'s')
	result1 = pipeline1.execute()
	count = 0
	for is_seen in result1:
		replies_list.append((group_replies[count],is_seen))
		count += 1
	return replies_list


###########################################################################################################################	

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


# this does not update notifications for users whose notification object was deleted (or wasn't created in the first place)
def bulk_update_notifications(viewer_id_list=None, object_id=None, object_type=None, seen=None, updated_at=None, single_notif=None, \
	unseen_activity=None, priority=None):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for viewer_id in viewer_id_list:
		hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(object_id)
		pipeline1.exists(hash_name)	#list of all hashes that exist
	result1, count = pipeline1.execute(), 0
	pipeline2 = my_server.pipeline()
	for exist in result1:
		if exist:
			hash_name = "np:"+str(viewer_id_list[count])+":"+str(object_type)+":"+str(object_id)
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


# this does not update a notification whose notification object was deleted
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
				if my_server.zscore(sorted_set,hash_name) is None:
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
	single_notif=None, priority=None, no_comment=None, check_parent_obj=False):
	"""
	Notifications are generated so that users' matka can be populated

	Each social action causes notifications to be generated for all concerned users
	Notifications can be 'seen', or 'unseen'
	The user whose actions generated the notification always gets a 'seen' notifcation, others get an 'unseen' notification
	"""
	my_server = redis.Redis(connection_pool=POOL)
	hash_name = "np:"+str(viewer_id)+":"+str(object_type)+":"+str(object_id)#viewer_id is the user whose matka will receive the notification
	composite_id = "o:"+str(object_type)+":"+str(object_id) #points to the parent object this notification is related to
	notif_already_exists = my_server.exists(hash_name)
	if check_parent_obj:
		parent_exists = my_server.exists(composite_id)
		if notif_already_exists or not parent_exists:
			return False
	else:
		if notif_already_exists:
			return False
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
	
############################# Personal Group related notification functionality #############################

def get_latest_notif_obj_pgh(group_id,my_server=None,send_status=False):
	"""
	Retrieves pgh value parked in notif object, along with some other supporting values
	"""
	if not my_server:
		my_server = redis.Redis(connection_pool=POOL)
	if send_status:
		return my_server.hmget('o:5:{}'.format(group_id),'pgh','idx','type','d')
	else:
		return my_server.hmget('o:5:{}'.format(group_id),'pgh','idx','type')


def update_pg_obj_anon(value,object_id,user_id):
	"""
	Special function created to update personal group object's anon status

	This is triggered each time a user updates their anon status in a personal group
	This makes sure the anon status is correctly displayed in single and matka notifiations
	"""
	my_server, group_hash = redis.Redis(connection_pool=POOL), "o:5:{}".format(object_id)
	if my_server.exists(group_hash):
		# anon1 and anon2 contains user_ids that are experiencing anonymity in this personal group
		anon1, anon2 = my_server.hmget(group_hash,'anon1','anon2')
		user_id = str(user_id)
		if value == '0':
			# remove anon status
			if user_id == anon1:
				my_server.hset(group_hash,'anon1','')
			elif user_id == anon2:
				my_server.hset(group_hash,'anon2','')
			else:
				pass
		elif value == '1':
			# add anon status
			if user_id in (anon1,anon2):
				# already anonimyzed, do nothing (ensures one can't 'double add' anon status)
				pass
			else:
				if not anon1:
					# slot is empty, use it
					my_server.hset(group_hash,'anon1',user_id)
				elif not anon2:
					# anon1 was taken by the other user
					my_server.hset(group_hash,'anon2',user_id)
				else:
					# all slots are filled, error
					pass


def update_pg_obj_del(action,blob_id,blob_idx,group_id):
	"""
	Updates del status of personal group object (upon user deleting or undeleting object from their chat)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	curr_latest_pgh, idx, type_ = get_latest_notif_obj_pgh(group_id, my_server)
	if type_ in ('text','img'):
		group_hash, deleted_blob = "o:5:{}".format(group_id), "pgh:{}:{}".format(group_id,blob_id)
		# index matters, since this is a 'normal' blob
		if deleted_blob == curr_latest_pgh and blob_idx == idx:
			# update its status (action contain 'del' or 'undel')
			my_server.hset(group_hash,'d',action)
	else:
		group_hash, deleted_blob = "o:5:{}".format(group_id), "pgh:{}:{}".format(group_id,blob_id)
		# index doesn't matter, just compare pgh
		if deleted_blob == curr_latest_pgh:
			# update its status (action contain 'del' or 'undel')
			my_server.hset(group_hash,'d',action)

def update_pg_obj_hide(action,blob_id,blob_idx,group_id):
	"""
	Updates hide status of personal group object (upon user hiding or unhiding a photo from their chat)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	curr_latest_pgh, idx, type_ = get_latest_notif_obj_pgh(group_id, my_server)
	group_hash, hidden_blob = "o:5:{}".format(group_id), "pgh:{}:{}".format(group_id,blob_id) # good for readability, not faster than concatenation
	# only images can be hidden
	if type_ == 'img' and curr_latest_pgh == hidden_blob and blob_idx == idx:
		my_server.hset(group_hash,'h','yes' if action == 'hide' else 'no')
	elif type_ == 'img_res' and curr_latest_pgh == hidden_blob:
		my_server.hset(group_hash,'h','yes' if action == 'hide' else 'no')


def update_private_chat_notif_object(group_id,lt_res_wid,lt_res_sub_name,lt_res_avurl,lt_res_time,lt_res_text,reply_photourl,res_count,\
	object_desc,lt_pgh,deleted=None,hidden=None,anon1=None,anon2=None,target_uname=None, target_avurl=None,target_id=None,update=None):
	"""
	Updates (or creates) personal group's notification object
	"""
	group_obj = "o:5:"+group_id
	my_server = redis.Redis(connection_pool=POOL)
	already_exists = my_server.exists(group_obj)
	if already_exists:
		if update:
			# update object
			# 1) res_count contains index number, used to identify exact location of content in case it's a 'normal' blob
			# 2) type (object_desc) can be 'notif','img','img_res','text','text_res','action','reentry','exited','creation'
			mapping = {'lrwi':lt_res_wid,'lrsn':lt_res_sub_name,'lrau':lt_res_avurl,'lrti':lt_res_time,'lrtx':lt_res_text,'rp':reply_photourl,\
			'idx':res_count,'type':object_desc,'pgh':lt_pgh,'d':deleted,'h':hidden}
			my_server.hmset(group_obj,mapping)
			# now queue notifications
		else:
			# cannot create if already exists
			return None
	else:
		if update:
			# cannot update if it doesn't exist
			return None
		else:
			# create object
			# 1) adding anon statuses and uname-avurl pairs as 'one offs' during creation time (do not repeat adding these when 'updating')
			mapping = {'lrwi':lt_res_wid,'lrsn':lt_res_sub_name,'lrau':lt_res_avurl,'lrti':lt_res_time,'lrtx':lt_res_text,'rp':reply_photourl,\
			'idx':res_count,'type':object_desc,'pgh':lt_pgh,'d':deleted,'h':hidden,'anon1':anon1,'anon2':anon2,'uname1':lt_res_sub_name,\
			'avurl1':lt_res_avurl,'id1':lt_res_wid,'uname2':target_uname,'avurl2':target_avurl,'id2':target_id,'n':'2','ot':'5','oi':group_id}
			my_server.hmset(group_obj,mapping)
			# now queue notifications


def update_private_chat_notifications(sender_id, receiver_id, group_id, sender_seen, receiver_seen, updated_at, sender_ua, receiver_ua,\
	sender_sn, receiver_sn, sender_bump_ua, receiver_bump_ua):
	"""
	Updates notifications associated to personal group objects for both sender and receiver
	"""
	object_hash, sender_id = "o:5:"+group_id, str(sender_id)
	sender_notif = "np:"+sender_id+":5:"+group_id
	receiver_notif = "np:"+receiver_id+":5:"+group_id
	sender_mapping, receiver_mapping = {'s':sender_seen,'u':updated_at,'c':object_hash}, {'s':receiver_seen,'u':updated_at,'c':object_hash}
	ua_sender, ua_receiver = "ua:"+sender_id, "ua:"+receiver_id
	uar_sender, uar_receiver = "uar:"+sender_id, "uar:"+receiver_id
	sn_sender, sn_receiver = "sn:"+sender_id, "sn:"+receiver_id
	my_server = redis.Redis(connection_pool=POOL)
	sender_notif_exists = my_server.zscore(ua_sender,sender_notif)
	receiver_notif_exists= my_server.zscore(ua_receiver,receiver_notif)
	######################################################
	pipeline1 = my_server.pipeline()
	pipeline1.hmset(sender_notif,sender_mapping)
	pipeline1.hmset(receiver_notif,receiver_mapping)
	if sender_ua:
		if sender_bump_ua:
			pipeline1.zadd(ua_sender,sender_notif,updated_at)
			pipeline1.zadd(uar_sender,sender_notif,updated_at+SEEN[sender_seen]) #in uar, notifs are sorted according to whether they are seen or unseen
		else:
			if sender_notif_exists is None:
				pipeline1.zadd(ua_sender,sender_notif, updated_at)#adding to unseen activity (matka)
				pipeline1.zadd(uar_sender, sender_notif, updated_at+SEEN[sender_seen])#ensuring that added matka entry was seen
			else:
				#i.e. don't bump up in unseen_activity by just 'viewing', but do adjust notification counter (i.e. uar)
				pipeline1.zadd(uar_sender, sender_notif, updated_at+SEEN[sender_seen])
	if receiver_ua:
		if receiver_bump_ua:
			pipeline1.zadd(ua_receiver,receiver_notif,updated_at)
			pipeline1.zadd(uar_receiver,receiver_notif,updated_at+SEEN[receiver_seen]) #in uar, notifs are sorted according to whether they are seen or unseen
		else:
			if receiver_notif_exists is None:
				pipeline1.zadd(ua_receiver,receiver_notif, updated_at)
				pipeline1.zadd(uar_receiver, receiver_notif, updated_at+SEEN[receiver_seen])
			else:
				#i.e. don't bump up in unseen_activity by just 'viewing', but do adjust notification counter (i.e. uar)
				pipeline1.zadd(uar_receiver, receiver_notif, updated_at+SEEN[receiver_seen])
	if sender_sn:
		score = PRIORITY['personal_group']+int(updated_at)
		pipeline1.zadd(sn_sender, sender_notif, score) #where updated_at is the score
	else:
		pipeline1.zrem(sn_sender,sender_notif) # removing from single notification
	if receiver_sn:
		score = PRIORITY['personal_group']+int(updated_at)
		pipeline1.zadd(sn_receiver, receiver_notif, score) #where updated_at is the score
	else:
		pipeline1.zrem(sn_receiver,receiver_notif) # removing from single notification
	pipeline1.execute()
	######################################################
	sender_limit = my_server.zcard(ua_sender)
	receiver_limit = my_server.zcard(ua_receiver)
	if sender_limit > UA_LIMIT and receiver_limit > UA_LIMIT:
		from tasks import delete_notifications
		delete_notifications.delay(sender_id)
		delete_notifications.delay(receiver_id)
	elif sender_limit > UA_LIMIT:
		from tasks import delete_notifications
		delete_notifications.delay(sender_id)
	elif receiver_limit > UA_LIMIT:
		from tasks import delete_notifications
		delete_notifications.delay(receiver_id)
	else:
		pass



def skip_private_chat_notif(own_id, group_id,curr_time, seen=False):
	"""
	Removes notification from skipper's single_notif table and ensure it's 'seen' in matka
	"""
	own_id = str(own_id)
	own_notif, sn, uar = "np:"+own_id+":5:"+group_id, "sn:"+own_id, 'uar:'+own_id
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.hget(own_notif,'s') != 'True':
		pipeline1 = my_server.pipeline()
		pipeline1.hmset(own_notif,{'s':True,'u':curr_time,'c':"o:5:"+group_id}) #seen set to True, updated at set to current time
		pipeline1.zrem(sn,own_notif) #notification removed from single_notif sorted set
		pipeline1.zadd(uar,own_notif,curr_time+SEEN[seen]) #notification in matka is set to seen
		pipeline1.execute()


######################################## Sanitization functions ########################################

def remove_erroneous_notif(notif_name, user_id):
	"""
	Removes notification that does have associated object

	This way the notification feed of users is not blocked
	"""
	my_server = redis.Redis(connection_pool=POOL)
	user_id = str(user_id)
	sorted_set = "sn:"+user_id
	unseen_activity = "ua:"+user_id
	unseen_activity_resorted = "uar:"+user_id #'uar' is unseen activity resorted (by whether notifs are seen or not). Used to show 'digit' next to Matka in navbar
	pipeline1 = my_server.pipeline()
	pipeline1.zrem(sorted_set, notif_name)
	pipeline1.zrem(unseen_activity, notif_name)
	pipeline1.zrem(unseen_activity_resorted, notif_name)
	pipeline1.execute()
	my_server.delete(notif_name)


def sanitize_eachothers_unseen_activities(user1_id, user2_id):
	"""
	This ensures all posts of eachothers are deleted from the respective matkas

	It's called in the event of a user-initiated block
	Associated objects are deleted too if they fall below a certain subscriber limit
	"""
	user1_id, user2_id = str(user1_id),str(user2_id)
	ua1, ua2 = "ua:"+user1_id, "ua:"+user2_id
	my_server = redis.Redis(connection_pool=POOL)
	notif_list1 = my_server.zrange(ua1,0,-1) # list of user1's notifications
	notif_list2 = my_server.zrange(ua2,0,-1) # list of user2's notifications
	ob_list1, only_fives1 = [], []
	for notif in notif_list1:
		data = notif.split(":")
		obj_type = data[2]
		if obj_type == '5':
			only_fives1.append({'ob':"o:5:"+data[3],'np':notif})
		else:
			# all others go here    
			ob_list1.append({'ob':"o:"+obj_type+":"+data[3],'np':notif})
	ob_list2, only_fives2 = [], []
	for notif in notif_list2:
		data = notif.split(":")
		obj_type = data[2]
		if obj_type == '5':
			only_fives2.append({'ob':"o:5:"+data[3],'np':notif})
		else:
			# all others go here    
			ob_list2.append({'ob':"o:"+obj_type+":"+data[3],'np':notif})

	######## get IDs of all original posters of notif objects ########
	pipeline1 = my_server.pipeline()
	for obj in ob_list1:
		pipeline1.hget(obj['ob'],'ooi')
	result1 = pipeline1.execute()
	counter1,notifs1_to_del = 0, []
	for obj in ob_list1:
		if result1[counter1] == user2_id:
			notifs1_to_del.append(obj['np'])
		counter1 += 1

	pipeline2 = my_server.pipeline()
	for obj in only_fives1:
		pipeline2.hmget(obj['ob'],'id1','id2')
	result2 = pipeline2.execute()
	counter2 = 0
	for obj in only_fives1:
		if user2_id in result2[counter2]:
			notifs1_to_del.append(obj['np'])
		counter2 += 1


	pipeline3 = my_server.pipeline()
	for obj in ob_list2:
		pipeline3.hget(obj['ob'],'ooi')
	result3 = pipeline3.execute()
	counter3,notifs2_to_del = 0, []
	for obj in ob_list2:
		if result3[counter3] == user1_id:
			notifs2_to_del.append(obj['np'])
		counter3 += 1

	pipeline4 = my_server.pipeline()
	for obj in only_fives2:
		pipeline4.hmget(obj['ob'],'id1','id2')
	result4 = pipeline4.execute()
	counter4 = 0
	for obj in only_fives2:
		if user1_id in result4[counter4]:
			notifs2_to_del.append(obj['np'])
		counter4 += 1

	# notifs1_to_del contains all matka notifications of user1_id that belong to user2_id
	# notifs2_to_del contains all matka notifications of user2_id that belong to user1_id
	# these can now be deleted without prejudice
	uar1, uar2 = "uar:"+user1_id, "uar:"+user2_id
	sn1, sn2 = 'sn:'+user1_id, 'sn:'+user2_id
	
	if notifs1_to_del:
		# clean out ua, uar and sn for respective users
		my_server.zrem(ua1,*notifs1_to_del)
		my_server.zrem(uar1,*notifs1_to_del)
		my_server.zrem(sn1,*notifs1_to_del)

	if notifs2_to_del:
		# clean out ua, uar and sn for respective users
		my_server.zrem(ua2,*notifs2_to_del)
		my_server.zrem(uar2,*notifs2_to_del)
		my_server.zrem(sn2,*notifs2_to_del)

	all_notifs_to_delete = notifs1_to_del+notifs2_to_del

	if all_notifs_to_delete:
		# get rid of all notification objects themselves
		pipeline5 = my_server.pipeline()
		for notif in all_notifs_to_delete:
			pipeline5.delete(notif)
		pipeline5.execute()

		# decrement all related objects
		pipeline6 = my_server.pipeline()
		for notif in all_notifs_to_delete:
			object_hash = "o:"+notif.split(":",2)[2]
			pipeline6.hincrby(object_hash,"n",amount=-1)
		pipeline6.execute()
		
		# delete all objects with no subscribers
		objects_to_review = []
		for notif in all_notifs_to_delete:
			object_hash = "o:"+notif.split(":",2)[2]
			objects_to_review.append(object_hash)
		objects_to_review = list(set(objects_to_review))
		pipeline7 = my_server.pipeline()
		for obj in objects_to_review:
			pipeline7.hget(obj,'n')
		subscribers = pipeline7.execute()
		count8 = 0
		pipeline8 = my_server.pipeline()
		for obj in objects_to_review:
			if subscribers[count8] and int(subscribers[count8]) < 1:
				pipeline8.delete(obj)
			count8 += 1
		pipeline8.execute()

# def remove_notification_of_banned_user(target_id, object_id, object_type):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	target_id = str(target_id)
# 	notification = "np:"+target_id+":"+object_type+":"+object_id
# 	################################################################################
# 	sorted_set = "sn:"+target_id
# 	unseen_activity = "ua:"+target_id
# 	unseen_activity_resorted = "uar:"+target_id #'uar' is unseen activity resorted (by whether notifs are seen or not)
# 	pipeline1 = my_server.pipeline()
# 	pipeline1.zrem(sorted_set, notification)
# 	pipeline1.zrem(unseen_activity, notification)
# 	pipeline1.zrem(unseen_activity_resorted, notification)
# 	pipeline1.execute()
# 	my_server.delete(notification)


def remove_group_object(group_id, my_server=None):
	"""
	Deletes the group parent object
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.delete("o:3:"+str(group_id))


def bulk_remove_multiple_group_notifications(grp_ids_and_members):
	"""
	Given a list of groups, it removes all their redis 2 related content

	It's called when a groups have already been deleted from redis 6
	Useful when groups undergo 'full deletion' after becoming ghosts (i.e. idle > 30 days)
	grp_ids_and_members is a dictionary of the sort { group_id:[member_ids] }
	"""
	if grp_ids_and_members:
		my_server = redis.Redis(connection_pool=POOL)
		for group_id, member_ids in grp_ids_and_members.iteritems():
			bulk_remove_group_notification(member_ids, group_id, my_server=my_server)
			remove_group_object(group_id, my_server=my_server)


def bulk_remove_group_notification(user_ids, group_id, my_server=None):
	"""
	Bulk removes the a group's notifications from matka (when users leave or get kicked out)
	"""
	group_id = str(group_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	for user_id in user_ids:
		parent_obj = "o:3:"+group_id
		notification = "np:"+str(user_id)+":3:"+group_id
		my_server.zrem("ua:"+str(user_id),notification)
		my_server.zrem("uar:"+str(user_id),notification)
		my_server.zrem("sn:"+str(user_id),notification)
		my_server.delete(notification)
		if my_server.exists(parent_obj):
			# decrementing number of subscribers of the object by 1
			my_server.hincrby(parent_obj, 'n', amount=-1)

def remove_group_notification(user_id,group_id):
	"""
	Removes the group's notification from matka (when a user leaves the group)
	"""
	group_id, user_id = str(group_id), str(user_id)
	unseen_activity = "ua:"+user_id
	unseen_activity_resorted = "uar:"+user_id #'uar' is unseen activity resorted (by whether notifs are seen or not)
	single_notif = "sn:"+user_id
	notification = "np:"+user_id+":3:"+group_id
	parent_object = "o:3:"+group_id
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zrem(unseen_activity, notification)
	my_server.zrem(unseen_activity_resorted, notification)
	my_server.zrem(single_notif, notification)
	my_server.delete(notification)        
	if my_server.exists(parent_object):
		# decrementing number of subscribers of the object by 1
		my_server.hincrby(parent_object, 'n', amount=-1)


def bulk_delete_pergrp_notif(groups_and_participants, obj_type='5'):
	"""
	Removes o:5:<obj_id> type objects, and also associated notifications np:<user_id>:5:<obj_id> 

	groups_and_participants is a list of tuples of the type [(group_id1, user1, user2),(group_id2, user2, user3),(group_id3, user1, user3), ...]
	"""
	if groups_and_participants:
		pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
		for group_id,user1_id,user2_id in groups_and_participants:
			hash_id = "5:"+group_id
			# object to be deleted
			object_hash = "o:"+hash_id
			notif1_hash = "np:"+user1_id+":"+hash_id
			notif2_hash = "np:"+user2_id+":"+hash_id
			pipeline1.delete(object_hash)
			pipeline1.delete(notif1_hash)
			pipeline1.delete(notif2_hash)
			#user 1
			single1_notif = "sn:"+user1_id
			unseen1_activity = "ua:"+user1_id
			unseen1_activity_resorted = "uar:"+user1_id
			pipeline1.zrem(single1_notif,notif1_hash)
			pipeline1.zrem(unseen1_activity,notif1_hash)
			pipeline1.zrem(unseen1_activity_resorted,notif1_hash)
			#user 2
			single2_notif = "sn:"+user2_id
			unseen2_activity = "ua:"+user2_id
			unseen2_activity_resorted = "uar:"+user2_id
			pipeline1.zrem(single2_notif,notif2_hash)
			pipeline1.zrem(unseen2_activity,notif2_hash)
			pipeline1.zrem(unseen2_activity_resorted,notif2_hash)
		pipeline1.execute()

def clean_expired_notifications(viewer_id):
	"""
	Cleans a user's matka once it grows beyond a certain size
	"""
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
		# deleting actual notification objects
		pipeline1 = my_server.pipeline()
		for notif in notif_to_del:
			pipeline1.delete(notif)							
		pipeline1.execute()
		# decrementing subscriber counts
		pipeline2 = my_server.pipeline()
		for notif in notif_to_del:
			object_hash="o:"+notif.split(":",2)[2]
			num_of_subscribers = pipeline2.hincrby(object_hash,"n",amount=-1)
		result2 = pipeline2.execute()
		count = 0
		# deleting objects with no subscriptions
		pipeline3 = my_server.pipeline()
		for result in result2:
			if result < 1:
				#delete the object hash
				object_hash = "o:"+notif_to_del[count].split(":",2)[2]
				pipeline3.delete(object_hash)
			count += 1
		result3 = pipeline3.execute()


def bulk_sanitize_notifications(inactive_user_ids):
	"""Sanitize all notification activity of inactive users to free up space taken by redis2

	This is a helper function for remove_inactives_notification_activity()
	We will be removing the following for each inactive user:
	1) sn:<user_id> --- a sorted set containing home screen 'single notifications',
	2) ua:<user_id> --- a sorted set containing notifications for 'matka',
	3) uar:<user_id> --- a sorted set containing resorted notifications,
	4) np:<user_id>:*:* --- all notification objects associated to the user,
	5) o:*:* --- any objects that remain with < 1 subscribers,
	We will do everything in chunks of 10K, so that no server timeouts are encountered.
	"""
	if inactive_user_ids:
		from itertools import chain
		my_server = redis.Redis(connection_pool=POOL)
		#####################################################
		ids_to_process = []
		for user_id in inactive_user_ids:
			try:
				ids_to_process.append(str(int(user_id)))
			except:
				pass
		#####################################################
		# get all notification objects to delete
		pipeline1 = my_server.pipeline()
		for user_id in ids_to_process:
			pipeline1.zrange("sn:"+user_id, 0, -1)
			pipeline1.zrange("ua:"+user_id, 0, -1)#ua and uar have similar notifcations
		all_notifications_to_delete = list(set(chain.from_iterable(pipeline1.execute())))
		#####################################################
		# get all sorted sets to delete
		all_sorted_sets_to_delete = []
		for user_id in ids_to_process:
			all_sorted_sets_to_delete.append("sn:"+user_id)
			all_sorted_sets_to_delete.append("ua:"+user_id)
			all_sorted_sets_to_delete.append("uar:"+user_id)
		#####################################################
		# delete all notification objects and sorted sets
		pipeline2 = my_server.pipeline()
		for key_name in all_notifications_to_delete+all_sorted_sets_to_delete:
			pipeline2.delete(key_name)
		pipeline2.execute()
		#####################################################
		# decrement all related objects
		if all_notifications_to_delete:
			pipeline3 = my_server.pipeline()
			for notif in all_notifications_to_delete:
				object_hash="o:"+notif.split(":",2)[2]
				pipeline3.hincrby(object_hash,"n",amount=-1)
			pipeline3.execute()
			#####################################################
			# delete all objects with no subscribers
			objects_to_review = []
			for notif in all_notifications_to_delete:
				object_hash="o:"+notif.split(":",2)[2]
				objects_to_review.append(object_hash)
			objects_to_review = list(set(objects_to_review))
			pipeline4 = my_server.pipeline()
			for obj in objects_to_review:
				pipeline4.hget(obj,'n')
			subscribers = pipeline4.execute()
			count, objects_deleted= 0, 0
			pipeline5 = my_server.pipeline()
			for obj in objects_to_review:
				if subscribers[count] and int(subscribers[count]) < 1:
					objects_deleted += 1
					pipeline5.delete(obj)
				count += 1
			pipeline5.execute()
			return len(all_notifications_to_delete), len(all_sorted_sets_to_delete), objects_deleted
		else:
			return 0, len(all_sorted_sets_to_delete), 0
	else:
		return 0, 0, 0


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
	count = my_server.zcount(sorted_set,'('+str(last_visit_time),'+inf') if last_visit_time else 0
	return count

#####################Public Group Rankings#####################

# #get public group's last 15 mins attendance

# def get_attendance(group_id):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	group_attendance = "ga:"+str(group_id)
# 	fifteen_mins_ago = time.time() - (15*60)
# 	return my_server.zrangebyscore(group_attendance, fifteen_mins_ago, '+inf')

#del public group's attendance register

def del_attendance(group_id):
	my_server = redis.Redis(connection_pool=POOL)
	group_attendance = "ga:"+str(group_id)
	my_server.delete(group_attendance)


# sanitize group from rankings if group owner wants to delete it

# def del_from_rankings(group_id):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	my_server.zrem("public_group_rankings", group_id)

#expire bottom feeders among top public groups

# def expire_top_groups():
# 	my_server = redis.Redis(connection_pool=POOL)
# 	limit = 1000
# 	size = my_server.zcard("public_group_rankings")
# 	if size > limit:
# 		my_server.zremrangebyrank("public_group_rankings", 0, (size-limit-1))

#get public group rankings

# def public_group_ranking():
# 	my_server = redis.Redis(connection_pool=POOL)
# 	sorted_set = "public_group_rankings"
# 	return my_server.zrevrange(sorted_set,0,100,withscores=True) # returning highest 100 groups

#each reply or refresh in a group means the group is voted up!

# def public_group_vote_incr(group_id,priority):
# 	my_server = redis.Redis(connection_pool=POOL)
# 	sorted_set = "public_group_rankings"
# 	increment_amount = 2**((time.time()-FUTURE_EPOCH)/HALF_LIFE) # <---- replace in 4 years from 10th Dec, 2016!
# 	increment_amount = increment_amount * priority #differentiate between refresh and reply, etc.
# 	my_server.zincrby(name=sorted_set, value=group_id,amount=increment_amount)

#####################Private Group Presence#####################

#saves the user's latest presence, to be used to show green, orange or grey blob
def save_user_presence(user_id,group_id,epochtime):
	my_server = redis.Redis(connection_pool=POOL)
	my_server.setex("up:"+str(user_id)+":"+str(group_id),epochtime,100)

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
		time_now, count = time.time(), 0
		for user_id in user_id_list:
			try:
				pres_dict[user_id] = time_now - float(result1[count])
			except:
				pres_dict[user_id] = 100.0
			count += 1
	except:
		pass
	return pres_dict

#######################Photo Fans#######################

def remove_from_photo_owner_activity(photo_owner_id,fan_id):
	my_server = redis.Redis(connection_pool=POOL)
	photo_owner_id = str(photo_owner_id)
	pipeline1 = my_server.pipeline()
	pipeline1.zrem("f:"+photo_owner_id,fan_id)
	pipeline1.zrem("rf:"+photo_owner_id,fan_id)
	pipeline1.execute()

def add_to_photo_owner_activity(photo_owner_id,fan_id,new=None):
	my_server = redis.Redis(connection_pool=POOL)
	photo_owner_id = str(photo_owner_id)
	fans = "f:"+photo_owner_id # after 30 days, remove .exists() query from tasks.py's photo_tasks function
	time_now = time.time()
	my_server.zadd(fans,fan_id,time_now)
	if new:
		my_server.zadd("rf:"+photo_owner_id,fan_id, time_now)

def get_active_fans(photo_owner_id, num_of_fans_to_notify):
	my_server = redis.Redis(connection_pool=POOL)
	fans = "f:"+str(photo_owner_id)
	if num_of_fans_to_notify:
		return my_server.zrevrange(fans,0,(num_of_fans_to_notify-1))
	else:
		return None

def is_fan(photo_owner_id, fan_id):
	my_server = redis.Redis(connection_pool=POOL)
	fans = "f:"+str(photo_owner_id)
	if my_server.zscore(fans,fan_id):
		return True
	else:
		return False


def bulk_is_fan(star_id_list, fan_id):
	"""
	Determines all the ids a user is a fan of (from a given list of stars)

	Answers the question: Is fan_id actually a fan of anyone among the star_id_list?
	"""
	my_server, stars = redis.Redis(connection_pool=POOL), []
	##################################
	if len(star_id_list) > 0:
		pipeline1 = my_server.pipeline()
		for star_id in star_id_list:
			key = "f:"+star_id
			pipeline1.zscore(key,fan_id)
		result1, counter = pipeline1.execute(), 0
		for star_id in star_id_list:
			if result1[counter]:
				stars.append(star_id)
			counter += 1
	##################################
	elif star_id_list:
		for star_id in star_id_list:
			key = "f:"+star_id
			if my_server.zscore(key,fan_id):
				stars.append(star_id)
	return stars


def get_all_fans(photo_owner_id):
	my_server = redis.Redis(connection_pool=POOL)
	fans = "f:"+str(photo_owner_id)
	return my_server.zrevrange(fans,0,-1), my_server.zcard(fans), get_recent_fans(photo_owner_id,server=my_server)

def get_recent_fans(photo_owner_id, server=None):
	if not server:
		server = redis.Redis(connection_pool=POOL)
	photo_owner_id = str(photo_owner_id)
	recent_fans = "rf:"+photo_owner_id
	server.zremrangebyscore(recent_fans,'-inf',time.time()-ONE_DAY)
	return server.zrange(recent_fans,0,-1), server.zcard(recent_fans)

def get_photo_fan_count(photo_owner_id):
	my_server = redis.Redis(connection_pool=POOL)
	photo_owner_id = str(photo_owner_id)
	fans = "f:"+photo_owner_id
	return my_server.zcard(fans), get_recent_photo_fan_count(photo_owner_id,my_server)

def get_recent_photo_fan_count(photo_owner_id,server=None):
	if not server:
		server = redis.Redis(connection_pool=POOL)
	server.zremrangebyscore("rf:"+photo_owner_id,'-inf',time.time()-ONE_DAY)
	return server.zcard("rf:"+photo_owner_id)

def get_fan_counts_in_bulk(user_ids):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for user_id in user_ids:
		pipeline1.zcard("f:"+user_id)
	result = pipeline1.execute()
	fan_counts = {}
	counter = 0
	for user_id in user_ids:
		fan_counts[user_id] = result[counter]
		counter += 1
	return fan_counts 

#######################Photos Benchmarking#######################

def set_benchmark(benchmark):
	my_server = redis.Redis(connection_pool=POOL)
	photos_benchmark = "photos_benchmark"
	my_server.delete(photos_benchmark)
	my_server.zadd(photos_benchmark,*benchmark)


def set_uploader_score(user_id,benchmark_score):
	"""
	Sets avg vote score of the user's prev 5 photos
	"""
	redis.Redis(connection_pool=POOL).hset("us:"+str(user_id),'b',benchmark_score)


def get_uploader_percentile(user_id):
	my_server = redis.Redis(connection_pool=POOL)
	user_score_hash = "us:"+str(user_id) 
	user_score = my_server.hget(user_score_hash,'b')# 1.0
	try:
		value = my_server.zrevrangebyscore('photos_benchmark','('+str(user_score), '-inf', start=0, num=1)
		if value:
			rank = my_server.zrank('photos_benchmark',value[0])+1 #added 1 because rank is 0 based
			cardinality = my_server.zcard('photos_benchmark')
			# the uploader beat the following percentage of users:
			percentile = rank/(cardinality*1.0)
		else:
			percentile = 0
	except:
		percentile = 0
	return percentile

def get_top_100():
	my_server = redis.Redis(connection_pool=POOL)
	photos_benchmark = "photos_benchmark"
	return my_server.zrevrange(photos_benchmark,0,99)