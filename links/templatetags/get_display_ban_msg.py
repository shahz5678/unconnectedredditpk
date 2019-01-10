from django import template

register = template.Library()

@register.inclusion_tag(file_name='judgement/display_ban_msg.html')
def display_ban_msg(static_url, is_banned, is_defender, is_own_profile, time_remaining, uname, ban_detail):
	return {'static_url':static_url,'is_banned':is_banned,'is_defender':is_defender,'is_own_profile':is_own_profile,'time_remaining':time_remaining,\
	'uname':uname,'ban_detail':ban_detail}