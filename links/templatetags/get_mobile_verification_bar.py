from django import template
from django.middleware import csrf
from links.redis3 import get_approved_places, get_all_pakistan_ad_count, is_mobile_verified, temporarily_save_user_csrf

register = template.Library()

@register.inclusion_tag(file_name='mobile_verification_bar.html')
def mobile_verification_bar(user_id, csrf):
	is_verified = is_mobile_verified(user_id)
	if not is_verified:
		temporarily_save_user_csrf(str(user_id), csrf)
	return { 'show_bar':not is_verified, 'csrf':csrf }