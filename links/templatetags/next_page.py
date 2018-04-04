from django import template
import string

register = template.Library()

@register.filter(name='next_page')
def next_page(current_page, page_count):
	try:
		current_page = int(current_page)
	except (ValueError,NameError,TypeError):
		return current_page
	if current_page < page_count:
		return str(current_page+1)
	elif current_page == page_count:
		return '1'
	else:
		return str(page_count)