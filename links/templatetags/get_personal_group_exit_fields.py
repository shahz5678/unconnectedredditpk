from django import template
from links.redis5 import get_suspension_details

register = template.Library()

@register.inclusion_tag(file_name='personal_group/exit_settings/personal_group_exit_fields.html')
def personal_group_exit_fields(group_id, t_nick, target_id, own_id):
	suspended_by, time_of_suspension, can_rejoin, time_remaining = get_suspension_details(own_id, target_id, group_id)
	return {'suspended_by':suspended_by, 'time_of_suspension':time_of_suspension, 't_nick':t_nick, 'can_rejoin':can_rejoin, 'time_remaining':time_remaining,\
	'tid':target_id}