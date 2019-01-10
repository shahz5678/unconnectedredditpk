from django import template

register = template.Library()

@register.inclusion_tag(file_name='judgement/banning_history.html')
def banning_history(banning_data, static_url, without_hyperlinks=None, super_admin=None, ledger_ttl=None, super_view_of_def=False, own_id=None):
	return {'static_url':static_url,'banning_data':banning_data,'without_hyperlinks':without_hyperlinks,'super_admin':super_admin,'ledger_ttl':ledger_ttl,\
	'super_view_of_def':super_view_of_def, 'own_id':own_id}