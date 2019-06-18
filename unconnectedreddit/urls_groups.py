from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required as auth    
from links.group_views import render_personal_group_invite, change_personal_group_invite_privacy, show_personal_group_invite_list, \
process_personal_group_invite, personal_group_sms_text, post_to_personal_group, personal_group_sms_settings, personal_group_own_chat_buttons, \
delete_post_from_personal_group, post_chat_action_in_personal_group, delete_all_posts_from_personal_group, save_post_in_personal_group,\
anonymize_user_in_personal_group, accept_personal_group_invite, send_personal_group_invite, personal_group_grant_chat_saving_perm, \
set_personal_group_photo_sharing_perm_from_chat, delete_or_hide_photo_from_photo_settings, hide_photo_from_personal_group_chat, private_chat_help_ad,\
personal_group_receive_sms, personal_group_customize_sms_text, personal_group_receive_sms_from_chat, enter_personal_group,personal_group_help1,\
personal_group_send_sms, personal_group_sms_text_form, personal_group_exit_settings, personal_group_their_chat_buttons, personal_group_reentry,\
show_all_saved_posts_in_personal_group, retrieve_personal_group_saved_content,personal_group_delete_saved_post, personal_group_photo_settings,\
post_js_reply_to_personal_group, personal_group_user_listing, unseen_per_grp, x_per_grp_notif, export_chat_logs, share_photo_in_personal_group,\
photo_shared, cant_share_photo, personal_group_help2, personal_group_help3, personal_group_help4, enter_personal_group_from_single_notif#, deletion_test
from links.number_verification import verify_personal_group_user
from links.views import redirect_to_1on1_list

admin.autodiscover()

urlpatterns = patterns('',
	# url(r'^deletion_test/$', auth(deletion_test), name='deletion_test'),
	############################## Personal Groups ###############################
	url(r'^1-on-1/$', auth(enter_personal_group), name='enter_personal_group'),
	url(r'^1-on-1/post/$', auth(post_to_personal_group), name='post_to_personal_group'),
	url(r'^1-on-1/post/js/$', auth(post_js_reply_to_personal_group), name='post_js_reply_to_personal_group'),
	url(r'^1-on-1/their-buttons/$', auth(personal_group_their_chat_buttons), name='personal_group_their_chat_buttons'),
	url(r'^1-on-1/list/saved-posts/$', auth(show_all_saved_posts_in_personal_group), name='show_all_saved_posts_in_personal_group'),
	url(r'^1-on-1/post/save/$', auth(save_post_in_personal_group), name='save_post_in_personal_group'),
	url(r'^1-on-1/post/delete/$', auth(delete_post_from_personal_group), name='delete_post_from_personal_group'),
	url(r'^1-on-1/photo/hide/$', auth(hide_photo_from_personal_group_chat), name='hide_photo_from_personal_group_chat'),
	url(r'^1-on-1/action/$', auth(post_chat_action_in_personal_group), name='post_chat_action_in_personal_group'),
	url(r'^1-on-1/my-buttons/$', auth(personal_group_own_chat_buttons), name='personal_group_own_chat_buttons'),
	url(r'^1-on-1/from-single-notif/$', auth(enter_personal_group_from_single_notif), name='enter_personal_group_from_single_notif'),
	########################## Personal Group Settings ###########################
	url(r'^1-on-1/post/save-permission/$', auth(personal_group_grant_chat_saving_perm), name='personal_group_grant_chat_saving_perm'),
	url(r'^1-on-1/post/delete-saved-entry/$', auth(personal_group_delete_saved_post), name='personal_group_delete_saved_post'),
	url(r'^1-on-1/list/saved-posts/retrieve/$', auth(retrieve_personal_group_saved_content), name='retrieve_personal_group_saved_content'),
	url(r'^1-on-1/exit/$', auth(personal_group_exit_settings), name='personal_group_exit_settings'),
	url(r'^1-on-1/re-enter/$', auth(personal_group_reentry), name='personal_group_reentry'),
	url(r'^1-on-1/delete/all-posts/$', auth(delete_all_posts_from_personal_group), name='delete_all_posts_from_personal_group'),
	url(r'^1-on-1/delete/photo/$', auth(delete_or_hide_photo_from_photo_settings), name='delete_or_hide_photo_from_photo_settings'),
	url(r'^1-on-1/photo/settings/$', auth(personal_group_photo_settings), name='personal_group_photo_settings'),
	url(r'^1-on-1/sms/settings/$', auth(personal_group_sms_settings), name='personal_group_sms_settings'),
	url(r'^1-on-1/sms/send/$',personal_group_send_sms, name="personal_group_send_sms"),
	url(r'^1-on-1/sms/text-form/$',personal_group_sms_text_form, name="personal_group_sms_text_form"),
	url(r'^1-on-1/photo/share-permission/$', auth(set_personal_group_photo_sharing_perm_from_chat), name='set_personal_group_photo_sharing_perm_from_chat'),
	url(r'^1-on-1/anonymize/$', auth(anonymize_user_in_personal_group), name='anonymize_user_in_personal_group'),
	########################### Verify Mobile Number #############################
	url(r'^1-on-1/verify-user/$',verify_personal_group_user, name="verify_personal_group_user"),
	url(r'^1-on-1/sms/receive/$',personal_group_receive_sms, name="personal_group_receive_sms"),
	url(r'^1-on-1/sms/text/$',personal_group_sms_text, name="personal_group_sms_text"),
	url(r'^1-on-1/sms/custom-text/$',personal_group_customize_sms_text, name="personal_group_customize_sms_text"),
	url(r'^1-on-1/sms/receive-from-chat/$',personal_group_receive_sms_from_chat, name="personal_group_receive_sms_from_chat"),
	########################### Personal Group Invites ###########################
	url(r'^1-on-1/invite/$', auth(render_personal_group_invite), name='render_personal_group_invite'),
	url(r'^1-on-1/invite/send/$', auth(send_personal_group_invite), name='send_personal_group_invite'),
	url(r'^1-on-1/invite/accept/$', auth(accept_personal_group_invite), name='accept_personal_group_invite'),
	url(r'^1-on-1/invite/process/$', auth(process_personal_group_invite), name='process_personal_group_invite'),
	url(r'^1-on-1/invite/privacy/$', auth(change_personal_group_invite_privacy), name='change_personal_group_invite_privacy'),
	############################## Personal Group Listing ###############################
	url(r'^1-on-1/invite/list/(?P<list_type>[\w.@+-]+)/$', auth(show_personal_group_invite_list), name='show_personal_group_invite_list'),
	url(r'^1-on-1/friends/$', auth(personal_group_user_listing), name='personal_group_user_listing'),
	############################## Personal Group Notifications ###############################
	url(r'^unpergrp/(?P<gid>\d+)/(?P<fid>\d+)/$', auth(unseen_per_grp), name='unseen_per_grp'),
	url(r'^xpergrp/(?P<gid>\d+)/(?P<fid>\d+)/(?P<from_home>\d+)/$', auth(x_per_grp_notif), name='x_per_grp_notif'),
	################################# Personal Group Help Ad ##################################
	url(r'^private_chat_ad/$', auth(private_chat_help_ad), name='private_chat_help_ad'),
	############################ Export chat logs #############################
	url(r'^1-on-1/export/chat/(?P<log_type>[\w.@+-]+)/$', auth(export_chat_logs), name='export_chat_logs'),
	############################ Personal Group Photo Sharing #############################
	url(r'^1-on-1/share/photo/$', auth(share_photo_in_personal_group), name='share_photo_in_personal_group'),
	url(r'^1-on-1/share/cant-share-photo/$', auth(cant_share_photo), name='cant_share_photo'),
	url(r'^1-on-1/share/cant-share-photo/(?P<ttl>\d+)/$', auth(cant_share_photo), name='cant_share_photo'),
	url(r'^1-on-1/share/photo/success/$', auth(photo_shared), name='photo_shared'),
	################################ Personal Group Help Pages #################################
	url(r'^1-on-1/help_page/1/$', auth(personal_group_help1), name='personal_group_help1'),
	url(r'^1-on-1/help_page/2/$', auth(personal_group_help2), name='personal_group_help2'),
	url(r'^1-on-1/help_page/3/$', auth(personal_group_help3), name='personal_group_help3'),
	url(r'^1-on-1/help_page/4/$', auth(personal_group_help4), name='personal_group_help4'),
	################################ Permanent redirects #################################
	url(r'^priv_chat_list/$', auth(redirect_to_1on1_list), name='redirect_to_1on1_list'),
)