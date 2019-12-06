from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.retention_views import display_retention, export_retention_activity_raw_log, export_retention_activity_occurrence_log,\
export_retention_activity_frequency_log, export_logged_actions#, reset_retention_counters

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^retention/(?P<variation>[\w.@+-]+)/$', auth(display_retention), name='display_retention'),
	url(r'^retention/export/raw/$', auth(export_retention_activity_raw_log), name='export_retention_activity_raw_log'),
	url(r'^retention/export/freq/$', auth(export_retention_activity_frequency_log), name='export_retention_activity_frequency_log'),
	url(r'^retention/export/occur/$', auth(export_retention_activity_occurrence_log), name='export_retention_activity_occurrence_log'),
	#################################################################################################
	url(r'^export/actions/$', auth(export_logged_actions), name='export_logged_actions'),
)