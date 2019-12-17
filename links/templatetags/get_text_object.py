from django import template
from links.score import VOTING_DRIVEN_CENSORSHIP

register = template.Library()

@register.inclusion_tag(file_name='content/text_object.html')

def text_object(obid, ooid, text, raw_text, origin, upload_time, machine_time, oun, av_url, vsc, static_url,home_hash=None, is_star=None, \
	alignment=None, just_description=False, block_time_remaining=None, topic=None, topic_url=None, show_topic=None, c1=None, c2=None, \
	is_fbs=False):
	pos = 'right' if alignment == '2' else 'left'
	context = {'obid':obid,'ooid':ooid,'text':text,'raw_text':raw_text,'origin':origin,'upload_time':upload_time,'oun':oun,'av_url':av_url,\
	'vsc':vsc,'home_hash':home_hash,'static_url':static_url,'is_star':is_star,'VDC':VOTING_DRIVEN_CENSORSHIP,'just_description':just_description,\
	'is_fbs':is_fbs,'block_time_remaining':block_time_remaining,'mt':machine_time,'pos':pos,'topic':topic,'topic_url':topic_url,'show_topic':show_topic,\
	'c1':c1, 'c2':c2}
	return context