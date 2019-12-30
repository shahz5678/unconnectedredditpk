from django.contrib.staticfiles.templatetags.staticfiles import static
from django import template
from unconnectedreddit.env import BUCKET_ADDR, NEW_BUCKET_ADDR
import string

# New: Everything stored in S3 after (and on) 27th Dec 2019 is saved in folders called /1-on-1/, /groups/, /dp/, /shared/

# Legacy files are files stored in S3 before 27th Dec 2019:
# Legacy 1: Everything stored in S3 after (and on) 13th Feb 2019 is saved in folders called /1on1/, /mehfil/, /avatar/, /public/
# Legacy 2: Everything stored in S3 before 13th Feb 2019 is saved in folders called /personal_group/, /mehfils/, /avatars/, /photos/

register = template.Library()

@register.filter(name='s3')
def get_s3_object(filename,category='img'):
	"""
	"""
	if not filename:
		if category == 'thumb':
			return static('img/default-avatar-min.jpg')
		else:
			return static('img/broken.svg')
	else:
		filename = str(filename)
		if category == 'thumb':
			# this is a thumbnail
			if filename in ('empty','None'):
				return static('img/default-avatar-min.jpg')
			else:
				name = filename[-40:]
				############################################
				################### New ####################
				############################################
				if "1-on-1/" in filename:
					return NEW_BUCKET_ADDR+'thumbnail/1-on-1/'+name
				elif "group/" in filename:
					return NEW_BUCKET_ADDR+'thumbnail/group/'+name
				elif "follower/" in filename:
					return NEW_BUCKET_ADDR+'thumbnail/follower/'+name
				elif "dp/" in filename:
					return NEW_BUCKET_ADDR+'thumbnail/dp/'+name
				elif "shared/" in filename:
					return NEW_BUCKET_ADDR+'thumbnail/shared/'+name
				############################################
				################# Legacy ###################
				############################################
				elif "1on1/" in filename:
					return BUCKET_ADDR+'thumb/1on1/'+name
				elif "mehfil/" in filename:
					return BUCKET_ADDR+'thumb/mehfil/'+name
				# elif "followers/" in filename:
				# 	return BUCKET_ADDR+'thumb/followers/'+name	
				elif "avatar/" in filename:
					return BUCKET_ADDR+'thumb/avatar/'+name
				elif "public/" in filename:
					return BUCKET_ADDR+'thumb/public/'+name
				############################################
				################# Legacy ###################
				############################################
				elif "photos/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				elif "personal_groups/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				elif "avatars/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				elif "mehfils/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				elif "users/" in filename:
					return BUCKET_ADDR+"thumbnails/"+name
				############################################
				############################################
				############################################
				else:
					return NEW_BUCKET_ADDR+"thumbnail/"+name
		else:
			# this is a full-sized image
			if filename in ('empty','None'):
				return static('img/broken.svg')
			else:
				name = filename[-40:]
				############################################
				################### New ####################
				############################################
				if "1-on-1/" in filename:
					return NEW_BUCKET_ADDR+'1-on-1/'+name
				elif "group/" in filename:
					return NEW_BUCKET_ADDR+'group/'+name
				elif "follower/" in filename:
					return NEW_BUCKET_ADDR+'follower/'+name
				elif "dp/" in filename:
					return NEW_BUCKET_ADDR+'dp/'+name
				elif "shared/" in filename:
					return NEW_BUCKET_ADDR+'shared/'+name
				############################################
				################# Legacy ###################
				############################################
				if "1on1/" in filename:
					return BUCKET_ADDR+'1on1/'+name
				elif "mehfil/" in filename:
					return BUCKET_ADDR+'mehfil/'+name
				# elif "followers/" in filename:
				# 	return BUCKET_ADDR+'followers/'+name	
				elif "avatar/" in filename:
					return BUCKET_ADDR+'avatar/'+name
				elif "public/" in filename:
					return BUCKET_ADDR+'public/'+name
				############################################
				################# Legacy ###################
				############################################
				elif "photos/" in filename:
					return BUCKET_ADDR+"photos/"+name
				elif "personal_groups/" in filename:
					return BUCKET_ADDR+"personal_groups/"+name
				elif "avatars/" in filename:
					return BUCKET_ADDR+"avatars/"+name
				elif "mehfils/" in filename:
					return BUCKET_ADDR+"mehfils/"+name
				elif "users/" in filename:
					return BUCKET_ADDR+"users/"+name
				############################################
				############################################
				############################################
				else:
					return NEW_BUCKET_ADDR+"shared/"+name