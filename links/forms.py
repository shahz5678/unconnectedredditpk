from django import forms
from django.forms import Textarea
from .redis1 import already_exists
from .models import UserProfile, TutorialFlag, ChatInbox, PhotoStream, PhotoVote, PhotoComment, ChatPicMessage, Photo, Link, Vote, \
ChatPic, UserSettings, Publicreply, Group, GroupInvite, Reply, GroupTraffic, GroupCaptain, VideoComment
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core import validators
from django.utils.translation import ugettext, ugettext_lazy as _
from detect_porn import detect
import PIL
from PIL import Image, ImageFile, ImageEnhance, ExifTags
ImageFile.LOAD_TRUNCATED_IMAGES = True
import StringIO, math, re, time
from user_sessions.models import Session
from django.core.files.uploadedfile import InMemoryUploadedFile

import unicodedata
#from django.core.files.base import ContentFile

# def uploaded_recently(avghash, hash_list):
# 	try:
# 		hash_list=list(hash_list)
# 		index = hash_list.index(avghash)
# 		return index
# 	except:
# 		index = -1 
# 		return index

def compute_avg_hash(image):
	small_image_bw = image.resize((8,8), Image.ANTIALIAS).convert("L")
	pixels = list(small_image_bw.getdata())
	avg = sum(pixels) / len(pixels)
	bits = "".join(map(lambda pixel: '1' if pixel > avg else '0', pixels)) #turning the image into string of 0s and 1s
	photo_hash = int(bits, 2).__format__('16x').upper()
	return photo_hash

def restyle_image(image):
	width = 300
	#height = 38
	wpercent = (width/float(image.size[0]))
	hsize = int((float(image.size[1])*float(wpercent)))
	image_resized = image.resize((width,hsize), PIL.Image.ANTIALIAS)
	return image_resized

def reorient_image(image):
	try:
		image_exif = image._getexif()
		image_orientation = image_exif[274]
		if image_orientation == 3:
			image = image.transpose(Image.ROTATE_180)
		if image_orientation == 6:
			image = image.transpose(Image.ROTATE_270)
		if image_orientation == 8:
			image = image.transpose(Image.ROTATE_90)
		return image
	except:
		return image

def MakeThumbnail(filee):
	img = filee
	img = restyle_image(img)
	if img.mode != 'RGB':
		img = img.convert("RGB")
	enhancer = ImageEnhance.Brightness(img)
	enhancer = enhancer.enhance(1.10)
	enhancer2 = ImageEnhance.Contrast(enhancer)
	enhancer2 = enhancer2.enhance(1.04)
	enhancer3 = ImageEnhance.Color(enhancer2)
	img = enhancer3.enhance(1.15)
	img.thumbnail((300, 300))
	thumbnailString = StringIO.StringIO()
	img.save(thumbnailString, 'JPEG', optimize=True)
	newFile = InMemoryUploadedFile(thumbnailString, None, 'temp.jpg', 'image/jpeg', thumbnailString.len, None)
	return newFile

def clean_image_file(image): # where self is the form
	# print "here"
	if image:
		image = Image.open(image)
		image = reorient_image(image)
		image = MakeThumbnail(image)
		#print "thumbnailed image is %s" % image.size
		return image
	else:
		return 0

def clean_image_file_with_hash(image):#, hashes): # where self is the form
	if image:
		# print image
		image = Image.open(image)
		# is_porn, rating = detect(image) #check if it's probably porn
		# print is_porn, rating
		image = reorient_image(image) #so that it appears the right side up
		avghash = compute_avg_hash(image) #to ensure a duplicate image hasn't been posted before
		exists = already_exists(avghash)
		if exists:
			return image, avghash, exists
		else:
			image = MakeThumbnail(image)
			return image, avghash, None
	else:
		return (0,-1)

def clear_zalgo_text(text):
	return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))

class UserProfileForm(forms.ModelForm): #this controls the userprofile edit form
	MardAurat = (
		('1','Girl'),
		('0','Boy'),
		)
	MaritalStatus = (
		('1','Yes'),
		('0','No'),
		)
	RATING = (
		('0','Ek dum kadak'),
		('1','Fifty fifty'),
		('2','Shakal pe mat ja'),
	)
	avatar = forms.ImageField(label='Photo Lagao', help_text='less than 1 mb', required=False)
	gender = forms.TypedChoiceField(choices=MardAurat, widget=forms.RadioSelect, coerce=int)
	shadi_shuda = forms.TypedChoiceField(choices=MaritalStatus, widget=forms.RadioSelect, coerce=int)
	attractiveness = forms.TypedChoiceField(choices=RATING, widget=forms.RadioSelect, coerce=int)
	bio = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'max-width:98%;'}))
	mobilenumber = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':1,'style':'max-width:80%;'}))
	age = forms.CharField(widget=forms.Textarea(attrs={'cols':10,'rows':1,'style':'max-width:50%;'}))
	class Meta:
		model = UserProfile
		exclude = ('user','previous_retort') #so user and previous_retort doesn't show, but the extended attributes of bio and mobile number do show    
		fields=('avatar', 'mobilenumber', 'bio', 'gender', 'age', 'shadi_shuda', 'attractiveness')
	
	def __init__(self, *args, **kwargs):
		# you take the user out of kwargs and store it as a class attribute
		self.user = kwargs.pop('user', None)
		super(UserProfileForm, self).__init__(*args, **kwargs)
		self.fields['avatar'].widget.attrs['style'] = 'width:95%;'

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

	def clean_bio(self):
		bio = self.cleaned_data.get("bio")
		bio = bio.strip()
		bio = clear_zalgo_text(bio)
		return bio

class CricketDashboardForm(forms.Form):
	class Meta:
		pass

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
	description = forms.CharField(label='Likho:', widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;'}))
	class Meta:
		model = Link
		exclude = ("submitter", "rank_score", "cagtegory",)
		fields = ("image_file", "description",)

	def clean_description(self):
		description = self.cleaned_data.get("description")
		description = description.strip()
		if len(description) < 5:
			raise forms.ValidationError('tip: home pr itna chota lafz nahi likh sakte')
		description = clear_zalgo_text(description)
		return description

class PublicGroupReplyForm(forms.ModelForm):
	text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;'}))
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

	def clean_text(self):
		text = self.cleaned_data.get("text")
		text = text.strip()
		text = clear_zalgo_text(text)
		return text

class OutsiderGroupForm(forms.ModelForm):
	text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

class PrivateGroupReplyForm(forms.ModelForm):
	text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;'}))
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

	def clean_text(self):
		text = self.cleaned_data.get("text")
		text = text.strip()
		text = clear_zalgo_text(text)
		return text

class WelcomeMessageForm(forms.ModelForm):
	description = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3}))
	class Meta:
		model = Publicreply
		exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
		fields = ("description",)

class CommentForm(forms.ModelForm):
	text = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = PhotoComment
		exclude = ("which_video", "device", "submitted_by", "submitted_on",)
		fields = ("text",)

	def clean_text(self):
		text = self.cleaned_data.get("text")
		text = text.strip()
		text = clear_zalgo_text(text)
		if len(text) < 2:
			raise forms.ValidationError('tip: tabsre mein itna chota lafz nahi likh sakte')
		return text

class VideoCommentForm(forms.ModelForm):
	text = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = VideoComment
		exclude = ("which_photo", "device", "submitted_by", "submitted_on",)
		fields = ("text",)

class PublicreplyForm(forms.ModelForm):
	description = forms.CharField(label='Jawab:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Publicreply
		exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
		fields = ("description",)

	def clean_description(self):
		description = self.cleaned_data.get("description")
		description = description.strip()
		description = clear_zalgo_text(description)
		if len(description) < 2:
			raise forms.ValidationError('tip: jawab mein itna chota lafz nahi likh sakte')
		return description

class OutsideMessageCreateForm(forms.Form):
	full_name = forms.CharField(max_length=50)
	mobile_number = forms.CharField(max_length=50)
	class Meta:
		fields = ("full_name","mobile_number")

class CaptionDecForm(forms.Form):
	class Meta:
		pass

class PhotostreamForm(forms.Form):
	class Meta:
		pass

class CaptionForm(forms.ModelForm):
	caption = forms.CharField(max_length=150)
	class Meta:
		model = ChatPicMessage
		exclude = ("which_pic","viewing_time","sending_time","expiry_interval","what_number","seen")
		fields = ("caption",)

class UserPhoneNumberForm(forms.ModelForm):
	what_number = forms.CharField(label='Mobile number:', max_length=50)
	class Meta:
		model = ChatPicMessage
		exclude = ("which_pic","viewing_time","sending_time","expiry_interval","caption","seen")
		fields = ("what_number",)

class UserSMSForm(forms.Form):
	class Meta:
		pass

class AdImageForm(forms.ModelForm):
	image_file = forms.ImageField(label='Upload', error_messages={'required': 'Photo ka intekhab sahi nahi hua'})
	class Meta:
		model = ChatPic
		exclude = ("sender","sending_time", "sms_created", "expiry_interval")
		fields = ("image_file",)

	def __init__(self, *args, **kwargs):
		super(AdImageForm, self).__init__(*args, **kwargs)
		self.fields['image_file'].widget.attrs['style'] = 'width:95%;'

class AdImageYesNoForm(forms.Form):
	class Meta:
		pass

class AdAddressYesNoForm(forms.Form):
	class Meta:
		pass

class AdCallPrefForm(forms.Form):
	class Meta:
		pass

class AdGenderChoiceForm(forms.Form):
	class Meta:
		pass

class AdTitleYesNoForm(forms.Form):
	class Meta:
		pass

class AdAddressForm(forms.Form):
	address = forms.CharField(max_length=250)
	class Meta:
		fields = ("address",)

class AdTitleForm(forms.Form):
	title = forms.CharField(max_length=250)
	class Meta:
		fields = ("title",)

class TestAdsForm(forms.Form):
	class Meta:
		pass		

class TestReportForm(forms.Form):
	class Meta:
		pass

class AdMobileNumForm(forms.Form):
	mobile_number = forms.CharField(max_length=20)
	class Meta:
		fields = ("mobile_number",)

class AdDescriptionForm(forms.Form):
	description = forms.CharField(max_length=250)
	class Meta:
		fields = ("description",)

class ReportFeedbackForm(forms.Form):
	description = forms.CharField(max_length=250)
	class Meta:
		fields = ("description",)

class UnseenActivityForm(forms.Form):
	comment = forms.CharField(max_length=250)
	group_reply = forms.CharField(max_length=500)
	class Meta:
		fields = ("comment", "group_reply", )

	def clean_comment(self):
		comment = self.cleaned_data.get("comment")
		comment = clear_zalgo_text(comment.strip())
		return comment

	def clean_group_reply(self):
		group_reply = self.cleaned_data.get("group_reply")
		group_reply = clear_zalgo_text(group_reply.strip())
		return group_reply

class PhotoTimeForm(forms.Form):
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

class ChangeOutsideGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='Neya Topic:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("topic",)

class ChangePrivateGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='New Topic:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("topic",)

class ChangeGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='Neya Topic:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("topic",)

class UploadPhotoReplyForm(forms.ModelForm):
	image_file = forms.ImageField(error_messages={'required': 'Photo ka intekhab doobara karo'})
	caption = forms.CharField(widget=forms.Textarea(attrs={'cols':20,'rows':2,'style':'width:98%;'}), error_messages={'required': 'Photo ke bary mien likhna zaroori hai'})
	class Meta:
		model = Photo
		exclude = ("owner", "children", "child_count", "upload_time", "comment_count", "category", "device", "latest_comment", "second_latest_comment", "is_visible", "visible_score", "invisible_score",)
		fields = ("image_file", "caption",)

	def __init__(self, *args, **kwargs):
		super(UploadPhotoReplyForm, self).__init__(*args, **kwargs)
		self.fields['image_file'].widget.attrs['style'] = 'width:95%;'

class UploadPhotoForm(forms.ModelForm):
	image_file = forms.ImageField(label='Upload', error_messages={'required': 'Photo ka intekhab sahi nahi hua'})
	caption = forms.CharField(widget=forms.Textarea(attrs={'cols':20,'rows':2,'style':'width:98%;'}), error_messages={'required': 'Photo ke barey mien likhna zaroori hai'})
	class Meta:
		model = Photo
		exclude = ("owner", "children", "child_count", "upload_time", "comment_count", "category", "device", "latest_comment", "second_latest_comment", "is_visible", "visible_score", "invisible_score",)
		fields = ("image_file","caption",)

	def __init__(self, *args, **kwargs):
		super(UploadPhotoForm, self).__init__(*args, **kwargs)
		self.fields['image_file'].widget.attrs['style'] = 'width:95%;'

class UploadVideoForm(forms.Form):
	video_file = forms.FileField()
	caption = forms.CharField(widget=forms.Textarea(attrs={'cols':20,'rows':2,'style':'width:98%;'}), error_messages={'required': 'Video ke bary mien likhna zaroori hai'})
	class Meta:
		fields = ("video_file", "caption",)

class PicsChatUploadForm(forms.ModelForm):
	image = forms.ImageField(label='Upload')
	#image.widget.attrs["value"] ='Upload'
	#image.widget.attrs["type"] ='image'
	class Meta:
		model = ChatPic
		exclude = ("sender","sending_time", "sms_created", "expiry_interval")
		fields = ("image",)

	def __init__(self, *args, **kwargs):
		super(PicsChatUploadForm, self).__init__(*args, **kwargs)
		self.fields['image'].widget.attrs['style'] = 'width:95%;'

class ChangeGroupRulesForm(forms.ModelForm):
	rules = forms.CharField(label='Neya Qanoon:', widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("rules",)

class HomeLinkListForm(forms.Form):
	reply = forms.CharField(max_length=250)
	class Meta:
		fields = ("reply",)

class BestPhotosListForm(forms.Form):
	class Meta:
		pass

class PhotosListForm(forms.Form):
	class Meta:
		pass

class UnauthHomeLinkListForm(forms.Form):
	class Meta:
		pass

class FacesPagesForm(forms.Form):
	class Meta:
		pass

class CrossNotifForm(forms.Form):
	class Meta:
		pass
		#model = Link

class PhotoShareForm(forms.Form):
	class Meta:
		pass

class InternalSalatInviteForm(forms.Form):
	class Meta:
		pass

class ExternalSalatInviteForm(forms.Form):
	class Meta:
		pass

class PhotoReplyForm(forms.Form):
	class Meta:
		pass

class PhotoJawabForm(forms.Form):
	class Meta:
		pass

class PicPasswordForm(forms.Form):
	mobile_number = forms.CharField(max_length=50)
	class meta:
		fields = ("mobile_number",)

class WelcomeReplyForm(forms.Form):
	class Meta:
		model = Publicreply

class SalatTutorialForm(forms.Form):
	class Meta:
		pass

class DirectMessageForm(forms.Form):
	class Meta:
		pass

class FanTutorialForm(forms.Form):
	class Meta:
		pass

class StarListForm(forms.Form):
	class Meta:
		pass

class FanListForm(forms.Form):
	class Meta:
		pass

class SalatInviteForm(forms.Form):
	class Meta:
		pass

class ChainPhotoTutorialForm(forms.Form):
	class Meta:
		pass

class VideoScoreForm(forms.Form):
	class Meta:
		pass

class PhotoScoreForm(forms.Form):
	class Meta:
		pass

class BaqiPhotosHelpForm(forms.Form):
	class Meta:
		pass

class PhotoQataarHelpForm(forms.Form):
	class Meta:
		pass

class ContactForm(forms.Form):
	class Meta:
		pass

class AboutForm(forms.Form):
	class Meta:
		pass

class PrivacyPolicyForm(forms.Form):
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

class InvitePrivateForm(forms.Form):
	class Meta:
		model = Session

class InviteForm(forms.Form): # doesn't work if one uses Model form
	class Meta:
		model = Session

class VerifiedForm(forms.Form):
	class Meta:
		model = User

class TopPhotoForm(forms.Form):
	class Meta:
		model = User

class TopForm(forms.Form):
	class Meta:
		model = User

class OwnerGroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class GroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class BigPhotoHelpForm(forms.Form):
	class Meta:
		pass

class OutsideMessageForm(forms.Form):
	class Meta:
		pass

class DeviceHelpForm(forms.Form):
	class Meta:
		pass

class ReportcommentForm(forms.Form):
	class Meta:
		pass

class MehfilCommentForm(forms.Form):
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

class FacesHelpForm(forms.Form):
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

class ReinvitePrivateForm(forms.Form):
	class Meta:
		pass

class ReportNicknameForm(forms.Form):
	class Meta:
		pass

class ReportProfileForm(forms.Form):
	class Meta:
		pass

class SpecialPhotoTutorialForm(forms.Form):
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

class CreateAccountForm(forms.ModelForm):
	username = forms.RegexField(max_length=50,regex=re.compile('^[\w.@+-]+$'),error_messages={'invalid': _("ye nickname sahi nahi hai")})
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = User
		fields = ('username',)

	def clean_username(self):
		username = self.cleaned_data.get("username")
		try:
			User._default_manager.get(username=username)
		except User.DoesNotExist:
			# print "returning username"
			return username
		raise forms.ValidationError('%s nick tum se pehle kisi aur ne rakh liya' % username)

	def clean_password(self):
		password = self.cleaned_data.get("password")
		lower_pass = password.lower()
		if len(password) < 6:
			raise ValidationError('password mein kam se kam 6 harf zaruri hain')
		elif lower_pass.isdigit():
			raise ValidationError('password mein sirf numbers nahi ho sakte')	
		elif 'babykobasspasandhai' in lower_pass:
			raise ValidationError('babykobasspasandhai ke bajai kuch aur password likho')
		elif 'chaachi420' in lower_pass:
			raise ValidationError('chaachi420 ke bajai kuch aur password likho')
		elif 'chachi420' in lower_pass:
			raise ValidationError('chachi420 ke bajai kuch aur password likho')
		elif 'garamaanday' in lower_pass:
			raise ValidationError('garamaanday ke bajai kuch aur password likho')
		elif 'damadam' in lower_pass:
			raise ValidationError('password mein damadam nahi likh sakte')
		elif 'qwerty' in lower_pass:
			raise ValidationError('qwerty ko boojhna aasan hai, kuch aur likho')	
		return password

	def save(self, commit=True):
		user = super(CreateAccountForm, self).save(commit=False)
		password = self.cleaned_data["password"]
		user.set_password(password)
		if commit:
			user.save()
		return user

class CreatePasswordForm(forms.Form):
	username = forms.RegexField(max_length=50,regex=re.compile('^[\w.@+-]+$'))
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		fields = ('password','username')

	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request',None)
		super(CreatePasswordForm, self).__init__(*args,**kwargs)

	def clean_username(self):
		return self.cleaned_data.get("username")

	def clean_password(self):
		password = self.cleaned_data.get("password")
		lower_pass = password.lower()
		nickname = self.cleaned_data.get("username")
		lower_nick = nickname.lower()
		if len(password) < 6:
			raise ValidationError('(tip: kam se kam 6 harf likhna zaruri hai)')
		elif lower_pass.isdigit():
			raise ValidationError('(tip: password mein sirf numbers nahi ho sakte)')
		elif lower_nick in lower_pass:
			raise ValidationError('(tip: %s nahi likh sakte kiyunke nickname mein hai)' % nickname)		
		elif 'babykobasspasandhai' in lower_pass:
			raise ValidationError('(tip: babykobasspasandhai ke bajai kuch aur likho)')
		elif 'chaachi420' in lower_pass:
			raise ValidationError('(tip: chaachi420 ke bajai kuch aur likho)')
		elif 'chachi420' in lower_pass:
			raise ValidationError('(tip: chachi420 ke bajai kuch aur likho)')
		elif 'garamaanday' in lower_pass:
			raise ValidationError('(tip: garamaanday ke bajai kuch aur likho)')
		elif 'damadam' in lower_pass:
			raise ValidationError('(tip: password mein damadam nahi likh sakte)')
		elif 'qwerty' in lower_pass:
			raise ValidationError('(tip: qwerty ko boojhna aasan hai, kuch aur likho)')	
		return password

class CreateNickForm(forms.Form):
	username = forms.RegexField(max_length=50,regex=re.compile('^[\w.@+-]+$'),help_text=_("Nick mein english harf, number ya @ _ . + - likho"),\
		error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)")})
	class Meta:
		fields = ('username',)

	def clean_username(self):
		"""
		Validate that the username is not already in use, etc.
		
		"""
		username = self.cleaned_data['username']
		if ' ' in username:
			raise ValidationError('(tip: nickname mein khali jaga nahi hoti. %s likho)' % username.replace(" ",""))
		elif User.objects.filter(username__iexact=username).exists():
			raise ValidationError(_('(tip: %s kisi aur ka nickname hai. Kuch aur likho)' % username)) 
		else:
			return username

class ReauthForm(forms.Form):
	password = forms.CharField(widget=forms.TextInput(attrs={'placeholder':''}))
	class Meta:
		fields = ("password",)

	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request',None)
		super(ReauthForm, self).__init__(*args,**kwargs)

	def clean_password(self):
		entered_password = self.cleaned_data["password"]
		real_password = self.request.user.password
		if check_password(password=entered_password,encoded=real_password):
			return entered_password
		else:
			raise forms.ValidationError('(tip: password theek nahi, phir se likho)')


class ResetPasswordForm(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		fields = ('password',)

	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request',None)
		super(ResetPasswordForm, self).__init__(*args,**kwargs)

	def clean_password(self):
		password = self.cleaned_data["password"]
		old_password = self.request.user.password
		lower_pass = password.lower()
		nickname = self.request.user.username
		lower_nick = nickname.lower()
		if check_password(password,old_password):
			raise ValidationError('(tip: new password purane password se mukhtalif rakho)')
		elif len(password) < 6:
			raise ValidationError('(tip: kam se kam 6 harf likhna zaruri hai)')
		elif lower_pass.isdigit():
			raise ValidationError('(tip: password mein sirf numbers nahi ho sakte)')
		elif lower_nick in lower_pass:
			raise ValidationError('(tip: %s nahi likh sakte kiyunke nickname mein hai)' % nickname)		
		elif 'babykobasspasandhai' in lower_pass:
			raise ValidationError('(tip: babykobasspasandhai ke bajai kuch aur likho)')
		elif 'chaachi420' in lower_pass:
			raise ValidationError('(tip: chaachi420 ke bajai kuch aur likho)')
		elif 'chachi420' in lower_pass:
			raise ValidationError('(tip: chachi420 ke bajai kuch aur likho)')
		elif 'garamaanday' in lower_pass:
			raise ValidationError('(tip: garamaanday ke bajai kuch aur likho)')
		elif 'damadam' in lower_pass:
			raise ValidationError('(tip: password mein damadam nahi likh sakte)')
		elif 'qwerty' in lower_pass:
			raise ValidationError('(tip: qwerty ko boojhna aasan hai, kuch aur likho)')	
		else:
			return password

	def save(self, commit=True):
		user = self.request.user
		password = self.cleaned_data["password"]
		user.set_password(password)
		if commit:
			user.save()
		return user

class LoginWalkthroughForm(forms.Form):
	class Meta:
		pass

class VoteOrProfForm(forms.Form):
	class Meta:
		pass

# class VoteOrProfileForm(forms.Form):
# 	class Meta:
# 		pass

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