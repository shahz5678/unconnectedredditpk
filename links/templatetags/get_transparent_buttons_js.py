from django import template

register = template.Library()

@register.inclusion_tag(file_name='transparent_buttons_js_helper.html')
def transparent_buttons_js(static_url,ident=None):
	return {'static_url':static_url,'ident':ident}
