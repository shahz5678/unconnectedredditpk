import ujson as json
from django import template

register = template.Library()

@register.inclusion_tag(file_name='photo_comments_section.html')
def photo_comments_section(raw_comments, static_url, self_user_id, origin=None, home_hash=None):
	if raw_comments:
		comments, counter = [], 0
		for raw_comment in reversed(json.loads(raw_comments)):
			comments.append(raw_comment)
			counter += 1
			if counter > 5:
				# this ensure only 6 comments can show up on the photo page (at max)
				break
		if comments:
			return {'comments':comments, 'static_url':static_url,'self_user_id':self_user_id,'origin':origin,'possible':True, 'home_hash':home_hash}
		else:
			return {'possible':False}
	else:
		return {'possible':False}