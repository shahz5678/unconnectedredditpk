from django import template

register = template.Library()

visibility = {False:'hidden',True:'visible',None:'hidden'}

@register.inclusion_tag(file_name='personal_group/main/personal_group_input_fields.html')
def personal_group_input_fields(sk, no_permit, no_notif, no_save_chat, t_nick, form_errors, personal_group_form, tid, static_url, chat_not_empty, \
	their_last_seen_time, last_seen_time_diff, is_js_env):
	return {'sk':sk,'no_permit':no_permit, 'no_notif':no_notif, 'no_save_chat':no_save_chat,'t_nick':t_nick,'personal_group_form':personal_group_form,\
	'form_errors':form_errors,'static_url':static_url, 'visib':visibility[chat_not_empty],'last_seen_time_diff':last_seen_time_diff, 'tid':tid, \
	'their_last_seen_time':their_last_seen_time, 'is_js_env':is_js_env}