# -*- coding: utf-8 -*-
from links.redis9 import get_reply_count
from django import template

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_reply_count(context):
	try:
		user_id = context['request'].user.id
		return get_reply_count(user_id) 
	except:
		return None