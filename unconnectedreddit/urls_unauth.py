from django.conf.urls import patterns, url
from django.contrib import admin
from links.unauth_views import unauth_home_new, unauth_home_new_ur, create_nick_new, create_password_new, create_account, login, forgot_password, log_google_in, \
set_forgetters_password, create_dummy_user
from django.contrib.auth.decorators import login_required as auth    
from links.views import first_time_choice, new_user_gateway
from links.number_verification import verify_forgetter_number

############################Optimizely Experiment############################
# from links.views import first_time_choice, new_user_gateway, first_time_best#
#############################################################################

admin.autodiscover()

urlpatterns = patterns('',
	
	########################################Optimizely####################################################
	# url(r'^first_time_best/(?P<algo>[\w.@+-]+)/$', auth(first_time_best), name='first_time_best'),#
	# url(r'^new_user_choice/(?P<best>[\w.@+-]+)/(?P<algo>[\w.@+-]+)/$', auth(first_time_choice), name='first_time_choice'),
	######################################################################################################

	url(r'^new_user_gateway/$', auth(new_user_gateway), name='new_user_gateway'),
	url(r'^new_user_gateway/(?P<lang>[\w.@+-]+)/$', auth(new_user_gateway), name='new_user_gateway'),
	url(r'^new_user_choice/$', auth(first_time_choice), name='first_time_choice'),
	url(r'^new_user_choice/(?P<lang>[\w.@+-]+)/$', auth(first_time_choice), name='first_time_choice'),

	url(r'^duc/$',create_dummy_user, name="create_dummy_user"),
	url(r'^goog_login/$', log_google_in, {"template_name": "login_backdoor.html"}, "login_backdoor"),

	url(r'^forgot_password/$',forgot_password, name="forgot_password"),
	url(r'^forgot_password/(?P<lang>[\w.@+-]+)/$',forgot_password, name="forgot_password"),
	url(r'^set_new_pass/$',set_forgetters_password, name="set_forgetters_password"),
	url(r'^vfn/$',verify_forgetter_number, name="verify_forgetter_number"),
	
	url(r'^login/$',login, name="login"),
	url(r'^login/(?P<lang>[\w.@+-]+)/$',login, name="login"),
	
	url(r'^signup/', unauth_home_new, name='unauth_home_new'),
	url(r'^signup_ur/', unauth_home_new_ur, name='unauth_home_new_ur'),
	
	url(r'^create_nick/$', create_nick_new, name='create_nick'),
	url(r'^create_name/$', create_nick_new, name='create_nick_new'),
	url(r'^create_name/(?P<lang>[\w.@+-]+)/$', create_nick_new, name='create_nick_new'),

	url(r'^create_pass/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password'), #[\w.?)&;[\]}:${@+-]+
	url(r'^create_pass_new/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password_new'),
	url(r'^create_pass_new/(?P<lang>[\w.@+-]+)/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password_new'),
	
	url(r'^create_acc/(?P<slug1>[\w.@+-]+)/(?P<length1>\d+)/(?P<slug2>[\w.@+-]+)/(?P<length2>\d+)/$', create_account, name='create_account'),
	url(r'^create_acc/(?P<lang>[\w.@+-]+)/(?P<slug1>[\w.@+-]+)/(?P<length1>\d+)/(?P<slug2>[\w.@+-]+)/(?P<length2>\d+)/$', create_account, name='create_account'),
	
	url(r'^home_unauth/', unauth_home_new, name='unauth_home'),
	url(r'^uphredi/(?P<pk>\d+)/$', unauth_home_new, name='unauth_photo_loc_pk'),
	url(r'^utphredi/(?P<pk>\d+)/$', unauth_home_new, name='unauth_best_photo_loc_pk'),
	url(r'^seetopphotos/$', unauth_home_new, name='unauth_best_photo'),
	url(r'^seefreshphotos/$', unauth_home_new, name='unauth_photo'),
)

