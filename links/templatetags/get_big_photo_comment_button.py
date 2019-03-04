from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_photo_comment_button.html')
def big_photo_comment_button(photo_id, origin, comm_count, static_url, star_id=None, seen=None, from_single_notif=None):
	comm_count = int(comm_count) if comm_count else 0
	return {'photo_id':photo_id,'origin':origin,'comm_count':comm_count,'static_url':static_url,'star_id':star_id,\
	'border_color':'#BFBFBF' if seen else '#ff8000','from_single_notif':from_single_notif}