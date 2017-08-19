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
	elif 'naam tum se pehle' in string:
		return 'یہ نام ابھی ابھی کسی اور نے رکھ لیا۔ معذرت'
	elif 'safed patti mein' in string:
		return 'اس سفید پٹی میں نام لکھو'
	elif 'sirf english harf':
		return 'نام میں صرف انگریزی حروف یا نمبر ہو سکتے ہیں'
	else:
		return FORM_SUBMISSION_ERRORS[string]