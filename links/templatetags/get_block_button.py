from django import template

register = template.Library()

@register.inclusion_tag(file_name='block_button.html')
def block_button(target_user_id, target_username, self_user_id, object_id, referrer, static_url, obj_type=None):
	if self_user_id and target_user_id:
		target_user_id, self_user_id = int(target_user_id), int(self_user_id)
		possible = True if (target_user_id and self_user_id) and (target_user_id != self_user_id) else False
		if possible:
			payload = "7f"+hex(target_user_id)+":a"
			return {'target_user_id':payload,'target_username':target_username,'self_user_id':self_user_id,'referrer':referrer, 'object_id':object_id,\
			'static_url':static_url, 'possible':possible,'link_id':object_id}
		else:
			return {'possible':False}
	else:
		return {'possible':False}