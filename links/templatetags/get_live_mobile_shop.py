from django import template
import time

#from links.redis3 import get_approved_places, get_all_pakistan_ad_count

register = template.Library()

@register.inclusion_tag(file_name='shop_open.html')
def open_mobile_shop(static_url):
	get_time = time.time()
	test_time = 1506362400-get_time 
	return {'static_url':static_url,'test_time':test_time}
