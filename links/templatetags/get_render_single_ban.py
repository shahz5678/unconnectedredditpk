from django import template

register = template.Library()

@register.inclusion_tag(file_name='judgement/render_single_ban.html')
def render_single_ban(time, sin, oun, tp, txt, obid, pu, utunm, oeunm, oeid, dunm, did, remark, dur, static_url):
	context = {'time':time, 'sin':sin, 'oun':oun, 'tp':tp, 'txt':txt, 'obid':obid, 'pu':pu, 'utunm':utunm, 'oeunm':oeunm, 'oeid':oeid, 'dunm':dunm, 'did':did, \
	'remark':remark, 'dur':dur, 'static_url':static_url}
	return context