from django import template

register = template.Library()

@register.inclusion_tag(file_name='judgement/report_navbar.html')
def report_navbar(categ, static_url, section, tp=None, orig=None, cap=None, purl=None, lid=None, oun=None, obid=None, oid=None, topic=None, rules=None,\
	guid=None):
	context = {'categ':categ, 'tp':tp,'orig':orig,'cap':cap,'purl':purl,'lid':lid,'oun':oun,'obid':obid,'oid':oid,'static_url':static_url,'section':section,\
	'guid':guid,'topic':topic,'rules':rules}
	return context