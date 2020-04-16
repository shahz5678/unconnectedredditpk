import unicodedata
from django import forms
from django.core.exceptions import ValidationError
from page_controls import PERSONAL_GROUP_MAX_SMS_SIZE, PERSONAL_GROUP_MAX_PHOTO_CAPTION_SIZE


def clear_zalgo_text(text):
	return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))


class PersonalGroupPostForm(forms.Form):
	"""
	Handles personal group chat input
	"""
	image = forms.ImageField(required=False, error_messages={'invalid':'Ye photo kharab hai. Koi aur chunein',\
		'invalid_image': 'Ye photo kharab hai. Koi aur chunein','required':'Photo lagana zaruri hai'})
	reply = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols':30,'class': 'cxl inp','autocomplete': 'off',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false'}))
	

	def __init__(self,*args,**kwargs):
		self.on_fbs = kwargs.pop('on_fbs',None)
		super(PersonalGroupPostForm, self).__init__(*args,**kwargs)
		self.fields['reply'].widget.attrs['style'] = 'width:100%;height:60px;border-radius:6px;border: 1px #bdebfe solid; background-color:white;padding:5px;box-sizing:border-box'
		self.fields['reply'].widget.attrs['id'] = 'text_field'
		self.fields['image'].widget.attrs['id'] = 'browse_image_btn'
		self.fields['image'].widget.attrs['class'] = 'cam_img'

	def clean(self):
		data = self.cleaned_data
		reply = data["reply"].strip()
		if "image" not in data:
			raise forms.ValidationError('Ye photo kharab hai. Koi aur chunein')#checked
		elif not reply and not data["image"]:
			raise forms.ValidationError('Msg likhein ya photo lagain')#checked
		elif self.on_fbs and data["image"] and data["image"].size > 200000:
			raise forms.ValidationError('Ap ne %s KB ki photo chunni. Freebasics pe 200 KB se barri photo mana hai' % \
				format(float(data["image"].size)/1000,'.1f'))#checked
		elif not self.on_fbs and data["image"] and data["image"].size > 10000000:
			raise forms.ValidationError('Ap ne %s MB ki photo chunni. 10MB se barri photo nahi lagti' % \
				format(float(data["image"].size)/1000000,'.1f'))#checked
		elif data["image"] and data["image"].size == 0:
			raise forms.ValidationError('Ye photo kharab hai. Koi aur chunein')
		elif len(reply) > 1500:
			raise forms.ValidationError('1500 haroof se barri baat nah likhein')
		# data["reply"] = clear_zalgo_text(reply) if reply else reply
		return data


class PersonalGroupSharedPhotoCaptionForm(forms.Form):
	"""
	Handles personal group shared photo captions
	"""
	text = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3,'class': 'cxl','autocomplete': 'off','autocorrect':'off',\
		'autofocus': 'autofocus','autocapitalize':'off','spellcheck':'false','maxlength':PERSONAL_GROUP_MAX_PHOTO_CAPTION_SIZE}),\
	error_messages={'invalid':"Title sahi se likhein"})


	def __init__(self,*args,**kwargs):
		# self.on_fbs = kwargs.pop('on_fbs',None)
		super(PersonalGroupSharedPhotoCaptionForm, self).__init__(*args,**kwargs)
		self.fields['text'].required = False
		self.fields['text'].widget.attrs['style'] = 'width:95%;height:50px;border-radius:10px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px'

	def clean_text(self):
		text = self.cleaned_data.get("text").strip()
		if text:
			text_len = len(text)
			if text_len > PERSONAL_GROUP_MAX_PHOTO_CAPTION_SIZE:
				raise forms.ValidationError('Title {} characters se bara nahi likhein'.format(PERSONAL_GROUP_MAX_PHOTO_CAPTION_SIZE))
			return clear_zalgo_text(text)
		else:
			return ''


class PersonalGroupSMSForm(forms.Form):
	"""
	Handles personal group sms text
	"""
	sms = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3,'class': 'cxl','autocomplete': 'off','autofocus': 'autofocus',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':PERSONAL_GROUP_MAX_SMS_SIZE}),\
	error_messages={'invalid':"SMS sahi se likhein",'required':"SMS ko khali nahi chore sakte"})


	def __init__(self,*args,**kwargs):
		self.on_fbs = kwargs.pop('on_fbs',None)
		super(PersonalGroupSMSForm, self).__init__(*args,**kwargs)
		self.fields['sms'].widget.attrs['style'] = 'width:99%;height:50px;border-radius:10px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_sms(self):
		sms = self.cleaned_data.get("sms").strip()
		sms_len = len(sms)
		if sms_len > PERSONAL_GROUP_MAX_SMS_SIZE:
			raise forms.ValidationError('SMS 150 characters se bara nahi likh saktey')
		elif sms_len < 1:
			raise forms.ValidationError('SMS ko khali nahi chore saktey')
		elif sms_len < 6:
			raise forms.ValidationError('SMS itna chota nahi ho sakta')
		return clear_zalgo_text(sms)

######################## JS-powered direct response ###########################

class PersonalGroupReplyPostForm(forms.Form):
	"""
	Handles personal group chat reply input for JS-devices

	It populates input fields rendered by pressing the reply button under each post in a JS-enabled environment
	"""
	rep_image = forms.ImageField(required=False, error_messages={'invalid':'Ye photo kharab hai. Koi aur chunein',\
		'invalid_image': 'Ye photo kharab hai. Koi aur chunein'})
	rep_reply = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'cxl','autocomplete': 'off','autocorrect':'off',\
		'autocapitalize':'off','spellcheck':'false','placeholder':'Reply likhein...'}))
	

	def __init__(self,*args,**kwargs):
		self.on_fbs = kwargs.pop('on_fbs',None)
		super(PersonalGroupReplyPostForm, self).__init__(*args,**kwargs)
		self.fields['rep_reply'].widget.attrs['style'] = 'width:100%;height:60px;box-sizing: border-box;border-radius:8px;border: 1px #C9FFED solid; background-color:#FAFAFA;padding:5px;'
		self.fields['rep_reply'].widget.attrs['id'] = 'rep_text_field'
		# self.fields['rep_reply'].widget.attrs['class'] = 'inp'
		self.fields['rep_image'].widget.attrs['id'] = 'browse_rep_image_btn'
		self.fields['rep_image'].widget.attrs['style'] = 'width: 0.1px;height: 0.1px;opacity: 0;overflow: hidden;position: absolute;z-index: -1;'

	def clean(self):
		data = self.cleaned_data
		reply = data["rep_reply"].strip()
		if "rep_image" not in data:
			raise forms.ValidationError('Ye photo kharab hai. Koi aur chunein')#checked
		elif not reply and not data["rep_image"]:
			raise forms.ValidationError('Chat likhein ya photo lagain')#checked
		elif self.on_fbs and data["rep_image"] and data["rep_image"].size > 200000:
			raise forms.ValidationError('Ap ne %s KB ki photo chunni. Freebasics pe 200 KB se barri photo mana hai' % \
				format(float(data["rep_image"].size)/1000,'.1f'))#checked
		elif not self.on_fbs and data["rep_image"] and data["rep_image"].size > 10000000:
			raise forms.ValidationError('Ap ne %s MB ki photo chunni. 10MB se barri photo nahi lagti' % \
				format(float(data["rep_image"].size)/1000000,'.1f'))#checked
		elif data["rep_image"] and data["rep_image"].size == 0:
			raise forms.ValidationError('Ye photo kharab hai. Koi aur chunein')
		elif len(reply) > 1500:
			raise forms.ValidationError('1500 haroof se barri baat nah likhein')
		# data["rep_reply"] = clear_zalgo_text(reply) if reply else reply
		return data