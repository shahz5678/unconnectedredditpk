from django import forms
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .redis3 import nick_already_exists,insert_nick, bulk_nicks_exist, log_erroneous_passwords, check_nick_status
from abuse import BANNED_WORDS
import re


class ResetForgettersPasswordForm(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput(),error_messages={'required':"Safed patti mein password likho:"})
	class Meta:
		fields = ('password',)

	def __init__(self,*args,**kwargs):
		self.user = kwargs.pop('user',None)
		super(ResetForgettersPasswordForm, self).__init__(*args,**kwargs)
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['password'].widget.attrs['class'] = 'cxl'
		self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'

	def clean_password(self):
		password = self.cleaned_data["password"]
		password = password.strip()
		lower_pass = password.lower()
		nickname = self.user.username
		lower_nick = nickname.lower()
		if len(password) < 6:
			raise ValidationError('Kam se kam 6 harf likhna zaruri hai!')
		elif lower_pass in '1234567890':
			raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho'  % lower_pass)
		elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
			raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho'  % lower_pass)
		elif lower_nick in lower_pass:
			raise ValidationError('"%s" nahi likh sakte kiyunke naam mein hai' % nickname)
		elif 'damadam' in lower_pass:
			raise ValidationError('"damadam" ko boojhna aasan hai, kuch aur likho')
		elif 'qwerty' in lower_pass:
			raise ValidationError('"qwerty" ko boojhna aasan hai, kuch aur likho')
		return password


	def save(self, commit=True):
		user = self.user
		password = self.cleaned_data["password"]
		user.set_password(password)
		if commit:
			user.save()
		return user

############################################################################################################

class SignInForm(forms.Form):
	username = forms.CharField(max_length=30,error_messages={'required': "naam khali nah choro"})
	password = forms.CharField(error_messages={'required':"password khali nah choro"})

	def __init__(self,*args,**kwargs):
		super(SignInForm, self).__init__(*args,**kwargs)
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #f9a61f;'
		self.fields['password'].widget.attrs['class'] = 'cxl'
		# self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		# self.fields['username'].widget.attrs['autocomplete'] = 'off'

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		if not username:
			raise forms.ValidationError('naam khali nah choro')
		if not password:
			raise forms.ValidationError('password khali nah choro')
		username = username.strip()
		password = password.strip()
		exists = nick_already_exists(nickname=username)
		result = check_nick_status(nickname=username)
		if result is None:
			# if 'nicknames' sorted set does not exist
			try:
				User._default_manager.get(username=username)
			except User.DoesNotExist:
				raise forms.ValidationError('"%s" naam hamarey record mein nahi' % username)
		elif result is True:
			pass
		elif result is False:
			raise forms.ValidationError('"%s" naam hamarey record mein nahi' % username)
		elif result == '0':
			raise forms.ValidationError('"%s" naam hamarey record mein nahi' % username)
		elif result == '1':
			raise forms.ValidationError('"%s" naam mein harf ghalat hain. Shayed chota harf bara likh diya hai, ya bara harf chota' % username)
		if username and password:
		    user = authenticate(username=username,password=password)
		    if user is None:
		        raise forms.ValidationError('Password sahi nahi. Agr bhool gaye ho tou neechay "Password yad nahi" pe jao')
		    elif not user.is_active:
		        raise forms.ValidationError(self.error_messages['inactive'])
		    else:
		    	return user

############################################################################################################

class CreateAccountForm(forms.ModelForm):
	username = forms.RegexField(max_length=30,regex=re.compile('^[\w.@+-]+$'),error_messages={'invalid': "ye naam sahi nahi hai"})
	password = forms.CharField(widget=forms.PasswordInput(),error_messages={'required':"password khali nah choro"})
	class Meta:
		model = User
		fields = ('username',)

	def clean_username(self):
		username = self.cleaned_data.get("username")
		exists = nick_already_exists(nickname=username)
		if exists is None:
			# if 'nicknames' sorted set does not exist
			try:
				User._default_manager.get(username=username)
			except User.DoesNotExist:
				return username
			raise forms.ValidationError('%s naam tum se pehle kisi aur ne rakh liya' % username)
		elif exists:
			raise forms.ValidationError('%s naam tum se pehle kisi aur ne rakh liya' % username)
		else:
			return username

	def clean_password(self):
		password = self.cleaned_data.get("password")
		lower_pass = password.lower()
		if len(password) < 6:
			raise ValidationError('password mein kam se kam 6 harf zaruri hai')
		elif lower_pass in '1234567890':
			raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho' % lower_pass)
		elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
			raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho'  % lower_pass)
		elif 'damadam' in lower_pass:
			raise ValidationError('"damadam" ko boojhna aasan hai, kuch aur likho')
		elif 'qwerty' in lower_pass:
			raise ValidationError('"qwerty" ko boojhna aasan hai, kuch aur likho')	
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
	password = forms.CharField(widget=forms.PasswordInput(),error_messages={'required':"Safed patti mein password likho:"})
	class Meta:
		fields = ('password','username')

	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request',None)
		super(CreatePasswordForm, self).__init__(*args,**kwargs)
		# self.fields['password'].widget.attrs['style'] = 'max-width:95%;'
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:95%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['password'].widget.attrs['class'] = 'cxl'
		self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'

	def clean_username(self):
		return self.cleaned_data.get("username")

	def clean_password(self):
		password = self.cleaned_data.get("password")
		password = password.strip()
		lower_pass = password.lower()
		nickname = self.cleaned_data.get("username")
		lower_nick = nickname.lower()
		if len(password) < 6:
			raise ValidationError('Kam se kam 6 harf likhna zaruri hai!')
		elif lower_pass in '1234567890':
			raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho' % lower_pass)
		elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
			raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho'  % lower_pass)
		elif lower_nick in lower_pass:
			raise ValidationError('"%s" nahi likh sakte kiyunke naam mein hai' % nickname)
		elif 'damadam' in lower_pass:
			raise ValidationError('"damadam" ko boojhna aasan hai, kuch aur likho')
		elif 'qwerty' in lower_pass:
			raise ValidationError('"qwerty" ko boojhna aasan hai, kuch aur likho')	
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

def validate_nickname_chars(value):
	reg = re.compile('^[\w\s.@+-]+$')
	if not reg.match(value):
		raise ValidationError('Naam mein sirf english harf, number ya @ _ . + - ho sakta hai')
	for name in BANNED_WORDS:
		if name in value.lower():
			raise ValidationError('Naam mein "%s" nahi ho sakta!' % name)

# for nicks with spaces
def form_variants(username):
	if username[-1].isdigit():
		words = username.split()
		return ['_'.join(words),'.'.join(words),''.join(words),'-'.join(words),\
		''.join(words)+'_hi',''.join(words)+'_me',''.join(words)+'_pk',''.join(words)+'_007',\
		'_'.join(words)+'_me','_'.join(words)+'_hi','_'.join(words)+'_007','_'.join(words)+'_pk'] #14 suggestions
	else:
		words = username.split()
		return ['_'.join(words),'.'.join(words),''.join(words),'-'.join(words),\
		''.join(words)+'11',''.join(words)+'_11',\
		''.join(words)+'22',''.join(words)+'_22',\
		''.join(words)+'33',''.join(words)+'_33',\
		''.join(words)+'44',''.join(words)+'_44',\
		''.join(words)+'55',''.join(words)+'_55',\
		''.join(words)+'66',''.join(words)+'_66',\
		''.join(words)+'77',''.join(words)+'_77',\
		''.join(words)+'007',''.join(words)+'_007',\
		''.join(words)+'786',''.join(words)+'_786'] #22 suggestions

# for nicks without spaces
def form_suggestions(username):
	if len(username) < 3: #small nickname
		if username[-1].isdigit():
			# return [username+'_pk']
			return [username+'_pk',username+'_hi',username+'_me',username+'hi',\
			username+'me',username+'pk',username+'-hi',username+'-me',\
			username+'.hi',username+'.me',username+'-pk'] #11 suggestions
		else:
			return [username+'1',username+'2',username+'3',username+'4',\
			username+'5',username+'6',username+'7',username+'8',username+'9',\
			username+'0',username+'007',username+'786'] #12 suggestions
	elif username[-1].isdigit():
		return [username+'_pk',username+'_me',username+'_hi',username+'pk',\
		'mr_'+username,'am_'+username,username+'_pm',username+'hum',\
		username+'-pk',username+'_00',username+'oye',username+'_007',\
		username+'pak',username+'.me',username+'.hi',username+'_yo'] #16 suggestions
	else:
		return [username+'11',username+'_11',username+'22',username+'_22',\
		'mr_'+username,username+'33',username+'_33',username+'44',\
		username+'_44',username+'55',username+'_55',username+'66',\
		username+'_66',username+'77',username+'_77',username+'88',\
		username+'_88',username+'99',username+'_99',username+'00',\
		username+'_00',username+'007',username+'_007',username+'786',\
		username+'_786',username+'.11',username+'-11',username+'.22',\
		username+'-22',username+'.33',username+'-33',username+'.44',\
		username+'-44',username+'.55',username+'-55',username+'.66',\
		username+'-66',username+'.77',username+'-77',username+'.88',\
		username+'-88',username+'.99',username+'-99',username+'.00',\
		username+'-00',username+'.007',username+'-007',username+'.786',\
		username+'-786'] #49 suggestions

class CreateNickNewForm(forms.Form):
	username = forms.CharField(max_length=30,error_messages={'invalid': "Naam mein sirf english harf, number ya @ _ . + - ho sakta hai",\
		'required':"Is safed patti mein naam likh kar OK dabao:"})#,validators=[validate_whitespaces_in_nickname])
	class Meta:
		fields = ('username',)

	def __init__(self, *args, **kwargs):
		super(CreateNickNewForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['username'].widget.attrs['autocomplete'] = 'off'

	def clean_username(self):
		"""
		Validate that the username is not already in use, etc.
		'status':'joined' the nickname has been concatenated together, removing any whitespaces
		'status':'replaced' means the nickname has been replaced by a different one
		"""
		username = self.cleaned_data['username']
		username = username.strip()
		validate_nickname_chars(username)
		exists = nick_already_exists(nickname=username)
		altered = {}
		if exists is None:
			#the redis DB is compromised, use PSQL DB. Check nick against DB, that's it
			if ' ' in username:
				username_original = username
				username = ''.join(username.split())
				altered = {'status':'joined'}
				if User.objects.filter(username__iexact=username).exists():
					raise ValidationError('"%s" kisi aur ka naam hai. Kuch aur likho' % username_original)
			else:
				if User.objects.filter(username__iexact=username).exists():
					raise ValidationError('"%s" kisi aur ka naam hai. Kuch aur likho' % username)
			return [username], altered, username
		############################################
		else:
			# form variants and suggestions
			# check al against redis DB
			if ' ' in username:
				alternatives = form_variants(username) #returns list of tuples containing variants and their statuses
				alt_choices = process_choices(alternatives)
				if not alt_choices:
					# no suggestions could be unearthed
					raise ValidationError('"%s" kisi aur ka naam hai. Kuch aur likho' % username)
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
						raise ValidationError('"%s" kisi aur ka naam hai. Kuch aur likho' % username)
					else:
						altered = {'status':'replaced'}
						return alt_choices, altered, username
				else:
					#nick is available
					# altered = False
					return [username], altered, username

############################################################################################################