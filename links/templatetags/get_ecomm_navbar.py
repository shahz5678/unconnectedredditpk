from django import template
from links.redis3 import get_approved_loc, get_all_pakistan_ad_count

register = template.Library()

@register.inclusion_tag(file_name='classifieds_navbar.html')
def ecomm_navbar(origin=None, is_feature_phone=None):
	locations_and_counts = get_approved_loc(withscores=True)
	ad_count = get_all_pakistan_ad_count()
	if len(locations_and_counts) < 3:
		is_feature_phone = '1'
	return {'top_3_locs':locations_and_counts[:3],'origin':origin,'is_feature_phone':is_feature_phone,\
		'other_cities':len(locations_and_counts[3:]),'ad_count':ad_count}