import random
from django import forms
from models import GroupTraffic, Group, Reply
from redis4 import get_and_delete_text_input_key, is_limited, many_short_messages, log_short_message
from forms import repetition_found, human_readable_time


class GroupHelpForm(forms.Form):
	class Meta:
		pass

class ReinviteForm(forms.Form):
	class Meta:
		pass

class OpenGroupHelpForm(forms.Form):
	class Meta:
		pass

class ClosedGroupHelpForm(forms.Form):
	class Meta:
		pass

class MehfilForm(forms.Form):
	class Meta:
		pass

class AppointCaptainForm(forms.Form): #doesn't work as forms.ModelForm
	class Meta:
		pass

class OwnerGroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class GroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class DirectMessageCreateForm(forms.Form):
	class Meta:
		model = Group

class ClosedGroupCreateForm(forms.ModelForm):
	class Meta:
		model = Group
		exclude = ("owner","created_at", "members", "cagtegory","private", "rules", "pics_ki_ijazat")
		fields = ("topic",)

	def __init__(self, *args, **kwargs):
		super(ClosedGroupCreateForm, self).__init__(*args, **kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:95%;'

class OpenGroupCreateForm(forms.ModelForm):
	PicNoPic = (
		('1','Haan'),
		('0','Nahi'),
		)
	pics_ki_ijazat = forms.TypedChoiceField(choices=PicNoPic, widget=forms.RadioSelect, coerce=int)
	class Meta:
		model = Group
		exclude = ("owner","created_at", "members", "cagtegory","private")
		fields = ("topic", "rules", "pics_ki_ijazat")

	def __init__(self, *args, **kwargs):
		self.is_mob_verified = kwargs.pop('verified',None)
		super(OpenGroupCreateForm, self).__init__(*args, **kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:95%;'
		self.fields['rules'].widget.attrs['style'] = 'width:95%;'

	def clean_topic(self):
		data, is_mob_verified = self.cleaned_data.get("topic"), self.is_mob_verified
		if not is_mob_verified:
			raise forms.ValidationError('Mobile number verify kiye beghair mehfil nahi ban sakti')
		return data

class DirectMessageForm(forms.Form):
	class Meta:
		pass		

class ReinvitePrivateForm(forms.Form):
	class Meta:
		pass

class GroupListForm(forms.Form):
	class Meta:
		pass

class GroupTypeForm(forms.Form):
	class Meta:
		pass

class ChangeGroupRulesForm(forms.ModelForm):
	rules = forms.CharField(label='Neya Qanoon:', widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("rules",)

class ChangePrivateGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='New Topic:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("topic",)

	def clean_topic(self):
		topic = self.cleaned_data.get("topic")
		topic = topic.strip()
		# topic = clear_zalgo_text(topic)
		if not topic:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		elif topic < 1:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		return topic


class ChangeGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='Neya Topic:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("topic",)

	def clean_topic(self):
		topic = self.cleaned_data.get("topic")
		topic = topic.strip()
		# topic = clear_zalgo_text(topic)
		if not topic:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		elif topic < 1:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		return topic

class PublicGroupReplyForm(forms.ModelForm):
	text = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':40,'rows':3,'autofocus': 'autofocus',\
		'class': 'cxl','autocomplete': 'off','autocapitalize':'off','spellcheck':'false'}),error_messages={'required': 'tip: likhna zaruri hai'})
	image = forms.ImageField(required=False,error_messages={'invalid_image': 'tip: photo sahi nahi hai'})
	sk = forms.CharField(required=False)
	gp = forms.IntegerField()

	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.is_mob_verified = kwargs.pop('is_mob_verified',None)
		super(PublicGroupReplyForm, self).__init__(*args,**kwargs)
		# self.fields['image'].widget.attrs['accept'] = 'image/*'
		self.fields['image'].widget.attrs['id'] = 'pub_grp_browse_image_btn'
		self.fields['text'].widget.attrs['id'] = 'pub_grp_text_field'
		self.fields['text'].widget.attrs['style'] = 'width:99%;height:50px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		data = self.cleaned_data
		text, user_id, section_id, section, image, secret_key_from_form = data.get("text"), self.user_id, data.get("gp"), 'pub_grp', \
		data.get('image'), data.get('sk')
		secret_key_from_session = get_and_delete_text_input_key(self.user_id,section_id,'pub_grp')
		text = text.strip() if text else text # make function sophisticated https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('tip: sirf aik dafa button dabain')
	
		elif not text:
			if image:
				rate_limited, reason = is_limited(user_id,section='pub_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap open mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				elif not self.is_mob_verified:
					raise forms.ValidationError('tip: yahan foto laganey ke liye apna mobile number verify karwain')
				else:
					data["text"] = random.choice(["... ... ...",".. .. ..","... .. ...",".. ... ..","... ... ..",".. ... ...",". ... .",\
						". . . . .",".. .. .. ..",".... . ....","... .... ..."]) # for aesthetic reasons
					return data
			else:
				raise forms.ValidationError('tip: likhna zaruri hai')
		else:
			if repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=text):
				raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
			else:
				rate_limited, reason = is_limited(user_id,section='pub_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap open mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					text_len = len(text)
					# if text_len < 1:
					#   raise forms.ValidationError('tip: likhna zaruri hai')
					# elif text_len < 2:
					#   raise forms.ValidationError('tip: itni choti baat nahi likh sakte')
					if text_len < 6:
						if many_short_messages(user_id,section,section_id):
							raise forms.ValidationError('tip: har thori deir baad yahan choti baat nah likhein')
						else:
							log_short_message(user_id,section,section_id)
					elif text_len > 500:
						raise forms.ValidationError('tip: itni barri baat nahi likh sakte')
					if not self.is_mob_verified:
						raise forms.ValidationError('tip: yahan likhne ke liye apna mobile number verify karwain')
					# text = clear_zalgo_text(text)
					# uni_str = uniform_string(text)
					# if uni_str:
					#   if uni_str.isspace():
					#       raise forms.ValidationError('tip: ziyada spaces daal di hain')
					#   else:
					#       raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likhein' % uni_str)
					data["text"] = text
					return data

class PrivateGroupReplyForm(forms.ModelForm):
	text = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':40,'rows':3,'autofocus': 'autofocus','class': 'cxl',\
		'autocomplete': 'off','autocapitalize':'off','spellcheck':'false'}),error_messages={'required': 'tip: likhna zaruri hai'})
	image = forms.ImageField(required=False,error_messages={'invalid_image': 'tip: photo sahi nahi hai'})
	sk = forms.CharField(required=False)
	gp = forms.IntegerField()
	
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		super(PrivateGroupReplyForm, self).__init__(*args,**kwargs)
		self.fields['text'].widget.attrs['style'] = 'width:99%;height:50px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		data = self.cleaned_data
		text, user_id, section_id, section, image, secret_key_from_form = data.get("text"), self.user_id, data.get("gp"), 'prv_grp', \
		data.get("image"), data.get("sk")
		secret_key_from_session = get_and_delete_text_input_key(self.user_id,section_id,'prv_grp')
		text = text.strip() if text else text
		if not text:
			if image:
				rate_limited, reason = is_limited(user_id,section='prv_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap private mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					data["text"] = random.choice(["... ... ...",".. .. ..","... .. ...",".. ... ..","... ... ..",".. ... ...",". ... .",\
						". . . . .",".. .. .. ..",".... . ....","... .... ..."]) # for aesthetic reasons
					return data
			else:
				raise forms.ValidationError('tip: likhna zaruri hai')
		elif secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('tip: sirf aik dafa button dabain')
		else:
			if repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=text):
				raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
			else:
				rate_limited, reason = is_limited(user_id,section='prv_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap private mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					text_len = len(text)
					if text_len < 1:
						raise forms.ValidationError('tip: likhna zaruri hai')
					# elif text_len < 2:
					#   raise forms.ValidationError('tip: itni choti baat nahi likh sakte')
					if text_len < 6:
						if many_short_messages(user_id,section,section_id):
							raise forms.ValidationError('tip: har thori deir baad yahan choti baat nah likhein')
						else:
							log_short_message(user_id,section,section_id)
					elif text_len > 500:
						raise forms.ValidationError('tip: itni barri baat nahi likh sakte')
					# text = clear_zalgo_text(text)
					# uni_str = uniform_string(text)
					# if uni_str:
					#   if uni_str.isspace():
					#       raise forms.ValidationError('tip: ziyada spaces daal di hain')
					#   else:
					#       raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
					data["text"] = text
					return data

