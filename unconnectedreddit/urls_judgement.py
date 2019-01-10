# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.judgement_views import report_content,cull_content, ban_content_submitter_or_voters, banned_users_list, show_blocking_history_of_defenders, \
show_your_banning_history, defender_instruction_failure, log_banning_reason_given_by_defender,add_new_defender, remove_current_defender, cull_content_loc,\
enter_inter_user_ban, inter_user_ban_not_permitted, first_time_inter_user_banner, change_ban_time, content_culling_instructions, user_ban_help, ban_underway,\
report_or_block, get_top_50_reporters, get_reporter_history, defender_history_super_admin_view, report_content_help, defender_instructions, \
voting_ban_defender_help, edit_content_submission_and_voting_ban, render_ban_details, notify_and_redirect, cull_content_post, \
spamming_definition, show_report_help, judge_content_voters, judge_content_submitters#, judge_mehfil, report_mehfil, report_mehfil_help

admin.autodiscover()

urlpatterns = patterns('',
	################################# Inter user banning #############################################
	url(r'^block/user/$', auth(enter_inter_user_ban), name='enter_inter_user_ban'),
	url(r'^block/user/in-progress/$', auth(ban_underway), name='ban_underway'),
	url(r'^blocked-users-list/$', auth(banned_users_list), name='banned_users_list'),
	url(r'^block/user/set-time/$', auth(change_ban_time), name='change_ban_time'),
	url(r'^block/user/verify-first/$', auth(inter_user_ban_not_permitted), name='inter_user_ban_not_permitted'),
	url(r'^block/user/help/$', auth(user_ban_help), name='user_ban_help'),
	url(r'^block/user/successful/$', auth(first_time_inter_user_banner), name='first_time_inter_user_banner'),
	############################ Content report or user block ########################################
	url(r'^report-or-block/$', auth(report_or_block), name='report_or_block'),
	#url(r'^report/mehfil/$', auth(report_mehfil), name='report_mehfil'),
	#url(r'^report/mehfil/help/$', auth(report_mehfil_help), name='report_mehfil_help'),
	url(r'^report/content/$', auth(report_content), name='report_content'),
	url(r'^report/content/help/$', auth(report_content_help), name='report_content_help'),
	url(r'^report/(?P<rtp>[\w.@+-]+)/(?P<ridx>\d+)/$', auth(show_report_help), name='show_report_help'),
	################################ Help page for users #############################################
	url(r'^report/what-is-spam/$', auth(spamming_definition), name='spamming_definition'),
	###################################### Defenders #################################################
	url(r'^defender/and/$', auth(add_new_defender), name='add_new_defender'),
	url(r'^defender/rcd/$', auth(remove_current_defender), name='remove_current_defender'),
	url(r'^defender/instructions/voting/$', auth(voting_ban_defender_help), name='voting_ban_defender_help'),
	url(r'^defender/instructions/failure/$', auth(defender_instruction_failure), name='defender_instruction_failure'),
	url(r'^defender/instructions/redux/$', auth(defender_instructions), name='defender_instructions'),
	url(r'^defender/instructions/submission/$', auth(content_culling_instructions), name='content_culling_instructions'),
	url(r'^defender/banning/reason/$', auth(log_banning_reason_given_by_defender), name='log_banning_reason_given_by_defender'),
	url(r'^defender/banning/history/global/$', auth(show_blocking_history_of_defenders), name='show_blocking_history_of_defenders'),
	url(r'^defender/banning/history/(?P<defender_id>\d+)/$', auth(defender_history_super_admin_view), name='defender_history_super_admin_view'),
	url(r'^defender/ybh/$', auth(show_your_banning_history), name='your_banning_history'),
	url(r'^defender/banning/$', auth(ban_content_submitter_or_voters), name='ban_content_submitter_or_voters'),
	url(r'^defender/cull-content/$', auth(cull_content), name='cull_content'),
	url(r'^defender/cull-content/data/$', auth(cull_content_post), name='cull_content_post'),
	# url(r'^defender/cull-content/single/$', auth(cull_single_content), name='cull_single_content'),
	url(r'^defender/show-expired-ban/content-submission-and-voting/$', auth(render_ban_details), name='render_ban_details'),
	url(r'^defender/edit-ban/content-submission-and-voting/$', auth(edit_content_submission_and_voting_ban), name='edit_content_submission_and_voting_ban'),
	url(r'^defender/set-ban/voting/$', auth(judge_content_voters), name='judge_content_voters'),
	url(r'^defender/set-ban/content-submission/$', auth(judge_content_submitters), name='judge_content_submitters'),
	#url(r'^defender/set-ban/mehfil/$', auth(judge_mehfil), name='judge_mehfil'),
	url(r'^defender/cull-content/loc/(?P<obj_id>\d+)/(?P<obj_type>[\w.@+-]+)/$', auth(cull_content_loc), name='cull_content_loc'),
	##################################################################################################
	url(r'^reporters/top-50/$', auth(get_top_50_reporters), name='get_top_50_reporters'),
	url(r'^reporters/history/(?P<reporter_id>\d+)/$', auth(get_reporter_history), name='get_reporter_history'),
	##################################################################################################
	url(r'^judgement/notify-and-redirect/$', auth(notify_and_redirect), name='judge_not_and_red'),
)