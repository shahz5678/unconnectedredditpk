from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.retention_views import export_logged_users_and_times, display_retention, reset_retention_counters, export_logged_actions

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^export_logged_users/$', auth(export_logged_users_and_times), name='export_logged_users'),
	#################################################################################################
	url(r'^export/actions/$', auth(export_logged_actions), name='export_logged_actions'),
	url(r'^retention/delete/$', auth(reset_retention_counters), name='reset_retention_counters'),
	url(r'^retention/(?P<variation>[\w.@+-]+)/$', auth(display_retention), name='display_retention'),
)