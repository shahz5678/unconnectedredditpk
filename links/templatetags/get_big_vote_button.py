from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_vote_button.html')
def big_vote_button(is_pht, obid, origin, ooid, user_voted_set, static_url, topic=None):
	"""
	is_pht must be '1' or '0'
	"""
	if user_voted_set and obid in user_voted_set:
		return {'static_url':static_url,'obid':obid,'from':origin,'is_pht':is_pht,'ooid':ooid,'tp':topic, 'liked':True}
	else:
		return {'static_url':static_url,'obid':obid,'from':origin,'is_pht':is_pht,'ooid':ooid,'tp':topic, 'liked':False}