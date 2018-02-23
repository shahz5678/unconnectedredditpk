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
	sub_header1 = 'Apko home ke rules break kartay huay pakra gaya hai'
	sub_header2 = 'Home Rules:'
	sub_header3 = '... aur last rule...'
	one = bold_head+'1) '+bold_tail
	two = bold_head+'2) '+bold_tail
	three = bold_head+'3) '+bold_tail
	four = bold_head+'4) '
	rule_one = 'Points barhaney ke liye home pe bar bar aik jesi baatien na likho'
	rule_two = 'Gandi baatoon aur galiyun se dur raho'
	rule_three = 'Kisi ko bila waja chupair na maro'
	rule_four = 'Boring hona mana hai.'+bold_tail+' Dil khol ke mazedar gup shup, jokes, shairi aur news share karo ;-)'
	button_text = bold_head+'OK'+bold_tail
	#################################################
	return outer_div_head+header+line_break+inner_div_1+sub_header1+line_break+div_tail+line+\
	inner_div_2+bold_colored+sub_header2+bold_tail+line_break+div_tail+one+rule_one+line_break+\
	two+rule_two+line_break+three+rule_three+line_break+inner_div_2+bold_colored+sub_header3+\
	bold_tail+line_break+div_tail+four+rule_four+line_break+a_href_head+button_head+button_text+\
	button_tail+a_href_tail+div_tail


def pinkstar_formatting(pinkstar):
	if pinkstar:
		return '<img src="/static/img/pstar.png" alt="*" width="13" height="13"></img>'
	else:
		return '<span></span>'

def category_formatting(categ):
	if categ == '1':
		#tyical home link
		div_head = '<span></span>'
	elif categ == '2':
		#public mehfil creation announcement on home
		div_head = '<div style="background-color:#F5E8ED;padding-top:1em;padding-bottom:1em" >'
	elif categ == '3':
		#Karachi Kings
		div_head = '<div class="mbs cs" style="background-color:#2857D0;color:#BFCDF3;padding:0.3em;border-radius:4px;letter-spacing: 1px">Karachi Kings fan</div>'
	elif categ == '4':
		#Peshawar Zalmi
		div_head = '<div class="mbs cs" style="background-color:#FCEE0A;color:#979002;padding:0.3em;border-radius:4px;letter-spacing: 1px">Peshawar Zalmi fan</div>'
	elif categ == '5':
		#Lahore Qalandars
		div_head = '<div class="mbs cs" style="background-color:#8AE44F;color:#366E11;padding:0.3em;border-radius:4px;letter-spacing: 1px">Lahore Qalandars fan</div>'
	elif categ == '6':
		#Photo sharing
		div_head = '<span></span>'
	elif categ == '7':
		#Quetta Glads
		div_head = '<div class="mbs cs" style="background-color:#54348A;color:#C6B5E3;padding:0.3em;border-radius:4px;letter-spacing: 1px">Quetta Gladiators fan</div>'
	elif categ == '8':
		#Islamabad United
		div_head = '<div class="mbs cs" style="background-color:#EE3000;color:#FFD6CC;padding:0.3em;border-radius:4px;letter-spacing: 1px">Islamabad United fan</div>'
	elif categ == '9':
		#misc
		div_head = '<div class="mbs cs" style="background-color:#40BEFC;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Cricket commentator</div>'
	elif categ == '10':
		#New Zealand
		div_head = '<div class="mbs cs" style="background-color:#404040;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">New Zealand fan</div>'
	elif categ == '11':
		# South Africa
		div_head = '<div class="mbs cs" style="background-color:#006663;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">South African fan</div>'
	elif categ == '12':
		# Pakistan
		div_head = '<div class="mbs cs" style="background-color:#00C354;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Pakistan fan</div>'
	elif categ == '13':
		# West Indies
		div_head = '<div class="mbs cs" style="background-color:#AE2D39;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">West Indies fan</div>'
	elif categ == '14':
		# India
		div_head = '<div class="mbs cs" style="background-color:#1F92D6;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Indian fan</div>'
	elif categ == '15':
		# Sri Lanka
		div_head = '<div class="mbs cs" style="background-color:#003366;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Sri Lankan fan</div>'
	elif categ == '16':
		# England
		div_head = '<div class="mbs cs" style="background-color:#1C16C1;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">England fan</div>'
	elif categ == '17':
		# urdu home link
		div_head = '<span></span>'
	elif categ == '18':
		# World-XI
		div_head = '<div class="mbs cs" style="background-color:#5A00B2;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">World XI fan</div>'
	elif categ == '19':
		#Multan Sultans
		div_head = '<div class="mbs cs" style="background-color:#525045;color:#D1CFC7;padding:0.3em;border-radius:4px;letter-spacing: 1px">Multan Sultans fan</div>'
	elif categ == '20':
		#Australia
		div_head = '<div class="mbs cs" style="background-color:#FFFF4D;color:#808000;padding:0.3em;border-radius:4px;letter-spacing: 1px">Australian supporter</div>'
	else:
		div_head = '<span></span>'
	return div_head, '</div>'


def device_formatting(device):
	if device == '1':
		device = '&nbsp;<img src="/static/img/featurephone.png" alt="pic" width="7" height="12">'
	elif device == '2':
		device = '&nbsp;<img src="/static/img/smartphone.png" alt="pic" width="7" height="12">'
	elif device == '3':
		device = '&nbsp;<img src="/static/img/laptop.png" alt="pic" width="17" height="13">'
	elif device == '4':
		device = '&nbsp;<img src="/static/img/tablet.png" alt="pic" width="14" height="11">'
	elif device == '5':
		device = '&nbsp;<img src="/static/img/other.png" alt="pic" width="7" height="12">'
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

def av_url_formatting(av_url, style=None, categ=None):
	url = None
	if av_url:
		if 'avatars' in av_url:
			url = "//s3.eu-central-1.amazonaws.com/damadam/thumbnails/"+av_url.split("avatars/")[1]
		else:
			url = av_url
	if url:
		if style == 'round':
			return '<img src="{}" style="border-radius:50%;border: 1px solid lightgrey;" width="22" height="22"/>'.format(url)
		else:
			if categ == '6':
				return '<button class="mbs" alt="no avatar" style="background-image: url({});border-radius:0px;background-repeat: no-repeat;background-position: center;width:24px;height:24px;border: 1px solid #A9A9A9;">&nbsp;</button>'.format(url)
			else:
				return '<img src="{}" style="border: 1px solid lightgrey" width="22" height="22"/>'.format(url)
	else:
		if style == 'round':
			return '<img src="/static/img/default-avatar-min.jpg" alt="no pic" style="border-radius:50%;border: 1px solid lightgrey;" width="22" height="22"/>'
		else:
			if categ == '6':
				return '<button class="mbs" alt="no avatar" style="background-image: url(/static/img/default-avatar-min.jpg);border-radius:0px;background-repeat: no-repeat;background-position: center;width:24px;height:24px;border:1px solid #E0E0E0;">&nbsp;</button>'
			else:
				return '<img src="/static/img/default-avatar-min.jpg" alt="no pic" style="border:1px solid lightgrey;" width="22" height="22"/>'