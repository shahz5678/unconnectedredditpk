from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/deletion/personal_group_deleted_post_message.html')
def personal_group_deleted_post_message(inset_color, shadow_base_color):
	return {'inset_color':inset_color,'shadow_base_color':shadow_base_color}