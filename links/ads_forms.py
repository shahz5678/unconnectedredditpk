from django import forms
import re
from django.utils.translation import ugettext, ugettext_lazy as _

class CareemAdForm(forms.Form):
	City = (
		('Karachi','Karachi'),
		('Lahore','Lahore'),
		('Islamabad','Islamabad'),
		#('Rawalpindi','Rawalpindi'),
		# ('Hyderabad','Hyderabad'),
		# ('Faisalabad','Faisalabad'),
		# ('Multan','Multan'),
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
		# self.fields['phonenumber'].widget.attrs['style'] = \
		# 'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #00c853;'
		# self.fields['phonenumber'].widget.attrs['class'] = 'cxl'
		# self.fields['phonenumber'].widget.attrs['autocomplete'] = 'off'
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
#		username = clear_zalgo_text(feedback)
		return username

	def clean_cnic(self):
		cnic = self.cleaned_data.get('cnic')
		return cnic


# class VerifyMobileForm(forms.Form):
# 	mobile_number = forms.CharField(max_length=13,\
# 		error_messages={'required':_("Is mein mobile number likho")})

# 	def clean_mobile_number(self):
# 		mobile_number = self.cleaned_data.get("mobile_number")
# 		if mobile_number.isdigit():
# 			return mobile_number
# 		else:
# 			raise forms.ValidationError('Mobile number sahi nahi hai, dubara likho')

# class AdFeedbackForm(forms.Form):
# 	feedback = forms.CharField(widget=forms.Textarea(attrs=\
# 		{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
# 		validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
# 		'required':_("(tip: isko khali nahi chore sakte)")})
# 	class Meta:
# 		fields = ("feedback",)

# 	def __init__(self, *args, **kwargs):
# 		super(AdFeedbackForm, self).__init__(*args, **kwargs)
# 		self.fields['feedback'].widget.attrs['class'] = 'cxl'
# 		self.fields['feedback'].widget.attrs['autocomplete'] = 'off'

# 	def clean_feedback(self):
# 		feedback = self.cleaned_data.get("feedback")
# 		feedback = feedback.strip()
# 		if len(feedback) < 5:
# 			raise forms.ValidationError('(tip: is se ziyada likho)')
# 		elif len(feedback) > 250:
# 			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
# 		feedback = clear_zalgo_text(feedback)
# 		return feedback