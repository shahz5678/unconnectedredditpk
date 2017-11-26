from django.shortcuts import render, redirect
from links.redis4 import log_ecomm_user_visit
from django.core.urlresolvers import resolve


# 21 Ecomm related URLs
URLS_TO_TRACK = {'classified_listing':True, 'city_list':True, 'exchange_classified_listing':True, 'city_exchange_classified_listing':True, 'city_classified_listing':True, \
'ad_detail':True, 'edit_classified':True, 'process_unfinished_ad':True, 'classified_tutorial_dec':True, 'expire_my_ad':True, 'process_ad_expiry_or_sms_feedback':True, \
'change_my_sms_settings':True, 'show_seller_number':True, 'show_user_ads':True, 'post_basic_item':True, 'post_seller_info':True, 'post_basic_item_photos':True, 'init_classified':True, \
'verify_basic_item_seller_number':True, 'verify_consumer_number':True}


class TrackUniqueEcommVisitsMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated() and resolve(request.path_info).url_name in URLS_TO_TRACK:
        	log_ecomm_user_visit(user_id=request.user.id)