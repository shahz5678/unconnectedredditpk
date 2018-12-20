# -*- coding: utf-8 -*-
from django import template
from links.redis5 import retrieve_personal_group_invite_count

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_invite_count(context):
	user_id = context['request'].user.id
	if user_id:
		return int(retrieve_personal_group_invite_count(user_id))
	else:
		return 0