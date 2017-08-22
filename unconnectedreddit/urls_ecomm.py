from links.ecomm import x2lite_details, x32_details, buyer_loc, process_city, post_basic_item, post_seller_info, post_basic_item_photos, \
init_classified, approve_classified, edit_classified, process_ad_approval, change_cover_photo, show_user_ads, ad_detail, process_unfinished_ad, \
ad_locked_by_agent, show_seller_number, classified_tutorial_dec, city_list, expire_my_ad, change_my_sms_settings, classified_listing, \
process_ad_expiry_or_sms_feedback, populate_photo_ads#, get_spam_export
from links.ecomm_tracking import display_latest_metrics, get_ad_export, get_click_distribution
from links.number_verification import verify_basic_item_seller_number, verify_consumer_number
from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^buy_and_sell/cities/$', city_list,name='city_list'),
	url(r'^buy_and_sell/$', classified_listing,name='classified_listing'),
	url(r'^buy_and_sell/exchange/$', classified_listing,name='exchange_classified_listing'),
	url(r'^buy_and_sell/exchange/(?P<city>[\w.@+-]+)/$', classified_listing,name='city_exchange_classified_listing'),
	url(r'^buy_and_sell/fotos/$', classified_listing,name='classified_listing_with_photos'),
	url(r'^buy_and_sell/fotos/(?P<city>[\w.@+-]+)/$', classified_listing,name='city_classified_listing_with_photos'),
	url(r'^buy_and_sell/(?P<city>[\w.@+-]+)/$', classified_listing,name='city_classified_listing'),
	url(r'^ad/(?P<ad_id>\d+)/$', ad_detail,name='ad_detail'),
	#################################################################################################
	url(r'^process_ad_approval/$', auth(process_ad_approval),name='process_ad_approval'),
	url(r'^edit_classified/$', auth(edit_classified),name='edit_classified'),
	url(r'^lock_ad/$', auth(ad_locked_by_agent),name='ad_locked_by_agent'),
	url(r'^change_cover_photo/$', auth(change_cover_photo),name='change_cover_photo'),
	url(r'^classified_approval_dashboard/(?P<only_locked>\d+)/$', auth(approve_classified),name='approve_classified'),
	#################################################################################################
	url(r'^process_unfinished_ad/$', auth(process_unfinished_ad),name='process_unfinished_ad'),
	url(r'^ctut/$', auth(classified_tutorial_dec),name='classified_tutorial_dec'),
	url(r'^expire_ad/$', auth(expire_my_ad),name='expire_my_ad'),
	url(r'^saesf/$', auth(process_ad_expiry_or_sms_feedback),name='process_ad_expiry_or_sms_feedback'),
	url(r'^sms_settings/$', auth(change_my_sms_settings),name='change_my_sms_settings'),
	url(r'^seller_number/$', auth(show_seller_number),name='show_seller_number'),
	url(r'^meray_ads/$', auth(show_user_ads),name='show_user_ads'),
	#############################################E Commerce##########################################
	url(r'^item_ki_detail_likho/$', auth(post_basic_item),name='post_basic_item'),
	url(r'^baichney_waley_ki_detail_likho/$', auth(post_seller_info),name='post_seller_info'),
	url(r'^item_ki_pics_lagao/$', auth(post_basic_item_photos),name='post_basic_item_photos'),
	url(r'^kuch_baicho/$', auth(init_classified),name='init_classified'),
	url(r'^vsn/$',verify_basic_item_seller_number, name="verify_basic_item_seller_number"),
	url(r'^vcn/$',verify_consumer_number, name="verify_consumer_number"),
	############################################################
	url(r'^ecomm_metrics/(?P<metrics_type>[\w.@+-]+)/$',auth(display_latest_metrics), name="display_latest_metrics"),
	url(r'^get_ad_export/$',auth(get_ad_export), name="get_ad_export"),
	url(r'^get_click_distribution/$',auth(get_click_distribution), name="get_click_distribution"),
	url(r'^populate_photo_ads/$',auth(populate_photo_ads), name="populate_photo_ads"),
	# url(r'^is_locked_by_someone_else/$', auth(is_locked_by_someone_else),name='is_locked_by_someone_else'),
	# url(r'^shop_city/(?P<city>[\w.@+-]+)/$', auth(shops_by_city),name='shops_by_city'),
	# url(r'^add_shop/$', auth(add_shop),name='add_shop'),
	# url(r'^mobile/$', auth(show_shop_choices),name='ecomm'),

	# url(r'^mobile/x32/$', x32_details,name='x32'),
	# url(r'^mobile/x2lite/$', x2lite_details,name='x2lite'),
	# url(r'^mobile/loc/$', auth(buyer_loc),name='buyer_loc'),
	# url(r'^mobile/proc_city/$', auth(process_city),name='process_city'),
)