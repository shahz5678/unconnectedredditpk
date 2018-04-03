from django import template
import string

register = template.Library()

@register.filter(name='subtract')
def subtract(val1, val2):
	try:
		val1,val2 = float(val1), float(val2)
	except (ValueError,TypeError,NameError):
		return ''
	return val1-val2