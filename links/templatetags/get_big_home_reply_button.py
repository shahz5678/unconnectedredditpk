from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_home_reply_button.html')
def big_home_reply_button(link_id, comm_count, static_url, always_show=False):
	comm_count = int(comm_count) if comm_count else 0
	THRESHOLD = -1 if always_show else 0
	return {'link_id':link_id,'comm_count':comm_count,'static_url':static_url,'show_reply_btn':'block' if comm_count > THRESHOLD else 'none'}