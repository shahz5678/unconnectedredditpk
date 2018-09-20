from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin
from links.verification_views import verify_user_artificially

admin.autodiscover()

urlpatterns = patterns('',
	#############################################Mobile verification##########################################
	url(r'^verification/mobile/artificial/$', auth(verify_user_artificially), name='verify_user_artificially'),
)