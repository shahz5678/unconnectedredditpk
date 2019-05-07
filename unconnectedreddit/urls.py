# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.models import UserProfile
from links.api import process_req, suspend_req, delete_req, resume_req
from django.views.generic.base import TemplateView
from urls_unauth import urlpatterns as urlpatterns_unauth
from urls_ecomm import urlpatterns as urlpatterns_ecomm
from urls_maint import urlpatterns as urlpatterns_maint
from urls_advertiser import urlpatterns as urlpatterns_adv
#from urls_retention import urlpatterns as urlpatterns_retention
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
from links.installment_calculator import calculator
from links.webhooks import webhook_event
from links.views import home_link_list, cross_notif, cross_comment_notif, user_profile_photo, welcome_reply, fan,\
comment_pk, reply_to_photo, link_create_pk, welcome_pk, unfan, \
star_list, cross_salat_notif, best_home_page, home_page, home_redirect,\
see_special_photo_pk, special_photo, photo_location, unseen_reply, unseen_comment, unseen_activity, videocomment_pk, \
profile_pk, faces_pages, error, share_content, sharing_help, non_fbs_vid, unseen_group, unseen_fans, unseen_help, make_ad, ad_finalize, \
click_ad, cross_group_notif,suspend, top_photo_help, home_location, reauth, reset_password, fan_list, best_photos_list,\
photo_list, manage_user, manage_user_help, cut_user_score, kick_user, show_clones, hell_ban, kick_ban_user,photo_top_trenders,\
first_time_unseen_refresh, missing_page, home_reply, home_location_pk,photo_page, photo_redirect,\
upload_public_photo, website_rules, photo_comment, public_reply_view, post_public_reply,redirect_to_profile_photos,\
public_photo_upload_denied, hide_jawab, hide_comment, logout_rules, display_link_detail
#cull_single_photo, ban_photo_upload_and_voters, curate_photo,comment_chat_pk
from links.redirection_views import redirect_to_content
from links.number_verification import verify_user_number
from links.views import TopView, UserProfilePhotosView, PhotoQataarHelpView, BaqiPhotosHelpView, \
PhotoTimeView, PhotostreamView, PicHelpView, PhotoJawabView, CommentView, \
AboutView, ContactView, PrivacyPolicyView, CaptionDecView, PhotosHelpView, DeviceHelpView, PicPasswordView, EmoticonsHelpView, \
UserSMSView, LogoutHelpView, DeletePicView, AuthPicsDisplayView, PicExpiryView, PicsChatUploadView, VerifiedView, WelcomeView, \
WelcomeMessageView, UserPhoneNumberView, LogoutPenaltyView, SmsReinviteView, AdTitleView,TestAdsView, AdAddressYesNoView,\
SmsInviteView, LoginWalkthroughView, RegisterLoginView, OnlineKonView, UserSettingsEditView, UserProfileDetailView, \
UserProfileEditView, LinkCreateView, CaptionView, LinkUpdateView, LinkDeleteView, ScoreHelpView, HelpView, AdMobileNumView, \
RegisterHelpView, VerifyHelpView, UserActivityView, HistoryHelpView, AdDescriptionView, \
PhotoShareView, PhotoDetailView, \
AdGenderChoiceView, \
VideoCommentView, FacesHelpView, AdTitleYesNoView, AdImageYesNoView,AdImageView, \
AdAddressView, AdCallPrefView
from links.announcement_views import coming_soon
from links.group_views import show_shared_photo_metrics
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^ad_suspend/(?P<ad_id>\d+)/$', suspend, name='suspend'),
	url(r'^test_ad/', TestAdsView.as_view(),name='test_ad'),
	url(r'^administer_me/', include(admin.site.urls)),
	url(r'^redirect/home/$', auth(home_redirect), name='redirect_to_home'),
	url(r'^redirect/home/(?P<pk>\d+)/$', auth(home_redirect), name='redirect_to_home'),
	url(r'^redirect/(?P<pk>\d+)/$', auth(home_location_pk), name='home_loc_pk'),
	url(r'^redirect-to-content/$', auth(redirect_to_content), name='redirect_to_content'),
	url(r'^redirect/$', auth(home_location), name='home_loc'),
	url(r'^redirect/(?P<lang>[\w.@+-]+)/$', auth(home_location), name='home_loc_ur'),
	url(r'^homerep/(?P<pk>\d+)/$', auth(home_reply), name='home_reply'),
	url(r'^fotocom/(?P<pk>\d+)/$', auth(photo_comment), name='photo_comment'),
	#url(r'^$', home_link_list, name='home'),
	url(r'^$', auth(home_page), name='home'),
	url(r'^best_home_test/$', best_home_page, name='best_home_test'),
	url(r'^home/(?P<lang>[\w.@+-]+)/$', home_link_list, name='ur_home'),
	url(r'^redirect_best/$', auth(home_location), name='home_loc_best'),
	url(r'^redirect_best/(?P<lang>[\w.@+-]+)/$', auth(home_location), name='home_loc_ur_best'),
	url(r'^best/(?P<lang>[\w.@+-]+)/$', home_link_list, name='ur_home_best'),
	url(r'^best/$', home_link_list, name='home_best'),
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
	url(r'^user/(?P<nick>[\w.@+-]+)/shared-fotos/$', show_shared_photo_metrics, name='show_shared_photo_metrics'),
	url(r'^user/(?P<slug>[\w.@+-]+)/$', redirect_to_profile_photos, name='profile_photos_redirect'),
	url(r'^user/(?P<slug>[\w.@+-]+)/(?P<type>[\w.@+-]+)/$', UserProfilePhotosView.as_view(), name='profile'),
	# url(r'^user/(?P<slug>.+)/$', missing_page, name='profile'), #captures any kind of slug - for errors
	url(r'^usrp/(?P<slug>[\w.@+-]+)/(?P<key>\d+)/$', profile_pk, name='profile_pk'),
	url(r'^user_prof/(?P<slug>[\w.@+-]+)/(?P<photo_pk>\d+)/$', user_profile_photo, name='user_profile_photo'),
	url(r'^user_prof/(?P<slug>[\w.@+-]+)/(?P<photo_pk>\d+)/(?P<is_notif>\d+)/$', user_profile_photo, name='user_profile_photo'),
	url(r'^users/(?P<slug>[\w.@+-]+)/$', UserProfileDetailView.as_view(), name='user_profile'),
	url(r'^edit_settings/$', auth(UserSettingsEditView.as_view()), name='edit_settings'),
	url(r'^edit_profile/$', auth(UserProfileEditView.as_view()), name='edit_profile'),
	url(r'^unseen_fans/$', auth(unseen_fans), name='unseen_fans'),
	url(r'^api/ad/live/$', process_req, name='process_req'),
	url(r'^api/ad/suspend/$', suspend_req, name='suspend_req'),
	url(r'^api/ad/delete/$', delete_req, name='delete_req'),
	url(r'^api/ad/resume/$', resume_req, name='resume_req'),
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
	# url(r'^closed_group/help/outside/$', auth(OutsideMessageView.as_view()), name='outside_message_help'),
	# url(r'^mehfilcomment/help/$', auth(MehfilCommentView.as_view()), name='mehfilcomment_help'),
	# url(r'^mehcomm/(?P<pk>\d+)/(?P<num>\d+)/(?P<origin>\d+)/$', auth(mehfilcomment_pk), name='mehfilcomment_pk'),
	# url(r'^mehcomm/(?P<pk>\d+)/(?P<num>\d+)/(?P<origin>\d+)/(?P<slug>\d+)/$', auth(mehfilcomment_pk), name='mehfilcomment_pk'),
	# url(r'^salat_reminder/$', auth(SalatInviteView.as_view()), name='salat_invite'),
	# url(r'^salat_notify/(?P<pk>\d+)/$', auth(salat_notification), name='salat_notification'),
	# url(r'^internal_salat/$', auth(InternalSalatInviteView.as_view()), name='internal_salat_invite'),
	# url(r'^external_salat/$', auth(ExternalSalatInviteView.as_view()), name='external_salat_invite'),
	# url(r'^salat_success/(?P<mins>\d+)/(?P<num>\d+)/$', auth(SalatSuccessView.as_view()), name='salat_success'),
	# url(r'^salat_tutorial/(?P<offered>[\w.@+-]+)/$', auth(salat_tutorial_init), name='salat_tutorial_init'),
	# url(r'^process_salat/$', auth(process_salat), name='process_salat'),
	# url(r'^namaz_report/$', SalatRankingView.as_view(), name='salat_ranking'),
	# url(r'^salatutorial/$', auth(SalatTutorialView.as_view()), name='salat_tutorial'),
	# url(r'^skip_salat/(?P<skipped>[\w.@+-]+)/$', auth(skip_salat), name='skip_salat'),
	# url(r'^skip_presalat/$', auth(skip_presalat), name='skip_presalat'),
	# url(r'^closed_group/create/outside/$', auth(OutsideMessageCreateView.as_view()), name='outside_message_create'),
	#url(r'^closed_group/recreate/outside/(?P<slug>[\w.@+-]+)/$', auth(OutsideMessageRecreateView.as_view()), name='outside_message_recreate'),
	url(r'^online_kon/$', auth(OnlineKonView.as_view()), name='online_kon'),
	url(r'^top/$', auth(TopView.as_view()), name='top'),
	url(r'^verified/$', auth(VerifiedView.as_view()), name='verified'),
	url(r'^reauth/$', auth(reauth), name='reauth'),
	url(r'^users/(?P<slug>[\w.@+-]+)/activity/$', auth(UserActivityView.as_view()), name='user_activity'),
	url(r'^unseen/(?P<slug>[\w.@+-]+)/activity/$', auth(unseen_activity), name='unseen_activity'),
	url(r'^unseen_help/activity/$', auth(unseen_help), name='unseen_help'),
	url(r'^comment/(?P<pk>\d+)/$', CommentView.as_view(), name='comment'),
	url(r'^comment/(?P<pk>\d+)/(?P<origin>\d+)/$', CommentView.as_view(), name='comment'),
	# url(r'^comment_chat_pk/(?P<pk>\d+)/(?P<ident>\d+)/$', comment_chat_pk, name='comment_chat_pk'),
	url(r'^vidcom/$', VideoCommentView.as_view(), name='video_comment'),
	url(r'^videocomment_pk/(?P<pk>\d+)/$', videocomment_pk, name='videocomment_pk'),
	url(r'^comment_pk/(?P<pk>\d+)/$', comment_pk, name='comment_pk'),
	url(r'^comment_pk/(?P<pk>\d+)/(?P<origin>\d+)/$', comment_pk, name='comment_pk'), #origin is an optional variable
	url(r'^comment_pk/(?P<pk>\d+)/(?P<origin>\d+)/(?P<ident>\d+)/$', comment_pk, name='comment_pk'), #origin and ident are an optional variable
	################################################# Home Notifications #######################################################
	url(r'^xcomment/(?P<pk>\d+)/(?P<usr>\d+)/(?P<from_home>\d+)/(?P<object_type>\d+)/(?P<lang>[\w.@+-]+)/(?P<sort_by>[\w.@+-]+)/$', auth(cross_comment_notif), name='cross_comment_notif'),
	url(r'^xcomment/(?P<pk>\d+)/(?P<usr>\d+)/(?P<from_home>\d+)/(?P<object_type>\d+)/(?P<lang>[\w.@+-]+)/$', auth(cross_comment_notif), name='cross_comment_notif'),
	url(r'^xcomment/(?P<pk>\d+)/(?P<usr>\d+)/(?P<from_home>\d+)/(?P<object_type>\d+)/$', auth(cross_comment_notif), name='cross_comment_notif'),
	url(r'^xgroup/(?P<pk>\d+)/(?P<uid>\d+)/(?P<from_home>\d+)/(?P<lang>[\w.@+-]+)/(?P<sort_by>[\w.@+-]+)/$', auth(cross_group_notif), name='x_group_notif'),
	url(r'^xgroup/(?P<pk>\d+)/(?P<uid>\d+)/(?P<from_home>\d+)/(?P<lang>[\w.@+-]+)/$', auth(cross_group_notif), name='x_group_notif'),
	url(r'^xgroup/(?P<pk>\d+)/(?P<uid>\d+)/(?P<from_home>\d+)/$', auth(cross_group_notif), name='x_group_notif'),
	url(r'^cross_notif/(?P<pk>\d+)/(?P<user>\d+)/(?P<from_home>\d+)/(?P<lang>[\w.@+-]+)/(?P<sort_by>[\w.@+-]+)/$', auth(cross_notif), name='x_notif'),
	url(r'^cross_notif/(?P<pk>\d+)/(?P<user>\d+)/(?P<from_home>\d+)/(?P<lang>[\w.@+-]+)/$', auth(cross_notif), name='x_notif'),
	url(r'^cross_notif/(?P<pk>\d+)/(?P<user>\d+)/(?P<from_home>\d+)/$', auth(cross_notif), name='x_notif'),
	url(r'^cross_salat_notif/(?P<pk>[\w:@+-]+)/(?P<user>\d+)/(?P<from_home>\d+)/(?P<lang>[\w.@+-]+)/(?P<sort_by>[\w.@+-]+)/$', auth(cross_salat_notif), name='cross_salat_notif'),
	url(r'^cross_salat_notif/(?P<pk>[\w:@+-]+)/(?P<user>\d+)/(?P<from_home>\d+)/(?P<lang>[\w.@+-]+)/$', auth(cross_salat_notif), name='cross_salat_notif'),
	url(r'^cross_salat_notif/(?P<pk>[\w:@+-]+)/(?P<user>\d+)/(?P<from_home>\d+)/$', auth(cross_salat_notif), name='cross_salat_notif'),
	############################################################################################################################
	url(r'^photo_jawab/$', auth(PhotoJawabView.as_view()), name='photo_jawab'),
	url(r'^photo_time/(?P<pk>\d+)/$', auth(PhotoTimeView.as_view()), name='photo_time'),
	url(r'^photo_detail/(?P<pk>\d+)/$', PhotoDetailView.as_view(), name='photo_detail'),
	url(r'^photo_detail/(?P<pk>\d+)/(?P<origin>\d+)/$', PhotoDetailView.as_view(), name='photo_detail'),
	url(r'^text/detail/(?P<link_id>\d+)/$', auth(display_link_detail), name='display_link_detail'),
	url(r'^fan/$', auth(fan), name='fan'),
	url(r'^unfan/$', auth(unfan), name='unfan'),
	url(r'^fanlist/(?P<pk>\d+)/$', auth(fan_list), name='fan_list'),
	url(r'^starlist/$', auth(star_list), name='star_list'),
	#url(r'^photo_ko_reply/$', auth(PhotoReplyView.as_view()), name='reply_options'),
	url(r'^photo_reply/(?P<pk>\d+)/(?P<ident>\d+)/$', auth(reply_to_photo), name='reply_to_photo'),
	#url(r'^videos/$', VideoView.as_view(), name='see_video'),
	# url(r'^eid_selfies/$', SpecialPhotoView.as_view(), name='see_special_photo'),
	# url(r'^eid_tutorial/$', SpecialPhotoTutorialView.as_view(), name='special_photo_tutorial'),
	#url(r'^special/$', special_photo, name='special_photo'),
	# url(r'^fan_seekho/$', auth(FanTutorialView.as_view()), name='fan_tutorial'),
	###################################################################################
	url(r'^photo/redirect/(?P<list_type>[\w.@+-]+)/(?P<pk>\d+)/$', auth(photo_redirect), name='redirect_to_photo'),
	url(r'^photo/redirect/(?P<list_type>[\w.@+-]+)/$', auth(photo_redirect), name='redirect_to_photo'),
	url(r'^photo/top-trenders/$', auth(photo_top_trenders), name='top_photo'),
	url(r'^photo/top-trenders/help/$', auth(top_photo_help), name='top_photo_help'),
	url(r'^photo/(?P<list_type>[\w.@+-]+)/$', auth(photo_page), name='photo'),
	###################################################################################
	# url(r'^freshphotos/$', photo_list, name='photo'),
	# url(r'^topphotos/$', best_photos_list, name='best_photo'),
	url(r'^phredi/$', auth(photo_location), name='photo_loc'),
	# url(r'^photostream_pk/(?P<pk>\d+)/$', photostream_pk, name='photostream_pk'),
	# url(r'^photostream_pk/(?P<pk>\d+)/(?P<ident>\d+)/$', photostream_pk, name='photostream_pk'), #ident is an optional variable
	url(r'^photostream/$', PhotostreamView.as_view(), name='photostream'),
	url(r'^sphk/(?P<pk>\d+)/$', see_special_photo_pk, name='see_special_photo_pk'),
	#url(r'^upload_photo_reply_pk/(?P<pk>\d+)/$', auth(upload_photo_reply_pk), name='upload_photo_reply_pk'),
	#url(r'^upload_photo_reply/$', auth(UploadPhotoReplyView.as_view()), name='upload_photo_reply'),
	######################################################## Content Sharing ###################################################
	url(r'^share/$', auth(share_content), name='share_content'),
	url(r'^share/help/$', auth(sharing_help), name='sharing_help'),
	url(r'^share/photo/upload-denied/$', auth(public_photo_upload_denied), name='public_photo_upload_denied'),
	url(r'^share/photo/upload/$', auth(upload_public_photo), name='upload_public_photo'),
	url(r'^share/text/$', auth(LinkCreateView.as_view()), name='link_create'),
	url(r'^share/text/redirect/$', auth(link_create_pk), name='link_create_pk'),
	url(r'^share/text/redirect/first-time/$', auth(link_create_pk), name='first_time_link'),
	#url(r'^upload_photo/$', auth(upload_public_photo), name='upload_photo'),
	#url(r'^public_photo_upload_denied/$', auth(public_photo_upload_denied), name='public_photo_upload_denied'),
	#url(r'^upload_public_photo/$', auth(upload_public_photo), name='upload_public_photo'),
	#url(r'^kuch/likho/$', auth(LinkCreateView.as_view()), name='link_create'),
	#url(r'^link/create/$', auth(link_create_pk), name='link_create_pk'),
	#url(r'^link/first_time/$', auth(link_create_pk), name='first_time_link'),
	############################################################################################################################
	#url(r'^upload_video/$', auth(UploadVideoView.as_view()), name='upload_video'),
	url(r'^photos_help/(?P<slug>[\w.@+-]+)/(?P<pk>\d+)/$', PhotosHelpView.as_view(), name='photos_help'),
	url(r'^khushamdeed/$', auth(WelcomeView.as_view()), name='welcome'),
	#url(r'^jawabi_photo_seekho/$', auth(ChainPhotoTutorialView.as_view()), name='chain_photo_tutorial'),
	url(r'^ftur/$', auth(first_time_unseen_refresh), name='first_time_unseen_refresh'),
	url(r'^welcome/(?P<pk>\d+)/$', auth(welcome_pk), name='welcome_pk'),
	#url(r'^izzat/(?P<pk>\d+)/$', photostream_izzat, name='photostream_izzat'),
	# url(r'^izzat_ya_bezati/(?P<pk>\d+)/(?P<origin>\d+)/$', PhotoScoreView.as_view(), name='photo_izzat'),
	# url(r'^izzat_ya_bezati/(?P<pk>\d+)/(?P<origin>\d+)/(?P<slug>[\w.@+-]+)/$', PhotoScoreView.as_view(), name='photo_izzat'),
	# url(r'^repnick/(?P<pk>\d+)/$', auth(repnick), name='repnick'),
	# url(r'^report_nickname/$', auth(ReportNicknameView.as_view()), name='report_nickname'),
	url(r'^device_help/(?P<pk>\d+)/$', auth(DeviceHelpView.as_view()), name='device_help'),
	url(r'^baqi_photos/(?P<pk>\d+)/$', BaqiPhotosHelpView.as_view(), name='baqi_photos_help'),
	url(r'^photo_qataar/(?P<pk>\d+)/$', PhotoQataarHelpView.as_view(), name='photo_qataar_help'),
	url(r'^damadam_par_khushamdeed/$', auth(welcome_reply), name='welcome_reply'),
	url(r'^khushamdeed/(?P<option>\d+)/$', auth(WelcomeMessageView.as_view()), name='welcome_message'),

	url(r'^group/invite/(?P<slug>[\w.@+-]+)/(?P<num>[\w.@+-]+)/(?P<name>[\w.@+-]+)/$', auth(SmsInviteView.as_view()), name='sms_invite'),
	url(r'^bahir/invite/$', auth(SmsReinviteView.as_view()), name='sms_reinvite'),
	url(r'^score/$', auth(ScoreHelpView.as_view()), name='score_help'),
	url(r'^history/$', auth(HistoryHelpView.as_view()), name='history_help'),
	url(r'^help/$', HelpView.as_view(), name='help'),
	# url(r'^register_help/$', RegisterHelpView.as_view(), name='register_help'),
	url(r'^register_login/$', RegisterLoginView.as_view(), name='register_login'),
	url(r'^login_walkthrough/$', LoginWalkthroughView.as_view(), name='login_walkthrough'),
	url(r'^reset_pass/$', auth(reset_password), name='reset_password'),
	url(r'^verify_help/$', VerifyHelpView.as_view(), name='verify_help'),

	url(r'^emoticons_help/$', EmoticonsHelpView.as_view(), name='emoticons_help'),
	url(r'^faces/$', FacesHelpView.as_view(), name='faces'),
	url(r'^facespage/$', faces_pages, name='faces_pages'), 
	url(r'^link/update/(?P<pk>\d+)/$', auth(LinkUpdateView.as_view()), name='link_update'),
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
	url(r'^nonfbs/(?P<id>\d+)/$', non_fbs_vid, name='non_fbs_vid'),
	url(r'^caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/(?P<err>\d+)/$', CaptionView.as_view(), name='caption'),
	url(r'^bool_caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/$', CaptionDecView.as_view(), name='captionview'),
	url(r'^user_phonenumber/(?P<slug>[\w.@+-]+)/(?P<num>\d+)/(?P<err>\d+)/(?P<id>\d+)/$', UserPhoneNumberView.as_view(), name='user_phonenumber'),
	url(r'^auth_pics_display/$', auth(AuthPicsDisplayView.as_view()), name='auth_pics_display'),
	url(r'^comments/', include('django.contrib.comments.urls')),
	#url(r'^vidvote/(?P<pk>\d+)/(?P<val>\d+)/(?P<usr>\d+)/$', auth(video_vote), name='video_vote'),
	#url(r'^vidizz/(?P<pk>\d+)/$', VideoScoreView.as_view(), name='video_izzat'),
	##################################################Publicreply################################################
	url(r'^jawab/$', auth(public_reply_view), name='publicreply_view'),
	url(r'^jawab/sent/$', auth(post_public_reply), name='publicreply_post'),
	url(r'^unlink/(?P<pk>\d+)/$', auth(unseen_reply), name='unseen_reply'),
	#############################################################################################################
	url(r'^ungroup/(?P<pk>\d+)/$', auth(unseen_group), name='unseen_group'),
	url(r'^unphoto/(?P<pk>\d+)/$', auth(unseen_comment), name='unseen_comment'),
	url(r'^reply/hide/(?P<publicreply_id>\d+)/(?P<link_id>\d+)/$', auth(hide_jawab), name='hide_jawab'),
	url(r'^comment/hide/(?P<comment_id>\d+)/(?P<photo_id>\d+)/(?P<origin>\d+)/$', auth(hide_comment), name='hide_comment'),
	# url(r'^groupreport/$', auth(GroupReportView.as_view()), name="group_report"),
	# url(r'^kick/$', auth(KickView.as_view()), name='kick'),
	# url(r'^tfrs/$', auth(test_functional_redis_server), name='test_functional_redis_server'),
	##########################################Photo Reporting########################################
	#url(r'^curate_photo/$', auth(curate_photo), name='curate_photo'),
	#url(r'^cull_photo/$', auth(cull_photo), name='cull_photo'),
	
	#################################################################################################
	##########################################Cricket Related########################################
	# url(r'^cricket_dashboard/$',auth(cricket_dashboard),name='cricket_dashboard'),
	# url(r'^cricket_remove/$',auth(cricket_remove),name='cricket_remove'),
	# url(r'^cricket_initiate/$', auth(cricket_initiate),name='cricket_initiate'),
	# url(r'^cricomm/$', auth(cricket_comment),name='cricket_comment'),
	# url(r'^cricket_page/$', auth(cricket_comment_page),name='cricket_comment_page'),
	# url(r'^redirectcric/$', auth(cricket_location), name='cric_loc'),
	# url(r'^ftcr/$', auth(first_time_cricket_refresh), name='first_time_cricket_refresh'),
	# url(r'^cricrep/(?P<pk>\d+)/$', auth(cricket_reply), name='cricket_reply'),
	url(r'^manage_user/$', auth(manage_user),name='manage_user'),
	url(r'^manage_user_help/$', auth(manage_user_help),name='manage_user_help'),
	url(r'^cut_user_score/$', auth(cut_user_score),name='cut_user_score'),
	url(r'^kick_user/$', auth(kick_user),name='kick_user'),
	url(r'^kick_ban_user/$', auth(kick_ban_user),name='kick_ban_user'),
	url(r'^show_clones/$', auth(show_clones),name='show_clones'),
	url(r'^hell_ban/$', auth(hell_ban),name='hell_ban'),
	url(r'^coming-soon/stay-tuned/$', auth(coming_soon), name='coming_soon'),
	#url(r'^maintainance_notice/stay-tuned/$', auth(maintainance_notice), name='maintainance_notice'),
	#################################################################################################
)
urlpatterns += urlpatterns_ecomm
urlpatterns += urlpatterns_ads
urlpatterns += urlpatterns_adv
urlpatterns += urlpatterns_feedback
urlpatterns += urlpatterns_unauth
#urlpatterns += urlpatterns_retention
urlpatterns += urlpatterns_maint
urlpatterns += urlpatterns_groups
urlpatterns += urlpatterns_sharing
urlpatterns += urlpatterns_mehfil
urlpatterns += urlpatterns_verification
urlpatterns += urlpatterns_judgement
urlpatterns += urlpatterns_voting
urlpatterns += urlpatterns_search
urlpatterns += urlpatterns_push_notif

handler404 = 'links.error_views.not_found'
handler500 = 'links.error_views.server_error'
handler403 = 'links.error_views.permission_denied'
handler400 = 'links.error_views.bad_request'