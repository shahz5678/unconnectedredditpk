# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.mehfil_views import public_group, public_group_request_denied, view_own_officer_app_history, process_public_group_invite, example_group_rules, \
kick_out, process_private_group_invite, public_mehfil_oversight_dashboard, public_group_officer_management, accept_open_group_rules, leave_public_group, \
first_time_public_refresh, remove_officer, group_hide_submission, cancel_open_group_invite, left_private_group, del_private_group, left_public_group, \
preview_open_group, create_open_group, invite_private, join_public_group, show_kicked_users, quick_accept_open_group_rules, process_officer_application_result, \
owner_rejoining_public_group, force_rules_onto_members, process_kicking_feedback, unkick_users, display_administrative_activity, first_time_refresh, \
public_group_invite_help, unaccepted_public_mehfil_invites, direct_message, process_open_group_feedback, show_open_group_feedback, delete_open_group_feedback, \
processing_group_ownership_transfer, private_mehfil_oversight_dashboard, join_private_group, group_ownership_transfer_tac, priv_group, display_group_info_page, \
display_detailed_info, display_group_users_list, send_request_to_owner, cancel_ownership_request, private_group_invite_help, unaccepted_private_mehfil_invites, \
cancel_closed_group_invite, leave_private_group, private_group_hide_submission, private_group_request_denied, apply_for_officer, display_officer_application, \
get_ranked_groups, del_public_group, view_officer_app_help, view_officer_application_form, view_officer_app_history, display_officer_app_detailed_info,\
group_list, group_page, DirectMessageView, GroupTypeView, ClosedGroupHelpView, PublicGroupView, ChangeGroupRulesView, ChangePrivateGroupTopicView, \
ChangeGroupTopicView, PrivateGroupView, GroupHelpView, DirectMessageCreateView, ReinvitePrivateView, ClosedGroupCreateView, InviteUsersToGroupView, \
InviteUsersToPrivateGroupView, GroupTypeView, OpenGroupHelpView, ReinviteView

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^mehfil/public/refresh/$', auth(first_time_public_refresh), name='first_time_public_refresh'),
	url(r'^mehfil/public/$', auth(PublicGroupView.as_view()), name='public_group_reply'),
	url(r'^mehfil/public/redirect/$', auth(public_group), name='public_group'),
	url(r'^mehfil/public/redirect/(?P<slug>[\w.@+-]+)/$', auth(public_group), name='public_group'),
	url(r'^mehfil/public/denied/$', auth(public_group_request_denied), name='public_group_request_denied'),
	url(r'^mehfil/private/denied/$', auth(private_group_request_denied), name='private_group_request_denied'),
	url(r'^mehfil/private/refresh/(?P<unique>[\w.@+-]+)/$', auth(first_time_refresh), name='first_time_refresh'),
	url(r'^mehfil/private/redirect/$', auth(priv_group), name='priv_group'),
	url(r'^mehfil/private/$', auth(PrivateGroupView.as_view()), name='private_group_reply'),
	################################# Mehfil deletion #############################################
	url(r'^mehfil/public/exit/$', auth(leave_public_group), name='leave_public_group'),
	url(r'^mehfil/public/delete/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/$', auth(del_public_group), name='del_public_group'),
	url(r'^mehfil/public/exited/$', auth(left_public_group), name='left_public_group'),
	url(r'^mehfil/private/delete/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/$', auth(del_private_group), name='del_private_group'),
	url(r'^mehfil/private/exit/$', auth(leave_private_group), name='leave_private_group'),
	url(r'^mehfil/private/exited/$', auth(left_private_group), name='left_private_group'),
	################################# Mehfil invites #############################################
	url(r'^mehfil/public/invited/$', auth(process_public_group_invite), name='process_public_group_invite'),
	url(r'^mehfil/public/invited/unaccepted/$', auth(unaccepted_public_mehfil_invites), name='unaccepted_public_mehfil_invites'),
	url(r'^mehfil/public/invite/$', auth(InviteUsersToGroupView.as_view()), name='invite'),
	url(r'^mehfil/public/invite/cancel/$', auth(cancel_open_group_invite), name='cancel_open_group_invite'),
	url(r'^mehfil/public/invite/help/$', auth(public_group_invite_help), name='public_group_invite_help'),
	url(r'^mehfil/public/cannot-reinvite/(?P<slug>[\w.@+-]+)/$', auth(ReinviteView.as_view()), name='reinvite_help'),
	url(r'^mehfil/private/invite/cancel/$', auth(cancel_closed_group_invite), name='cancel_closed_group_invite'),
	url(r'^mehfil/private/invited/unaccepted/$', auth(unaccepted_private_mehfil_invites), name='unaccepted_private_mehfil_invites'),
	url(r'^mehfil/private/invite/help/$', auth(private_group_invite_help), name='private_group_invite_help'),
	url(r'^mehfil/private/invited/$', auth(process_private_group_invite), name='process_private_group_invite'),
	url(r'^mehfil/private/invite/(?P<slug>[\w.@+-]+)/$', auth(invite_private), name='invite_private'),
	url(r'^mehfil/private/invite/$', auth(InviteUsersToPrivateGroupView.as_view()), name='invite_private_group'),
	url(r'^mehfil/private/cannot-reinvite/$', auth(ReinvitePrivateView.as_view()), name='reinvite_private_help'),
	################################# Mehfil listing #############################################
	url(r'^mehfil/your-list/$', auth(group_page), name='group_page'),
	url(r'^mehfil/your-mehfil-list/$', auth(group_list), name='group_list'),
	################################# Mehfil help #############################################
	url(r'^mehfil/help/$', auth(GroupHelpView.as_view()), name='group_help'),
	################################# Popular mehfils #############################################
	url(r'^mehfil/popular-list/$', auth(get_ranked_groups), name='get_ranked_groups'),
	################################# Mehfil administration #############################################
	url(r'^mehfil/public/hide/$', auth(group_hide_submission), name="group_hide_submission"),
	url(r'^mehfil/public/officer/decide/$', auth(process_officer_application_result), name='process_officer_application_result'),
	url(r'^mehfil/public/officer/remove/$', auth(remove_officer), name='remove_officer'),
	url(r'^mehfil/public/dashboard/$', auth(public_mehfil_oversight_dashboard), name='public_mehfil_oversight_dashboard'),
	url(r'^mehfil/public/officer/management/$', auth(public_group_officer_management), name='public_group_officer_management'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/activity/$', auth(display_administrative_activity), name='display_administrative_activity'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/kick/reverse/$', auth(unkick_users), name='unkick_users'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/kick/list/$', auth(show_kicked_users), name='show_kicked_users'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/kick/feedback/$', auth(process_kicking_feedback), name='process_kicking_feedback'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/kick/$', auth(kick_out), name='kick_out'),
	url(r'^mehfil/private/dashboard/$', auth(private_mehfil_oversight_dashboard), name='private_mehfil_oversight_dashboard'),
	url(r'^mehfil/private/hide/$', auth(private_group_hide_submission), name="private_group_hide_submission"),
	url(r'^mehfil/public/officer-application/apply/$', auth(apply_for_officer), name='apply_for_officer'),
	url(r'^mehfil/public/officer-application/read/$', auth(display_officer_application), name='display_officer_application'),
	url(r'^mehfil/public/officer-application/own-history/$', auth(view_own_officer_app_history), name='view_own_officer_app_history'),
	url(r'^mehfil/public/officer-application/help/$', auth(view_officer_app_help), name='view_officer_app_help'),
	url(r'^mehfil/public/officer-application/$', auth(view_officer_application_form), name='view_officer_application_form'),
	url(r'^mehfil/public/officer-application/history/$', auth(view_officer_app_history), name='view_officer_app_history'),
	url(r'^mehfil/public/officer-application/history/detail/$', auth(display_officer_app_detailed_info), name='display_officer_app_detailed_info'),
	################################# Change mehfil topic or rules #############################################
	url(r'^mehfil/public/topic/change/$', auth(ChangeGroupTopicView.as_view()), name='change_topic'),
	url(r'^mehfil/public/rules/change/$', auth(ChangeGroupRulesView.as_view()), name='change_rules'),
	url(r'^mehfil/public/rules/example/$', auth(example_group_rules), name='example_group_rules'),
	url(r'^mehfil/public/rules/accept/$', auth(accept_open_group_rules), name='accept_open_group_rules'),
	url(r'^mehfil/public/rules/reaccept/$', auth(quick_accept_open_group_rules), name='quick_accept_open_group_rules'),
	url(r'^mehfil/public/join/$', auth(join_public_group), name='join_public_group'),
	url(r'^mehfil/public/rules/enforce/$', auth(force_rules_onto_members), name='force_rules_onto_members'),
	url(r'^mehfil/public/join/owner/$', auth(owner_rejoining_public_group), name='owner_rejoining_public_group'),
	url(r'^mehfil/private/join/$', auth(join_private_group), name='join_private_group'),
	url(r'^mehfil/private/topic/change/$', auth(ChangePrivateGroupTopicView.as_view()), name='change_private_topic'),
	################################# Mehfil list of online members #############################################
	url(r'^mehfil/(?P<grp_priv>[\w.@+-]+)/current/(?P<list_type>[\w.@+-]+)/$', auth(display_group_users_list), name='display_group_users_list'),
	######################################### Mehfil info page ##################################################
	url(r'^mehfil/info/$', auth(display_group_info_page), name='display_group_info_page'),
	url(r'^mehfil/info/details/$', auth(display_detailed_info), name='display_detailed_info'),
	######################################### Mehfil creation ###################################################
	url(r'^mehfil/select-type/$', auth(GroupTypeView.as_view()), name='group_type'),
	url(r'^mehfil/public/help/$', auth(OpenGroupHelpView.as_view()), name='open_group_help'),
	url(r'^mehfil/public/preview/$', auth(preview_open_group), name='open_group_preview'),
	url(r'^mehfil/public/create/$', auth(create_open_group), name='create_open_group'),
	url(r'^mehfil/private/help/$', auth(ClosedGroupHelpView.as_view()), name='closed_group_help'),
	url(r'^mehfil/private/direct/$', auth(DirectMessageView.as_view()), name='direct_message_help'),
	url(r'^mehfil/private/(?P<pk>\d+)/$', auth(direct_message), name='direct_message'),
	url(r'^mehfil/private/create/(?P<pk>\d+)/$', auth(DirectMessageCreateView.as_view()), name='direct_message_create'),
	url(r'^mehfil/private/create/$', auth(ClosedGroupCreateView.as_view()), name='closed_group_create'),
	######################################### Mehfil feedback ###################################################
	url(r'^mehfil/public/feedback-for-owner/$', auth(process_open_group_feedback), name='process_open_group_feedback'),
	url(r'^mehfil/public/feedback/display/(?P<pk>\d+)/$', auth(show_open_group_feedback), name='show_open_group_feedback'),
	url(r'^mehfil/public/feedback/delete/$', auth(delete_open_group_feedback), name='delete_open_group_feedback'),
	######################################### Mehfil ownership transfer #########################################
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/transfer-ownership-request/cancel/$', auth(cancel_ownership_request), name='cancel_ownership_request'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/transfer-ownership-request/$', auth(send_request_to_owner), name='send_request_to_owner'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/transfer-ownership-request/process/$', auth(processing_group_ownership_transfer), name='processing_group_ownership_transfer'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/transfer-ownership-request/terms-and-conditions/$', auth(group_ownership_transfer_tac), name='group_ownership_transfer_tac'),
)