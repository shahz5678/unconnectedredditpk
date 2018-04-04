# coding=utf-8
from django.template.defaulttags import register
from links.error_translations import FORM_SUBMISSION_ERRORS

@register.filter(name='get_ur')
def get_ur(string):
	if 'kisi aur ka nickname hai' in string:
		return 'یہ نام پہل سے کسی نے رکھا ہوا ہے، کوئ اور نام رکھو'
	elif 'nahi ho sakta!' in string:
		return 'نام میں برے الفاظ نہ ڈالو'
	elif 'ko boojhna aasan hai' in string:
		return 'اس پاس ورڈ کا اندازہ لگانا آسان ہے۔ کچھ اور لکھو'
	elif 'kiyunke nickname mein hai' in string:
		return 'پاس ورڈ میں نام نہ ڈالو'
	elif 'nickname ap se pehle' in string:
		return 'یہ نام ابھی ابھی کسی اور نے رکھ لیا۔ معذرت'
	elif 'safed patti mein' in string:
		return 'اس سفید پٹی میں نام لکھو'
	elif 'sirf english harf' in string:
		return 'نام میں صرف انگریزی حروف یا نمبر ہو سکتے ہیں'
	elif 'hamarey record mein nahi' in string:
		return 'یہ نک نیم ﮨمارے رکارڈ میں نہیں'
	elif 'Agr bhool gaye hain' in string:
		return 'پاس ورڈ غلط لکھا ہے ۔ اگر بھول گۓ ﮨو تو نیچے "پاس ورڈ بھول گۓ" کو دباؤ'
	elif 'nickname khali nah chorein' in string:
		return 'نک نیم خالی نہ چھوڑو'
	elif 'chota harf bara'  in string:
		return 'نک نیم میں یا بڑا حرف چھوٹا لکھ دیا ے، یا چھوٹا حرف بڑا'
	elif 'Nickname mein harf likhna' in string:
		return 'نک نیم میں حرف لکهنا ضروری ے'
	elif 'Password mein harf likhna' in string:
		return 'پاس ورڈ میں حرف لکهنا ضروری ے'
	elif 'akhir mein . nah' in string:
		return 'نک نیم کے آخر میں نقطہ نہ ڈالیں'
	elif 'shuru mein . nah' in string:
		return 'نک نیم کے شروع میں نقطہ نہ ڈالیں'
	else:
		return FORM_SUBMISSION_ERRORS[string]