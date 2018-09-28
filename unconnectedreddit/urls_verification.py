from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.verification_views import verify_user_artificially, verify_user_mobile, pin_verification, number_verification_help

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Mobile verification##########################################
	url(r'^verification/mobile/artificial/$', auth(verify_user_artificially), name='verify_user_artificially'),
	url(r'^verification/mobile/$', auth(verify_user_mobile), name='verify_user_mobile'),
	url(r'^verification/confirm-pin/$', auth(pin_verification), name='pin_verification'),
	url(r'^verification/help/$', auth(number_verification_help), name='number_verification_help'),
	# url(r'^verification/pink-star/help/$', auth(pink_star_verification_help), name='pink_star_verification_help'),
)