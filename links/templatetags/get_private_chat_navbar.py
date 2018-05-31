from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/navbars/private_chat_navbar.html')
def private_chat_navbar(static_url, section):
	return {'static_url':static_url,'section':section}