import string

def pinkstar_formatting(pinkstar):
	if pinkstar:
		return '<img src="/static/img/pstar.png" alt="*" width="13" height="13"></img>'
	else:
		return '<span></span>'

def category_formatting(categ):
	if categ == '1':
		#tyical home link
		div_head = '<span></span>'
		div_tail = '<p><hr size=1 COLOR="#3cb7dd"></p>'
	elif categ == '2':
		#public mehfil creation announcement on home
		div_head = '<div style="background-color:#faebeb;margin-top:-1em;padding-top:1em;" >'
		div_tail = '<p><hr size=1 COLOR="#ac39ac"></p></div>'
	elif categ == '3':
		#Karachi Kings
		div_head = '<div style="background-color:#e9eefc;"><h1 style="font-size:0.7em;background-color:#244ed8;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Karachi Kings</h1>'
		div_tail = '<p><hr size=1 COLOR="#244ed8"></p></div>'
	elif categ == '4':
		#Peshawar Zalmi
		div_head = '<div style="background-color:#fbf8ea;"><h1 style="font-size:0.7em;background-color:#ddcc5e;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Peshawar Zalmi</h1>'
		div_tail = '<p><hr size=1 COLOR="#ddcc5e"></p></div>'
	elif categ == '5':
		#Lahore Qalandars
		div_head = '<div style="background-color:#e6ffe6;"><h1 style="font-size:0.7em;background-color:#00e600;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Lahore Qalandars</h1>'
		div_tail = '<p><hr size=1 COLOR="#00e600"></p></div>'
	elif categ == '6':
		#Photo sharing
		div_head = '<span></span>'
		div_tail = '<p><hr size=1 COLOR="#ff9933"></p>'
	elif categ == '7':
		#Quetta Glads
		div_head = '<div style="background-color:#f5edf8;"><h1 style="font-size:0.7em;background-color:#9040a8;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Quetta Gladiators</h1>'
		div_tail = '<p><hr size=1 COLOR="#9040a8"></p></div>'
	elif categ == '8':
		#Islamabad United
		div_head = '<div style="background-color:#ffece6;"><h1 style="font-size:0.7em;background-color:#ff4500;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Islamabad United</h1>'
		div_tail = '<p><hr size=1 COLOR="#ec544f"></p></div>'
	elif categ == '9':
		#misc
		div_head = '<div style="background-color:#e7f2fe;"><h1 style="font-size:0.7em;background-color:#59A5F5;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Cricket</h1>'
		div_tail = '<p><hr size=1 COLOR="#59A5F5"></p></div>'
	elif categ == '10':
		#New Zealand
		div_head = '<div style="background-color:#f2f2f2;"><h1 style="font-size:0.7em;background-color:#404040;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">New Zealand</h1>'
		div_tail = '<p><hr size=1 COLOR="#404040"></p></div>'
	elif categ == '11':
		# South Africa
		div_head = '<div style="background-color:#fbf8ea;"><h1 style="font-size:0.7em;background-color:#ddcc5e;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">South Africa</h1>'
		div_tail = '<p><hr size=1 COLOR="#ddcc5e"></p></div>'
	else:
		div_head = '<span></span>'
		div_tail = '<span></span>'
	return div_head, div_tail

def device_formatting(device):
	if device == '1':
		device = '&nbsp;<img src="/static/img/featurephone.png" alt="pic" width="7" height="12"></img>'
	elif device == '2':
		device = '&nbsp;<img src="/static/img/smartphone.png" alt="pic" width="7" height="12"></img>'
	elif device == '3':
		device = '&nbsp;<img src="/static/img/laptop.png" alt="pic" width="17" height="13"></img>'
	elif device == '4':
		device = '&nbsp;<img src="/static/img/tablet.png" alt="pic" width="14" height="11"></img>'
	elif device == '5':
		device = '&nbsp;<img src="/static/img/other.png" alt="pic" width="7" height="12"></img>'
	else:
		device = None
	return device

def scr_formatting(score):
	style_tag = '<span style="font-size:85%;" class="cg">'
	if score < 1:
		score = style_tag + "(1)" + '</span>'
	else:
		score = style_tag + "(" + str(score) + ")" + '</span>'
	return score

def username_formatting(username,is_pinkstar,size,is_bold):
	username = username.decode('utf-8')
	if size == 'small':
		a_href = "<a style='font-size:80%;' "+ ("href='/user/%s'>" % username)
		if is_bold:
			username = a_href+"<b>"+username+"</b></a>"
		else:
			username = a_href+username+"</a>"
	elif size == 'medium':
		a_href = ("<a href='/user/%s'>" % username)
		if is_bold:
			username = a_href+"<b>"+username+"</b></a>"
		else:
			username = a_href+username+"</a>"
	if is_pinkstar:
		username = '<bdi>'+username+'</bdi>'+'<img src="/static/img/pstar_small.png" alt="*" width="9" height="9"></img>'
	else:
		username = '<bdi>'+username+'</bdi>'
	return username

def av_url_formatting(av_url):
	if av_url:
		if 'res/avatars' in av_url:
			url = string.replace(av_url, "damadam.blob.core.windows.net/pictures/avatars", "damadamthumbs.azureedge.net")
		else:
			url = av_url
		return '<img src="%s" width="22" height="22"></img>' % url
	else:
		return '<img src="/static/img/default-avatar-min.jpg" alt="no pic"  width="22" height="22"></img>'

# def comment_count_formatting(comment_count, link_id):
# 	form_head = '<form method="POST" action="/link/%s/" style="display:inline;">' % link_id
# 	csrf = '{%% csrf_token %}'
# 	form_tail = '</form>'
# 	button_head = '<button class="btn nw bl mbs mts" type="submit" style="color:#229ec3;background-color:#F8F8F8;border-color:#B8B8B8;">'
# 	button_tail = '</button>'
# 	# a_href_head = '<a href="/link/%s/">' % link_id
# 	# a_href_tail = '</a>'
# 	if comment_count > 0:
# 		button = form_head+csrf+button_head+'<b>'+str(comment_count)+'</b>&nbsp;&nbsp;jawab'+button_tail+form_tail
# 		# button = '&nbsp;&nbsp;'+a_href_head+button_head+'<b>'+str(comment_count)+'</b>&nbsp;&nbsp;jawab'+button_tail+a_href_tail
# 	else:
# 		button = ''
# 	return button