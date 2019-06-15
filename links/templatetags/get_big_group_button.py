from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_group_button.html')
def big_group_button(own_id, target_id, parent_object_id, object_type, origin,target_username=None, home_hash=None, topic=None):
	if not own_id or int(own_id) == int(target_id):
		return {'own_id':True,'tp':topic}
	else:
		return {'own_id':False, 'tid':target_id, 'poid':parent_object_id, 'ot':object_type, 'org':origin, 'tun':target_username, \
		'home_hash':home_hash,'tp':topic}