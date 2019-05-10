from django import template
from links.score import VOTING_DRIVEN_CENSORSHIP, VOTING_DRIVEN_PIXELATION

register = template.Library()

@register.inclusion_tag(file_name='content/photo_object.html')
def photo_object(pid, ooid, img_url, vsc, img_thumb ,upload_time, machine_time, oun, origin, static_url, caption, raw_caption, is_fbs=None, \
	av_url=None, home_hash='',block_time_remaining=None,is_pinkstar=None, show_uname_credentials=True, show_report=True, show_trending=False):
	# score = '1' if (score and int(score) < 1) else score
	return {'vsc':float(vsc) if vsc else 0,'oun':oun, 'static_url':static_url, 'VDC':(VOTING_DRIVEN_CENSORSHIP+1),'VDP':(VOTING_DRIVEN_PIXELATION+1),\
	'cap':caption,'av_url':av_url,'ut':upload_time,'img_url':img_url,'img_thumb':img_thumb,'is_fbs':is_fbs,'home_hash':home_hash, 'origin':origin, \
	'show_avatar':'block' if av_url else 'none','block_time_remaining':block_time_remaining,'ooid':ooid, 'pid':pid,'raw_caption':raw_caption, \
	'is_pinkstar':is_pinkstar,'show_uname_credentials':show_uname_credentials, 'report_display':'block' if show_report else 'none',\
	'show_trending':True if show_trending == '6' else False,'mt':machine_time}# a value of '6' implies the image trended