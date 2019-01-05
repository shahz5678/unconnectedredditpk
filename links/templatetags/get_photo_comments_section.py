import ujson as json
from django import template
from links.redis7 import get_raw_comments

register = template.Library()

@register.inclusion_tag(file_name='photo_comments_section.html')
def photo_comments_section(raw_comments, static_url, self_user_id, origin=None, score=None, home_hash=None):
	# if originates from home ('3'), raw_comments contains 'photo_id' in that case
	if origin == '3':
		raw_comments = get_raw_comments(raw_comments)
	if raw_comments:
		comments, counter = [], 0
		for raw_comment in reversed(json.loads(raw_comments)):
			comments.append(raw_comment)
			counter += 1
			if counter > 5:
				# this ensure only 6 comments can show up on the photo page (at max)
				break
		if comments:
			return {'comments':comments, 'static_url':static_url,'self_user_id':self_user_id,'score':score,'origin':origin,'possible':True, 'home_hash':home_hash}
		else:
			return {'possible':False}
	else:
		return {'possible':False}