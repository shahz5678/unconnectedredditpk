from django import forms
from .models import UserProfile, Link, Vote, UserSettings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image, ImageFile
import StringIO
import math
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

def MakeThumbnail(file):
    img = file
    img = square_image(img)
    img.thumbnail((120, 120))
    thumbnailString = StringIO.StringIO()
    if img.mode != 'RGB':
        img = img.convert("RGB")
    img.save(thumbnailString, 'JPEG')
    newFile = InMemoryUploadedFile(thumbnailString, None, 'temp.jpg', 'image/jpeg', thumbnailString.len, None)
    return newFile

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
    avatar = forms.ImageField(label='Upload Photo', help_text='less than 1 mb')
    gender = forms.TypedChoiceField(choices=MardAurat, widget=forms.RadioSelect, coerce=int)
    shadi_shuda = forms.TypedChoiceField(choices=MaritalStatus, widget=forms.RadioSelect, coerce=int)
    attractiveness = forms.TypedChoiceField(choices=RATING, widget=forms.RadioSelect, coerce=int)
    class Meta:
        model = UserProfile
        exclude = ('user','previous_retort') #so user and previous_retort doesn't show, but the extended attributes of bio and mobile number do show    
        fields=('avatar', 'mobilenumber', 'bio', 'gender', 'age', 'shadi_shuda', 'attractiveness')
    

    def clean_avatar(self): # where self is the form
        image=self.cleaned_data.get("avatar")
        if image:
            if image.size > 1000000:
                raise ValidationError("File buhut barri hai, doosri try karo")
            image = Image.open(image)
            image = MakeThumbnail(image)
            return image
        else:
            raise ValidationError("File kharab hai, doosri try karo")       

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

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        exclude = ("submitter", "rank_score", "category")
        fields = ("description", "url")

class VoteForm(forms.ModelForm): #creates a form for Vote
    class Meta:
        model = Vote

class ScoreHelpForm(forms.Form):
    class Meta:
        pass

class HelpForm(forms.Form):
    class Meta:
        pass
#####################################################################################################