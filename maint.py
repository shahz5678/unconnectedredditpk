import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
from django.contrib.auth.models import User
from links.models import TotalFanAndPhotos, UserFan, Photo
from django.conf import settings
import datetime
from datetime import datetime, timedelta
from datetime import time as time_object
from django.utils import timezone
from django.utils.timezone import utc

now = datetime.utcnow()+timedelta(hours=5)

def Totalify():
	all_users = User.objects.all()
	totalfanandphotos = []
	users = 0
	photos = 0
	fans = 0
	print "Starting..."
	for user in all_users:
		total_fans = UserFan.objects.filter(star=user).count()
		total_photos = Photo.objects.filter(owner=user).count()
		totalfanandphotos.append(TotalFanAndPhotos(total_fans=total_fans, total_photos=total_photos, owner=user, last_updated=(datetime.utcnow()+timedelta(hours=5))))
		users = users + 1
		photos = photos + total_photos
		fans = fans + total_fans
	print "Commencing bulk creation..."
	TotalFanAndPhotos.objects.bulk_create(totalfanandphotos)
	total_users = User.objects.count()
	total_fan = UserFan.objects.count()
	total_photo = Photo.objects.count()
	print "REPORT:"
	print "Total users processed: %s" % users
	print "Total fans processed: %s" % fans
	print "Total photos processed: %s" % photos
	print "----------------------"
	print "Total users in system: %s" % total_users
	print "Total fans in system: %s" % total_fan
	print "Total photos in system: %s" % total_photo
	
Totalify()