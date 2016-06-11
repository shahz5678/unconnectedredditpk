from datetime import datetime, date, timedelta
from datetime import time as time_object
import january, february, march, april, may, june, july, august, september, october, november, december

namaz_timings = {}
now = datetime.utcnow()+timedelta(hours=5)
day_number = (datetime.utcnow()+timedelta(hours=5)).date().day
month_name={'01':january,'02':february,'03':march,'04':april,'05':may,'06':june,'07':july,'08':august,'09':september,'10':october,'11':november,'12':december}
month_days={january:31, february:28, march:31, april:30, may: 31, june:30, july:31, august:31, september:30, october:31, november:30, december:31}

def get_time(day_number, month, time_at_start, time_at_end):
	time_at_end = datetime.combine(date.today(), time_at_end)
	time_at_start = datetime.combine(date.today(), time_at_start)
	if time_at_end > time_at_start:
		drift_in_time_interval = time_at_end - time_at_start
		daily_drift_in_time_interval = drift_in_time_interval/((month_days[month])-1)
		daily_drift_in_seconds = daily_drift_in_time_interval.total_seconds()
		time_window = time_at_start + timedelta(seconds = (daily_drift_in_seconds*(day_number-1)))
	elif time_at_start > time_at_end:
		drift_in_time_interval = time_at_start - time_at_end
		daily_drift_in_time_interval = drift_in_time_interval/((month_days[month])-1)
		daily_drift_in_seconds = daily_drift_in_time_interval.total_seconds()
		time_window = time_at_start - timedelta(seconds = (daily_drift_in_seconds*(day_number-1)))
	else:
		time_window = time_at_start
	return time_window.time()

def prefajr_least(month):
	return get_time(day_number, month, month.prefajr_least_before, month.prefajr_least_after)

def prefajr_most(month):
	return get_time(day_number, month, month.prefajr_most_before, month.prefajr_most_after)

def fajr_least(month):
	return get_time(day_number, month, month.fajr_least_before, month.fajr_least_after)

def fajr_most(month):
	return get_time(day_number, month, month.fajr_most_before, month.fajr_most_after)

def prezuhr_least(month):
	return get_time(day_number, month, month.prezuhr_least_before, month.prezuhr_least_after)

def prezuhr_most(month):
	return get_time(day_number, month, month.prezuhr_most_before, month.prezuhr_most_after)

def zuhr_least(month):
	return get_time(day_number, month, month.zuhr_least_before, month.zuhr_least_after)

def zuhr_most(month):
	return get_time(day_number, month, month.zuhr_most_before, month.zuhr_most_after)

def preasr_least(month):
	return get_time(day_number, month, month.preasr_least_before, month.preasr_least_after)

def preasr_most(month):
	return get_time(day_number, month, month.preasr_most_before, month.preasr_most_after)

def asr_least(month):
	return get_time(day_number, month, month.asr_least_before, month.asr_least_after)

def asr_most(month):
	return get_time(day_number, month, month.asr_most_before, month.asr_most_after)

def premaghrib_least(month):
	return get_time(day_number, month, month.premaghrib_least_before, month.premaghrib_least_after)

def premaghrib_most(month):
	return get_time(day_number, month, month.premaghrib_most_before, month.premaghrib_most_after)

def maghrib_least(month):
	return get_time(day_number, month, month.maghrib_least_before, month.maghrib_least_after)

def maghrib_most(month):
	return get_time(day_number, month, month.maghrib_most_before, month.maghrib_most_after)

def preisha_least(month):
	return get_time(day_number, month, month.preisha_least_before, month.preisha_least_after)

def preisha_most(month):
	return get_time(day_number, month, month.preisha_most_before, month.preisha_most_after)

def isha_least(month):
	return get_time(day_number, month, month.isha_least_before, month.isha_least_after)

def isha_most(month):
	return get_time(day_number, month, month.isha_most_before, month.isha_most_after)


def WhichNamaz(minutes, month):
	hour = minutes // 60
	minute = minutes % 60
	current_time = time_object(hour=hour, minute=minute)
	if prefajr_least(month) <= current_time < prefajr_most(month):
		namaz = False
		next_namaz = 'Fajr'
		previous_namaz = 'Isha'
	elif fajr_least(month) <= current_time < fajr_most(month):
		namaz = 'Fajr'
		next_namaz = 'Zuhr'
		previous_namaz = 'Isha'
	elif prezuhr_least(month) <= current_time < prezuhr_most(month):
		namaz = False
		next_namaz = 'Zuhr'
		previous_namaz = 'Fajr'
	elif zuhr_least(month) <= current_time < zuhr_most(month):
		namaz = 'Zuhr'
		next_namaz = 'Asr'
		previous_namaz = 'Fajr'
	elif preasr_least(month) <= current_time < preasr_most(month):
		namaz = False
		next_namaz = 'Asr'
		previous_namaz = 'Zuhr'
	elif asr_least(month) <= current_time < asr_most(month):
		namaz = 'Asr'
		next_namaz = 'Maghrib'
		previous_namaz = 'Zuhr'
	elif premaghrib_least(month) <= current_time < premaghrib_most(month):
		namaz = False
		next_namaz = 'Maghrib'
		previous_namaz = 'Asr'
	elif maghrib_least(month) <= current_time < maghrib_most(month):
		namaz = 'Maghrib'
		next_namaz = 'Isha'
		previous_namaz = 'Asr'
	elif preisha_least(month) <= current_time < preisha_most(month):
		namaz = False
		next_namaz = 'Isha'
		previous_namaz = 'Maghrib'
	elif isha_least(month) <= current_time <= isha_most(month):
		namaz = 'Isha'
		next_namaz = 'Fajr'
		previous_namaz = 'Maghrib'
	else:
		namaz = False
		next_namaz = False
		previous_namaz = False
	return previous_namaz, next_namaz, namaz

month = now.strftime("%m")
namaz_timings = {minute: WhichNamaz(minute,month_name[month]) for minute in range(1440)}

def streak_alive(prev_salat_name, latest_salat_object, now):
	if latest_salat_object.skipped:# and latest_namaz:
		return False
	else:
		latest_salat_date = latest_salat_object.when.date()
		latest_salat_time = latest_salat_object.when.time()
		if prev_salat_name == 'Fajr':
			if (fajr_least(month_name[month]) <= latest_salat_time < fajr_most(month_name[month])) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Zuhr':
			if (zuhr_least(month_name[month]) <= latest_salat_time < zuhr_most(month_name[month])) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Asr':
			if (asr_least(month_name[month]) <= latest_salat_time < asr_most(month_name[month])) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Maghrib':
			if (maghrib_least(month_name[month]) <= latest_salat_time < maghrib_most(month_name[month])) and latest_salat_date == now.date():
				return True
			else:
				return False
		elif prev_salat_name == 'Isha':
			# print isha_least(month_name[month])
			# print latest_salat_time
			# print isha_most(month_name[month])
			# print latest_salat_date
			# print now.date()
			# print now.date()-timedelta(days=1)
			if (isha_least(month_name[month]) <= latest_salat_time < isha_most(month_name[month])) and (latest_salat_date == now.date() or latest_salat_date == (now.date()-timedelta(days=1))):
				# print "True"
				return True
			else:
				return False
		else:
			return False