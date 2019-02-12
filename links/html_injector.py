import string

# def create_gibberish_punishment_text(amount):
# 	outer_div_head = '<div style="background-color:#0091ea;color:white;padding:5px 5px 5px 5px;border-radius:4px;">'
# 	inner_div_1 = '<div class="mts mbs">'
# 	inner_div_2 = '<div class="mts mbs cl">'
# 	div_tail = '</div>'
# 	line = '<hr size=1 COLOR="#ffeb3b">'
# 	span_colored = '<span style="color:#ffeb3b;">'
# 	span_tail = '</span>'
# 	bold_head = '<b>'
# 	bold_cxl = '<b class="cxl">'
# 	bold_colored = '<b style="color:#ffeb3b;">'
# 	bold_tail = '</b>'
# 	line_break = '<br>'
# 	button_head = '<button class="btn bco mbl mtl bm">'
# 	button_tail = '</button>'
# 	a_href_head = "<a href='/rhr/'>"
# 	a_href_tail = '</a>'
# 	#################################################
# 	header = bold_cxl+'Ap ke '+span_colored+str(amount)+' points'+span_tail+' cut gaye!'+bold_tail
# 	sub_header1 = 'Apko home ke rules break kartay huay pakra gaya hai'
# 	sub_header2 = 'Home Rules:'
# 	sub_header3 = '... aur last rule...'
# 	one = bold_head+'1) '+bold_tail
# 	two = bold_head+'2) '+bold_tail
# 	three = bold_head+'3) '+bold_tail
# 	four = bold_head+'4) '
# 	rule_one = 'Points barhaney ke liye home pe bar bar aik jesi baatien na share karein'
# 	rule_two = 'Gandi baatoon aur galiyun se dur rahein'
# 	rule_three = 'Kisi ko bila waja chupair na marein'
# 	rule_four = 'Boring hona mana hai.'+bold_tail+' Dil khol ke mazedar news, funny SMS, shairi aur fotos share karein ;-)'
# 	button_text = bold_head+'OK'+bold_tail
# 	#################################################
# 	return outer_div_head+header+line_break+inner_div_1+sub_header1+line_break+div_tail+line+\
# 	inner_div_2+bold_colored+sub_header2+bold_tail+line_break+div_tail+one+rule_one+line_break+\
# 	two+rule_two+line_break+three+rule_three+line_break+inner_div_2+bold_colored+sub_header3+\
# 	bold_tail+line_break+div_tail+four+rule_four+line_break+a_href_head+button_head+button_text+\
# 	button_tail+a_href_tail+div_tail


# def pinkstar_formatting(pinkstar):
# 	"""
# 	Provide a pre-formatted pink star image that can be used with |safe in templates
# 	"""
# 	if pinkstar:
# 		return '<img src="/static/img/pstar.svg" alt="*" height="13" width="13">'
# 	else:
# 		return ''

def category_formatting(categ):
	if categ == '1':
		#tyical home link
		div_head = '<span></span>'
		div_tail = ''
	elif categ == '2':
		#public mehfil creation announcement on home
		div_head = '<span></span>'
		div_tail = ''
	elif categ == '3':
		#Karachi Kings
		div_head = '<div class="mbs cs" style="background-color:#2857D0;color:#BFCDF3;padding:0.3em;border-radius:4px;letter-spacing: 1px">Karachi Kings fan</div>'
		div_tail = ''
	elif categ == '4':
		#Peshawar Zalmi
		div_head = '<div class="mbs cs" style="background-color:#FCEE0A;color:#979002;padding:0.3em;border-radius:4px;letter-spacing: 1px">Peshawar Zalmi fan</div>'
		div_tail = ''
	elif categ == '5':
		#Lahore Qalandars
		div_head = '<div class="mbs cs" style="background-color:#8AE44F;color:#366E11;padding:0.3em;border-radius:4px;letter-spacing: 1px">Lahore Qalandars fan</div>'
		div_tail = ''
	elif categ == '6':
		#Photo sharing
		div_head = '<span></span>'
		div_tail = ''
	elif categ == '7':
		#Quetta Glads
		div_head = '<div class="mbs cs" style="background-color:#54348A;color:#C6B5E3;padding:0.3em;border-radius:4px;letter-spacing: 1px">Quetta Gladiators fan</div>'
		div_tail = ''
	elif categ == '8':
		#Islamabad United
		div_head = '<div class="mbs cs" style="background-color:#EE3000;color:#FFD6CC;padding:0.3em;border-radius:4px;letter-spacing: 1px">Islamabad United fan</div>'
		div_tail = ''
	elif categ == '9':
		#misc
		div_head = '<div class="mbs cs" style="background-color:#40BEFC;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Cricket commentator</div>'
		div_tail = ''
	elif categ == '10':
		#New Zealand
		div_head = '<div class="mbs cs" style="background-color:#404040;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">New Zealand fan</div>'
		div_tail = ''
	elif categ == '11':
		# South Africa
		div_head = '<div class="mbs cs" style="background-color:#006663;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">South African fan</div>'
		div_tail = ''
	elif categ == '12':
		# Pakistan
		div_head = '<div class="mbs cs" style="background-color:#00C354;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Pakistan fan</div>'
		div_tail = ''
	elif categ == '13':
		# West Indies
		div_head = '<div class="mbs cs" style="background-color:#AE2D39;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">West Indies fan</div>'
		div_tail = ''
	elif categ == '14':
		# India
		div_head = '<div class="mbs cs" style="background-color:#1F92D6;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Indian fan</div>'
		div_tail = ''
	elif categ == '15':
		# Sri Lanka
		div_head = '<div class="mbs cs" style="background-color:#003366;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">Sri Lankan fan</div>'
		div_tail = ''
	elif categ == '16':
		# England
		div_head = '<div class="mbs cs" style="background-color:#1C16C1;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">England fan</div>'
		div_tail = ''
	elif categ == '17':
		# urdu home link
		div_head = '<span></span>'
		div_tail = ''
	elif categ == '18':
		# World-XI
		div_head = '<div class="mbs cs" style="background-color:#5A00B2;color:white;padding:0.3em;border-radius:4px;letter-spacing: 1px">World XI fan</div>'
		div_tail = ''
	elif categ == '19':
		#Multan Sultans
		div_head = '<div class="mbs cs" style="background-color:#525045;color:#D1CFC7;padding:0.3em;border-radius:4px;letter-spacing: 1px">Multan Sultans fan</div>'
		div_tail = ''
	elif categ == '20':
		#Australia
		div_head = '<div class="mbs cs" style="background-color:#FFFF4D;color:#808000;padding:0.3em;border-radius:4px;letter-spacing: 1px">Australian supporter</div>'
		div_tail = ''
	else:
		div_head = '<span></span>'
		div_tail = ''
	return div_head, div_tail


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

# def scr_formatting(score):
# 	"""
# 	Provie a pre-formatted score string that can be used with |safe in templates
# 	"""
# 	if score:
# 		style_tag = '<span class="cxs sp cg">'
# 		if score < 1:
# 			score = style_tag + "(1)" + '</span>'
# 		else:
# 			score = style_tag + "(" + str(score) + ")" + '</span>'
# 		return score
# 	else:
# 		return ''

# def username_formatting(username,is_pinkstar,size,is_bold):
# 	username = username.decode('utf-8')
# 	if size == 'small':
# 		a_href = "<a style='font-size:80%;' "+ ("href='/user/%s'>" % username)
# 		if is_bold:
# 			username = a_href+"<b>"+username+"</b></a>"
# 		else:
# 			username = a_href+username+"</a>"
# 	elif size == 'medium':
# 		a_href = ("<a href='/user/%s'>" % username)
# 		if is_bold:
# 			username = a_href+"<b>"+username+"</b></a>"
# 		else:
# 			username = a_href+username+"</a>"
# 	if is_pinkstar:
# 		username = '<bdi>'+username+'</bdi>'+'<img src="/static/img/pstar.svg" alt="*" width="10" height="10">'
# 	else:
# 		username = '<bdi>'+username+'</bdi>'
# 	return username


def image_thumb_formatting(img_url,pid):
	"""
	Created a string blob of a provided image url

	The result is used in displaying image thumbs at various parts of the website
	"""
	return '<button class="mls mbs" style="background-color:transparent;outline:none;overflow: hidden;padding:0px;border:none;" type="submit" name="pid" value="%s"><img src="%s" style="border-radius:4px" height="38"></button>' \
	% (pid,img_url)


def av_url_formatting(av_url, style=None, categ=None, pub_rep=False):
	url = None
	if av_url:
		if 'avatars' in av_url:
			url = "//s3.eu-central-1.amazonaws.com/damadam/thumbnails/"+av_url.split("avatars/")[1]
		else:
			url = av_url
	if url:
		if style == 'round':
			if pub_rep:
				# is a public reply
				return '<img src="{}" style="border-radius:50%;border: 1px solid lightgray" width="22" height="22">'.format(url)
			else:
				# is a normal home post
				# print "\nnormal home post"
				return '<img src="{}" style="border: 1px solid lightgray;position:absolute;z-index:10;margin-left:-12px" class="tl_cnr av_btn" width="22" height="22">'.format(url)
		else:
			if categ == '6':
				# print "\ncateg 6 home post"
				return '<img src="{}" style="border: 1px solid lightgray;position:absolute;z-index:10;margin-left:-12px" class="tl_cnr av_btn" width="22" height="22">'.format(url)
			else:
				return '<img src="{}" style="border: 1px solid lightgray" width="22" height="22">'.format(url)
	else:
		if style == 'round':
			if pub_rep:
				# is a public reply
				return '<img src="/static/img/default-avatar-min.jpg" alt="pic" style="border-radius:50%;border: 1px solid lightgray" width="22" height="22">'
			else:
				# is a normal home post
				# print "\nnormal home post (no-avatar)"
				return '<img src="/static/img/default-avatar-min.jpg" alt="pic" style="position:absolute;border: 1px solid lightgray;z-index:10;margin-left:-12px" class="tl_cnr av_btn" width="22" height="22">'
		else:
			if categ == '6':
				# print "\ncateg 6 home post (no-avatar)"
				return '<img src="/static/img/default-avatar-min.jpg" alt="pic" style="position:absolute;border: 1px solid lightgray;z-index:10;margin-left:-12px" class="tl_cnr av_btn" width="22" height="22">'
			else:
				return '<img src="/static/img/default-avatar-min.jpg" alt="pic" style="border:1px solid lightgray" width="22" height="22">'