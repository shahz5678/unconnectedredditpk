from django import template

register = template.Library()

@register.inclusion_tag(file_name='user_profile_navbar.html')
def user_profile_navbar(static_url, section, uname, is_own_profile):
	return {'static_url':static_url,'section':section,'uname':uname, 'is_own_profile':is_own_profile}