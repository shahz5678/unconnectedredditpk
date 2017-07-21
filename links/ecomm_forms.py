# coding=utf-8
import StringIO, re
from django import forms
from forms import clear_zalgo_text, uniform_string
from django.core.exceptions import ValidationError
from django.core import validators
from django.utils.translation import ugettext, ugettext_lazy as _


def get_choices(num_list):
	nums = []
	for num in num_list:
		num = "0"+num
		nums.append((num,num))
	nums.append(('Kisi aur number pe','Kisi aur number pe'))
	return tuple(nums)


class EditFieldForm(forms.Form):
	text_field = forms.CharField()

	def __init__(self, *args, **kwargs):
		super(EditFieldForm, self).__init__(*args, **kwargs)
		self.fields['text_field'].widget.attrs['autofocus'] = 'autofocus'
		self.fields['text_field'].widget.attrs['class'] = 'cxl'

class VerifySellerMobileForm(forms.Form):
	mobile_number = forms.CharField(max_length=13,\
		error_messages={'required':_("Is mein mobile number likho")})

	def clean_mobile_number(self):
		mobile_number = self.cleaned_data.get("mobile_number")
		if mobile_number.isdigit():
			return mobile_number
		else:
			raise forms.ValidationError('Mobile number sahi nahi hai, dubara likho')


class SellerInfoForm(forms.Form):

	seller_name = forms.RegexField(max_length=43, regex=re.compile("^[a-zA-Z\s]+$"),\
		error_messages={'invalid': _("Naam mein sirf english harf ho sakta hai"),\
		'required':_("Is mein apna naam likho")})
	city = forms.RegexField(max_length=250,regex=re.compile("^[A-Za-z0-9._~()'!*:@, ;+?-]*$"),\
		error_messages={'invalid': _("sirf english harf, number ya @ _ . + - likh sakte ho"),\
		'required':_("is mein apna city likho")})
	town = forms.RegexField(max_length=250,regex=re.compile("^[A-Za-z0-9._~()'!*:@, ;+?-]*$"),\
		error_messages={'invalid': _("sirf english harf, number ya @ _ . + - likh sakte ho"),\
		'required':_("is mein apna ilaka likho")})


	def __init__(self, *args, **kwargs):
		self.has_num_on_file = kwargs.pop('mob_num', None)
		self.nums = kwargs.pop('nums', None)
		super(SellerInfoForm, self).__init__(*args, **kwargs)
		if self.nums:
			# initializing a new field if self.nums exists
			mob_num_choices = get_choices(self.nums)
			self.fields['mobile'] = forms.TypedChoiceField(choices=mob_num_choices,initial='0'+self.nums[0],required=False,widget=forms.RadioSelect,\
				error_messages={'required': 'Intikhab karo'})
		self.fields['seller_name'].widget.attrs['class'] = 'cxl'
		self.fields['seller_name'].widget.attrs['style'] = \
		'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #179b36;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #179b36;'
		self.fields['city'].widget.attrs['class'] = 'cxl'
		self.fields['city'].widget.attrs['style'] = \
		'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #179b36;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #179b36;'
		self.fields['town'].widget.attrs['class'] = 'cxl'
		self.fields['town'].widget.attrs['style'] = \
		'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #179b36;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #179b36;'

	def clean_seller_name(self):
		seller_name = self.cleaned_data.get("seller_name")
		seller_name = seller_name.strip()
		seller_name_length = len(seller_name)
		if seller_name_length < 2:
			raise forms.ValidationError('Poora naam likho')
		elif seller_name_length > 42:
			raise forms.ValidationError('Naam chota kar ke likho')
		return " ".join(seller_name.split())

	def clean_city(self):
		city = self.cleaned_data.get("city")
		city = city.strip()
		city_length = len(city)
		if city_length < 2:
			raise forms.ValidationError('City ka poora naam likho')
		elif city_length > 249:
			raise forms.ValidationError('Naam chota kar ke likho')
		return " ".join(city.split())

	def clean_town(self):
		town = self.cleaned_data.get("town")
		town = town.strip()
		town_length = len(town)
		if town_length < 2:
			raise forms.ValidationError('Ilakey ka poora naam likho')
		elif town_length > 249:
			raise forms.ValidationError('Naam chota kar ke likho')
		return " ".join(town.split())

	# def clean_mobile(self):
	# 	mobile = self.cleaned_data.get("mobile")
	# 	return mobile
		# mobile = mobile.strip()
		# mobile_length = len(mobile)
		# if self.has_num_on_file:
		# 	if not mobile:
		# 		raise forms.ValidationError('Mobile number likhna zaruri hai')
		# 	elif mobile_length < 11:
		# 		raise forms.ValidationError('Poora mobile number likho')
		# return ''.join(re.split('[, \-_!?:]+',mobile)) #removes any excess characters from the mobile number

class BasicItemPhotosForm(forms.Form):
	photo1 = forms.ImageField(label='Upload', required=False, error_messages={'invalid': 'Photo ka intekhab sahi nahi hua'})
	photo2 = forms.ImageField(label='Upload', required=False, error_messages={'invalid': 'Photo ka intekhab sahi nahi hua'})
	photo3 = forms.ImageField(label='Upload', required=False, error_messages={'invalid': 'Photo ka intekhab sahi nahi hua'})

	def __init__(self,*args,**kwargs):
		super(BasicItemDetailForm,self).__init__(*args,**kwargs)
		self.fields["photo1"].widget.attrs['id'] = 'p1'
		self.fields["photo2"].widget.attrs['id'] = 'p2'
		self.fields["photo3"].widget.attrs['id'] = 'p3'

class BasicItemDetailForm(forms.Form):
	NEWORUSED = (
		('Istamal shuda','Istamal shuda'),
		('Bilkul new','Bilkul new'),
		)
	BARTER = (
		('Sirf paisey','Sirf paisey'),
		('Paisey aur badley mein cheez dono','Paisey aur badley mein cheez dono'),
		)
	description = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':2,'class': 'cxl','autofocus': 'autofocus','autocomplete': 'off'}),\
	error_messages={'required': 'Isko khali nahi chore saktey'})
	new = forms.TypedChoiceField(choices=NEWORUSED, initial='Istamal shuda',widget=forms.RadioSelect,error_messages={'required': 'In mein se aik chunno'})
	ask = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'rows':1,'class': 'cxl'}),error_messages={'required': 'Isko khali nahi chore saktey'})
	barter = forms.TypedChoiceField(choices=BARTER, initial='Paisey aur badley mein cheez dono',widget=forms.RadioSelect,error_messages={'required': 'In mein se aik chunno'})

	def __init__(self, *args, **kwargs):
		super(BasicItemDetailForm, self).__init__(*args, **kwargs)
		self.fields['description'].widget.attrs['style'] = \
		'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #179b36;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #179b36;'
		self.fields['ask'].widget.attrs['style'] = \
		'max-width:90%;width:500px;background-color:#F8F8F8;border: 1px solid #179b36;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #179b36;'

	def clean_description(self):
		description = self.cleaned_data.get("description")
		description = description.strip()
		if len(description) < 10:
			raise forms.ValidationError('Aur tafseel likho takey khareedar ka trust barhey')
		elif len(description) > 500:
			raise forms.ValidationError('Tafseel ko chota karo takey khareedar asani se parh sakey')
		description = clear_zalgo_text(description)
		uni_str = uniform_string(description)
		if uni_str:
			if uni_str.isspace():
				raise forms.ValidationError('Ziyada spaces daal di hain')
			else:	
				raise forms.ValidationError('"%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
		return description

	def clean_ask(self):
		ask = self.cleaned_data.get("ask")
		ask = ask.strip()
		if len(ask) < 3:
			raise forms.ValidationError('Sahi price likho')
		elif len(ask) > 20:
			raise forms.ValidationError('Sahi price likho')
		elif ask in '00000000':
			raise forms.ValidationError('Sahi price likho')
		return ask

class EcommCityForm(forms.Form):
	loc = forms.RegexField(max_length=250,regex=re.compile("^[A-Za-z0-9._~()'!*:@, ;+?-]*$"),\
		error_messages={'invalid': _("sirf english harf, number ya @ _ . + - likh sakte ho"),\
		'required':_("isko khali nahi chore sakte")})

	def __init__(self,*args,**kwargs):
		super(EcommCityForm, self).__init__(*args,**kwargs)
		self.fields['loc'].widget.attrs['style'] = \
		'background-color:#F8F8F8;width:1000px;max-width:85%;border: 1px solid #1f8cad;border-radius:5px;padding: 6px 6px 6px 0;text-indent: 6px;color: #1f8cad;'
		self.fields['loc'].widget.attrs['autocomplete'] = 'off'

	def clean_loc(self):
		loc = self.cleaned_data.get("loc")
		loc = loc.strip()
		if len(loc) < 3:
			raise forms.ValidationError('itna chota city ka naam nahi likh sakte!')
		elif loc.isdigit():
			raise ValidationError('city ke naam mein sirf numbers nahi ho sakte!')
		elif loc.lower() == 'islamabad':
			raise ValidationError('Islamabad ko wapis ja ke list mein se select kro!')
		elif loc.lower() == 'lahore':
			raise ValidationError('Lahore ko wapis ja ke list mein se select kro!')
		elif loc.lower() == 'rawalpindi':
			raise ValidationError('Rawalpindi ko wapis ja ke list mein se select kro!')
		return loc

# class AddShopForm(forms.Form):
# 	LOCATIONS = (  
#     ('Rawalpindi', 'Rawalpindi'),
#     ('Islamabad', 'Islamabad'),
#     ('Lahore', 'Lahore'),
#     ('Karachi', 'Karachi'),)
	
# 	# Should we add photos?

# 	shop_name = forms.RegexField(max_length=250,regex=re.compile("^[a-zA-Z\s]+$"),\
# 		error_messages={'invalid': _("Shop name mein sirf english harf, number ya @ _ . + - ho sakta hai"),\
# 		'required':_("Is mein shop name likhein:")})
# 	city = forms.ChoiceField(choices=LOCATIONS, required=True)
# 	address = forms.CharField(max_length=50,\
# 		error_messages={'invalid': _("Address mein sirf english harf, number ya @ _ . + - ho sakta hai"),\
# 		'required':_("Is mein address likhein:")})
# 	mobile = forms.CharField(max_length=13,\
# 		error_messages={'required':_("Is mein mobile number likhein:")})
# 	owner_name = forms.RegexField(max_length=43, regex=re.compile("^[a-zA-Z\s]+$"),\
# 		error_messages={'invalid': _("Name mein sirf english harf ho sakta hai"),\
# 		'required':_("Is mein name likhein:")})
# 	owner_cnic = forms.CharField(max_length=50,\
# 		error_messages={'invalid': _("CNIC mein sirf english harf, number ya @ _ . + - ho sakta hai"),\
# 		'required':_("Is mein CNIC likhein:")})
# #####################################################################################################	