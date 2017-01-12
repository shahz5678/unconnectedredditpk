from django.template.defaulttags import register
from links.redis1 import get_home_link_votes

@register.filter(name='get_votes')
def get_votes(link_pk):
	return get_home_link_votes(link_pk)