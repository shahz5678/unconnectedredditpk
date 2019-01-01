from django import template

register = template.Library()

@register.inclusion_tag(file_name='big_buttons/big_external_share_button.html')
def big_external_share_button(owner_username, is_mobile, photo_id, origin, static_url, owner_id=None, sharer_id=None, js_class='', sharing_type=None\
	, seen=None):
	border_color = '#2CB742' if is_mobile else '#944CB2'
	return {'owner_username':owner_username,'photo_id':photo_id,'static_url':static_url,'is_mobile':is_mobile,'origin':origin,\
	'owner_id':owner_id,'sharer_id':sharer_id,'js_class':js_class,'sharing_type':sharing_type,'border_color':'#BFBFBF' if seen else border_color}