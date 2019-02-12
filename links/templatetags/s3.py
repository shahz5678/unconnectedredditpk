from django.contrib.staticfiles.templatetags.staticfiles import static
from django import template
from unconnectedreddit.env import BUCKET_ADDR
import string

# Legacy files are files stored in S3 before 13th Feb 2019
# Everything stored in S3 after (and on) 13th Feb 2019 is saved in folders called /1on1/, /mehfil/, /avatar/, /public/
# Everything stored in S3 before 13th Feb 2019 is saved in folders called /personal_group/, /mehfils/, /avatars/, /photos/

register = template.Library()

@register.filter(name='s3')
def get_s3_object(filename,category='img'):
	if not filename:
		if category == 'thumb':
			return static('img/default-avatar-min.jpg')
		else:
			return static('img/broken.svg')
	else:
		filename = str(filename)
		if category == 'thumb':
			# this is a thumbnail
			if filename == 'empty':
				return static('img/default-avatar-min.jpg')
			else:
				name = filename[-40:]
				if "1on1/" in filename:
					return BUCKET_ADDR+'thumb/1on1/'+name
				elif "mehfil/" in filename:
					return BUCKET_ADDR+'thumb/mehfil/'+name
				elif "avatar/" in filename:
					return BUCKET_ADDR+'thumb/avatar/'+name
				elif "public/" in filename:
					return BUCKET_ADDR+'thumb/public/'+name
				############################################
				################# Legacy ###################
				############################################
				elif "photos/" in filename:
					# print name
					return BUCKET_ADDR+"thumbnails/"+name
				elif "personal_groups/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				elif "avatars/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				elif "mehfils/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				elif "users/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				else:
					return BUCKET_ADDR+"thumbnails/"+name
				############################################
				############################################
				############################################
		else:
			# this is a full-sized image
			if filename == 'empty':
				return static('img/broken.svg')
			else:
				if "1on1/" in filename:
					return BUCKET_ADDR+filename
				elif "mehfil/" in filename:
					return BUCKET_ADDR+filename
				elif "avatar/" in filename:
					return BUCKET_ADDR+filename
				elif "public/" in filename:
					return BUCKET_ADDR+filename
				else:
					############################################
					################# Legacy ###################
					############################################
					name = filename[-40:]
					if "photos/" in filename:
						return BUCKET_ADDR+"photos/"+name
					elif "personal_groups/" in filename:
						return BUCKET_ADDR+"personal_groups/"+name
					elif "avatars/" in filename:
						return BUCKET_ADDR+"avatars/"+name
					elif "mehfils/" in filename:
						return BUCKET_ADDR+"mehfils/"+name
					elif "users/" in filename:
						return BUCKET_ADDR+"users/"+name
					else:
						return BUCKET_ADDR+"photos/"+name
					############################################
					############################################
					############################################