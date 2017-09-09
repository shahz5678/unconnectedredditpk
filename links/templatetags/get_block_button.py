from django import template
from links.redis4 import log_button_error

register = template.Library()

@register.inclusion_tag(file_name='block_button.html')
def block_button(target_user_id, target_username, self_user_id, object_id, referrer, static_url):
	try:
		target_user_id, self_user_id = int(target_user_id), int(self_user_id)
		possible = True if (target_user_id and self_user_id) and (target_user_id != self_user_id) else False
		if possible:
			payload = "7f"+hex(target_user_id)+":a"
			return {'target_user_id':payload,'target_username':target_username,'self_user_id':self_user_id,'referrer':referrer, 'object_id':object_id,\
			'static_url':static_url, 'possible':possible}
		else:
			return {'possible':False}
	except:
		log_button_error(target_user_id=target_user_id, id_type=type(target_user_id),target_username=target_username,own_id=self_user_id, object_id=object_id,referrer=referrer)
		return {'possible':False}