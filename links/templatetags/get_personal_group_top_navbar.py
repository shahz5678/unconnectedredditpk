from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/navbars/personal_group_top_navbar.html')
def personal_group_top_navbar(target_id, static_url, chat_not_empty):
	return {'tid':target_id,'static_url':static_url,'chat_not_empty':chat_not_empty}