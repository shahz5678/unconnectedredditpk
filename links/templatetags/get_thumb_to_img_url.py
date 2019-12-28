from django import template
from unconnectedreddit.env import NEW_BUCKET_ADDR, BUCKET_ADDR

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
		name = filename[-40:]
		if "thumbnail/follower/" in filename:
			return NEW_BUCKET_ADDR+"follower/"+name
		elif "thumb/public/" in filename:
			return BUCKET_ADDR+"public/"+name
		############################################
		################# Legacy ###################
		############################################
		elif "thumbnails/" in filename:
			return BUCKET_ADDR+"photos/"+name