from django.template.defaulttags import register
import time

@register.filter(name='future_time')
def future_time(value):
	try:
		m, s = divmod(value, 60)
		if m:
			return "%s min baad" % int(m)
		elif s:
			return "%s secs baad" % int(s)
	except:
		return "kuch waqt baad"