import redis
from django import forms
from django.contrib.auth.models import User
from redis3 import is_mobile_verified
from location import REDLOC3
FIVE_MINS = 60*5
POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC3, db=0)


def rate_limit_artificial_verification():
	"""
	rate limits artificial verification for 30 mins for security reasons
	"""
	myserver = redis.Redis(connection_pool=POOL)
	if myserver.exists('avrl'):
		return False
	else:
		myserver.setex("avrl","1",FIVE_MINS)
		return True

def is_artificial_verification_ratelimited():
	"""
	checks if artificial verification is ratelimited
	"""		
	ttl = redis.Redis(connection_pool=POOL).ttl("avrl")
	if ttl>0:
		return ttl
	else:
		return None

class AddVerifiedUserForm(forms.Form):
	user_id = forms.CharField(max_length=50)

	class Meta:
		fields = ("user_id",)

	def __init__(self, *args, **kwargs):
		# self.user_id = kwargs.pop('user_id',None)
		super(AddVerifiedUserForm, self).__init__(*args, **kwargs)
		self.fields['user_id'].widget.attrs['class'] = 'cxl sp'
		self.fields['user_id'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['user_id'].widget.attrs['autocomplete'] = 'off'
		self.fields['user_id'].widget.attrs['style'] = 'max-width:90%;background-color:#F8F8F8;border: 1px solid lightgray;border-radius:5px;color: #404040;height:30px'

	def clean_user_id(self):
		user_id = self.cleaned_data.get("user_id")
		user_id = user_id.strip()
		try:
			user_id = int(user_id)
		except (ValueError,TypeError):
			raise forms.ValidationError('Does not compute')

		ttl=is_artificial_verification_ratelimited()
		if ttl:
			raise forms.ValidationError('Not possible till %s years' % ttl)
		else:	
			# does user exist
			if User.objects.filter(id=user_id).exists():
				# go on
				if is_mobile_verified(user_id):
					raise forms.ValidationError('This dude is already king')
				else:
					return user_id
			else:
				raise forms.ValidationError('Is gone with the wind')
