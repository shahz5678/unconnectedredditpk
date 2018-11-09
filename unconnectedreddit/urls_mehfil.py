from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, url
from django.contrib import admin
from links.mehfil_views import GroupHelpView, ReinviteView, OpenGroupHelpView, ClosedGroupHelpView

admin.autodiscover()

urlpatterns = patterns('',
	############################################# Mehfil help ##########################################
	url(r'^group_help/$', auth(GroupHelpView.as_view()), name='group_help'),
	####################################### Mehfil invites #############################################
	url(r'^reinvite/(?P<slug>[\w.@+-]+)/$', auth(ReinviteView.as_view()), name='reinvite_help'),
	######################################### Mehfil creation ##########################################
	url(r'^open_group/help/$', auth(OpenGroupHelpView.as_view()), name='open_group_help'),
	url(r'^closed_mehfil/help/$', auth(ClosedGroupHelpView.as_view()), name='closed_group_help'),
)