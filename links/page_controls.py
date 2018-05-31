ITEMS_PER_PAGE = 20
PHOTOS_PER_PAGE = 20
CRICKET_COMMENTS_PER_PAGE = 20
FANS_PER_PAGE = 100
STARS_PER_PAGE = 100
ADS_TO_APPROVE_PER_PAGE = 30
APPROVED_ADS_PER_PAGE = 20
MAX_ITEMS_PER_PAGE = 100
########################
WEEKLY_ECOMM_METRICS_HISTORY_LIMIT = 12
DAILY_ECOMM_METRICS_HISTORY_LIMIT = 60
########################
MOBILE_NUM_CHG_COOLOFF = 7776000 #3 months
########################
PERSONAL_GROUP_OBJECT_CEILING = 27#size after which the personal group could be trimmed
PERSONAL_GROUP_OBJECT_FLOOR = 21#size to which the group is trimmed down
PERSONAL_GROUP_BLOB_SIZE_LIMIT = 10
PERSONAL_GROUP_PHT_XFER_IVTS = 5
PERSONAL_GROUP_SMS_IVTS = 5
PERSONAL_GROUP_MAX_PHOTOS = 25
PERSONAL_GROUP_IMG_WIDTH = 400
PERSONAL_GROUP_IMGS_PER_PAGE = 20
PERSONAL_GROUP_MAX_SMS_SIZE = 150
PERSONAL_GROUP_MAX_PHOTO_CAPTION_SIZE = 150#max size of caption of shared photo
PERSONAL_GROUP_SMS_LOCK_TTL = 3600 #1 hour
PERSONAL_GROUP_SAVED_CHAT_COUNTER = 17 # number of messages a user can save at a time
PERSONAL_GROUP_OWN_BG = 'csb'
PERSONAL_GROUP_OWN_BORDER = 'sbb'
PERSONAL_GROUP_THEIR_BG = 'ca'
PERSONAL_GROUP_THEIR_BORDER =  'ab'
PERSONAL_GROUP_REJOIN_RATELIMIT = 86400 #1 day
PERSONAL_GROUP_SOFT_DELETION_CUTOFF = 604800#7 days old groups are target of soft deletion
PERSONAL_GROUP_HARD_DELETION_CUTOFF = 2479680#30 days old groups are target of hard deletion
EXITED_PERSONAL_GROUP_HARD_DELETION_CUTOFF = 604800#7 days old exited groups are target of hard deletion
OBJS_PER_PAGE_IN_USER_GROUP_LIST = 15#number of groups to show in paginated user group list
OBJS_PER_PAGE_IN_USER_GROUP_INVITE_LIST = 30#number of group invites to show in paginated user group list
PERSONAL_GROUP_INVITES = 4
PERSONAL_GROUP_INVITES_COOLOFF = 14400#4 hours
USER_GROUP_LIST_CACHING_TIME = 10# cached for 10 seconds
USER_FRIEND_LIST_CACHING_TIME = 300# cached for 5 minutes
URL_POSTINGS_ALLOWED = 5# number of urls that can be pasted in a 5 minute window (rate limiting for performance reasons)
PERSONAL_GROUP_URL_IMG_WIDTH = 70# in pixels
PRIV_CHAT_EMOTEXT = {'1':'ki dharkan tez ho geyi','2':'ko hansi ka dora par gaya','3':'ne kaha usko jaldi reply karo...',\
'4':'buhut udas hai...','5':'ne poocha kya scene hai?'}# used when generating notifications only (not centrally connected)
PRIV_CHAT_NOTIF = {'1':'ne photo send karney ki ijazat mangi','2':'ne ijazat mangi ke jab ap online na hon tou apko Damadam pe SMS ke zariye bulaya ja sakey'}
PHOTO_SHARING_FRIEND_LIMIT = 5#number of friends a person can share a photo with simultaneously