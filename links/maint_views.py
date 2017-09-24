import random, itertools
from operator import itemgetter
from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from models import Link, Photo, PhotoComment, UserProfile, Publicreply, Reply,UserFan, ChatPic
from redis3 import insert_nick_list, get_nick_likeness
from redis1 import get_inactives, set_inactives



def change_nicks(request,*args,**kwargs):
	"""This frees up the name space of nicks.

    Nicks, once taken, are locked out of the namespace.
    This changes nicknames that aren't in use anymore to a random string.
    """
	if request.user.username == 'mhb11':
		inactives = get_inactives()
		id_list = map(itemgetter(1), inactives) #list of ids to deprecate
		id_len = len(id_list)
		rand_nums = random.sample(xrange(100000,999999), id_len+10)
		counter = 0
		for pk in id_list:
			nick = "dmdm_"+str(rand_nums[counter])
			User.objects.filter(id=int(pk)).update(username=nick)
			counter += 1
		return render(request,'deprecate_nicks.html',{})
	else:
		return render(request,'404.html',{})

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
		# all user ids who last logged in more than 3 months ago
		three_months_ago = datetime.utcnow()-timedelta(days=90)
		all_old_ids = set(User.objects.filter(last_login__lte=three_months_ago).values_list('id',flat=True))
		# user ids not found in Sessions
		current_users = Session.objects.filter(user__isnull=False,last_activity__gte=three_months_ago).values_list('user_id',flat=True)
		logged_out_users = set(User.objects.exclude(id__in=current_users).values_list('id',flat=True))
		# # messaged on home more than 3 months ago
		current_home_messegers = Link.objects.filter(submitted_on__gte=three_months_ago).values_list('submitter_id',flat=True)
		never_home_message = set(User.objects.exclude(id__in=current_home_messegers).values_list('id',flat=True))
		# # never submitted a publicreply
		current_public_repliers = Publicreply.objects.filter(submitted_on__gte=three_months_ago).values_list('submitted_by_id',flat=True)
		never_publicreply = set(User.objects.exclude(id__in=current_public_repliers).values_list('id',flat=True))
		# never sent a photocomment
		current_photo_commenters = PhotoComment.objects.filter(submitted_on__gte=three_months_ago).values_list('submitted_by_id',flat=True)
		never_photocomment = set(User.objects.exclude(id__in=current_photo_commenters).values_list('id',flat=True))
		# never wrote in a group
		current_group_writers = Reply.objects.filter(submitted_on__gte=three_months_ago).values_list('writer_id',flat=True)
		never_groupreply = set(User.objects.exclude(id__in=current_group_writers).values_list('id',flat=True))
		# # never uploaded a photo
		current_photo_uploaders = Photo.objects.filter(upload_time__gte=three_months_ago).values_list('owner_id',flat=True)
		never_uploaded_photo = set(User.objects.exclude(id__in=current_photo_uploaders).values_list('id',flat=True))
		# # never sent a chatpic
		current_chat_pic_users = ChatPic.objects.filter(upload_time__gte=three_months_ago).values_list('owner_id',flat=True)
		never_sent_chat_pic = set(User.objects.exclude(id__in=current_chat_pic_users).values_list('id',flat=True))
		# # never fanned anyone
		current_fanners = UserFan.objects.filter(fanning_time__gte=three_months_ago).values_list('fan_id',flat=True)
		never_fanned = set(User.objects.exclude(id__in=current_fanners).values_list('id',flat=True))
		# # score is below 15000
		less_than_15000 = set(UserProfile.objects.filter(score__lte=15000).values_list('user_id',flat=True))
		# # intersection of all such ids
		sets = [all_old_ids, logged_out_users, never_home_message, never_publicreply, never_photocomment, never_uploaded_photo, never_fanned, less_than_15000, \
		never_groupreply, never_sent_chat_pic]
		inactive = set.intersection(*sets)
		#################
		#sanitize pink stars:
		pink_stars = set(User.objects.filter(username__in=FEMALES).values_list('id',flat=True))
		inactive = inactive - pink_stars
		#################
		inactives = []
		inactives_data = User.objects.select_related('userprofile').filter(id__in=inactive).values_list('username','id','userprofile__score')
		for inact in inactives_data:
			inactives.append((inact[0]+":"+str(inact[2]),inact[1]))
		size = len(inactives)
		list1 = inactives[:size/2]
		list2 = inactives[size/2:]
		from itertools import chain
		# breaking it into two lists avoids socket time out
		set_inactives([x for x in chain.from_iterable(list1)])
		set_inactives([x for x in chain.from_iterable(list2)])
		return render(request,'deprecate_nicks.html',{})
	else:
		return render(request,'404.html',{})



def insert_nicks(request,*args,**kwargs):
	"""Inserts nicks in a redis sorted set for quick checking at the time of sign up

    All nicknames are first retrieved from the database.
    They are then inserted, chunk-wise, into the redis sorted set.
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

###############################################################
