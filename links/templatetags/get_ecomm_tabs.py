from django import template

register = template.Library()

@register.inclusion_tag(file_name='classifieds_tabs.html')
def ecomm_tabs(origin=None, exchange=None, photos=None, is_feature_phone=None, variation=None):
	return {'origin':origin,'is_feature_phone':is_feature_phone,\
		'exchange':exchange, 'photos':photos,'variation':variation}