from django.conf.urls import patterns, url
from django.contrib import admin
from links.unauth_views import unauth_home_new, unauth_home_new_ur, create_nick_new, create_nick_new_ur, create_password_new, create_password_new_ur,\
create_account, create_account_ur, login #, insert_nicks

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^login/$',login, name="login"),
	url(r'^signup/', unauth_home_new, name='unauth_home_new'),
	url(r'^signup_ur/', unauth_home_new_ur, name='unauth_home_new_ur'),
	url(r'^create_nick/$', create_nick_new, name='create_nick'),
	url(r'^createnick/$', create_nick_new, name='create_nick_new'),
	url(r'^create_pass/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password'), #[\w.?)&;[\]}:${@+-]+
	url(r'^create_pass_new/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password_new, name='create_password_new'),
	url(r'^create_acc/(?P<slug1>[\w.@+-]+)/(?P<length1>\d+)/(?P<slug2>[\w.@+-]+)/(?P<length2>\d+)/$', create_account, name='create_account'),
	url(r'^home_unauth/', unauth_home_new, name='unauth_home'),
	url(r'^uphredi/(?P<pk>\d+)/$', unauth_home_new, name='unauth_photo_loc_pk'),
	url(r'^utphredi/(?P<pk>\d+)/$', unauth_home_new, name='unauth_best_photo_loc_pk'),
	url(r'^seetopphotos/$', unauth_home_new, name='unauth_best_photo'),
	url(r'^seefreshphotos/$', unauth_home_new, name='unauth_photo'),
)
