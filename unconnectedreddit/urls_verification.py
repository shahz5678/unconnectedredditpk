from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.verification_views import verify_user_artificially, pin_verification, number_verification_help, wait_before_verifying, \
account_kit_verification_commencement, account_kit_verification_processing, account_kit_verification_result, unverify_user, \
verify_user_mobile_unpaid, firebase_verification, unable_to_verify_on_fbs, firebase_verification_result
# from links.unauth_views import render_set_new_password
admin.autodiscover()

urlpatterns = patterns('',
	###################### Via Firebase #############################
	url(r'^verification/mobile/$', auth(verify_user_mobile_unpaid), name='verify_user_mobile_unpaid'),
	url(r'^verification/mobile/via-firebase/$', auth(firebase_verification), name='firebase_verification'),
	url(r'^verification/mobile/via-firebase/cannot-verify-on-fbs/$', auth(unable_to_verify_on_fbs), name='unable_to_verify_on_fbs'),
	url(r'^verification/mobile/via-firebase/failed/verification/$', auth(firebase_verification_result), name='firebase_verification_failed'),
	url(r'^verification/mobile/via-firebase/successful/verification/$', auth(firebase_verification_result), name='firebase_verification_successful'),
	url(r'^verification/mobile/via-firebase/failed/forgot-pass/$', firebase_verification_result, name='firebase_forgot_pass_verification_failed'),
	# url(r'^verification/mobile/via-firebase/successful/forgot-pass/$', render_set_new_password, name='firebase_forgot_pass_verification_successful'),
	############################################# Artificial Verification and Unverfication Urls #####################
	url(r'^verification/mobile/via-artificial/$', auth(verify_user_artificially), name='verify_user_artificially'),
	url(r'^verification/mobile/unverified/$', auth(unverify_user), name='unverify_user'),
	
	############################################# Via 3rd Party SMS Service ##########################################
	#url(r'^verification/mobile/$', auth(verify_user_mobile_paid), name='verify_user_mobile_paid'),
	url(r'^verification/confirm-pin/$', auth(pin_verification), name='pin_verification'),
	url(r'^verification/help/$', auth(number_verification_help), name='number_verification_help'),
	#url(r'^verification/please-wait/$', auth(wait_before_verifying), name='wait_before_verifying'),
	# url(r'^verification/pink-star/help/$', auth(pink_star_verification_help), name='pink_star_verification_help'),
	
	############################################# Via Account Kit ##########################################
	url(r'^verification/mobile/via-account-kit/$', auth(account_kit_verification_commencement), name='account_kit_verification_commencement'),
	url(r'^verification/mobile/via-account-kit/process-verification/$', auth(account_kit_verification_processing), name='account_kit_verification_processing'),
	url(r'^verification/mobile/via-account-kit/verification-successful/account-verification/$', auth(account_kit_verification_result), name='account_kit_verification_successful'),
	# url(r'^verification/mobile/via-account-kit/verification-successful/forgot-pass/$', render_set_new_password, name='account_kit_forgot_pass_verification_successful'),
	url(r'^verification/mobile/via-account-kit/verification-failed/account-verification/$', auth(account_kit_verification_result), name='account_kit_verification_failed'),
	url(r'^verification/mobile/via-account-kit/verification-failed/forgot-pass/$', account_kit_verification_result, name='account_kit_forgot_pass_verification_failed'),
)