from django.conf.urls import patterns, url
from django.contrib import admin
from links.unauth_views import unauth_home_new, create_nick_new, create_password_new, create_account, login, forgot_password, log_google_in, \
set_forgetters_password, create_dummy_user, logout_then_login, prelim_mobile_verification#verify_forgetters_pin, send_SMS_to_forgetter, unauth_home_new_ur
from django.contrib.auth.decorators import login_required as auth    
from links.views import first_time_choice, new_user_gateway, turn_off_newbie
#from links.number_verification import verify_forgetter_number

############################Optimizely Experiment############################
# from links.views import first_time_choice, new_user_gateway, first_time_best#
#############################################################################

admin.autodiscover()

urlpatterns = patterns('',
	
	########################################Optimizely####################################################
	# url(r'^first_time_best/(?P<algo>[\w.@+-]+)/$', auth(first_time_best), name='first_time_best'),#
	# url(r'^new_user_choice/(?P<best>[\w.@+-]+)/(?P<algo>[\w.@+-]+)/$', auth(first_time_choice), name='first_time_choice'),
	######################################################################################################
	
	url(r'^turn-off-newbie/(?P<origin>\d+)/$', auth(turn_off_newbie), name='turn_off_newbie'),
	url(r'^new-user-gateway/$', auth(new_user_gateway), name='new_user_gateway'),
	url(r'^new-user-gateway/(?P<lang>[\w.@+-]+)/$', auth(new_user_gateway), name='new_user_gateway'),
	url(r'^new-user-choice/$', auth(first_time_choice), name='first_time_choice'),
	url(r'^new-user-choice/(?P<lang>[\w.@+-]+)/$', auth(first_time_choice), name='first_time_choice'),

	url(r'^duc/$',create_dummy_user, name="create_dummy_user"),
	url(r'^goog_login/$', log_google_in, {"template_name": "unauth/login_backdoor.html"}, "login_backdoor"),

	############################## Forgot Password Functionality ##############################

	url(r'^forgot-password/$',forgot_password, name="forgot_password"),
	#url(r'^forgot-password/sms/$',send_SMS_to_forgetter, name="send_SMS_to_forgetter"),
	# url(r'^forgot-password/verify-pin/$',verify_forgetters_pin, name="verify_forgetters_pin"),

	url(r'^forgot-password/set-new-pass/$',set_forgetters_password, name="set_forgetters_password"),
	url(r'^forgot-password/confirm-number/$',prelim_mobile_verification, name="prelim_mobile_verification"),
	#url(r'^forgot-password/confirm-number/$',verify_forgetter_number, name="verify_forgetter_number"),	
	# url(r'^forgot-password/sms/(?P<lang>[\w.@+-]+)/$',send_SMS_to_forgetter, name="send_SMS_to_forgetter"),
	#url(r'^forgot-password/verify-pin/(?P<lang>[\w.@+-]+)/$',verify_forgetters_pin, name="verify_forgetters_pin"),
	url(r'^forgot-password/confirm-number/(?P<lang>[\w.@+-]+)/$',prelim_mobile_verification, name="prelim_mobile_verification"),
	url(r'^forgot-password/(?P<lang>[\w.@+-]+)/$',forgot_password, name="forgot_password"),
	url(r'^forgot-password/set-new-pass/(?P<lang>[\w.@+-]+)/$',set_forgetters_password, name="set_forgetters_password"),
	
	############################################################################################

	url(r'^login/$',login, name="login"),
	url(r'^logout-then-login/$', auth(logout_then_login), name='logout_then_login'),
	url(r'^login/(?P<lang>[\w.@+-]+)/$',login, name="login"),
	
	url(r'^signup/$', unauth_home_new, name='unauth_home_new'),

	url(r'^signup/create-nick/$', create_nick_new, name='create_nick'),
	url(r'^signup/create-name/$', create_nick_new, name='create_nick_new'),
	
	url(r'^signup/create-pass/new/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password_new'),
	url(r'^signup/create-pass/new/(?P<lang>[\w.@+-]+)/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password_new'),
	url(r'^signup/create-name/(?P<lang>[\w.@+-]+)/$', create_nick_new, name='create_nick_new'),
	url(r'^signup/create-pass/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password'), #[\w.?)&;[\]}:${@+-]+
	
	url(r'^signup/create-acc/(?P<slug1>[\w.@+-]+)/(?P<length1>\d+)/(?P<slug2>[\w.@+-]+)/(?P<length2>\d+)/$', create_account, name='create_account'),
	url(r'^signup/create-acc/(?P<lang>[\w.@+-]+)/(?P<slug1>[\w.@+-]+)/(?P<length1>\d+)/(?P<slug2>[\w.@+-]+)/(?P<length2>\d+)/$', create_account, name='create_account'),
	
	url(r'^signup/(?P<lang>[\w.@+-]+)/$', unauth_home_new, name='unauth_home_new'),

	url(r'^home-unauth/$', unauth_home_new, name='unauth_home'),
	url(r'^uphredi/(?P<pk>\d+)/$', unauth_home_new, name='unauth_photo_loc_pk'),
	url(r'^utphredi/(?P<pk>\d+)/$', unauth_home_new, name='unauth_best_photo_loc_pk'),
	url(r'^seetopphotos/$', unauth_home_new, name='unauth_best_photo'),
	url(r'^seefreshphotos/$', unauth_home_new, name='unauth_photo'),
)

