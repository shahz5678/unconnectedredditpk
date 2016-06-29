from django import template
import string

register = template.Library()

@register.filter(name='thumbedge')
def cdnize_target_url(url):
	if 'res/avatars' in url:
		url = string.replace(url, "damadam.blob.core.windows.net/pictures/avatars", "damadamthumbs.azureedge.net")
		return url
	elif 'res/users' in url:
		url = string.replace(url, "damadam.blob.core.windows.net/pictures/users", "damadamthumbs.azureedge.net")
		return url
	elif 'res/photos' in url:
		url = string.replace(url, "damadam.blob.core.windows.net/pictures/photos", "damadamthumbs.azureedge.net")
		return url
	else:
		return url