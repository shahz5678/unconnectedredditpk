import redis
from random import random
from multiprocessing import Pool
from templatetags.s3 import get_s3_object
from score import PUBLIC_SUBMISSION_TTL, VOTE_SPREE_ALWD, FBS_PUBLIC_PHOTO_UPLOAD_RL
from location import REDLOC7

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC7, db=0)

CONTENT_SUBMISSION_AND_VOTING_BAN = "csv:"#prefix for hash containing details about a ban levied by a defender on a user
CONTENT_BAN_TEMP_KEY = "cbtk:"#prefix for key containing temporary data regarding a potentially bannable user
HOME_FEED = "homefeed:1000" # list containing latest 1000 home feed hashes (e.g. tx:234134 or img:341243)
PHOTO_FEED = "photofeed:1000" # list containing latest 1000 photo feed hashes (e.g. img:234132)
BEST_PHOTO_FEED = "bestphotofeed:1000"# list containing best 1000 photo feed hashes (e.g. img:123123)
VOTE_ON_IMG = "vi:" #prefix for a sorted set that contains users who voted on a particular image. Each user's vote value is used as a score
VOTE_ON_TXT = "vt:" #prefix for a sorted set that contains users who voted on a particular text post. Each user's vote value is used as a score

FBS_PUBLIC_PHOTO_UPLOAD_RATE_LIMIT = 'fbsuprl:'#rate limit key to throttle FBS users from uploading way too many public photos




TEN_MINS = 10*60
FORTY_FIVE_SECS = 45
NINE_SECS = 9


##################################################################################################################
################################# Detecting duplicate images post in public photos ###############################
##################################################################################################################


def already_exists(photo_hash,categ=None):
	my_server = redis.Redis(connection_pool=POOL)
	if categ == 'ecomm':
		exists = my_server.zscore("perceptual_hash_used_item_set", photo_hash)
	else:
		exists = my_server.zscore("perceptual_hash_set", photo_hash)
	return exists


def insert_hash(photo_id, photo_hash,categ=None):
	my_server = redis.Redis(connection_pool=POOL)
	if categ == 'ecomm':
		set_name = "perceptual_hash_used_item_set"
	else:
		set_name = "perceptual_hash_set"
	##########################
	try:
		size = my_server.zcard(set_name)
		if categ == 'ecomm':
			limit = 500
		else:
			limit = 10000
		if size < (limit+1):
			my_server.zadd(set_name, photo_hash, photo_id)
		else:
		   my_server.zremrangebyrank(set_name, 0, (size-limit-1))
		   my_server.zadd(set_name, photo_hash, photo_id)
	except:
		my_server.zadd(set_name, photo_hash, photo_id)


def delete_avg_hash(hash_list, categ=None):
	my_server = redis.Redis(connection_pool=POOL)
	if hash_list:
		if categ == 'ecomm':
			my_server.zrem("perceptual_hash_used_item_set", *hash_list)
		else:
			my_server.zrem("perceptual_hash_set", *hash_list)


##################################################################################################################
########################################## Content posted on the platform ########################################  
##################################################################################################################


def add_text_post(obj_id, categ, submitter_id, submitter_av_url, submitter_username, submitter_score, is_pinkstar,\
	text, submission_time, from_fbs, add_to_feed=False):
	"""
	Creating text object (used in home feed, etc)
	"""
	obj_id = str(obj_id)
	submitter_av_url = get_s3_object(submitter_av_url,category='thumb')#pre-convert avatar url for the feed so that we don't have to do it again and again
	hash_name = "tx:"+obj_id
	mapping = {'i':obj_id,'c':categ,'si':submitter_id,'sa':submitter_av_url,'su':submitter_username,'sc':submitter_score,\
	't':submission_time,'d':text,'nv':'0','uv':'0','dv':'0','pv':'0','h':hash_name}
	if from_fbs:
		mapping["fbs"]='1'
	if is_pinkstar:
		mapping['p']='1'
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	pipeline1.hmset(hash_name,mapping)
	pipeline1.expire(hash_name,PUBLIC_SUBMISSION_TTL)#setting ttl to one day
	#### initialize voting sorted set ####
	pipeline1.zadd(VOTE_ON_TXT+obj_id,-1,-1)
	pipeline1.expire(VOTE_ON_TXT+obj_id,PUBLIC_SUBMISSION_TTL)
	pipeline1.execute()
	if add_to_feed:
		add_obj_to_home_feed(hash_name, my_server)


def update_comment_in_home_link(reply,writer,is_pinkstar,time,writer_id,link_pk):
	"""
	Appends publicreply in home_replies_section
	"""
	hash_name = "tx:"+str(link_pk) #lk is 'link'
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(hash_name):
		#################################Saving latest publicreply################################
		existing_payload = my_server.hget(hash_name,'comms')
		payload = is_pinkstar+"#"+str(time)+"#"+str(writer_id)+"#"+writer+"#"+str(link_pk)+"#"+reply+"#el#"
		if existing_payload:
			existing_payload = truncate_payload(existing_payload)
			payload = existing_payload.decode('utf-8')+payload
		my_server.hset(hash_name,'comms',payload)
		amnt = my_server.hincrby(hash_name, "cc", amount=1) #updating comment count in home link
		return amnt
	else:
		return 0


def add_obj_to_home_feed(hash_name, my_server=None):
	"""
	Adding various objects to home feed
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	my_server.lpush(HOME_FEED, hash_name)
	my_server.ltrim(HOME_FEED, 0, 999)


def retrieve_obj_feed(obj_list):
	"""
	Retrieves details to show in home, top and fresh photos (full-fledged list of dictionaries)

	Works for both text and image objects
	"""
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for hash_name in obj_list:
		pipeline1.hgetall(hash_name)
	return filter(None, pipeline1.execute())


def get_home_feed():
	"""
	Retrieve list of all home feed objects
	"""
	return redis.Redis(connection_pool=POOL).lrange(HOME_FEED, 0, -1)   


def get_link_writer(link_id):
	"""
	Return writer_id of given link (only if redis object of link exists)
	"""
	return redis.Redis(connection_pool=POOL).hget("tx:"+str(link_id),'si')

def voted_for_link(link_id, voter_id):
	"""
	Retrieves whether user voted on given textual content

	Used by 'cast_vote' to ensure voter isn't double voting
	"""
	already_exists = redis.Redis(connection_pool=POOL).zscore(VOTE_ON_TXT+str(link_id), voter_id)
	if already_exists is None:
		# never voted
		return False
	else:
		# voted 1.0 (up) or 0.0 (down) - return value is a float
		return already_exists


def can_vote_on_obj(voter_id, is_pht):
	"""
	Vote blocking algorithm that cools down with time

	Used in 'cast_vote' to check whether potential voter is eligible to vote
	Works for both textual and image objects
	return values are: waiting_ttl, did_vote_go_through
	"""
	my_server, voter_id = redis.Redis(connection_pool=POOL), str(voter_id)
	votes_allowed = "pva:"+voter_id if is_pht == '1' else "va:"+voter_id #votes allowed to voter_id
	current_spree = my_server.get(votes_allowed)
	if current_spree is None:
		# i.e. user hasn't voted at all in the past [45 secs - 4.5 mins] (timeout depends on how aggressively the were voting earlier)
		my_server.incr(votes_allowed)
		my_server.expire(votes_allowed,FORTY_FIVE_SECS)
		return None, True
	elif int(current_spree) > (VOTE_SPREE_ALWD-1):#value set at '6' in the system (score.py)
		ttl = my_server.ttl(votes_allowed)
		return ttl, False
	else:
		# current spree exists
		short_term_rate_limit_key = 'rlpv:'+voter_id if is_pht == '1' else 'rlv:'+voter_id
		short_term_rate_limit = my_server.ttl(short_term_rate_limit_key)
		if short_term_rate_limit < 0:
			my_server.incr(votes_allowed)
			my_server.expire(votes_allowed,FORTY_FIVE_SECS*(int(current_spree)+1))
			return None, True
		else:
			# user has to wait a few seconds (upto 9) - they were voting super fast
			return short_term_rate_limit, False

def get_voting_details(obj_id, is_pht, only_exists=False):
	"""
	Returns for each content: net_votes, num of upvotes, num of downvotes, and num of votes by pinkstars

	Works for home, fresh and top photos
	"""
	hash_name = "img:"+obj_id if is_pht == '1' else "tx:"+obj_id #lk is 'link'
	my_server = redis.Redis(connection_pool=POOL)
	if only_exists:
		return my_server.exists(hash_name)
	else:
		if my_server.exists(hash_name):
			net_votes, upvotes, downvotes, pink_votes = my_server.hmget(hash_name,'nv','uv','dv','pv')
			return True, net_votes, upvotes, downvotes, pink_votes
		else:
			return False, None, None, None, None

def record_vote(obj_id,net_votes,is_upvote,is_pinkstar,username,own_id,revert_prev, is_pht):
	"""
	Record a vote on textual or photo objects (used in 'cast_vote')
	
	Records net_votes, num of upvotes, num of downvotes, and num of votes by pinkstars
	Only add if redis object exists. Otherwise voting is closed!
	Can take reputation under consideration (later)
	"""
	obj_id, own_id = str(obj_id), str(own_id)
	hash_name = "img:"+obj_id if is_pht == '1' else "tx:"+obj_id
	rate_limit_key = 'rlpv:'+own_id if is_pht == '1' else 'rlv:'+own_id
	vote_store = VOTE_ON_IMG+obj_id if is_pht == '1' else VOTE_ON_TXT+obj_id
	my_server = redis.Redis(connection_pool=POOL)
	obj_exists = my_server.exists(hash_name)#if redis obj exists, voting is still open (otherwise consider it closed)
	if obj_exists:
		if revert_prev:
			# reverting an old vote
			my_server.zrem(vote_store,own_id)
			my_server.hset(hash_name,'nv',net_votes)
			if is_upvote == '1':
				# this implies previous one was a downvote
				my_server.hincrby(hash_name,'dv',amount=-1)
			else:
				# this implies previous one was an upvote
				my_server.hincrby(hash_name,'uv',amount=-1)
			if is_pinkstar:
				# reduce one pv vote
				my_server.hincrby(hash_name,'pv',amount=-1)
			# reverting doesn't hit voting rate limits
			return True
		elif not my_server.exists(rate_limit_key):
			# cast vote normally
			my_server.zadd(vote_store,own_id, is_upvote)
			my_server.hset(hash_name,'nv',net_votes)
			if is_upvote == '1':
				my_server.hincrby(hash_name,'uv',amount=1)
			else:
				# is a downvote
				my_server.hincrby(hash_name,'dv',amount=1)
			if is_pinkstar:
				my_server.hincrby(hash_name,'pv',amount=1)
			###############################################
			# setting voting rate limit for those voting "too fast" (i.e. 3 times within 10 secs)
			vote_count_key = 'fpv:'+own_id if is_pht=='1' else 'fv:'+own_id
			is_set = my_server.setnx(vote_count_key,1)
			if is_set:
				# key didn't hitherto exist, now set its ttl
				my_server.expire(vote_count_key,10)
			else:
				# key already exists'
				new_value = my_server.incr(vote_count_key)
				if new_value > 2:
					# this person has voted 3 times in 10 seconds, rate limit them for 9 seconds
					my_server.setex(rate_limit_key,'1',NINE_SECS)
			return True
		else:
			return False
	else:
		return False


#################################################### Updating image content objects ############################################


def add_obj_to_photo_feed(hash_name, my_server=None):
	"""
	Adding various objects to photo feed
	"""
	if not my_server:
		my_server = redis.Redis(connection_pool=POOL)
	my_server.lpush(PHOTO_FEED, hash_name)
	my_server.ltrim(PHOTO_FEED, 0, 999)


def add_image_post(obj_id, categ, submitter_id, submitter_av_url, submitter_username, submitter_score, is_pinkstar,\
	img_url, img_caption, submission_time, from_fbs, add_to_home_feed=False, add_to_photo_feed=True):
	"""
	Creating image object (used in home and photo feed, etc)
	"""
	obj_id = str(obj_id)
	submitter_av_url = get_s3_object(submitter_av_url,category='thumb')#pre-convert avatar url for the feed so that we don't have to do it again and again
	img_thumb = get_s3_object(img_url,category="thumb")
	hash_name = "img:"+obj_id
	mapping = {'i':obj_id,'c':categ,'si':submitter_id,'sa':submitter_av_url,'su':submitter_username,'sc':submitter_score,\
	't':submission_time,'d':img_caption,'iu':img_url,'it':img_thumb,'nv':'0','uv':'0','dv':'0','pv':'0','h':hash_name}
	if from_fbs:
		mapping["fbs"]='1'
	if is_pinkstar:
		mapping['p']='1'#is_pinkstar
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	pipeline1.hmset(hash_name,mapping)
	pipeline1.expire(hash_name,PUBLIC_SUBMISSION_TTL)#setting TTL to one day
	#### initialize voting sorted set ####
	pipeline1.zadd(VOTE_ON_IMG+obj_id,-1,-1)
	pipeline1.expire(VOTE_ON_IMG+obj_id,PUBLIC_SUBMISSION_TTL)
	pipeline1.execute()
	if add_to_photo_feed:
		add_obj_to_photo_feed(hash_name, my_server)
	if add_to_home_feed:
		add_obj_to_home_feed(hash_name, my_server)
	return hash_name


def add_photo_comment(photo_id=None,photo_owner_id=None,latest_comm_text=None,latest_comm_writer_id=None,\
	is_pinkstar=None,latest_comm_writer_uname=None,comment_count=None, time=None):
	"""
	Adds comment to photo object (only if it exists in redis)
	"""
	hash_name = "img:"+str(photo_id)
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(hash_name):
		#################################Saving latest photo comment################################
		existing_payload = my_server.hget(hash_name,'comms')
		payload = is_pinkstar+"#"+latest_comm_writer_uname+"#"+str(time)+"#"+str(latest_comm_writer_id)+"#"+str(photo_id)+"#"+\
		latest_comm_text+"#el#" #el# signifies an end-of-line character
		if existing_payload:
			existing_payload = truncate_payload(existing_payload)
			payload = existing_payload.decode('utf-8')+payload
		my_server.hset(hash_name,'comms',payload)
		my_server.hincrby(hash_name,'cc',amount=1)


def get_raw_comments(photo_id):
	"""
	Returns comments associated to an image (if its redis object exists)
	"""
	return redis.Redis(connection_pool=POOL).hget("img:"+str(photo_id),"comms")

	
def truncate_payload(payload):
	"""
	Helper function for add_photo_comment and update_comment_in_home_link
	
	On average, truncate this after 10 messages have been aggregated
	"""
	if random() < 0.1:
		raw_text_set = filter(None,payload.split('#el#'))[-5:] #just keeping the latest 5 entries
		payload = '#el#'.join(raw_text_set)+"#el#" #reforming the payload
	return payload


def get_photo_owner(photo_id):
	"""
	Return owner id of photo object (only if redis object of link exists)
	"""
	return redis.Redis(connection_pool=POOL).hget("img:"+str(photo_id),'si')


def voted_for_single_photo(photo_id, voter_id):
	"""
	Retrieves whether user voted on given image content

	Used in 'cast_vote' to ensure user isn't double voting
	"""
	already_exists = redis.Redis(connection_pool=POOL).zscore(VOTE_ON_IMG+str(photo_id), voter_id)
	if already_exists is None:
		# i.e. does not already exist
		return False
	else:
		# voted 1.0 (up) or 0.0 (down) - return value is a float
		return already_exists


def get_photo_feed():
	"""
	Retrieve list of all image feed objects
	"""
	return redis.Redis(connection_pool=POOL).lrange(PHOTO_FEED, 0, -1)


def add_photos_to_best_photo_feed(photo_scores):
	"""
	Constructing bestphotofeed
	"""
	#executing the following commands as a single transaction
	try:
		my_server = redis.Redis(connection_pool=POOL)
		pipeline1 = my_server.pipeline()
		pipeline1.delete(BEST_PHOTO_FEED)
		pipeline1.zadd(BEST_PHOTO_FEED,*photo_scores)
		pipeline1.execute()
	except:
		pass


def get_best_photo_feed():
	"""
	Returns IDs of ranked images, alongwith scores
	"""
	return redis.Redis(connection_pool=POOL).zrevrange(BEST_PHOTO_FEED, 0, -1, withscores=True)


def is_fbs_user_rate_limited_from_photo_upload(user_id):
	"""
	Checks whether FBS user is rate limited from uploading a public image for the photo feed

	We implement rate limits on FBS users since their uploads are low quality in terms of resolution
	"""
	ttl = redis.Redis(connection_pool=POOL).ttl(FBS_PUBLIC_PHOTO_UPLOAD_RATE_LIMIT+str(user_id))
	if ttl > 0:
		return True, ttl
	else:
		return False, None


def rate_limit_fbs_public_photo_uploaders(user_id):
	"""
	Rate limiting fbs public photo uploaders
	"""
	redis.Redis(connection_pool=POOL).setex(FBS_PUBLIC_PHOTO_UPLOAD_RATE_LIMIT+str(user_id),'1',FBS_PUBLIC_PHOTO_UPLOAD_RL)

#################### Content submissiong and voting ban ####################

def retrieve_user_content_and_vote_ban_dictionary(user_id_list):
	"""
	Returns whether a list of users are vote banned (or not)

	Used to show ban-status of already vote-banned users so that defenders don't ban them yet again!
	"""
	pipeline1 = redis.Redis(connection_pool=POOL).pipeline()
	for user_id in user_id_list:
		pipeline1.exists(CONTENT_SUBMISSION_AND_VOTING_BAN+user_id)
	results1, counter, users_with_bans = pipeline1.execute(), 0, {}
	for user_id in user_id_list:
		users_with_bans[user_id] = '1' if results1[counter] else '0'
		counter += 1
	return users_with_bans


def check_content_and_voting_ban(target_user_id, with_details=False):
	"""
	Used to check if a user is banned, and if required, can also fetch the ban details for showing to the user
	
	"""
	hash_name = CONTENT_SUBMISSION_AND_VOTING_BAN+str(target_user_id)
	my_server = redis.Redis(connection_pool=POOL)
	hash_contents = my_server.hgetall(hash_name)
	if hash_contents:
		ban_type = hash_contents["b"]
		if ban_type == '6':
			if with_details:
				hash_contents['r'] = hash_contents['r'].decode('utf-8') if 'r' in hash_contents else ''
				hash_contents['oun'] = hash_contents['oun'].decode('utf-8') if 'oun' in hash_contents else ''
				hash_contents['dunm'] = hash_contents['dunm'].decode('utf-8') if 'dunm' in hash_contents else ''
				hash_contents['tunm'] = json.loads(hash_contents['tunm'])
				return True, '-1', hash_contents
			else:
				return True, '-1'#'-1' is forever in templates
		elif ban_type in ('1','2','3','4','5'):
			ban_start_time = hash_contents["t"]
			is_banned, time_remaining = ban_time_remaining(ban_start_time, ban_type, hash_name=hash_name)
			if with_details:
				hash_contents['r'] = hash_contents['r'].decode('utf-8') if 'r' in hash_contents else ''
				hash_contents['oun'] = hash_contents['oun'].decode('utf-8') if 'oun' in hash_contents else ''
				hash_contents['dunm'] = hash_contents['dunm'].decode('utf-8') if 'dunm' in hash_contents else ''
				hash_contents['tunm'] = json.loads(hash_contents['tunm'])
				return is_banned, time_remaining, hash_contents
			else:
				return is_banned, time_remaining
		else:
			if with_details:
				return False, None, None
			else:
				return False, None
	else:
		if with_details:
			return False, None, None
		else:
			return False, None

####################### Cleanse feed of content posted by punished user #######################

def cleanse_all_feeds_of_user_content(target_user_id, post_type, cleanse_feeds='1'):
	"""
	Ensures no content of target_user_id is part of current feeds

	Called when a defender bans a user's content
	Removes textual and image content both
	Suggested edit: IF CONTENT TYPE IS 'TX', ONLY CLEANSE FROM HOMEFEED
	"""
	if post_type not in ('img','tx'):
		pass
	elif cleanse_feeds != '1':
		pass
	else:
		target_user_id = str(target_user_id)
		my_server = redis.Redis(connection_pool=POOL)
		# retrieve all feeds
		pipeline1 = my_server.pipeline()
		pipeline1.lrange(PHOTO_FEED,0,-1)
		pipeline1.zrange(BEST_PHOTO_FEED,0,-1)
		pipeline1.lrange(HOME_FEED,0,-1)
		result1 = pipeline1.execute()
		fresh_image_objs, best_image_objs, home_objs = result1[0], result1[1], result1[2]
		
		
		# isolating target user's fresh photos
		pipeline2 = my_server.pipeline()
		for hash_name in fresh_image_objs:#contains img:4312341 type objs
			pipeline2.hget(hash_name,'si')
		result2, counter = pipeline2.execute(), 0
		target_fresh_photo_hashes = []
		for hash_name in fresh_image_objs:
			if result2[counter] == target_user_id:
				target_fresh_photo_hashes.append(hash_name)# i.e. all objs target user uploaded in photofeed:1000
			counter += 1

		#isolating target user's best photos
		pipeline3 = my_server.pipeline()
		for hash_name in best_image_objs:#contains img:4312341 type objs
			pipeline3.hget(hash_name,'si')
		result3, counter = pipeline3.execute(), 0
		target_best_photo_hashes = []
		for hash_name in best_image_objs:
			if result3[counter] == target_user_id:
				target_best_photo_hashes.append(hash_name)# i.e. all objs target user uploaded in bestphotofeed:1000
			counter += 1
		
		#isolating target user's home posts (text and photos both)
		pipeline4 = my_server.pipeline()
		for hash_name in home_objs:#contains tx:1231 or img:4312341 type objs
			pipeline4.hget(hash_name,'si')
		result4, counter = pipeline4.execute(), 0
		target_home_hashes = []
		for hash_name in home_objs:
			if result4[counter] == target_user_id:
				target_home_hashes.append(hash_name)# i.e. all objs target user uploaded in homefeed:1000
			counter += 1

		# 1) delete isolated hash, 2) expire voting objects so voting is 'closed' after ten more mins, 3) cleanse the feeds

		# removing target users' photofeed hashes, and expiring voting objs
		pipeline5 = my_server.pipeline()
		for hash_name in target_fresh_photo_hashes:
			pipeline5.delete(hash_name)
			pipeline5.expire(VOTE_ON_IMG+hash_name[4:],TEN_MINS)#expire - don't delete - so that a defender can ban voters if need be in the next 10 min window!
			pipeline5.lrem(PHOTO_FEED,hash_name, num=1)
		pipeline5.execute()

		# removing target users' bestphotofeed hashes, and expiring voting objs
		pipeline6 = my_server.pipeline()
		for hash_name in target_best_photo_hashes:
			pipeline6.delete(hash_name)#might have been deleted in the previous loop, but we need to catch cases where a hash may not have been in the previous list
			pipeline6.expire(VOTE_ON_IMG+hash_name[4:],TEN_MINS)
			pipeline6.zrem(BEST_PHOTO_FEED,hash_name)
		pipeline6.execute()

		# removing target users' homefeed hashes, and expiring voting objs
		pipeline7 = my_server.pipeline()
		for hash_name in target_home_hashes:
			pipeline7.delete(hash_name)
			if hash_name[:2] == 'tx':
				pipeline7.expire(VOTE_ON_TXT+hash_name[3:],TEN_MINS)
			else:
				pipeline7.expire(VOTE_ON_IMG+hash_name[4:],TEN_MINS)
			pipeline7.lrem(HOME_FEED,hash_name, num=1)
		pipeline7.execute()
		# this approach has a lot of duplication of effort, but is comprehensive