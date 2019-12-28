from django.contrib import admin
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as auth
from links.follower_views import follow, unfollow, custom_feed_page, custom_feed_redirect, show_follower_list, remove_my_follower,\
show_following_list, remove_single_post, display_user_public_feed_history, display_user_follower_feed_history,skip_notif,\
display_user_private_feed_history, show_new_followers
from links.views import finalize_audience, publish_post
admin.autodiscover()

urlpatterns = patterns('',

	####################### Display feed #######################
	url(r'^for-me/$', auth(custom_feed_page), name='my_home'),
	####################### Remove post ########################
	url(r'^for-me/remove-single-post/$', auth(remove_single_post), name='remove_post'),
	####################### Redirects #######################
	url(r'^redirect/for-me/$', auth(custom_feed_redirect), name='custom_feed_redirect'),
	url(r'^redirect/for-me/(?P<obj_hash>[\w:@+-]+)/$', auth(custom_feed_redirect), name='custom_feed_redirect'),
	####################### Follow/Unfollow #######################
	url(r'^follow/add/$', auth(follow), name='follow'),
	url(r'^follow/remove/$', auth(unfollow), name='unfollow'),
	url(r'^follow/remove-my-follower/(?P<target_username>[\w.@+-]+)/$', auth(remove_my_follower), name='remove_my_follower'),
	url(r'^follow/skip_notif/$', auth(skip_notif), name='skip_notif'),
	url(r'^follow/recent_followers/$', auth(show_new_followers), name='show_new_followers'),
	####################### User feed history #######################
	url(r'^profile/public/(?P<target_uname>[\w.@+-]+)/$', display_user_public_feed_history, name='display_user_public_feed_history'),
	url(r'^profile/followers/(?P<target_uname>[\w.@+-]+)/$', auth(display_user_follower_feed_history), name='display_user_follower_feed_history'),
	url(r'^profile/private/(?P<target_uname>[\w.@+-]+)/$', auth(display_user_private_feed_history), name='display_user_private_feed_history'),
	####################### Display followers #######################
	url(r'^profile/follower-list/$', auth(show_follower_list), name='show_follower_list'),
	url(r'^profile/following-list/$', auth(show_following_list), name='show_following_list'),
	####################### Select followers #######################
	url(r'^share/select-followers/$', auth(finalize_audience), name='finalize_audience'),
	url(r'^share/publish/$', auth(publish_post), name='publish_post'),
)