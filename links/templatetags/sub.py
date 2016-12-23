from django.template.defaulttags import register

@register.filter(name='sub')
def sub(value, arg):
	diff = int(value) - int(arg)
	return diff