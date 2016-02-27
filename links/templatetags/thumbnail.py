from django import template
import string

register = template.Library()

@register.filter(name='thumbnail')
def thumbnailize_target_url(url):
	if 'avatars' in url:
		url = string.replace(url, "avatars", "thumbnails")
		return url
	elif 'users' in url:
		url = string.replace(url, "users", "thumbnails")
		return url
	else:
		return url