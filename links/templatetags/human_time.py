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
	mo, d = divmod(d, 30)
	if mo:
		if int(mo) == 1:
			return "%s month ago" % int(mo)
		else:
			return "%s months ago" % int(mo)
	elif d:
		if int(d) == 1:
			return "%s day ago" % int(d)
		else:
			return "%s days ago" % int(d)
	elif h:
		if int(h) == 1:
			return "%s hour ago" % int(h)
		else:
			return "%s hours ago" % int(h)
	elif m:
		if int(m) == 1:
			return "%s min ago" % int(m)
		else:
			return "%s mins ago" % int(m)
	elif s:
		if int(s) == 1:
			return "%s sec ago" % int(s)
		else:
			return "%s secs ago" % int(s)