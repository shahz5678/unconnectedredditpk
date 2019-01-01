from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_send_button.html')
def big_send_button(photo_owner_username, photo_id, photo_owner_id, photo_caption, origin, img_url, static_url,home_hash=None, seen=None):
	return {'owner_uname':photo_owner_username,'pid':photo_id,'oid':photo_owner_id,'caption':photo_caption,'origin':origin,'img_url':img_url,\
	'static_url':static_url,'border_color':'#BFBFBF' if seen else '#6092F8','home_hash':home_hash}