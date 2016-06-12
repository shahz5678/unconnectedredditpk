import os
from unconnectedreddit import celery_app1
import time
from django.core.cache import get_cache, cache
from django.db.models import Count, Q
import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from links.models import Photo, UserFan, PhotoObjectSubscription, LatestSalat
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
	previous_namaz, next_namaz, namaz, next_namaz_start_time = namaz_timings[current_minute]
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

@celery_app1.task(name='tasks.bulk_create_notifications')
def bulk_create_notifications(user_id, photo_id, timestring):
	fans = UserFan.objects.filter(star_id=user_id).values_list('fan',flat=True)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	if fans:
		fan_list = []
		for fan in fans:
			fan_list.append(PhotoObjectSubscription(viewer_id=fan, which_photo_id=photo_id, updated_at=timeobj, seen=False, type_of_object='1'))
		PhotoObjectSubscription.objects.bulk_create(fan_list)