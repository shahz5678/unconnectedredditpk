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
	
	username = forms.RegexField(max_length=43, regex=re.compile("^[a-zA-Z\s]+$"),\
		error_messages={'invalid': _("Name mein sirf english harf ho sakta hai"),\
		'required':_("Is mein apna name likho")})
#	phonenumber = forms.CharField(max_length=11)#,validators=[validate_whitespaces_in_nickname])
	cnic = forms.CharField(max_length=13,error_messages={'required': 'CNIC number dena zaroori hai'})#,validators=[validate_whitespaces_in_nickname])
	city = forms.TypedChoiceField(choices=City, widget=forms.RadioSelect,error_messages={'required': 'In mein se aik chunno'})
	license = forms.TypedChoiceField(choices=License, widget=forms.RadioSelect,error_messages={'required': 'In mein se aik chunno'})
	class Meta:
		fields = ('username','cnic','city',license)

	def __init__(self, *args, **kwargs):
		super(CareemAdForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['username'].widget.attrs['class'] = 'cxl'
		self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['username'].widget.attrs['autocomplete'] = 'off'
		self.fields['cnic'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		self.fields['cnic'].widget.attrs['class'] = 'cxl'
		self.fields['cnic'].widget.attrs['autocomplete'] = 'off'

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if len(username) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(username) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		return username

	def clean_cnic(self):
		cnic = self.cleaned_data.get('cnic')
		if cnic == '3740523212212':
			raise forms.ValidationError('(tip: Asli shanakhti card ka number dalo)')
		return cnic

