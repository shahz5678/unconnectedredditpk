from django.template.defaulttags import register
import time

@register.filter(name='human_time')
def human_time(value,result=None):
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
				return "1 mo ago"
			else:
				return "%s mos ago" % int(mo)
		elif w:
			if int(w) == 1:
				return "1 wk ago"
			else:
				return "%s wks ago" % int(w)
		elif d:
			if int(d) == 1:
				return "1 day ago"
			else:
				return "%s days ago" % int(d)
		elif h:
			if int(h) == 1:
				return "1 hr ago"
			else:
				return "%s hrs ago" % int(h)
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
	else:
		if mo:
			if int(mo) == 1:
				return "1 month ago"
			else:
				return "%s months ago" % int(mo)
		elif w:
			if int(w) == 1:
				return "1 week ago"
			else:
				return "%s weeks ago" % int(w)
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