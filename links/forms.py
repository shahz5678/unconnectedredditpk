from django import forms
from django.forms import Textarea
from .models import UserProfile, ChatInbox, ChatPicMessage, Link, Vote, ChatPic, UserSettings, Publicreply, Group, GroupInvite, Reply, GroupTraffic, GroupCaptain
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image, ImageFile, ImageEnhance
import StringIO
import math
from user_sessions.models import Session
from django.core.files.uploadedfile import InMemoryUploadedFile
#from django.core.files.base import ContentFile

def image_entropy(img):
	"""calculate the entropy of an image"""
	hist = img.histogram()
	hist_size = sum(hist)
	hist = [float(h) / hist_size for h in hist]
	return -sum([p * math.log(p, 2) for p in hist if p != 0])

#cuts 80% from the bottom, 20% from the top
def square_image(img):
	"""if the image is taller than it is wide, square it off. determine
	which pieces to cut off based on the entropy pieces."""
	x,y = img.size
	while y > x:
		#slice 10px at a time until square
		slice_height = min(y - x, 20) #ensure image cropping is done with precision
		img = img.crop((0, 0, x, y - slice_height)) #cut from the bottom
		x,y = img.size
		slice_height = min(y - x, 5)
		img = img.crop((0, slice_height, x, y)) #cut from the top
		x,y = img.size
	return img
'''
def square_image(img):
	if the image is taller than it is wide, square it off. determine
	which pieces to cut off based on the entropy pieces."""
	x,y = img.size
	while y > x:
		slice_height = min(y - x, 10)
		img = img.crop((0,30,x,y-30))
		x,y = img.size
	return img
'''

def MakeThumbnail(filee):
	img = filee
	img = square_image(img)
	if img.mode != 'RGB':
		img = img.convert("RGB")
	enhancer = ImageEnhance.Brightness(img)
	enhancer = enhancer.enhance(1.2)
	enhancer2 = ImageEnhance.Contrast(enhancer)
	enhancer2 = enhancer2.enhance(1.07)
	enhancer3 = ImageEnhance.Color(enhancer2)
	img = enhancer3.enhance(1.15)
	img.thumbnail((200, 200))
	thumbnailString = StringIO.StringIO()
	#if img.mode != 'RGB':
	#    img = img.convert("RGB")
	img.save(thumbnailString, 'JPEG')
	newFile = InMemoryUploadedFile(thumbnailString, None, 'temp.jpg', 'image/jpeg', thumbnailString.len, None)
	return newFile

def clean_image_file(image): # where self is the form
	if image:
		#print image
		if image.size > 1000000:
			#raise ValidationError("File buhut barri hai, doosri try karo")
			return 0
		image = Image.open(image)
		#print "inside clean_image_file"
		image = MakeThumbnail(image)
		print "thumbnailed image is %s" % image.size
		return image
	else:
		return 0

class UserProfileForm(forms.ModelForm): #this controls the userprofile edit form
	MardAurat = (
		('1','Aurat'),
		('0','Mard'),
		)
	MaritalStatus = (
		('1','Yes'),
		('0','No'),
		)
	RATING = (
		('0','Ekdum kadak yaar'),
		('1','Itni burri bhi nahi'),
		('2','Shakal pe mat ja'),
	)
	avatar = forms.ImageField(label='Photo Lagao', help_text='less than 1 mb', required=False)
	gender = forms.TypedChoiceField(choices=MardAurat, widget=forms.RadioSelect, coerce=int)
	shadi_shuda = forms.TypedChoiceField(choices=MaritalStatus, widget=forms.RadioSelect, coerce=int)
	attractiveness = forms.TypedChoiceField(choices=RATING, widget=forms.RadioSelect, coerce=int)
	class Meta:
		model = UserProfile
		exclude = ('user','previous_retort') #so user and previous_retort doesn't show, but the extended attributes of bio and mobile number do show    
		fields=('avatar', 'mobilenumber', 'bio', 'gender', 'age', 'shadi_shuda', 'attractiveness')
	
	def __init__(self, *args, **kwargs):
		# you take the user out of kwargs and store it as a class attribute
		self.user = kwargs.pop('user', None)
		super(UserProfileForm, self).__init__(*args, **kwargs)

	def clean_avatar(self):
		image=self.cleaned_data.get("avatar")
		try:
			if image.name in self.user.userprofile.avatar.url:
				#print "no need to re-submit image"
				return image
		except:
			pass
		if image:
			try:
				if image.size > 1000000:
					return 0
			except:
				pass
			image = Image.open(image)
			image = MakeThumbnail(image)
			return image
		else:
			return 0   

class UserSettingsForm(forms.ModelForm):
	ScoreVisible = (
		('0','No'),
		('1','Yes'),
		)
	score_setting = forms.TypedChoiceField(choices=ScoreVisible, widget=forms.RadioSelect, coerce=int)
	class Meta:
		model = UserSettings
		exclude = ('user', 'setting2', 'setting3', 'setting4', 'setting5')
		fields = ('score_setting',)

class LinkForm(forms.ModelForm):#this controls the link edit form
	#image_file = forms.ImageField(label='Tasveer dallo:', help_text='less than 1 mb')
	description = forms.CharField(label='Kuch likho:', widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Link
		exclude = ("submitter", "rank_score", "category")
		fields = ("image_file", "description",)

class PublicGroupReplyForm(forms.ModelForm):
	text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

class OutsiderGroupForm(forms.ModelForm):
	text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

class PrivateGroupReplyForm(forms.ModelForm):
	text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

class WelcomeMessageForm(forms.ModelForm):
	description = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Publicreply
		exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
		fields = ("description",)

class PublicreplyForm(forms.ModelForm):
	description = forms.CharField(label='Jawab:', widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Publicreply
		exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
		fields = ("description",)

class OutsideMessageRecreateForm(forms.Form):
	mobile_number = forms.CharField(max_length=50)
	class meta:
		fields = ("mobile_number",)

class OutsideMessageCreateForm(forms.Form):
	full_name = forms.CharField(max_length=50)
	mobile_number = forms.CharField(max_length=50)
	class meta:
		fields = ("full_name","mobile_number")

class UserPhoneNumberForm(forms.ModelForm):
	what_number = forms.CharField(label='Mobile number:', max_length=50)
	class Meta:
		model = ChatPicMessage
		exclude = ("which_pic","viewing_time","sending_time","expiry_interval","caption","seen")
		fields = ("what_number",)

class UserSMSForm(forms.Form):
	class Meta:
		pass

class ClosedGroupCreateForm(forms.ModelForm):
	class Meta:
		model = Group
		exclude = ("owner","created_at", "members", "cagtegory","private", "rules", "pics_ki_ijazat")
		fields = ("topic",)
	
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

class ChangeGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='Neya Topic:', widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Group
		fields = ("topic",)

class PicsChatUploadForm(forms.ModelForm):
	class Meta:
		model = ChatPic
		exclude = ("sender","sending_time", "sms_created", "expiry_interval")
		fields = ("image",)

class ChangeGroupRulesForm(forms.ModelForm):
	rules = forms.CharField(label='Neya Qanoon:', widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Group
		fields = ("rules",)

class CrossNotifForm(forms.Form):
	class Meta:
		pass
		#model = Link

class PicPasswordForm(forms.Form):
	mobile_number = forms.CharField(max_length=50)
	class meta:
		fields = ("mobile_number",)

class WelcomeReplyForm(forms.Form):
	class Meta:
		model = Publicreply

class DirectMessageForm(forms.Form):
	class Meta:
		pass

class PhotoHelpForm(forms.Form):
	class Meta:
		pass

class DeletePicForm(forms.Form):
	class Meta:
		pass

class PicHelpForm(forms.Form):
	class Meta:
		pass

class DirectMessageCreateForm(forms.Form):
	class Meta:
		model = Group

class PicExpiryForm(forms.Form):
	class Meta:
		pass

class InviteForm(forms.Form): # doesn't work if one uses Model form
	class Meta:
		model = Session

class VerifiedForm(forms.Form):
	class Meta:
		model = User

class TopForm(forms.Form):
	class Meta:
		model = User

class UnseenActivityForm(forms.ModelForm): #creates a form for Link
	class Meta:
		model = Link

class OwnerGroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class GroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class OutsideMessageForm(forms.Form):
	class Meta:
		pass

class DeviceHelpForm(forms.Form):
	class Meta:
		pass

class WelcomeForm(forms.Form):
	class Meta:
		pass

class GroupPageForm(forms.Form):
	class Meta:
		model = Reply

class AppointCaptainForm(forms.Form): #doesn't work as forms.ModelForm
	class Meta:
		pass

class GroupListForm(forms.Form):
	class Meta:
		pass

class OpenGroupHelpForm(forms.Form):
	class Meta:
		pass

class ClosedGroupHelpForm(forms.Form):
	class Meta:
		pass

class GroupTypeForm(forms.Form):
	class Meta:
		pass

class DownvoteForm(forms.Form):
	class Meta:
		pass

class UpvoteForm(forms.Form):
	class Meta:
		pass

class LogoutHelpForm(forms.Form):
	class Meta:
		pass

class EmoticonsHelpForm(forms.Form):
	class Meta:
		pass

class ReportreplyForm(forms.Form):
	class Meta:
		pass

class LogoutReconfirmForm(forms.Form):
	class Meta:
		pass

class LogoutPenaltyForm(forms.Form):
	class Meta:
		pass

class ReinviteForm(forms.Form):
	class Meta:
		pass

class KickForm(forms.Form):
	class Meta:
		pass

class MehfilForm(forms.Form):
	class Meta:
		pass

class GroupReportForm(forms.Form):
	class Meta:
		model = Reply

class MehfildecisionForm(forms.Form):
	class Meta:
		pass

class ReportForm(forms.Form):
	class Meta:
		model = Publicreply

class ScoreHelpForm(forms.Form):
	class Meta:
		pass

class RegisterLoginForm(forms.Form):
	class Meta:
		pass

class RegisterWalkthroughForm(forms.Form):
	class Meta:
		pass

class LoginWalkthroughForm(forms.Form):
	class Meta:
		pass

class VoteOrProfileForm(forms.Form):
	class Meta:
		pass

class OpenInviteTypeForm(forms.Form):
	class Meta:
		pass

class SmsReinviteForm(forms.Form):
	class Meta:
		pass

class SmsInviteForm(forms.Form):
	class Meta:
		pass

class ClosedInviteTypeForm(forms.Form):
	class Meta:
		pass

class NotifHelpForm(forms.Form):
	class Meta:
		pass

class HistoryHelpForm(forms.Form):
	class Meta:
		pass

class WhoseOnlineForm(forms.Form):
	class Meta:
		pass

class GroupHelpForm(forms.Form):
	class Meta:
		pass

class HelpForm(forms.Form):
	class Meta:
		pass

class RegisterHelpForm(forms.Form):
	class Meta:
		pass	

class VerifyHelpForm(forms.Form):
	class Meta:
		pass		
#####################################################################################################