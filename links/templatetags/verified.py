from django import template
from django.db import models
from django.contrib.auth.models import User

register = template.Library()

FEMALES = ['Aishmato', 'Jaana', 'ayla', 'Maleenjaslee', 'Hoor', 'Tani_789', 'Sanam_khan', 'Esha-ali-subhani', 'dipika', 'Pomi', 'Hina', 'July', 'Juhikhan', 'gori', 'samreen', 'Farheen', 'pholi', 'AlinaNoor_786', 'rabika', 'mehro', 'Sheeery', 'Maleenjalee','Rimiii','Remsha','sherikhokhar5','Roshni_malik_53','Rahat',]

@register.simple_tag
def verified(user):
	#print "user is %s" % user.username
	if user in FEMALES:
		return True
	else:
		return False

register.simple_tag(verified)