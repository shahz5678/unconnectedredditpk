from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/photos/personal_group_hidden_pht_small.html')
def personal_group_hidden_pht_small(max_width, thumb_height, css_shadow, right_align):
	return {'max_width':max_width, 'thumb_height':thumb_height,'css_shadow':css_shadow, 'right_align':right_align}