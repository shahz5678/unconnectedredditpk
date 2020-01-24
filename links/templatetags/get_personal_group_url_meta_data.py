from django import template

register = template.Library()

@register.inclusion_tag(file_name='personal_group/sharing/personal_group_url_meta_data.html')
def personal_group_url_meta_data(doc, url, url_desc, url_title, url_img, url_height, is_youtube, vid_id, static_url):
	"""
	'doc' stands for degree of completeness (of retrieved metadata):

	'0': no metadata retrieved (case doesn't exist if this template tag has been called)
	'1': just image retrieved
	'2': just title retrieved
	'3': just desc retrieved
	'4': just img and img_dim retrieved
	'5': just desc and img retrieved
	'6': just title and img retrieved
	'7': just desc and title retrieved
	'8': just title, img and img_dim retrieved
	'9': just desc, img and img_dim retrieved
	'10': just desc, title and img retrieved
	'11': desc, title, img and img_dim retrieved
	"""
	return {'doc':doc,'url':url,'url_desc':url_desc, 'url_title':url_title, 'url_img':url_img, 'url_height':url_height, 'is_yt':is_youtube,\
	'static_url':static_url, 'vid_id':vid_id}