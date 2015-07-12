import tweepy
from tweepy import OAuthHandler
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
from links.views import LinkAutoCreate
from django.contrib.auth.models import User

auth = tweepy.OAuthHandler('sjYHR8YZXyrm0tJYpuhuNHcqc', 'ZQAFbi782pJm8wMMVEQ31jMmLdqdEXWqaIxIgi1dE0SRfkvtDo')
auth.set_access_token('19013184-IPGMNzMnTZmg9acmnSrfcMBUPGvHhvzrpA3ZxDhYF', 'HFLgH0aMShnEPtfPVMBcE6JXae8kaSu6oznJyh60y0aVx')

api = tweepy.API(auth)

#public_tweets = api.home_timeline()
public_tweet = api.user_timeline(id='pak_fun', count=1, include_rts=False)
#public_tweet2 = api.user_timeline(id='baigi', count=1, include_rts=False)
for tweet in public_tweet:
    retort = tweet.text
    user = User(id=3) #can set to any user via their ID
    if retort == user.userprofile.previous_retort:
        pass
    else:
    	LinkAutoCreate(user=user, content=retort)
	'''
for tweet2 in public_tweet2:
    retort2 = tweet2.text
    user2 = User(id=1) #can set to any user via their ID
    if retort2 == user2.userprofile.previous_retort:
        print 'NOTHING NEW'
    else:
    	LinkAutoCreate(user=user2, content=retort2)
	'''