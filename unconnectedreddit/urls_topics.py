from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from links.topic_views import topic_page, submit_topic_post, suggest_new_topic_feed, topic_redirect, subscribe_to_topic, delete_topic, \
topic_gone, topic_listing, unsubscribe_topics

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^topic/listing/$', topic_listing, name='topic_listing'),
	url(r'^(?P<topic_url>[\w.@+-]+)/$', topic_page, name='topic_page'),
	url(r'^topic/redirect/$', auth(topic_redirect), name='topic_redirect'),
	url(r'^topic/gone/(?P<topic_url>[\w.@+-]+)/$', topic_gone, name='topic_gone'),
	url(r'^topic/unsubscribe/$', auth(unsubscribe_topics), name='unsubscribe_topics'),
	url(r'^topic/suggest/$', auth(suggest_new_topic_feed), name='suggest_new_topic_feed'),
	url(r'^topic/delete/(?P<topic_url>[\w.@+-]+)/$', auth(delete_topic), name='delete_topic'),
	url(r'^topic/redirect/(?P<topic_url>[\w.@+-]+)/$', auth(topic_redirect), name='topic_redirect'),
	url(r'^topic/submit/(?P<topic_url>[\w.@+-]+)/$', auth(submit_topic_post), name='submit_topic_post'),
	url(r'^topic/subscribe/(?P<topic_url>[\w.@+-]+)/$', auth(subscribe_to_topic), name='subscribe_to_topic'),
	url(r'^topic/redirect/(?P<topic_url>[\w.@+-]+)/(?P<obj_hash>[\w\:]+)/$', auth(topic_redirect), name='topic_redirect'),
)