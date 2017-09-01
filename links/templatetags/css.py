from django import template
from links.redis4 import log_html_error

register = template.Library()

def htmlattributes(value, arg):
	try:
		return value.as_widget(attrs={"style":arg})
	except:
		log_html_error(value=value,arg=arg)

register.filter('htmlattributes', htmlattributes)