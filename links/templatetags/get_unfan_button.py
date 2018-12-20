from django import template

register = template.Library()

@register.inclusion_tag(file_name='unfan_button.html')
def unfan_button(target_user_id, self_user_id, target_username, static_url):
	target_user_id, self_user_id = int(target_user_id), int(self_user_id)
	possible = True if (target_user_id and self_user_id) and (target_user_id != self_user_id) else False
	return {'static_url':static_url,'possible':possible,'target_username':target_username,'target_user_id':target_user_id}