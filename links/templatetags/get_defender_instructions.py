from django import template

register = template.Library()

@register.inclusion_tag(file_name='judgement/defender_instructions.html')
def defender_instructions(with_warning=None):
	return {'with_warning':with_warning}