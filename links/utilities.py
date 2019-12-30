# coding=utf-8
import time
from pytz import timezone
from datetime import datetime


def beautiful_date(epoch_time, format_type='1'):
	"""
	Provides human readable date, beautilfully formatted

	Format type is:

	i) '10:23 AM - 30 Nov 2015'
	"""
	if format_type == '1':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%a %I:%M %p - %d %b")# gives "Sun 03:39 PM - 05 May"
	elif format_type == '2':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%Y-%m-%d %I:%M:%S %p")# gives YYYY-MM-DDThh:mm:ssTZD
	elif format_type == '3':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%I:%M %p, %a - %d %b %Y")# gives "03:39 PM, Sun - 05 May 2019"
	elif format_type == '4':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%Y-%m-%dT%H:%M:%S+05:00")# gives YYYY-MM-DDThh:mm:ss+05:00 format
	elif format_type == '5':
		return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_time))
	elif format_type == '6':
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%Y-%m-%d %H:%M:%S")# gives calendar time format
	else:
		return datetime.fromtimestamp(epoch_time, tz=timezone('Asia/Karachi')).strftime("%I:%M %p %d-%m-%Y")# gives "05-05-2019 03:39 PM"


def convert_to_epoch(time):
	"""
	Converts a datetime obj to epoch time
	"""
	return (time-datetime(1970,1,1)).total_seconds()