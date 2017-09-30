from django import template
from links.redis3 import seen_outage_notif

register = template.Library()

@register.inclusion_tag(file_name='outage_notif.html')
def outage_notif(STATIC_URL, user_id, origin):
	if seen_outage_notif(user_id):
		allowed = False
	else:
		allowed = True
	return {'static_url':STATIC_URL,'user_id':user_id,'orig':origin,'allowed':allowed}