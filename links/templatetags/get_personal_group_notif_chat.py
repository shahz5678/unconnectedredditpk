from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/notifications/personal_group_notif_chat.html')
def personal_group_notif_chat(own_id, writer_id, notif, username, av_url, t_username, t_av_url, static_url, their_nick, trunick, time,blob_id, status, tid):
	return {'notif':notif, 'sent_by_username':username, 'sent_by_av_url':av_url, 'sent_to_username':t_username,'sent_to_av_url':t_av_url,\
	'static_url':static_url, 'their_nick':their_nick,'trunick':trunick, 'i_am_sender':True if own_id == int(writer_id) else False, 'time':time,\
	'their_id':writer_id,'blob_id':blob_id, 'status':status, 'tid':tid}