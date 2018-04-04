# coding=utf-8
from django import template

register = template.Library()

@register.filter(name='truncap')
def truncate_and_capitalize(s):
	return s[:1].upper()