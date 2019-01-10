from django import template

register = template.Library()

@register.inclusion_tag(file_name='voting/voting_defender_navbar.html')
def voting_defender_navbar(is_pht, orig, obid, vote_score, static_url, section):
	if int(vote_score) > -1:
		sign = '+'
		color = '#18B488'
		img = 'defender_voting_ban_help-cg.svg'
	else:
		sign = ''
		color = '#FF6347'
		img = 'defender_voting_ban_help-cr.svg'
	return {'static_url':static_url,'section':section,'vsc':vote_score,'sign':sign,'color':color,'img':img,'is_pht':is_pht,'orig':orig,'obid':obid}