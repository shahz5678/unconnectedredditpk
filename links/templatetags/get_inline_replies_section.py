import ujson as json
from django import template

register = template.Library()

@register.inclusion_tag(file_name='inline_replies_section.html')
def inline_replies_section(raw_replies, static_url, self_user_id, origin, obj_owner_id, obj_type, home_hash=None, topic_url=None):
	"""
	Generates "inline replies" under a given post
	"""
	if raw_replies:
		replies, counter = [], 0
		for reply_id, reference_id, reply_data in reversed(json.loads(raw_replies)):
			reply_data['reply_id'] = reply_id# enriching reply 
			reply_data['ref_id'] = reference_id
			replies.append(reply_data)
			counter += 1
			if counter > 3:
				# this ensures only 4 comments can show up on the photo page (at max)
				break
		if replies:
			################################################
			# declaring some legacy object types still used in the code. TODO: phase these out
			if obj_type == 'tx':
				object_type, obtp = 'link', '3'
			else:
				# obj_type == 'img' in this scenario
				object_type, obtp = 'photos', '4'
			################################################
			return {'replies':replies,'static_url':static_url,'self_user_id':self_user_id, 'possible':True,'home_hash':home_hash,\
			'topic_url':topic_url, 'obj_owner_id':obj_owner_id, 'origin':origin, 'obj_type':obj_type, 'object_type':object_type, \
			'obtp':obtp}
		else:
			return {'possible':False}
	else:
		return {'possible':False}