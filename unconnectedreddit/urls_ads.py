from links.views import skin_clinic, skin_doctor_price, ad_feedback, virgin_tees, bykea, asan_doc
from links.number_verification import verify_careem_applicant
from links.ads_views import careem_ad, verify_careem_number, s_test
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^vca/', auth(verify_careem_applicant), name='verify_careem_applicant'),
	#############################################Ads##########################################
	url(r'^ad_feedback/', auth(ad_feedback), name='ad_feedback'),
	url(r'^vtees/', auth(virgin_tees), name='virgin_tees'),
	url(r'^bykea/', auth(bykea), name='bykea'),
	url(r'^skin_clinic/', auth(skin_clinic), name='skin_clinic'),
	url(r'^skin_doctor_price/', auth(skin_doctor_price), name='skin_doctor_price'),
	url(r'^asan_doc/', auth(asan_doc), name='asan_doc'),
	url(r'^careem_ad/', auth(careem_ad), name='careem_ad'),
	url(r'^s_test/', auth(s_test), name='s_test'),
	url(r'^verify_careem_number/', auth(verify_careem_number), name='verify_careem_number'),
)