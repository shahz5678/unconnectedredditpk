from django import template

register = template.Library()

@register.inclusion_tag(file_name='curate_photo.html')
def curate_photo(pid, vsc, oun, caption, oid, purl, origin, static_url,lid=None):
	return {'pid':pid, 'vsc':vsc, 'oun':oun, 'caption':caption,'oid':oid, 'purl':purl, 'lid':lid, 'origin':origin, 'static_url':static_url}