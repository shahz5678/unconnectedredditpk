from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_points_button.html')
def big_points_button(obj_id, owner_id, is_pht, origin, net_votes, base_color, static_url):
	net_votes = int(net_votes) if net_votes else 0
	color = 'rgb(255, 99, 71)' if net_votes < 0 else base_color
	return {'obid':obj_id,'ooid':owner_id,'is_pht':is_pht,'net_votes':net_votes,'pts_color':color,'base_color':base_color,'static_url':static_url,\
	'from':origin}