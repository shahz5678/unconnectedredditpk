from links.views import advertise_with_us, show_advertisers
from django.contrib.auth.decorators import login_required as auth
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^show_advertisers/', auth(show_advertisers), name='show_advertisers'),
	url(r'^advertise_with_us/', advertise_with_us, name='advertise_with_us'),
)