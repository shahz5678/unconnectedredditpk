from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_block_button.html')
def big_block_button(target_user_id, origin, page_num, static_url):
	target_user_id = int(target_user_id)
	context = {'target_user_id':"7f"+hex(target_user_id)+":a",'static_url':static_url, 'origin':origin, 'page_num':page_num}
	return context