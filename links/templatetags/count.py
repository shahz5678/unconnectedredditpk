# -*- coding: utf-8 -*-
from links.redis2 import get_notif_count
from django import template

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_notif_count(context):
	try:
		user_id = context['request'].user.id
		notif = get_notif_count(user_id) 
		return notif
	except:
		return 0