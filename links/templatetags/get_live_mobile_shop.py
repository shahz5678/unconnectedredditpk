from django import template
import time

register = template.Library()

@register.inclusion_tag(file_name='shop_open.html')
def open_mobile_shop(static_url):
	test_time = 1511654400-time.time()
	return {'static_url':static_url,'test_time':test_time}
