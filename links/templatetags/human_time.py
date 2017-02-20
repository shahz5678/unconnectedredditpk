from django.template.defaulttags import register
import time

@register.filter(name='human_time')
def human_time(value):
	try:
		diff = time.time() - float(value)
	except:
		return ''
	m, s = divmod(diff, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	if d:
		return "%s days ago" % int(d)
	elif h:
		return "%s hours ago" % int(h)
	elif m:
		return "%s mins ago" % int(m)
	elif s:
		return "%s secs ago" % int(s)