import ujson as json
from django import template

register = template.Library()

@register.inclusion_tag(file_name='home_replies_section.html')
def home_replies_section(raw_replies, static_url, self_user_id, home_hash):
	if raw_replies:
		replies, counter = [], 0
		for payload in reversed(json.loads(raw_replies)):
			replies.append(payload)
			counter += 1
			if counter > 3:
				# this ensures only 4 comments can show up on the photo page (at max)
				break
		if replies:
			return {'replies':replies,'static_url':static_url,'self_user_id':self_user_id, 'possible':True,'home_hash':home_hash} 
		else:
			return {'possible':False}
	else:
		return {'possible':False}