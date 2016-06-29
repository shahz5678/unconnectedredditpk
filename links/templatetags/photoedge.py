from django import template
import string

register = template.Library()

@register.filter(name='photoedge')
def cdnize_target_url(url):
	if 'damadam.blob.core.windows.net' in url:
		url = string.replace(url, "damadam.blob.core.windows.net/pictures/photos", "damadamphotos.azureedge.net")
		return url
	# elif 'users' in url:
	# 	url = string.replace(url, "users", "thumbnails")
	# 	return url
	# elif 'photos' in url:
	# 	url = string.replace(url, "photos", "thumbnails")
	# 	return url
	else:
		return url