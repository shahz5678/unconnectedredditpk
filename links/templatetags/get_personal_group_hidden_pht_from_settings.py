from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/photos/photo_settings/personal_group_hidden_pht_from_settings.html')
def personal_group_hidden_pht_from_settings(hw_ratio):
	return {'hw_ratio':hw_ratio}