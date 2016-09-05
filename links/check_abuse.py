from django.utils import timezone
from datetime import timedelta

def time_diff(new_time, old_time):
	difference = new_time - old_time
	difference_in_seconds = difference.total_seconds()
	return difference_in_seconds

def check_video_abuse(count, videos):
	if count == 0:
		forbidden = False
		time_remaining = None
		return forbidden, time_remaining
	else:
		#video[0][X] is always the latest video, video[2][X] etc. was uploaded much earlier
		time_now = timezone.now()
		if count == 1:
			if videos[0][0] < -2 and time_diff(time_now,videos[0][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds=(60*60*24-time_diff(time_now, videos[0][1])))
			else:
				forbidden = False
				time_remaining = None
			return forbidden, time_remaining
		elif count == 2:
			if videos[0][0] < -2 and videos[1][0] < -2 and time_diff(time_now,videos[1][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[1][1])))
			elif videos[0][0] < -2 and time_diff(time_now, videos[0][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[0][1])))
			elif videos[1][0] < -2 and time_diff(time_now, videos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[1][1])))
			else:
				forbidden = False
				time_remaining = None
			return forbidden, time_remaining
		elif count ==3:
			if videos[0][0] < -2 and videos[1][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[2][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and time_diff(time_now, videos[1][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[1][1])))
			elif videos[0][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[2][1])))
			elif videos[1][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[2][1])))
			elif videos[0][0] < -2 and time_diff(time_now, videos[0][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[0][1])))
			elif videos[1][0] < -2 and time_diff(time_now, videos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[1][1])))
			elif videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[2][1])))
			else:
				forbidden = False
				time_remaining = None
			return forbidden, time_remaining
		elif count ==4:
			if videos[0][0] < -2 and videos[1][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*240):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*240-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[2][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[3][1])))
			elif videos[1][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and time_diff(time_now, videos[1][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[1][1])))
			elif videos[0][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[2][1])))
			elif videos[0][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[3][1])))
			elif videos[1][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[2][1])))
			elif videos[1][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[3][1])))
			elif videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and time_diff(time_now, videos[0][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[0][1])))
			elif videos[1][0] < -2 and time_diff(time_now, videos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[1][1])))
			elif videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[2][1])))
			elif videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[3][1])))
			else:
				forbidden = False
				time_remaining = None
			return forbidden, time_remaining
		elif count ==5:
			if videos[0][0] < -2 and videos[1][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*360):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*360-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*240):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*240-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*240):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*240-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*240):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*240-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[2][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*240):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*240-time_diff(time_now, videos[4][1])))
			elif videos[1][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*240):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*240-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[2][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and videos[2][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[4][1])))
			elif videos[1][0] < -2 and videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[3][1])))
			elif videos[1][0] < -2 and videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[4][1])))
			elif videos[1][0] < -2 and videos[2][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[4][1])))
			elif videos[2][0] < -2 and videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*96):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*96-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and videos[1][0] < -2 and time_diff(time_now, videos[1][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[1][1])))
			elif videos[0][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[2][1])))
			elif videos[0][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[3][1])))
			elif videos[0][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[4][1])))
			elif videos[1][0] < -2 and videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[2][1])))
			elif videos[1][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[3][1])))
			elif videos[1][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[4][1])))
			elif videos[2][0] < -2 and videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[3][1])))
			elif videos[2][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[4][1])))
			elif videos[3][0] < -2 and videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, videos[4][1])))
			elif videos[0][0] < -2 and time_diff(time_now, videos[0][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[0][1])))
			elif videos[1][0] < -2 and time_diff(time_now, videos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[1][1])))
			elif videos[2][0] < -2 and time_diff(time_now, videos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[2][1])))
			elif videos[3][0] < -2 and time_diff(time_now, videos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[3][1])))
			elif videos[4][0] < -2 and time_diff(time_now, videos[4][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, videos[4][1])))
			return forbidden, time_remaining
		else:
			pass

def check_photo_abuse(count, photos):
	#photos is a list
	#count is the number of objects in that list
	if count == 0:
		forbidden = False
		time_remaining = None
		return forbidden, time_remaining
	else:
		#time_now = datetime.utcnow().replace(tzinfo=utc)			
		time_now = timezone.now()
		if count == 1:
			if photos[0][0] < -2 and time_diff(time_now, photos[0][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[0][1])))
				return forbidden, time_remaining
			else:
				forbidden = False
				time_remaining = None
				return forbidden, time_remaining
		elif count == 2:
			if photos[0][0] < -2 and photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and time_diff(time_now, photos[0][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[0][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			else:
				forbidden = False
				time_remaining = None
				return forbidden, time_remaining
		elif count == 3:
			if photos[0][0] < -2 and photos[1][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and time_diff(time_now, photos[0][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[0][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			elif photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			else:
				forbidden = False
				time_remaining = None
				return forbidden, time_remaining
		elif count == 4:
			if photos[0][0] < -2 and photos[1][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*144):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*144-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and time_diff(time_now, photos[0][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[0][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			elif photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			else:
				forbidden = False
				time_remaining = None
				return forbidden, time_remaining
		elif count == 5:
			if photos[0][0] < -2 and photos[1][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*288):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*288-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*144):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*144-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[2][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*144):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*144-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*144):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*144-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*144):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*144-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*144):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*144-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[2][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[2][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[2][0] < -2 and photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*72):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*72-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[2][0] < -2 and photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[2][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[3][0] < -2 and photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*24):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*24-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			elif photos[0][0] < -2 and time_diff(time_now, photos[0][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[0][1])))
				return forbidden, time_remaining
			elif photos[1][0] < -2 and time_diff(time_now, photos[1][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[1][1])))
				return forbidden, time_remaining
			elif photos[2][0] < -2 and time_diff(time_now, photos[2][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[2][1])))
				return forbidden, time_remaining
			elif photos[3][0] < -2 and time_diff(time_now, photos[3][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[3][1])))
				return forbidden, time_remaining
			elif photos[4][0] < -2 and time_diff(time_now, photos[4][1]) < (60*60*6):
				forbidden = True
				time_remaining = time_now + timedelta(seconds = (60*60*6-time_diff(time_now, photos[4][1])))
				return forbidden, time_remaining
			else:
				forbidden = False
				time_remaining = None
				return forbidden, time_remaining
		else:
			forbidden = False
			time_remaining = None
			return forbidden, time_remaining
		forbidden = False
		time_remaining = None
		return forbidden, time_remaining
