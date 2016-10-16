from django.template.defaulttags import register
#from django.utils import timezone
#from datetime import datetime, timedelta
#from django.utils.timesince import timesince
import time

@register.filter(name='human_time')
def human_time(value):
	#to_go = timezone.now()+timedelta(seconds=time_remaining)
	# now = datetime.now()
	try:
		diff = time.time() - float(value)
	except:
		return ''
	m, s = divmod(diff, 60)
	h, m = divmod(m, 60)
	if h:
		return "%s hours ago" % int(h)
	elif m:
		return "%s minutes ago" % int(m)
	elif s:
		return "%s seconds ago" % int(s)