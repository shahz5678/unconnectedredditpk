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
	if h:
		return "%s hours ago" % int(h)
	elif m:
		return "%s minutes ago" % int(m)
	elif s:
		return "%s seconds ago" % int(s)