"""
The EXP dictionary holds the key-names of all variations within the experiment

Each variation requires the following key names:
'n' - the variation number. n can be '1', '2', '3', so on
var(n):<user_id> - key holding time a user_id 'first' showed up in the variation, think of it as a 'registration time' (rt) in the variation
var(n)r:<time_cohort> - sorted set holding daily retention values for time cohorts experiencing the variation (e.g. d0, score0, d1, score1, d2, score2, etc)
var(n)cr - key containing cached retention data for the variation (useful for reporting)
"""

EXP = {\
# var1 relates to retention of users who select 'famous' variation in the tut
'var1':'rt1:','var1r':'e1r:','var1cr':'e1cr',\
# var2 relates to retention of users who select 'dosti' variation in the tut
'var2':'rt2:','var2r':'e2r:','var2cr':'e2cr',\
# var3 relates to retention of users who select 'content' variation in the tut
'var3':'rt3:','var3r':'e3r:','var3cr':'e3cr',\
# var4 relates to retention of users who select 'other' variation in the tut
'var4':'rt4:','var4r':'e4r:','var4cr':'e4cr',\
# var5 relates to retention of users who select 'dosti' variation in the tut (and are taken to mehfils)
'var5':'rt5:','var5r':'e5r:','var5cr':'e5cr',\
# var6 relates to retention of users who select 'content' variation in the tut (and are taken to topics)
'var6':'rt6:','var6r':'e6r:','var6cr':'e6cr',\
# var6 relates to retention of users who select 'content' variation in the tut (and are taken to topics)
'var7':'rt7:','var7r':'e7r:','var7cr':'e7cr'
}

EXPERIMENTS_CURRENTLY_BEING_RUN = ['var1','var2','var3','var4','var5','var6','var7']