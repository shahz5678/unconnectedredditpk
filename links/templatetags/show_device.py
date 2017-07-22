from django import template

register = template.Library()

@register.inclusion_tag(file_name='device.html')
def device(submission_device, static_url):
	return {'submission_device':submission_device,'static_url':static_url}