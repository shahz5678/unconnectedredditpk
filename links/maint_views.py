import random, itertools
from verified import FEMALES
from operator import itemgetter
from datetime import datetime, timedelta
from user_sessions.models import Session
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from models import Link, Photo, PhotoComment, UserProfile, Publicreply, UserFan, ChatPic
from redis7 import get_inactives, set_inactives, get_inactive_count, create_inactives_copy, delete_inactives_copy, bulk_sanitize_group_invite_and_membership
from redis3 import insert_nick_list, get_nick_likeness, skip_outage, retrieve_all_mobile_numbers, retrieve_numbers_with_country_codes, remove_verified_mob
from redis4 import save_deprecated_photo_ids_and_filenames, invalidated_cached_uname_credentials#, report_rate_limited_conversation
from redis2 import bulk_sanitize_notifications

######################################## Notifications ########################################

@csrf_protect
def skip_outage_notif(request, *args, **kwargs):
	if request.method == "POST":
		which_user = request.POST.get("skip",None)
		origin = request.POST.get("orig",'1')
		if which_user is not None:
			skip_outage(which_user)
		if origin == '1':
				return redirect("home")
		elif origin == '2':
			return redirect("best_photo")
		elif origin == '0':
			return redirect("photo")
		else:
			return redirect("home")
	else:
		return redirect("home")


def damadam_cleanup(request, *args, **kwargs):
	context = {'referrer':request.META.get('HTTP_REFERER',None)}
	return render(request,"damadam_cleanup.html",context)

######################################## Username Sanitzation ########################################


def change_nick(target_id,new_nick):
	"""
	Change nickname of target_id to 'new_nick'
	"""
	User.objects.filter(id=target_id).update(username=new_nick)


@csrf_protect
def change_nicks(request,*args,**kwargs):
	"""This frees up the name space of nicks, 100K at a time.

	Nicks, once taken, are locked out of the namespace.
	This changes nicknames that aren't in use anymore to a random string.
	It also removes their mobile verification and cached uname entries (if they exist)
	"""
	if request.user.username == 'mhb11':
		if request.method == "POST":
			decision = request.POST.get("dec",None)
			count = int(request.POST.get("count",None))
			if decision == 'No':
				return redirect("home")
			elif decision == 'Yes':
				inactives, last_batch = get_inactives(get_10K=True)
				id_list = map(itemgetter(1), inactives) #list of ids to deprecate
				id_len = len(id_list)
				start = count*100000
				end = start+100000-1
				sample_size = id_len+10# ensure sample_size is lesser than (start-end)
				rand_nums = map(str,random.sample(xrange(start,end),sample_size))#strinigied random nums
				invalidated_cached_uname_credentials(user_ids=id_list)# invalidating uname caches in bulk
				counter = 0
				for pk in id_list:
					# change 'inactive-' (and can't keep 'i_i__') next time this is run; otherwise there will be collisions
					change_nick(target_id=pk, new_nick='d_m_d_'+rand_nums[counter])
					counter += 1
				remove_verified_mob(target_user_ids=id_list)# unverifying users in bulk
				if last_batch:
					return render(request,'deprecate_nicks.html',{})
				else:
					return render(request,'change_nicks.html',{'count':count+1,'nicks_remaining':get_inactive_count()})
			else:
				return redirect("home")
		else:
			return render(request,'change_nicks.html',{'count':1,'nicks_remaining':get_inactive_count()})
	else:
		return redirect("home")


def export_nicks(request,*args,**kwargs):
	"""Exports deprecated nicks in a CSV.

	This writes all nicks, scores and ids into a CSV.
	The CSV is then exported.
	"""
	if request.user.username == 'mhb11':
		inactives = get_inactives()
		import csv
		with open('inactives.csv','wb') as f:
			wtr = csv.writer(f, delimiter=',')
			columns = "username score id".split()
			wtr.writerow(columns)
			for inactive in inactives:
				tup = inactive[0].split(":")
				username = tup[0]
				try:
					score = tup[1]
				except:
					score = None
				id_ = inactive[1]
				to_write = [username, score, id_]
				wtr.writerows([to_write])
		return render(request,'deprecate_nicks.html',{})
	else:
		return render(request,'404.html',{})

def deprecate_nicks(request,*args,**kwargs):
	"""This singles out user_ids and nicks that haven't been in use over the past 3 months.
	It looks at criteria such as last messaging time and a ton of other things.
	It ensures pink stars are not included in the list.
	Only 'mhb11' can run this function.
	"""
	if request.user.username == 'mhb11':

		import redis
		from location import REDLOC1
		POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC1, db=0)
		my_server = redis.Redis(connection_pool=POOL)
		
		# populate required sorted_set in redis 7 (called 'inactive_users')
		inactives = []
		all_inactives = set(my_server.lrange("all_inactives",0,-1))
		inactives_data = User.objects.only('username','id','userprofile__score').filter(id__in=all_inactives).values_list('username','id','userprofile__score')
		for inact in inactives_data:
			inactives.append((inact[0]+":"+str(inact[2]),inact[1]))#creating a list of tuples
		print "step 17 calculated"
		
		size = len(inactives)
		child1 = inactives[:size/8]
		child2 = inactives[size/8:size/4]
		child3 = inactives[size/4:(size*3)/8]
		child4 = inactives[(size*3)/8:size/2]
		child5 = inactives[size/2:(size*5)/8]
		child6 = inactives[(size*5)/8:(size*6)/8]
		child7 = inactives[(size*6)/8:(size*7)/8]
		child8 = inactives[(size*7)/8:]
		print "step 18 calculated"
		
		from itertools import chain    
		# breaking it into 8 lists avoids socket time out
		set_inactives([x for x in chain.from_iterable(child1)])
		set_inactives([x for x in chain.from_iterable(child2)])
		set_inactives([x for x in chain.from_iterable(child3)])
		set_inactives([x for x in chain.from_iterable(child4)])
		set_inactives([x for x in chain.from_iterable(child5)])
		set_inactives([x for x in chain.from_iterable(child6)])
		set_inactives([x for x in chain.from_iterable(child7)])
		set_inactives([x for x in chain.from_iterable(child8)])
		print "step 19 calculated\n"
		print "we are done!"
		return render(request,'deprecate_nicks.html',{})
	else:
		return render(request,'404.html',{})


# def deprecate_nicks(request,*args,**kwargs):
#     """This singles out user_ids and nicks that haven't been in use over the past 3 months.
#     It looks at criteria such as last messaging time and a ton of other things.
#     It ensures pink stars are not included in the list.
#     Only 'mhb11' can run this function.
#     """
#     if request.user.username == 'mhb11':

#         import redis
#         from location import REDLOC1
#         ONE_DAY = 60*60*24
#         ONE_WEEK = 60*60*24*7
#         POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC1, db=0)
#         my_server = redis.Redis(connection_pool=POOL)

#         six_months_ago = datetime.utcnow()-timedelta(days=180)#240
		
#         if my_server.exists("active_users"):
#             print "step 14 from cache"
#             active_users = my_server.lrange("active_users",0,-1)
#             print "by passing steps 1-13\n"

#         else:

#             # uploaded a photo recently
#             if my_server.exists("photo_uploaders"):
#                 current_photo_uploaders = my_server.lrange("photo_uploaders",0,-1)
#                 print "step 7 from cache"
#             else:
#                 current_photo_uploaders = set(Photo.objects.filter(upload_time__gte=six_months_ago).values_list('owner_id',flat=True))
#                 current_photo_uploaders = map(str, current_photo_uploaders)
#                 print "step 7 calculated"
#                 my_server.lpush("photo_uploaders",*current_photo_uploaders)
#                 my_server.expire("photo_uploaders",ONE_WEEK)
#                 print "... saved in redis\n"

			
#             # fanned someone recently
#             if my_server.exists("fanners"):
#                 current_fanners = my_server.lrange("fanners",0,-1)
#                 print "step 9 from cache"
#             else:
#                 current_fanners = set(UserFan.objects.filter(fanning_time__gte=six_months_ago).values_list('fan_id',flat=True))
#                 current_fanners = map(str, current_fanners)
#                 print "step 9 calculated"
#                 my_server.lpush("fanners",*current_fanners)
#                 my_server.expire("fanners",ONE_WEEK)
#                 print "... saved in redis\n"
			
			
#             # score is above 500
#             if my_server.exists("high_score_users"):
#                 more_than_500 = my_server.lrange("high_score_users",0,-1)
#                 print "step 10 from cache"
#             else:
#                 more_than_500 = set(UserProfile.objects.filter(score__gte=600).values_list('user_id',flat=True))
#                 more_than_500 = map(str, more_than_500)
#                 print "step 10 calculated"
#                 my_server.lpush("high_score_users",*more_than_500)
#                 my_server.expire("high_score_users",ONE_WEEK)
#                 print "... saved in redis\n"


#             # is a pink stars
#             if my_server.exists("pink_stars"):
#                 pink_stars = my_server.lrange("pink_stars",0,-1)
#                 print "step 11 from cache"
#             else:
#                 pink_stars = set(User.objects.filter(username__in=FEMALES).values_list('id',flat=True))
#                 pink_stars = map(str, pink_stars)
#                 print "step 11 calculated"
#                 my_server.lpush("pink_stars",*pink_stars)
#                 my_server.expire("pink_stars",ONE_WEEK)
#                 print "... saved in redis\n"



#             # submitted a publicreply recently
#             random_six_months_old_publicreply = 129806681#<- 2nd aug 2018#115706681
#             if my_server.exists("public_repliers"):
#                 current_public_repliers = my_server.lrange("public_repliers",0,-1)
#                 print "step 4 from cache"
#             else:
#                 current_public_repliers = set(Publicreply.objects.filter(id__gte=random_six_months_old_publicreply).values_list('submitted_by_id',flat=True))
#                 print "step 4a calculated"
#                 current_public_repliers = map(str, current_public_repliers)
#                 print "step 4b calculated"
#                 my_server.lpush("public_repliers",*current_public_repliers)
#                 my_server.expire("public_repliers",ONE_WEEK)
#                 print "... saved in redis\n"

			
#             # sent a photocomment recently
#             if my_server.exists("photo_commenters"):
#                 current_photo_commenters = my_server.lrange("photo_commenters",0,-1)
#                 print "step 5 from cache"
#             else:
#                 random_six_months_old_photocomment = 60750000#<- 2nd aug 2018#53000000
#                 current_photo_commenters = set(PhotoComment.objects.filter(id__gte=random_six_months_old_photocomment).values_list('submitted_by_id',flat=True))
#                 print "step 5a calculated"
#                 current_photo_commenters = map(str, current_photo_commenters)
#                 print "step 5b calculated"
#                 my_server.lpush("photo_commenters",*current_photo_commenters)
#                 my_server.expire("photo_commenters",ONE_WEEK)
#                 print "... saved in redis\n"


#             # all user ids who last logged in less than 6 months ago
#             if my_server.exists("latest_logins"):
#                 latest_logins = my_server.lrange("latest_logins",0,-1)
#                 print "step 1 from cache"
#             else:
#                 latest_logins = list(set(User.objects.filter(last_login__gte=six_months_ago).values_list('id',flat=True)))
#                 latest_logins = map(str, latest_logins)
#                 print "step 1 calculated"
#                 my_server.lpush("latest_logins",*latest_logins)
#                 my_server.expire("latest_logins",ONE_WEEK)
#                 print "... saved in redis\n"

			
#             # latest user ids found in Sessions
#             if my_server.exists("current_sessions"):
#                 current_sessions = my_server.lrange("current_sessions",0,-1)
#                 print "step 2 from cache"
#             else:
#                 current_sessions = set(Session.objects.filter(user__isnull=False,last_activity__gte=six_months_ago).values_list('user_id',flat=True))
#                 current_sessions = map(str, current_sessions)
#                 print "step 2 calculated"
#                 my_server.lpush("current_sessions",*current_sessions)
#                 my_server.expire("current_sessions",ONE_WEEK)
#                 print "... saved in redis\n"


#             # messaged on home recently
#             if my_server.exists("home_messegers"):
#                 current_home_messegers = my_server.lrange("home_messegers",0,-1)
#                 print "step 3 from cache"
#             else:
#                 current_home_messegers = set(Link.objects.filter(submitted_on__gte=six_months_ago).values_list('submitter_id',flat=True))
#                 current_home_messegers = map(str, current_home_messegers)
#                 print "step 3 calculated"
#                 my_server.lpush("home_messegers",*current_home_messegers)
#                 my_server.expire("home_messegers",ONE_WEEK)
#                 print "... saved in redis\n"


#             # created an account recently
#             if my_server.exists("recent_account_creators"):
#                 recent_account_creators = my_server.lrange("recent_account_creators",0,-1)
#                 print "step 6 from cache"
#             else:
#                 recent_account_creators = set(User.objects.filter(date_joined__gte=six_months_ago).values_list('id',flat=True))
#                 recent_account_creators = map(str, recent_account_creators)
#                 print "step 6 calculated"
#                 my_server.lpush("recent_account_creators",*recent_account_creators)
#                 my_server.expire("recent_account_creators",ONE_WEEK)
#                 print "... saved in redis\n"
			

#                 # has at least 1 private chat
#                 # TODO: 1_on_1_chatted = 
#                 # last ran 10th Sept 2018

#             # create a list of the data
#             sets = [set(current_public_repliers),set(current_photo_commenters),set(latest_logins),set(current_sessions),set(current_home_messegers),\
#             set(current_photo_uploaders),set(current_fanners),set(more_than_500),set(pink_stars),set(recent_account_creators)]#, 1_on_1_chatted]
#             print "step 12 calculated"

#             # the union of all of the above gives us users that have been at least remotely active in the last 4 months
#             active_users = set.union(*sets)

#             print "step 13 calculated"
#             my_server.lpush("active_users",*active_users)
#             my_server.expire("active_users",ONE_WEEK)
#             print "... saved in redis\n"
		
#         # all user ids
#         all_users = list(User.objects.all().values_list('id',flat=True))
#         all_users = map(str, all_users)
#         print "step 15 calculated"

#         # all inactives are simply all users minus all active users
#         all_inactives = set(all_users) - set(active_users)
#         print "step 16 calculated"

#         all_inactives = list(all_inactives)
#         llen = len(all_inactives)
#         list1 = all_inactives[:llen/2]
#         list2 = all_inactives[llen/2:]
#         my_server.lpush("all_inactives",*list1)
#         my_server.lpush("all_inactives",*list2)
#         my_server.expire("all_inactives",ONE_WEEK)
#         print "... saved in redis\n"

		

#         # populate required sorted_set in redis 1 (called 'inactive_users')
#         inactives = []
#         inactives_data = User.objects.only('username','id','userprofile__score').filter(id__in=all_inactives).values_list('username','id','userprofile__score')
#         for inact in inactives_data:
#             inactives.append((inact[0]+":"+str(inact[2]),inact[1]))#creating a list of tuples
#         print "step 17 calculated"
		
#         # inactives = list(all_inactives)
#         size = len(inactives)
#         child1 = inactives[:size/8]
#         child2 = inactives[size/8:size/4]
#         child3 = inactives[size/4:(size*3)/8]
#         child4 = inactives[(size*3)/8:size/2]
#         child5 = inactives[size/2:(size*5)/8]
#         child6 = inactives[(size*5)/8:(size*6)/8]
#         child7 = inactives[(size*6)/8:(size*7)/8]
#         child8 = inactives[(size*7)/8:]
#         print "step 18 calculated"
		
#         from itertools import chain    
#         # breaking it into 8 lists avoids socket time out
#         set_inactives([x for x in chain.from_iterable(child1)])
#         set_inactives([x for x in chain.from_iterable(child2)])
#         set_inactives([x for x in chain.from_iterable(child3)])
#         set_inactives([x for x in chain.from_iterable(child4)])
#         set_inactives([x for x in chain.from_iterable(child5)])
#         set_inactives([x for x in chain.from_iterable(child6)])
#         set_inactives([x for x in chain.from_iterable(child7)])
#         set_inactives([x for x in chain.from_iterable(child8)])
#         print "step 19 calculated\n"
#         print "we are done!"
#         return render(request,'deprecate_nicks.html',{})
#     else:
#         return render(request,'404.html',{})


def insert_nicks(request,*args,**kwargs):
	"""Inserts nicks in a redis sorted set (for quick validation at the time of sign up)

	All nicknames are first retrieved from the database.
	They are then inserted, chunk-wise, into the redis sorted set.
	It's a standalone function. One only needs to block new signups before running this.
	"""
	if request.user.username == 'mhb11':
		nicknames = User.objects.values_list('username',flat=True)
		list_len = len(nicknames)
		each_slice = int(list_len/10)
		counter = 0
		slices = []
		while counter < list_len:
			slices.append((counter,counter+each_slice))
			counter += each_slice
		for sublist in slices:
			insert_nick_list(nicknames[sublist[0]:sublist[1]])
		return render(request,'nicks_populated.html',{})
	else:
		return render(request,'404.html',{})



######################################## Redis Sanitzation ########################################

@csrf_protect
def remove_inactives_notification_activity(request,*args,**kwargs):
	"""Sanitize all notification activity of inactive users from redis2.

	We will be removing the following for each inactive user:
	1) sn:<user_id> --- a sorted set containing home screen 'single notifications',
	2) ua:<user_id> --- a sorted set containing notifications for 'matka',
	3) uar:<user_id> --- a sorted set containing resorted notifications,
	4) np:<user_id>:*:* --- all notification objects associated to the user,
	5) o:*:* --- any objects that remain with 0 subscribers,
	We will do everything in chunks of 10K, so that no server timeouts are encountered.
	"""
	if request.user.username == 'ZippoLighter':
		if request.method == "POST":
			decision = request.POST.get("dec",None)
			if decision == 'No':
				delete_inactives_copy()
				return redirect("home")
			elif decision == 'Yes':
				inactives, last_batch = get_inactives(get_5K=True, key="copy_of_inactive_users")
				id_list = map(itemgetter(1), inactives) #list of user ids
				notification_hash_deleted, sorted_sets_deleted, object_hash_deleted = bulk_sanitize_notifications(id_list)
				if last_batch:
					# delete_inactives_copy(delete_orig=True)
					delete_inactives_copy()
				return render(request,'sanitize_inactives_activity.html',{'inactives_remaining':get_inactive_count(key_name="copy_of_inactive_users"),\
					'last_batch':last_batch,'notif_deleted':notification_hash_deleted,'sorted_sets_deleted':sorted_sets_deleted,\
					'objs_deleted':object_hash_deleted})
		else:
			return render(request,'sanitize_inactives_activity.html',{'inactives_remaining':create_inactives_copy()})
	else:
		return redirect("missing_page")

@csrf_protect
def remove_inactives_groups(request,*args,**kwargs):
	"""Sanitize all group invites and memberships.
	
	This is from redis 1
	"""
	if request.user.username == 'mhb11':
		if request.method == "POST":
			decision = request.POST.get("dec",None)
			if decision == 'No':
				delete_inactives_copy()
				return redirect("home")
			elif decision == 'Yes':
				inactives, last_batch = get_inactives(get_50K=True, key="copy_of_inactive_users")
				id_list = map(itemgetter(1), inactives) #list of user ids
				bulk_sanitize_group_invite_and_membership(id_list)
				if last_batch:
					# delete_inactives_copy(delete_orig=True)
					delete_inactives_copy()
				return render(request,"sanitize_groups.html",{'last_batch':last_batch, \
					'inactives_remaining':get_inactive_count(key_name="copy_of_inactive_users")})
		else:
			return render(request,"sanitize_groups.html",{'inactives_remaining':create_inactives_copy()})
	else:
		return redirect("missing_page")


######################################## PSQL Sanitzation ########################################

@csrf_protect
def remove_inactive_user_sessions(request,*args,**kwargs):
	"""Sanitize all sessions of deprecated ids.

	"""
	if request.user.username == 'mhb11':
		if request.method == "POST":
			decision = request.POST.get("dec",None)
			if decision == 'No':
				delete_inactives_copy()
				return redirect("home")
			elif decision == 'Yes':
				inactives, last_batch = get_inactives(get_10K=True, key="copy_of_inactive_users")
				id_list = map(itemgetter(1), inactives) #list of user ids
				# print "Deleting %s sessions created by %s users" % (Session.objects.filter(user_id__in=id_list).count(), len(id_list))
				Session.objects.filter(user_id__in=id_list).delete()
				if last_batch:
					delete_inactives_copy(delete_orig=True)
				return render(request,'sanitize_inactive_sessions.html',{'last_batch':last_batch, \
					'inactives_remaining':get_inactive_count(key_name="copy_of_inactive_users")})
		else:
			return render(request,'sanitize_inactive_sessions.html',{'inactives_remaining':create_inactives_copy()})
	else:
		return redirect("missing_page")




# def process_filenames(list_of_filenames):
# 	"""Parse filenames and save them in redis for exporting

# 	"""
# 	for filename,photo_id in list_of_filenames:
# 		filename = filename.split('photos/')[1]


def confirm_uninteresting(photo_ids):
	"""Returns photo_ids of photos that are uninteresting

	1) Photos that have no related comments, and comment_count is 0
	2) Where the vote score was 0 (although, this could be net 0 couting positives and negatives both. Acknowledging and ignoring that)
	3) Where latest_comment and second_latest_comment were null
	"""
	############
	photo_ids_with_associated_comments = PhotoComment.objects.filter(which_photo_id__in=photo_ids).values_list('which_photo_id',flat=True)
	return list(set(photo_ids) - set(photo_ids_with_associated_comments))
	############

@csrf_protect
def remove_inactives_photos(request,*args,**kwargs):
	"""Sanitize all inactives' photos that garnered 0 comments.

	1) We get the list of inactive ids (divided into batches for performance)
	2) For each batch, find all photo ids
	3) For each photo id, mark photos that do not have a corresponding photocomment
	4) Retrieve the file name of all such photos and store them in a redis list
	"""
	if request.user.username == 'mhb11':
		if request.method == "POST":
			decision = request.POST.get("dec",None)
			if decision == 'No':
				delete_inactives_copy()
				return redirect("home")
			elif decision == 'Yes':
				inactives, last_batch = get_inactives(get_10K=True, key="copy_of_inactive_users")
				id_list = map(itemgetter(1), inactives) #list of user ids
				uninteresting_photo_ids = Photo.objects.filter(owner_id__in=id_list, comment_count=0,vote_score=0,latest_comment__isnull=True).\
				values_list('id',flat=True)
				uninteresting_photo_ids = confirm_uninteresting(uninteresting_photo_ids)
				filenames_and_ids = Photo.objects.filter(id__in=uninteresting_photo_ids).values_list('image_file','id')
				save_deprecated_photo_ids_and_filenames(filenames_and_ids)
				if last_batch:
					delete_inactives_copy(delete_orig=True)
				return render(request,"sanitize_photos.html",{'last_batch':last_batch, \
					'inactives_remaining':get_inactive_count(key_name="copy_of_inactive_users")})
		else:
			return render(request,"sanitize_photos.html",{'inactives_remaining':create_inactives_copy()})
	else:
		return redirect("missing_page")



# def remove_inactives_groups(request,*args,**kwargs):
# 	"""Sanitize all home links and publicreplies.

# 	1) We pick a date constant from over 5 months ago.
# 	2) Set all latest_reply fields to 0 among links created before 5 months ago.
# 	3) Delete all links created before 5 months ago.
# 	4) Delete all publicreplies created before 5 months ago.

#     """
#     if request.user.username == 'mhb11':
#     	if request.method == "POST":
#     		decision = request.POST.get("dec",None)
# 			if decision == 'No':
# 				delete_inactives_copy()
# 				return redirect("home")
# 			elif decision == 'Yes':
# 				inactives, last_batch = get_inactives(get_50K=True, key="copy_of_inactive_users")
# 				id_list = map(itemgetter(1), inactives) #list of user ids
# 				if last_batch:
# 					delete_inactives_copy(delete_orig=True)
# 				return render(request,"santize_groups.html",{'last_batch':last_batch, \
# 					'inactives_remaining':get_inactive_count(key_name="copy_of_inactive_users")})
#     	else:
#     		return render(request,"sanitize_groups.html",{'inactives_remaining':create_inactives_copy()})
#     else:
#     	return redirect("missing_page")

######################################## Mobile Number Sanitzation ########################################

def isolate_non_national_phone_numbers(request):
	all_numbers_and_user_ids = retrieve_all_mobile_numbers() # this produces a list of tuples
	dictionary_of_nums_and_ids = dict(all_numbers_and_user_ids)
	bogus_numbers, users = [], []
	for number, user_id in all_numbers_and_user_ids:
		users.append(int(float(user_id)))
	all_numbers = retrieve_numbers_with_country_codes(set(users))
	import ast
	for entry in all_numbers:
		for number in entry:
			number = ast.literal_eval(number)
			if number["country_prefix"] != '92':
				bogus_numbers.append(((int(float(dictionary_of_nums_and_ids[number["national_number"]]))),number["number"]))
	processed_bogus_pairs = []
	for user_id, number in bogus_numbers:
		user = User.objects.filter(id=user_id).values_list('username',flat=True)[0]
		processed_bogus_pairs.append((user,number))
	return render(request,"show_bogus_mobile_user_ids.html",{'bogus_pairs':processed_bogus_pairs,'total':len(processed_bogus_pairs)})

# ############################################### Logger ###############################################

# def rate_limit_logging_report(request):
# 	report_rate_limited_conversation()
# 	return redirect("missing_page")