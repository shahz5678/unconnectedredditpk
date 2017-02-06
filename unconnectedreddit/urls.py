from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
# from brake.decorators import ratelimit
# from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import login, logout_then_login
from links.models import UserProfile
from links.api import process_req, suspend_req, delete_req, resume_req
from django.views.generic.base import TemplateView
from links.views import cross_notif, cast_vote, cross_comment_notif, photostream_vote, user_profile_photo, photo_vote, vote_on_vote, \
comment_pk, photostream_pk, upload_photo_reply_pk, see_photo_pk, reply_to_photo, private_group, direct_message, mehfil_help, \
reply_pk, reportreply_pk, kick_pk, groupreport_pk, public_group, appoint_pk, invite_private, link_create_pk, welcome_pk, \
fan, fan_list, comment_profile_pk, comment_chat_pk, photostream_izzat, star_list, process_salat, skip_salat, skip_presalat, \
salat_tutorial_init, salat_notification, cross_salat_notif, reportcomment_pk, mehfilcomment_pk, see_special_photo_pk, special_photo, \
repnick, reprofile, rep, leave_private_group, left_private_group, unseen_reply, unseen_comment, unseen_activity, videocomment_pk, \
video_vote, profile_pk, first_time_refresh, first_time_public_refresh, leave_public_group, left_public_group, del_public_group, \
faces_pages, ban_photo_uploader, redirect_ban_or_resurrect_page, ban_photo_voter, resurrect_photo, process_private_group_invite, \
process_public_group_invite, non_fbs_vid, unseen_group, unseen_fans, unseen_help, make_ad, ad_finalize, click_ad, cross_group_notif,\
suspend, top_photo_help, home_location, reauth, create_nick, create_password, create_account, reset_password, unauth_home_link_list, \
best_photos_list, unauth_best_photos, unauth_best_photo_location_pk, best_photo_location, photo_location, see_best_photo_pk#, set_usernames
from links.views import home_link_list, TopView, PhotoReplyView, PhotoOptionTutorialView, UserProfilePhotosView, PhotoScoreView, \
PhotoQataarHelpView, BaqiPhotosHelpView, ChainPhotoTutorialView, PhotoTimeView, PhotostreamView, UploadPhotoReplyView, PicHelpView, \
PhotoView, PhotoJawabView, CommentView, UploadPhotoView, AboutView, ChangeOutsideGroupTopicView, ReinvitePrivateView, \
ChangePrivateGroupTopicView, ContactView, PrivacyPolicyView, CaptionView, CaptionDecView, PhotosHelpView, DeviceHelpView, \
PicPasswordView, EmoticonsHelpView, UserSMSView, LogoutHelpView, DeletePicView, AuthPicsDisplayView, UserPhoneNumberView, \
PicExpiryView, PicsChatUploadView, VerifiedView, GroupHelpView, WelcomeView, WelcomeReplyView, WelcomeMessageView, \
NotifHelpView, MehfilView, LogoutReconfirmView, LogoutPenaltyView, GroupReportView, OwnerGroupOnlineKonView, AppointCaptainView, \
KickView, SmsReinviteView, OpenGroupHelpView, SmsInviteView, OutsideMessageCreateView, OutsideMessageView, DirectMessageCreateView, \
DirectMessageView, ClosedInviteTypeView, PrivateGroupView, PublicGroupView, OpenInviteTypeView, ReinviteView, LoginWalkthroughView, \
RegisterLoginView, ChangeGroupRulesView, ClosedGroupHelpView, ChangeGroupTopicView, GroupOnlineKonView, GroupListView, \
GroupTypeView, GroupPageView, ClosedGroupCreateView, OpenGroupCreateView, InviteUsersToGroupView, OnlineKonView, UserProfileDetailView, \
UserProfileEditView, LinkCreateView, LinkDetailView, LinkUpdateView, LinkDeleteView, ScoreHelpView, UserSettingsEditView, HelpView, \
WhoseOnlineView, RegisterHelpView, VerifyHelpView, PublicreplyView, ReportreplyView, UserActivityView, ReportView, HistoryHelpView, \
InviteUsersToPrivateGroupView, BigPhotoHelpView, TopPhotoView, FanListView, StarListView, FanTutorialView, PhotoShareView, PhotoDetailView, \
SalatSuccessView, SalatTutorialView, SalatInviteView, InternalSalatInviteView, ExternalSalatInviteView, SalatRankingView, ReportcommentView, \
MehfilCommentView, SpecialPhotoView, SpecialPhotoTutorialView, ReportNicknameView, ReportProfileView, ReportFeedbackView, UploadVideoView, \
VideoView, VideoCommentView, VideoScoreView, FacesHelpView, VoteOrProfView, AdDescriptionView, AdTitleView, AdTitleYesNoView, AdImageYesNoView, \
AdImageView, AdGenderChoiceView, AdAddressYesNoView, AdAddressView, AdCallPrefView, AdMobileNumView, TestAdsView #LinkListView

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^ad/suspend/(?P<ad_id>\d+)/$', suspend, name='suspend'),
	url(r'^test_ad/', TestAdsView.as_view(),name='test_ad'),
	url(r'^administer_me/', include(admin.site.urls)),
	#url(r'^uname/$', set_usernames, name='get_username'),
	url(r'^redirect/$', auth(home_location), name='home_loc'),
	url(r'^$', home_link_list, name='home'),
	url(r'^unauth/', unauth_home_link_list, name='unauth_home'),
	# url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
	url(r'^login/$',login, {'template_name': 'login.html'}, name="login"),
	url(r'^bahirniklo/$', logout_then_login, name="bahirniklo"),
	url(r'^logout_penalty/$', LogoutPenaltyView.as_view(), name='logout_penalty'),
	url(r'^click_ad/(?P<ad_id>\d+)/', auth(click_ad),name='click_ad'),
	url(r'^logout_reconfirm/$', LogoutReconfirmView.as_view(), name='logout_reconfirm'),
	url(r'^logout_help/$', LogoutHelpView.as_view(), name='logout_help'),
	url(r'', include('user_sessions.urls', 'user_sessions')),
	url(r'^user/(?P<slug>[\w.@+-]+)/$', UserProfilePhotosView.as_view(), name='profile'),
	url(r'^usrp/(?P<slug>[\w.@+-]+)/(?P<key>\d+)/$', profile_pk, name='profile_pk'),
	url(r'^user_prof/(?P<slug>[\w.@+-]+)/(?P<photo_pk>\d+)/$', user_profile_photo, name='user_profile_photo'),
	url(r'^user_prof/(?P<slug>[\w.@+-]+)/(?P<photo_pk>\d+)/(?P<is_notif>\d+)/$', user_profile_photo, name='user_profile_photo'),
	url(r'^users/(?P<slug>[\w.@+-]+)/$', UserProfileDetailView.as_view(), name='user_profile'),
	url(r'^vote_or_user/(?P<pk>\d+)/(?P<id>\d+)/(?P<slug>[\w.@+-]+)/$', auth(VoteOrProfView.as_view()), name='vote_or_prof'),
	#url(r'^vote_or_user/(?P<pk>\d+)/(?P<id>\d+)/(?P<num>\d+)/$', auth(VoteOrProfileView.as_view()), name='vote_or_profile'),#r'^[\w.@+-]+$'
	url(r'^edit_settings/$', auth(UserSettingsEditView.as_view()), name='edit_settings'),
	url(r'^edit_profile/$', auth(UserProfileEditView.as_view()), name='edit_profile'),
	url(r'^unseen_fans/$', auth(unseen_fans), name='unseen_fans'),
	url(r'^api/ad/live/$', process_req, name='process_req'),
	url(r'^api/ad/suspend/$', suspend_req, name='suspend_req'),
	url(r'^api/ad/delete/$', delete_req, name='delete_req'),
	url(r'^api/ad/resume/$', resume_req, name='resume_req'),
	url(r'^make_ad/$', make_ad, name='make_ad'),
	url(r'^ad_finalize/$', ad_finalize, name='ad_finalize'),
	# url(r'^ad_location/$', AdLocationChoiceView.as_view(), name='ad_location'),
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
	url(r'^accounts/', include('registration.backends.simple.urls')),
	url(r'^closed_group/help/outside/$', auth(OutsideMessageView.as_view()), name='outside_message_help'),
	url(r'^closed_group/help/$', auth(DirectMessageView.as_view()), name='direct_message_help'),
	url(r'^dm/(?P<pk>\d+)/$', auth(direct_message), name='direct_message'),
	url(r'^mehfil/help/$', auth(MehfilView.as_view()), name='mehfil_help'),
	url(r'^mehfilcomment/help/$', auth(MehfilCommentView.as_view()), name='mehfilcomment_help'),
	#url(r'^mehcomm/(?P<pk>\d+)/(?P<num>\d+)/$', auth(mehfilcomment_pk), name='mehfilcomment_pk'),
	#url(r'^mehcomm/(?P<pk>\d+)/(?P<num>\d+)/(?P<photostream>\d+)/$', auth(mehfilcomment_pk), name='mehfilcomment_pk'),
	url(r'^mehcomm/(?P<pk>\d+)/(?P<num>\d+)/(?P<origin>\d+)/$', auth(mehfilcomment_pk), name='mehfilcomment_pk'),
	url(r'^mehcomm/(?P<pk>\d+)/(?P<num>\d+)/(?P<origin>\d+)/(?P<slug>\d+)/$', auth(mehfilcomment_pk), name='mehfilcomment_pk'),
	url(r'^salat_reminder/$', auth(SalatInviteView.as_view()), name='salat_invite'),
	url(r'^salat_notify/(?P<pk>\d+)/$', auth(salat_notification), name='salat_notification'),
	url(r'^internal_salat/$', auth(InternalSalatInviteView.as_view()), name='internal_salat_invite'),
	url(r'^external_salat/$', auth(ExternalSalatInviteView.as_view()), name='external_salat_invite'),
	url(r'^salat_success/(?P<mins>\d+)/(?P<num>\d+)/$', auth(SalatSuccessView.as_view()), name='salat_success'),
	url(r'^salat_tutorial/(?P<offered>[\w.@+-]+)/$', auth(salat_tutorial_init), name='salat_tutorial_init'),
	url(r'^process_salat/$', auth(process_salat), name='process_salat'),
	url(r'^namaz_report/$', SalatRankingView.as_view(), name='salat_ranking'),
	url(r'^salatutorial/$', auth(SalatTutorialView.as_view()), name='salat_tutorial'),
	url(r'^skip_salat/(?P<skipped>[\w.@+-]+)/$', auth(skip_salat), name='skip_salat'),
	url(r'^skip_presalat/$', auth(skip_presalat), name='skip_presalat'),
	url(r'^mehfil_help/(?P<pk>\d+)/(?P<num>\d+)/$', auth(mehfil_help), name='mehfilhelp'),
	url(r'^closed_group/create/(?P<pk>\d+)/$', auth(DirectMessageCreateView.as_view()), name='direct_message_create'),
	url(r'^closed_group/create/outside/$', auth(OutsideMessageCreateView.as_view()), name='outside_message_create'),
	#url(r'^closed_group/recreate/outside/(?P<slug>[\w.@+-]+)/$', auth(OutsideMessageRecreateView.as_view()), name='outside_message_recreate'),
	url(r'^online_kon/$', auth(OnlineKonView.as_view()), name='online_kon'),
	url(r'^top/$', auth(TopView.as_view()), name='top'),
	url(r'^best_photo_uploaders/$', auth(TopPhotoView.as_view()), name='top_photo'),
	url(r'^verified/$', auth(VerifiedView.as_view()), name='verified'),
	url(r'^reauth/$', auth(reauth), name='reauth'),
	url(r'^users/(?P<slug>[\w.@+-]+)/activity/$', auth(UserActivityView.as_view()), name='user_activity'),
	# url(r'^users/(?P<slug>[\w.@+-]+)/unseen/$', auth(UnseenActivityView.as_view()), name='unseen_activity'),
	url(r'^unseen/(?P<slug>[\w.@+-]+)/activity/$', auth(unseen_activity), name='unseen_activity'),
	url(r'^unseen_help/activity/$', auth(unseen_help), name='unseen_help'),
	url(r'^top_photo/help/$', auth(top_photo_help), name='top_photo_help'),
	url(r'^comment/$', CommentView.as_view(), name='comment'),
	url(r'^comment/(?P<origin>\d+)/$', CommentView.as_view(), name='comment'),
	url(r'^comment_chat_pk/(?P<pk>\d+)/(?P<ident>\d+)/$', comment_chat_pk, name='comment_chat_pk'),
	url(r'^vidcom/$', VideoCommentView.as_view(), name='video_comment'),
	url(r'^videocomment_pk/(?P<pk>\d+)/$', videocomment_pk, name='videocomment_pk'),
	url(r'^comment_pk/(?P<pk>\d+)/$', comment_pk, name='comment_pk'),
	url(r'^comment_pk/(?P<pk>\d+)/(?P<origin>\d+)/$', comment_pk, name='comment_pk'), #origin is an optional variable
	url(r'^comment_pk/(?P<pk>\d+)/(?P<origin>\d+)/(?P<ident>\d+)/$', comment_pk, name='comment_pk'), #origin and ident are an optional variable
	#url(r'^comment_prof_pk/(?P<pk>\d+)/(?P<user_id>\d+)/(?P<from_photos>\d+)/$', comment_profile_pk, name='comment_profile_pk'), #from_photos is an optional variable
	url(r'^xcomment/(?P<pk>\d+)/(?P<usr>\d+)/(?P<from_home>\d+)/(?P<object_type>\d+)/$', auth(cross_comment_notif), name='cross_comment_notif'),
	url(r'^xgroup/(?P<pk>\d+)/(?P<uid>\d+)/(?P<from_home>\d+)/$', auth(cross_group_notif), name='x_group_notif'),
	url(r'^photo_jawab/$', auth(PhotoJawabView.as_view()), name='photo_jawab'),
	url(r'^photo_time/(?P<pk>\d+)/$', auth(PhotoTimeView.as_view()), name='photo_time'),
	url(r'^photo_detail/(?P<pk>\d+)/$', PhotoDetailView.as_view(), name='photo_detail'),
	url(r'^fan/(?P<star_id>\d+)/(?P<obj_id>\d+)/(?P<origin>\d+)/$', auth(fan), name='fan'),
	url(r'^fanlist/(?P<pk>\d+)/$', fan_list, name='fan_list'),
	url(r'^fan_list/$', FanListView.as_view(), name='fan_list_view'),
	url(r'^starlist/(?P<pk>\d+)/$', star_list, name='star_list'),
	url(r'^star_list/$', StarListView.as_view(), name='star_list_view'),
	url(r'^photo_ko_reply/$', auth(PhotoReplyView.as_view()), name='reply_options'),
	url(r'^photo_reply/(?P<pk>\d+)/(?P<ident>\d+)/$', auth(reply_to_photo), name='reply_to_photo'),
	url(r'^photo/$', PhotoView.as_view(), name='see_photo'),
	url(r'^videos/$', VideoView.as_view(), name='see_video'),
	url(r'^eid_selfies/$', SpecialPhotoView.as_view(), name='see_special_photo'),
	url(r'^eid_tutorial/$', SpecialPhotoTutorialView.as_view(), name='special_photo_tutorial'),
	#url(r'^special/$', special_photo, name='special_photo'),
	# url(r'^fan_tutorial/$', auth(fan_tutorial), name='fan_tutorial'),
	url(r'^fan_seekho/$', auth(FanTutorialView.as_view()), name='fan_tutorial'),
	url(r'^photo/best/$', best_photos_list, name='see_best_photo'), # DEPRECATE after 10th Feb 2017
	url(r'^topphotos/$', best_photos_list, name='best_photo'),
	url(r'^tphredi/$', auth(best_photo_location), name='best_photo_loc'),
	url(r'^tphredi/(?P<pk>\d+)/$', auth(see_best_photo_pk), name='best_photo_loc_pk'),
	url(r'^phredi/$', auth(photo_location), name='photo_loc'),
	url(r'^utphredi/(?P<pk>\d+)/$', unauth_best_photo_location_pk, name='unauth_best_photo_loc_pk'),
	url(r'^seetopphotos/$', unauth_best_photos, name='unauth_best_photo'),
	url(r'^photostream_pk/(?P<pk>\d+)/$', photostream_pk, name='photostream_pk'),
	url(r'^photostream_pk/(?P<pk>\d+)/(?P<ident>\d+)/$', photostream_pk, name='photostream_pk'), #ident is an optional variable
	url(r'^photostream/$', PhotostreamView.as_view(), name='photostream'),
	url(r'^photo_pk/(?P<pk>\d+)/$', see_photo_pk, name='see_photo_pk'),
	url(r'^sphk/(?P<pk>\d+)/$', see_special_photo_pk, name='see_special_photo_pk'),
	url(r'^rep/(?P<num>\d+)/(?P<pk>\d+)/(?P<nick>[\w.@+-]+)/(?P<uuid>[\w.@+-]+)/(?P<priv>\d+)/(?P<scr>\d+)/$', auth(rep), name='rep'),
	url(r'^repback/(?P<pk>\d+)/(?P<nick>[\w.@+-]+)/(?P<uuid>[\w.@+-]+)/(?P<private>\d+)/(?P<scr>\d+)/$', auth(ReportFeedbackView.as_view()), name='report_feedback'),
	url(r'^upload_photo_reply_pk/(?P<pk>\d+)/$', auth(upload_photo_reply_pk), name='upload_photo_reply_pk'),
	url(r'^upload_photo_reply/$', auth(UploadPhotoReplyView.as_view()), name='upload_photo_reply'),
	url(r'^upload_photo/$', auth(UploadPhotoView.as_view()), name='upload_photo'),
	#url(r'^upload_photo/(?P<opt>\d+)/$', auth(UploadPhotoView.as_view()), name='upload_photo'),
	url(r'^upload_video/$', auth(UploadVideoView.as_view()), name='upload_video'),
	url(r'^photos_help/(?P<slug>[\w.@+-]+)/(?P<pk>\d+)/$', PhotosHelpView.as_view(), name='photos_help'),
	url(r'^kuch/likho/$', auth(LinkCreateView.as_view()), name='link_create'),
	url(r'^link/create/$', auth(link_create_pk), name='link_create_pk'),
	url(r'^khushamdeed/$', auth(WelcomeView.as_view()), name='welcome'),
	url(r'^jawabi_photo_seekho/$', auth(ChainPhotoTutorialView.as_view()), name='chain_photo_tutorial'),
	url(r'^photo_option_seekho/$', auth(PhotoOptionTutorialView.as_view()), name='photo_option_tutorial'),
	url(r'^ftr/(?P<unique>[\w.@+-]+)/$', auth(first_time_refresh), name='first_time_refresh'),
	url(r'^ftpr/(?P<unique>[\w.@+-]+)/$', auth(first_time_public_refresh), name='first_time_public_refresh'),
	url(r'^welcome/(?P<pk>\d+)/$', auth(welcome_pk), name='welcome_pk'),
	url(r'^izzat/(?P<pk>\d+)/$', photostream_izzat, name='photostream_izzat'),
	url(r'^izzat_ya_bezati/(?P<pk>\d+)/(?P<origin>\d+)/$', PhotoScoreView.as_view(), name='photo_izzat'),
	url(r'^izzat_ya_bezati/(?P<pk>\d+)/(?P<origin>\d+)/(?P<slug>[\w.@+-]+)/$', PhotoScoreView.as_view(), name='photo_izzat'),
	url(r'^repnick/(?P<pk>\d+)/$', auth(repnick), name='repnick'),
	url(r'^report_nickname/$', auth(ReportNicknameView.as_view()), name='report_nickname'),
	url(r'^device_help/(?P<pk>\d+)/$', auth(DeviceHelpView.as_view()), name='device_help'),
	url(r'^bari_photo_help/(?P<pk>\d+)/$', BigPhotoHelpView.as_view(), name='bari_photo_help'),
	url(r'^baqi_photos/(?P<pk>\d+)/$', BaqiPhotosHelpView.as_view(), name='baqi_photos_help'),
	url(r'^photo_qataar/(?P<pk>\d+)/$', PhotoQataarHelpView.as_view(), name='photo_qataar_help'),
	url(r'^damadam_par_khushamdeed/$', auth(WelcomeReplyView.as_view()), name='welcome_reply'),
	url(r'^khushamdeed/(?P<option>\d+)/$', auth(WelcomeMessageView.as_view()), name='welcome_message'),
	url(r'^open_group/help/$', auth(OpenGroupHelpView.as_view()), name='open_group_help'),
	url(r'^closed_mehfil/help/$', auth(ClosedGroupHelpView.as_view()), name='closed_group_help'),
	url(r'^open_group/create/$', auth(OpenGroupCreateView.as_view()), name='open_group_create'),
	url(r'^closed_group/create/$', auth(ClosedGroupCreateView.as_view()), name='closed_group_create'),
	url(r'^group/invite/$', auth(InviteUsersToGroupView.as_view()), name='invite'),
	url(r'^privatemehfil/invite/$', auth(InviteUsersToPrivateGroupView.as_view()), name='invite_private_group'),
	url(r'^privmef/invite/(?P<uuid>[\w.@+-]+)/(?P<pk>\d+)/$', auth(process_private_group_invite), name='process_private_group_invite'),
	url(r'^pubmef/invite/(?P<uuid>[\w.@+-]+)/(?P<pk>\d+)/$', auth(process_public_group_invite), name='process_public_group_invite'),
	url(r'^privateinvite/(?P<slug>[\w.@+-]+)/$', auth(invite_private), name='invite_private'),
	url(r'^group/invite/(?P<slug>[\w.@+-]+)/(?P<num>[\w.@+-]+)/(?P<name>[\w.@+-]+)/$', auth(SmsInviteView.as_view()), name='sms_invite'),
	url(r'^bahir/invite/$', auth(SmsReinviteView.as_view()), name='sms_reinvite'),
	url(r'^group/open_invite_type/$', auth(OpenInviteTypeView.as_view()), name='open_invite_type'),
	url(r'^group/closed_invite_type/$', auth(ClosedInviteTypeView.as_view()), name='closed_invite_type'),
	url(r'^score/$', auth(ScoreHelpView.as_view()), name='score_help'),
	url(r'^reinvite/(?P<slug>[\w.@+-]+)/$', auth(ReinviteView.as_view()), name='reinvite_help'),
	url(r'^reinvite/private/$', auth(ReinvitePrivateView.as_view()), name='reinvite_private_help'),
	url(r'^history/$', auth(HistoryHelpView.as_view()), name='history_help'),
	url(r'^notif_help/(?P<pk>\d+)/$', auth(NotifHelpView.as_view()), name='notif_help'),
	url(r'^cross_notif/(?P<pk>\d+)/(?P<user>\d+)/(?P<from_home>\d+)/$', auth(cross_notif), name='x_notif'),
	url(r'^cross_salat_notif/(?P<pk>[\w:@+-]+)/(?P<user>\d+)/(?P<from_home>\d+)/$', auth(cross_salat_notif), name='cross_salat_notif'),
	url(r'^help/$', HelpView.as_view(), name='help'),
	url(r'^register_help/$', RegisterHelpView.as_view(), name='register_help'),
	url(r'^register_login/$', RegisterLoginView.as_view(), name='register_login'),
	url(r'^login_walkthrough/$', LoginWalkthroughView.as_view(), name='login_walkthrough'),
	url(r'^create_acc/(?P<slug1>[\w.@+-]+)/(?P<length1>\d+)/(?P<slug2>[\w.@+-]+)/(?P<length2>\d+)/$', create_account, name='create_account'),
	url(r'^reset_pass/$', auth(reset_password), name='reset_password'),
	url(r'^create_pass/(?P<slug>[\w.@+-]+)/(?P<length>\d+)/$', create_password, name='create_password'), #[\w.?)&;[\]}:${@+-]+
	url(r'^create_nick/$', create_nick, name='create_nick'),
	url(r'^verify_help/$', VerifyHelpView.as_view(), name='verify_help'),
	url(r'^group_help/$', GroupHelpView.as_view(), name='group_help'),
	url(r'^emoticons_help/$', EmoticonsHelpView.as_view(), name='emoticons_help'),
	url(r'^faces/$', FacesHelpView.as_view(), name='faces'),
	url(r'^facespage/$', faces_pages, name='faces_pages'), 
	url(r'^resurrect_photo/(?P<pk>\d+)/(?P<ident>\d+)/(?P<dec>\d+)/(?P<uname>[\w.@+-]+)/(?P<origin>\d+)/(?P<link_id>\d+)/$', auth(resurrect_photo), name='resurrect_photo'),
	url(r'^ban_photo_voter/(?P<pk>\d+)/(?P<owner_name>[\w.@+-]+)/(?P<duration>\d+)/(?P<origin>\d+)/(?P<link_id>\d+)/$', auth(ban_photo_voter), name='ban_photo_voter'),
	url(r'^ban_photo_uploader/(?P<pk>\d+)/(?P<uname>[\w.@+-]+)/(?P<ident>\d+)/(?P<duration>\d+)/(?P<origin>\d+)/(?P<link_id>\d+)/(?P<val>\d+)/$', auth(ban_photo_uploader), name='ban_photo_uploader'),
	url(r'^redirect_ban_photo_uploader/(?P<pk>\d+)/(?P<uname>[\w.@+-]+)/(?P<ident>\d+)/(?P<origin>\d+)/(?P<link_id>\d+)/(?P<val>\d+)/$', auth(redirect_ban_or_resurrect_page), name='redirect_ban_or_resurrect_page'),
	url(r'^link/update/(?P<pk>\d+)/$', auth(LinkUpdateView.as_view()), name='link_update'),
	#url(r'^link/delete/(?P<pk>\d+)/$', auth(LinkDeleteView.as_view()), name='link_delete'),
	url(r'^pic_expiry/(?P<slug>[\w.@+-]+)/$', PicExpiryView.as_view(), name='pic_expiry'),
	url(r'^delete_pic/(?P<slug>[\w.@+-]+)/$', DeletePicView.as_view(), name='delete_pic'),
	url(r'^pic_upload/$', PicsChatUploadView.as_view(), name='pic_upload'),
	url(r'^p/(?P<code>\d+)/$', PicPasswordView.as_view(), name='pic_password'),
	#url(r'^cooldown/$', CooldownView.as_view(), name='cooldown'),
	#url(r'^user_inbox_help/$', UserInboxHelpView.as_view(), name='user_inbox_help'),
	url(r'^photo_share/(?P<pk>\d+)/(?P<loc>\d+)/$', PhotoShareView.as_view(), name='photo_share'),
	url(r'^photo_share/(?P<pk>\d+)/(?P<loc>\d+)/(?P<slug>[\w.@+-]+)/$', PhotoShareView.as_view(), name='photo_share'),
	url(r'^dlpgr/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/(?P<private>\d+)/$', auth(del_public_group), name='del_public_group'),
	url(r'^lvpgr/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/(?P<private>\d+)/(?P<inside_grp>\d+)/$', auth(leave_public_group), name='leave_public_group'),
	url(r'^leftpgroup/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/(?P<private>\d+)/$', auth(left_public_group), name='left_public_group'),
	url(r'^lvpg/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/(?P<private>\d+)/(?P<inside_grp>\d+)/$', auth(leave_private_group), name='leave_private_group'),
	url(r'^leftgroup/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/(?P<private>\d+)/$', auth(left_private_group), name='left_private_group'),
	url(r'^user_SMS/(?P<fbs>\d+)/(?P<num>[\w.@+-]+)/$', UserSMSView.as_view(), name='user_SMS'),
	url(r'^p/$', PicHelpView.as_view(), name='pic_help'),
	url(r'^privacy_policy/$', PrivacyPolicyView.as_view(), name='privacy_policy'),
	url(r'^about/$', AboutView.as_view(), name='about'),
	url(r'^contact/$', ContactView.as_view(), name='contact'),
	url(r'^nonfbs/(?P<id>\d+)/$', non_fbs_vid, name='non_fbs_vid'),
	url(r'^caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/(?P<err>\d+)/$', CaptionView.as_view(), name='caption'),
	url(r'^bool_caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/$', CaptionDecView.as_view(), name='captionview'),
	url(r'^user_phonenumber/(?P<slug>[\w.@+-]+)/(?P<num>\d+)/(?P<err>\d+)/(?P<id>\d+)/$', UserPhoneNumberView.as_view(), name='user_phonenumber'),
	#url(r'^send_pic_sms/(?P<slug>[\w.@+-]+)/(?P<num>\d+)/$', SendPicSMSView.as_view(), name='send_pic_sms'),
	url(r'^auth_pics_display/$', auth(AuthPicsDisplayView.as_view()), name='auth_pics_display'),
	url(r'^comments/', include('django.contrib.comments.urls')),
	url(r'^vote_on_vote/(?P<vote_id>\d+)/(?P<target_id>\d+)/(?P<link_submitter_id>\d+)/(?P<val>\d+)/$', auth(vote_on_vote), name='vote_on_vote'),
	# url(r'^vote/(?P<pk>\d+)/(?P<usr>\d+)/(?P<loc>\d+)/(?P<val>\d+)/$', auth(vote), name='vote'),
	url(r'^cast_vote/$', auth(cast_vote), name='cast_vote'),
	url(r'^phstote/(?P<pk>\d+)/(?P<val>\d+)/(?P<origin>\d+)/$', auth(photo_vote), name='photo_vote'),
	url(r'^phstote/(?P<pk>\d+)/(?P<val>\d+)/(?P<origin>\d+)/(?P<slug>[\w.@+-]+)/$', auth(photo_vote), name='photo_vote'),
	url(r'^phstot/(?P<pk>\d+)/(?P<val>\d+)/(?P<from_best>\d+)/$', auth(photostream_vote), name='photostream_vote'),
	url(r'^vidvote/(?P<pk>\d+)/(?P<val>\d+)/(?P<usr>\d+)/$', auth(video_vote), name='video_vote'),
	url(r'^vidizz/(?P<pk>\d+)/$', VideoScoreView.as_view(), name='video_izzat'),
	url(r'^link/reply/$', auth(PublicreplyView.as_view()), name='reply'),
	url(r'^link/(?P<pk>\d+)/$', auth(reply_pk), name='reply_pk'),
	url(r'^ungroup/(?P<pk>\d+)/$', auth(unseen_group), name='unseen_group'),
	url(r'^unlink/(?P<pk>\d+)/$', auth(unseen_reply), name='unseen_reply'),
	url(r'^unphoto/(?P<pk>\d+)/$', auth(unseen_comment), name='unseen_comment'),
	url(r'^mehfil/awami/$', auth(PublicGroupView.as_view()), name='public_group_reply'),
	url(r'^mehfilawami/(?P<slug>[\w.@+-]+)/$', auth(public_group), name='public_group'),
	url(r'^mehfil/private/$', auth(PrivateGroupView.as_view()), name='private_group_reply'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/$', auth(private_group), name='private_group'),
	# url(r'^mehfilbahir/$', OutsiderGroupView.as_view(), name='outsider_group_reply'),####
	# url(r'^mehfil/(?P<slug>[\w.@+-]+)/bahir/$', outsider_group, name='outsider_group'),
	url(r'^group/change_topic/$', auth(ChangeGroupTopicView.as_view()), name='change_topic'),
	url(r'^group/change_private_topic/$', auth(ChangePrivateGroupTopicView.as_view()), name='change_private_topic'),
	url(r'^group/change_outside_topic/$', auth(ChangeOutsideGroupTopicView.as_view()), name='change_outside_topic'),
	url(r'^group/change_rules/$', auth(ChangeGroupRulesView.as_view()), name='change_rules'),
	url(r'^group/online_kon/$', auth(GroupOnlineKonView.as_view()), name='group_online_kon'),
	url(r'^group/owner_online_kon/$', auth(OwnerGroupOnlineKonView.as_view()), name='owner_group_online_kon'),
	url(r'^group/$', auth(GroupPageView.as_view()), name='group_page'),
	url(r'^group_list/$', auth(GroupListView.as_view()), name='group_list'),
	url(r'^group_type/$', auth(GroupTypeView.as_view()), name='group_type'),
	url(r'^reportjawab/$', auth(ReportreplyView.as_view()), name='reportreply'),
	url(r'^report/$', auth(ReportView.as_view()), name="report"),
	url(r'^report/(?P<pk>\d+)/(?P<num>\d+)/$', auth(reportreply_pk), name='reportreply_pk'),
	#url(r'^repcomm/(?P<pk>\d+)/(?P<num>\d+)/$', auth(reportcomment_pk), name='reportcomment_pk'),
	url(r'^repcomm/(?P<pk>\d+)/(?P<num>\d+)/(?P<origin>\d+)/$', auth(reportcomment_pk), name='reportcomment_pk'),
	url(r'^repcomm/(?P<pk>\d+)/(?P<num>\d+)/(?P<origin>\d+)/(?P<slug>\d+)/$', auth(reportcomment_pk), name='reportcomment_pk'),
	url(r'^appoint/$', auth(AppointCaptainView.as_view()), name='appoint'),
	url(r'^appoint/(?P<pk>\d+)/(?P<app>\d+)/$', auth(appoint_pk), name='appoint_pk'),
	url(r'^report_comment/$', auth(ReportcommentView.as_view()), name="reportcomment"),
	url(r'^groupreport/$', auth(GroupReportView.as_view()), name="group_report"),
	url(r'^groupreport/(?P<slug>[\w.@+-]+)/(?P<pk>\d+)/$', auth(groupreport_pk), name="group_report_pk"),
	url(r'^kick/$', auth(KickView.as_view()), name='kick'),
	url(r'^report_profile/$', auth(ReportProfileView.as_view()), name='report_profile'),
	url(r'^kick/(?P<pk>\d+)/(?P<slug>[\w.@+-]+)/$', auth(kick_pk), name='kick_pk'),
	url(r'^reprofile/(?P<pk>\d+)/(?P<unique>[\w.@+-]+)/(?P<private>\d+)/(?P<grp>\d+)/(?P<uname>[\w.@+-]+)/$', auth(reprofile), name='reprofile'),
	#url(r'^kick/$', auth(KickView.as_view()), name='kick'),
)