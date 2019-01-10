from django.contrib.staticfiles.templatetags.staticfiles import static
from django import template

register = template.Library()

@register.filter(name='thumb_to_img')
def thumb_to_img(filename):
	"""
	Doing the reverse of what the s3 template tag does
	"""
	if not filename or filename == 'empty':
		return ''
	else:
		filename = str(filename)
		split_by = "thumbnails/"
		######################################################
		try:
			return "//s3.eu-central-1.amazonaws.com/damadam/photos/"+filename.split(split_by)[1]
		except IndexError:
			return static('img/default-avatar-min.jpg')