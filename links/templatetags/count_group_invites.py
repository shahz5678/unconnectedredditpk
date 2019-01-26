from django import template
from links.redis6 import get_num_user_invites

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_group_invite_count(context):
	user_id = context['request'].user.id
	if user_id:
		return int(get_num_user_invites(user_id))
	else:
		return 0