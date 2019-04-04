from django.contrib import admin
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as auth
from links.push_notification_api import save_subscription, push_notification_permission_denied, push_notification_permission_temporarily_denied, \
push_notification_not_available, push_notification_not_working
from links.group_views import decide_notification_perms_in_personal_group, personal_group_notif_prompts, personal_group_subscription_failure,\
personal_group_subscription_success, render_notification_perms_in_personal_group, send_push_notification_for_1on1, logging_notif_reception,\
logging_notif_allowance

admin.autodiscover()

urlpatterns = patterns('',
	###################################### Push notifications ########################################
	url(r'^push-notification/subscription/save/$', auth(save_subscription), name='save_subscription'),
	url(r'^push-notification/subscription/malformed-target/$', auth(push_notification_not_working), name='push_notification_not_working'),
	url(r'^push-notification/subscription/unavailable/$', auth(push_notification_not_available), name='push_notification_not_available'),
	url(r'^push-notification/subscription/denied/$', auth(push_notification_permission_denied), name='push_notification_permission_denied'),
	url(r'^push-notification/subscription/temporarily-denied/$', auth(push_notification_permission_temporarily_denied), name='push_notification_permission_temporarily_denied'),
	###################################### Push notifications (1on1) ########################################
	url(r'^1-on-1/push-notif/settings/decision/$', auth(decide_notification_perms_in_personal_group), name='decide_notification_perms_in_personal_group'),
	url(r'^1-on-1/push-notif/settings/$', auth(render_notification_perms_in_personal_group), name='render_notification_perms_in_personal_group'),
	url(r'^1-on-1/push-notif/send/$', auth(send_push_notification_for_1on1), name='send_push_notification_for_1on1'),
	url(r'^1-on-1/push-notif/received/$', logging_notif_reception, name='logging_notif_reception'),
	url(r'^1-on-1/push-notif/allow-attempt/$', auth(logging_notif_allowance), name='logging_notif_allowance'),
	url(r'^1-on-1/push-notif/success/$', auth(personal_group_notif_prompts), name='personal_group_notif_successfully_sent'),
	url(r'^1-on-1/push-notif/failure/rate-limited/$', auth(personal_group_notif_prompts), name='personal_group_notif_failure_rate_limited'),
	url(r'^1-on-1/push-notif/failure/1on1-does-not-exist/$', auth(personal_group_notif_prompts), name='personal_group_notif_failure_1on1_gone'),
	url(r'^1-on-1/push-notif/failure/no-permission-given/$', auth(personal_group_notif_prompts), name='personal_group_notif_failure_not_permitted'),
	url(r'^1-on-1/push-notif/failure/subscription-action/$', auth(personal_group_subscription_failure), name='personal_group_subscription_failure'),
	url(r'^1-on-1/push-notif/failure/browser-subscription-expired/$', auth(personal_group_notif_prompts), name='personal_group_notif_failure_subscription_expired'),
	url(r'^1-on-1/push-notif/success/subscription-action/$', auth(personal_group_subscription_success), name='personal_group_subscription_success'),
)