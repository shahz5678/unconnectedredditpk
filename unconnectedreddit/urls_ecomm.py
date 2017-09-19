from links.ecomm import x2lite_details, x32_details, buyer_loc, mobile_shop, post_basic_item, post_seller_info, post_basic_item_photos, \
init_classified, approve_classified, edit_classified, process_ad_approval, change_cover_photo, show_user_ads, ad_detail, process_unfinished_ad, \
ad_locked_by_agent, city_list, expire_my_ad, change_my_sms_settings, classified_listing, process_ad_expiry_or_sms_feedback, print_referrer_logs, \
redirect_to_social_section, initiate_seller_verification_process,show_city, buyer_details, buyer_verify, get_new_orders, confirm_order,i6metal_details,\
in_process,x33_details, x29_details, i8i_details, s6_details, j1_details, delivery, warranty, order_successful

#classified_tutorial_dec, show_seller_number, populate_photo_ads, get_spam_export
from links.ecomm_tracking import display_latest_metrics, get_ad_export, get_click_distribution
from links.number_verification import verify_basic_item_seller_number,verify_buyer_number#, verify_consumer_number
from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^social_networking/$', redirect_to_social_section,name='redirect_to_social_section'),
	#################################################################################################
	url(r'^buy_and_sell/cities/$', city_list,name='city_list'),
	url(r'^buy_and_sell/$', classified_listing,name='classified_listing'),
	url(r'^buy_and_sell/exchange/$', classified_listing,name='exchange_classified_listing'),
	url(r'^buy_and_sell/exchange/(?P<city>[\w.@+-]+)/$', classified_listing,name='city_exchange_classified_listing'),
	# url(r'^buy_and_sell/fotos/$', classified_listing,name='photos_classified_listing'),
	# url(r'^buy_and_sell/fotos/(?P<city>[\w.@+-]+)/$', classified_listing,name='city_photos_classified_listing'),
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
	# url(r'^ctut/$', auth(classified_tutorial_dec),name='classified_tutorial_dec'),
	url(r'^expire_ad/$', auth(expire_my_ad),name='expire_my_ad'),
	url(r'^saesf/$', auth(process_ad_expiry_or_sms_feedback),name='process_ad_expiry_or_sms_feedback'),
	url(r'^sms_settings/$', auth(change_my_sms_settings),name='change_my_sms_settings'),
	# url(r'^seller_number/$', auth(show_seller_number),name='show_seller_number'),
	url(r'^meray_ads/$', auth(show_user_ads),name='show_user_ads'),
	#############################################E Commerce##########################################
	url(r'^item_ki_detail_likho/$', auth(post_basic_item),name='post_basic_item'),
	url(r'^baichney_waley_ki_detail_likho/$', auth(post_seller_info),name='post_seller_info'),
	url(r'^item_ki_pics_lagao/$', auth(post_basic_item_photos),name='post_basic_item_photos'),
	url(r'^kuch_baicho/$', init_classified,name='init_classified'),
	url(r'^vsn/$',verify_basic_item_seller_number, name="verify_basic_item_seller_number"),
	# url(r'^vcn/$',verify_consumer_number, name="verify_consumer_number"),
	############################################################
	url(r'^ecomm_metrics/(?P<metrics_type>[\w.@+-]+)/$',auth(display_latest_metrics), name="display_latest_metrics"),
	url(r'^get_ad_export/$',auth(get_ad_export), name="get_ad_export"),
	url(r'^print_referrer_logs/$',auth(print_referrer_logs), name="print_referrer_logs"),
	url(r'^get_click_distribution/$',auth(get_click_distribution), name="get_click_distribution"),
	# url(r'^populate_photo_ads/$',auth(populate_photo_ads), name="populate_photo_ads"),
	# url(r'^is_locked_by_someone_else/$', auth(is_locked_by_someone_else),name='is_locked_by_someone_else'),
	# url(r'^shop_city/(?P<city>[\w.@+-]+)/$', auth(shops_by_city),name='shops_by_city'),
	# url(r'^add_shop/$', auth(add_shop),name='add_shop'),
	# url(r'^mobile/$', auth(show_shop_choices),name='ecomm'),

	url(r'^mobile_shop/$', auth(mobile_shop),name='mobile_shop'),
	url(r'^mobile_shop/x33/$', x33_details,name='x33'),
	url(r'^mobile_shop/x29/$', x29_details,name='x29'),
	url(r'^mobile_shop/i8i/$', i8i_details,name='i8i'),
	url(r'^mobile_shop/s6/$', s6_details,name='s6'),			
	url(r'^mobile_shop/j1/$', j1_details,name='j1'),
	url(r'^mobile_shop/i6metal/$', i6metal_details,name='i6metal'),

	#url(r'^mobile/x32/$', x32_details,name='x32'),
	#url(r'^mobile/x2lite/$', x2lite_details,name='x2lite'),
	url(r'^mobile/i6metal/$', i6metal_details,name='i6metal'),
	url(r'^mobile/loc/$', auth(buyer_loc),name='buyer_loc'),
	# url(r'^mobile/proc_city/$', auth(process_city),name='process_city'),

	url(r'^show_city/$', auth(show_city),name='show_city'),
	url(r'^buyer_details/$', auth(buyer_details),name='buyer_details'),
#	url(r'^num_verification/$', auth(num_verification),name='num_verification'),
	url(r'^buyer_verify/$', auth(buyer_verify),name='buyer_verify'),
	url(r'^new_orders/$', auth(get_new_orders),name='new_orders'),
	url(r'^vbn/', auth(verify_buyer_number), name='verify_buyer_number'),
	url(r'^confirm_order/', auth(confirm_order), name='confirm_order'),
	url(r'^in_process/', auth(in_process), name='in_process'),
	url(r'^order_successful/', auth(order_successful), name='order_successful'),


	url(r'^delivery/(?P<origin>[\w.@+-]+)/$', auth(delivery), name='delivery'),
	url(r'^warranty/(?P<origin>[\w.@+-]+)/$', auth(warranty), name='warranty'),
)