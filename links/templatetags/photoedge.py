from django import template
import string

register = template.Library()

@register.filter(name='photoedge')
def cdnize_target_url(url):
	if 'damadam.blob.core.windows.net/pictures/photos' in url:
		url = string.replace(url, "damadam.blob.core.windows.net/pictures/photos", "damadamphotos.azureedge.net")
		return url
	elif 'damadam.blob.core.windows.net/pictures/mehfils' in url:
	 	url = string.replace(url, "damadam.blob.core.windows.net/pictures/mehfils", "damadammehfil.azureedge.net")
	 	return url
	# elif 'photos' in url:
	# 	url = string.replace(url, "photos", "thumbnails")
	# 	return url
	else:
		return url