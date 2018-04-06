from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/photos/personal_group_big_photo.html')
def personal_group_big_photo(img_url, img_caption, css_shadow, max_width, static_url):
	return {'img_url':img_url, 'img_caption':img_caption, 'css_shadow':css_shadow, 'max_width':max_width, 'static_url':static_url}