from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.retention import export_logged_users_and_times

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^export_logged_users/$', auth(export_logged_users_and_times), name='export_logged_users'),
	#################################################################################################
)