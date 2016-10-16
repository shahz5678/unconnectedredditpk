from django.template.defaulttags import register
from links.redismodules import voted_for_photo

@register.filter(name='photo_voted')
def photo_voted(photo_pk,username):
	return voted_for_photo(photo_pk, username)