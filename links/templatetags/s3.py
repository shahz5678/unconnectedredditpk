from django.contrib.staticfiles.templatetags.staticfiles import static
from django import template
import string

register = template.Library()

bucket_addr = '//s3.ap-southeast-1.amazonaws.com/damadam-2019/'

@register.filter(name='s3')
def get_s3_object(filename,category='img'):
	if not filename:
		if category == 'thumb':
			return static('img/default-avatar-min.jpg')
		else:
			return static('img/broken.svg')
	else:
		filename = str(filename)
		if filename == 'empty':
			if category == 'thumb':
				return static('img/default-avatar-min.jpg')
			else:
				return static('img/broken.svg')
		elif "photos/" in filename:
			split_by = "photos/"
		elif "personal_groups/" in filename:
			split_by = "personal_groups/"
		elif "avatars/" in filename:
			split_by = "avatars/"
		elif "mehfils/" in filename:
			split_by = "mehfils/"
		elif "users/" in filename:
			split_by = "users/"
		else:
			split_by = "photos/"
		######################################################
		if category=='thumb':
			try:
				return bucket_addr+"thumbnails/"+filename.split(split_by)[1]
			except IndexError:
				return static('img/default-avatar-min.jpg')
		else:
			try:
				return bucket_addr+split_by+filename.split(split_by)[1]
			except IndexError:
				return static('img/broken.svg')