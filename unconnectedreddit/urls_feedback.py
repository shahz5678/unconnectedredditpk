from links.export_website_feedback import export_error_feedback, export_website_feedback
from links.user_feedback import website_feedback, see_website_feedback, website_choices_feedback
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Ads##########################################
	url(r'^see_website_feedback/$', auth(see_website_feedback), name='see_website_feedback'),
	url(r'^feedback/$', auth(website_feedback), name='website_feedback'),
	url(r'^choices_feedback/$', auth(website_choices_feedback), name='website_choices_feedback'),
	#############################################Ads##########################################
	url(r'^export_website_feedback/$', auth(export_website_feedback), name='export_website_feedback'),
	url(r'^export_error_feedback/$', auth(export_error_feedback), name='export_error_feedback'),
)