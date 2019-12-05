# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from django.views.generic.base import TemplateView
from urls_unauth import urlpatterns as urlpatterns_unauth
from urls_maint import urlpatterns as urlpatterns_maint
from urls_advertiser import urlpatterns as urlpatterns_adv
from urls_retention import urlpatterns as urlpatterns_retention
from urls_ads import urlpatterns as urlpatterns_ads
from urls_feedback import urlpatterns as urlpatterns_feedback
from urls_groups import urlpatterns as urlpatterns_groups
from urls_sharing import urlpatterns as urlpatterns_sharing
from urls_mehfil import urlpatterns as urlpatterns_mehfil
from urls_verification import urlpatterns as urlpatterns_verification
from urls_judgement import urlpatterns as urlpatterns_judgement
from urls_voting import urlpatterns as urlpatterns_voting
from urls_search import urlpatterns as urlpatterns_search
from urls_push_notif import urlpatterns as urlpatterns_push_notif
from urls_direct_response import urlpatterns as urlpatterns_direct_response
from urls_topics import urlpatterns as urlpatterns_topics
from links.installment_calculator import calculator
from links.webhooks import webhook_event
from links.views import user_profile_photo, welcome_reply, reauth, comment_pk, reply_to_photo, public_reply_view,\
link_create_pk, welcome_pk, sitemap, show_online_users,perm_redirect_to_home, logout_rules, best_home_page, \
home_page, home_redirect, best_photos_list, fresh_photos_list, see_special_photo_pk, special_photo, display_link_detail,\
submit_text_post, display_image_comments, profile_pk, faces_pages, error, share_content, sharing_help, photo_sitemap, \
hide_comment, photo_sitemap_of_sitemaps, make_ad, ad_finalize, click_ad,suspend, top_photo_help, reset_password, \
manage_user, manage_user_help, cut_user_score, kick_user, show_clones, hell_ban, kick_ban_user,photo_top_trenders,\
user_profile_photos, missing_page, hide_jawab,photo_page, photo_redirect,upload_public_photo, website_rules,\
redirect_to_profile_photos,public_photo_upload_denied, user_profile_photos_redirect
from links.redirection_views import redirect_to_content
from links.number_verification import verify_user_number
from links.views import FacesHelpView, PhotoTimeView, PhotostreamView, DeviceHelpView,AdCallPrefView, AdAddressView,\
PicHelpView, PhotoJawabView, AdImageView, AboutView, ContactView, PrivacyPolicyView, CaptionDecView, PhotosHelpView,\
PicPasswordView, EmoticonsHelpView, UserSMSView, LogoutHelpView, DeletePicView, AuthPicsDisplayView, PicExpiryView, \
PicsChatUploadView, VerifiedView, WelcomeView, WelcomeMessageView, UserPhoneNumberView, LogoutPenaltyView, SmsReinviteView,\
AdTitleView,TestAdsView, AdAddressYesNoView,SmsInviteView, UserSettingsEditView, UserProfileDetailView, UserProfileEditView,\
CaptionView, LinkDeleteView, HelpView, AdMobileNumView, RegisterHelpView, VerifyHelpView, UserActivityView, HistoryHelpView,\
AdDescriptionView, PhotoShareView, PhotoDetailView, AdGenderChoiceView, AdTitleYesNoView, AdImageYesNoView
from links.voting_views import user_vote_history
from links.announcement_views import export_survey_results, coming_soon#, survey

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^sitemap\.xml$', sitemap, name='sitemap'),
	url(r'^photo_sitemap_(?P<cohort>\d+)\.xml$', photo_sitemap, name='photo_sitemap'),
	url(r'^photo_sitemap_of_sitemaps\.xml$', photo_sitemap_of_sitemaps, name='photo_sitemap_of_sitemaps'),
	url(r'^robots\.txt/$', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
	url(r'^ad_suspend/(?P<ad_id>\d+)/$', suspend, name='suspend'),
	url(r'^test_ad/', TestAdsView.as_view(),name='test_ad'),
	url(r'^administer_me/', include(admin.site.urls)),
	url(r'^redirect/home/$', auth(home_redirect), name='redirect_to_home'),
	url(r'^redirect/home/(?P<pk>\d+)/$', auth(home_redirect), name='redirect_to_home'),
	url(r'^redirect-to-content/$', auth(redirect_to_content), name='redirect_to_content'),
	url(r'^$', auth(home_page), name='home'),
	url(r'^best_home_test/$', best_home_page, name='best_home_test'),
	url(r'^vun/$',verify_user_number, name="verify_user_number"),
	url(r'^calculator/$', auth(calculator), name='calculator'),
	url(r'^whook/$', webhook_event, name='webhook_event'),
	#########################################Logging out############################################
	url(r'^are_you_sure/$', auth(logout_rules), name="bahirniklo"),
	url(r'^logout_penalty/$', LogoutPenaltyView.as_view(), name='logout_penalty'),
	url(r'^click_ad/(?P<ad_id>\d+)/', auth(click_ad),name='click_ad'),
	################################################################################################
	url(r'^logout_help/$', LogoutHelpView.as_view(), name='logout_help'),
	url(r'', include('user_sessions.urls', 'user_sessions')),
	url(r'^user/(?P<slug>[\w.@+-]+)/$', redirect_to_profile_photos, name='profile_photos_redirect'),
	url(r'^user/likes/history/$', auth(user_vote_history), name='user_vote_history'),
	url(r'^user/(?P<slug>[\w.@+-]+)/(?P<type>[\w.@+-]+)/$', user_profile_photos, name='profile'),
	url(r'^user/redirect/(?P<slug>[\w.@+-]+)/(?P<list_type>[\w.@+-]+)/$', user_profile_photos_redirect, name='profile_photos_redirect'),
	url(r'^usrp/(?P<slug>[\w.@+-]+)/(?P<key>\d+)/$', profile_pk, name='profile_pk'),
	url(r'^user_prof/(?P<slug>[\w.@+-]+)/(?P<photo_pk>\d+)/$', user_profile_photo, name='user_profile_photo'),
	url(r'^user_prof/(?P<slug>[\w.@+-]+)/(?P<photo_pk>\d+)/(?P<is_notif>\d+)/$', user_profile_photo, name='user_profile_photo'),
	url(r'^users/(?P<slug>[\w.@+-]+)/$', UserProfileDetailView.as_view(), name='user_profile'),
	url(r'^edit_settings/$', auth(UserSettingsEditView.as_view()), name='edit_settings'),
	url(r'^edit_profile/$', auth(UserProfileEditView.as_view()), name='edit_profile'),
	url(r'^make_ad/$', make_ad, name='make_ad'),
	url(r'^ad_finalize/$', ad_finalize, name='ad_finalize'),
	url(r'^missing/$', missing_page, name='missing_page'),
	url(r'^error/$', error, name='error'),
	url(r'^ad_description/$', AdDescriptionView.as_view(), name='ad_description'),
	url(r'^ad_mobile_num/$', AdMobileNumView.as_view(), name='ad_mobile_num'),
	url(r'^ad_title/$', AdTitleView.as_view(), name='ad_title'),
	url(r'^ad_call_pref/$', AdCallPrefView.as_view(), name='ad_call_pref'),
	url(r'^ad_address/$', AdAddressView.as_view(), name='ad_address'),
	url(r'^ad_address_yesno/$', AdAddressYesNoView.as_view(), name='ad_address_yesno'),
	url(r'^ad_image_yesno/$', AdImageYesNoView.as_view(), name='ad_image_yesno'),
	url(r'^ad_gender/$', AdGenderChoiceView.as_view(), name='ad_gender'),
	url(r'^ad_image/$', AdImageView.as_view(), name='ad_image'),
	url(r'^ad_title_yesno/$', AdTitleYesNoView.as_view(), name='ad_title_yesno'),
	url(r'^online_kon/$', auth(show_online_users), name='online_kon'),
	# url(r'^top/$', auth(TopView.as_view()), name='top'),
	url(r'^verified/$', auth(VerifiedView.as_view()), name='verified'),
	url(r'^reauth/$', auth(reauth), name='reauth'),
	url(r'^users/(?P<slug>[\w.@+-]+)/activity/$', auth(UserActivityView.as_view()), name='user_activity'),
	# url(r'^unseen_help/activity/$', auth(unseen_help), name='unseen_help'),
	url(r'^comment/(?P<pk>\d+)/$', display_image_comments, name='comment'),
	url(r'^comment/(?P<pk>\d+)/(?P<origin>\d+)/$', display_image_comments, name='comment'),
	# url(r'^vidcom/$', VideoCommentView.as_view(), name='video_comment'),
	# url(r'^videocomment_pk/(?P<pk>\d+)/$', videocomment_pk, name='videocomment_pk'),
	url(r'^comment_pk/(?P<pk>\d+)/$', comment_pk, name='comment_pk'),
	url(r'^comment_pk/(?P<pk>\d+)/(?P<origin>\d+)/$', comment_pk, name='comment_pk'), #origin is an optional variable
	url(r'^comment_pk/(?P<pk>\d+)/(?P<origin>\d+)/(?P<ident>\d+)/$', comment_pk, name='comment_pk'), #origin and ident are an optional variable
	############################################################################################################################
	url(r'^photo_jawab/$', auth(PhotoJawabView.as_view()), name='photo_jawab'),
	url(r'^photo_time/(?P<pk>\d+)/$', auth(PhotoTimeView.as_view()), name='photo_time'),
	url(r'^photo_detail/(?P<pk>\d+)/$', PhotoDetailView.as_view(), name='photo_detail'),
	url(r'^photo_detail/(?P<pk>\d+)/(?P<origin>\d+)/$', PhotoDetailView.as_view(), name='photo_detail'),
	url(r'^text/detail/(?P<link_id>\d+)/$', auth(display_link_detail), name='display_link_detail'),
	# url(r'^fan/$', auth(fan), name='fan'),
	# url(r'^unfan/$', auth(unfan), name='unfan'),
	# url(r'^fanlist/(?P<pk>\d+)/$', auth(fan_list), name='fan_list'),
	# url(r'^starlist/$', auth(star_list), name='star_list'),
	url(r'^photo_reply/(?P<pk>\d+)/(?P<ident>\d+)/$', auth(reply_to_photo), name='reply_to_photo'),
	###################################################################################
	url(r'^photo/redirect/(?P<list_type>[\w.@+-]+)/(?P<pk>\d+)/$', auth(photo_redirect), name='redirect_to_photo'),
	url(r'^photo/redirect/(?P<list_type>[\w.@+-]+)/$', auth(photo_redirect), name='redirect_to_photo'),
	url(r'^photo/top-trenders/$', auth(photo_top_trenders), name='top_photo'),
	url(r'^photo/top-trenders/help/$', auth(top_photo_help), name='top_photo_help'),
	url(r'^photo/(?P<list_type>[\w.@+-]+)/$', photo_page, name='photo'),
	###################################################################################
	url(r'^topphotos/$', best_photos_list, name='best_photo'),
	url(r'^photostream/$', PhotostreamView.as_view(), name='photostream'),
	url(r'^sphk/(?P<pk>\d+)/$', see_special_photo_pk, name='see_special_photo_pk'),
	######################################################## Content Sharing ###################################################
	url(r'^share/$', auth(share_content), name='share_content'),
	url(r'^share/help/$', auth(sharing_help), name='sharing_help'),
	url(r'^share/photo/upload-denied/$', auth(public_photo_upload_denied), name='public_photo_upload_denied'),
	url(r'^share/photo/upload/$', auth(upload_public_photo), name='upload_public_photo'),
	url(r'^share/text/$', auth(submit_text_post), name='link_create'),
	url(r'^share/text/redirect/$', auth(link_create_pk), name='link_create_pk'),
	url(r'^share/text/redirect/first-time/$', auth(link_create_pk), name='first_time_link'),
	############################################################################################################################
	url(r'^photos_help/(?P<slug>[\w.@+-]+)/(?P<pk>\d+)/$', PhotosHelpView.as_view(), name='photos_help'),
	url(r'^khushamdeed/$', auth(WelcomeView.as_view()), name='welcome'),
	# url(r'^ftur/$', auth(first_time_unseen_refresh), name='first_time_unseen_refresh'),
	url(r'^welcome/(?P<pk>\d+)/$', auth(welcome_pk), name='welcome_pk'),
	url(r'^device_help/(?P<pk>\d+)/$', auth(DeviceHelpView.as_view()), name='device_help'),
	url(r'^damadam_par_khushamdeed/$', auth(welcome_reply), name='welcome_reply'),
	url(r'^khushamdeed/(?P<option>\d+)/$', auth(WelcomeMessageView.as_view()), name='welcome_message'),

	url(r'^group/invite/(?P<slug>[\w.@+-]+)/(?P<num>[\w.@+-]+)/(?P<name>[\w.@+-]+)/$', auth(SmsInviteView.as_view()), name='sms_invite'),
	url(r'^bahir/invite/$', auth(SmsReinviteView.as_view()), name='sms_reinvite'),
	url(r'^history/$', auth(HistoryHelpView.as_view()), name='history_help'),
	url(r'^help/$', HelpView.as_view(), name='help'),
	url(r'^register_login/$', perm_redirect_to_home, name='register_login'),
	url(r'^login_walkthrough/$', perm_redirect_to_home, name='login_walkthrough'),
	url(r'^reset_pass/$', auth(reset_password), name='reset_password'),
	url(r'^verify_help/$', perm_redirect_to_home, name='verify_help'),

	url(r'^emoticons_help/$', EmoticonsHelpView.as_view(), name='emoticons_help'),
	url(r'^faces/$', FacesHelpView.as_view(), name='faces'),
	url(r'^facespage/$', faces_pages, name='faces_pages'), 
	url(r'^pic_expiry/(?P<slug>[\w.@+-]+)/$', PicExpiryView.as_view(), name='pic_expiry'),
	url(r'^delete_pic/(?P<slug>[\w.@+-]+)/$', DeletePicView.as_view(), name='delete_pic'),
	url(r'^pic_upload/$', PicsChatUploadView.as_view(), name='pic_upload'),
	url(r'^p/(?P<code>\d+)/$', PicPasswordView.as_view(), name='pic_password'),
	url(r'^photo_share/(?P<pk>\d+)/(?P<loc>\d+)/$', PhotoShareView.as_view(), name='photo_share'),
	url(r'^photo_share/(?P<pk>\d+)/(?P<loc>\d+)/(?P<slug>[\w.@+-]+)/$', PhotoShareView.as_view(), name='photo_share'),
	url(r'^user_SMS/(?P<fbs>\d+)/(?P<num>[\w.@+-]+)/$', UserSMSView.as_view(), name='user_SMS'),
	url(r'^p/$', PicHelpView.as_view(), name='pic_help'),
	url(r'^privacy_policy/$', PrivacyPolicyView.as_view(), name='privacy_policy'),
	url(r'^about/$', AboutView.as_view(), name='about'),
	url(r'^website-rules/$', website_rules, name='website_rules'),
	url(r'^contact/$', ContactView.as_view(), name='contact'),
	url(r'^caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/(?P<err>\d+)/$', CaptionView.as_view(), name='caption'),
	url(r'^bool_caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/$', CaptionDecView.as_view(), name='captionview'),
	url(r'^user_phonenumber/(?P<slug>[\w.@+-]+)/(?P<num>\d+)/(?P<err>\d+)/(?P<id>\d+)/$', UserPhoneNumberView.as_view(), name='user_phonenumber'),
	url(r'^auth_pics_display/$', auth(AuthPicsDisplayView.as_view()), name='auth_pics_display'),
	##################################################Publicreply################################################
	url(r'^jawab/(?P<parent_id>\d+)/$', auth(public_reply_view), name='publicreply_view'),
	#############################################################################################################
	url(r'^reply/hide/(?P<publicreply_id>\d+)/(?P<link_id>\d+)/$', auth(hide_jawab), name='hide_jawab'),
	url(r'^comment/hide/(?P<comment_id>\d+)/(?P<photo_id>\d+)/(?P<origin>\d+)/$', auth(hide_comment), name='hide_comment'),
	#################################################################################################
	##########################################Cricket Related########################################
	url(r'^manage_user/$', auth(manage_user),name='manage_user'),
	url(r'^manage_user_help/$', auth(manage_user_help),name='manage_user_help'),
	url(r'^cut_user_score/$', auth(cut_user_score),name='cut_user_score'),
	url(r'^kick_user/$', auth(kick_user),name='kick_user'),
	url(r'^kick_ban_user/$', auth(kick_ban_user),name='kick_ban_user'),
	url(r'^show_clones/$', auth(show_clones),name='show_clones'),
	url(r'^hell_ban/$', auth(hell_ban),name='hell_ban'),
	# url(r'^survey/answers/$', auth(survey),name='survey'),
	url(r'^survey/export/$', auth(export_survey_results), name='export_survey_results'),
	url(r'^announcement/new/$', auth(coming_soon), name='coming_soon'),
	#################################################################################################
	############################# Permanent redirects ###############################################
	url(r'^freshphotos/$', auth(fresh_photos_list), name='fresh_photos_list'),
	url(r'^unauth/$',perm_redirect_to_home, name='perm_redirect_to_home'),
	url(r'^izzat_ya_bezati/(?P<pk>\d+)/(?P<origin>\d+)/$',perm_redirect_to_home, name='perm_redirect_to_home'),
	url(r'^izzat_ya_bezati/(?P<pk>\d+)/(?P<origin>\d+)/(?P<slug>[\w.@+-]+)/$',perm_redirect_to_home, name='perm_redirect_to_home'),
)

urlpatterns += urlpatterns_ads
urlpatterns += urlpatterns_adv
urlpatterns += urlpatterns_feedback
urlpatterns += urlpatterns_unauth
urlpatterns += urlpatterns_retention
urlpatterns += urlpatterns_maint
urlpatterns += urlpatterns_groups
urlpatterns += urlpatterns_sharing
urlpatterns += urlpatterns_mehfil
urlpatterns += urlpatterns_verification
urlpatterns += urlpatterns_judgement
urlpatterns += urlpatterns_voting
urlpatterns += urlpatterns_search
urlpatterns += urlpatterns_push_notif
urlpatterns += urlpatterns_direct_response
urlpatterns += urlpatterns_topics# must always be the last thing object to be concatenated

handler404 = 'links.error_views.not_found'
handler500 = 'links.error_views.server_error'
handler403 = 'links.error_views.permission_denied'
handler400 = 'links.error_views.bad_request'