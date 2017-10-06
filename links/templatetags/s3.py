from django import template
import string

register = template.Library()

@register.filter(name='s3')
def get_s3_object(filename,category='image'):
	filename = str(filename)
	if "photos/" in filename:
		split_by = "photos/"
	elif "avatars/" in filename:
		split_by = "avatars/"
	elif "mehfils/" in filename:
		split_by = "mehfils/"
	elif "users/" in filename:
		split_by = "users/"
	else:
		split_by = "photos/"
	if category=='thumb':
		return "//s3.eu-central-1.amazonaws.com/damadam/thumbnails/"+filename.split(split_by)[1]
	else:
		return "//s3.eu-central-1.amazonaws.com/damadam/"+split_by+filename.split(split_by)[1]