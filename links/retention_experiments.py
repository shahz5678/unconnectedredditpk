"""
The EXP dictionary holds the key-names of all experiments currently being run for the purposes of measuring retention

Each experiment requires the following key names:
exp(n):<user_id> - key holding time a user_id 'first' showed up in the experiment, think of it as a 'registration time' (rt) in the experiment. n can be '1', '2', '3', so on
exp(n)rl:<user_id> - key rate limiting a user_id from being counted again in the experiment's retention calculation
exp(n)r:<time_cohort> - sorted set holding daily retention values for time cohorts experiencing the experiment (e.g. d0, score0, d1, score1, d2, score2, etc)
exp(n)cr - key containing cached retention data for the experiment (useful for reporting)
"""

EXP = {\
# exp1 relates to retention of users who select 'trending photos' the first time they register on Damadam
'exp1':'rt1:','exp1rl':'e1rl:','exp1r':'e1r:','exp1cr':'e1cr',\
# exp2 relates to retention of users who select 'home' the first time they register on Damadam
'exp2':'rt2:','exp2rl':'e2rl:','exp2r':'e2r:','exp2cr':'e2cr',\
}

EXPERIMENTS_CURRENTLY_BEING_RUN = []#['exp1']