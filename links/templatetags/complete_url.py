from django import template
import string

register = template.Library()

@register.filter(name='complete_url')
def complete_target_url(url):
	return string.replace(url, "avatars", "//damadamthumbs.azureedge.net")