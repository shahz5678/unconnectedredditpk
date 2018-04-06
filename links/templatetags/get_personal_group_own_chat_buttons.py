from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/buttons/personal_group_own_chat_buttons.html')
def personal_group_own_chat_buttons(blob_id, tid, index, username, score, av_url, tt, ct, img_caption, pt, is_res, id_name, \
	static_url, own_anon_status, their_anon_status, img_width, target_username=None, target_av_url=None, target_score=None, target_content_type=None, \
	target_content=None, target_img_caption=None, target_img_s_caption=None, target_posting_time=None, target_status=None):
	is_minus = id_name == 'minus-bl'
	return {'blob_id':blob_id, 'tid':tid, 'index':index, 'username':username, 'score':score,'av_url':av_url, 'tt':tt, 'ct':ct, 'img_caption':img_caption,\
	'posting_time':pt, 'is_res':is_res,'static_url':static_url,'t_usr':target_username,'t_aurl':target_av_url,'t_scr':target_score,\
	't_tt':target_content_type,'t_ct':target_content,'t_ic':target_img_caption,'t_pt':target_posting_time,'t_st':target_status, 'id_name':id_name,\
	'own_anon':own_anon_status,'their_anon':their_anon_status,'t_isc':target_img_s_caption,'incl_save':'' if is_minus else 'display:none;',\
	'img_width':img_width,'add_margin':'mrl' if is_minus else '' }