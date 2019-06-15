from django import template

register = template.Library()

@register.inclusion_tag(file_name='home_publicreply_bar.html')
def home_publicreply_bar(link_pk, link_writer_pk, lang, sort_by, user_id, replyform, origin, sk, topic=None):
	return {'link_id':link_pk,'lang':lang,'user_id':user_id,'replyform':replyform,'sort_by':sort_by, 'link_writer_pk':link_writer_pk, 'origin':origin, \
	'sk':sk,'tp':topic}