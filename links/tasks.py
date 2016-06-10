import os
from unconnectedreddit import celery_app1
import time
from django.core.cache import get_cache, cache
from django.db.models import Count
import datetime
from datetime import datetime, timedelta
from django.utils import timezone
from links.models import Photo, UserFan, PhotoObjectSubscription
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

@celery_app1.task(name='tasks.bulk_create_notifications')
def bulk_create_notifications(user_id, photo_id, timestring):
	fans = UserFan.objects.filter(star_id=user_id).values_list('fan',flat=True)
	timeobj = datetime.strptime(timestring, "%Y-%m-%dT%H:%M:%S.%f")
	if fans:
		fan_list = []
		for fan in fans:
			fan_list.append(PhotoObjectSubscription(viewer_id=fan, which_photo_id=photo_id, updated_at=timeobj, seen=False, type_of_object='1'))
		PhotoObjectSubscription.objects.bulk_create(fan_list)