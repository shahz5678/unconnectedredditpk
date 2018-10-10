from django.template.defaulttags import register
import time

@register.filter(name='time_string')
def time_string(value,result=None):
	try:
		diff = time.time() - float(value)
	except (ValueError,TypeError):
		return ''
	m, s = divmod(diff, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)
	w, d = divmod(d, 7)
	mo, w = divmod(w, 4)
	if result == 'abbreviated':
		# abbreviate the result
		if mo:
			if int(mo) == 1:
				return "1 mo"
			else:
				return "%s mos" % int(mo)
		elif w:
			if int(w) == 1:
				return "1 wk"
			else:
				return "%s wks" % int(w)
		elif d:
			if int(d) == 1:
				return "1 day"
			else:
				return "%s days" % int(d)
		elif h:
			if int(h) == 1:
				return "1 hr"
			else:
				return "%s hrs" % int(h)
		elif m:
			if int(m) == 1:
				return "1 min"
			else:
				return "%s mins" % int(m)
		elif s:
			if int(s) == 0:
				return "abhi"
			elif int(s) == 1:
				return "1 sec"
			else:
				return "%s secs" % int(s)
		else:
			return ''
	else:
		if mo:
			if int(mo) == 1:
				return "1 month"
			else:
				return "%s months" % int(mo)
		elif w:
			if int(w) == 1:
				return "1 week"
			else:
				return "%s weeks" % int(w)
		elif d:
			if int(d) == 1:
				return "1 day"
			else:
				return "%s days" % int(d)
		elif h:
			if int(h) == 1:
				return "1 hour"
			else:
				return "%s hours" % int(h)
		elif m:
			if int(m) == 1:
				return "1 min"
			else:
				return "%s mins" % int(m)
		elif s:
			if int(s) == 0:
				return "abhi"
			elif int(s) == 1:
				return "1 sec"
			else:
				return "%s secs" % int(s)
		else:
			return ''