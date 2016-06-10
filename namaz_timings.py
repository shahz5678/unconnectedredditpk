from datetime import time as time_object

namaz_timings = {}

prefajr_least = time_object(hour=0, minute=0)
prefajr_most = time_object(hour=3, minute=0) 
fajr_least = time_object(hour=3, minute=0)
fajr_most = time_object(hour=6, minute=30) #i.e. FAJR is between 3AM and 6:30AM
prezuhr_least = time_object(hour=6, minute=30) 
prezuhr_most = time_object(hour=11, minute=50)
zuhr_least = time_object(hour=11, minute=50)
zuhr_most = time_object(hour=14, minute=55)#i.e. ZUHR is between 11:50AM and 2:55PM
asr_least = time_object(hour=14, minute=55)
asr_most = time_object(hour=16, minute=55)#i.e. ASR is between 2:55PM and 4:55PM
maghrib_least = time_object(hour=16, minute=55)
maghrib_most = time_object(hour=20, minute=0)#i.e. MAGHRIB is between 4:55PM and 8:00PM
isha_least = time_object(hour=20, minute=0)
isha_most = time_object(hour=23, minute=59)#i.e. ISHA is between 8:00PM and 12:00AM (midnight)

def WhichNamaz(minutes):
	hour = minutes // 60
	minute = minutes % 60
	current_time = time_object(hour=hour, minute=minute)
	#print current_time, isha_least, isha_most
	if prefajr_least <= current_time < prefajr_most:
		namaz = False
		next_namaz = 'Fajr'
		previous_namaz = 'Isha'
	elif fajr_least <= current_time < fajr_most:
		namaz = 'Fajr'
		next_namaz = 'Zuhr'
		previous_namaz = 'Isha'
	elif prezuhr_least <= current_time < prezuhr_most:
		namaz = False
		next_namaz = 'Zuhr'
		previous_namaz = 'Fajr'
	elif zuhr_least <= current_time < zuhr_most:
		namaz = 'Zuhr'
		next_namaz = 'Asr'
		previous_namaz = 'Fajr'
	elif asr_least <= current_time < asr_most:
		namaz = 'Asr'
		next_namaz = 'Maghrib'
		previous_namaz = 'Zuhr'
	elif maghrib_least <= current_time < maghrib_most:
		namaz = 'Maghrib'
		next_namaz = 'Isha'
		previous_namaz = 'Asr'
	elif isha_least <= current_time <= isha_most:
		namaz = 'Isha'
		next_namaz = 'Fajr'
		previous_namaz = 'Maghrib'
	else:
		namaz = False
		next_namaz = False
		previous_namaz = False
	return previous_namaz, next_namaz, namaz

namaz_timings = {minute: WhichNamaz(minute) for minute in range(1440)}

def streak_alive(prev_salat_name, latest_salat_object, now):
	#latest_salat_minute = latest_salat_object.when.hour * 60 + latest_salat_object.when.minute
	#previous_latest_namaz, next_latest_namaz, latest_namaz = namaz_timings[latest_salat_minute]
	#latest_namaz is False if pre-namaz object was skipped
	if latest_salat_object.skipped:# and latest_namaz:
		return False
	else:
		latest_salat_date = latest_salat_object.when.date()
		latest_salat_time = latest_salat_object.when.time()
		# print "prev_salat_name: %s" % prev_salat_name
		# print "latest_salat_date: %s" % latest_salat_date
		# print "latest_salat_time: %s" % latest_salat_time
		# print "now.date(): %s" % now.date()
		if prev_salat_name == 'Fajr':
			if (fajr_least <= latest_salat_time < fajr_most) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Zuhr':
			if (zuhr_least <= latest_salat_time < zuhr_most) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Asr':
			if (asr_least <= latest_salat_time < asr_most) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Maghrib':
			if (maghrib_least <= latest_salat_time < maghrib_most) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Isha':
			if (isha_least <= latest_salat_time < isha_most) and (latest_salat_date == now.date() or latest_salat_date == (now.date()-timedelta(days=1))):
				return True
			else:
				return False
		else:
			return False