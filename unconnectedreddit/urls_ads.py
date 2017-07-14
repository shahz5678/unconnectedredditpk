from links.views import skin_clinic, skin_doctor_price, ad_feedback, virgin_tees, bykea, asan_doc
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Ads##########################################
	url(r'^ad_feedback/', auth(ad_feedback), name='ad_feedback'),
	url(r'^vtees/', auth(virgin_tees), name='virgin_tees'),
	url(r'^bykea/', auth(bykea), name='bykea'),
	url(r'^skin_clinic/', auth(skin_clinic), name='skin_clinic'),
	url(r'^skin_doctor_price/', auth(skin_doctor_price), name='skin_doctor_price'),
	url(r'^asan_doc/', auth(asan_doc), name='asan_doc'),
)