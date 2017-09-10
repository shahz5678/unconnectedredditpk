# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from links.judgement import enter_inter_user_ban, inter_user_ban_not_permitted, first_time_inter_user_banner, banned_users_list, change_ban_time, \
user_ban_help, ban_underway, ban_leaderboard, export_ban_error

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^ban_user/$', auth(enter_inter_user_ban), name='enter_inter_user_ban'),
	url(r'^maaf_kijiye_ga/$', auth(ban_underway), name='ban_underway'),
	url(r'^banned_users_list/$', auth(banned_users_list), name='banned_users_list'),
	url(r'^change_ban_time/$', auth(change_ban_time), name='change_ban_time'),
	url(r'^not_permitted/$', auth(inter_user_ban_not_permitted), name='inter_user_ban_not_permitted'),
	url(r'^user_ban_help/$', auth(user_ban_help), name='user_ban_help'),
	url(r'^ftiub/$', auth(first_time_inter_user_banner), name='first_time_inter_user_banner'),
	url(r'^ban_leaderboard/$', auth(ban_leaderboard), name='ban_leaderboard'),
	url(r'^export_ban_error/$', auth(export_ban_error), name='export_ban_error'),
)