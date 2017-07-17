import string

def create_gibberish_punishment_text(amount):
	outer_div_head = '<div style="background-color:#0091ea;color:white;padding:5px 5px 5px 5px;border-radius:4px;">'
	inner_div_1 = '<div class="mts mbs">'
	inner_div_2 = '<div class="mts mbs cl">'
	div_tail = '</div>'
	line = '<hr size=1 COLOR="#ffeb3b">'
	span_colored = '<span style="color:#ffeb3b;">'
	span_tail = '</span>'
	bold_head = '<b>'
	bold_cxl = '<b class="cxl">'
	bold_colored = '<b style="color:#ffeb3b;">'
	bold_tail = '</b>'
	line_break = '<br>'
	button_head = '<button class="btn bco mbl mtl bm">'
	button_tail = '</button>'
	a_href_head = "<a href='/rhr/'>"
	a_href_tail = '</a>'
	#################################################
	header = bold_cxl+'Ap ke '+span_colored+str(amount)+' points'+span_tail+' cut gaye!'+bold_tail
	sub_header1 = 'Ap ko home ke rules break kartay huay report kiya gaya.'
	sub_header2 = 'Home Rules:'
	sub_header3 = '... aur last rule...'
	one = bold_head+'1) '+bold_tail
	two = bold_head+'2) '+bold_tail
	three = bold_head+'3) '+bold_tail
	four = bold_head+'4) '
	rule_one = 'Points barhaney ke liye home ka najaiz istimal na karein'
	rule_two = 'Gandi baatoon aur galiyun se dur rehain'
	rule_three = 'Kisi ko bila waja chupair na marein'
	rule_four = 'Boring hona mana hai.'+bold_tail+' Dil khol ke mazedar gup shup, jokes, shairi aur news share karein ;-)'
	button_text = bold_head+'OK'+bold_tail
	#################################################
	return outer_div_head+header+line_break+inner_div_1+sub_header1+line_break+div_tail+line+\
	inner_div_2+bold_colored+sub_header2+bold_tail+line_break+div_tail+one+rule_one+line_break+\
	two+rule_two+line_break+three+rule_three+line_break+inner_div_2+bold_colored+sub_header3+\
	bold_tail+line_break+div_tail+four+rule_four+line_break+a_href_head+button_head+button_text+\
	button_tail+a_href_tail+div_tail


# <div style="background-color:#0091ea;color:white;padding:5px 5px 5px 5px;border-radius:4px;">
# <b class="cxl">Ap ke <span style="color:#ffeb3b;">12 points</span> cut ho gaye!</b>
# <br>
# 	<div class="mts mbs">
# 	Ap ko home ke rules break kartay huay report kiya gaya.<br>
# 	</div>
# <hr size=1 COLOR="#ffeb3b">
# <div class="mts mbs cl">
# <b style="color:#ffeb3b;">Home Rules:</b><br>
# </div>
# <b>1)</b> Points barhaney ke liye home ka najaiz istimal nah karein<br>
# <b>2)</b> Gandi baatoon aur galiyun se dur rehain<br>
# <b>3)</b> Kisi ko bila waja chupair na marien<br>
# <div class="mts mbs cl">
# <b style="color:#ffeb3b;">... aur last rule...</b><br>
# </div>
# <b>4) Boring hona mana hai.</b> Dil khol ke mazedar gup shup, lateefay, shairi aur khabrein sunaien!<br>
# <a href="{% url 'retire_home_rules' %}"><button class="btn bco mbl mtl bm"><b>OK</b></button></a>
# </div>

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
	elif categ == '12':
		# Pakistan
		div_head = '<div style="background-color:#e6ffe6;"><h1 style="font-size:0.7em;background-color:#008000;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Pakistan</h1>'
		div_tail = '<p><hr size=1 COLOR="#008000"></p></div>'
	elif categ == '13':
		# West Indies
		div_head = '<div style="background-color:#ffe6e6;"><h1 style="font-size:0.7em;background-color:#990000;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">West Indies</h1>'
		div_tail = '<p><hr size=1 COLOR="#990000"></p></div>'
	elif categ == '14':
		# India
		div_head = '<div style="background-color:#e8f7fd;"><h1 style="font-size:0.7em;background-color:#1293CC;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">India</h1>'
		div_tail = '<p><hr size=1 COLOR="#1293CC"></p></div>'
	elif categ == '15':
		# Sri Lanka
		div_head = '<div style="background-color:#ebf2fa;"><h1 style="font-size:0.7em;background-color:#26548B;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">Sri Lanka</h1>'
		div_tail = '<p><hr size=1 COLOR="#26548B"></p></div>'
	elif categ == '16':
		# England
		div_head = '<div style="background-color:#e6e6ff;"><h1 style="font-size:0.7em;background-color:#020277;color:white;margin-top:-1.5em;padding-top:0.3em;padding-left:0.3em;padding-bottom:0.3em;">England</h1>'
		div_tail = '<p><hr size=1 COLOR="#020277"></p></div>'
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

def image_thumb_formatting(img_url,pid):
	return '<button class="mls mbs" style="border-radius:0px;background-color:transparent;outline:none;overflow: hidden;padding:0px;border:none;" type="submit" name="pid" value="%s"><img src="%s" height="38"></button>' \
	% (pid,img_url)

def av_url_formatting(av_url):
	if av_url:
		if 'res/avatars' in av_url:
			url = string.replace(av_url, "damadam.blob.core.windows.net/pictures/avatars", "damadamthumbs.azureedge.net")
		else:
			url = av_url
		return '<img src="%s" width="22" height="22"></img>' % url
	else:
		return '<img src="/static/img/default-avatar-min.jpg" alt="no pic"  width="22" height="22"></img>'

# def contacter_string(phone_number):
# 	return '<span class="cg"><b>%s</b> ne tumhara mobile number hasil kiya</span><br>' % phone_number
