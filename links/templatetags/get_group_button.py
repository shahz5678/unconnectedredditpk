from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/buttons/group_button.html')
def group_button(own_id, target_id, parent_object_id, object_type, origin, target_username=None):
	if not own_id or int(own_id) == int(target_id):
		return {'own_id':True}
	else:
		return {'own_id':False, 'tid':target_id, 'poid':parent_object_id, 'ot':object_type, 'org':origin, 'tun':target_username}