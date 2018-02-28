from django import template

register = template.Library()

@register.inclusion_tag(file_name='cricket_summary.html')
def cricket_summary(enqueued_match):
	return {'match_ended':enqueued_match['ended'],'score1':enqueued_match['score1'],'score2':enqueued_match['score2'],\
	'team1':enqueued_match['team1'],'team2':enqueued_match['team2'],'status':enqueued_match['status'],'cc':enqueued_match['cc']}