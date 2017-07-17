from django import template

register = template.Library()

@register.inclusion_tag(file_name='pagination_buttons.html')
def pagination_buttons(page_obj=None):
	return {'page':page_obj}
