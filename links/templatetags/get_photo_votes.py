from django.template.defaulttags import register
from links.redismodules import get_photo_votes

@register.filter(name='get_photovotes')
def get_photovotes(photo_pk):
	return get_photo_votes(photo_pk)