import unicodedata, re
from django import forms
from django.forms import Textarea
from django.core.exceptions import ValidationError
from django.core import validators
from django.utils.translation import ugettext, ugettext_lazy as _

def clear_zalgo_text(text):
	return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))

class WebsiteChoicesFeedbackForm(forms.Form):
	CHOICES1 = (('a','Users ki baatein parhna'),
			   ('b','Home pe laggi photos dekhna'),
			   ('c','Jhappi/Chupair'),
			   ('d','Jawab dena'),
			   ('e','Points banana'),
			   ('f','Welcome mithai bhejna'),)
	CHOICES2 = (('a','Home'),
			   ('b','Photos'),
			   ('c','Open Mehfil'),
			   ('d','Private Mehfil'),
			   ('e','Matka'),)
	CHOICES3 = (('a','Home ki chat pe'),
			   ('b','Open mehfil ki chat mein'),
			   ('c','Prvaite mehfil ki chat mein'),
			   ('d','Photo tabsrey mein'),
			   ('e','Jawab do mein'),
			   ('e','Chupeir maar ke'),)
	CHOICES4 = (('a','Block system'),
			   ('b','Videos'),
			   ('c','Friend list'),
			   ('d','Search'),
			   ('e','Private photos'),)
	CHOICES5 = (('a','Koi jawab nahi deta'),
			   ('b','Points ke liye users bar bar fazool cheezain likhte hai'),
			   ('c','Gandey names ya gandi baatein likhtay hain users'),)
	CHOICES6 = (('a','Home pe kuch likh ke'),
			   ('b','Home pe jawab de ke'),
			   ('c','Open mehfil mein gup ghup lafa ke'),
			   ('d','Private mehfil mein guo '),
			   ('e','Photo tabsra kartay huay'),)
	feedback1 = forms.MultipleChoiceField(choices=CHOICES1, widget=forms.CheckboxSelectMultiple())
	feedback2 = forms.MultipleChoiceField(choices=CHOICES2, widget=forms.CheckboxSelectMultiple())
	feedback3 = forms.MultipleChoiceField(choices=CHOICES3, widget=forms.CheckboxSelectMultiple())
	feedback4 = forms.MultipleChoiceField(choices=CHOICES4, widget=forms.CheckboxSelectMultiple())
	feedback5 = forms.MultipleChoiceField(choices=CHOICES5, widget=forms.CheckboxSelectMultiple())
	feedback6 = forms.MultipleChoiceField(choices=CHOICES6, widget=forms.CheckboxSelectMultiple())

	def clean_feedback1(self):
		if len(self.cleaned_data['feedback1']) > 3:
			raise forms.ValidationError('3 se ziyada select na karo')
		return self.cleaned_data['feedback1']

	def clean_feedback2(self):
		if len(self.cleaned_data['feedback2']) > 3:
			raise forms.ValidationError('3 se ziyada select na karo')
		return self.cleaned_data['feedback2']

	def clean_feedback3(self):
		if len(self.cleaned_data['feedback3']) > 3:
			raise forms.ValidationError('3 se ziyada select na karo')
		return self.cleaned_data['feedback3']

	def clean_feedback4(self):
		if len(self.cleaned_data['feedback4']) > 3:
			raise forms.ValidationError('3 se ziyada select na karo')
		return self.cleaned_data['feedback4']

	def clean_feedback5(self):
		if len(self.cleaned_data['feedback5']) > 3:
			raise forms.ValidationError('3 se ziyada select na karo')
		return self.cleaned_data['feedback5']

	def clean_feedback6(self):
		if len(self.cleaned_data['feedback6']) > 3:
			raise forms.ValidationError('3 se ziyada select na karo')
		return self.cleaned_data['feedback6']

class WebsiteDescriptiveFeedbackForm(forms.Form):
	feedback1 = forms.CharField(widget=forms.Textarea(attrs=\
		{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
		validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
		'required':_("(tip: isko khali nahi chore sakte)")})
	feedback2 = forms.CharField(widget=forms.Textarea(attrs=\
		{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
		validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
		'required':_("(tip: isko khali nahi chore sakte)")})
	feedback3 = forms.CharField(widget=forms.Textarea(attrs=\
		{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
		validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
		'required':_("(tip: isko khali nahi chore sakte)")})
	feedback4 = forms.CharField(widget=forms.Textarea(attrs=\
		{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
		validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
		'required':_("(tip: isko khali nahi chore sakte)")})
	feedback5 = forms.CharField(widget=forms.Textarea(attrs=\
		{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
		validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
		'required':_("(tip: isko khali nahi chore sakte)")})
	# feedback6 = forms.CharField(widget=forms.Textarea(attrs=\
	# 	{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
	# 	validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
	# 	'required':_("(tip: isko khali nahi chore sakte)")})
	# feedback7 = forms.CharField(widget=forms.Textarea(attrs=\
	# 	{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
	# 	validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
	# 	'required':_("(tip: isko khali nahi chore sakte)")})
	# feedback8 = forms.CharField(widget=forms.Textarea(attrs=\
	# 	{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
	# 	validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
	# 	'required':_("(tip: isko khali nahi chore sakte)")})
	# feedback9 = forms.CharField(widget=forms.Textarea(attrs=\
	# 	{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
	# 	validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
	# 	'required':_("(tip: isko khali nahi chore sakte)")})
	# feedback10 = forms.CharField(widget=forms.Textarea(attrs=\
	# 	{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
	# 	validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
	# 	'required':_("(tip: isko khali nahi chore sakte)")})
	class Meta:
		fields = ("feedback1","feedback2","feedback3","feedback4","feedback5",)
		# exclude = ("feedback6","feedback7","feedback8","feedback9","feedback10",)

	def __init__(self, *args, **kwargs):
		super(WebsiteDescriptiveFeedbackForm, self).__init__(*args, **kwargs)
		self.fields['feedback1'].widget.attrs['class'] = 'cxl'
		self.fields['feedback1'].widget.attrs['autocomplete'] = 'off'
		self.fields['feedback2'].widget.attrs['class'] = 'cxl'
		self.fields['feedback2'].widget.attrs['autocomplete'] = 'off'
		self.fields['feedback3'].widget.attrs['class'] = 'cxl'
		self.fields['feedback3'].widget.attrs['autocomplete'] = 'off'
		self.fields['feedback4'].widget.attrs['class'] = 'cxl'
		self.fields['feedback4'].widget.attrs['autocomplete'] = 'off'
		self.fields['feedback5'].widget.attrs['class'] = 'cxl'
		self.fields['feedback5'].widget.attrs['autocomplete'] = 'off'
		# self.fields['feedback6'].widget.attrs['class'] = 'cxl'
		# self.fields['feedback6'].widget.attrs['autocomplete'] = 'off'
		# self.fields['feedback7'].widget.attrs['class'] = 'cxl'
		# self.fields['feedback7'].widget.attrs['autocomplete'] = 'off'
		# self.fields['feedback8'].widget.attrs['class'] = 'cxl'
		# self.fields['feedback8'].widget.attrs['autocomplete'] = 'off'
		# self.fields['feedback9'].widget.attrs['class'] = 'cxl'
		# self.fields['feedback9'].widget.attrs['autocomplete'] = 'off'
		# self.fields['feedback10'].widget.attrs['class'] = 'cxl'
		# self.fields['feedback10'].widget.attrs['autocomplete'] = 'off'

	def clean_feedback1(self):
		feedback1 = self.cleaned_data.get("feedback1")
		feedback1 = feedback1.strip()
		if len(feedback1) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(feedback1) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		feedback1 = clear_zalgo_text(feedback1)
		return feedback1

	def clean_feedback2(self):
		feedback2 = self.cleaned_data.get("feedback2")
		feedback2 = feedback2.strip()
		if len(feedback2) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(feedback2) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		feedback2 = clear_zalgo_text(feedback2)
		return feedback2
		
	def clean_feedback3(self):
		feedback3 = self.cleaned_data.get("feedback3")
		feedback3 = feedback3.strip()
		if len(feedback3) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(feedback3) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		feedback3 = clear_zalgo_text(feedback3)
		return feedback3

	def clean_feedback4(self):
		feedback4 = self.cleaned_data.get("feedback4")
		feedback4 = feedback4.strip()
		if len(feedback4) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(feedback4) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		feedback4 = clear_zalgo_text(feedback4)
		return feedback4

	def clean_feedback5(self):
		feedback5 = self.cleaned_data.get("feedback5")
		feedback5 = feedback5.strip()
		if len(feedback5) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(feedback5) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		feedback5 = clear_zalgo_text(feedback5)
		return feedback5

	# def clean_feedback6(self):
	# 	feedback6 = self.cleaned_data.get("feedback6")
	# 	feedback6 = feedback6.strip()
	# 	if len(feedback6) < 5:
	# 		raise forms.ValidationError('(tip: is se ziyada likho)')
	# 	elif len(feedback6) > 250:
	# 		raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
	# 	feedback6 = clear_zalgo_text(feedback6)
	# 	return feedback6

	# def clean_feedback7(self):
	# 	feedback7 = self.cleaned_data.get("feedback7")
	# 	feedback7 = feedback7.strip()
	# 	if len(feedback7) < 5:
	# 		raise forms.ValidationError('(tip: is se ziyada likho)')
	# 	elif len(feedback7) > 250:
	# 		raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
	# 	feedback7 = clear_zalgo_text(feedback7)
	# 	return feedback7

	# def clean_feedback8(self):
	# 	feedback8 = self.cleaned_data.get("feedback8")
	# 	feedback8 = feedback8.strip()
	# 	if len(feedback8) < 5:
	# 		raise forms.ValidationError('(tip: is se ziyada likho)')
	# 	elif len(feedback8) > 250:
	# 		raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
	# 	feedback8 = clear_zalgo_text(feedback8)
	# 	return feedback8

	# def clean_feedback9(self):
	# 	feedback9 = self.cleaned_data.get("feedback9")
	# 	feedback9 = feedback9.strip()
	# 	if len(feedback9) < 5:
	# 		raise forms.ValidationError('(tip: is se ziyada likho)')
	# 	elif len(feedback9) > 250:
	# 		raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
	# 	feedback9 = clear_zalgo_text(feedback9)
	# 	return feedback9

	# def clean_feedback10(self):
	# 	feedback10 = self.cleaned_data.get("feedback10")
	# 	feedback10 = feedback10.strip()
	# 	if len(feedback10) < 5:
	# 		raise forms.ValidationError('(tip: is se ziyada likho)')
	# 	elif len(feedback10) > 250:
	# 		raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
	# 	feedback10 = clear_zalgo_text(feedback10)
	# 	return feedback10

class WebsiteFeedbackUserDetailsForm(forms.Form):
	Gender = (
		('1','Aurat'),
		('0','Mard'),
		)

	gender = forms.TypedChoiceField(choices=Gender, widget=forms.RadioSelect, coerce=int,error_messages={'required':_("isko khali nahi chore sakte")})
	mobile = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':1,'style':'max-width:80%;'}),\
		error_messages={'required':_("isko khali nahi chore sakte")})
	age = forms.CharField(widget=forms.Textarea(attrs={'cols':10,'rows':1,'style':'max-width:50%;'}),\
		error_messages={'required':_("isko khali nahi chore sakte")})
	loc = forms.RegexField(max_length=250,regex=re.compile("^[A-Za-z0-9._~()'!*:@, ;+?-]*$"),\
		error_messages={'invalid': _("sirf english harf, number ya @ _ . + - likh sakte ho"),\
		'required':_("isko khali nahi chore sakte")})

	def clean_gender(self):
		return self.cleaned_data.get("gender")

	def clean_mobile(self):
		mobile = self.cleaned_data.get("mobile")
		mobile = mobile.strip()
		if not mobile.isdigit():
			raise forms.ValidationError('number sahi se likho')
		if len(mobile) < 11:
			raise forms.ValidationError('poora mobile number likho!')
		mobile = clear_zalgo_text(mobile)
		return mobile

	def clean_age(self):
		age = self.cleaned_data.get("age")
		age = clear_zalgo_text(age)
		return age

	def clean_loc(self):
		loc = self.cleaned_data.get("loc")
		loc = loc.strip()
		loc = clear_zalgo_text(loc)
		if len(loc) < 3:
			raise forms.ValidationError('itna chota city ka naam nahi likh sakte!')
		elif loc.isdigit():
			raise ValidationError('city ke naam mein sirf numbers nahi ho sakte!')
		else:
			return loc

class AdvertiseWithUsForm(forms.Form):
	name = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':1,'style':'max-width:90%;'}),\
		error_messages={'required':_("isko khali nahi chore sakte")})
	detail = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':3,'style':'max-width:90%;'}),\
		error_messages={'required':_("isko khali nahi chore sakte")})
	mobile = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':1,'style':'max-width:90%;'}),\
		error_messages={'required':_("isko khali nahi chore sakte")})
	loc = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':1,'style':'max-width:90%;'}),\
		error_messages={'required':_("isko khali nahi chore sakte")})

	class Meta:
		fields = ("name","detail","mobile","loc",)

	def __init__(self, *args, **kwargs):
		super(AdvertiseWithUsForm, self).__init__(*args, **kwargs)
		self.fields['name'].widget.attrs['class'] = 'cxl'
		self.fields['name'].widget.attrs['autocomplete'] = 'off'
		self.fields['detail'].widget.attrs['class'] = 'cxl'
		self.fields['detail'].widget.attrs['autocomplete'] = 'off'
		self.fields['mobile'].widget.attrs['class'] = 'cxl'
		self.fields['mobile'].widget.attrs['autocomplete'] = 'off'
		self.fields['loc'].widget.attrs['class'] = 'cxl'
		self.fields['loc'].widget.attrs['autocomplete'] = 'off'

	def clean_mobile(self):
		mobile = self.cleaned_data.get("mobile")
		mobile = mobile.strip()
		if not mobile.isdigit():
			raise forms.ValidationError('number sahi se likhein')
		if len(mobile) < 11:
			raise forms.ValidationError('poora mobile number likhein')
		mobile = clear_zalgo_text(mobile)
		return mobile

	def clean_name(self):
		name = self.cleaned_data.get("name")
		name = name.strip()
		if name.isdigit():
			raise forms.ValidationError('name sahi se likhein')
		name = clear_zalgo_text(name)
		return name

	def clean_loc(self):
		loc = self.cleaned_data.get("loc")
		loc = loc.strip()
		loc = clear_zalgo_text(loc)
		if len(loc) < 3:
			raise forms.ValidationError('itna chota city name nahi likh sakte')
		elif loc.isdigit():
			raise ValidationError('city name mein sirf numbers nahi ho sakte')
		else:
			return loc

	def clean_detail(self):
		detail = self.cleaned_data.get("detail")
		detail = detail.strip()
		if detail.isdigit():
			raise forms.ValidationError('detail sahi se likhein')
		detail = clear_zalgo_text(detail)
		return detail