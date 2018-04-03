from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/actions/personal_group_own_action_chat.html')
def personal_group_own_action_chat(action, username, av_url, static_url, border_class, own_nick, trunick):
	return {'action':action, 'username':username, 'av_url':av_url, 'static_url':static_url, 'bclass':border_class,'own_nick':own_nick,\
	'trunick':trunick}