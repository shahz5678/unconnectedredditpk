from django import template

register = template.Library()

@register.inclusion_tag(file_name='newbie_rules.html')
def newbie_rules(location, static_url, lang=None):
	return {'location':location, 'static_url':static_url, 'lang':lang}