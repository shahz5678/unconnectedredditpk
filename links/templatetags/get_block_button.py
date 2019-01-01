from django import template

register = template.Library()

@register.inclusion_tag(file_name='block_button.html')
def block_button(target_user_id, target_username, self_user_id, obj_id, origin, static_url, obj_type=None):
	if self_user_id and target_user_id:
		target_user_id, self_user_id = int(target_user_id), int(self_user_id)
		possible = True if (target_user_id and self_user_id) and (target_user_id != self_user_id) else False
		if possible:
			payload = "7f"+hex(target_user_id)+":a"
			if obj_type:
				link_id = 'tx:'+str(obj_id) if obj_type == 'tx' else 'img:'+str(obj_id)
			else:
				link_id = None
			context = {'target_user_id':payload,'target_username':target_username,'self_user_id':self_user_id,'static_url':static_url, \
			'possible':possible,'origin':origin,'obj_id':obj_id,'link_id':link_id}
			return context
		else:
			return {'possible':False}
	else:
		return {'possible':False}