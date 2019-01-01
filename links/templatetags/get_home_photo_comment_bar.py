from django import template

register = template.Library()

@register.inclusion_tag(file_name='home_photo_comment_bar.html')
def home_photo_comment_bar(photo_id, photo_owner_id, lang, sort_by, user_id, comment_form, origin, home_hash, sk):
	return {'photo_id':photo_id,'lang':lang,'user_id':user_id,'comment_form':comment_form,'sort_by':sort_by,'origin':origin, 'home_hash':home_hash, \
	'photo_owner_id':photo_owner_id, 'sk':sk}