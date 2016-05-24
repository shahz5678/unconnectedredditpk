from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from django.views.decorators.cache import cache_page
from links.models import UserProfile
from django.views.generic.base import TemplateView
from links.views import cross_notif, vote, cross_comment_notif, photostream_vote, user_profile_photo, photo_vote, vote_on_vote, \
comment_pk, photostream_pk, upload_photo_reply_pk, see_photo_pk, reply_to_photo, private_group, direct_message, mehfil_help, \
reply_pk, reportreply_pk, kick_pk, groupreport_pk, outsider_group, public_group, appoint_pk, invite_private, link_create_pk, welcome_pk
from links.views import LinkListView, TopView, PhotoReplyView, PhotoOptionTutorialView, UserProfilePhotosView, PhotoScoreView, \
PhotoQataarHelpView, BaqiPhotosHelpView, ChainPhotoTutorialView, PhotoTimeView, PhotostreamView, UploadPhotoReplyView, PicHelpView, \
PhotoView, PhotoJawabView, CommentView, UploadPhotoView, AboutView, ChangeOutsideGroupTopicView, ReinvitePrivateView, \
ChangePrivateGroupTopicView, ContactView, PrivacyPolicyView, CaptionView, CaptionDecView, PhotosHelpView, DeviceHelpView, \
PicPasswordView, VoteOrProfileView, EmoticonsHelpView, UserSMSView, LogoutHelpView, DeletePicView, AuthPicsDisplayView, \
UserPhoneNumberView, PicExpiryView, PicsChatUploadView, VerifiedView, GroupHelpView, WelcomeView, WelcomeReplyView, WelcomeMessageView, \
NotifHelpView, MehfilView, LogoutReconfirmView, LogoutPenaltyView, GroupReportView, OwnerGroupOnlineKonView, AppointCaptainView, \
KickView, SmsReinviteView, OutsiderGroupView, SmsInviteView, OutsideMessageCreateView, OutsideMessageView, DirectMessageCreateView, \
DirectMessageView, ClosedInviteTypeView, PrivateGroupView, PublicGroupView, OpenInviteTypeView, ReinviteView, LoginWalkthroughView, \
RegisterWalkthroughView, RegisterLoginView, ChangeGroupRulesView, ClosedGroupHelpView, ChangeGroupTopicView, GroupOnlineKonView, \
GroupListView, OpenGroupHelpView, GroupTypeView, GroupPageView, ClosedGroupCreateView, OpenGroupCreateView, InviteUsersToGroupView, \
OnlineKonView, UserProfileDetailView, UserProfileEditView, LinkCreateView, LinkDetailView, LinkUpdateView, LinkDeleteView, \
ScoreHelpView, UserSettingsEditView, HelpView, UnseenActivityView, WhoseOnlineView, RegisterHelpView, VerifyHelpView, PublicreplyView, \
ReportreplyView, UserActivityView, ReportView, HistoryHelpView, InviteUsersToPrivateGroupView, BigPhotoHelpView, BestPhotoView, \
see_best_photo_pk #, UpvoteView, DownvoteView, MehfildecisionView CrossNotifView, OutsideMessageRecreateView,

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^administer_me/', include(admin.site.urls)),
	url(r'^$', LinkListView.as_view(), name='home'),
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
	url(r'^bahirniklo/$', 'django.contrib.auth.views.logout_then_login', name="bahirniklo"),
	url(r'^logout_penalty/$', LogoutPenaltyView.as_view(), name='logout_penalty'),
	url(r'^logout_reconfirm/$', LogoutReconfirmView.as_view(), name='logout_reconfirm'),
	url(r'^logout_help/$', LogoutHelpView.as_view(), name='logout_help'),
	url(r'', include('user_sessions.urls', 'user_sessions')),
	url(r'^user/(?P<slug>[\w.@+-]+)/$', UserProfilePhotosView.as_view(), name='profile'),#r'^[\w.@+-]+$'
	url(r'^user_prof/(?P<slug>[\w.@+-]+)/(?P<photo_pk>\d+)/$', user_profile_photo, name='user_profile_photo'),#r'^[\w.@+-]+$'
	url(r'^users/(?P<slug>[\w.@+-]+)/$', UserProfileDetailView.as_view(), name='user_profile'),#r'^[\w.@+-]+$'
	url(r'^vote_or_user/(?P<pk>\d+)/(?P<id>\d+)/(?P<num>\d+)/$', auth(VoteOrProfileView.as_view()), name='vote_or_profile'),#r'^[\w.@+-]+$'
	url(r'^edit_settings/$', auth(UserSettingsEditView.as_view()), name='edit_settings'),
	url(r'^edit_profile/$', auth(UserProfileEditView.as_view()), name='edit_profile'),
	url(r'^accounts/', include('registration.backends.simple.urls')),
	url(r'^closed_group/help/outside/$', auth(OutsideMessageView.as_view()), name='outside_message_help'),
	url(r'^closed_group/help/$', auth(DirectMessageView.as_view()), name='direct_message_help'),
	url(r'^dm/(?P<pk>\d+)/$', auth(direct_message), name='direct_message'),
	url(r'^mehfil/help/$', auth(MehfilView.as_view()), name='mehfil_help'),
	url(r'^mehfil_help/(?P<pk>\d+)/(?P<num>\d+)/$', auth(mehfil_help), name='mehfilhelp'),
	url(r'^closed_group/create/(?P<pk>\d+)/$', auth(DirectMessageCreateView.as_view()), name='direct_message_create'),
	url(r'^closed_group/create/outside/$', auth(OutsideMessageCreateView.as_view()), name='outside_message_create'),
	#url(r'^closed_group/recreate/outside/(?P<slug>[\w.@+-]+)/$', auth(OutsideMessageRecreateView.as_view()), name='outside_message_recreate'),
	url(r'^online_kon/$', auth(OnlineKonView.as_view()), name='online_kon'),
	url(r'^top/$', auth(TopView.as_view()), name='top'),
	url(r'^verified/$', auth(VerifiedView.as_view()), name='verified'),
	url(r'^users/(?P<slug>[\w.@+-]+)/activity/$', auth(UserActivityView.as_view()), name='user_activity'),
	url(r'^users/(?P<slug>[\w.@+-]+)/unseen/$', auth(UnseenActivityView.as_view()), name='unseen_activity'),
	url(r'^comment/$', CommentView.as_view(), name='comment'),
	url(r'^comment/(?P<from_photos>\d+)/$', CommentView.as_view(), name='comment'), #from_photos is an optional variable
	url(r'^comment_pk/(?P<pk>\d+)/$', comment_pk, name='comment_pk'),
	url(r'^comment_pk/(?P<pk>\d+)/(?P<stream_id>\d+)/$', comment_pk, name='comment_pk'), #stream is an optional variable
	url(r'^comment_pk/(?P<pk>\d+)/(?P<stream_id>\d+)/(?P<from_photos>\d+)/$', comment_pk, name='comment_pk'), #from_photos is an optional variable
	url(r'^xcomment/(?P<pk>\d+)/(?P<usr>\d+)/(?P<from_home>\d+)/$', auth(cross_comment_notif), name='cross_comment_notif'),
	url(r'^photo_jawab/$', auth(PhotoJawabView.as_view()), name='photo_jawab'),
	url(r'^photo_time/(?P<pk>\d+)/$', auth(PhotoTimeView.as_view()), name='photo_time'),
	url(r'^photo_ko_reply/$', auth(PhotoReplyView.as_view()), name='reply_options'),
	url(r'^photo_reply/(?P<pk>\d+)/(?P<ident>\d+)/$', auth(reply_to_photo), name='reply_to_photo'),
	url(r'^photo/$', PhotoView.as_view(), name='see_photo'),
	url(r'^photo/best/$', BestPhotoView.as_view(), name='see_best_photo'),
	url(r'^photostream_pk/(?P<pk>\d+)/$', photostream_pk, name='photostream_pk'),
	url(r'^photostream_pk/(?P<pk>\d+)/(?P<ident>\d+)/$', photostream_pk, name='photostream_pk'), #ident is an optional variable
	url(r'^photostream/$', PhotostreamView.as_view(), name='photostream'),
	url(r'^photo_pk/(?P<pk>\d+)/$', see_photo_pk, name='see_photo_pk'),
	url(r'^best_photo_pk/(?P<pk>\d+)/$', see_best_photo_pk, name='see_best_photo_pk'),
	url(r'^upload_photo_reply_pk/(?P<pk>\d+)/$', auth(upload_photo_reply_pk), name='upload_photo_reply_pk'),
	url(r'^upload_photo_reply/$', auth(UploadPhotoReplyView.as_view()), name='upload_photo_reply'),
	url(r'^upload_photo/$', auth(UploadPhotoView.as_view()), name='upload_photo'),
	url(r'^photos_help/(?P<slug>[\w.@+-]+)/(?P<pk>\d+)/$', PhotosHelpView.as_view(), name='photos_help'),
	url(r'^kuch/likho/$', auth(LinkCreateView.as_view()), name='link_create'),
	url(r'^link/create/$', auth(link_create_pk), name='link_create_pk'),
	url(r'^khushamdeed/$', auth(WelcomeView.as_view()), name='welcome'),
	url(r'^jawabi_photo_seekho/$', auth(ChainPhotoTutorialView.as_view()), name='chain_photo_tutorial'),
	url(r'^photo_option_seekho/$', auth(PhotoOptionTutorialView.as_view()), name='photo_option_tutorial'),
	url(r'^welcome/(?P<pk>\d+)/$', auth(welcome_pk), name='welcome_pk'),
	url(r'^izzat_ya_bezati/(?P<pk>\d+)/$', PhotoScoreView.as_view(), name='photo_izzat'),
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
	url(r'^privateinvite/(?P<slug>[\w.@+-]+)/$', auth(invite_private), name='invite_private'),
	url(r'^group/invite/(?P<slug>[\w.@+-]+)/(?P<num>[\w.@+-]+)/(?P<name>[\w.@+-]+)/$', auth(SmsInviteView.as_view()), name='sms_invite'),
	url(r'^bahir/invite/$', auth(SmsReinviteView.as_view()), name='sms_reinvite'),
	url(r'^group/open_invite_type/$', auth(OpenInviteTypeView.as_view()), name='open_invite_type'),
	url(r'^group/closed_invite_type/$', auth(ClosedInviteTypeView.as_view()), name='closed_invite_type'),
	#url(r'^link/(?P<pk>\d+)/$', LinkDetailView.as_view(), name='link_detail'),
	url(r'^score/$', auth(ScoreHelpView.as_view()), name='score_help'),
	url(r'^reinvite/(?P<slug>[\w.@+-]+)/$', auth(ReinviteView.as_view()), name='reinvite_help'),
	url(r'^reinvite/private/$', auth(ReinvitePrivateView.as_view()), name='reinvite_private_help'),
	url(r'^history/$', auth(HistoryHelpView.as_view()), name='history_help'),
	url(r'^notif_help/(?P<pk>\d+)/$', auth(NotifHelpView.as_view()), name='notif_help'),
	url(r'^cross_notif/(?P<pk>\d+)/(?P<user>\d+)/(?P<from_home>\d+)/$', cross_notif, name='x_notif'),
	url(r'^help/$', HelpView.as_view(), name='help'),
	url(r'^register_help/$', RegisterHelpView.as_view(), name='register_help'),
	url(r'^register_login/$', RegisterLoginView.as_view(), name='register_login'),
	url(r'^login_walkthrough/$', LoginWalkthroughView.as_view(), name='login_walkthrough'),
	url(r'^register_walkthrough/$', RegisterWalkthroughView.as_view(), name='register_walkthrough'),
	url(r'^verify_help/$', VerifyHelpView.as_view(), name='verify_help'),
	url(r'^group_help/$', GroupHelpView.as_view(), name='group_help'),
	url(r'^emoticons_help/$', EmoticonsHelpView.as_view(), name='emoticons_help'),
	url(r'^link/update/(?P<pk>\d+)/$', auth(LinkUpdateView.as_view()), name='link_update'),
	#url(r'^link/delete/(?P<pk>\d+)/$', auth(LinkDeleteView.as_view()), name='link_delete'),
	url(r'^pic_expiry/(?P<slug>[\w.@+-]+)/$', PicExpiryView.as_view(), name='pic_expiry'),
	url(r'^delete_pic/(?P<slug>[\w.@+-]+)/$', DeletePicView.as_view(), name='delete_pic'),
	url(r'^pic_upload/$', PicsChatUploadView.as_view(), name='pic_upload'),
	url(r'^p/(?P<code>\d+)/$', PicPasswordView.as_view(), name='pic_password'),
	#url(r'^cooldown/$', CooldownView.as_view(), name='cooldown'),
	#url(r'^user_inbox_help/$', UserInboxHelpView.as_view(), name='user_inbox_help'),
	url(r'^user_SMS/(?P<fbs>\d+)/(?P<num>[\w.@+-]+)/$', UserSMSView.as_view(), name='user_SMS'),
	url(r'^p/$', PicHelpView.as_view(), name='pic_help'),
	url(r'^privacy_policy/$', PrivacyPolicyView.as_view(), name='privacy_policy'),
	url(r'^about/$', AboutView.as_view(), name='about'),
	url(r'^contact/$', ContactView.as_view(), name='contact'),
	url(r'^caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/(?P<err>\d+)/$', CaptionView.as_view(), name='caption'),
	url(r'^bool_caption/(?P<num>\d+)/(?P<slug>[\w.@+-]+)/$', CaptionDecView.as_view(), name='captionview'),
	url(r'^user_phonenumber/(?P<slug>[\w.@+-]+)/(?P<num>\d+)/(?P<err>\d+)/(?P<id>\d+)/$', UserPhoneNumberView.as_view(), name='user_phonenumber'),
	#url(r'^send_pic_sms/(?P<slug>[\w.@+-]+)/(?P<num>\d+)/$', SendPicSMSView.as_view(), name='send_pic_sms'),
	url(r'^auth_pics_display/$', auth(AuthPicsDisplayView.as_view()), name='auth_pics_display'),
	url(r'^comments/', include('django.contrib.comments.urls')),
	url(r'^vote_on_vote/(?P<vote_id>\d+)/(?P<target_id>\d+)/(?P<link_submitter_id>\d+)/(?P<val>\d+)/$', auth(vote_on_vote), name='vote_on_vote'),
	url(r'^vote/(?P<pk>\d+)/(?P<usr>\d+)/(?P<loc>\d+)/(?P<val>\d+)/$', auth(vote), name='vote'),
	url(r'^phstote/(?P<stream>\d+)/(?P<pk>\d+)/(?P<val>\d+)/$', auth(photo_vote), name='photo_vote'),
	url(r'^phstot/(?P<pk>\d+)/(?P<val>\d+)/(?P<from_best>\d+)/$', auth(photostream_vote), name='photostream_vote'),
	url(r'^link/reply/$', auth(PublicreplyView.as_view()), name='reply'),
	url(r'^link/(?P<pk>\d+)/$', auth(reply_pk), name='reply_pk'),
	url(r'^mehfil/awami/$', auth(PublicGroupView.as_view()), name='public_group_reply'),
	url(r'^mehfilawami/(?P<slug>[\w.@+-]+)/$', auth(public_group), name='public_group'),
	url(r'^mehfil/private/$', auth(PrivateGroupView.as_view()), name='private_group_reply'),
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/$', auth(private_group), name='private_group'),
	url(r'^mehfilbahir/$', OutsiderGroupView.as_view(), name='outsider_group_reply'),####
	url(r'^mehfil/(?P<slug>[\w.@+-]+)/bahir/$', outsider_group, name='outsider_group'),
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
	url(r'^report/(?P<pk>\d+)/(?P<num>\d+)/$', auth(reportreply_pk), name='reportreply_pk'),
	url(r'^appoint/$', auth(AppointCaptainView.as_view()), name='appoint'),
	url(r'^appoint/(?P<pk>\d+)/(?P<app>\d+)/$', auth(appoint_pk), name='appoint_pk'),
	url(r'^report/$', auth(ReportView.as_view()), name="report"),
	url(r'^groupreport/$', auth(GroupReportView.as_view()), name="group_report"),
	url(r'^groupreport/(?P<slug>[\w.@+-]+)/(?P<pk>\d+)/$', auth(groupreport_pk), name="group_report_pk"),
	url(r'^kick/$', auth(KickView.as_view()), name='kick'),
	url(r'^kick/(?P<pk>\d+)/(?P<slug>[\w.@+-]+)/$', auth(kick_pk), name='kick_pk'),
	#url(r'^kick/$', auth(KickView.as_view()), name='kick'),
)