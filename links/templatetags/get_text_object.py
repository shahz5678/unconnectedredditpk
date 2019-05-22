from django import template
from links.score import VOTING_DRIVEN_CENSORSHIP

register = template.Library()

@register.inclusion_tag(file_name='content/text_object.html')

def text_object(obid, ooid, text, raw_text, origin, upload_time, machine_time, oun, av_url, vsc, static_url,home_hash=None, is_pinkstar=None, \
alignment=None, just_description=False, block_time_remaining=None):
	pos = 'right' if alignment == '2' else 'left'
	context = {'obid':obid,'ooid':ooid,'text':text,'raw_text':raw_text,'origin':origin,'upload_time':upload_time,'oun':oun,'av_url':av_url,'vsc':vsc,\
	'home_hash':home_hash,'static_url':static_url,'is_pinkstar':is_pinkstar,'VDC':VOTING_DRIVEN_CENSORSHIP,'just_description':just_description,\
	'block_time_remaining':block_time_remaining,'mt':machine_time,'pos':pos}
	return context