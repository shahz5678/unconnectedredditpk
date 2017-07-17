from django import template

register = template.Library()

@register.filter(name='join_string')
def join_input_string(string):
	return string.replace (" ", "_")