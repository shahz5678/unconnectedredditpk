from django.template.defaulttags import register
from links.redis1 import voted_for_single_photo

@register.filter(name='photo_voted')
def photo_voted(photo_pk,username):
	return voted_for_single_photo(photo_pk, username)