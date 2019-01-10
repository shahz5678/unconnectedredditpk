from django import template

register = template.Library()

@register.inclusion_tag(file_name='judgement/super_defender_navbar.html')
def super_defender_navbar(static_url, section):
	return {'static_url':static_url,'section':section}