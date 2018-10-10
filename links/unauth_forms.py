from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from redis3 import nick_already_exists,insert_nick, bulk_nicks_exist, log_erroneous_passwords, check_nick_status, invalidate_user_pin, verify_user_pin,\
is_mobile_verified, is_sms_sending_rate_limited, get_user_verified_number, log_pin_attempt, invalid_nick_logger#, someone_elses_number
from abuse import BANNED_NICKS, BANNED_FORGOTTEN_NICKS
from forms import retrieve_validation_error_string
from views import secs_to_mins
import re



def validate_string_chars(value, banned_nicks, lang=None):
	reg = re.compile('^[\w\s.@+-]+$')
	if not reg.match(value):
		raise ValidationError(retrieve_validation_error_string('invalid_new_nick',lang=lang))
	for name in banned_nicks:
		if name.lower() in value.lower():
			invalid_nick_logger(name,value)
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload=name.capitalize()))


############################################# Forgot Password ##############################################

class ForgettersMobileNumber(forms.Form):
	"""
	Generates a form for user mobile number verification when a user has forgotten their password
	"""	
	phonenumber = forms.RegexField(max_length=11, regex=re.compile("^[0-9]+$"))
	
	class Meta:
		fields = ('phonenumber')

	def __init__(self, *args, **kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.lang = kwargs.pop('lang',None)
		super(ForgettersMobileNumber, self).__init__(*args, **kwargs)
		self.fields['phonenumber'].error_messages = \
		{'required': retrieve_validation_error_string('required_mobnum',lang=self.lang),'invalid':retrieve_validation_error_string('invalid_mobnum',lang=self.lang)}
		self.fields['phonenumber'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #16d68a;'
		self.fields['phonenumber'].widget.attrs['class'] = 'cxl'
		self.fields['phonenumber'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['phonenumber'].widget.attrs['autocomplete'] = 'off'
		self.fields['phonenumber'].widget.attrs['autocapitalize'] = 'none'
		self.fields['phonenumber'].widget.attrs['spellcheck'] = 'false'
	
	def clean_phonenumber(self):
		lang, phonenumber = self.lang, self.cleaned_data.get('phonenumber')
		verified = is_mobile_verified(self.user_id)
		mobile_length = len(phonenumber)
		if phonenumber[0:2] != '03':
			raise forms.ValidationError(retrieve_validation_error_string('mobnum_wrong_format',lang=lang))
		elif mobile_length < 11:
			raise forms.ValidationError(retrieve_validation_error_string('mobnum_too_small',lang=lang))
		elif phonenumber == '03451234567':
			raise forms.ValidationError(retrieve_validation_error_string('fake_mobnum',lang=lang))
		elif not verified:
			raise forms.ValidationError(retrieve_validation_error_string('mobnum_not_verified',lang=lang))
		user_nums = get_user_verified_number(user_id=self.user_id)
		if phonenumber[-10:] in user_nums:
			ttl = is_sms_sending_rate_limited(self.user_id)
			if ttl:
				return phonenumber[-11:], ttl
			else:
				return phonenumber[-11:], None
		else:
			raise forms.ValidationError(retrieve_validation_error_string('not_your_mobnum',lang=lang))
		

class ForgettersPin(forms.Form):
	pinnumber = forms.RegexField(max_length=5,regex=re.compile("^[0-9]+$"))

	class Meta:
		fields = ('pinnumber')

	def __init__(self, *args, **kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.lang = kwargs.pop('lang',None)
		super(ForgettersPin, self).__init__(*args, **kwargs)
		self.fields['pinnumber'].error_messages = {'required':retrieve_validation_error_string('required_pin',lang=self.lang),'invalid':retrieve_validation_error_string('invalid_pin',lang=self.lang)}
		self.fields['pinnumber'].widget.attrs['style'] = 'text-indent: 6px;color: #16d68a;width:80px;border-radius:5px;border: 1px solid #00c853; background-color:#fffce6;padding: 6px 6px 6px 0;'
		self.fields['pinnumber'].widget.attrs['class'] = 'cxl'
		self.fields['pinnumber'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['pinnumber'].widget.attrs['autocomplete'] = 'off'
		self.fields['pinnumber'].widget.attrs['autocapitalize'] = 'none'
		self.fields['pinnumber'].widget.attrs['spellcheck'] = 'false'
		
			
	def clean_pinnumber(self):
		lang, pinnumber = self.lang, self.cleaned_data.get('pinnumber')
		if len(pinnumber) < 5:
			raise forms.ValidationError(retrieve_validation_error_string('pin_too_small',lang=lang))
		else:
			logged, ttl = log_pin_attempt(self.user_id)
			if logged:
				exists, status = verify_user_pin(self.user_id,pinnumber)	
				if exists:
					return status
				else:
					if status == 'pin_incorrect':
						raise forms.ValidationError(retrieve_validation_error_string('wrong_pin',lang=lang))
					else:
						#return when pin is invalid or has expired
						invalidate_user_pin(self.user_id)
						return status
			else:
				raise forms.ValidationError(retrieve_validation_error_string('pin_tries_rate_limited',lang=lang,payload=secs_to_mins(ttl)))


class ResetForgettersPasswordForm(forms.Form):
	password = forms.CharField()
	class Meta:
		fields = ('password',)

	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',None)
		self.lang = kwargs.pop('lang',None)
		super(ResetForgettersPasswordForm, self).__init__(*args,**kwargs)
		self.fields['password'].error_messages = {'required':retrieve_validation_error_string('required_new_pass',lang=self.lang)}
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #16d68a;'
		self.fields['password'].widget.attrs['class'] = 'cxl'
		self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'
		self.fields['password'].widget.attrs['autocapitalize'] = 'none'
		self.fields['password'].widget.attrs['spellcheck'] = 'false'

	def clean_password(self):
		lang, password = self.lang, self.cleaned_data["password"]
		password = password.strip()
		if not password:
			raise ValidationError(retrieve_validation_error_string('pass_empty',lang=lang))
		lower_pass = password.lower()
		nickname = self.user.username
		lower_nick = nickname.lower()
		if len(password) < 6:
			raise ValidationError(retrieve_validation_error_string('pass_too_small',lang=lang))
		elif lower_pass in '1234567890':
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload=lower_pass))
		elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload=lower_pass))
		elif lower_nick in lower_pass:
			raise ValidationError(retrieve_validation_error_string('nickname_in_pass',lang=lang,payload=nickname))
		elif 'facebook' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='facebook'))
		elif 'damadam' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='damadam'))
		elif 'qwerty' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='qwerty'))
		elif 'babykobasspasandhai' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='babykobasspasandhai'))
		elif 'chaachi420' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='chaachi420'))
		elif 'garamaanday' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='garamaanday'))
		else:
			return password


	def save(self, commit=True):
		user = self.user
		password = self.cleaned_data["password"]
		user.set_password(password)
		if commit:
			user.save()
		return user


class ForgettersNicknameForm(forms.Form):
	username = forms.CharField(max_length=30)#,validators=[validate_whitespaces_in_nickname])
	class Meta:
		fields = ('username',)

	def __init__(self, *args, **kwargs):
		self.lang = kwargs.pop('lang',None)
		super(ForgettersNicknameForm, self).__init__(*args, **kwargs)
		self.fields['username'].error_messages = \
		{'required': retrieve_validation_error_string('required_new_nick',lang=self.lang),'invalid':retrieve_validation_error_string('invalid_new_nick',lang=self.lang)}
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #16d68a;'
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['username'].widget.attrs['autocomplete'] = 'off'
		self.fields['username'].widget.attrs['autocapitalize'] = 'none'
		self.fields['username'].widget.attrs['spellcheck'] = 'false'

	def clean_username(self):
		"""
		Validate that the username exists
		"""
		lang, username = self.lang, self.cleaned_data['username']
		username = username.strip()
		if not username:
			raise forms.ValidationError(retrieve_validation_error_string('required_visible_nick',lang=lang))
		else:
			validate_string_chars(username, BANNED_FORGOTTEN_NICKS, lang)
			exists = check_nick_status(nickname=username)
			if exists is True:
				try:
					# nick exists, try to retrieve the existing nickname's ID
					user_id = User.objects.only('id').get(username=username).id
				except User.DoesNotExist:
					raise forms.ValidationError(retrieve_validation_error_string('not_found',lang=lang,payload=username))
				return username, user_id
			elif exists is False:
				raise forms.ValidationError(retrieve_validation_error_string('not_found',lang=lang,payload=username))
			elif exists is '1':
				raise forms.ValidationError(retrieve_validation_error_string('bad_case',lang=lang,payload=username))
			elif exists is '0':
				#this shouldn't happen - the specific form of a nickname can't exist without its generic form in our DB
				pass
			elif exists is None:
				#the redis DB is compromised, use PSQL DB. Check nick against DB, that's it
				try:
					user_id = User.objects.only('id').get(username=username).id
				except User.DoesNotExist:
					raise forms.ValidationError(retrieve_validation_error_string('not_found',lang=lang,payload=username))
				return username, user_id

############################################################################################################

class SignInForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField()

	def __init__(self,*args,**kwargs):
		self.lang = kwargs.pop('lang',None)
		super(SignInForm, self).__init__(*args,**kwargs)
		self.fields['username'].error_messages = {'required':retrieve_validation_error_string('nick_empty',lang=self.lang)}
		self.fields['password'].error_messages = {'required':retrieve_validation_error_string('pass_empty',lang=self.lang)}
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #f9a61f;'
		self.fields['password'].widget.attrs['class'] = 'cxl'
		# self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'
		self.fields['password'].widget.attrs['autocapitalize'] = 'none'
		self.fields['password'].widget.attrs['spellcheck'] = 'false'
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #16d68a;'
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		# self.fields['username'].widget.attrs['autocomplete'] = 'off'
		self.fields['username'].widget.attrs['autocapitalize'] = 'none'
		self.fields['username'].widget.attrs['spellcheck'] = 'false'

	def clean(self):
		lang = self.lang
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		username = username.strip() if username else username
		password = password.strip() if password else password
		if not username:
			raise forms.ValidationError(retrieve_validation_error_string('required_visible_nick',lang=lang))
		if not password:
			raise forms.ValidationError(retrieve_validation_error_string('required_visible_pass',lang=lang))
		exists = nick_already_exists(nickname=username)
		result = check_nick_status(nickname=username)
		if result is None:
			# if 'nicknames' sorted set does not exist
			try:
				User._default_manager.get(username=username)
			except User.DoesNotExist:
				raise forms.ValidationError(retrieve_validation_error_string('not_found',lang=lang,payload=username))
		elif result is True:
			pass
		elif result is False:
			raise forms.ValidationError(retrieve_validation_error_string('not_found',lang=lang,payload=username))
		elif result == '0':
			raise forms.ValidationError(retrieve_validation_error_string('not_found',lang=lang,payload=username))
		elif result == '1':
			# the 'case' of the nickname is incorrect
			raise forms.ValidationError(retrieve_validation_error_string('bad_case',lang=lang,payload=username))
		if username and password:
			user = authenticate(username=username,password=password)
			if user is None:
				raise forms.ValidationError(retrieve_validation_error_string('wrong_pass_input',lang=lang))
			elif not user.is_active:
				raise forms.ValidationError(self.error_messages['inactive'])
			else:
				return user

############################################################################################################

class CreateAccountForm(forms.ModelForm):
	username = forms.RegexField(max_length=30,regex=re.compile('^[\w.@+-]+$'))
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('username',)

	def __init__(self,*args,**kwargs):
		self.lang = kwargs.pop('lang',None)
		super(CreateAccountForm, self).__init__(*args,**kwargs)
		self.fields['username'].error_messages = {'invalid': retrieve_validation_error_string('generic_nickname_error',lang=self.lang)}
		self.fields['password'].error_messages = {'required':retrieve_validation_error_string('pass_empty',lang=self.lang)}

	def clean_username(self):
		lang, username = self.lang, self.cleaned_data.get("username")
		if len(username) < 2:
			raise ValidationError(retrieve_validation_error_string('nick_too_small',lang=lang))
		elif username.isdigit():
			# the username is only made up of numbers, disallow
			raise ValidationError(retrieve_validation_error_string('nick_only_has_digits',lang=lang))
		else:
			exists = nick_already_exists(nickname=username)
			if exists is None:
				# if 'nicknames' redis sorted set does not exist, resort to PSQL
				try:
					User._default_manager.get(username=username)
				except User.DoesNotExist:
					return username
				raise ValidationError(retrieve_validation_error_string('nick_recently_taken',lang=lang,payload=username))
			elif exists:
				raise ValidationError(retrieve_validation_error_string('nick_recently_taken',lang=lang,payload=username))
			else:
				return username

	def clean_password(self):
		lang, password = self.lang, self.cleaned_data.get("password")
		lower_pass = password.lower()
		if len(password) < 6:
			raise ValidationError(retrieve_validation_error_string('pass_too_small',lang=lang))
		elif lower_pass in '1234567890':
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload=lower_pass))
		elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload=lower_pass))
		elif 'facebook' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='facebook'))
		elif 'damadam' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='damadam'))
		elif 'qwerty' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='qwerty'))
		elif 'babykobasspasandhai' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='babykobasspasandhai'))
		elif 'chaachi420' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='chaachi420'))
		elif 'garamaanday' in lower_pass:
			raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='garamaanday'))
		return password

	def save(self, commit=True):
		user = super(CreateAccountForm, self).save(commit=False)
		password = self.cleaned_data["password"]
		user.set_password(password)
		if commit:
			with transaction.commit_on_success():
				user.save()
				insert_nick(self.cleaned_data.get("username"))
		return user

############################################################################################################

class CreatePasswordForm(forms.Form):
	username = forms.RegexField(max_length=30,regex=re.compile('^[\w.@+-]+$'))
	password = forms.CharField()
	class Meta:
		fields = ('password','username')

	def __init__(self,*args,**kwargs):
		self.lang = kwargs.pop('lang',None)
		super(CreatePasswordForm, self).__init__(*args,**kwargs)
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #16d68a;'
		self.fields['password'].error_messages = {'required': retrieve_validation_error_string('required_new_pass',lang=self.lang)}
		self.fields['password'].widget.attrs['class'] = 'cxl'
		self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'
		self.fields['password'].widget.attrs['autocapitalize'] = 'none'
		self.fields['password'].widget.attrs['spellcheck'] = 'false'

	def clean_username(self):
		return self.cleaned_data.get("username")

	def clean_password(self):
		password = self.cleaned_data.get("password")
		lang, password = self.lang, password.strip()
		if not password:
			raise ValidationError(retrieve_validation_error_string('required_visible_pass',lang=lang))
		else:
			lower_pass = password.lower()
			nickname = self.cleaned_data.get("username")
			lower_nick = nickname.lower()
			if len(password) < 6:
				raise ValidationError(retrieve_validation_error_string('pass_too_small',lang=lang))
			elif lower_pass in '1234567890':
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload=lower_pass))
			elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload=lower_pass))
			elif lower_nick in lower_pass:
				raise ValidationError(retrieve_validation_error_string('nickname_in_pass',lang=lang,payload=nickname))
			elif 'facebook' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='facebook'))
			elif 'damadam' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='damadam'))
			elif 'qwerty' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',lang=lang,payload='qwerty'))
			elif 'babykobasspasandhai' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='babykobasspasandhai'))
			elif 'chaachi420' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='chaachi420'))
			elif 'garamaanday' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',lang=lang,payload='garamaanday'))
			else:
				return password

############################################################################################################


def process_choices(alternatives):
	chunks = [alternatives[x:x+3] for x in xrange(0, len(alternatives), 3)]
	alt_choices = []
	for chunk in chunks:
		nicks = bulk_nicks_exist(chunk)
		for nick in nicks:
			if not nick[1]:
				alt_choices.append(nick[0])
			if len(alt_choices) > 2:
				return alt_choices
	return alt_choices


def form_variants(username):
	"""
	Give suggestions of possible nicknames - for nicks with spaces
	"""
	words = username.split()
	first, fusable = True, []
	for word in words:
		if first:
			if word[-1] not in ['-','_','.','+']:
				fusable.append(word)
		else:
			if word[-1] not in ['-','_','.','+'] and word[0] not in ['-','_','.','+']:
				fusable.append(word)
		first = False
	len_fusable = len(fusable)
	if len_fusable > 1:
		return ['_'.join(fusable),'.'.join(fusable),'-'.join(fusable),''.join(fusable),\
		'-'.join(fusable)+'-pk','-'.join(fusable)+'-me','-'.join(fusable)+'-hi','-'.join(fusable)+'-007',\
		'_'.join(fusable)+'_pk','_'.join(fusable)+'_me','_'.join(fusable)+'_hi','_'.join(fusable)+'_007',\
		''.join(fusable)+'-pk',''.join(fusable)+'-me',''.join(fusable)+'-hi',''.join(fusable)+'-007']# 16 suggestions
	else:
		# nothing is fusable
		first = fusable[0] if len_fusable == 1 else words[0]
		return [first+"33",first+"me",first+"22",first+"00",first+"44",first+"55",first+"66",first+'77',first+"88",first+"99",\
		first+"11",first+"pk",first+"786",first+"007","king"+first]#14 suggestions

# for nicks without spaces
def form_suggestions(username):
	last_letter = username[-1]
	if len(username) < 3: #small nickname
		if last_letter.isdigit():
			# return [username+'_pk']
			return [username+'_pk',username+'_hi',username+'_me',username+'hi',\
			username+'me',username+'pk',username+'-hi',username+'-me',\
			username+'.hi',username+'.me',username+'-pk'] #11 suggestions
		elif last_letter in ['-','.','_','+']:
			return [username+'1',username+'2',username+'3',username+'4',\
			username+'5',username+'6',username+'7',username+'8',username+'9',\
			username+'0',username+'007',username+'786'] #12 suggestions
		else:
			return [username+'1',username+'2',username+'3',username+'4',\
			username+'5',username+'6',username+'7',username+'8',username+'9',\
			username+'0',username+'007',username+'786'] #12 suggestions
	elif last_letter.isdigit():
		return [username+'_pk',username+'_me',username+'_hi',username+'pk',\
		'mr_'+username,'am_'+username,username+'_pm',username+'hum',\
		username+'-pk',username+'_00',username+'oye',username+'_007',\
		username+'pak',username+'.me',username+'.hi',username+'_yo'] #16 suggestions
	elif last_letter in ['-','.','_','+']:
		return [username+'11',username+'22',username+'33',username+'44',\
		username+'55',username+'66',username+'77',username+'88',\
		username+'99',username+'00',username+'007',username+'786'] #12 suggestions
	else:
		return [username+'786',username+'-11',username+'22',username+'_22',\
		'mr_'+username,username+'33',username+'_33',username+'44',\
		username+'_44',username+'55',username+'_55',username+'66',\
		username+'_66',username+'77',username+'_77',username+'88',\
		username+'_88',username+'99',username+'_99',username+'00',\
		username+'_00',username+'007',username+'_007',username+'11',\
		username+'_786',username+'.11',username+'_11',username+'.22',\
		username+'-22',username+'.33',username+'-33',username+'.44',\
		username+'-44',username+'.55',username+'-55',username+'.66',\
		username+'-66',username+'.77',username+'-77',username+'.88',\
		username+'-88',username+'.99',username+'-99',username+'.00',\
		username+'-00',username+'.007',username+'-007',username+'.786',\
		username+'-786'] #49 suggestions


class CreateNickNewForm(forms.Form):
	username = forms.CharField(max_length=30)
	class Meta:
		fields = ('username',)

	def __init__(self, *args, **kwargs):
		self.lang = kwargs.pop('lang',None)
		super(CreateNickNewForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:100%;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #16d68a;'
		self.fields['username'].error_messages = \
		{'required': retrieve_validation_error_string('required_new_nick',lang=self.lang),'invalid':retrieve_validation_error_string('invalid_new_nick',lang=self.lang)}
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['username'].widget.attrs['autocomplete'] = 'off'
		self.fields['username'].widget.attrs['autocapitalize'] = 'none'
		self.fields['username'].widget.attrs['spellcheck'] = 'false'

	def clean_username(self):
		"""
		Validate that the username is not already in use, etc.
		'status':'joined' the nickname has been concatenated together, removing any whitespaces
		'status':'replaced' means the nickname has been replaced by a different one
		"""
		username = self.cleaned_data['username']
		lang, username = self.lang, username.strip()
		if not username:
			raise ValidationError(retrieve_validation_error_string('required_visible_nick',lang=lang))
		len_uname = len(username)
		

		# ENRICH WITH MORE POWERFUL NICKNAME VALIDATION CHECKS
		if len_uname < 2:
			raise ValidationError(retrieve_validation_error_string('nick_too_small',lang=lang))
		if username.isdigit():
			# the username is only made up of numbers, disallow
			raise ValidationError(retrieve_validation_error_string('nick_only_has_digits',lang=lang))
		elif username == username[0]*len_uname: #checks if it's a string made of a single character
			raise ValidationError(retrieve_validation_error_string('repeating_sequence_in_nick',lang=lang))
		elif username[:1] == '.':
			raise ValidationError(retrieve_validation_error_string('dot_at_nick_start',lang=lang))
		elif username[-1:] == '.':
			raise ValidationError(retrieve_validation_error_string('dot_at_nick_end',lang=lang))
		elif username[:1] == '-':
			raise ValidationError(retrieve_validation_error_string('dash_at_nick_start',lang=lang))
		elif username[-1:] == '-':
			raise ValidationError(retrieve_validation_error_string('dash_at_nick_end',lang=lang))
		elif username[:1] == '+':
			raise ValidationError(retrieve_validation_error_string('plus_at_nick_start',lang=lang))
		elif username[-1:] == '+':
			raise ValidationError(retrieve_validation_error_string('plus_at_nick_end',lang=lang))
		elif username[:1] == '_':
			raise ValidationError(retrieve_validation_error_string('uscore_at_nick_start',lang=lang))
		elif username[-1:] == '_':
			raise ValidationError(retrieve_validation_error_string('uscore_at_nick_end',lang=lang))
		elif '..' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='..'))
		elif '--' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='--'))
		elif '__' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='__'))
		elif '++' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='++'))
		elif '+.' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='+.'))
		elif '+-' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='+-'))
		elif '+_' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='+_'))
		elif '.+' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='.+'))
		elif '-+' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='-+'))
		elif '_+' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='_+'))
		elif '-.' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='-.'))
		elif '-_' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='-_'))
		elif '.-' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='.-'))
		elif '_-' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='_-'))
		elif '_.' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='_.'))
		elif '._' in username:
			raise ValidationError(retrieve_validation_error_string('banned_sequence_in_nick',lang=lang,payload='._'))
		
		validate_string_chars(username, BANNED_NICKS, lang)

		exists = nick_already_exists(nickname=username)
		altered = {}
		if exists is None:
			#the redis DB is compromised, use PSQL DB. Check nick against DB, that's it (can't give suggestions)
			if ' ' in username:
				username_original = username
				username = ''.join(username.split())
				altered = {'status':'joined'}
				if User.objects.filter(username__iexact=username).exists():
					raise ValidationError(retrieve_validation_error_string('nick_is_taken',lang=lang,payload=username_original))
			else:
				if User.objects.filter(username__iexact=username).exists():
					raise ValidationError(retrieve_validation_error_string('nick_is_taken',lang=lang,payload=username))
			return [username], altered, username
		############################################
		else:
			# form variants and suggestions
			# check all against redis DB
			if ' ' in username:
				alternatives = form_variants(username) #returns list of tuples containing variants and their statuses
				alt_choices = process_choices(alternatives)
				if not alt_choices:
					# no suggestions could be unearthed
					raise ValidationError(retrieve_validation_error_string('nick_is_taken',lang=lang,payload=username))
				else:
					# some suggestions unearthed
					altered = {'status':'joined'}
					return alt_choices, altered, username
			else:
				if exists:
					# nick is not available
					alternatives = form_suggestions(username) #returns list of tuples containing suggestions and their statuses
					alt_choices = process_choices(alternatives)
					if not alt_choices:
						raise ValidationError(retrieve_validation_error_string('nick_is_taken',lang=lang,payload=username))
					else:
						altered = {'status':'replaced'}
						return alt_choices, altered, username
				else:
					#nick is available
					return [username], altered, username

############################################################################################################