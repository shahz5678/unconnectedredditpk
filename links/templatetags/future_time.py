from django.template.defaulttags import register
import time

@register.filter(name='future_time')
def future_time(value):
	try:
		m, s = divmod(value, 60)
		h, m = divmod(m, 60)
		d, h = divmod(h, 24)
		mo, d = divmod(d, 30)
		if mo:
			return "%s month(s) baad" % int(mo)
		elif d:
			return "%s days baad" % int(d)
		elif h:
			return "%s hours baad" % int(h)
		elif m:
			return "%s mins baad" % int(m)
		elif s:
			return "%s secs baad" % int(s)
		else:
			return "kuch waqt baad"
	except:
		return "kuch waqt baad"