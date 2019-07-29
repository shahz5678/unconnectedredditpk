from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_vote_button.html')
def big_vote_button(is_pht, obid, origin, ooid, user_voted, static_url, topic=None):
	"""
	Helps render a 'like' button, in either its default or 'already-liked' state

	is_pht must be '1' or '0'
	'user_voted' contains 'True' if user has liked an object, otherwise it's simply None
	"""
	return {'static_url':static_url,'obid':obid,'from':origin,'is_pht':is_pht,'ooid':ooid,'tp':topic, 'liked':user_voted}