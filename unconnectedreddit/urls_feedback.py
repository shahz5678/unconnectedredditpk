from links.export_website_feedback import export_error_feedback, export_website_feedback
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Ads##########################################
	url(r'^export_website_feedback/$', auth(export_website_feedback), name='export_website_feedback'),
	url(r'^export_error_feedback/$', auth(export_error_feedback), name='export_error_feedback'),
)