# coding=utf-8
from django import forms
from django.forms import Textarea
from django.core import validators
from django.core import validators
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from page_controls import DEFENDER_BLOCK_REASON_LEN
from django.utils.translation import ugettext, ugettext_lazy as _
from redis7 import is_rate_limited_from_adding_defender, in_defenders
from redis3 import is_mobile_verified
from forms import clear_zalgo_text

class PhotoReportForm(forms.Form):
	description = forms.CharField(widget=forms.Textarea(attrs=\
		{'style':'max-width:90%;height:120px;background-color:#F8F8F8;border: 1px solid red;border-radius:5px;color: #404040;'}),\
		error_messages={'required':"Report ko khali nahi chorein"})
	class Meta:
		fields = ("description",)

	def __init__(self, *args, **kwargs):
		super(PhotoReportForm, self).__init__(*args, **kwargs)
		self.fields['description'].widget.attrs['class'] = 'cxl'
		self.fields['description'].widget.attrs['autofocus'] = 'autofocus'

	def clean_description(self):
		description = self.cleaned_data.get("description")
		description = description.strip()
		length = len(description)
		if length < 5:
			raise forms.ValidationError('Itni choti report nahi likh sakte')
		elif length > 150:
			raise forms.ValidationError('150 chars se ziyada nah hon, ap ne {} chars likhay'.format(length))
		return clear_zalgo_text(description)


class RemDefenderIDForm(forms.Form):
	defender_id = forms.CharField(max_length=50)

	class Meta:
		fields = ("defender_id",)

	def __init__(self, *args, **kwargs):
		self.user_id = kwargs.pop('user_id',None)
		super(RemDefenderIDForm, self).__init__(*args, **kwargs)
		self.fields['defender_id'].widget.attrs['class'] = 'cxl'
		self.fields['defender_id'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['defender_id'].widget.attrs['autocomplete'] = 'off'
		self.fields['defender_id'].widget.attrs['style'] = 'max-width:90%;background-color:#F8F8F8;border: 1px solid lightgray;border-radius:5px;color: #404040;height:30px'

	def clean_defender_id(self):
		defender_id = self.cleaned_data.get("defender_id")
		defender_id = defender_id.strip()
		try:
			defender_id = int(defender_id)
		except (ValueError,TypeError):
			raise forms.ValidationError('Invalid entry')
		if defender_id == 1:
			# cannot act upon super user
			raise forms.ValidationError('Unable to compute')
		else:
			is_defender = in_defenders(defender_id)
			if is_defender:
				return defender_id
			else:
				# not a defender, can't remove
				raise forms.ValidationError('Unsubstantiated')


class AddDefenderIDForm(forms.Form):
	defender_id = forms.CharField(max_length=50)

	class Meta:
		fields = ("defender_id",)

	def __init__(self, *args, **kwargs):
		self.user_id = kwargs.pop('user_id',None)
		super(AddDefenderIDForm, self).__init__(*args, **kwargs)
		self.fields['defender_id'].widget.attrs['class'] = 'cxl sp'
		self.fields['defender_id'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['defender_id'].widget.attrs['autocomplete'] = 'off'
		self.fields['defender_id'].widget.attrs['style'] = 'max-width:90%;background-color:#F8F8F8;border: 1px solid lightgray;border-radius:5px;color: #404040;height:30px'

	def clean_defender_id(self):
		defender_id = self.cleaned_data.get("defender_id")
		defender_id = defender_id.strip()
		is_rl = is_rate_limited_from_adding_defender(self.user_id)
		if is_rl:
			# disallow due to hitting rate limit
			raise forms.ValidationError('You have been removed from the system')
		else:
			try:
				defender_id = int(defender_id)
			except (ValueError,TypeError):
				raise forms.ValidationError('Invalid entry')
			if not is_mobile_verified(defender_id):
				# not mobile verified - disallow
				raise forms.ValidationError('Mobile verification non-existent')
			elif in_defenders(defender_id):
				# already a defender
				raise forms.ValidationError('Duplication of effort')
			elif not User.objects.filter(id=defender_id).exists():
				# defender id is invalid
				raise forms.ValidationError('Hypothetical entity')
			else:
				return defender_id


class DefenderBlockingReasonForm(forms.Form):
	"""
	Handles text written by defender when blocking a user
	"""
	text = forms.CharField(widget=forms.Textarea(attrs={'class': 'cxl','autocomplete': 'off','autofocus': 'autofocus',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':DEFENDER_BLOCK_REASON_LEN}),\
	error_messages={'invalid':"Reason sahi se likhein",'required':"Reason dena lazmi hai takey users apni ghaltiyun se seekhain"})


	def __init__(self,*args,**kwargs):
		super(DefenderBlockingReasonForm, self).__init__(*args,**kwargs)
		self.fields['text'].widget.attrs['style'] = 'width:99%;height:100px;border-radius:10px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_text(self):
		text = self.cleaned_data.get("text").strip()
		text_len = len(text)
		if text_len > DEFENDER_BLOCK_REASON_LEN:
			raise forms.ValidationError('Reason {0} chars se chota likhein. Abhi {1} chars hai'.format(DEFENDER_BLOCK_REASON_LEN,text_len))
		elif text_len < 1:
			raise forms.ValidationError('Reason dena lazmi hai takey users apni ghaltiyun se seekhain')
		elif text_len < 6:
			raise forms.ValidationError('Reason itna chota nahi ho sakta')
		return clear_zalgo_text(text)