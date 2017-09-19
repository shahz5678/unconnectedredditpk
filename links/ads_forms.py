from django import forms
import re
from django.utils.translation import ugettext, ugettext_lazy as _

class CareemAdForm(forms.Form):
	City = (
		('Karachi','Karachi'),
		('Lahore','Lahore'),
		('Islamabad','Islamabad'),
		('Peshawar','Peshawar'),
		('Koi aur','Koi aur'),
		)

	License = (
		('Yes','Yes'),
		('No','No'),
		)

	Car = (
		('Yes','Yes'),
		('No','No'),
		)


	username = forms.RegexField(max_length=43, regex=re.compile("^[a-zA-Z\s]+$"),\
		error_messages={'invalid': _("Name mein sirf english harf ho sakta hai"),\
		'required':_("Is mein apna name likho")})
#	phonenumber = forms.CharField(max_length=11)#,validators=[validate_whitespaces_in_nickname])
	phonenumber = forms.CharField(max_length=11,error_messages={'required': 'Mobile number diay gaiey tareekay say likhna zaroori hai'})#,validators=[validate_whitespaces_in_nickname])
	city = forms.TypedChoiceField(choices=City, widget=forms.RadioSelect,error_messages={'required': 'In mein se aik chunno'})
	license = forms.TypedChoiceField(choices=License, widget=forms.RadioSelect,error_messages={'required': 'In mein se aik chunno'})
	car = forms.TypedChoiceField(choices=Car, widget=forms.RadioSelect,error_messages={'required': 'In mein se aik chunno'})

	class Meta:
		fields = ('username','phonenumber','city','license','car')

	def __init__(self, *args, **kwargs):
		super(CareemAdForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['username'].widget.attrs['autocomplete'] = 'off'
		self.fields['phonenumber'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['phonenumber'].widget.attrs['class'] = 'cxl'
		self.fields['phonenumber'].widget.attrs['autocomplete'] = 'off'

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if len(username) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(username) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		return username



	def clean_phonenumber(self):
		phonenumber = self.cleaned_data.get("phonenumber")
		if phonenumber == '03451234567':
			raise forms.ValidationError('(tip: Apna asli phonenumber dalo)')
		mobile_length = len(phonenumber)
		if mobile_length < 11:
			raise forms.ValidationError('Poora mobile number likho')
		phonenumber = ''.join(re.split('[, \-_!?:]+',phonenumber)) #removes any excess characters from the mobile number
		return phonenumber[-11:]

class BuyerForm(forms.Form):

	username = forms.RegexField(max_length=43, regex=re.compile("^[a-zA-Z\s]+$"),\
		error_messages={'invalid': _("Name mein sirf english harf ho sakta hai"),\
		'required':_("Is mein apna name likhien")})
#	phonenumber = forms.CharField(max_length=11)#,validators=[validate_whitespaces_in_nickname])
	address = forms.RegexField(max_length=300, regex=re.compile("^[A-Za-z0-9999!-/@#,$%^&* ]+$"),\
		error_messages={'required':_("Is mein apna address likhien")})
	
	class Meta:
		fields = ('username','address')

	def __init__(self, *args, **kwargs):
		super(BuyerForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['username'].widget.attrs['autocomplete'] = 'off'
		self.fields['address'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['address'].widget.attrs['class'] = 'cxl'
		self.fields['address'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['address'].widget.attrs['autocomplete'] = 'off'

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if len(username) < 5:
			raise forms.ValidationError('(tip: apna poora naam likhien)')
		elif len(username) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota kerien)')
		return username

	def clean_address(self):
		address = self.cleaned_data.get('address')
		if len(address) < 10:
			raise forms.ValidationError('(tip: apna poora address bataien jiss per daak bheji ja sakey)')
		elif len(address) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karien)')
		return address


