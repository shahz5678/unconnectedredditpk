from django.template.defaulttags import register
import time

@register.filter(name='future_time')
def future_time(value):
	m, s = divmod(value, 60)
	h, m = divmod(m, 60)
	if h:
		return "%s hours baad" % int(h)
	elif m:
		return "%s minutes baad" % int(m)
	elif s:
		return "%s seconds baad" % int(s)