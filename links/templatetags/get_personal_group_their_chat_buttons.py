from django import template
from s3 import get_s3_object

register = template.Library()

@register.inclusion_tag(file_name='personal_group/buttons/personal_group_their_chat_buttons.html')
def personal_group_their_chat_buttons(blob_id, target_id, username, av_url, posting_time, content_type, index, img_caption, main_content, \
	static_url, img_s_caption, incl_hide, hide_key, img_id, their_nick, own_nick, img_width, is_res, t_uname=None, t_aurl=None, t_st=None,\
	t_ctype=None,t_ct=None,t_s_img_cap=None,t_time=None,original_poster=None):
	is_yes = hide_key == 'yes'
	hval, is_hidden = False if is_yes else True, 'display:none;' if is_yes else ''
	incl_tgt = True if (is_res == 'res' and hval) else False
	return {'username':username, 'av_url':av_url, 't':posting_time, 'img_caption':img_caption, 'tt':content_type, 'ct':main_content, 'idx':index, \
	'blob_id':blob_id, 'tid':target_id, 'static_url':static_url, 'img_s_caption':img_s_caption, 'incl_save':is_hidden,'img_id':img_id, 't_st':t_st,\
	'incl_hide':'' if incl_hide in ('img','shared_img') else 'display:none;', 't_time':t_time, 'incl_dresp':is_hidden, 'hval':hval,'t_ct':t_ct,\
	'their_nick':their_nick, 'own_nick':own_nick,'img_width':img_width, 'is_res':is_res, 't_uname':t_uname,'t_aurl':t_aurl,'t_ctype':t_ctype,\
	't_s_img_cap':t_s_img_cap,'incl_tgt':incl_tgt,'original_poster':original_poster,'hide_label':"UNHIDE" if is_yes else 'HIDE'}