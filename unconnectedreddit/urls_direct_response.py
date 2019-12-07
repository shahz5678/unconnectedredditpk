from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, url
from django.contrib import admin
from links.direct_response_views import render_direct_response_form, post_direct_response, retrieve_direct_responses, skip_direct_responses,\
retrieve_direct_response_activity, render_uname_list, remove_direct_response_activity_log

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Direct response functionality##########################################
	url(r'^inbox/$', auth(retrieve_direct_responses), name='retrieve_direct_responses'),
	url(r'^direct-response/send/$', auth(post_direct_response), name='post_direct_response'),
	url(r'^direct-response/skip/$', auth(skip_direct_responses), name='skip_direct_responses'),
	url(r'^direct-response/create/$', auth(render_direct_response_form), name='render_direct_response_form'),
	url(r'^inbox/activity/$', auth(retrieve_direct_response_activity), name='retrieve_direct_response_activity'),
	url(r'^inbox/activity/remove/$', auth(remove_direct_response_activity_log), name='remove_direct_response_activity_log'),
	url(r'^inbox/activity/interactions/(?P<obj_type>\d+)/(?P<parent_obj_id>[\w.@+-]+)/$', auth(render_uname_list), name='render_uname_list'),
)