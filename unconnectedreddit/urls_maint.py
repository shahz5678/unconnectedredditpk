from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.maint_views import insert_nicks, change_nicks, export_nicks, deprecate_nicks, remove_inactives_notification_activity, \
remove_inactive_user_sessions


admin.autodiscover()


urlpatterns = patterns('',
	######################################## Redis Sanitzation ########################################
	url(r'^delete_sessions/$', auth(remove_inactive_user_sessions), name='remove_inactive_user_sessions'),
	url(r'^delete_notifications/$', auth(remove_inactives_notification_activity), name='remove_inactives_notification_activity'),
	######################################## Username Sanitzation ########################################
	url(r'^populate_nicks/$', auth(insert_nicks), name='insert_nicks'),
	url(r'^change_nicks/$', auth(change_nicks), name='change_nicks'),
	url(r'^export_nicks/$', auth(export_nicks), name='export_nicks'),
	url(r'^deprecate_nicks/$', auth(deprecate_nicks), name='deprecate_nicks'),
)