from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/photos/personal_group_hidden_pht_big.html')
def personal_group_hidden_pht_big(max_width, hw_ratio, css_shadow, right_align):
	return {'max_width':max_width,'hw_ratio':hw_ratio,'css_shadow':css_shadow,'right_align':right_align}