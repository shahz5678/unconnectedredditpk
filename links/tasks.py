import os
from unconnectedreddit import celery_app1
import time
from django.core.cache import get_cache, cache
#from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from links.models import Photo
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
	cache_mem.set('online_users', users)  # expiring in 70 seconds