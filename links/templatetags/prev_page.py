from django import template
import string

register = template.Library()

@register.filter(name='prev_page')
def prev_page(current_page, page_count):
	try:
		current_page = int(current_page)
	except (ValueError,NameError,TypeError):
		return current_page
	if current_page == 1:
		return str(page_count)
	elif current_page <= page_count:
		return str(current_page-1)
	else:
		return str(page_count)