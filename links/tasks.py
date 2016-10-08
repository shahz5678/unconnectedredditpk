import os
from unconnectedreddit import celery_app1
import time
from django.core.cache import get_cache, cache
from django.db.models import Count, Q, F
import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from links.models import Photo, UserFan, PhotoObjectSubscription, LatestSalat, Photo, PhotoComment, Link, Publicreply, TotalFanAndPhotos, Report, \
UserProfile, Video, HotUser
from links.redismodules import add_filtered_post, add_unfiltered_post, add_photo_to_best, all_photos, add_video, save_recent_video, \
add_to_whose_online
from links.azurevids.azurevids import uploadvid
from namaz_timings import namaz_timings, streak_alive
from user_sessions.models import Session
from django.contrib.auth.models import User

@celery_app1.task(name='tasks.rank_all_photos')
def rank_all_photos():
	pass

@celery_app1.task(name='tasks.rank_all_photos1')
def rank_all_photos1():
	pass

@celery_app1.task(name='tasks.rank_photos')
def rank_photos():
	for photo in Photo.objects.filter(id__in=all_photos()):
		score = photo.set_rank()
		add_photo_to_best(photo.id, score)

#@shared_task(name='tasks.whoseonline')
@celery_app1.task(name='tasks.whoseonline')
def whoseonline():
	user_ids = Session.objects.filter(user__isnull=False).filter(last_activity__gte=(timezone.now()-timedelta(minutes=5))).\
	values_list('user_id', flat=True).distinct('user')
	add_to_whose_online(user_ids)
	# unique_user_sessions = Session.objects.filter(last_activity__gte=(timezone.now()-timedelta(minutes=5))).only('user').distinct('user').prefetch_related('user__userprofile')
	# #unique_user_sessions are session objects, e.g. [<Session_Deferred_expire_date_ip_last_activity_session_data_user_agent: Session_Deferred_expire_date_ip_last_activity_session_data_user_agent object>, <Session_Deferred_expire_date_ip_last_activity_session_data_user_agent: Session_Deferred_expire_date_ip_last_activity_session_data_user_agent object>]
	# users = [session.user for session in unique_user_sessions]
	# users = [user for user in users if user is not None] #these are user objects, e.g. [<User: mhb11>, <User: gori>]
	# print users 
	# cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
 #            'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 120,
 #        })
	# cache_mem.set('online_users', users)  # expiring in 120 seconds

@celery_app1.task(name='tasks.fans')
def fans():
	object_list = TotalFanAndPhotos.objects.select_related('owner__userprofile').exclude(total_photos=0).order_by('-total_fans','-total_photos')[:100]
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
            'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 120,
        })
	cache_mem.set('fans', object_list)  # expiring in 120 seconds

@celery_app1.task(name='tasks.salat_streaks')
def salat_streaks():
	now = datetime.utcnow()+timedelta(hours=5)
	current_minute = now.hour * 60 + now.minute
	twelve_hrs_ago = now - timedelta(hours=12)
	previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time, current_namaz_end_time = namaz_timings[current_minute]
	if namaz == 'Fajr':
		salat = '1'
		object_list = LatestSalat.objects.filter(Q(latest_salat='1')|Q(latest_salat='5')).exclude(when__lte=twelve_hrs_ago).order_by('-salatee__userprofile__streak')[:500]
	elif namaz == 'Zuhr':
		salat = '2'
		object_list = LatestSalat.objects.filter(Q(latest_salat='2')|Q(latest_salat='1')).exclude(when__lte=twelve_hrs_ago).order_by('-salatee__userprofile__streak')[:500]
	elif namaz == 'Asr':
		salat = '3'
		object_list = LatestSalat.objects.filter(Q(latest_salat='3')|Q(latest_salat='2')).exclude(when__lte=twelve_hrs_ago).order_by('-salatee__userprofile__streak')[:500]
	elif namaz == 'Maghrib':
		salat = '4'
		object_list = LatestSalat.objects.filter(Q(latest_salat='4')|Q(latest_salat='3')).exclude(when__lte=twelve_hrs_ago).order_by('-salatee__userprofile__streak')[:500]
	elif namaz == 'Isha':
		salat = '5'
		object_list = LatestSalat.objects.filter(Q(latest_salat='5')|Q(latest_salat='4')).exclude(when__lte=twelve_hrs_ago).order_by('-salatee__userprofile__streak')[:500]
	else:
		salat = '1'
		object_list = LatestSalat.objects.filter(Q(latest_salat='1')|Q(latest_salat='5')).exclude(when__lte=twelve_hrs_ago).order_by('-salatee__userprofile__streak')[:500]
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
        'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 120,
    })
	cache_mem.set('salat_streaks', object_list)  # expiring in 120 seconds

@celery_app1.task(name='tasks.photo_upload_tasks')
def photo_upload_tasks(banned, user_id, photo_id, timestring, stream_id, device):
	photo = Photo.objects.get(id=photo_id)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	update = TotalFanAndPhotos.objects.filter(owner_id=user_id).update(last_updated=datetime.utcnow()+timedelta(hours=5), total_photos=F('total_photos')+1)
	if not update:
		TotalFanAndPhotos.objects.create(owner_id=user_id, total_fans=0, total_photos=1, last_updated=datetime.utcnow()+timedelta(hours=5))
	PhotoObjectSubscription.objects.create(viewer_id=user_id, which_photo_id=photo_id, updated_at=timeobj)#
	UserProfile.objects.filter(user_id=user_id).update(score=F('score')-3)
	hotuser = HotUser.objects.filter(which_user_id=user_id).latest('id')
	if hotuser.allowed and hotuser.hot_score > 4:
		link = Link.objects.create(description=photo.caption, submitter_id=user_id, device=device, cagtegory='6', which_photostream_id=stream_id)#
		if banned == '1':
			add_unfiltered_post(link.id)
		else:
			add_filtered_post(link.id)
			add_unfiltered_post(link.id)

@celery_app1.task(name='tasks.photo_tasks')
def photo_tasks(user_id, photo_id, timestring, photocomment_id, count, text, it_exists):
	user = User.objects.get(id=user_id)
	photo = Photo.objects.get(id=photo_id)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	all_commenter_ids = list(set(PhotoComment.objects.filter(which_photo_id=photo_id).order_by('-id').values_list('submitted_by', flat=True)[:25]))
	if photo.owner_id not in all_commenter_ids:	
		all_commenter_ids.append(photo.owner_id)
	PhotoObjectSubscription.objects.filter(viewer_id__in=all_commenter_ids, type_of_object='0', which_photo_id=photo_id).update(seen=False, updated_at=timeobj)			
	exists = PhotoObjectSubscription.objects.filter(viewer_id=user_id, type_of_object='0', which_photo_id=photo_id).update(updated_at=timeobj, seen=True)
	if not exists:
		PhotoObjectSubscription.objects.create(viewer_id=user_id, which_photo_id=photo_id, type_of_object='0',updated_at=timeobj)
	photo.second_latest_comment = photo.latest_comment
	photo.latest_comment_id = photocomment_id
	photo.comment_count = count
	user.userprofile.previous_retort = text
	if user_id != photo.owner_id and not it_exists:
		user.userprofile.score = user.userprofile.score + 2 #giving score to the commenter
		photo.owner.userprofile.media_score = photo.owner.userprofile.media_score + 2 #giving media score to the photo poster
		photo.owner.userprofile.score = photo.owner.userprofile.score + 2 # giving score to the photo poster
		photo.visible_score = photo.visible_score + 2
		photo.owner.userprofile.save()
	photo.save()
	user.userprofile.save()

@celery_app1.task(name='tasks.video_vote_tasks')
def video_vote_tasks(video_id, user_id, vote_score_increase, visible_score_increase, media_score_increase, score_increase):
	Video.objects.filter(id=video_id).update(vote_score=F('vote_score')+vote_score_increase, visible_score=F('visible_score')+visible_score_increase)
	UserProfile.objects.filter(user_id=user_id).update(media_score=F('media_score')+media_score_increase, score=F('score')+score_increase)

@celery_app1.task(name='tasks.photo_vote_tasks')
def photo_vote_tasks(photo_id, user_id, vote_score_increase, visible_score_increase, media_score_increase, score_increase):
	Photo.objects.filter(id=photo_id).update(vote_score=F('vote_score')+vote_score_increase, visible_score=F('visible_score')+visible_score_increase)
	UserProfile.objects.filter(user_id=user_id).update(media_score=F('media_score')+media_score_increase, score=F('score')+score_increase)

@celery_app1.task(name='tasks.video_tasks')
def video_tasks(user_id, video_id, timestring, videocomment_id, count, text, it_exists):
	user = User.objects.get(id=user_id)
	video = Video.objects.get(id=video_id)
	video.second_latest_comment = video.latest_comment
	video.latest_comment_id = videocomment_id
	video.comment_count = count
	user.userprofile.previous_retort = text
	if user_id != video.owner_id and not it_exists:
		user.userprofile.score = user.userprofile.score + 2 #giving score to the commenter
		video.owner.userprofile.media_score = video.owner.userprofile.media_score + 2 #giving media score to the video poster
		video.owner.userprofile.score = video.owner.userprofile.score + 2 # giving score to the video poster
		video.visible_score = video.visible_score + 2
		video.owner.userprofile.save()
	video.save()
	user.userprofile.save()	

@celery_app1.task(name='tasks.publicreply_tasks')
def publicreply_tasks(user_id, description):
	user = User.objects.get(id=user_id)
	UserProfile.objects.filter(user_id=user_id).update(score=F('score')+2, previous_retort=description)
	# user.userprofile.previous_retort = description
	# user.userprofile.score = user.userprofile.score + 2
	# user.userprofile.save()

@celery_app1.task(name='tasks.report')
def report(reporter_id, target_id, report_origin=None, report_reason=None, which_link_id=None, which_publicreply_id=None, which_photo_id=None, which_photocomment_id=None, which_group_id=None, which_reply_id=None, nickname=None):
	if report_origin == '1':
		#origin:chupair
		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason='Chupair', report_origin=report_origin, which_link_id=which_link_id)
	elif report_origin == '2':
		#origin:publicreply
		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason='Publicreply', report_origin=report_origin, which_publicreply_id=which_publicreply_id)
	elif report_origin == '7':
		#origin:photocomment
		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason='PhotoComment', report_origin=report_origin, which_photocomment_id=which_photocomment_id, which_photo_id=which_photo_id)
	elif report_origin == '3':
		#origin:nickname
		userprofile = UserProfile.objects.get(user_id=reporter_id)
		target = User.objects.get(id=target_id)
		latest_user = User.objects.latest('id')
		userprofile.score = userprofile.score - 10
		userprofile.save()
		if int(latest_user.id) - int(target_id) < 50:
			Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_reason=target.username, report_origin=report_origin)
		else:
			# i.e. do nothing if it's an old id
			pass
	elif report_origin == '4':
		#origin:profile
		if report_reason == '1':
			reason = 'gali di'
		elif report_reason == '2':
			reason = 'dhamki di'
		elif report_reason == '3':
			reason = 'fake profile'
		elif report_reason == '4':
			reason = 'gandi baat'
		elif report_reason == '5':
			reason = 'password manga'
		elif report_reason == '6':
			reason = 'firqa wariyat'
		elif report_reason == '7':
			reason = 'gandi photo'
		elif report_reason == '8':
			reason = 'fake admin'
		else:
			reason = report_reason
		Report.objects.create(reporter_id=reporter_id, target_id=target_id, report_origin=report_origin, report_reason=reason)
	
@celery_app1.task(name='tasks.bulk_create_notifications')
def bulk_create_notifications(user_id, photo_id, timestring):
	fans = UserFan.objects.filter(star_id=user_id).values_list('fan',flat=True)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	if fans:
		fan_list = []
		for fan in fans:
			fan_list.append(PhotoObjectSubscription(viewer_id=fan, which_photo_id=photo_id, updated_at=timeobj, seen=False, type_of_object='1'))
		PhotoObjectSubscription.objects.bulk_create(fan_list)

@celery_app1.task(name='tasks.video_upload_tasks')
def video_upload_tasks(video_name, video_id, user_id):
	lst = uploadvid(video_name)
	low_res_thumb = "//"+lst[0].partition('://')[2]
	small_thumb = "//"+lst[1].partition('://')[2]
	low_res_video = "//"+lst[2].partition('://')[2]
	high_res_video = "//"+lst[3].partition('://')[2]
	video = Video.objects.filter(id=video_id).update(low_res_thumb=low_res_thumb, small_thumb=small_thumb, low_res_video=low_res_video, high_res_video=high_res_video, processed=True)
	if video:
		add_video(video_id)
		save_recent_video(user_id, video_id)
		UserProfile.objects.filter(user_id=user_id).update(score=F('score')-5)
	else:
		pass