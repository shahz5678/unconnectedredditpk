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
			mo = int(mo)
			if mo == 1:
				return "1 month baad"
			else:
				return "%s months baad" % mo
		elif d:
			d = int(d)
			if d == 1:
				return "1 day baad"
			else:
				return "%s days baad" % d
		elif h:
			h = int(h)
			if h == 1:
				return "1 hour baad"
			else:
				return "%s hours baad" % h
		elif m:
			m = int(m)
			if m == 1:
				return "1 min baad"
			else:
				return "%s mins baad" % m
		elif s:
			s = int(s)
			if s == 1:
				return "1 sec baad"
			else:
				return "%s secs baad" % s
		else:
			return "kuch waqt baad"
	except (NameError,TypeError):
		return "kuch waqt baad"