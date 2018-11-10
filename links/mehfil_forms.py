from django import forms
from models import GroupTraffic, Group

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
