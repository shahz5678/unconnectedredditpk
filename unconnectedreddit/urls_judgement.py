# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.judgement_views import ban_underway, banned_users_list, first_time_inter_user_banner, inter_user_ban_not_permitted,\
enter_inter_user_ban, user_ban_help, change_ban_time, report_or_block, report_content

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
    url(r'^report/content/$', auth(report_content), name='report_content'),
)