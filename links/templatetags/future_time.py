from django.template.defaulttags import register
import time

@register.filter(name='future_time')
def future_time(value):
	try:
		m, s = divmod(value, 60)
		if m:
			return "%s minutes baad" % int(m)
		elif s:
			return "%s seconds baad" % int(s)
	except:
		return "kuch minute baad"