from django import template

register = template.Library()

@register.inclusion_tag(file_name='vote_buttons.html')
def vote_buttons(vote_type, origin, static_url, females=None, sort_by=None, lang=None, lid=None, pid=None, oun=None, oid=None,from_cricket=None):
	super_cricket_upvote = '5'
	super_cricket_downvote = '-5'
	cricket_upvote = '4'
	cricket_downvote = '-4'
	super_upvote = '2'
	super_downvote = '-2'
	upvote = '1'
	downvote = '-1'
	return {'vote_type':vote_type,'lang':lang,'sort_by':sort_by,'females':females,'lid':lid,'from':origin,'static_url':static_url,'pid':pid,\
	'oun':oun,'oid':oid,'from_cricket':from_cricket, 'upvote':upvote,'downvote':downvote,'cricket_upvote':cricket_upvote,'cricket_downvote':cricket_downvote,\
	'super_upvote':super_upvote,'super_downvote':super_downvote,'super_cricket_upvote':super_cricket_upvote,'super_cricket_downvote':super_cricket_downvote}