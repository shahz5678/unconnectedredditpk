from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/navbars/personal_group_bottom_navbar.html')
def personal_group_bottom_navbar(target_id, static_url, is_nick_visible):
	return {'tid':target_id,'static_url':static_url,'is_nick':is_nick_visible}