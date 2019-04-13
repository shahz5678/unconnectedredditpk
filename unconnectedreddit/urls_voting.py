from django.contrib import admin
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required as auth
from links.voting_views import vote_result, cast_vote, show_voting_summary,show_handpicked_count

admin.autodiscover()

urlpatterns = patterns('',
	###################################### Voting ########################################
	url(r'^cast_vote/$', auth(cast_vote), name='cast_vote'),
	url(r'^vote_result/$', auth(vote_result), name='vote_result'),
	url(r'^voting/super-defenders/$', auth(show_handpicked_count), name='show_handpicked_count'),
	url(r'^voting_results/(?P<pk>\d+)/(?P<orig>\d+)/(?P<pht>\d+)/$', auth(show_voting_summary), name='show_voting_summary'),

)