import time
from django import template
from links.redis2 import get_feed_count, set_for_me_seen_time

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_feed_count(context, is_for_me):
	try:
		user_id = context['request'].user.id
		feed_count = get_feed_count(user_id)
		if is_for_me:
			set_for_me_seen_time(user_id, time.time())
		return feed_count
	except:
		return None