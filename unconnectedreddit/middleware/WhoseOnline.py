import random, time
from django.core.urlresolvers import resolve
from links.tasks import save_online_user, set_user_age#, set_section_retention

class WhoseOnlineMiddleware(object):

	def process_request(self, request):
		ran_num = random.random()
		####################################################################################
		if ran_num < 0.08 and request.user.is_authenticated():
			# between 0% - 8%
			# set "online" list of users
			save_online_user.delay(user_id=request.session['_auth_user_id'], user_ip=request.META.get('X-IORG-FBS-UIP',request.META.get('REMOTE_ADDR')))
		####################################################################################
		elif ran_num > 0.92 and request.user.is_authenticated():
			# between 92% - 100%
			# set user world age
			set_user_age.delay(user_id=request.session['_auth_user_id'])
		####################################################################################
		
		# PRIVATE AND PUBLIC MEHFIL URL NAMES HAVE BEEN CHANGED - PLEASE UPDATE THEM BELOW

		# elif True:#(0.84 < ran_num <= 0.92) and request.user.is_authenticated():
		# 	# between 92% - 84%, calculate retention for private mehfils
			
		# 	PRIVATE_MEHFIL_URLS = {'reinvite_private_help':True,'process_private_group_invite':True,'invite_private':True,\
		# 	'invite_private_group':True,'closed_group_help':True,'mehfil_help':True,'mehfilhelp':True,'direct_message_create':True,\
		# 	'closed_group_create':True,'direct_message':True,'direct_message_help':True,'leave_private_group':True,'priv_group':True,\
		# 	'left_private_group':True,'change_private_topic':True,'private_group_reply':True,'first_time_refresh':True}
			
		# 	if resolve(request.path_info).url_name in PRIVATE_MEHFIL_URLS:
		# 		set_section_retention.delay(which_section='private_mehfil',user_id=request.session['_auth_user_id'])
		# ####################################################################################
		# elif (0.78 < ran_num <= 0.84) and request.user.is_authenticated():
		# 	# between 84% - 78%, calculate retention for public mehfils
			
		# 	PUBLIC_MEHFIL_URLS = {'reinvite_help':True,'process_public_group_invite':True,'invite':True,'open_group_help':True,\
		# 	'open_group_create':True,'leave_public_group':True,'left_public_group':True,'del_public_group':True,'appoint_pk':True,\
		# 	'appoint':True,'owner_group_online_kon':True,'group_online_kon':True,'group_ranking':True,'change_rules':True,\
		# 	'change_topic':True,'public_group_request_denied':True,'public_group_reply':True,'public_group':True,'kick_pk':True,\
		# 	'first_time_public_refresh':True,'group_report_pk':True}

		# 	if resolve(request.path_info).url_name in PUBLIC_MEHFIL_URLS:
		# 		set_section_retention.delay(which_section='public_mehfil',user_id=request.session['_auth_user_id'])
		# # URLS excluded from public/private: 'group_help', 'group_type', 'group_page'
		# ####################################################################################
		# elif (0.7 < ran_num <= 0.78) and request.user.is_authenticated():
		# 	# between 78% - 70%, calculate retention for private chat

		# 	PRIVATE_CHAT_URLS = {'enter_personal_group':True,'post_to_personal_group':True,'post_js_reply_to_personal_group':True,\
		# 	'personal_group_their_chat_buttons':True,'show_all_saved_posts_in_personal_group':True,'save_post_in_personal_group':True,\
		# 	'delete_post_from_personal_group':True,'hide_photo_from_personal_group_chat':True,'post_chat_action_in_personal_group':True,\
		# 	'personal_group_own_chat_buttons':True,'personal_group_grant_chat_saving_perm':True,'personal_group_delete_saved_post':True,\
		# 	'retrieve_personal_group_saved_content':True,'personal_group_exit_settings':True,'delete_or_hide_photo_from_photo_settings':True,\
		# 	'delete_all_posts_from_personal_group':True,'personal_group_reentry':True,'personal_group_photo_settings':True,'photo_shared':True,\
		# 	'personal_group_sms_settings':True,'personal_group_send_sms':True,'personal_group_sms_text_form':True,'x_per_grp_notif':True,\
		# 	'set_personal_group_photo_sharing_perm_from_chat':True,'anonymize_user_in_personal_group':True,'send_personal_group_invite':True,\
		# 	'verify_personal_group_user':True,'personal_group_receive_sms':True,'personal_group_sms_text':True,'unseen_per_grp':True,\
		# 	'personal_group_customize_sms_text':True,'personal_group_receive_sms_from_chat':True,'render_personal_group_invite':True,\
		# 	'accept_personal_group_invite':True,'process_personal_group_invite':True,'change_personal_group_invite_privacy':True,\
		# 	'show_personal_group_invite_list':True,'personal_group_user_listing':True,'share_photo_in_personal_group':True,\
		# 	'cant_share_photo':True,'personal_group_help1':True,'personal_group_help2':True,'personal_group_help3':True,\
		# 	'personal_group_help4':True}

		# 	if resolve(request.path_info).url_name in PRIVATE_CHAT_URLS:
		# 		set_section_retention.delay(which_section='private_chat',user_id=request.session['_auth_user_id'])
		# 	# URLS excluded from private chat: 'private_chat_help_ad', 'personal_group_metrics','show_shared_photo_metrics'