from django import template

register = template.Library()

def htmlattributes(value, arg):
	return value.as_widget(attrs={"style":arg})

register.filter('htmlattributes', htmlattributes)