# coding=utf-8
MAX_BIO_SIZE = 1000
MAX_HOME_SUBMISSION_SIZE = 750
MAX_HOME_REPLY_SIZE = 350# i.e. Publicreply
MAX_PHOTO_COMMENT_SIZE = 350# i.e. PhotoComment
MAX_PHOTO_CAPTION_SIZE = 100
THRESHOLD_WORLD_AGE = 17# world age after which a user is considered an 'experienced' user
###############################################################################################################
VOTING_CLOSED_ARCHIVE_OVERFLOW_TIME = 1728000# i.e. 20 days. This is the amount of time closed-voting objs are kept around for 'like_prob' analysis
###############################################################################################################
PUBLIC_SUBMISSION_TTL = 86400#24 hours set as ttl for links and photos submitted to Damadam (i.e. redis object TTL)
UPLOAD_PHOTO_REQ = 30 #score below which you're not allowed photo uploads
PHOTO_HOT_SCORE_REQ = 4 #aggregated 'vote_score' over previous 5 photos, above which your photo appears on home
NUM_TRENDING_PHOTOS = 200 #how many trending photos to keep in a sorted set for users' viewing?
NUM_SUBMISSION_ALLWD_PER_DAY = 100#num of home and photo posts allowed in one day
CONTENT_SHARING_SHORT_RATELIMIT = 45#amount of time to wait between sharing posts (time pooled between home and photos) 
CONTENT_SHARING_LONG_RATELIMIT = 86400# 
HOURS_LOOKBACK_FOR_CHECKING_CONTENT_CLONES = 50#how many hours to look back when reporting a content clone (used in get_content_history in judgement_views.py)
CONTEST_LENGTH = 604800 #Length of time to calculate top trending photo contributors
RIGHT_ALIGNMENT_THRESHOLD_RATIO = 0.5 #if a text has more 'urdu' characters than this ratio, right align it
################################################ Topics ################################################
TOPIC_LIFELINE = 1728000#20 days - i.e. how long a topic should exist even if it has no visits
TOPIC_SUBMISSION_TTL = 604800#7 days set as ttl for content submitted into a topic
TOPIC_UNSUB_LOCKING_TIME = 7200#2 hours is how long a subscriber must stay inside a topic after subscribing to it
MAX_TOPIC_SIZE = 80
MIN_TOPIC_SIZE = 3
MIN_TOPIC_DESCRIPTION_SIZE = 20
################################################ Judgement Related Variables ##################################
USER_REBAN_ACTION_RATELIMIT = 86400#1 day is the length of time a user should be rate limited from re-blocking a target (right after unblocking them)
USER_UNBAN_ACTION_RATELIMIT = 86400#1 day is the length of time a user should be rate limited from unblocking a target (right after blocking them)
###############################################################################################################
TRENDER_RANKS_TO_COUNT = 15 #of top trenders to be shown
# SEARCH_FEATURE_THRESHOLD = 100# REMOVE
# SUPER_UPVOTE = 20# REMOVE
# PERMANENT_RESIDENT_SCORE = 300#REMOVE
# SUPER_DOWNVOTE = -20# REMOVE
# PHOTO_CASE_COMPLETION_BONUS = 6#REMOVE
GIBBERISH_PUNISHMENT_MULTIPLIER = 5#REMOVE
CITIES = ["Rawalpindi","Islamabad"]#REMOVE
SHARE_ORIGIN = {'1':'fresh_photos','3':'user_albums'}#REMOVE
SHARED_PHOTOS_CEILING = 120#REMOVE
PHOTO_DELETION_BUFFER = 15#REMOVE
VOTE_TEXT = {'1':'<span style="font-size:80%;color:#009940;"> ne barri si <b>jhappi</b> di</span><br>',\
'-1':'<span style="font-size:80%;color:#F4511E;"> ne bharey bazar mein <b>chupair</b> mari</span><br>',\
'2': '<span style="font-size:80%;color:#009940;"> ne zordar <b>jhappi</b> di <b>(+20)</b></span><br>',\
'-2': '<span style="font-size:80%;color:#F4511E;"> ne <b>chupair</b> mr mr ke nani yad kra di <b>(-20)</b></span><br>',\
'3': '<span style="font-size:80%;color:#009940;"> ko ye photo <b>zabrdast</b> lagi</span><br>',\
'-3': '<span style="font-size:80%;color:#F4511E;"> ko ye photo <b>bekaar</b> lagi</span><br>',\
'4':'<span style="font-size:80%;color:#009940;"> ne iski shot pe <b>taliyan</b> bajaien</span><br>',\
'-4':'<span style="font-size:80%;color:#F4511E;"> ne isko ghuma ke <b>balla</b> mara</span><br>',\
'5': '<span style="font-size:80%;color:#009940;"> ne iske <b>six</b> pe chalangein lagaien <b>(+20)</b></span><br>',\
'-5': '<span style="font-size:80%;color:#F4511E;"> ne isko <b>andey</b> pe out kr diya <b>(-20)</b></span><br>'}#REMOVE
###############################################################################################################
THUMB_HEIGHT = 38
MIN_PUBLIC_IMG_WIDTH = 315# this number must belong to this interval: [450, 405, 360, 315, 270, 225, 180, 135, 90] (equal to resize_ranges in image_processing.py)
###############################################################################################################
FBS_VERIFICATION_WAIT_TIME = 86400# amount of time (1 day) a free basics person has to wait before mobile verification is allowed
FBS_PUBLIC_PHOTO_UPLOAD_RL = 900#amount of time an FBS user has to wait before being allowed to upload a public photo again. MUST be greater than CONTENT_SHARING_SHORT_RATELIMIT
###############################################################################################################
VOTE_SPREE_ALWD = 25# number of votes allowed on link objects within a small time window before cooldown begins (applied separately to photo voting too)
UPVOTE = 2#number to add to user score
DOWNVOTE = -2#number to subtract from user score
VOTING_DRIVEN_CENSORSHIP = -15# at what total vote count should a photo be completely disappeared
VOTING_DRIVEN_PIXELATION = -7# at what total vote count should a photo be pixellated
###############################################################################################################
BAYESIAN_PROB_THRESHOLD_FOR_VOTE_NERFING = 0.3# if a voter shows a bias of at least (or greater than) this magnitude, their vote counts for zilch!
UPPER_RELATIONSHIP_UVOTE_CUTOFF = 4# upper threshold for 'score' used when doing a sequential scan of UVOTER_AFFINITY sorted set
UPPER_RELATIONSHIP_DVOTE_CUTOFF = 4# upper threshold for 'score' used when doing a sequential scan of DVOTER_AFFINITY sorted set
MEANINGFUL_VOTING_SAMPLE_SIZE = 10# threshold used to determine whether a 'voting relationship' should be investigated or not
NUM_VOTES_TO_TGT = 5# a target user must have received these many votes from voter to make calculating their Bayesian affinity worthwhile (upvotes and downvotes both)
###############################################################################################################
MICRO_CACHE_TTL = 15# useful for micro caching some fast changing keys in groups (do a ctrl+f in redis6 to see examples)
PRIVATE_GROUP_MAX_TITLE_SIZE = 150 #more than 150 chars not allowed
PRIVATE_GROUP_MAX_MEMBERSHIP = 50
PUBLIC_GROUP_MAX_TITLE_SIZE = 150 #more than 150 chars not allowed
PUBLIC_GROUP_MAX_RULES_SIZE = 500 #more than 500 chars not allowed
PUBLIC_GROUP_REPLY_LENGTH = 500
NUM_PUBLIC_GROUPS_OWNED_SHOWN_ON_PROFILE = 5#how many public groups to show on user profile
PRIVATE_GROUP_REPLY_LENGTH = 500

###### Mehfil list ######
TOTAL_LIST_SIZE = 80
MEHFIL_LIST_PAGE_SIZE = 20
#########################

###### Officer applications in public groups ######
PUBLIC_GROUP_OFFICER_APPLICATION_ANSWER_LEN = 200# each answer in officer application is going to be this many chars in length
MAX_OFFICER_APPOINTMENTS_ALLWD = 3 #num of officers one ID can be
MAX_ARCHIVED_OFFICER_APPS_PER_GROUP = 4#when the same user submits an officer app to the same group again and again, how many should we keep in the user history?
OFFICER_APPLICATION_EXPIRY_TIME = 259200# 3 days
OFFICER_APPLICATIONS_RATE_LIMIT = 345600# 4 days - must ALWAYS be greater than 'OFFICER_APPLICATION_EXPIRY_TIME'
MIN_GRP_MEMBERSHIP_AGE_FOR_REQUESTING_GRP_OFFICERSHIP = 86400#1 day
MIN_APP_MEMBERSHIP_AGE_FOR_REQUESTING_GRP_OFFICERSHIP = 604800#7 days
OFFICER_APP_ARCHIVE_EXPIRY_TIME = 10368000#4 months
GROUP_OFFICER_QUESTIONS = {'1':'Ap mehfil ka mahol khush gawar rakhney mein owner ki kya kya help karo ge?',\
'2':'Ap is mehfil ko daily kitna time do ge?'}
###################################################

########## Invites in groups ##########
GROUP_INVITE_LOCK_DURATION = 1209600#2 weeks - use this key to disallow reinviting the same user again and again
INVITER_PRIVATE_INVITE_LOCK_DURATION = 259200#3 days - use this key to disallow reinviting by the same user again and again (even to different groups)
INVITER_PUBLIC_INVITE_LOCK_DURATION = 259200#3 days - use this key to disallow reinviting by the same user again and again (even to different groups)
CANCEL_PUBLIC_INVITE_AFTER_TIME_PASSAGE = 259200#3 days after inviting, a public group owner can cancel their invite
CANCEL_PRIVATE_INVITE_AFTER_TIME_PASSAGE = 86400#1 day after inviting, a private group owner can cancel their invite
PRIVATE_GROUP_INVITE_TTL = 604800#7 days ttl for private group invites. Must be shorter than INVITE_LOCK_DURATION and longer than CANCEL_PRIVATE_INVITE_AFTER_TIME_PASSAGE to work
PUBLIC_GROUP_INVITE_TTL = 604800#7 days ttl for public group invites. Must be shorter than INVITE_LOCK_DURATION and longer than CANCEL_PUBLIC_INVITE_AFTER_TIME_PASSAGE to work
MAX_OWNER_INVITES_PER_PUBLIC_GROUP = 30 #num users an owner can invite into a group within a week
MAX_OWNER_INVITES_PER_PRIVATE_GROUP = 30 #num users a priv mehfil owner can invite
MAX_OFFICER_INVITES_PER_PUBLIC_GROUP = 10 #num users all officers can invite into a group
MAX_MEMBER_INVITES_PER_PRIVATE_GROUP = 10 # num users a priv mehfil member can invite
#######################################

########## Group transactions #########
MIN_MEMBERSHIP_AGE_FOR_REQUESTING_GRP_OWNERSHIP = 172800#2 days
GROUP_TRANSACTION_RATE_LIMIT = 2592000# number of days (30) to rate limit the participants of a successfully concluded group transaction
GROUP_AGE_AFTER_WHICH_IT_CAN_BE_TRANSFERRED = 864000# group must be at least 10 days in age before it can be transferred
FOLLOW_UP_REQUEST_RATE_LIMIT = 604800#7 days rate limit for re-requesting group transfer from the same group owner
#######################################

######## Public/Private group creation ########
USER_AGE_AFTER_WHICH_PUBLIC_MEHFIL_CAN_BE_CREATED = 604800# age requirement is 7 days in seconds
PUBLIC_GROUP_COST = 5000 # cost of buying a public group
PRIVATE_GROUP_CREATION_RATE_LIMIT = 14400#4 hrs
PUBLIC_GROUP_CREATION_RATE_LIMIT = 604800#7 days

####### Group topic changing rate limits #######
TOPIC_SHORT_RATE_LIMIT = 1800#30 mins rate limiting
TOPIC_LONG_RATE_LIMIT = 86400#1 day rate limiting
RULES_CHANGE_RATE_LIMIT = 86400#1 day rate limiting
NUM_TOPIC_CHANGE_ATTEMPTS_ALLOWED = 3 # num of topic change 'failed' attempts in groups after which the user is rate limited
MAX_TIME_BETWEEN_TOPIC_CHANGE_ATTEMPTS = 300#if less than 5 mins between topic change attempts, increment the 'attempts' counter
MAX_TIME_BETWEEN_RULE_CHANGE_ATTEMPTS = 300#if less than 5 mins between rule change attempts, increment the 'attempts' counter
EXCESSIVE_ATTEMPTS_TO_CHANGE_TOPIC_RATE_LIMIT = 1200#20 min rate limit if user tries excessive amount of times to change topic
EXCESSIVE_ATTEMPTS_TO_CHANGE_RULES_RATE_LIMIT = 1200#20 min rate limit if user tries excessive amount of times to change rules
NUM_RULES_CHANGE_ATTEMPTS_ALLOWED = 4 # num of rules change 'failed' attempts in groups after which the user is rate limited
################################################

####### Group messaging thresholds #######
GROUP_GREEN_DOT_CUTOFF = 60# if seen in last 60 seconds, show green dot
GROUP_IDLE_DOT_CUTOFF = 210# if seen later than 60 but before 210, show idle dot
MSGS_TO_SHOW_IN_GROUP = 35# number of messages to show in groups (public and private both)
DELETION_THRESHOLD = 70# number of messages to keep in group list (before deletion sets in)
NUM_TO_DELETE = 35#number of messages to delete once DELETION_THRESHOLD HITS
PUBLIC_GROUP_MESSAGE = 2 # score for messaging in public group
PRIVATE_GROUP_MESSAGE = 2 # score for messaging in privte group
##########################################

########## Group exiting ##########
PUBLIC_GROUP_EXIT_LOCK = 7200# lock public mehfil enterer from exiting for 2 hours (they can however be kicked)
PRIVATE_GROUP_EXIT_LOCK = 2400# lock private mehfil enterer from exiting for 40 mins (they can however be kicked)
GROUP_REENTRY_LOCK = 54000#lock group reentry (after exiting) for 15 hours (both public and private groups)
###################################

############ Group feedback ############
MIN_MEMBERSHIP_AGE_FOR_GIVING_PUBLIC_GRP_FEEDBACK = 108000#30 hours (a little more than a day)
GROUP_FEEDBACK_SIZE = 200 #num of chars in feedback provided to kicked users or by users to admins
FEEDBACK_TTL = 1209600#2 weeks;num seconds feedback stays alive for
FEEDBACK_RATELIMIT = 259200#3 days; num seconds user is rate limited from sending feedback again
FEEDBACK_CACHE = 86400#1 day, num seconds the feedback list is cached for
########################################

MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC = 2# how many times can '.' or '-' (etc) occur in a mehfil topic
GROUP_MEMBERS_PER_PAGE = 50 #num of group members per page, shown in a mehfil's group members page
GROUP_VISITORS_PER_PAGE = 50 #num of group members per page, shown in a mehfil's group members page

POINTS_DEDUCTED_WHEN_GROUP_SUBMISSION_HIDDEN = 2
PRIVATE_GROUP_COST = 500 # cost of buying a private group
PUBLIC_GROUP_MAX_SELLING_PRICE = 0#(PUBLIC_GROUP_COST*2)-1
PUBLIC_GROUP_MIN_SELLING_PRICE = 0#PUBLIC_GROUP_COST#PUBLIC_GROUP_COST*0.3
GROUP_HARD_DELETION_CUTOFF = 2479680#30 days old groups are targets of hard deletion (i.e. full deletion)
GROUP_SOFT_DELETION_CUTOFF = 604800#7 days old groups are target of soft deletion (i.e. emptying content)

PUBLICREPLY = 2 #score for leaving publicreply on a home 'link'
###############################################################################################################
CRICKET_SUPPORT_STARTING_POINT = 10 #score at which PSL support options open up
CRICKET_TEAM_NAMES = {'Lahore Qalandars':'Qalandars','Islamabad United':'United',\
'Karachi Kings':'Kings','Peshawar Zalmi':'Zalmi','Quetta Gladiators':'Gladiators',\
'South Africa':'South Africa','New Zealand':'New Zealand', 'Pakistan':'Pakistan',\
'West Indies':'West Indies', 'India':'India','Sri Lanka':'Sri Lanka','England':'England',\
'World-XI':'World-XI','Multan Sultans':'Sultans','Australia':'Australia'}
CRICKET_TEAM_IDS = {'Lahore Qalandars':'5','Islamabad United':'8','Karachi Kings':'3',\
'Peshawar Zalmi':'4','Quetta Gladiators':'7','misc':'9','South Africa':'11','New Zealand':'10',\
'Pakistan':'12','West Indies':'13', 'India':'14', 'Sri Lanka':'15','England':'16','World-XI':'18',\
'Multan Sultans':'19','Australia':'20'}
CRICKET_COLOR_CLASSES = {'Lahore Qalandars':'qal','Islamabad United':'uni','Multan Sultans':'msu',\
'Karachi Kings':'kng','Peshawar Zalmi':'zal','Quetta Gladiators':'gld','misc':'bcb',\
'South Africa':'saf','New Zealand':'nze','Pakistan':'pak','West Indies':'wid','India':'ind',\
'Sri Lanka':'slk','England':'eng','World-XI':'wxi','Australia':'aus'}
###############################################################################################################
PHOTOS_WITH_SEARCHED_NICKNAMES = 5
#REPORTED_CASE_COMPLETION_BONUS = 0#15#turning case completion bonus to '0' for now (revert if defenders complain)

PHOTO_REPORT_PROMPT = {'0':'Report rehne dein','1':'Foto mein nudity ya sex hai','2':'Foto mein firqa wariyat hai',\
'3':'Foto mein khoon kharaba ya aziyat hai','4':'Foto dehshat gardi ki himayat kar rahi hai',\
'7':'Title ka foto se taluq nahi hai','8':'Title mein vote or comments ki bheek hai',\
'5':'Foto Damadam ki screenshot hai','6':'Foto quality buhut ziyada dhundhli hai','9':'Apki recent foto copy ki hai',\
'10':'Isne apni recent foto dubara lagai hai'}# 9 and 10 keys of this dictionary MUST MATCH 9 and 10 keys of TEXT_REPORT_PROMPT
GET_PHOTO_REPORT_HELP_LABEL = {'0':'','1':'photo_nudity_or_sex','2':'photo_firqa_wariyat','3':'photo_bloodshed','4':'photo_terrorism',\
'5':'photo_screenshot','6':'photo_low_quality','7':'photo_wrong_title','8':'photo_title_solicitation','9':'photo_plagiarism',\
'10':'photo_double_posting'}

TEXT_REPORT_PROMPT = {'0':'Report rehne dein','1':'Fan to fan ya 1 on 1 ki post ki hai',\
'2':'Galiyan ya dhamkiyan di hain','3':'Sexual ya vulgar post ki hai','4':'Betukki cheez likhi hai (e.g. "sadfsadfa" or ":P:D:P")',\
'5':'Repeat honay wali cheez likhi hai (e.g. "سلام, سلام, سلام")','6':'Home pe chat karney ki koshish ki hai (e.g. "Hello, how are you")',\
'7':'Firqa wariyat wali post ki hai','8':'Dehshat gardi ki himayat ki hai','9':'Apki recent post copy ki hai',\
'10':'Isne apni recent post dubara lagai hai','11':'Romance ki bheek mangi hai',\
'12':'Ghalat afwahein phelai hain (e.g. "Admin users ke phone number bech raha hai")',\
'13':'Kam alfaz mein ziyada new-lines hain: <div style="text-align:center">(e.g.<br>"malik ne<br>nokar se<br>poocha")</div>'}
GET_TEXT_REPORT_HELP_LABEL = {'0':'','1':'text_fan_to_fan','2':'text_abuse','3':'text_vulgar','4':'text_crap','5':'text_repeating',\
'6':'text_chat','7':'text_firqa_wariyat','8':'text_terrorism','9':'text_plagiarism','10':'text_double_posting',\
'11':'text_romantic_solicitation','12':'text_rumor','13':'text_multi_new_line'}

MEHFIL_REPORT_PROMPT = {'0':'Report rehne dein','1':'Topic ganda hai','2':'Topic mein abuse hai',\
'3':'Topic mein firqa wariyat hai','4':'Topic mein jhooti afwah hai','5':'Rules gandey hain',\
'6':'Rules mein abuse hai','7':'Rules mein firqa wariyat hai',\
'8':'Rules mein jhooti afwah hai'}# do NOT add '9' and '10' (those are reserved for TEXT_REPORT_PROMPT and PHOTO_REPORT_PROMPT)
GET_MEHFIL_REPORT_HELP_LABEL = {'0':'','1':'mehfil_topic_vulgar','2':'mehfil_topic_abuse','3':'mehfil_topic_firqa_wariyat',\
'4':'mehfil_topic_rumor','5':'mehfil_rules_vulgar','6':'mehfil_rules_abuse','7':'mehfil_rules_firqa_wariyat','8':'mehfil_rules_rumor'}

PROFILE_REPORT_PROMPT = {'0':'Report rehne dein','1':'Nickname ganda hai','2':'Nickname mein abuse hai',\
'3':'Nickname mein firqa wariyat hai','4':'Profile foto gandi hai','5':'Profile foto mein screenshot hai',\
'6':'Profile foto mein firqa wariyat hai','7':'Profile foto mein jhooti afwah hai'}# do NOT add '9' and '10'
GET_PROFILE_REPORT_HELP_LABEL = {'0':'','1':'username_vulgar','2':'username_abuse','3':'username_firqa_wariyat','4':'profile_pic_vulgar',\
'5':'profile_pic_screenshot','6':'profile_pic_firqa_wariyat','7':'profile_pic_rumor'}

EXIT_DISCOUNT = 1
KICK_DISCOUNT = 0.5
GROUP_SIZE_PERCENTILE_CUTOFF = 0.95#what percentile of groups to consider when ranking public groups
###############################################################################################################
ON_FBS_PHOTO_THRESHOLD = 200000
OFF_FBS_PHOTO_THRESHOLD = 10000000
LEAST_CLICKS = 5
MOST_CLICKS = 45
MEDIUM_CLICKS = 15
MOST_DURATION = 336 # Two weeks in hours
LEAST_DURATION = 168 # One week in hours
TWILIO_NOTIFY_THRESHOLD = 20
###############################################################################################################
NUMBER_VERIFICATION_THRESHOLD = 0
NUMBER_VERIFICATION_BONUS = 500
###############################################################################################################
PW = 'F1l2O3c4C5i6N7a8U9c1I2n3I4h5I6l7I8p9I1l2I3f4I5c6A7t8I9o1N2'
###############################################################################################################
PERSONAL_GROUP_NOTIF_IVT_RATE_LIMIT = 86400#1 day breather between sending notification invites in personal groups
PERSONAL_GROUP_NOTIF_RATE_LIMIT = 1800#rate limit a person for 30 mins after they've sent a push notification
PERSONAL_GROUP_ERR = {'too_high':'Ye foto buhut lambi hai, koi aur chunein',\
'mismatch':'Rabta munqata ho gaya, phir se karien','generic':'Internet ka rabta munqata ho gaya, phir se karien'}
PERSONAL_GROUP_DEFAULT_SMS_TXT = ' ne apko Damadam ki 1 on 1 mein bulaya'
EXTRA_PADDING = 20 #used to adjust image sizes in cases where CSS uses box-sizing:border-box property
PERSONAL_GROUP_SAVE_MSGS = {'err2':'Ye msg mita diye janey ki waja se save nahi ho saka',\
'err3':'Ye msg hide honay ki waja se save nahi ho saka','err4':'Ye msg apkey save karney se pehlay delete ho gya',\
'err5':'Ap is msg ko save kar sakein ge ','err1':'Ye msg save nahi ho sakta','msg1':'Msg save kar dia gya',\
'err6':'Ye msg save karney ke liye apney pichley saved msgs mein se kuch delete karein',\
'err7':'Ye msg pehley bhi save kia ja chuka hai, dubara nahi ho sakta',\
'err8':'Kharabi ho geyi, phir se koshish karein','err9':'Ap ko ye msg save karney ki ijazat nahi'}
###############################################################################################################
# helps in setting TTL on rate limits set on abusive users. Each key defines 'level' of offense, values are ttl
BAN_REASON = {'flooding':'tez tez likhna (flooding or spamming)'}
RATELIMIT_TTL = {'0':60*4,'1':60*10,'2':60*30,'3':60*60*2,'4':60*60*8,'5':60*60*24,'6':60*60*24*3,'7':60*60*24*7,'8':60*60*24*30}
SUPER_FLOODING_THRESHOLD = 3 # 3 seconds on avg between multiple sentences
FLOODING_THRESHOLD = 5 # 5 seconds on avg between multiple sentences
LAZY_FLOODING_THRESHOLD = 7 # 7 seconds on avg between multiple sentences
SHORT_MESSAGES_ALWD = 4
MERCH = { 
'1': {'price':'4200' ,'discounted_price':'4200', 'points_cost': '5000', 'discount':'Rs. 400', 'name':'Qmobile Noir X29' }, \
'2': {'price':'4500' ,'discounted_price':'4500', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'QMobile Noir X33'}, \
'3': {'price':'7800' ,'discounted_price':'7800', 'points_cost': '5000', 'discount':'Rs. 680', 'name':'QMobile Noir i8i'}, \
'4': {'price':'6570' ,'discounted_price':'6570', 'points_cost': '5000', 'discount':'Rs. 730', 'name':'QMobile Noir i6 Metal One'}, \
'5': {'price':'8100','discounted_price':'8100', 'points_cost': '5000', 'discount':'Rs. 900', 'name':'Samsung J1 Mini Prime'}, \
'6': {'price':'9630','discounted_price':'9630', 'points_cost': '5000', 'discount':'Rs. 1070', 'name':'QMobile Noir S6'}, \
'7': {'price':'7000','discounted_price':'6500', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'QMobile Noir 4G LT550'}, \
'8': {'price':'8500','discounted_price':'8500', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'Infinix Smart'}, \
'9': {'price':'8840','discounted_price':'8840', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'Huawei Y3 3G 2017'}, \
'10': {'price':'9630','discounted_price':'9630', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'QMobile Energy X2'}, \
'11': {'price':'13800','discounted_price':'13800', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'Samsung Galaxy Grand Prime Plus'}, \
'12': {'price':'18900','discounted_price':'18900', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'Samsung J5 Prime'}, \
'13': {'price':'5500','discounted_price':'5500', 'points_cost': '5000', 'discount':'Rs. 0', 'name':'QMobile Noir X36'}, \
'14': {'price':'11300','discounted_price':'11300', 'points_cost': '5000', 'discount':'Rs. 0', 'name':'Huawei Ascend G700'}, \
'15': {'price':'11000','discounted_price':'11000', 'points_cost': '5000', 'discount':'Rs. 0', 'name':'Nokia 2'}, \
}#REMOVE
###############################################################################################################
# '2' DELIBERATELY SKIPPED DUE TO LEGACY REASONS
ZODIAC = {'1':'None','3':'Aquarius','4':'Pisces','5':'Aries','6':'Taurus','7':'Gemini','8':'Cancer','9':'Leo','10':'Virgo',\
'11':'Libra','12':'Scorpio','13':'Sagittarius','14':'Capricorn'}
###############################################################################################################
SEGMENT_STARTING_TIME = 1560425907	# starting time of user segment analysis
SEGMENT_STARTING_USER_ID = 1979518# starting user ID of user segment analysis
PROJ_ZUCK_STARTING_USER_ID = 1975000

"""
TYPES OF USER ACTIVITIES:
note: we only log authenticated users. Non-auth users are not logged at the moment

'.u' is added if the user is attempting the action while 'unverified'
'.i' is added if the user is attempting an 'invalid' action (while verified)

A1 - loaded home text history 
A2 - loaded own about page
A3 - loaded photos history page
A4 - loaded photos trending history page
A1.u - loaded home text history (while unverified)
A2.u - loaded about page (while unverified)
A3.u - loaded photos history page (while unverified)
A4.u - loaded photos trending history page (while unverified)

D - visited edit profile page
D.u - visited edit profile page (while unverified)
D.i - profile changes were invalid (whether it was an image change, bio change, etc)
D.u.i - profile changes were invalid (whether it was an image change, bio change, etc), and the user was unverified (doesn't matter - they're allowed to change their profiles)
D1 - new avatar uploaded
D1.u - new avatar uploaded (while unverified)
D2 - bio has been updated
D2.u - bio has been updated (while unverified)

H - landing on 'home' page
H.u - landing on 'home' page (while unverified)

B - landing on 'best photos'
B.u - landing on 'best photos' (while unverified)

C - comment (tabsra) from comment page
C.u - comment (tabsra) attempt from comment page (while unverified)
C.i - comment (tabsra) attempt from comment page (invalid)

C1 - landing on comment (tabsra) page
C1.u - landing on comment (tabsra) page while unverified

L - publicreply (jawab) from jawab page
L.u - publicreply (jawab) attempted from jawab page (while unverified)
L.i - publicreply (jawab) attempted from jawab page (invalid)

L1 - landing on publicreply (jawab) page
L1.u - landing on publicreply (jawab) page (while unverified)

F - landing on 'fresh photos'
F.u - landing on 'fresh photos' while unverified

T - landing on 'topic'
T.u - landing on 'topic' (while unverified)

I3 - inline 'home' text jawab
I4 - inline 'topic' text jawab
I6 - inline 'home' photo tabsra
I7 - inline 'fresh-photos' tabsra
I8 - inline 'best-photos' tabsra
I3.u - inline 'home' text jawab attempt (while unverified)
I4.u - inline 'topic' text jawab (while unverified)
I6.u - inline 'home' photo tabsra attempt (while unverified)
I7.u - inline 'fresh-photos' tabsra attempt (while unverified)
I8.u - inline 'best-photos' tabsra attempt (while unverified)
I3.i - inline 'home' text jawab attempt (invalid)
I4.i - inline 'topic' text jawab (invalid)
I6.i - inline 'home' photo tabsra attempt (invalid)
I7.i - inline 'fresh-photos' tabsra attempt (invalid)
I8.i - inline 'best-photos' tabsra attempt (invalid)

X - text public post submitted successfully
X.t - text public post w/ topic submitted successfully
X.u - text public post attempt (while unverified)
X.i - text public post attempt (invalid)

X1 - landed on the page from where user can submit a text public post
X1.u - landed on the page from where user can submit a text public post (while unverified)

X2 - landed on page where one can select 'text' or 'photos' for sharing
X2.u - landed on page where one can select 'text' or 'photos' for sharing (while unverified)

X3 - landed on sharing help page
X3.u - landed on sharing help page (while unverified)

P - photo public post submitted successfully
P.u - photo public post uploading attempt (while unverified)
P.i - photo public post uploading attempt (invalid)

P1 - landed on the page from where user can submit a photo public post
P1.u - landed on the page from where user can submit a photo public post (while unverified)

N - became a fan
N1 - unfan
N.u - fanning attempt (while unverified)

S1 - single notification response for a public text post (i.e. jawab via single notif)
S2 - single notification response for a public photo post (i.e. a tabsra via single notif)
S3 - single notification response for private mehfil (i.e. replying to private mehfil via single notif)
S4 - single notification response for public mehfil (i.e. replying to public mehfil via single notif) 
S5 - single notification response for 1on1 (i.e. replying to 1on1 via single notif)
S5.e - single notification error response for 1on1 (i.e. replying to 1on1 via single notif)
S6 - single notification response for photo comment (i.e. writing a photo comment under an img via single notif) 
S6.u - single notification photo comment (while unverified)
S7 - single notification text jawab (i.e. writing a text jawab via single notif) 
S7.u - single notification text jawab (while unverified)

S3.i - single notification invalid response for private mehfil (i.e. replying to private mehfil via single notif)
S4.i - single notification invalid response for public mehfil (i.e. replying to public mehfil via single notif) 
S5.i - single notification invalid response for 1on1 (i.e. replying to 1on1 via single notif) 
S6.i - single notification invalid response for photo comment (i.e. writing a photo comment under an img via single notif)
S7.i - single notification invalid response for text jawab (i.e. writing a text jawab via single notif)

M - matka loaded
M.u - matka loaded (while unverified)

M3 - matka reply to private mehfil
M4 - matka reply to public mehfil
M5 - matka reply to 1on1
M5.e - matka error reply to 1on1
M6 - matka photo comment
M6.u - matka photo comment (while unverified)
M7 - matka home jawab
M7.u - matka home jawab (while unverified - e.g. trying to reply to 'welcome' message)
M8 - likes history loaded
M8.u - likes history loaded (while unverified)

M3.i - matka invalid reply to private mehfil
M4.i - matka invalid reply to public mehfil
M5.i - matka invalid reply to 1on1
M6.i - matka invalid photo comment
M7.i - matka invalid home jawab

V - voted on an object
V.u - voted on an object (while unverified)

V1 - selected 'var1' in the tutorial
V2 - selected 'var2' in the tutorial
V3 - selected 'var3' in the tutorial
V4 - selected 'var4' in the tutorial

G1 - loaded list of joined mehfils
G2 - loaded mehfil invite list
G3 - loaded mehfil creation page

R - joined private mehfil
R1 - visited joined private mehfil
R2 - visited unjoined private mehfil
R3 - created private mehfil
R.u - attempted to join private mehfil (while unverified)
R1.u - visited joined private mehfil (while unverified)
R2.u - visited unjoined private mehfil (while unverified)
R3.u - attempted to create a private mehfil (while unverified)
R3.i - attempted to create a private mehfil (invalid)

G1.u - loaded list of joined mehfils (while unverified)
G2.u - loaded mehfil invite list (while unverified)
G3.u - loaded mehfil creation page (while unverified)

U - joined public mehfil
U0 - entered unjoined public mehfil rules screen
U1 - visited joined public mehfil
U2 - visited unjoined public mehfil
U3 - created public mehfil
U4 - visited popular mehfil list
U.u - attempted to join public mehfil (while unverified)
U1.u - visited joined public mehfil (while unverified)
U2.u - visited unjoined public mehfil (while unverified)
U3.u - attempted to create a public mehfil (while unverified)
U3.i - attempted to create a public mehfil (invalid)
U4.u - visited popular mehfil list (while unverified)

W0 - exited a 1on1
W1 - posted in 1on1
W2 - posted in private mehfil
W3 - posted in public mehfil
W4 - posted in a topic (from within a topic)

W1.u - attempted to post in 1on1 (while unverified)
W2.u - attempted to post in private mehfil (while unverified)
W3.u - attempted to post in public mehfil (while unverified)
W4.u - attempted to post in a topic from within a topic (while unverified)

W1.i - attempted to post in 1on1 (invalid)
W2.i - attempted to post in private mehfil (invalid)
W3.i - attempted to post in pubic mehfil (invalid)
W4.i - attempted to post in a topic from within a topic (invalid)
W4.s - subscribed successfully to a topic

O - loaded online page
O.u - loaded online page (while unverified)

Y.v - visited a joined 1on1
Y.s - visited a joined 1on1's settings

Y - sent 1on1 invite successfully
Y.d - declined 1on1 invite successfully
Y.a - accepted 1on1 invite successfully
Y1- initiated 1on1 invite (i.e. first screen)
Y3 - loaded 1on1 invites received screen
Y4 - loaded 1on1 invites sent screen
Y5 - loaded 1on1 list screen
Y1.u - attempted to send 1on1 invite (while unverified)
Y2.u - attempted to change 1on1 invite privacy setting (while unverified)
Y3.u - attempted to load 1on1 invites received screen (while unverified)
Y4.u - attempted to load 1on1 invites sent screen (while unverified)
Y5.u - attempted to load 1on1 list screen (while unverified). This never displays, instead user is redirected to a 'verify-now' prompt

Z1 - visited 'help' page
Z1.u - visited 'help' page (while unverified)
Z2 - visited 'rules' page
Z2.u - visited 'rules' page (while unverified)
Z3 - visited website 'about' page
Z3.u - visited website 'about' page (while unverified)
Z4 - visited 'search' page
Z4.u - visited 'search' page (while unverified)
Z5 - visited 'topic list' page
Z5.u - visited 'topic list' page (while unverified)
Z6 - visited 'fan list'
Z6.u - visited 'fan list' (while unverified)
Z7 - visited 'star list'
Z7.u - visited 'star list' (while unverified)
Z8 - visited photo detail page
Z8.u - visited photo detail page (while unverified)
Z9 - visited 'top photo stars' page
Z9.u - visited 'top photo stars' page (while unverified)
Z10 - visited help page on how to get an image into trending
Z10.u - visited help page on how to get an image into trending (while unverified)
Z11 - landed on 1st page of pvp blocking
Z11.u - landed on 1st page of pvp blocking (while unverified)
Z12 - landed on 1st page of 'content reporting'
Z12.u - landed on 1st page of 'content reporting' (while unverified)

Z - verified successfully
Z.u - visited verification page where one inputs their mobile number (i.e. verification_button.html)

J - blocking another user successfully (pvp)
J.u - blocking another user successfully (pvp), while unverified

K - reported content

F - searched a username, and some results were obtained
F.u - searched a username, and some results were obtained (while unverified)
F.i - searched a username (but no results obtained)
F.u.i - searched a username (but no results obtained - while unverified)

E - public image shared in a 1on1, successfully
E.i - invalid attempt at sharing a public image in a 1on1 (because no 1on1s selected, or none of the selected 1on1s have given img sharing perm)

E1 - landed on "share image in 1on1" 1st page
E1.u - landed on "share image in 1on1" 1st page (while unverified)

Q - sent welcome 'mithai' to user
Q.u - sent welcome 'mithai' to user (while unverified)

Q1 - skipped 'jawab' single notification
Q2 - skipped 'tabsra' single notification
Q3 - skipped 'mehfil' single notification
Q4 - skipped '1on1' single notification

Q1.u - skipped 'jawab' single notification (while unverified)
Q2.u - skipped 'tabsra' single notification (while unverified)
Q3.u - skipped 'mehfil' single notification (while unverified)
Q4.u - skipped '1on1' single notification (while unverified)

"""