from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, url
from django.contrib import admin
from links.mehfil_views import GroupHelpView, ReinviteView, OpenGroupHelpView, ClosedGroupHelpView, MehfilView, AppointCaptainView, OwnerGroupOnlineKonView,\
GroupOnlineKonView, DirectMessageCreateView, ClosedGroupCreateView, InviteUsersToPrivateGroupView, DirectMessageView, ReinvitePrivateView,\
InviteUsersToGroupView, GroupTypeView, ChangeGroupRulesView, ChangePrivateGroupTopicView, ChangeGroupTopicView, PublicGroupView, PrivateGroupView, group_list,\
appoint_pk, direct_message, leave_public_group, leave_private_group, left_private_group, mehfil_help, process_public_group_invite,\
process_private_group_invite, invite_private, public_group_request_denied, public_group, left_public_group, first_time_public_refresh,\
first_time_refresh, priv_group, del_public_group, kick_pk, groupreport_pk, get_ranked_groups, group_page, create_open_group, preview_open_group

admin.autodiscover()

urlpatterns = patterns('',
	############################################# Mehfil help #####################################
	url(r'^mehfil/help-page/$', auth(GroupHelpView.as_view()), name='group_help'),
	####################################### Mehfil invites ########################################
	url(r'^reinvite/private/$', auth(ReinvitePrivateView.as_view()), name='reinvite_private_help'),
	url(r'^reinvite/(?P<slug>[\w.@+-]+)/$', auth(ReinviteView.as_view()), name='reinvite_help'),
	url(r'^pubmef/invite/$', auth(process_public_group_invite), name='process_public_group_invite'),
	url(r'^privmef/invite/$', auth(process_private_group_invite), name='process_private_group_invite'),	

	url(r'^privateinvite/(?P<slug>[\w.@+-]+)/$', auth(invite_private), name='invite_private'),	
	url(r'^privatemehfil/invite/$', auth(InviteUsersToPrivateGroupView.as_view()), name='invite_private_group'),
	url(r'^group/invite/$', auth(InviteUsersToGroupView.as_view()), name='invite'),
	######################################### Mehfil creation #####################################
	url(r'^mehfil/select-type/$', auth(GroupTypeView.as_view()), name='group_type'),
	url(r'^mehfil/private/help/$', auth(ClosedGroupHelpView.as_view()), name='closed_group_help'),
	url(r'^mehfil/public/help/$', auth(OpenGroupHelpView.as_view()), name='open_group_help'),
	url(r'^mehfil/help/$', auth(MehfilView.as_view()), name='mehfil_help'),
	url(r'^mehfil_help/(?P<pk>\d+)/(?P<num>\d+)/$', auth(mehfil_help), name='mehfilhelp'),
	url(r'^closed_group/create/(?P<pk>\d+)/$', auth(DirectMessageCreateView.as_view()), name='direct_message_create'),
	url(r'^mehfil/private/create/$', auth(ClosedGroupCreateView.as_view()), name='closed_group_create'),
	url(r'^mehfil/public/create/$', auth(create_open_group), name='create_open_group'),
	url(r'^mehfil/public/preview/$', auth(preview_open_group), name='open_group_preview'),

	url(r'^mehfil/private/(?P<pk>\d+)/$', auth(direct_message), name='direct_message'),
	url(r'^mehfil/private/direct/$', auth(DirectMessageView.as_view()), name='direct_message_help'),
	################################# Mehfil deletion #############################################
	url(r'^mehfil/public/exit/$', auth(leave_public_group), name='leave_public_group'),
	url(r'^mehfil/private/exit/$', auth(leave_private_group), name='leave_private_group'),
	url(r'^leftgroup/$', auth(left_private_group), name='left_private_group'),
	url(r'^leftpgroup/$', auth(left_public_group), name='left_public_group'),	
	url(r'^dlpgr/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/(?P<private>\d+)/$', auth(del_public_group), name='del_public_group'),	
	################################# Mehfil administration #######################################
	url(r'^appoint/(?P<pk>\d+)/(?P<app>\d+)/$', auth(appoint_pk), name='appoint_pk'),
	url(r'^appoint/$', auth(AppointCaptainView.as_view()), name='appoint'),
	url(r'^group/owner_online_kon/$', auth(OwnerGroupOnlineKonView.as_view()), name='owner_group_online_kon'),
	url(r'^group/online_kon/$', auth(GroupOnlineKonView.as_view()), name='group_online_kon'),
	########################## Popular mehfil list #########################
	url(r'^mehfil/popular-list/$', auth(get_ranked_groups), name='get_ranked_groups'),
	#################### Rendering list of all mehfils #####################
	url(r'^mehfil/your-list/$', auth(group_page), name='group_page'),
	url(r'^mehfil/your-mehfil-list/$', auth(group_list), name='group_list'),
	############################## Changing public and private mehfil topic ##############################
	url(r'^group/change_rules/$', auth(ChangeGroupRulesView.as_view()), name='change_rules'),
	url(r'^group/change_private_topic/$', auth(ChangePrivateGroupTopicView.as_view()), name='change_private_topic'),
	url(r'^group/change_topic/$', auth(ChangeGroupTopicView.as_view()), name='change_topic'),
	############################## Rendering and posting to private mehfil ##############################
	url(r'^mehfil/private/redirect/$', auth(priv_group), name='priv_group'),
	url(r'^mehfil/private/$', auth(PrivateGroupView.as_view()), name='private_group_reply'),	
	############################## Rendering and posting to public mehfil ##############################
	url(r'^awami_mehfil_request_denied/$', auth(public_group_request_denied), name='public_group_request_denied'),
	url(r'^mehfil/awami/$', auth(PublicGroupView.as_view()), name='public_group_reply'),
	url(r'^mehfil/public/redirect/$', auth(public_group), name='public_group'),
	url(r'^mehfil/public/redirect/(?P<slug>[\w.@+-]+)/$', auth(public_group), name='public_group'),	

	#################### Refreshing mehfils #####################
	url(r'^ftpr/$', auth(first_time_public_refresh), name='first_time_public_refresh'),	
	url(r'^ftr/(?P<unique>[\w.@+-]+)/$', auth(first_time_refresh), name='first_time_refresh'),	
	############################## Mehfil punishments ##############################
	url(r'^kick/$', auth(kick_pk), name='kick_pk'),	
	url(r'^groupreport/$', auth(groupreport_pk), name="group_report_pk"),
)