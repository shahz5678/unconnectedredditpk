# coding=utf-8
from django import template

register = template.Library()

@register.filter(name='truncap')
def truncate_and_capitalize(s):
	# return s.decode('utf-8')[:1].upper()
	return s[:1].upper()