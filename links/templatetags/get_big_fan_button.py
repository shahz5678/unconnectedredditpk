from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_fan_button.html')
def big_fan_button(own_user_id, target_user_id, object_id, origin, fan_list, static_url,home_hash=None, seen=None):
	if int(own_user_id) != int(target_user_id):
		is_already_fan = target_user_id in fan_list
		return {'possible':True, 'org':origin,'oid':object_id,'tid':target_user_id,'static_url':static_url, 'is_already_fan':is_already_fan,\
		'border_color':'#BFBFBF' if seen else '#FFCD00','home_hash':home_hash}
	else:
		return {'possible':False}