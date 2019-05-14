from django.template.defaulttags import register
from links.views import beautiful_date

@register.filter(name='datetime')
def datetime(value):
	return beautiful_date(value,format_type='2')