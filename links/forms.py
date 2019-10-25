# coding=utf-8
import re, time, random, unicodedata
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from django.core.files.images import get_image_dimensions
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core import validators
from django.forms import Textarea
from django import forms
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from tasks import invalidate_avatar_url
from redis7 import retrieve_topic_credentials
from image_processing import compute_avg_hash, reorient_image, make_thumbnail, prep_image
from redis6 import is_group_member_and_rules_signatory, human_readable_time, group_member_exists
from score import MAX_HOME_SUBMISSION_SIZE, MAX_HOME_REPLY_SIZE, MAX_PHOTO_CAPTION_SIZE, MAX_PHOTO_COMMENT_SIZE, RIGHT_ALIGNMENT_THRESHOLD_RATIO,\
MAX_BIO_SIZE, PRIVATE_GROUP_REPLY_LENGTH, PUBLIC_GROUP_REPLY_LENGTH
from models import UserProfile, TutorialFlag, ChatInbox, PhotoStream, PhotoComment, ChatPicMessage, Photo, Link, ChatPic, UserSettings, \
Publicreply, VideoComment
from redis4 import retrieve_previous_msgs,many_short_messages, log_short_message, is_limited, get_and_delete_text_input_key, get_aurl, \
is_attribute_change_rate_limited, log_home_post#, log_abusive_home_post


########################################### Utilities #######################################

def retrieve_validation_error_string(err_type, lang=None, payload=None):
	"""
	Return a validation error string, if given 'err_type' of error

	Takes 'payload' as an optional parameter in case the error string requires enrichment (e.g. a nickname has to be inserted into it)
	"""
	if err_type == 'nick_empty':
		if lang == 'ur':
			return 'نام کو خالی نہ چھویں'
		else:
			return "Nickname khali nahi chorein"
	if err_type == 'nick_too_small':
		if lang == 'ur':
			return 'نام اتنا چهوٹا نہیں ہو سکتا'
		else:
			return 'Nickname itna chota nahi ho sakta'
	elif err_type == 'invalid_new_nick':
		if lang == 'ur':
			return "نام میں انگریزی حروف، نمبر اور @ _ + - کے نشان کے علاوہ اور کچھ نہیں ہو سکتا۔ دوبارا کوشش کریں"
		else:
			return "Nickname mein english harf, number ya @ _ . + - likhein"
	elif err_type == 'required_new_nick':
		if lang == 'ur':
			return 'اس سفید پٹی میں نام لکھیں'
		else:
			return "Safed patti mein nickname likh ke OK dabain"
	elif err_type == 'required_visible_nick':
		if lang == 'ur':
			return 'نک نیم میں حرف لکهنا ضروری ے'
		else:
			return "Nickname mein harf likhna zaruri hain"
	elif err_type == 'nick_only_has_digits':
		if lang == 'ur':
			return 'نام میں صرف نمبر نہیں ہو سکتے'
		else:
			return 'Nickname mei sirf numbers nahi ho saktey'
	elif err_type == 'nick_is_taken':
		if lang == 'ur':
			return 'یہ نام پہلے سے کسی نے رکھا ہوا ہے، کوی اور نام رکھیں'
		else:
			return '"%s" kisi aur ka nickname hai. Kuch aur likhein' % payload
	elif err_type == 'nick_recently_taken':
		if lang == 'ur':
			return 'یہ نام آپ سے پہلے کسی اور نے رکھ لیا'
		else:
			return '"%s" nickname ap se pehle kisi aur ne rakh liya' % payload
	elif err_type == 'banned_sequence_in_nick':
		if lang == 'ur':
			return 'نام میں "%s" نہیں ڈالیں' % payload
		else:
			return 'Nickname mein "%s" nahi ho sakta' % payload
	elif err_type == 'illegal_sequence_in_nick':
		if lang == 'ur':
			return 'نام میں "%s" نہیں ڈالیں' % payload
		else:
			return 'Nickname mein "%s" nahi dalein' % payload
	elif err_type == 'dot_at_nick_start':
		if lang == 'ur':
			return 'نام کے شروع میں . نہیں ڈالیں'
		else:
			return "Nickname ke start mein . nahi dalein"
	elif err_type == 'dot_at_nick_end':
		if lang == 'ur':
			return 'نام کے آخر میں . نہیں ڈالیں'
		else:
			return "Nickname ke end mein . nahi dalein"
	elif err_type == 'dash_at_nick_start':
		if lang == 'ur':
			return 'نام کے شروع میں - نہیں ڈالیں'
		else:
			return "Nickname ke start mein - nahi dalein"
	elif err_type == 'dash_at_nick_end':
		if lang == 'ur':
			return 'نام کے آخر میں - نہیں ڈالیں'
		else:
			return 'Nickname ke end mein - nahi dalein'
	elif err_type == 'plus_at_nick_start':
		if lang == 'ur':
			return 'نام کے شروع میں + نہیں ڈالیں'
		else:
			return 'Nickname ke start mein + nahi dalein'
	elif err_type == 'plus_at_nick_end':
		if lang == 'ur':
			return 'نام کے آخر میں + نہیں ڈالیں'
		else:
			return 'Nickname ke end mein + nahi dalein'
	elif err_type == 'uscore_at_nick_start':
		if lang == 'ur':
			return 'نام کے شروع میں _ نہیں ڈالیں'
		else:
			return 'Nickname ke start mein _ nahi dalein'
	elif err_type == 'uscore_at_nick_end':
		if lang == 'ur':
			return 'نام کے آخر میں _ نہیں ڈالیں'
		else:
			return 'Nickname ke end mein _ nahi dalein'
	elif err_type == 'repeating_sequence_in_nick':
		if lang == 'ur':
			return "ایک ہی چیز کو بار بار نہ لکھیں"
		else:
			return 'Nickname mein aik hi cheez bar bar nahi likhein'
	elif err_type == 'generic_nickname_error':
		if lang == 'ur':
			return 'یہ نام صحیح نہیں ہے'
		else:
			return "Ye nickname sahi nahi hai"
	elif err_type == 'bad_case':
		if lang == 'ur':
			return 'نک نیم میں حرف غلط ہیں ـ یا بڑا حرف چھوٹا لکھ دیا ے، یا چھوٹا حرف بڑا'
		else:
			return '"%s" nickname mein harf ghalat hain. Ya chota harf bara likh diya hai, ya bara harf chota' % payload
	elif err_type == 'not_found':
		if lang == 'ur':
			return 'یہ نک نیم ﮨمارے رکارڈ میں نہیں'
		else:
			return '"%s" hamarey record mein nahi' % payload
	elif err_type == 'banned_sequence_in_pass':
		if lang == 'ur':
			return 'اس پاس ورڈ کا اندازہ لگانا آسان ہے، کچھ اور لکھیں'
		else:
			return '"%s" ko boojhna aasan hai, kuch aur likhein' % payload
	elif err_type == 'example_sequence_in_pass':
		if lang == 'ur':
			return 'یہ پاس ورڈ استعمال نہیں کریں'
		else:
			return '"%s" ko password nahi rakhein' % payload
	elif err_type == 'nickname_in_pass':
		if lang == 'ur':
			return 'پاس ورڈ میں نام نہ لکھیں'
		else:
			return '"%s" nahi likh sakte kiyunke nickname mein hai' % payload
	elif err_type == 'pass_too_small':
		if lang == 'ur':
			return 'کم سے کم چھ حرف لکھنا ضروری ہے'
		else:
			return "Kam se kam 6 letters likhna zaruri hain!"
	elif err_type == 'required_visible_pass':
		if lang == 'ur':
			return 'پاس ورڈ میں حرف لکهنا ضروری ہے'
		else:
			return 'Password mein harf likhna zaruri hain'
	elif err_type == 'old_new_pass_same':
		if lang == 'ur':
			return 'نیا پاس ورڈ پرانے پاس ورڈ سے مختلف رکھیں'
		else:
			return 'New password old password se different rakhein'
	elif err_type == 'required_new_pass':
		if lang == 'ur':
			return 'سفید پٹی میں پاس ورڈ لکھیں'
		else:
			return "Safed patti mein password likhein"
	elif err_type == 'pass_empty':
		if lang == 'ur':
			return 'پاس ورڈ خالی نہیں چھوڑیں'
		else:
			return "Password khali nahi chorein"
	elif err_type == 'wrong_pass_input':
		if lang == 'ur':
			return 'پاس ورڈ غلط لکھا ہے ۔ اگر پاس ورڈ یاد نہیں تو سب سے نیچے "پاس ورڈ بھول گۓ" کو دبایں'
		else:
			return 'Password sahi nahi. Agr password yad nahi tou sab se neechay "Password yad nahi" dabain'
	elif err_type == 'wrong_pin':
		if lang == 'ur':
			return 'کوڈ غلط ہے'
		else:
			return 'Apka pin code ghalat hai'
	elif err_type == 'invalid_pin':
		if lang == 'ur':
			return 'کوڈ میں صرف نمبر لکھیں'
		else:
			return 'Pin mein sirf number likhein'
	elif err_type == 'pin_too_small':
		if lang == 'ur':
			return 'پورا کوڈ لکھیں'
		else:
			return 'Pura pin code likhien'
	elif err_type == 'required_pin':
		if lang == 'ur':
			return 'خفیہ کوڈ لکهنا ضروری ے'
		else:
			return 'Pin code likhna zaruri hai'
	elif err_type == 'pin_tries_rate_limited':
		if lang == 'ur':
			return 'بہت زیادہ غلطیاں ہو گیں، واپس آیں %s baad' % payload
		else:
			return 'Ziyada ghalat tries ho gaien, %s baad wapis aien' % payload
	elif err_type == 'mobnum_too_small':
		if lang == 'ur':
			return 'پورا موبائل نمبر لکھیں'
		else:
			return 'Pura mobile number likhein'
	elif err_type == 'fake_mobnum':
		if lang == 'ur':
			return 'اپنا اصلی موبائل نمبر لکھیں'
		else:
			return 'Apna real mobile number likhein'
	elif err_type == 'mobnum_not_verified':
		if lang == 'ur':
			return 'آپکا موبائل نمبر تصدیق شدہ نہیں، پاس ورڈ نہیں مل سکتا'
		else:
			return 'Ap verified nahi, password nahi mil sakta'
	elif err_type == 'not_your_mobnum':
		if lang == 'ur':
			return ' موبائل نمبر صحیح لکھیں'
		else:
			return 'Mobile number sahi likhein'
	elif err_type == 'mobnum_wrong_format':
		if lang == 'ur':
			return 'موبائل نمبر "03" سے شروع کریں'
		else:
			return 'Mobile number "03" se start karein'
	elif err_type == 'required_mobnum':
		if lang == 'ur':
			return 'موبائل نمبر لکهنا ضروری ے'
		else:
			return 'Mobile number likhna zaruri hai'
	elif err_type == 'invalid_mobnum':
		if lang == 'ur':
			return 'اپنا موبائل نمبر اس طرح لکھیں - 03451234567'
		else:
			return 'Mobile number is andaz mein likhein - 03451234567'
	elif err_type == 'display_pic_rate_limited':
		if lang == 'ur':
			return ''
		else:
			return 'Ap profile photo change kar sakien ge %s secs baad' % payload
	elif err_type == 'required_age':
		if lang == 'ur':
			return 'عمر ضرور لکھیں'
		else:
			return 'Age likhna zaruri hai'
	elif err_type == 'age_too_large':
		if lang == 'ur':
			return 'عمر صحیح لکھیں'
		else:
			return 'Age sahi likhein'
	elif err_type == 'display_pic_frozen':
		if lang == 'ur':
			return ''
		else:
			return 'Sorry! Apki profile report ho chuki hai. Investigation puri honay tak display pic change nahi ki ja sakti'
	elif err_type == 'fbs_image_too_big':
		if lang == 'ur':
			return 'فری بیسکس پے دو سو کے بی سے بڑی فوٹو نہیں لگتی'
		else:
			return 'Freebasics pe 200 KB se barri photos nahi lagtein. Data package on karein!'
	elif err_type == 'image_too_big':
		if lang == 'ur':
			return 'دس ایم بی سے بڑی فوٹو نہیں لگتی'
		else:
			return 'Sorry! 10 MB se barri photos nahi lagtein'
	else:
		# generic error string
		return "Ye sahi nahi hai"


def repetition_found(section,section_id,user_id, target_text):
	msgs_list = retrieve_previous_msgs(section=section, section_id=section_id,user_id=user_id)
	if msgs_list:
		if target_text in [x.decode('utf-8') for x in msgs_list[1:]]:
			return True
		else:
			return False
	else:
		return False


def strip_zero_width_characters(string):
	"""
	Strips out 'zero-width' characters from given string - disallowing users from successfully submitting blank enteries

	List of easily copy-able zero-width characters can be found at https://coolsymbol.com/zero-width-space-joiner-non-joiner-ltr-rtl-lrm-rlm-characters-symbols.html
	u"\u200B" - Zero Width Space
	u"\u200C" - Zero Width Non-Joiner
	u"\u200D" - Zero Width Joiner
	u"\u200E" - Left-To-Right Mark
	u"\u200F" - Right-To-Left Mark
	u"\u2060" - Word Joiner
	u"\uFEFF" - Zero Width No-Break Space
	u"\u3164" - Hangful filler
	"""
	if string:
		return ''.join( c for c in string if  c not in (u"\u200B",u"\u200C",u"\u200D",u"\u200E",u"\u200F",u"\u2060",u"\uFEFF",u"\u3164"))
	else:
		return string


def uniform_string(text,n=7):
	text = text.lower()
	for i, c in enumerate(text):
		if text[i:i+n] == c * n:
			return text[i:i+n]
	return False

def getip(request):
	ip = request.META.get('X-IORG-FBS-UIP',
		request.META.get('REMOTE_ADDR')
	)
	return ip

def clear_zalgo_text(text):
	return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))


def is_urdu(text):
	"""
	Provides a percentage of how much text is predominantly in "Urdu"

	Can be used to right-align text that is predominantly in Urdu
	Utilizes the fact that "0600-06FF" and "FB50-FEFF" is the Unicode range for Urdu
	"""
	num_urdu_chars, total_chars = 0, len(text)
	if total_chars:
		for c in text:
			if u'\u0600' <= c <= u'\u06FF' or u'\uFB50' <= c <= u'\uFEFF':
				num_urdu_chars += 1
		return (num_urdu_chars*1.0)/total_chars
	else:
		return 0


################################################################################################


class UserProfileForm(forms.ModelForm):
	"""
	This controls the userprofile edit form
	"""
	MardAurat = (
		('1','Female'),
		('0','Male'),
		)
	MaritalStatus = (
		('1','Yes'),
		('0','No'),
		)
	# RATING = (
	# 	('0','Ek dum kadak'),
	# 	('1','Fifty fifty'),
	# 	('2','Shakal pe mat ja'),
	# )
	avatar = forms.ImageField(label='Photo Lagao', help_text='less than 1 mb', required=False)
	gender = forms.TypedChoiceField(choices=MardAurat, widget=forms.RadioSelect, coerce=int)
	shadi_shuda = forms.TypedChoiceField(choices=MaritalStatus, widget=forms.RadioSelect, coerce=int)
	# attractiveness = forms.TypedChoiceField(choices=RATING, widget=forms.RadioSelect, coerce=int)
	bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'cxl lsp sp','autocomplete': 'off','autocapitalize':'off','spellcheck':'false',\
		'maxlength':MAX_BIO_SIZE}),error_messages={'required': 'Ye likhna zaruri hai'})
	age = forms.IntegerField(required=False,widget=forms.Textarea(attrs={'cols':10,'rows':1,'style':'width:50px;height:20px;border-radius:5px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;','class':'cxl sp'}))
	streak = forms.IntegerField(required=False)
	attractiveness = forms.IntegerField()

	class Meta:
		model = UserProfile
		exclude = ('user','previous_retort') #so user and previous_retort doesn't show, but the extended attributes of bio and mobile number do show
		fields=('avatar', 'streak', 'bio', 'gender', 'age', 'shadi_shuda', 'attractiveness')

	def __init__(self, *args, **kwargs):
		# you take the user out of kwargs and store it as a class attribute
		self.user = kwargs.pop('user', None)
		self.on_fbs = kwargs.pop('on_fbs', None)
		super(UserProfileForm, self).__init__(*args, **kwargs)
		self.fields['avatar'].widget.attrs['style'] = 'width:95%;'
		self.fields['bio'].widget.attrs['style'] = 'width:95%;height:200px;border-radius:8px;border: 1px #1edea8 solid; background-color:#f2f1f0;padding:5px;'
		self.fields['age'].error_messages = {'required':retrieve_validation_error_string('required_age'),\
		'invalid':retrieve_validation_error_string('age_too_large')}
		self.fields['age'].widget.attrs['maxlength'] = 2
		self.fields['streak'].error_messages = {'invalid':'Ye ghalat hai'}
		

	def clean_avatar(self):
		image=self.cleaned_data.get("avatar")
		try:
			if image.name in self.user.userprofile.avatar.url:
				#print "no need to re-submit image"
				return image
		except (AttributeError, ValueError):
			pass
		if image or image is False:    
			user_id, on_fbs = self.user.id, self.on_fbs
			# is_frozen = is_user_profile_frozen(user_id)# TODO: could be frozen if was reported
			# if is_frozen:
			#     raise forms.ValidationError(retrieve_validation_error_string('display_pic_frozen'))
			# else:
			ttl = get_aurl(user_id)# in case avatar changing is rate limited because user just changed their avatar (small TTL) 
			if ttl > 1:
				raise forms.ValidationError(retrieve_validation_error_string('display_pic_rate_limited',payload=ttl))
			invalidate_avatar_url.delay(user_id, set_rate_limit=True)
			if image:
				if on_fbs:
					if image.size > 200000:#200 KB allowance
						raise forms.ValidationError(retrieve_validation_error_string('fbs_image_too_big'))
					else:
						pass
				else:
					if image.size > 10000000:#10 MB allowance
						raise forms.ValidationError(retrieve_validation_error_string('image_too_big'))
					else:
						pass
				image = Image.open(image)
				if on_fbs:
					image = make_thumbnail(image,None)#low quality upload for fbs
				else:
					image, img_width, img_height = prep_image(image,quality=True)#high qualuty upload for non-fbs
				return image
			else:
				return 0
		else:
			return None

	def clean_bio(self):
		bio = self.cleaned_data.get("bio")
		bio = bio.strip()
		bio = clear_zalgo_text(bio)
		len_bio = len(bio)
		if len_bio > MAX_BIO_SIZE:
			raise forms.ValidationError("Apki story {0} chars se barri nahi ho sakti. Aap ne {1} chars likhey".format(MAX_BIO_SIZE,len_bio))
		return bio

	def clean_age(self):
		age = self.cleaned_data.get("age")
		if age:
			if age > 99:
				raise forms.ValidationError(retrieve_validation_error_string('age_too_large'))
			elif age < 12:	
				raise forms.ValidationError(retrieve_validation_error_string('age_too_large'))
			return age

	def clean_streak(self):
		"""
		Actually contains 'city' data. Mislabelled for legacy reasons
		"""
		city = self.cleaned_data.get("streak")
		if not city:
			city = 0
		is_rate_limited, rate_limit_time = is_attribute_change_rate_limited(user_id=self.user.id, time_now=time.time(), attribute_value=city,\
			rate_limit_type='city')
		if is_rate_limited:
			raise forms.ValidationError("Ap city change kar sakein ge {} baad".format(human_readable_time(rate_limit_time)))
		return city

	def clean_attractiveness(self):
		"""
		Actually contains 'zodiac' data. Mislabelled for legacy reasons
		"""
		zodiac = self.cleaned_data.get("attractiveness")
		is_rate_limited, rate_limit_time = is_attribute_change_rate_limited(user_id=self.user.id, time_now=time.time(), attribute_value=zodiac,\
			rate_limit_type='zodiac')
		if is_rate_limited:
			raise forms.ValidationError("Ap star sign change kar sakein ge {} baad".format(human_readable_time(rate_limit_time)))
		return zodiac


	# def clean_mobilenumber(self):
	# 	mob_num = self.cleaned_data.get("mobilenumber")
	# 	return mob_num if mob_num else ''


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

class CricketCommentForm(forms.Form): #a 'Form' version of the LinkForm modelform
	description = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;',\
		'class': 'cxl','autocomplete': 'off','autocapitalize':'off','spellcheck':'false'}))
	sk = forms.CharField(required=False)

	class Meta:
		fields = ("description",)

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		super(CricketCommentForm, self).__init__(*args, **kwargs)
		self.fields['description'].widget.attrs['style'] = 'width:95%;height:50px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		data = self.cleaned_data
		user_id, description, section_id, section, secret_key_from_form = self.user_id, data.get("description"), '1', 'home', data.get("sk")
		description = description.strip() if description else None
		if not description:
			raise forms.ValidationError('tip: likhna zaruri hai')
		secret_key_from_session = get_and_delete_text_input_key(user_id,'1','home')
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('tip: sirf aik dafa button dabain')
		if repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=description):
			raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
		else:
			rate_limited, reason = is_limited(user_id,section='home',with_reason=True)
			if rate_limited > 0:
				raise forms.ValidationError('Ap yahan likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
			else:
				desc_len = len(description)
				# if desc_len < 2:
				#   raise forms.ValidationError('tip: itna choti reply nahi likh sakte')
				if desc_len < 6:
					if many_short_messages(user_id,section,section_id):
						raise forms.ValidationError('Har thori deir baad yahan choti reply nahi likhein')
					else:
						log_short_message(user_id,section,section_id)
				elif desc_len > 500:
					raise forms.ValidationError('Itni lambi reply nahi likh sakte')
				# description = clear_zalgo_text(description)
				# uni_str = uniform_string(description)
				# if uni_str:
				#   if uni_str.isspace():
				#       raise forms.ValidationError('tip: ziyada spaces daal di hain')
				#   else:
				#       raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
				return data


class LinkForm(forms.ModelForm):#this controls the link edit form
	description = forms.CharField(widget=forms.Textarea(attrs={'class': 'cxl','autofocus': 'autofocus',\
		'autocomplete': 'off','autocapitalize':'off','spellcheck':'false','maxlength':MAX_HOME_SUBMISSION_SIZE}),\
	error_messages={'required': 'Pehlay kuch likhein, phir OK dabain'})
	sk = forms.CharField(required=False)
	turl = forms.CharField(required=False)# this is topic_url

	class Meta:
		model = Link
		exclude = ("submitter", "rank_score", "cagtegory",)
		fields = ("image_file", "description",)

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.on_fbs = kwargs.pop('on_fbs',None)
		self.on_opera = kwargs.pop('on_opera',None)
		super(LinkForm, self).__init__(*args,**kwargs)
		self.fields['description'].widget.attrs['style'] = 'width:95%;height:220px;border-radius:10px;border: 1px #93d7ec solid; background-color:white;padding:7px;'

	def clean(self):
		on_fbs, on_opera = self.on_fbs, self.on_opera
		data = self.cleaned_data
		description, user_id, section_id, section, secret_key_from_form, topic_url = data.get("description"), self.user_id, '1', 'home', \
		data.get("sk"), data.get('turl',None)
		secret_key_from_session = get_and_delete_text_input_key(user_id,'1','likho')
		description = description.strip() if description else None
		description = strip_zero_width_characters(description)
		if not description or description.isspace():
			raise forms.ValidationError('Likhna zaruri hai')
		else:
			len_ = len(description)
			if len_ > MAX_HOME_SUBMISSION_SIZE+150:
				# if post is too long, short circuit the rest of the cleaning method anyway
				raise forms.ValidationError('Itni lambi post submit nahi hoti kiyun ke parhney waley bore ho jatey hain')
			else:
				description = re.sub(r'\n\s*\n', '\n', description)# collapsing multiple new lines into 1
				lines = description.split('\n')
				if len(lines) > 10:
					raise forms.ValidationError('Itni zyada new lines nahi dalein!')
				elif secret_key_from_form != secret_key_from_session:
					raise forms.ValidationError('Sirf aik dafa button dabain')
				elif repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=description):
					raise forms.ValidationError('Milti julti baatien nahi likhein')
				else:
					rate_limited, reason = is_limited(user_id,section='home',with_reason=True)
					if rate_limited > 0:
						raise forms.ValidationError('Ap yahan pe likhne se {0} tak banned hain. Reason: {1}'.format(human_readable_time(rate_limited),reason))
					else:
						##########################
						# abusive_words=(' hot ','private','sex','xxx','1on1','1 on 1')
						# lower_case_desc = description.lower()
						# if any(word in lower_case_desc for word in abusive_words):
						# 	log_abusive_home_post(user_id=user_id, text=description)
						##########################
						if len_ < 4:
							raise forms.ValidationError('Itni choti reply nahi likh sakte')
						elif len_ < 6:
							if many_short_messages(user_id,section,section_id):
								raise forms.ValidationError('Har thori deir baad yahan choti reply nahi likhein')
							else:
								log_short_message(user_id,section,section_id)
						elif len_ > MAX_HOME_SUBMISSION_SIZE:
							raise forms.ValidationError('Ap ne {0} chars likhey, ap {1} se zyada chars nahi likh saktey'.format(len_,MAX_HOME_SUBMISSION_SIZE))
						# '2' means right-aligned text, '1' means left-aligned text
						data['alignment'] = '2' if is_urdu(description) >= RIGHT_ALIGNMENT_THRESHOLD_RATIO else '1'
						data['description'] = description
						#################################
						data['tpay'], data['turl'], data['tname'], data['bgt'] = None, None, None, None
						if topic_url:
							topic_name, bg_theme, is_subscribed = retrieve_topic_credentials(topic_url=topic_url, with_name=True, \
								with_theme=True, with_is_subscribed=True, retriever_id=user_id)
							if is_subscribed:
								data['tpay'], data['turl'], data['tname'], data['bgt'] = bg_theme+":"+topic_name+":"+topic_url, topic_url, \
								topic_name, bg_theme
						##################################
						# log_home_post(user_id=user_id, text=description, is_urdu=data['alignment'], on_opera=on_opera, on_fbs=on_fbs)
						##################################
						return data


class WelcomeMessageForm(forms.ModelForm):
	description = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3}))

	class Meta:
		model = Publicreply
		exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
		fields = ("description",)


class CommentForm(forms.ModelForm):
	text = forms.CharField(widget=forms.Textarea(attrs={'class': 'cxl','autofocus': 'autofocus',\
		'autocomplete': 'off','autocapitalize':'off','spellcheck':'false','maxlength':MAX_PHOTO_COMMENT_SIZE}))
	sk = forms.CharField(required=False)

	class Meta:
		model = PhotoComment
		exclude = ("which_video", "device", "submitted_by", "submitted_on",)
		fields = ("text",)

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.photo_id = kwargs.pop('photo_id',None)
		self.mob_verified = kwargs.pop('mobile_verified',None)
		super(CommentForm, self).__init__(*args,**kwargs)
		self.fields['text'].widget.attrs['style'] = 'width:97%;height:75px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		user_id = self.user_id
		if user_id and not self.mob_verified:
			raise forms.ValidationError('Account verify kiye beghair ap yahan nahi likh saktey')
		else:
			data = self.cleaned_data
			text, photo_id, section, secret_key_from_form = data.get("text"), self.photo_id, 'pht_comm', data.get("sk")
			secret_key_from_session = get_and_delete_text_input_key(user_id, self.photo_id,'pht_comm')
			if secret_key_from_form != secret_key_from_session:
				raise forms.ValidationError('Rabta munqata ho gaya, phir se karien')
			text = text.strip() if text else text
			if not text:
				raise forms.ValidationError('Likhna zaruri hai')
			elif repetition_found(section=section,section_id=photo_id,user_id=user_id, target_text=text):
				raise forms.ValidationError('Milti julti baatien nahi likhein, kuch new likho')
			else:
				rate_limited, reason = is_limited(user_id,section='pht_comm',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap photos pe reply karney se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					text_len = len(text)
					if text_len < 6:
						if many_short_messages(user_id,section,photo_id):
							raise forms.ValidationError('Har thori deir baad yahan choti reply nahi likhein')
						else:
							log_short_message(user_id,section,photo_id)
					elif text_len > MAX_PHOTO_COMMENT_SIZE:
						raise forms.ValidationError('Ap ne {0} chars likhey, ap {1} se zyada chars nahi likh saktey'.format(text_len,MAX_PHOTO_COMMENT_SIZE))
					return data


class VideoCommentForm(forms.ModelForm):
	text = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = VideoComment
		exclude = ("which_photo", "device", "submitted_by", "submitted_on",)
		fields = ("text",)


class PublicreplyForm(forms.ModelForm):
	description = forms.CharField(label='Jawab:', widget=forms.Textarea(attrs={'class': 'cxl','autofocus': 'autofocus',\
		'autocomplete': 'off','autocapitalize':'off','spellcheck':'false','maxlength':MAX_HOME_REPLY_SIZE}), \
	error_messages={'required': 'Pehlay reply likhein, phir OK dabain'})
	sk = forms.CharField(required=False)

	class Meta:
		model = Publicreply
		exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
		fields = ("description",)

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.link_id = kwargs.pop('link_id',None)
		self.mob_verified = kwargs.pop('mob_verified',None)
		super(PublicreplyForm, self).__init__(*args,**kwargs)
		self.fields['description'].widget.attrs['style'] = 'width:97%;height:75px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean_sk(self):
		secret_key_from_form, secret_key_from_session = self.cleaned_data.get("sk"), get_and_delete_text_input_key(self.user_id,self.link_id,'home_rep')
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('Rabta munqata ho gaya, phir se karien')
		return secret_key_from_form

	def clean_description(self):
		if not self.mob_verified:
			raise forms.ValidationError('Account verify kiye beghair ap yahan nahi likh saktey')
		else:
			description, user_id, section_id, section = self.cleaned_data.get("description"), self.user_id, self.link_id, 'home_rep'
			description = description.strip() if description else None
			if not description:
				raise forms.ValidationError('Likhna zaruri hai')
			elif repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=description):
				raise forms.ValidationError('Milte julte reply nahi likhein')
			else:
				rate_limited, reason = is_limited(user_id,section='home_rep',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap reply karney se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					desc_len = len(description)
					if desc_len < 6:
						if many_short_messages(user_id,section,section_id):
							raise forms.ValidationError('Har thori deir baad yahan choti reply nahi likhein')
						else:
							log_short_message(user_id,section,section_id)
					elif desc_len > MAX_HOME_REPLY_SIZE:
						raise forms.ValidationError('Ap ne {0} chars likhey, ap {1} se zyada chars nahi likh saktey'.format(desc_len,MAX_HOME_REPLY_SIZE))
					return description


class PublicreplyMiniForm(PublicreplyForm):
	description = forms.CharField(max_length=MAX_HOME_REPLY_SIZE, \
		error_messages={'required': 'Pehlay safed patti mein likhein, phir "reply" dabain'})
	sk = forms.CharField(required=False)

	def __init__(self,*args,**kwargs):
		super(PublicreplyMiniForm, self).__init__(*args,**kwargs)
		self.fields['description'].error_messages = {'required': 'Pehlay safed patti mein likhein, phir "reply" dabain','max_length':'Reply 350 characters se zyada nahi hona chahiye'}
		self.fields['description'].widget.attrs['class'] = 'box-with-button-right cdt'
		self.fields['description'].widget.attrs['style'] = 'max-width:750px;border: 1px solid lightgrey; border-radius:4px; line-height:30px;'
		self.fields['description'].widget.attrs['autocomplete'] = 'off'

	def clean_sk(self):
		secret_key_from_form, secret_key_from_session = self.cleaned_data.get("sk"), get_and_delete_text_input_key(self.user_id, '1', 'home')
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('Phir se karein, reply send nahi hua')
		return secret_key_from_form


class SearchNicknameForm(forms.Form):
	nickname = forms.CharField(max_length=71,error_messages={'required': 'Safed patti mein "nickname" likhein jisko search karna hai'})

	def __init__(self, *args, **kwargs):
		self.searched = kwargs.pop('searched',False)
		super(SearchNicknameForm, self).__init__(*args, **kwargs)
		self.fields['nickname'].widget.attrs['style'] = \
		'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #3cb7dd;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #229ec9;'
		self.fields['nickname'].widget.attrs['class'] = 'cxl'
		if not self.searched:
			self.fields['nickname'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['nickname'].widget.attrs['autocomplete'] = 'off'

	def clean_nickname(self):
		nickname = self.cleaned_data.get("nickname")
		nickname = nickname.strip()
		if len(nickname) > 70:
			raise forms.ValidationError('Itna bara nickname nahi likh sakte')
		# nickname = clear_zalgo_text(nickname)
		return nickname


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
	image = forms.ImageField(label='Upload', error_messages={'required': 'Photo ka intekhab sahi nahi hua'})
	class Meta:
		model = ChatPic
		exclude = ("sender","sending_time", "sms_created", "expiry_interval")
		fields = ("image",)

	def __init__(self, *args, **kwargs):
		super(AdImageForm, self).__init__(*args, **kwargs)
		self.fields['image'].widget.attrs['style'] = 'width:95%;'

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


class PhotoCommentForm(forms.Form):
	photo_comment = forms.CharField(max_length=MAX_PHOTO_COMMENT_SIZE, error_messages={'required': 'Pehlay safed patti mein likhein, phir "reply" dabain'})
	sk = forms.CharField(required=False)
	origin = forms.CharField(required=False)

	class Meta:
		fields = ("photo_comment",)

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.photo_id = kwargs.pop('photo_id',None)
		self.is_mob_verified = kwargs.pop('mob_verified',False)
		super(PhotoCommentForm, self).__init__(*args, **kwargs)
		self.fields['photo_comment'].widget.attrs['class'] = 'box-with-button-right cdo'
		self.fields['photo_comment'].widget.attrs['style'] = 'border: 1px solid lightgrey; border-radius:4px;'
		self.fields['photo_comment'].widget.attrs['autocomplete'] = 'off'
		self.fields['photo_comment'].widget.attrs['autocapitalize'] = 'off'
		self.fields['photo_comment'].widget.attrs['spellcheck'] = 'false'
		self.fields['photo_comment'].widget.attrs['maxlength'] = MAX_PHOTO_COMMENT_SIZE

	def clean(self):
		if not self.is_mob_verified:
			raise forms.ValidationError('Account verify kiye beghair ap yahan nahi likh saktey')
		else:
			data = self.cleaned_data
			comment, user_id, photo_id, section, secret_key_from_form, origin = data.get("photo_comment"), self.user_id, self.photo_id, \
			'pht_comm', data.get("sk"), data.get("origin")
			if origin == '1' or origin == '20':
				org = 'fresh_photos'
			elif origin == '3' or origin == '19':
				org = 'home'
			else:
				org = 'best_photos'
			secret_key_from_session = get_and_delete_text_input_key(user_id,'1',org)
			if secret_key_from_form != secret_key_from_session:
				raise forms.ValidationError('Sirf aik dafa button dabain')
			comment = comment.strip() if comment else comment
			if not comment:
				raise forms.ValidationError('Pehlay safed patti mein likhein, phir "reply" button dabain')
			elif repetition_found(section=section,section_id=photo_id,user_id=user_id, target_text=comment):
				raise forms.ValidationError('Milti julti baatien nahi likhein, kuch new likhein')
			else:
				rate_limited, reason = is_limited(user_id,section='pht_comm',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap photos pe reply karney se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					comm_len = len(comment)
					if comm_len < 6:
						if many_short_messages(user_id,section,photo_id):
							raise forms.ValidationError('Har thori deir baad choti reply nahi likhein')
						else:
							log_short_message(user_id,section,photo_id)
					elif comm_len > MAX_PHOTO_COMMENT_SIZE:
						raise forms.ValidationError('Itni lambi reply nahi likh sakte')
					return data


class UnseenActivityForm(forms.Form):
	home_comment = forms.CharField(required=False, max_length=MAX_HOME_REPLY_SIZE, error_messages={'required': 'Pehlay yahan likhein, phir "reply" button dabain'})
	photo_comment = forms.CharField(required=False, max_length=MAX_PHOTO_COMMENT_SIZE, error_messages={'required': 'Pehlay yahan likhein, phir "reply" button dabain'})
	public_group_reply = forms.CharField(required=False, max_length=PUBLIC_GROUP_REPLY_LENGTH, error_messages={'required': 'Pehlay yahan likhein, phir "reply" button dabain'})
	private_group_reply = forms.CharField(required=False, max_length=PRIVATE_GROUP_REPLY_LENGTH, error_messages={'required': 'Pehlay yahan likhein, phir "reply" button dabain'})
	personal_group_reply = forms.CharField(required=False, max_length=500, error_messages={'required': 'Pehlay yahan likhein, phir "reply" button dabain'})
	sk = forms.CharField(required=False)
	origin = forms.CharField(required=False)

	class Meta:
		fields = ("home_comment", "photo_comment", "public_group_reply", "private_group_reply", "personal_group_reply")

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.link_id = kwargs.pop('link_id',None)
		self.photo_id = kwargs.pop('photo_id',None)
		self.pub_grp_id = kwargs.pop('pub_grp_id',None)
		self.prv_grp_id = kwargs.pop('prv_grp_id',None)
		self.per_grp_id = kwargs.pop('per_grp_id',None)
		super(UnseenActivityForm, self).__init__(*args, **kwargs)
		self.fields['public_group_reply'].widget.attrs['class'] = 'box-with-button-right cp'
		self.fields['public_group_reply'].widget.attrs['style'] = 'border: 1px solid #765989'
		self.fields['public_group_reply'].widget.attrs['autocomplete'] = 'off'
		self.fields['public_group_reply'].widget.attrs['autocapitalize'] = 'off'
		self.fields['public_group_reply'].widget.attrs['spellcheck'] = 'false'

		self.fields['private_group_reply'].widget.attrs['class'] = 'box-with-button-right cdg'
		self.fields['private_group_reply'].widget.attrs['style'] = 'border: 1px solid #00c853'
		self.fields['private_group_reply'].widget.attrs['autocomplete'] = 'off'
		self.fields['private_group_reply'].widget.attrs['autocapitalize'] = 'off'
		self.fields['private_group_reply'].widget.attrs['spellcheck'] = 'false'

		self.fields['home_comment'].widget.attrs['class'] = 'box-with-button-right cdt'
		self.fields['home_comment'].widget.attrs['style'] = 'border: 1px solid #229ec3'
		self.fields['home_comment'].widget.attrs['autocomplete'] = 'off'
		self.fields['home_comment'].widget.attrs['autocapitalize'] = 'off'
		self.fields['home_comment'].widget.attrs['spellcheck'] = 'false'

		self.fields['photo_comment'].widget.attrs['class'] = 'box-with-button-right cdo'
		self.fields['photo_comment'].widget.attrs['style'] = 'border: 1px solid #ff9933'
		self.fields['photo_comment'].widget.attrs['autocomplete'] = 'off'
		self.fields['photo_comment'].widget.attrs['autocapitalize'] = 'off'
		self.fields['photo_comment'].widget.attrs['spellcheck'] = 'false'

		self.fields['personal_group_reply'].widget.attrs['class'] = 'box-with-button-right'
		self.fields['personal_group_reply'].widget.attrs['style'] = 'color:#306654;border: 1px solid #306654'
		self.fields['personal_group_reply'].widget.attrs['autocomplete'] = 'off'
		self.fields['personal_group_reply'].widget.attrs['autocapitalize'] = 'off'
		self.fields['personal_group_reply'].widget.attrs['spellcheck'] = 'false'


	def clean(self):
		data, user_id = self.cleaned_data, self.user_id
		origin, secret_key_from_form = data.get("origin"), data.get("sk")
		if origin in ('1','20'):
			org = 'fresh_photos'
		elif origin in ('3','19'):
			org = 'home'
		elif origin in ('2','21'):
			org = 'best_photos'
		else:
			org = 'home'
		secret_key_from_session = get_and_delete_text_input_key(user_id,'1',org)
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('Sirf aik dafa button dabain, bar bar nahi')
		else:
			link_id, photo_id, pub_grp_id, prv_grp_id, per_grp_id = self.link_id, self.photo_id, self.pub_grp_id, self.prv_grp_id, self.per_grp_id
			if link_id:
				section, payload, obj_id = 'home_rep', data.get("home_comment"), link_id
				payload = payload.strip() if payload else None
				if not payload:
					raise forms.ValidationError('Pehlay text likhein, phir button dabain')
				elif repetition_found(section=section,section_id=obj_id,user_id=user_id, target_text=payload):
					raise forms.ValidationError('Aik hi reply bar bar nahi likhein')
				rate_limited, reason = is_limited(user_id,section=section,with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap reply karney se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					len_payload = len(payload)
					if len_payload < 6:
						if many_short_messages(user_id,section,obj_id):
							raise forms.ValidationError('Har thori deir baad yahan choti reply nahi likhein')
						else:
							log_short_message(user_id,section,obj_id)
					elif len_payload > MAX_HOME_REPLY_SIZE:
						raise forms.ValidationError('Itni lambi reply nahi likh sakte')
					return data
			elif photo_id:
				section, payload, obj_id = 'pht_comm', data.get("photo_comment"), photo_id
				payload = payload.strip() if payload else None
				if not payload:
					raise forms.ValidationError('Pehlay text likhein, phir button dabain')
				elif repetition_found(section=section,section_id=obj_id,user_id=user_id, target_text=payload):
					raise forms.ValidationError('Aik hi reply bar bar nah likhein')
				rate_limited, reason = is_limited(user_id,section=section,with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap photo pe reply karney se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					len_payload = len(payload)
					if len_payload < 6:
						if many_short_messages(user_id,section,obj_id):
							raise forms.ValidationError('Har thori deir baad yahan choti reply nahi likhein')
						else:
							log_short_message(user_id,section,obj_id)
					elif len_payload > MAX_PHOTO_COMMENT_SIZE:
						raise forms.ValidationError('Itni lambi reply nahi likh sakte')
					return data
			elif pub_grp_id:
				section, payload, obj_id= 'pub_grp', data.get("public_group_reply"), pub_grp_id
				#######################################
				membership = is_group_member_and_rules_signatory(group_id=obj_id, user_id=user_id)
				is_member, is_signatory = membership[0], membership[1]
				#######################################
				if is_member and is_signatory:
					payload = payload.strip() if payload else None
					if not payload:
						raise forms.ValidationError('Pehlay text likhein, phir button dabain')
					elif repetition_found(section=section,section_id=obj_id,user_id=user_id, target_text=payload):
						raise forms.ValidationError('Milti julti baatien nahi post karein')
					rate_limited, reason = is_limited(user_id,section=section,with_reason=True)
					if rate_limited > 0:
						raise forms.ValidationError('Ap public mehfils mein post karney se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
					else:
						len_payload = len(payload)
						if len_payload < 6:
							if many_short_messages(user_id,section,obj_id):
								raise forms.ValidationError('Har thori deir baad yahan choti reply nah likhein')
							else:
								log_short_message(user_id,section,obj_id)
						elif len_payload > 500:
							raise forms.ValidationError('Itni lambi reply nahi likh sakte')
						return data
				elif is_member:
					# needs to become a signatory
					raise forms.ValidationError('Pehlay mehfil ke andr ja ke rules accept karein')
				else:
					raise forms.ValidationError('Pehlay mehfil ke andr ja ke "join" press karein')
			elif prv_grp_id:
				section, payload, obj_id = 'prv_grp', data.get("private_group_reply"), prv_grp_id
				#######################################
				is_member = group_member_exists(group_id=obj_id, user_id=user_id)
				#######################################
				if is_member:
					payload = payload.strip() if payload else None
					if not payload:
						raise forms.ValidationError('Pehlay text likhein, phir button dabain')
					elif repetition_found(section=section,section_id=obj_id,user_id=user_id, target_text=payload):
						raise forms.ValidationError('Aik hi reply bar bar nahi likhein')
					rate_limited, reason = is_limited(user_id,section='prv_grp',with_reason=True)
					if rate_limited > 0:
						raise forms.ValidationError('Ap private mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
					else:
						len_payload = len(payload)
						if len_payload < 6:
							if many_short_messages(user_id,section,obj_id):
								raise forms.ValidationError('Har thori deir baad yahan choti reply nahi likhein')
							else:
								log_short_message(user_id,section,obj_id)
						elif len_payload > 500:
							raise forms.ValidationError('Itni lambi reply nahi likh sakte')
						return data
				else:
					raise forms.ValidationError('Pehlay mehfil ke andr ja ke "join" press karein')
			elif per_grp_id:
				payload = data.get("personal_group_reply")
				payload = payload.strip() if payload else None
				if not payload:
					raise forms.ValidationError('Pehlay text likhein, phir button dabain')
				# No need to check for repetition, length or rate limit
				return data
			else:
				pass
			return data


class PhotoTimeForm(forms.Form):
	class Meta:
		pass


class UploadPhotoReplyForm(forms.ModelForm):
	image_file = forms.ImageField(error_messages={'required': 'Photo ka intekhab dubara karein'})
	caption = forms.CharField(widget=forms.Textarea(attrs={'cols':20,'rows':2,'style':'width:98%;'}), error_messages={'required': 'Photo ke bary mien likhna zaroori hai'})
	class Meta:
		model = Photo
		exclude = ("owner", "children", "child_count", "upload_time", "comment_count", "category", "device", "latest_comment", "second_latest_comment", "is_visible", "visible_score", "invisible_score",)
		fields = ("image_file", "caption",)

	def __init__(self, *args, **kwargs):
		super(UploadPhotoReplyForm, self).__init__(*args, **kwargs)
		self.fields['image_file'].widget.attrs['style'] = 'width:95%;'


class UploadPhotoForm(forms.Form):
	image_file = forms.ImageField(label='Upload', error_messages={'required': 'Photo ka intekhab sahi nahi hua','invalid':'Selected photo upload nahi ho sakti'})
	caption = forms.CharField(widget=forms.Textarea(attrs={'cols':20,'rows':2,'spellcheck':'false','maxlength':MAX_PHOTO_CAPTION_SIZE}),\
		error_messages={'required': 'Photo ke barey mien likhna zaroori hai'})

	def __init__(self, *args, **kwargs):
		super(UploadPhotoForm, self).__init__(*args, **kwargs)
		self.fields['caption'].widget.attrs['style'] = 'width:95%;height:70px;border-radius:10px;border: 1px #93d7ec solid; background-color:white;padding:7px;'
		self.fields['caption'].widget.attrs['id'] = 'pub_img_caption_field'
		self.fields['caption'].widget.attrs['class'] = 'cxl'
		self.fields['image_file'].widget.attrs['style'] = 'width:95%;background:#beeef4;height:45px;border-radius:7px'
		self.fields['image_file'].widget.attrs['id'] = 'browse_pub_img_btn'

	def clean_caption(self):
		caption = self.cleaned_data["caption"]
		caption = caption.strip() if caption else None
		caption = strip_zero_width_characters(caption)
		if not caption:
			raise forms.ValidationError('Photo ke barey mien likhna zaroori hai')
		else:
			caption_len = len(caption)
			if caption_len < 1:
				raise forms.ValidationError('Photo ke barey mien likhna zaroori hai')
			if caption_len < 8:
				raise forms.ValidationError('Zyada tafseel likhein ke photo mein kya hai')
			elif caption_len > MAX_PHOTO_CAPTION_SIZE:
				raise forms.ValidationError('{} chars se zyada nahi likhein, ap ne {} chars likhey'.format(MAX_PHOTO_CAPTION_SIZE,caption_len))
			elif caption.isdigit():
				raise forms.ValidationError('Sirf numbers nahi likhein, tafseel se likhein photo mein kya hai')
			elif '#' in caption:
				raise forms.ValidationError('Photo ki tafseel mein "#" nahi likhein')
			uni_str = uniform_string(caption)
			if uni_str:
			  if uni_str.isspace():
			      raise forms.ValidationError('Spaces itni zyada nahi daalein')
			  else:
			      raise forms.ValidationError('"%s" itni zyada dafa aik hi character repeat nahi karein, photo ko sahi se describe karein' % uni_str)
			else:
				return caption


class UploadVideoForm(forms.Form):
	video_file = forms.FileField()
	caption = forms.CharField(widget=forms.Textarea(attrs={'cols':20,'rows':2,'style':'width:98%;'}), error_messages={'required': 'Video ke bary mien likhna zaroori hai'})
	class Meta:
		fields = ("video_file", "caption",)

class PicsChatUploadForm(forms.ModelForm):
	image = forms.ImageField(label='Upload')
	class Meta:
		model = ChatPic
		exclude = ("sender","sending_time", "sms_created", "expiry_interval")
		fields = ("image",)

	def __init__(self, *args, **kwargs):
		super(PicsChatUploadForm, self).__init__(*args, **kwargs)
		self.fields['image'].widget.attrs['style'] = 'width:95%;'
		# self.fields['image'].widget.attrs['accept'] = 'image/*'


class HomeLinkListForm(forms.Form):
	reply = forms.CharField(max_length=250)

	class Meta:
		fields = ("reply",)

	def __init__(self, *args, **kwargs):
		super(HomeLinkListForm, self).__init__(*args, **kwargs)
		self.fields['reply'].widget.attrs['style'] = \
		'background-color:#F8F8F8;width:1400px;max-width:90%;border: 1px solid #1f8cad;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #1f8cad;'

class BestPhotosListForm(forms.Form):
	class Meta:
		pass

class PhotosListForm(forms.Form):
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

	def __init__(self, *args, **kwargs):
		super(PicPasswordForm, self).__init__(*args, **kwargs)
		self.fields['mobile_number'].widget.attrs['style'] = 'width:95%;'

class SalatTutorialForm(forms.Form):
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

# class PhotoQataarHelpForm(forms.Form):
# 	class Meta:
# 		pass

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

class PicExpiryForm(forms.Form):
	class Meta:
		pass

class VerifiedForm(forms.Form):
	class Meta:
		model = User

class TopPhotoForm(forms.Form):
	class Meta:
		model = User

class TopForm(forms.Form):
	class Meta:
		model = User

class DeviceHelpForm(forms.Form):
	class Meta:
		pass

class ReportcommentForm(forms.Form):
	class Meta:
		pass

# class MehfilCommentForm(forms.Form):
# 	class Meta:
# 		pass

class WelcomeForm(forms.Form):
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

class LogoutPenaltyForm(forms.Form):
	class Meta:
		pass

class UserProfileDetailForm(forms.Form):
	class Meta:
		pass

class ScoreHelpForm(forms.Form):
	class Meta:
		pass

class RegisterLoginForm(forms.Form):
	class Meta:
		pass

class ReauthForm(forms.Form):
	password = forms.CharField(widget=forms.TextInput(attrs={'placeholder':''}))
	class Meta:
		fields = ("password",)

	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request',None)
		super(ReauthForm, self).__init__(*args,**kwargs)
		self.fields['password'].error_messages = {'required':retrieve_validation_error_string('pass_empty'),'invalid':retrieve_validation_error_string('generic')}
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color:#1cb841;'
		self.fields['password'].widget.attrs['class'] = 'cxl'
		self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'
		self.fields['password'].widget.attrs['autocapitalize'] = 'none'
		self.fields['password'].widget.attrs['spellcheck'] = 'false'

	def clean_password(self):
		entered_password = self.cleaned_data["password"]
		real_password = self.request.user.password
		if check_password(password=entered_password,encoded=real_password):
			return entered_password
		else:
			raise forms.ValidationError(retrieve_validation_error_string('generic'))


class ResetPasswordForm(forms.Form):
	password = forms.CharField()
	class Meta:
		fields = ('password',)

	def __init__(self,*args,**kwargs):
		self.request = kwargs.pop('request',None)
		super(ResetPasswordForm, self).__init__(*args,**kwargs)
		self.fields['password'].error_messages = {'required':retrieve_validation_error_string('pass_empty'),'invalid':retrieve_validation_error_string('generic')}
		self.fields['password'].widget.attrs['style'] = \
		'background-color:#fffce6;width:1000px;border: 1px solid #00c853;max-width:90%;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color:#1cb841;'
		self.fields['password'].widget.attrs['class'] = 'cxl'
		self.fields['password'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['password'].widget.attrs['autocomplete'] = 'off'
		self.fields['password'].widget.attrs['autocapitalize'] = 'none'
		self.fields['password'].widget.attrs['spellcheck'] = 'false'

	def clean_password(self):
		password = self.cleaned_data["password"]
		password = password.strip()
		if not password:
			raise ValidationError(retrieve_validation_error_string('pass_empty'))
		else:
			old_password = self.request.user.password
			lower_pass = password.lower()
			nickname = self.request.user.username
			lower_nick = nickname.lower()
			if check_password(password,old_password):
				raise ValidationError(retrieve_validation_error_string('old_new_pass_same'))
			if len(password) < 6:
				raise ValidationError(retrieve_validation_error_string('pass_too_small'))
			elif lower_pass in '1234567890':
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',payload=lower_pass))
			elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',payload=lower_pass))
			elif lower_nick in lower_pass:
				raise ValidationError(retrieve_validation_error_string('nickname_in_pass',payload=nickname))
			elif 'facebook' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',payload='facebook'))
			elif 'damadam' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',payload='damadam'))
			elif 'qwerty' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('banned_sequence_in_pass',payload='qwerty'))
			elif 'babykobasspasandhai' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',payload='babykobasspasandhai'))
			elif 'chaachi420' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',payload='chaachi420'))
			elif 'garamaanday' in lower_pass:
				raise ValidationError(retrieve_validation_error_string('example_sequence_in_pass',payload='garamaanday'))
			else:
				return password


	def save(self, commit=True):
		user = self.request.user
		password = self.cleaned_data["password"]
		user.set_password(password)
		if commit:
			user.save()
		return user

class SmsReinviteForm(forms.Form):
	class Meta:
		pass

class SmsInviteForm(forms.Form):
	class Meta:
		pass

class HistoryHelpForm(forms.Form):
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

class SearchAdFeedbackForm(forms.Form):
	ad_campaign = forms.CharField(max_length=100)

	def __init__(self, *args, **kwargs):
		super(SearchAdFeedbackForm, self).__init__(*args, **kwargs)
		self.fields['ad_campaign'].widget.attrs['style'] = \
		'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #179b36;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #179b36;'
		self.fields['ad_campaign'].widget.attrs['class'] = 'cxl'
		self.fields['ad_campaign'].widget.attrs['autofocus'] = 'autofocus'

	def clean_ad_campaign(self):
		ad_campaign = self.cleaned_data.get("ad_campaign")
		ad_campaign = ad_campaign.strip()
		if len(ad_campaign) > 100:
			raise forms.ValidationError('tip: inta bara name nahi likh sakte')
		ad_campaign = clear_zalgo_text(ad_campaign)
		return ad_campaign

class AdFeedbackForm(forms.Form):
	feedback = forms.CharField(widget=forms.Textarea(attrs=\
		{'cols':40,'rows':3,'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid green;border-radius:5px;color: #404040;'}),\
		validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
		'required':_("(tip: isko khali nahi chore sakte)")})
	class Meta:
		fields = ("feedback",)

	def __init__(self, *args, **kwargs):
		super(AdFeedbackForm, self).__init__(*args, **kwargs)
		self.fields['feedback'].widget.attrs['class'] = 'cxl'
		self.fields['feedback'].widget.attrs['autocomplete'] = 'off'

	def clean_feedback(self):
		feedback = self.cleaned_data.get("feedback")
		feedback = feedback.strip()
		if len(feedback) < 5:
			raise forms.ValidationError('(tip: is se ziyada likho)')
		elif len(feedback) > 250:
			raise forms.ValidationError('(tip: buhut ziyada likh diya hai. Chota karo)')
		feedback = clear_zalgo_text(feedback)
		return feedback
		
