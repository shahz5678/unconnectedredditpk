from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/actions/personal_group_their_action_chat.html')
def personal_group_their_action_chat(action, username, av_url, static_url, border_class, their_nick, trunick):
	return {'action':action, 'username':username, 'av_url':av_url, 'static_url':static_url, 'bclass':border_class,'their_nick':their_nick,\
	'trunick':trunick}