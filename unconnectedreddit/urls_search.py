from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, url
from django.contrib import admin
from links.search_views import search_username, go_to_username, go_to_user_photo, remove_searched_username

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Search nicknames functionality##########################################
	url(r'^search/nickname/remove-from-history/(?P<nick>[\w.@+-]+)/$', auth(remove_searched_username), name='remove_searched_username'),
	url(r'^search/nickname/$', auth(search_username), name='search_username'),
	url(r'^search/nickname/redirect/(?P<nick>[\w.@+-]+)/$', auth(go_to_username), name='go_to_username'),
	url(r'^search/nickname/redirect/photo/(?P<nick>[\w.@+-]+)/(?P<add_score>\d+)/$', auth(go_to_user_photo), name='go_to_user_photo'),
)