from django import template
import string

register = template.Library()

@register.filter(name='complete_url')
def complete_target_url(url,thumb=False):
	if "avatars" in url:
		if thumb:
			return string.replace(url, "avatars", "//damadamthumbs.azureedge.net")
		else:
			return string.replace(url, "avatars", "//damadamavatar.azureedge.net")
	elif "photos" in url:
		if thumb:
			return string.replace(url, "photos", "//damadamthumbs.azureedge.net")
		else:
			return string.replace(url, "photos", "//damadamphotos.azureedge.net")