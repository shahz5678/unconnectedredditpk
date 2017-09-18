# coding=utf-8
from django.template.defaulttags import register
from links.error_translations import FORM_SUBMISSION_ERRORS

@register.filter(name='get_ur')
def get_ur(string):
	if 'kisi aur ka naam hai' in string:
		return 'یہ نام پہل سے کسی نے رکھا ہوا ہے، کوئ اور نام رکھو'
	elif 'nahi ho sakta!' in string:
		return 'نام میں برے الفاظ نہ ڈالو'
	elif 'ko boojhna aasan hai' in string:
		return 'اس پاس ورڈ کا اندازہ لگانا آسان ہے۔ کچھ اور لکھو'
	elif 'kiyunke naam mein hai' in string:
		return 'پاس ورڈ میں نام نہ ڈالو'
	elif 'naam aap se pehle' in string:
		return 'یہ نام ابھی ابھی کسی اور نے رکھ لیا۔ معذرت'
	elif 'safed patti mein' in string:
		return 'اس سفید پٹی میں نام لکھو'
	elif 'sirf english harf' in string:
		return 'نام میں صرف انگریزی حروف یا نمبر ہو سکتے ہیں'
	elif 'hamarey record mein nahi' in string:
		return 'یہ نک نیم ﮨمارے رکارڈ میں نہیں'
	elif 'Agr bhool gaye ho' in string:
		return 'پاس ورڈ غلط لکھا ہے ۔ اگر بھول گۓ ﮨو تو نیچے "پاس ورڈ بھول گۓ" کو دباؤ'
	elif 'naam khali nah choro' in string:
		return 'نک نیم خالی نہ چھوڑو'
	elif 'chota harf bara'  in string:
		return 'نک نیم میں یا بڑا حرف چھوٹا لکھ دیا ے، یا چھوٹا حرف بڑا'
	else:
		return FORM_SUBMISSION_ERRORS[string]