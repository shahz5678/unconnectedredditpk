from django.contrib import admin
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as auth
from links.sharing_views import log_sharing

admin.autodiscover()

urlpatterns = patterns('',
	###################################### Social Sharing ########################################
	url(r'^log-share/$', log_sharing, name='log_sharing'),
)