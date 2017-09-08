from django import template
#from links.redis3 import get_approved_places, get_all_pakistan_ad_count

register = template.Library()

@register.inclusion_tag(file_name='mobile_shop_ad.html')
def mobile_shop(static_url):
	return {'static_url':static_url}
