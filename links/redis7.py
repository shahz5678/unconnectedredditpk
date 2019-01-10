import redis, time
from random import random
import ujson as json
from multiprocessing import Pool
from templatetags.s3 import get_s3_object
from score import PUBLIC_SUBMISSION_TTL, VOTE_SPREE_ALWD, FBS_PUBLIC_PHOTO_UPLOAD_RL
from page_controls import ITEMS_PER_PAGE_IN_ADMINS_LEDGER, DEFENDER_LEDGERS_SIZE, GLOBAL_ADMIN_LEDGERS_SIZE
from location import REDLOC7

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC7, db=0)

TWO_MONTHS = 2*4*7*24*60*60  
ONE_MONTH = 4*7*24*60*60 
TWO_WEEKS = 2*7*24*60*60 
ONE_WEEK = 7*24*60*60
FOUR_DAYS = 4*24*60*60
THREE_DAYS = 3*24*60*60
ONE_DAY = 24*60*60
TWELVE_HOURS = 12*60*60
SIX_HOURS = 6*60*60
THREE_HOURS = 3*60*60
ONE_HOUR = 60*60
TWENTY_MINS = 20*60
TEN_MINS = 10*60
FOUR_MINS = 4*60
FORTY_FIVE_SECS = 45
NINE_SECS = 9


DEFENDER_ADDITION_RATE_LIMITED = "darl:" #prefix for key that rate limits super admins from adding new defenders (FOUR_MINS each try)
DEFENDERS = "defs" # sorted set containing data of current defenders
DEFENDER_DATA = "dd:" # hash containing privileges available to defenders (in order to create M1, M2, etc)
DEFENDERS_FOREVER = 'defs_forever' # sorted set containing data of all defenders ever appointed


DEFENDERS_LEDGER = "dlg:" #prefix for a list which records the defenders last 40 blocks
GLOBAL_ADMINS_LEDGER = "ledger" # a global list for super admins, contains latest 3000 blocks
DEFENDER_CASE_COUNT = "dcn:" #hash prefix for a running counter of how many cases a said defender handled


COMPLAINT_LIST = "cl" #sorted set containing all reported content hashes (useful for 'cull list' view)
COMPLAINTS_SUBMITTED = "cs:" #sorted set logging complaint objs submitted by regular users (contains most recent 20 reports of a user)
COMPLAINT_HIST_OBJ = "co:" # a simple key containing a json object with complaint details logged by a regular user, used in 'historical' view of who reported what
COMPLAINT = "c:" #prefix for content, mehfil or profile report hash - contains all appended complaints for the same object, used in 'cull-list' etc
PAYABLES = "p:" #prefix for content payables sorted set - contains all point amounts owed to all reporter ids


COMPLAINING_RATE_LIMITED = "crl:" #prefix for sorted set used to rate limit regular users from reporting content too fast
COMPLAINER_TIME_LIST = "ctl" # sorted set containing time-sorted instances of latest time a user made any report
COMPLAINER_CORRECT_TIME_LIST = "cctl" # sorted set containing time-sorted instances of latest time a user made a 'correct' report
COMPLAINER_ATTEMPT_SORTED_SET = "cass" # sorted set containing sorted (by volume) instances of all reports made by a user
COMPLAINER_CORRECT_SORTED_SET = "ccss" # sorted set containing sorted (by volume) instances of correct reports made by a user
TOP_50_CACHED_DATA = "top_50_reporters" # key containing cached data of top 50 reporters


CONTENT_SUBMISSION_AND_VOTING_BAN = "csv:"#prefix for hash containing details about a ban levied by a defender on a user
CONTENT_BAN_TEMP_KEY = "cbtk:"#prefix for key containing temporary data regarding a potentially bannable user
HOME_FEED = "homefeed:1000" # list containing latest 1000 home feed hashes (e.g. tx:234134 or img:341243)
PHOTO_FEED = "photofeed:1000" # list containing latest 1000 photo feed hashes (e.g. img:234132)
BEST_PHOTO_FEED = "bestphotofeed:1000"# list containing best 1000 photo feed hashes (e.g. img:123123)
VOTE_ON_IMG = "vi:" #prefix for a sorted set that contains users who voted on a particular image. Each user's vote value is used as a score
VOTE_ON_TXT = "vt:" #prefix for a sorted set that contains users who voted on a particular text post. Each user's vote value is used as a score


FBS_PUBLIC_PHOTO_UPLOAD_RATE_LIMIT = 'fbsuprl:'#rate limit key to throttle FBS users from uploading way too many public photos



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
		comment_blob = my_server.hget(hash_name,'cb')
		comment_blob = truncate_payload(json.loads(comment_blob)) if comment_blob else []
		payload = {'is_pinkstar':is_pinkstar,'replier_username':writer,'link_id':link_pk,'text':reply,'replier_id':writer_id,\
		'epoch_time':time}
		comment_blob.append(payload)
		my_server.hset(hash_name,'cb',json.dumps(comment_blob))
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


def get_recent_photos(user_id):
	"""
	Contains last 5 photos

	This list self-deletes if user doesn't upload a photo for more than 4 days
	"""
	my_server = redis.Redis(connection_pool=POOL)
	return my_server.lrange("phts:"+str(user_id), 0, -1)


def save_recent_photo(user_id, photo_id):
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	pipeline1.lpush("phts:"+str(user_id), photo_id)
	pipeline1.ltrim("phts:"+str(user_id), 0, 4) # save the most recent 5 photos'
	pipeline1.expire("phts:"+str(user_id),FOUR_DAYS) #ensuring people who don't post anything for 4 days have to restart
	pipeline1.execute()


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
		comment_blob = my_server.hget(hash_name,'cb')
		comment_blob = truncate_payload(json.loads(comment_blob)) if comment_blob else []
		payload = {'is_pinkstar':is_pinkstar,'writer_uname':latest_comm_writer_uname,'text':latest_comm_text,'epoch_time':time,\
		'commenter_id':latest_comm_writer_id,'photo_id':photo_id}
		comment_blob.append(payload)
		my_server.hset(hash_name,'cb',json.dumps(comment_blob))
		my_server.hincrby(hash_name, "cc", amount=1) #updating comment count in home link


def get_raw_comments(photo_id):
	"""
	Returns comments associated to an image (if its redis object exists)
	"""
	return redis.Redis(connection_pool=POOL).hget("img:"+str(photo_id),"cb")

	
def truncate_payload(comment_blob):
	"""
	Helper function for add_photo_comment and update_comment_in_home_link
	
	On average, truncate this after 14 comments have been aggregated
	A 'comment_blob' is a list of lists stored as a JSON string
	"""
	return comment_blob[-5:] if (random() < 0.07 and comment_blob) else comment_blob


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


#################################################### Vote banning functionality (defenders) ############################################


def get_votes(obj_id,obj_type, with_net_score=False):
	"""
	Returns all vote values and voter_ids

	Used to show who voted which way on a piece of content (used by defenders)
	Once voting closes, this information is deleted from the system
	"""
	prefix = VOTE_ON_TXT if obj_type == 'tx' else VOTE_ON_IMG
	raw_data = redis.Redis(connection_pool=POOL).zrange(prefix+str(obj_id), 0, -1, withscores=True)
	final_data = []
	for tup in raw_data:
		if int(tup[0]) == -1 and int(tup[1]) == -1:
			#removing default (-1,-1) tuple since it's not a real ID,vote pair
			pass
		else:
			final_data.append((tup[0],tup[1]))# list of tuples, of the sort [('16', 1.0), ('2', 1.0)]
	if with_net_score:
		return final_data, int(sum(n for _, n in final_data))
	else:
		return final_data


def is_content_voting_closed(obj_id,obj_type):
	"""
	Returns whether voting on object is open or closed
	"""
	prefix = VOTE_ON_TXT if obj_type == 'tx' else VOTE_ON_IMG
	if redis.Redis(connection_pool=POOL).exists(prefix+str(obj_id)):
		return False
	else:
		return True


#################### Content submission and voting ban ####################


def ban_time_remaining(ban_time, ban_type,hash_name=None):
	"""
	Calculates ban time remaining of a user banned by a defender

	'ban_type' is:
		'1' is 3 hours
		'2' is 1 day
		'3' is 3 days
		'4' is 1 week
		'5' is 1 month
		'6' is forever
	"""
	current_time = time.time()
	time_difference = current_time - float(ban_time)
	if ban_type == '1':
		BENCHMARK_TIME_DIFF = THREE_HOURS
	elif ban_type == '2':
		BENCHMARK_TIME_DIFF = ONE_DAY
	elif ban_type == '3':
		BENCHMARK_TIME_DIFF = THREE_DAYS
	elif ban_type == '4':
		BENCHMARK_TIME_DIFF = ONE_WEEK
	elif ban_type == '5':
		BENCHMARK_TIME_DIFF = ONE_MONTH
	elif ban_type == '6':
		# banned forever
		return True, '-1'
	if time_difference < BENCHMARK_TIME_DIFF:
		return True, (float(ban_time)+BENCHMARK_TIME_DIFF)-current_time
	else:
		if hash_name:
			redis.Redis(connection_pool=POOL).delete(hash_name)    
		return False, None


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


def are_ids_unbannable(defender_id, target_id_list):
	"""
	Returns IDs that the defender_id is able to pass judgement on (and are not locked due to another defender handling the case)
	"""
	if target_id_list and defender_id:
		ban_keys, defender_id = [], str(defender_id)
		for target_id in target_id_list:
			ban_keys.append(CONTENT_SUBMISSION_AND_VOTING_BAN+str(target_id))
		my_server = redis.Redis(connection_pool=POOL)
		pipeline1 = my_server.pipeline()
		for ban_key in ban_keys:
			pipeline1.hget(ban_key,'did')
		result1 = pipeline1.execute()
		counter, unbannable_ids = 0, []
		for target_id in target_id_list:
			banner_id = result1[counter]
			if banner_id:
				if banner_id == defender_id:
					# banned by self, hence can ban
					pass
				else:
					# banned by someone else, cannot ban
					unbannable_ids.append(target_id)
			else:
				# not already banned, hence can ban
				pass
			counter += 1
		return unbannable_ids
	else:
		return None


def filter_ids_with_content_and_voting_ban(target_user_ids):
	"""
	Separates fed IDs into banned and unbanned IDs

	Useful in avoiding 'double banning'
	"""
	target_user_ids, ban_keys = map(str,target_user_ids), []
	for target_user_id in target_user_ids:
		ban_keys.append(CONTENT_SUBMISSION_AND_VOTING_BAN+target_user_id)
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	for ban_key in ban_keys:
		pipeline1.exists(ban_key)
	result1 = pipeline1.execute()
	unbanned_ids, banned_ids, counter = [], [], 0
	for target_user_id in target_user_ids:
		if result1[counter]:
			banned_ids.append(target_user_id)
		else:
			unbanned_ids.append(target_user_id)
		counter += 1
	return unbanned_ids, banned_ids


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


def remove_content_and_voting_ban(target_user_id, target_username, removal_reason, time_now, editor_id, editor_uname):
	"""
	Remove user's content submission ban (both photos or text)
	
	PARAMETERS:
	target_user_id: ID of the user who's ban is to be edited
	removal_reason: string containing reason why ban is removed
	time_now: time of editing/removal
	editor_id: ID of defender editing/removing the ban (i.e. self)
	editor_uname: username of defender editing/removing the ban (i.e. self)
	"""
	ban_key = CONTENT_SUBMISSION_AND_VOTING_BAN+str(target_user_id)
	my_server = redis.Redis(connection_pool=POOL)
	if my_server.exists(ban_key):
		ban_detail = my_server.hgetall(ban_key)
		old_editor_id, old_editor_uname, ban_levied_by = ban_detail.get('eid',''), ban_detail.get('eun',''), ban_detail['did']
		previously_banned_by_some_else = True if ban_levied_by != str(editor_id) else False
		if previously_banned_by_some_else and in_defenders(ban_levied_by,my_server):
			# if this person is still a defender, inform them about the removal
			# form payload for 'prev' defender (it will go in their ledger via 'lpush')
			payload_for_prev_defender_ledger = ban_detail
			payload_for_prev_defender_ledger['utid'] = target_user_id# the target user being unbanned
			payload_for_prev_defender_ledger['utunm'] = target_username# the target user being unbanned (same as 'oun' if bad_submission)
			payload_for_prev_defender_ledger['edit_time'] = time_now
			payload_for_prev_defender_ledger['edit_remark'] = removal_reason
			payload_for_prev_defender_ledger['eid'] = editor_id
			payload_for_prev_defender_ledger['eunm'] = editor_uname
			payload_for_prev_defender_ledger['oeid'] = old_editor_id
			payload_for_prev_defender_ledger['oeunm'] = old_editor_uname.decode('utf-8') if old_editor_uname else ''
			payload_for_prev_defender_ledger['act'] = 'ban_removed_by_other'# over writing 'act'
			pushed = push_to_defender_ledger(defender_id=ban_levied_by, json_payload=json.dumps(payload_for_prev_defender_ledger), also_super_admin=False, \
				my_server=my_server)# no need to save this in super admin's ledger, that will happen when 'payload_for_your_ledger' gets filled anyway
		payload_for_your_ledger = ban_detail
		payload_for_your_ledger['utid'] = target_user_id# the target user being unbanned
		payload_for_your_ledger['utunm'] = target_username# the target user being unbanned
		payload_for_your_ledger['edit_time'] = time_now
		payload_for_your_ledger['edit_remark'] = removal_reason
		payload_for_your_ledger['eid'] = editor_id
		payload_for_your_ledger['eunm'] = editor_uname
		payload_for_your_ledger['oeid'] = old_editor_id
		payload_for_your_ledger['oeunm'] = old_editor_uname.decode('utf-8') if old_editor_uname else ''
		payload_for_your_ledger['act'] = 'others_ban_removed_by_self' if previously_banned_by_some_else else 'own_ban_removed_by_self'
		pushed = push_to_defender_ledger(defender_id=editor_id, json_payload=json.dumps(payload_for_your_ledger), also_super_admin=True, my_server=my_server)
		# get the current ban ttl
		ban_exists = my_server.exists(ban_key)
		if ban_exists:
			ban_ttl = my_server.ttl(ban_key)
			# delete the ban before returning the value, to honor 'ban_removed' command
			my_server.delete(ban_key)
			if ban_ttl:
				return ban_ttl
			else:
				return 'forever'
		else:
			return 'key_does_not_exist'
	else:
		return 'key_does_not_exist'


def edit_content_and_voting_ban(target_user_id, target_username, edit_reason, new_dur, time_now, editor_id, editor_uname):
	"""
	PARAMETERS:
	target_user_id: ID of the user who's ban is to be edited
	new_dur: the new ban duration (encoded into '1','2','3','4','5','6')
	banner_uname: username of defender
	banner_id: ID of defender
	inform_prev_banner: Boolean depicting whether the previous banner has to be informed of this edition or not
	"""
	ban_key = CONTENT_SUBMISSION_AND_VOTING_BAN+str(target_user_id)
	my_server = redis.Redis(connection_pool=POOL)
	# get the current ban ttl
	ban_exists = my_server.exists(ban_key)
	if not ban_exists:
		return None, 'key_does_not_exist'
	else:
		original_ttl = my_server.ttl(ban_key)
		ban_detail = my_server.hgetall(ban_key)
		old_editor_id, old_editor_uname, ban_levied_by = ban_detail.get('eid',None), ban_detail.get('eun',None), ban_detail['did']
		previously_banned_by_some_else = True if ban_levied_by != str(editor_id) else False
		if previously_banned_by_some_else and in_defenders(ban_levied_by,my_server):
			# if this person is still a defender, inform them about the edit
			# form payload for 'prev' defender (it will go in their ledger via 'lpush')
			payload_for_prev_defender_ledger = ban_detail
			payload_for_prev_defender_ledger['utid'] = target_user_id# the target user being unbanned
			payload_for_prev_defender_ledger['utunm'] = target_username# the target user being unbanned (same as 'oun' if bad_submission)
			payload_for_prev_defender_ledger['edit_time'] = time_now
			payload_for_prev_defender_ledger['edit_remark'] = edit_reason
			payload_for_prev_defender_ledger['edit_dur'] = new_dur
			payload_for_prev_defender_ledger['eid'] = editor_id
			payload_for_prev_defender_ledger['eunm'] = editor_uname
			if old_editor_id:
				payload_for_prev_defender_ledger['oeid'] = old_editor_id
				payload_for_prev_defender_ledger['oeunm'] = old_editor_uname.decode('utf-8')
			payload_for_prev_defender_ledger['act'] = 'ban_edited_by_other'# over writing 'act'
			pushed = push_to_defender_ledger(defender_id=ban_levied_by, json_payload=json.dumps(payload_for_prev_defender_ledger), also_super_admin=False, \
				my_server=my_server)# no need to save this in super admin's ledger, that will happen when 'payload_for_your_ledger' gets filled anyway
		payload_for_your_ledger = ban_detail
		payload_for_your_ledger['utid'] = target_user_id# the target user being unbanned
		payload_for_your_ledger['utunm'] = target_username# the target user being unbanned
		payload_for_your_ledger['edit_time'] = time_now
		payload_for_your_ledger['edit_remark'] = edit_reason
		payload_for_your_ledger['edit_dur'] = new_dur
		payload_for_your_ledger['eid'] = editor_id
		payload_for_your_ledger['eunm'] = editor_uname
		if old_editor_id:
			payload_for_your_ledger['oeid'] = old_editor_id
			payload_for_your_ledger['oeunm'] = old_editor_uname.decode('utf-8')
		payload_for_your_ledger['act'] = 'others_ban_edited_by_self' if previously_banned_by_some_else else 'own_ban_edited_by_self'
		pushed = push_to_defender_ledger(defender_id=editor_id, json_payload=json.dumps(payload_for_your_ledger), also_super_admin=True, my_server=my_server)
		#############################################
		# retrieve some required details from existing ban
		old_dur, old_time = ban_detail['b'], ban_detail['t']
		# add some required details into existing ban to edit it
		context = {'b':new_dur,'t':time_now,'ob':old_dur,'ot':old_time,'eid':editor_id,'eun':editor_uname}
		if has_super_privilege(editor_id,my_server):
			context["sd_lock"] = '1'# super_defender_lock is in place
		my_server.hmset(ban_key,context)
		# edit the ban's ttl
		if new_dur == '1':
			# ban for 3 hrs
			my_server.expire(ban_key,THREE_HOURS)
			expire_time = THREE_HOURS
		elif new_dur == '2':
			# ban for 24 hrs
			my_server.expire(ban_key,ONE_DAY)
			expire_time = ONE_DAY
		elif new_dur == '3':
			# ban for 3 days
			my_server.expire(ban_key,THREE_DAYS)
			expire_time = THREE_DAYS
		elif new_dur == '4':
			# ban for 1 week
			my_server.expire(ban_key,ONE_WEEK)
			expire_time = ONE_WEEK
		elif new_dur == '5':
			# ban for 1 month
			my_server.expire(ban_key,ONE_MONTH)
			expire_time = ONE_MONTH
		else:
			# ban 'forever'
			my_server.persist(ban_key)# remove any 'ttl' that might exist
			expire_time = 'forever'
		if old_dur == '6':
			return expire_time,'forever'
		else:
			# return original_ttl
			return expire_time,original_ttl


def is_ban_editing_locked(banned_id):
	"""
	Checks if a ban has been locked after a super defender changed it
	"""
	if redis.Redis(connection_pool=POOL).hget(CONTENT_SUBMISSION_AND_VOTING_BAN+str(banned_id),'sd_lock') == '1':
		return True
	else:
		return False


def impose_content_and_voting_ban(target_user_ids, target_usernames, ban_duration, current_time, banner_uname, obj_type, obj_id, obj_owner_uname, \
	obj_owner_id, ban_reason, reference, banner_id, sin):
	"""
	This is triggered when content submitter or malicious voter are slapped with a ban

	PARAMETERS:
	'target_user_ids': list of ids that are to be banned
	'target_usernames': list of usernames that are being banned
	'ban_duration': ranges between '1','2','3','4','5' and '6', and denotes the duration of the ban
	'current_time': time at the point of banning
	'banner_uname': username of the banning defender
	'obj_type': 'tx' or 'img' object
	'obj_id': object ID
	'obj_owner_uname': username of the object owner. Same as target_usernames list if banning a content submitter, or could be different if banning bad voters
	'obj_owner_id': ID of the object owner. Same as target_user_ids if banning a content submitter, or coule be different if banning bad voters
	'ban_reason': ban reason provided by the defender (in defender's own words)
	'reference': data containing a reference a banned user can be shown regarding the text/image object that was acted upon
	'banner_id': defender ID
	'sin': string identifying why user is being banned. 'bad_submission' if it's a malicious content submission, otherwise 'bad_voting'
	"""
	if ban_duration not in ('1','2','3','4','5','6') or not sin:
		return None
	else:
		# creating keys allowing banned users to see their ban payloads
		target_user_ids, ban_keys = map(str,target_user_ids), []
		for target_user_id in target_user_ids:
			ban_keys.append(CONTENT_SUBMISSION_AND_VOTING_BAN+target_user_id)

		# forming payload to be shown to the banned user
		payload = {'t':current_time,'b':ban_duration,'tp':obj_type, 'remark':ban_reason, 'oun':obj_owner_uname, 'obid':obj_id, 'sin':sin,\
		'did':banner_id,'dunm':banner_uname,'tunm':json.dumps(target_usernames),'act':'banned'}
		if obj_type == 'tx':
			payload['txt'] = reference
		else:
			payload['pu'] = reference

		# determining ban durations
		if ban_duration == '1':
			# ban for 3 hrs
			ban_time = THREE_HOURS
		elif ban_duration == '2':
			# ban for 24 hrs
			ban_time = ONE_DAY
		elif ban_duration == '3':
			# ban for 3 days
			ban_time = THREE_DAYS
		elif ban_duration == '4':
			# ban for 1 week
			ban_time = ONE_WEEK
		elif ban_duration == '5':
			# ban for 1 month
			ban_time = ONE_MONTH
		else:
			# do nothing, ban 'forever'
			ban_time = '-1'

		# setting user ban(s)
		my_server = redis.Redis(connection_pool=POOL)
		pipeline1 = my_server.pipeline()
		for ban_key in ban_keys:
			pipeline1.hmset(ban_key,payload)
			if ban_time != '-1':
				pipeline1.expire(ban_key,ban_time)
		pipeline1.execute()

		# logging the fact that defender 'handled' a case (incrementing their case file's counter)
		if sin == "bad_submission":
			increment_defender_case_file(banner_id,'bad_submission',my_server)
		elif sin == "bad_voting":
			# even if multiple voters banned, it's counted as 1 case
			increment_defender_case_file(banner_id,'bad_voting',my_server)

		# adding to defender's and super_admin's ledgers
		json_payload = json.dumps(payload)
		pushed = push_to_defender_ledger(defender_id=banner_id, json_payload=json_payload, also_super_admin=True, my_server=my_server)

		return ban_time


def increment_defender_case_file(defender_id,sin,my_server=None):
	"""
	Tracks number of various cases handled by a defender during their tenure
	"""
	defender_id = str(defender_id)
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if sin == 'bad_submission':
		my_server.hincrby(DEFENDER_CASE_COUNT+defender_id,'bad_submission',amount=1)
	elif sin == 'bad_voting':
		my_server.hincrby(DEFENDER_CASE_COUNT+defender_id,'bad_voting',amount=1)
	elif sin == 'bad_profile':
		my_server.hincrby(DEFENDER_CASE_COUNT+defender_id,'bad_profile',amount=1)# i.e. bad profile pic or bad nickname
	elif sin == 'bad_mehfil':
		my_server.hincrby(DEFENDER_CASE_COUNT+defender_id,'bad_mehfil',amount=1)# i.e bad topic or rules
	else:
		pass


def push_to_defender_ledger(defender_id, json_payload, also_super_admin=False, my_server=None):
	"""
	Pushes banning data into defender's and super_admin's respective ledgers
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if in_defenders(defender_id, my_server):
		defenders_ledger = DEFENDERS_LEDGER+str(defender_id)
		my_server.lpush(defenders_ledger, json_payload)#defenders' ledger
		my_server.ltrim(defenders_ledger, 0, (DEFENDER_LEDGERS_SIZE-1))# keeping latest 40 blocks/unblocks for each defender
		if also_super_admin:
			my_server.lpush(GLOBAL_ADMINS_LEDGER,json_payload)#global admin's ledger
			my_server.ltrim(GLOBAL_ADMINS_LEDGER, 0, (GLOBAL_ADMIN_LEDGERS_SIZE-1))# keeps most recent 3000 blocks/unblocks
		return True
	else:
		return False

		
##################### Defenders case logging #####################


def get_defenders_ledger(defender_id, with_ttl=False):
	"""
	Retrieves previous banning activity of given defender
	"""
	info, my_server, ledger_key = [], redis.Redis(connection_pool=POOL), DEFENDERS_LEDGER+str(defender_id)
	data = my_server.lrange(ledger_key,0,-1)
	if data:
		for block_info in data:
			credentials = json.loads(block_info)
			credentials['tunm'] = json.loads(credentials['tunm'])
			info.append(credentials)
	if with_ttl:
		ttl = my_server.ttl(ledger_key)
		if ttl > 4:
			return info, ttl# a 'ttl' is enforced on the ledger if defender has been removed (i.e. this is a legacy ledger)
		else:
			return info, None
	else:
		return info


def get_global_admins_ledger(page_number):
	"""
	Retrieves previous banning activity of all defenders
	"""
	info, my_server = [], redis.Redis(connection_pool=POOL)
	data = my_server.lrange(GLOBAL_ADMINS_LEDGER,ITEMS_PER_PAGE_IN_ADMINS_LEDGER*(page_number-1),(ITEMS_PER_PAGE_IN_ADMINS_LEDGER*page_number)-1)#ITEMS_PER_PAGE_IN_ADMINS_LEDGER = 50
	if data:
		for block_info in data:
			credentials = json.loads(block_info)
			credentials['tunm'] = json.loads(credentials['tunm'])
			credentials['dunm'] = credentials['dunm'].encode('utf-8')# if 'dunm' in credentials else ''
			info.append(credentials)
	if info:
		return info, my_server.llen(GLOBAL_ADMINS_LEDGER)
	else:
		return [], 0


def log_banning(target_uname,reason_of_ban,action, dur_of_ban,time_of_ban,banned_by_id,banned_by_uname, obj_id, owner_id, oun, \
	photo_thumb=None, cap=None, ban_type=None, obj_type=None):
	"""
	Logging banning event for defender and super admins (for later reference)

	Also keeps account of banning for global admin
	'action' is 'banned_content_submitter' 'undo_content_ban' 'banned_voter' ('tp' is type of obj)
	"""
	banning_data = {'rsn':reason_of_ban,'dur':dur_of_ban,'t':time_of_ban,'obj_id':obj_id,'owner_id':owner_id,'act':action, \
	'tunm':target_uname,'oun':oun, 'bt':ban_type, 'tp':obj_type}# target_uname can be a list of unames if multi_ban is being documented (over erroneous voting)
	if obj_type == 'tx':
		banning_data['c'] = cap
	else:
		banning_data['p'] = photo_thumb
	my_server, defenders_ledger = redis.Redis(connection_pool=POOL), DEFENDERS_LEDGER+str(banned_by_id)
	my_server.lpush(defenders_ledger,json.dumps(banning_data))#defenders' ledger
	my_server.ltrim(defenders_ledger, 0, 39)# keeping latest 40 blocks/unblocks for each defender
	# save for global admin as well
	banning_data["did"] = banned_by_id
	banning_data['dunm'] = banned_by_uname
	my_server.lpush(GLOBAL_ADMINS_LEDGER,json.dumps(banning_data))#global admin's ledger
	my_server.ltrim(GLOBAL_ADMINS_LEDGER, 0, (ADMIN_LEDGERS_SIZE-1))# keeps most recent 3000 blocks/unblocks


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


##################### Adding or removing defenders ######################


def in_defs_forever(user_id):
	"""
	Checks if given user ID is a defender (currently or in the past)

	DEFENDERS is a current list
	DEFENDERS_FOREVER is a lasting list of all defenders ever
	"""
	if redis.Redis(connection_pool=POOL).zscore(DEFENDERS_FOREVER, user_id):
		return True
	else:
		return False


def in_defenders(user_id, my_server=None, return_super_status=False):
	"""
	Checks if given user ID is indeed a defender currently

	DEFENDERS is a current list
	DEFENDERS_FOREVER is a lasting list of all defenders ever
	"""
	my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
	if my_server.zscore(DEFENDERS, user_id):
		if return_super_status:
			priv_level = my_server.hget(DEFENDER_DATA+str(user_id),'priv')
			if priv_level == '1':
				return True, True
			else:
				return True, False
		else:
			return True
	else:
		if return_super_status:
			return False, False
		else:
			return False


def has_super_privilege(user_id, my_server=None):
	"""
	Checks whether a given user_id has super defender priveleges (outlined in add_defender()'s docstring)
	"""
	is_defender, is_super = in_defenders(user_id, my_server=my_server, return_super_status=True)
	return is_super


def retrieve_all_defenders(mark_super=False):
	"""
	Returns all current and olden defenders

	if 'mark_super' is set, return the privilege level of current defenders too
	"""
	my_server = redis.Redis(connection_pool=POOL)
	curr_defenders = my_server.zrevrange(DEFENDERS,0,-1, withscores=True)
	all_defenders = my_server.zrevrange(DEFENDERS_FOREVER,0,-1, withscores=True)
	if mark_super:
		curr_defenders_with_privs = []
		for curr_def_id,adding_time in curr_defenders:
			priv_level = '1' if my_server.hget(DEFENDER_DATA+curr_def_id,'priv') == '1' else '0'
			curr_defenders_with_privs.append((curr_def_id,adding_time,priv_level))
		return curr_defenders, all_defenders, curr_defenders_with_privs
	else:
		return curr_defenders, all_defenders


def remove_defender(user_id):
	"""
	Remove from defender list

	Keep user_id intact in DEFENDERS_FOREVER (so we can always tell who was once a defender)
	"""
	user_id = str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	my_server.zrem(DEFENDERS, user_id)
	my_server.delete(DEFENDER_DATA+user_id)# removing the hash map with defender data
	my_server.expire(DEFENDERS_LEDGER+user_id,2)#TWO_MONTHS)# their ledger expires after a while


def add_defender(own_id, target_id, time_of_adding, is_super):
	"""
	Adds a new defender

	Privileges:
	'0': Regular defender
	'1': Has the privilege to:
		i) edit/remove other defenders' banning actions 
		ii) access the global ledger
		iii) add/remove basic defenders
		iv) view top reporters
	"""
	if target_id:
		target_id = str(target_id)
		my_server = redis.Redis(connection_pool=POOL)
		my_server.zadd(DEFENDERS, target_id, time_of_adding)# this just records current defenders
		my_server.zadd(DEFENDERS_FOREVER,target_id,time_of_adding)#simply keeps a record of all defenders
		my_server.hmset(DEFENDER_DATA+target_id,{'dfid':target_id,'priv':'1' if is_super else '0','appointed_at':time_of_adding,'appointed_by':own_id})
		# remove any 'ttl' that might have existed on the defender's ledger (in case they were 're-added')
		ledger_key = DEFENDERS_LEDGER+target_id
		if my_server.exists(ledger_key):
			my_server.persist(ledger_key)
		# Even admins can't add defenders in quick fire. Rate limit them as a precaution!
		my_server.setex(DEFENDER_ADDITION_RATE_LIMITED+str(own_id),'1',TWENTY_MINS)


def is_rate_limited_from_adding_defender(own_id):
	"""
	Check if admin is able to add a defender
	"""
	if redis.Redis(connection_pool=POOL).ttl(DEFENDER_ADDITION_RATE_LIMITED+str(own_id)) > 2:
		return True
	else:
		return False


##################### Content banning temp data (while defender is filling the banning forms) ######################


def temporarily_save_content_details(obj_id, owner_id, photo_url, caption, obj_type, origin, owner_uname, link_id, banner_id, sin, target_id=None, \
	target_ids=None, voting_ban_dur=None):
	"""
	Temporarily saves target item and item poster credentials for processing a content_submission_and_voting ban
	"""
	data = {'obid':obj_id,'ooid':owner_id,'purl':photo_url,'cap':caption,'tp':obj_type,'orig':origin,'oun':owner_uname,'lid':link_id,\
		'bid':banner_id,'sin':sin}
	if target_id:
		data['tid'] = target_id
	elif target_ids:
		data['tids'] = target_ids
		data['vdur'] = voting_ban_dur
	else:
		return False
	redis.Redis(connection_pool=POOL).setex(CONTENT_BAN_TEMP_KEY+str(banner_id),json.dumps(data),ONE_HOUR)
	return True


def enrich_temporarily_saved_content_details_with_duration(banner_id, duration, return_credentials=False):
	"""
	Enriches a temporarily saved ban data key with 'duration'

	Applicable for 'bad_submission' type banning only. 'bad_voting' type banning is pre-enriched with 'dur' data
	"""
	saved_key = CONTENT_BAN_TEMP_KEY+str(banner_id)
	my_server = redis.Redis(connection_pool=POOL)
	data = my_server.get(saved_key)
	if data:
		data = json.loads(data)
		data['dur'] = duration
		my_server.setex(saved_key,json.dumps(data),TWENTY_MINS)
		if return_credentials:
			return True, data
		else:
			return True
	else:
		# data was never set, or has expired
		if return_credentials:
			return False, None
		else:
			return False

def retrieve_temporary_saved_content_details(banner_id):
	"""
	Retrieves and returns temporarily saved data useful when imposing a content ban
	"""
	data = redis.Redis(connection_pool=POOL).get(CONTENT_BAN_TEMP_KEY+str(banner_id))
	if data:
		return json.loads(data)
	else:
		return None

def delete_temporarily_saved_content_details(banner_id):
	"""
	Deletes temporarily saved content
	"""
	redis.Redis(connection_pool=POOL).delete(CONTENT_BAN_TEMP_KEY+str(banner_id))



##################### Content, mehfil and profile complaints by users ######################

def set_complaint(report_desc, rep_type, obj_id, obj_owner_id, obj_type, price_paid, reporter_id, time_now, feedback_text=None, img_caption=None, \
	obj_url=None, obj_txt=None, orig_obid=None,orig_url=None, orig_txt=None, mehfil_topic=None, mehfil_rules=None, mehfil_report_tp=None, \
	reported_item_ct=None, orig_item_ct=None):
	"""
	Enter a complaint in the list displayed to our defenders

	Handles both object type 'tx' and type 'img'
	If 'mf', save obj_id, obj_type, mehfil topic and rules
	If 'pf', save obj_id, obj_type, image_url and nickname
	If 'tx', save obj_id and obj_txt
	If 'img', save obj_id, img_caption and obj_url
	If special case of rep_type in ('9','10'), use orig_obid and orig_txt (for 'tx'), or orig_obid and orig_url (for 'img')
	Note: also creates a historical object of the complaint for viewing in a list
	"""
	reporter_id, obj_id = str(reporter_id), str(obj_id)
	my_server = redis.Redis(connection_pool=POOL)
	complaining_rate_limited = my_server.ttl(COMPLAINING_RATE_LIMITED+reporter_id)
	if complaining_rate_limited > 1:
		# reporter is rate limited from reporting
		return complaining_rate_limited
	else:
		# if user reported this object recently, disallow (we're pinging a sorted set that contains most recent 20 reports of a user)
		complaint_id = obj_type+":"+obj_id#turn this into payload for COMPLAINTS_SUBMITTED, and its current contents into a hash
		# reported_recently = my_server.zcount(COMPLAINTS_SUBMITTED+reporter_id,complaint_id,complaint_id)
		reported_recently = my_server.zscore(COMPLAINTS_SUBMITTED+reporter_id,complaint_id)
		if reported_recently:
			return '-1'
		else:
			# didn't report recently, proceed
			report = {'h':report_desc,'i':reporter_id,'rt':rep_type}
			if obj_type == 'mf':
				# public mehfil topic/rules complaint
				report["d"] = feedback_text
				report["categ"] = mehfil_report_tp
				mehfil_report, num_reports = COMPLAINT+complaint_id, 1
				if my_server.exists(mehfil_report):
					# appending to a pre-existing report
					existing_reports = json.loads(my_server.hget(mehfil_report,'pl'))
					existing_reports.append(report)
					my_server.hset(mehfil_report,'pl',json.dumps(existing_reports))
					num_reports = my_server.hincrby(mehfil_report,'n',amount=1)
				else:
					# new report
					new_payload = []
					new_payload.append(report)
					mapping = {'pl':json.dumps(new_payload),'obid':obj_id, 'ooid':obj_owner_id, 'n':num_reports,'tp':obj_type,'c':mehfil_topic,\
					'r':mehfil_rules,'ct':reported_item_ct}
					my_server.hmset(mehfil_report,mapping)
				
				# payables sorted set - contains all amounts owed to all reporter ids - recalled when complaint's fate is decided
				payables = PAYABLES+complaint_id
				prev_payable = my_server.zscore(payables,reporter_id)
				new_amnt_owed = (price_paid if prev_payable is None else prev_payable+int(price_paid))# in case a user has double reported a photo
				my_server.zadd(payables,reporter_id,new_amnt_owed)
				
				# sorted set containing all complaints (useful in defender view - 'cull list')
				pipeline1 = my_server.pipeline()
				pipeline1.zadd(COMPLAINT_LIST,mehfil_report,num_reports)
				pipeline1.setex(COMPLAINING_RATE_LIMITED,1,FOUR_MINS)# stop user from going on a reporting spree in quick succession

				# logging attempt and case description
				pipeline1.zadd(COMPLAINER_TIME_LIST,reporter_id,time_now)
				pipeline1.zincrby(COMPLAINER_ATTEMPT_SORTED_SET,reporter_id,amount=1)
				payload = {'ftx':feedback_text,'h':report_desc,'tp':obj_type,'obid':obj_id,'categ':mehfil_report_tp,'c':mehfil_topic,\
				'r':mehfil_rules,'t':time_now}
				# pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,json.dumps(payload),complaint_id) #logging reporter submissions (change: obj_id+":"+obj_type)
				pipeline1.set(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id,json.dumps(payload))
				pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,complaint_id,time_now)
				pipeline1.execute()

				# trimming the sorted set to latest 20, nothing more!
				to_delete = my_server.zrevrange(COMPLAINTS_SUBMITTED+reporter_id,20,-1)
				if to_delete:
					pipeline2 = my_server.pipeline()
					for complaint_id in to_delete:
						pipeline2.delete(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id)
					pipeline2.zrem(COMPLAINTS_SUBMITTED+reporter_id,*to_delete)
					pipeline2.execute()

				return None
			elif obj_type == 'pf':
				# profile complaint
				report["d"] = feedback_text
				report["categ"] = mehfil_report_tp
				profile_report, num_reports = COMPLAINT+complaint_id, 1
				if my_server.exists(profile_report):
					existing_reports = json.loads(my_server.hget(profile_report,'pl'))
					existing_reports.append(report)
					my_server.hset(profile_report,'pl',json.dumps(existing_reports))
					num_reports = my_server.hincrby(profile_report,'n',amount=1)
				else:
					new_payload = []
					new_payload.append(report)
					mapping = {'pl':json.dumps(new_payload),'obid':obj_id,'ooid':obj_owner_id,'nick':img_caption,'av_img':obj_url,'n':num_reports,\
					'tp':obj_type,'ct':reported_item_ct}
					my_server.hmset(profile_report,mapping)
				# payables sorted set - contains all amounts owed to all reporter ids - recalled when content's fate is decided
				payables = PAYABLES+complaint_id
				prev_payable = my_server.zscore(payables,reporter_id)
				new_amnt_owed = (price_paid if prev_payable is None else prev_payable+int(price_paid))# in case a user has double reported a photo
				my_server.zadd(payables,reporter_id,new_amnt_owed)

				#sorted set containing all reported content (useful in defender view)
				pipeline1 = my_server.pipeline()
				pipeline1.zadd(COMPLAINT_LIST,profile_report,num_reports)
				pipeline1.setex(COMPLAINING_RATE_LIMITED,1,FOUR_MINS)# stop user from going on a reporting spree in quick succession

				# logging attempt and case description
				pipeline1.zadd(COMPLAINER_TIME_LIST,reporter_id,time_now)
				pipeline1.zincrby(COMPLAINER_ATTEMPT_SORTED_SET,reporter_id,amount=1)
				payload = {'ftx':feedback_text,'h':report_desc,'tp':obj_type,'obid':obj_id,'categ':mehfil_report_tp,'purl':obj_url,\
				'nick':img_caption,'t':time_now}
				# pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,json.dumps(payload),complaint_id) #logging reporter submissions (change: obj_id+":"+obj_type)
				pipeline1.set(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id,json.dumps(payload))
				pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,complaint_id,time_now)
				pipeline1.execute()

				#trimming the sorted set to latest 20, nothing more!
				to_delete = my_server.zrevrange(COMPLAINTS_SUBMITTED+reporter_id,20,-1)
				if to_delete:
					pipeline2 = my_server.pipeline()
					for complaint_id in to_delete:
						pipeline2.delete(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id)
					pipeline2.zrem(COMPLAINTS_SUBMITTED+reporter_id,*to_delete)
					pipeline2.execute()

				return None
			elif obj_type == 'img':
				# public image complaint
				if rep_type in ('9','10'):# (change: differentiate between rep_type AND obj_type)
					# this is a report regarding duplicate content
					report["oobid"] = orig_obid
					report["ourl"] = orig_url
				else:
					# essentially not adding feedback_text when duplicate items are being reported (i.e. rep_type in ('9','10')) because we don't need explanatory text then
					report["d"] = feedback_text
				public_image_report, num_reports = COMPLAINT+complaint_id, 1
				if my_server.exists(public_image_report):
					existing_reports = json.loads(my_server.hget(public_image_report,'pl'))
					existing_reports.append(report)
					my_server.hset(public_image_report,'pl',json.dumps(existing_reports))
					num_reports = my_server.hincrby(public_image_report,'n',amount=1)
				else:
					new_payload = []
					new_payload.append(report)
					mapping = {'pl':json.dumps(new_payload),'obid':obj_id,'ooid':obj_owner_id,'c':img_caption,'url':obj_url,'n':num_reports,\
					'tp':obj_type,'ct':reported_item_ct}
					if rep_type in ('9','10'):
						mapping['oict'] = orig_item_ct
					my_server.hmset(public_image_report,mapping)
				# payables sorted set - contains all amounts owed to all reporter ids - recalled when content's fate is decided
				payables = PAYABLES+complaint_id
				prev_payable = my_server.zscore(payables,reporter_id)
				new_amnt_owed = (price_paid if prev_payable is None else prev_payable+int(price_paid))# in case a user has double reported a photo
				my_server.zadd(payables,reporter_id,new_amnt_owed)
				
				#sorted set containing all reported content (useful in defender view)
				pipeline1 = my_server.pipeline()
				pipeline1.zadd(COMPLAINT_LIST,public_image_report,num_reports)
				pipeline1.setex(COMPLAINING_RATE_LIMITED,1,FOUR_MINS)# stop user from going on a reporting spree in quick succession

				# logging attempt and case description
				pipeline1.zadd(COMPLAINER_TIME_LIST,reporter_id,time_now)
				pipeline1.zincrby(COMPLAINER_ATTEMPT_SORTED_SET,reporter_id,amount=1)
				payload = {'ftx':feedback_text,'h':report_desc,'tp':obj_type,'obid':obj_id,'purl':obj_url,'t':time_now}
				# pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,json.dumps(payload),complaint_id) #logging reporter submissions (change: obj_id+":"+obj_type)
				pipeline1.set(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id,json.dumps(payload))
				pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,complaint_id,time_now)
				pipeline1.execute()

				#trimming the sorted set to latest 20, nothing more!
				to_delete = my_server.zrevrange(COMPLAINTS_SUBMITTED+reporter_id,20,-1)
				if to_delete:
					pipeline2 = my_server.pipeline()
					for complaint_id in to_delete:
						pipeline2.delete(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id)
					pipeline2.zrem(COMPLAINTS_SUBMITTED+reporter_id,*to_delete)
					pipeline2.execute()

				return None
			elif obj_type == 'tx':
				# public text complaint
				if rep_type in ('9','10'):
					# this is a report regarding duplicate content
					report["oobid"] = orig_obid
					report["otxt"] = orig_txt
				else:
					# essentially not adding feedback_text when duplicate items are being reported (i.e. rep_type in ('9','10')) because we don't need explanatory text then
					report["d"] = feedback_text
				public_text_report, num_reports = COMPLAINT+complaint_id, 1
				if my_server.exists(public_text_report):
					existing_reports = json.loads(my_server.hget(public_text_report,'pl'))
					existing_reports.append(report)
					my_server.hset(public_text_report,'pl',json.dumps(existing_reports))
					num_reports = my_server.hincrby(public_text_report,'n',amount=1)
				else:
					new_payload = []
					new_payload.append(report)
					mapping = {'pl':json.dumps(new_payload),'obid':obj_id,'ooid':obj_owner_id,'c':obj_txt,'n':num_reports,'tp':obj_type,'ct':reported_item_ct}
					if rep_type in ('9','10'):
						mapping['oict'] = orig_item_ct
					my_server.hmset(public_text_report,mapping)
				# payables sorted set - contains all amounts owed to all reporter ids - recalled when content's fate is decided
				payables = PAYABLES+complaint_id
				prev_payable = my_server.zscore(payables,reporter_id)
				new_amnt_owed = (price_paid if prev_payable is None else prev_payable+int(price_paid))# in case a user has double reported a photo
				my_server.zadd(payables,reporter_id,new_amnt_owed)
				
				#sorted set containing all reported content (useful in defender view)
				pipeline1 = my_server.pipeline()
				pipeline1.zadd(COMPLAINT_LIST,public_text_report,num_reports)
				pipeline1.setex(COMPLAINING_RATE_LIMITED,1,FOUR_MINS)# stop user from going on a reporting spree in quick succession

				# logging attempt and case description
				pipeline1.zadd(COMPLAINER_TIME_LIST,reporter_id,time_now)
				pipeline1.zincrby(COMPLAINER_ATTEMPT_SORTED_SET,reporter_id,amount=1)
				payload = {'ftx':feedback_text,'h':report_desc,'tp':obj_type,'obid':obj_id,'c':obj_txt,'t':time_now}
				# pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,json.dumps(payload),complaint_id) #logging reporter submissions (change: obj_id+":"+obj_type)
				pipeline1.set(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id,json.dumps(payload))
				pipeline1.zadd(COMPLAINTS_SUBMITTED+reporter_id,complaint_id,time_now)
				pipeline1.execute()

				#trimming the sorted set to latest 20, nothing more!
				to_delete = my_server.zrevrange(COMPLAINTS_SUBMITTED+reporter_id,20,-1)
				if to_delete:
					pipeline2 = my_server.pipeline()
					for complaint_id in to_delete:
						pipeline2.delete(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id)
					pipeline2.zrem(COMPLAINTS_SUBMITTED+reporter_id,*to_delete)
					pipeline2.execute()
					
				return None
			else:
				# not entertaining any other reports currently
				return None


def get_complainer_ids(obj_id, obj_type, my_server=None):
	"""
	Returns IDs of all complainers of a certain object or content

	obj_type is either 'tx', 'img', 'pf' or 'mf'
	"""
	if not obj_id:
		return []
	else:
		my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
		indiv_complaints = json.loads(my_server.hget(COMPLAINT+obj_type+":"+str(obj_id),'pl'))#list of dictionaries
		complainer_ids = []
		for complaint in indiv_complaints:
			complainer_ids.append(str(complaint["i"]))
		return complainer_ids


def get_payables(reporter_ids,obj_id,obj_type):
	"""
	Return (id,payable) tuple list for ids.

	These are payable points for complainers of content or objects
	"""
	all_payables, selected_payables = redis.Redis(connection_pool=POOL).zrange(PAYABLES+obj_type+":"+obj_id,0,-1,withscores=True), []
	if all_payables:
		for reporter_id, payable_score in all_payables:
			if reporter_id in reporter_ids:
				selected_payables.append((reporter_id,payable_score))
	return selected_payables


def complaint_exists(obj_id, obj_type):
	"""
	Checking to see if an item was already reported

	We allow users to report already reported items
	But we let defenders know in case they themselves try to report an item
	We also let them know if they try to handle an already-handled case
	"""
	return redis.Redis(connection_pool=POOL).exists(COMPLAINT+obj_type+":"+obj_id)


def retrieve_top_complainer_reputation():
	"""
	Shows global list of top complaint reporting IDs (by reputation)
	"""
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(TOP_50_CACHED_DATA)
	if cached_data:
		return json.loads(cached_data)
	else:
		top_50_with_scores = my_server.zrevrange(COMPLAINER_CORRECT_SORTED_SET,0,49,withscores=True)#top 50, with number of correct reports
		top_50_dict = {}
		for reporter_id, num_correct in top_50_with_scores:
			top_50_dict[reporter_id] = num_correct
		only_ids = [i[0] for i in top_50_with_scores]
		pipeline1 = my_server.pipeline()
		for reporter_id in only_ids:
			pipeline1.zscore(COMPLAINER_ATTEMPT_SORTED_SET,reporter_id)
		result1, counter = pipeline1.execute(), 0
		top_50 = []
		for reporter_id in only_ids:
			top_50.append((reporter_id,top_50_dict[reporter_id],result1[counter]))
			counter += 1
		num_correct = my_server.zcard(COMPLAINER_CORRECT_SORTED_SET)# total correct
		my_server.setex(TOP_50_CACHED_DATA,json.dumps([top_50, num_correct]),TWENTY_MINS)
		return (top_50, num_correct)


def cleanse_inactive_complainers():
	"""
	Scrub complainers who haven't complained (i.e. reported content) for over two months (reasoning: they probably don't show up any more)

	The reasoning is that they've probably dropped out, and no longer should be in the "top reporters" lists, nor do we need their case histories, etc.
	This is a scheduled task and runs every 3 days
	"""
	epoch_time_two_months_ago = time.time() - TWO_MONTHS
	my_server = redis.Redis(connection_pool=POOL)
	inactive_complainer_ids = my_server.zrangebyscore(COMPLAINER_TIME_LIST,'-inf','('+str(epoch_time_two_months_ago))

	if inactive_complainer_ids:
		inactive_complainer_ids = set(inactive_complainer_ids)
		# only consider those inactive_complainer_ids whose complaints do NOT exist CURRENTLY in cull-list
		all_current_complaint_objs = my_server.zrange(COMPLAINT_LIST,0,-1)
		for complaint_obj in all_current_complaint_objs:
			data = complaint_obj.split(":")
			obj_type, obj_id = data[1], data[2]
			current_complainer_ids = get_complainer_ids(obj_id, obj_type, my_server)
			if current_complainer_ids:
				for complainer_id in current_complainer_ids:
					inactive_complainer_ids.discard(complainer_id)

		if inactive_complainer_ids:
			# only proceed if inactive_complainers are not present in the current cull-list
			inactive_complainer_ids = list(inactive_complainer_ids)
			pipeline1 = my_server.pipeline()
			#removing from 'attempts' list and set
			pipeline1.zrem(COMPLAINER_TIME_LIST,*inactive_complainer_ids)
			pipeline1.zrem(COMPLAINER_ATTEMPT_SORTED_SET,*inactive_complainer_ids)
			#removing from 'correct' list and set
			pipeline1.zrem(COMPLAINER_CORRECT_TIME_LIST,*inactive_complainer_ids)
			pipeline1.zrem(COMPLAINER_CORRECT_SORTED_SET,*inactive_complainer_ids)
			pipeline1.execute()

			for complainer_id in inactive_complainer_ids:
				# removing 'case files' that are shown to defenders in top 50 reporters view, etc. (retrieve_top_complainer_reputation() for example)
				all_hist_objs = my_server.zrange(COMPLAINTS_SUBMITTED+complainer_id,0,-1)
				pipeline2 = my_server.pipeline()
				for complaint_id in all_hist_objs:
					pipeline2.delete(COMPLAINT_HIST_OBJ+complainer_id+":"+complaint_id)
				pipeline2.delete(COMPLAINTS_SUBMITTED+complainer_id)
				pipeline2.execute()
	my_server.delete(TOP_50_CACHED_DATA)



def log_case_and_incr_reputation(correct_reporter_ids,incorrect_reporter_ids, malicious_reporter_ids, time_now, obj_id, defender_id, defender_uname,\
	obj_type):
	"""
	Logging report 'attempts' and successful outcomes, so that a % success rate (per reporter) can be computed later

	This is called whenever a defender 'decides' a case (from the cull-list)
	It also logs cases raised by each reporter separately
	
	Reporter reputation is calculated thusly:
		Correct reports get +1 (incorrect or malicious reports both don't merit a positive score)
		Incorrect reports get 0 (incorrect and malicious are highly subjective, hence don't give malicious -1)
		Malicious reports get 0
	"""
	complaint_id = obj_type+":"+obj_id
	my_server = redis.Redis(connection_pool=POOL)
	# Retrieving report object and enriching objects according to decision
	report_data = my_server.hget(COMPLAINT+complaint_id,'pl')# 'pl' is the payload - a JSON string (list of dictionaries) containing all reports
	if report_data:
		for report in json.loads(report_data):
			reporter_id = str(report['i'])#int format originally, converted to string
			
			complaint_obj_key = COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_id
			complaint_obj = my_server.get(complaint_obj_key)#we disallow users from reporting something that already exists in this list, so only 1 such item would be present - hence [0] is what we needed
			complaint_obj = json.loads(complaint_obj) if complaint_obj else complaint_obj
			
			if reporter_id in correct_reporter_ids:
				# marking the reporter's complaint object
				complaint_obj['o'] = '1'
			elif reporter_id in incorrect_reporter_ids:
				# marking the reporter's complaint object
				complaint_obj['o'] = '0'
			elif reporter_id in malicious_reporter_ids:
				# marking the reporter's complaint object
				complaint_obj['o'] = '-1'

			# set 'decided by' credentials
			complaint_obj['dun'] = defender_uname
			complaint_obj['did'] = defender_id
			my_server.set(complaint_obj_key,json.dumps(complaint_obj))# and then re-save the enriched complaint_obj

		pipeline1 = my_server.pipeline()
		for reporter_id in correct_reporter_ids:
			# logging good outcome - that's the only one which merits a +1 score (all others are zero)
			pipeline1.zadd(COMPLAINER_CORRECT_TIME_LIST,reporter_id,time_now)# sorted by latest complaint logged
			pipeline1.zincrby(COMPLAINER_CORRECT_SORTED_SET,reporter_id,amount=1)# sorted by score
		pipeline1.execute()


def get_complainer_case_history(reporter_id):
	"""
	Retrieves reports logged by reporters (along with whether they were correct, incorrect or malicious)

	Sorted by time - most recent first
	"""
	reporter_id = str(reporter_id)
	my_server = redis.Redis(connection_pool=POOL)
	complaint_obj_postfixes = my_server.zrevrange(COMPLAINTS_SUBMITTED+reporter_id,0,-1)
	complaint_obj_keys = []
	for complaint_obj_postfix in complaint_obj_postfixes:
		complaint_obj_keys.append(COMPLAINT_HIST_OBJ+reporter_id+":"+complaint_obj_postfix)
	complaint_objs = my_server.mget(*complaint_obj_keys)
	# retrieved complaint_objs are sorted by time (which is what we need)
	all_cases = []
	for case in complaint_objs:
		all_cases.append(json.loads(case))
	return all_cases
	# # return list sorted by time
	# sorted_cases = sorted(all_cases, key=lambda k: int(k['t']), reverse=True) 
	# return sorted_cases


def delete_complaint(obj_id, defender_id, obj_type):
	"""
	Wrapping up a complaint on an object (removing it from the cull-list)

	Logs defender_id against a report
	Content type is 'img', 'tx', 'pf' or 'mf'
	"""
	obj_id = str(obj_id)
	complaint = COMPLAINT+obj_type+":"+obj_id
	my_server = redis.Redis(connection_pool=POOL)
	# delete the complaint and update relevant defender's stats
	pipeline1 = my_server.pipeline()
	pipeline1.delete(PAYABLES+obj_type+":"+obj_id) #deleting the payables sorted set
	pipeline1.delete(complaint) #deleting the complaint hash
	pipeline1.zrem(COMPLAINT_LIST,complaint) #removing the complaint from the sorted set of 'all complaint'
	pipeline1.execute()
	sin = None
	if obj_type in ('img','tx'):
		sin = 'bad_submission'
	elif obj_type == 'pf':
		sin = 'bad_profile'# i.e. bad profile pic or bad nickname
	elif obj_type == 'mf':
		sin = 'bad_mehfil'# i.e bad topic or rules
	increment_defender_case_file(defender_id,sin,my_server)


def rate_limit_complainer(reporter_ids, my_server=None):
	"""
	If a reporter's report was done in jest (or maliciously), rate limit their reporting for many days
	"""
	if reporter_ids:
		my_server = my_server if my_server else redis.Redis(connection_pool=POOL)
		if len(reporter_ids) > 5:
			pipeline1 = my_server.pipeline()
			for reporter_id in reporter_ids:
				pipeline1.setex(COMPLAINING_RATE_LIMITED+reporter_id,'1',ONE_WEEK)
			pipeline1.execute()
		else:
			for reporter_id in reporter_ids:
				my_server.setex(COMPLAINING_RATE_LIMITED+reporter_id,'1',ONE_WEEK)


def get_content_complaints():
	"""
	Returns all current photo reports' hash names
	"""
	# Sorted by number of complaints
	return redis.Redis(connection_pool=POOL).zrevrange(COMPLAINT_LIST,0,-1)


def get_complaint_details(complaint_list):
	"""
	Given a hash_name for a content complaint, this can retrieve all the data related to that.

	Complaint hashes must be fed in list format
	"""
	my_server = redis.Redis(connection_pool=POOL)
	pipeline1 = my_server.pipeline()
	complaints_with_details = []
	for complaint in complaint_list:
		pipeline1.hgetall(complaint)
	result1 = pipeline1.execute()
	for complaint in result1:
		complaint["pl"] = json.loads(complaint["pl"])
		complaints_with_details.append(complaint)
	return complaints_with_details


def get_num_complaints():
	"""
	Retrieves num of outstanding reports for the attention of mods
	"""
	return redis.Redis(connection_pool=POOL).zcard(COMPLAINT_LIST)