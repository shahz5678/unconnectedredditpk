THUMB_HEIGHT = 38
###############################################################################################################
VOTE_TEXT = {'1':'<span style="font-size:80%;color:#009940;"> ne barri si <b>jhappi</b> di</span><br>',\
'-1':'<span style="font-size:80%;color:#F4511E;"> ne bharey bazar mein <b>chupair</b> mari</span><br>',\
'2': '<span style="font-size:80%;color:#009940;"> ne zordar <b>jhappi</b> di <b>(+20)</b></span><br>',\
'-2': '<span style="font-size:80%;color:#F4511E;"> ne <b>chupair</b> mr mr ke nani yad kra di <b>(-20)</b></span><br>',\
'3': '<span style="font-size:80%;color:#009940;"> ko ye photo <b>zabrdast</b> lagi</span><br>',\
'-3': '<span style="font-size:80%;color:#F4511E;"> ko ye photo <b>bekaar</b> lagi</span><br>',\
'4':'<span style="font-size:80%;color:#009940;"> ne iski shot pe <b>taliyan</b> bajaien</span><br>',\
'-4':'<span style="font-size:80%;color:#F4511E;"> ne isko ghuma ke <b>balla</b> mara</span><br>',\
'5': '<span style="font-size:80%;color:#009940;"> ne iske <b>six</b> pe chalangein lagaien <b>(+20)</b></span><br>',\
'-5': '<span style="font-size:80%;color:#F4511E;"> ne isko <b>andey</b> pe out kr diya <b>(-20)</b></span><br>'}
UPVOTE = 3
SUPER_UPVOTE = 20
DOWNVOTE = -3
SUPER_DOWNVOTE = -20
###############################################################################################################
PRIVATE_GROUP_COST = 500 # cost of buying a private group
PUBLIC_GROUP_COST = 5000 # cost of buying a public group
PUBLIC_GROUP_MESSAGE = 2 # score for messaging in public group
PRIVATE_GROUP_MESSAGE = 1 # score for messaging in privte group
PUBLICREPLY = 2 #score for leaving publicreply on a home 'link'
###############################################################################################################
UPLOAD_PHOTO_REQ = 30 #score below which you're not allowed photo uploads
PHOTO_HOT_SCORE_REQ = 6 #aggregated 'visible_score' over previous 5 photos, above which your photo appears on home
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
SEARCH_FEATURE_THRESHOLD = 100
PERMANENT_RESIDENT_SCORE = 300
PHOTO_REPORT_PROMPT = {'1':'Photo buhut gandi hai','2':'Photo mazhabi fasad phela rahi hai',\
'3':'Photo mein buhut ziyada tashadud hai','4':'Photo takhreeb karoon ki wakalat kr rahi hai',\
'5':'Photo pe fake accounts ke zariye vote daley gaye hain','6':'Kuch aur masla hai'}
PHOTO_CASE_COMPLETION_BONUS = 6
###############################################################################################################
GIBBERISH_PUNISHMENT_MULTIPLIER = 5
###############################################################################################################
#Ecomm cities
CITIES = ["Rawalpindi","Islamabad"]
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
NUMBER_VERIFICATION_THRESHOLD = 10
NUMBER_VERIFICATION_BONUS = 500
###############################################################################################################
PW = 'F1l2O3c4C5i6N7a8U9c1I2n3I4h5I6l7I8p9I1l2I3f4I5c6A7t8I9o1N2'
###############################################################################################################
PERSONAL_GROUP_ERR = {'too_high':'Ye foto buhut lambi hai, koi aur chunein',\
'mismatch':'Rabta munqata ho gaya, phir se karien','generic':'Internet ka rabta munqata ho gaya, phir se karien'}
PERSONAL_GROUP_DEFAULT_SMS_TXT = ' ne apko Damadam ki private chat mein bulaya'
EXTRA_PADDING = 20 #used to adjust image sizes in cases where CSS uses box-sizing:border-box property
PERSONAL_GROUP_SAVE_MSGS = {'err2':'Ye chat mita diye janey ki waja se save nahi ho saki',\
'err3':'Ye chat hide honay ki waja se save nahi ho saki','err4':'Ye chat apkey save karney se pehlay delete ho geyi',\
'err5':'Ap is chat ko save kar sakein ge ','err1':'Ye chat save nahi ho sakti','msg1':'Chat save kar di geyi',\
'err6':'Ye chat save karney ke liye apni pichli saved chat mein se kuch delete karein',\
'err7':'Ye chat pehlay bhi save ki ja chuki hai, dubara nahi ho sakti',\
'err8':'Kharabi ho geyi, phir se koshish karein','err9':'Ap ko ye chat save karney ki ijazat nahi'}
###############################################################################################################
# helps in setting TTL on rate limits set on abusive users. Each key defines 'level' of offense, values are ttl
BAN_REASON = {'flooding':'tez tez likhna (flooding or spamming)'}
RATELIMIT_TTL = {'1':60*7,'2':60*30,'3':60*60*2,'4':60*60*8,'5':60*60*24,'6':60*60*24*3,'7':60*60*24*7,'8':60*60*24*30}
SUPER_FLOODING_THRESHOLD = 3 # 3 seconds on avg between multiple sentences
FLOODING_THRESHOLD = 5 # 5 seconds on avg between multiple sentences
SHORT_MESSAGES_ALWD = 4