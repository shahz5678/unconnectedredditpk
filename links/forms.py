from django import forms
from .models import UserProfile, Link, Vote, UserSettings
from django.contrib.auth.models import User


class UserProfileForm(forms.ModelForm):
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
    gender = forms.TypedChoiceField(choices=MardAurat, widget=forms.RadioSelect, coerce=int)
    shadi_shuda = forms.TypedChoiceField(choices=MaritalStatus, widget=forms.RadioSelect, coerce=int)
    attractiveness = forms.TypedChoiceField(choices=RATING, widget=forms.RadioSelect, coerce=int)
    class Meta:
        model = UserProfile
        exclude = ('user','previous_retort') #so user and previous_retort doesn't show, but the extended attributes of bio and mobile number do show    
        fields=('mobilenumber', 'bio', 'gender', 'age', 'shadi_shuda', 'attractiveness')

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