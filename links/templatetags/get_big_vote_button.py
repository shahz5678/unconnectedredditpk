from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_vote_button.html')
def big_vote_button(vote_type, obid, origin, net_votes, base_color, ooid, static_url,oun=None):
	net_votes = int(net_votes) if net_votes else 0
	color = 'rgb(255, 99, 71)' if net_votes < 0 else base_color
	context = {'static_url':static_url,'vote_type':vote_type,'obid':obid,'net_votes':net_votes,'from':origin,'pts_color':color,\
	'border_color':base_color,'font_color':base_color,'is_pht':'1' if vote_type == 'photo_vote' else '0','ooid':ooid}
	return context