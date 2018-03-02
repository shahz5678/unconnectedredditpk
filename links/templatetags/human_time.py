from django.template.defaulttags import register
import time

@register.filter(name='human_time')
def human_time(value):
	try:
		diff = time.time() - float(value)
	except (ValueError,TypeError):
		return ''
	m, s = divmod(diff, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	mo, d = divmod(d, 30)
	if mo:
		if int(mo) == 1:
			return "1 month ago"
		else:
			return "%s months ago" % int(mo)
	elif d:
		if int(d) == 1:
			return "1 day ago"
		else:
			return "%s days ago" % int(d)
	elif h:
		if int(h) == 1:
			return "1 hour ago"
		else:
			return "%s hours ago" % int(h)
	elif m:
		if int(m) == 1:
			return "1 min ago"
		else:
			return "%s mins ago" % int(m)
	elif s:
		if int(s) == 0:
			return "abhi"
		elif int(s) == 1:
			return "1 sec ago"
		else:
			return "%s secs ago" % int(s)
	else:
		return ''