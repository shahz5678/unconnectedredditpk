from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.maint_views import insert_nicks, change_nicks, export_nicks, deprecate_nicks, remove_inactives_notification_activity, \
remove_inactive_user_sessions, remove_inactives_groups, damadam_cleanup, skip_outage_notif


admin.autodiscover()


urlpatterns = patterns('',
	##################################### Shutdown Notifications ######################################
	url(r'^son/$', auth(skip_outage_notif), name='skip_outage_notif'),
	url(r'^damadam_cleanup/$', auth(damadam_cleanup), name='damadam_cleanup'),
	######################################## Redis Sanitzation ###########################################
	url(r'^cleanup_groups/$', auth(remove_inactives_groups), name='remove_inactives_groups'),
	url(r'^delete_sessions/$', auth(remove_inactive_user_sessions), name='remove_inactive_user_sessions'),
	url(r'^delete_notifications/$', auth(remove_inactives_notification_activity), name='remove_inactives_notification_activity'),
	######################################## Username Sanitzation ########################################
	url(r'^populate_nicks/$', auth(insert_nicks), name='insert_nicks'),
	url(r'^change_nicks/$', auth(change_nicks), name='change_nicks'),
	url(r'^export_nicks/$', auth(export_nicks), name='export_nicks'),
	url(r'^deprecate_nicks/$', auth(deprecate_nicks), name='deprecate_nicks'),
)