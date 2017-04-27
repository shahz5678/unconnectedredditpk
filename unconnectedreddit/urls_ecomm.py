from links.ecomm import show_ecomm_choices, x2lite_details, x32_details, buyer_loc, process_city
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	#############################################E Commerce##########################################
	url(r'^mobile/$', show_ecomm_choices,name='ecomm'),
	url(r'^mobile/x32/$', x32_details,name='x32'),
	url(r'^mobile/x2lite/$', x2lite_details,name='x2lite'),
	url(r'^mobile/loc/$', auth(buyer_loc),name='buyer_loc'),
	url(r'^mobile/proc_city/$', auth(process_city),name='process_city'),
)