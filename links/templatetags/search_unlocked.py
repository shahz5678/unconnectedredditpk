from links.redis1 import is_uname_search_unlocked
from django import template

register = template.Library()

@register.assignment_tag(takes_context=True)
def khoji_unlocked(context):
	try:
		user_id = context['request'].user.id
		return is_uname_search_unlocked(user_id) 
	except:
		return False