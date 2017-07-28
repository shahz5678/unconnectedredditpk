# coding=utf-8
from django import forms
from django.forms import Textarea
from .tasks import log_gibberish_writer
from .redis1 import get_prev_retorts, get_prev_replies, get_prev_group_replies, many_short_messages, log_short_message
from .models import UserProfile, TutorialFlag, ChatInbox, PhotoStream, PhotoComment, ChatPicMessage, Photo, Link, Vote, \
ChatPic, UserSettings, Publicreply, Group, GroupInvite, Reply, GroupTraffic, GroupCaptain, VideoComment
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core import validators
from django.core.files.images import get_image_dimensions
from django.utils.translation import ugettext, ugettext_lazy as _
from image_processing import compute_avg_hash, restyle_image, reorient_image, make_thumbnail, clean_image_file, clean_image_file_with_hash
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import re, time
from user_sessions.models import Session
import unicodedata
from fuzzywuzzy import fuzz


def can_group_reply(text,user_id):
    prev_group_replies = get_prev_group_replies(user_id)
    # print prev_group_replies
    for group_reply in prev_group_replies:
        score = fuzz.partial_ratio(text,group_reply.decode('utf-8'))
        if score > 95:
            return False
    return True

def can_reply(text,user_id):
    prev_publicreplies = get_prev_replies(user_id)
    for publicreply in prev_publicreplies:
        score = fuzz.partial_ratio(text,publicreply.decode('utf-8'))
        if score > 95:
            return False
    return True

def can_post(text,user_id):
    prev_retorts = get_prev_retorts(user_id)
    for retort in prev_retorts:
        score = fuzz.partial_ratio(text,retort.decode('utf-8'))
        if score > 85:
            return False
    return True

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
            image = make_thumbnail(image,None)
            return image
        else:
            return 0

    def clean_bio(self):
        bio = self.cleaned_data.get("bio")
        bio = bio.strip()
        bio = clear_zalgo_text(bio)
        return bio

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if len(age) > 2:
            raise forms.ValidationError('tip: age sahi likho')
        return age

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
        'class': 'cxl','autocomplete': 'off'}))
    class Meta:
        fields = ("description",)

    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop('request', None)
        super(CricketCommentForm, self).__init__(*args, **kwargs)

    def clean_description(self):
        description = self.cleaned_data.get("description")
        description = description.strip()
        if len(description) < 10:
            raise forms.ValidationError('tip: itna choti baat nahi likh sakte')
        elif len(description) > 500:
            raise forms.ValidationError('tip: itna barri baat nahi likh sakte')
        description = clear_zalgo_text(description)
        uni_str = uniform_string(description)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('tip: ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
        if not can_post(description,self.request.user.id):
            raise forms.ValidationError('tip: milti julti baatein nah likho, kuch new likho')
        return description

class LinkForm(forms.ModelForm):#this controls the link edit form
    description = forms.CharField(label='Likho:', widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;',\
        'class': 'cxl','autofocus': 'autofocus','autocomplete': 'off'}))
    class Meta:
        model = Link
        exclude = ("submitter", "rank_score", "cagtegory",)
        fields = ("image_file", "description",)

    def __init__(self,*args,**kwargs):
        self.user_id = kwargs.pop('user_id',None)
        super(LinkForm, self).__init__(*args,**kwargs)

    def clean_description(self):
        description = self.cleaned_data.get("description")
        description = description.strip()
        len_ = len(description)
        if len_ < 2:
            raise forms.ValidationError('itni choti baat nahi likh sakte')
        elif len_ < 10:
            if many_short_messages(self.user_id):
                raise forms.ValidationError('har thori deir baad choti baat nah likho')
            else:
                log_short_message(self.user_id)
        elif len_ > 500:
            raise forms.ValidationError('itni barri baat nahi likh sakte')
        description = clear_zalgo_text(description)
        if not can_post(description,self.user_id):
            raise forms.ValidationError('milti julti batein nah likho, kuch new likho')
        uni_str = uniform_string(description)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('"%s" is terhan bar bar ek hi harf nah likho' % uni_str)
        log_gibberish_writer.delay(self.user_id,description,len_) # flags the user_id in case the text turned out to be gibberish
        return description

class PublicGroupReplyForm(forms.ModelForm):
    text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;',\
        'class': 'cxl','autofocus': 'autofocus','autocomplete': 'off'}))
    class Meta:
        model = Reply
        exclude = ("submitted_on","which_group","writer","abuse")
        fields = ("image", "text")

    def __init__(self,*args,**kwargs):
        self.user_id = kwargs.pop('user_id',None)
        super(PublicGroupReplyForm, self).__init__(*args,**kwargs)

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()
        if len(text) < 2:
            raise forms.ValidationError('tip: itni choti baat nahi likh sakte')
        elif len(text) > 500:
            raise forms.ValidationError('tip: intni barri baat nahi likh sakte')
        text = clear_zalgo_text(text)
        uni_str = uniform_string(text)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('tip: ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
        if not can_group_reply(text,self.user_id):
            raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
        return text

class OutsiderGroupForm(forms.ModelForm):
    text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3}))
    class Meta:
        model = Reply
        exclude = ("submitted_on","which_group","writer","abuse")
        fields = ("image", "text")

class PrivateGroupReplyForm(forms.ModelForm):
    text = forms.CharField(label='Likho:',widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;',\
        'class': 'cxl','autofocus': 'autofocus','autocomplete': 'off'}))
    class Meta:
        model = Reply
        exclude = ("submitted_on","which_group","writer","abuse")
        fields = ("image", "text")

    def __init__(self,*args,**kwargs):
        self.user_id = kwargs.pop('user_id',None)
        super(PrivateGroupReplyForm, self).__init__(*args,**kwargs)

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()
        if len(text) < 2:
            raise forms.ValidationError('tip: itni choti baat nahi likh sakte')
        elif len(text) > 500:
            raise forms.ValidationError('tip: intni barri baat nahi likh sakte')
        text = clear_zalgo_text(text)
        uni_str = uniform_string(text)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('tip: ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
        if not can_group_reply(text,self.user_id):
            raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
        return text

class WelcomeMessageForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3}))
    class Meta:
        model = Publicreply
        exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
        fields = ("description",)

class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;',\
        'class': 'cxl','autofocus': 'autofocus','autocomplete': 'off'}))
    class Meta:
        model = PhotoComment
        exclude = ("which_video", "device", "submitted_by", "submitted_on",)
        fields = ("text",)

    def __init__(self,*args,**kwargs):
        self.user_id = kwargs.pop('user_id',None)
        super(CommentForm, self).__init__(*args,**kwargs)

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()
        if len(text) < 2:
            raise forms.ValidationError('tip: tabsre mein itna chota lafz nahi likh sakte')
        elif len(text) > 250:
            raise forms.ValidationError('tip: inta bara tabsra nahi likh sakte')
        text = clear_zalgo_text(text)
        uni_str = uniform_string(text)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('tip: ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
        if not can_reply(text,self.user_id):
            raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
        return text

class VideoCommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
    class Meta:
        model = VideoComment
        exclude = ("which_photo", "device", "submitted_by", "submitted_on",)
        fields = ("text",)

class PublicreplyForm(forms.ModelForm):
    description = forms.CharField(label='Jawab:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;',\
        'class': 'cxl','autofocus': 'autofocus','autocomplete': 'off'}))
    class Meta:
        model = Publicreply
        exclude = ("submitted_by","answer_to","seen","category","abuse","submitted_on")
        fields = ("description",)

    def __init__(self,*args,**kwargs):
        self.user_id = kwargs.pop('user_id',None)
        super(PublicreplyForm, self).__init__(*args,**kwargs)

    def clean_description(self):
        description = self.cleaned_data.get("description")
        description = description.strip()
        if len(description) < 2:
            raise forms.ValidationError('tip: itna chota jawab nahi likh sakte')
        elif len(description) > 250:
            raise forms.ValidationError('tip: inta bara jawab nahi likh sakte')
        description = clear_zalgo_text(description)
        uni_str = uniform_string(description)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('tip: ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
        if not can_reply(description,self.user_id):
            raise forms.ValidationError('tip: milte julte jawab nah likho, kuch new likho')
        return description

class PublicreplyMiniForm(PublicreplyForm):
    description = forms.CharField(max_length=250)

    def __init__(self,*args,**kwargs):
        super(PublicreplyMiniForm, self).__init__(*args,**kwargs)
        self.fields['description'].widget.attrs['style'] = \
        'background-color:#F8F8F8;width:1000px;max-width:95%;border: 1px solid #1f8cad;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #1f8cad;'
        self.fields['description'].widget.attrs['autocomplete'] = 'off'

class SearchNicknameForm(forms.Form):
    nickname = forms.CharField(max_length=71)

    def __init__(self, *args, **kwargs):
        super(SearchNicknameForm, self).__init__(*args, **kwargs)
        self.fields['nickname'].widget.attrs['style'] = \
        'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #179b36;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #179b36;'
        self.fields['nickname'].widget.attrs['class'] = 'cxl'
        # self.fields['nickname'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['nickname'].widget.attrs['autocomplete'] = 'off'

    def clean_nickname(self):
        nickname = self.cleaned_data.get("nickname")
        nickname = nickname.strip()
        if len(nickname) > 70:
            raise forms.ValidationError('tip: inta bara naam nahi likh sakte')
        nickname = clear_zalgo_text(nickname)
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

class UnseenActivityForm(forms.Form):
    comment = forms.CharField(max_length=250)
    group_reply = forms.CharField(max_length=500)
    class Meta:
        fields = ("comment", "group_reply", )

    def __init__(self,*args,**kwargs):
        self.user = kwargs.pop('user',None)
        super(UnseenActivityForm, self).__init__(*args, **kwargs)
        self.fields['group_reply'].widget.attrs['style'] = \
        'background-color:#F8F8F8;max-width:95%;width:1000px;border: 1px solid #a6a6a6;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #404040;'
        self.fields['group_reply'].widget.attrs['autocomplete'] = 'off'
        self.fields['comment'].widget.attrs['style'] = \
        'background-color:#F8F8F8;max-width:95%;width:1000px;border: 1px solid #a6a6a6;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #404040;'
        self.fields['comment'].widget.attrs['autocomplete'] = 'off'

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        comment = comment.strip()
        if len(comment) < 2:
            raise forms.ValidationError('tip: itna chota lafz nahi likh sakte')
        elif len(comment) > 250:
            raise forms.ValidationError('tip: inti barri baat nahi likh sakte')
        comment = clear_zalgo_text(comment)
        uni_str = uniform_string(comment)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('tip: ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
        if not can_reply(comment,self.user.id):
            raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
        return comment

    def clean_group_reply(self):
        group_reply = self.cleaned_data.get("group_reply")
        group_reply = group_reply.strip()
        if len(group_reply) < 2:
            raise forms.ValidationError('tip: itna chota lafz nahi likh sakte')
        elif len(group_reply) > 500:
            raise forms.ValidationError('tip: inti barri baat nahi likh sakte')
        group_reply = clear_zalgo_text(group_reply)
        uni_str = uniform_string(group_reply)
        if uni_str:
            if uni_str.isspace():
                raise forms.ValidationError('tip: ziyada spaces daal di hain')
            else:
                raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
        if not can_group_reply(group_reply,self.user.id):
            raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
        return group_reply

class PhotoTimeForm(forms.Form):
    class Meta:
        pass

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
        super(OpenGroupCreateForm, self).__init__(*args, **kwargs)
        self.fields['topic'].widget.attrs['style'] = 'width:95%;'
        self.fields['rules'].widget.attrs['style'] = 'width:95%;'

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
        self.fields["image_file"].widget.attrs['class'] = 'p'

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

class PhotoReportForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs=\
        {'style':'max-width:90%;background-color:#F8F8F8;border: 1px solid red;border-radius:5px;color: #404040;'}),\
        validators=[validators.RegexValidator(regex="^[A-Za-z0-9._~()'!*:@, ;+?-]*$")],error_messages={'invalid': _("(tip: sirf english harf, number ya @ _ . + - likh sakte ho)"),\
        'required':_("(tip: report ko khali nahi chore sakte)")})
    class Meta:
        fields = ("description",)

    def __init__(self, *args, **kwargs):
        super(PhotoReportForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'cxl'
        self.fields['description'].widget.attrs['autofocus'] = 'autofocus'

    def clean_description(self):
        description = self.cleaned_data.get("description")
        description = description.strip()
        if len(description) < 5:
            raise forms.ValidationError('(tip: itni choti report nahi likh sakte)')
        elif len(description) > 250:
            raise forms.ValidationError('(tip: inti barri report nahi likh sakte)')
        description = clear_zalgo_text(description)
        return description

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

class DirectMessageForm(forms.Form):
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

class ReauthForm(forms.Form):
    password = forms.CharField(widget=forms.TextInput(attrs={'placeholder':''}))
    class Meta:
        fields = ("password",)

    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop('request',None)
        super(ReauthForm, self).__init__(*args,**kwargs)
        self.fields['password'].widget.attrs['style'] = 'max-width:95%;'

    def clean_password(self):
        entered_password = self.cleaned_data["password"]
        real_password = self.request.user.password
        if check_password(password=entered_password,encoded=real_password):
            return entered_password
        else:
            raise forms.ValidationError('Password theek nahi, phir se likho')


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        fields = ('password',)

    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop('request',None)
        super(ResetPasswordForm, self).__init__(*args,**kwargs)
        self.fields['password'].widget.attrs['style'] = 'max-width:95%;'

    def clean_password(self):
        password = self.cleaned_data["password"]
        password = password.strip()
        old_password = self.request.user.password
        lower_pass = password.lower()
        nickname = self.request.user.username
        lower_nick = nickname.lower()
        if check_password(password,old_password):
            raise ValidationError('New password purane password se mukhtalif rakho')
        if len(password) < 6:
            raise ValidationError('Kam se kam 6 harf likhna zaruri hai!')
        elif lower_pass in '1234567890':
            raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho'  % lower_pass)
        elif lower_pass == lower_pass[0]*len(lower_pass): #checks if it's a string made of a single character
            raise ValidationError('"%s" ko boojhna aasan hai, kuch aur likho'  % lower_pass)
        elif lower_nick in lower_pass:
            raise ValidationError('"%s" nahi likh sakte kiyunke naam mein hai' % nickname)
        elif 'damadam' in lower_pass:
            raise ValidationError('"damadam" ko boojhna aasan hai, kuch aur likho')
        elif 'qwerty' in lower_pass:
            raise ValidationError('"qwerty" ko boojhna aasan hai, kuch aur likho')
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

class SmsReinviteForm(forms.Form):
    class Meta:
        pass

class SmsInviteForm(forms.Form):
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
