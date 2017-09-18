from django import template

register = template.Library()

@register.inclusion_tag(file_name='fan_button.html')
def fan_button(own_user_id, target_user_id, object_id, origin, fan_list, static_url):
	if int(own_user_id) != int(target_user_id):
		return {'possible':True, 'org':origin,'oid':object_id,'tid':target_user_id,'static_url':static_url, 'fan_list':fan_list}
	else:
		return {'possible':False}