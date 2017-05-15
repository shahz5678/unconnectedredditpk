from links.views import umrah, umrah_price, ad_feedback
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Ads##########################################
	url(r'^ad_feedback/', auth(ad_feedback), name='ad_feedback'),
	url(r'^umrah/', auth(umrah), name='umrah'),
	url(r'^umrah_price/', auth(umrah_price), name='umrah_price'),
)