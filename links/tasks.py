import os
from unconnectedreddit import celery_app1
import time
from django.core.cache import get_cache, cache
from django.db.models import Count, Q
import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from links.models import Photo, UserFan, PhotoObjectSubscription, LatestSalat, Photo, PhotoComment, Link, Publicreply
from namaz_timings import namaz_timings, streak_alive
from user_sessions.models import Session
from django.contrib.auth.models import User

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")

# @celery_app1.task(name='tasks.rank_all')
# def rank_all():
#     for link in Link.with_votes.all():
#         link.set_rank()

@celery_app1.task(name='tasks.rank_all_photos')
def rank_all_photos():
	for photo in Photo.objects.order_by('-id')[:400]:
		photo.set_rank()

#@shared_task(name='tasks.whoseonline')
@celery_app1.task(name='tasks.whoseonline')
def whoseonline():
	unique_user_sessions = Session.objects.filter(last_activity__gte=(timezone.now()-timedelta(minutes=5))).only('user').distinct('user')
	users = [session.user for session in unique_user_sessions]
	users = [user for user in users if user is not None]
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
            'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 120,
        })
	cache_mem.set('online_users', users)  # expiring in 120 seconds

@celery_app1.task(name='tasks.fans')
def fans():
	object_list = User.objects.annotate(photo_count=Count('photo', distinct=True)).exclude(photo_count=0).annotate(num_fans=Count('star', distinct=True)).order_by('-num_fans')[:100]
	#ids = [user.id for user in object_list]
	#users = User.objects.annotate(photo_count=Count('photo', distinct=True)).annotate(num_fans=Count('star', distinct=True)).in_bulk(ids)
	#users_fans = [(users[id], users[id].photo_count, users[id].num_fans) for id in ids]
	cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
            'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 120,
        })
	cache_mem.set('fans', object_list)  # expiring in 120 seconds

@celery_app1.task(name='tasks.salat_streaks')
def salat_streaks():
	now = datetime.utcnow()+timedelta(hours=5)
	current_minute = now.hour * 60 + now.minute
	twelve_hrs_ago = now - timedelta(hours=12)
	previous_namaz, next_namaz, namaz, next_namaz_start_time, current_namaz_start_time = namaz_timings[current_minute]
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

@celery_app1.task(name='tasks.photo_tasks')
def photo_tasks(user_id, photo_id, timestring, photocomment_id, count, text, it_exists):
	user = User.objects.get(id=user_id)
	photo = Photo.objects.get(id=photo_id)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	all_commenter_ids = list(set(PhotoComment.objects.filter(which_photo_id=photo_id).order_by('-id').values_list('submitted_by', flat=True)[:25]))
	if photo.owner_id not in all_commenter_ids:	
		all_commenter_ids.append(photo.owner_id)
	PhotoObjectSubscription.objects.filter(viewer_id__in=all_commenter_ids, type_of_object='0', which_photo_id=photo_id).update(seen=False)			
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

@celery_app1.task(name='tasks.publicreply_tasks')
def publicreply_tasks(user_id, answer_to_id, timestring, reply_id, description):
	user = User.objects.get(id=user_id)
	link = Link.objects.get(id=answer_to_id)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	all_reply_ids = list(set(Publicreply.objects.filter(answer_to_id=answer_to_id).order_by('-id').values_list('submitted_by', flat=True)[:25]))
	if link.submitter_id not in all_reply_ids:
		all_reply_ids.append(link.submitter_id)
	PhotoObjectSubscription.objects.filter(viewer_id__in=all_reply_ids, type_of_object='2', which_link_id=answer_to_id).update(seen=False)
	exists = PhotoObjectSubscription.objects.filter(viewer_id=user_id, type_of_object='2', which_link_id=answer_to_id).update(updated_at=timeobj, seen=True)
	if not exists: #i.e. could not be updated
		PhotoObjectSubscription.objects.create(viewer_id=user_id, type_of_object='2', which_link_id=answer_to_id, updated_at=timeobj)
	link.latest_reply_id=reply_id
	link.save()
	user.userprofile.previous_retort = description
	user.userprofile.score = user.userprofile.score + 2
	user.userprofile.save()
	
@celery_app1.task(name='tasks.bulk_create_notifications')
def bulk_create_notifications(user_id, photo_id, timestring):
	fans = UserFan.objects.filter(star_id=user_id).values_list('fan',flat=True)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	if fans:
		fan_list = []
		for fan in fans:
			fan_list.append(PhotoObjectSubscription(viewer_id=fan, which_photo_id=photo_id, updated_at=timeobj, seen=False, type_of_object='1'))
		PhotoObjectSubscription.objects.bulk_create(fan_list)