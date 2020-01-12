from links.redis2 import get_feed_count
from django import template

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_feed_count(context):
	try:
		user_id = context['request'].user.id
		return get_feed_count(user_id) 
	except:
		return None