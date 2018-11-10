from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, url
from django.contrib import admin
from links.mehfil_views import GroupHelpView, ReinviteView, OpenGroupHelpView, ClosedGroupHelpView, MehfilView, AppointCaptainView, OwnerGroupOnlineKonView,\
GroupOnlineKonView, DirectMessageCreateView, ClosedGroupCreateView, OpenGroupCreateView, InviteUsersToPrivateGroupView, DirectMessageView, ReinvitePrivateView,\
InviteUsersToGroupView, GroupRankingView, appoint_pk, direct_message, leave_public_group, leave_private_group, left_private_group, mehfil_help, \
process_public_group_invite, process_private_group_invite,invite_private

admin.autodiscover()

urlpatterns = patterns('',
	############################################# Mehfil help #####################################
	url(r'^group_help/$', auth(GroupHelpView.as_view()), name='group_help'),
	####################################### Mehfil invites ########################################
	url(r'^reinvite/private/$', auth(ReinvitePrivateView.as_view()), name='reinvite_private_help'),
	url(r'^reinvite/(?P<slug>[\w.@+-]+)/$', auth(ReinviteView.as_view()), name='reinvite_help'),
	url(r'^pubmef/invite/$', auth(process_public_group_invite), name='process_public_group_invite'),
	url(r'^privmef/invite/$', auth(process_private_group_invite), name='process_private_group_invite'),	

	url(r'^privateinvite/(?P<slug>[\w.@+-]+)/$', auth(invite_private), name='invite_private'),	
	url(r'^privatemehfil/invite/$', auth(InviteUsersToPrivateGroupView.as_view()), name='invite_private_group'),
	url(r'^group/invite/$', auth(InviteUsersToGroupView.as_view()), name='invite'),
	######################################### Mehfil creation #####################################
	url(r'^open_group/help/$', auth(OpenGroupHelpView.as_view()), name='open_group_help'),
	url(r'^closed_mehfil/help/$', auth(ClosedGroupHelpView.as_view()), name='closed_group_help'),
	url(r'^mehfil/help/$', auth(MehfilView.as_view()), name='mehfil_help'),
	url(r'^mehfil_help/(?P<pk>\d+)/(?P<num>\d+)/$', auth(mehfil_help), name='mehfilhelp'),
	url(r'^closed_group/create/(?P<pk>\d+)/$', auth(DirectMessageCreateView.as_view()), name='direct_message_create'),
	url(r'^closed_group/create/$', auth(ClosedGroupCreateView.as_view()), name='closed_group_create'),
	url(r'^open_group/create/$', auth(OpenGroupCreateView.as_view()), name='open_group_create'),
	url(r'^dm/(?P<pk>\d+)/$', auth(direct_message), name='direct_message'),
	url(r'^closed_group/help/$', auth(DirectMessageView.as_view()), name='direct_message_help'),
	################################# Mehfil deletion #############################################
	url(r'^lvpgr/$', auth(leave_public_group), name='leave_public_group'),
	url(r'^lvpg/$', auth(leave_private_group), name='leave_private_group'),
	url(r'^leftgroup/$', auth(left_private_group), name='left_private_group'),
	################################# Mehfil administration #######################################
	url(r'^appoint/(?P<pk>\d+)/(?P<app>\d+)/$', auth(appoint_pk), name='appoint_pk'),
	url(r'^appoint/$', auth(AppointCaptainView.as_view()), name='appoint'),
	url(r'^group/owner_online_kon/$', auth(OwnerGroupOnlineKonView.as_view()), name='owner_group_online_kon'),
	url(r'^group/online_kon/$', auth(GroupOnlineKonView.as_view()), name='group_online_kon'),
	########################## Popular mehfil list #########################
	url(r'^popular_mehfil/$', auth(GroupRankingView.as_view()), name='group_ranking'),
	
)