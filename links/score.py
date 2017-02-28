VOTE_TEXT = {'1':'<span class="cg" style="font-size:80%;"> ne barri si <b>jhappi</b> di</span><br>',\
'-1':'<span class="cr" style="font-size:80%;"> ne bharey bazar mein <b>chupair</b> mari</span><br>',\
'2': '<span class="cg" style="font-size:80%;"> ne zordar <b>jhappi</b> di <b>(+50)</b></span><br>',\
'-2': '<span class="cr" style="font-size:80%;"> ne <b>chupair</b> mr mr ke nani yad kra di <b>(-50)</b></span><br>',\
'3': '<span class="cg" style="font-size:80%;"> ko ye photo <b>zabrdast</b> lagi</span><br>',\
'-3': '<span class="cr" style="font-size:80%;"> ko ye photo <b>bekaar</b> lagi</span><br>',\
'4':'<span class="cg" style="font-size:80%;"> ne iski shot pe <b>taliyan</b> bajaien</span><br>',\
'-4':'<span class="cr" style="font-size:80%;"> ne isko ghuma ke <b>balla</b> mara</span><br>',\
'5': '<span class="cg" style="font-size:80%;"> ne iske <b>six</b> pe chalangein lagaien <b>(+50)</b></span><br>',\
'-5': '<span class="cr" style="font-size:80%;"> ne isko <b>andey</b> pe out kr diya <b>(-50)</b></span><br>'}
UPVOTE = 3
SUPER_UPVOTE = 50
DOWNVOTE = -3
SUPER_DOWNVOTE = -50
###############################################################################################################
PRIVATE_GROUP_COST = 500 # cost of buying a private group
PUBLIC_GROUP_COST = 5000 # cost of buying a public group
PUBLIC_GROUP_MESSAGE = 2 # score for messaging in public group
PRIVATE_GROUP_MESSAGE = 1 # score for messaging in privte group
PUBLICREPLY = 2 #score for leaving publicreply on a home 'link'
###############################################################################################################
UPLOAD_PHOTO_REQ = 30 #score below which you're not allowed photo uploads
PHOTO_HOT_SCORE_REQ = 9 #aggregated 'visible_score' over previous 5 photos, above which your photo appears on home
###############################################################################################################
CRICKET_SUPPORT_STARTING_POINT = 15 #score at which PSL support options open up
CRICKET_TEAM_NAMES = {'Lahore Qalandars':'Qalandars','Islamabad United':'United',\
'Karachi Kings':'Kings','Peshawar Zalmi':'Zalmi','Quetta Gladiators':'Gladiators',\
'North':'North','Northwest':'Northwest'}
CRICKET_TEAM_IDS = {'Lahore Qalandars':'5','Islamabad United':'8','Karachi Kings':'3',\
'Peshawar Zalmi':'4','Quetta Gladiators':'7','misc':'9','North':'9','Northwest':'9'}
CRICKET_COLOR_CLASSES = {'Lahore Qalandars':'qal','Islamabad United':'uni',\
'Karachi Kings':'kng','Peshawar Zalmi':'zal','Quetta Gladiators':'gld','misc':'bcb',\
'North':'bco','Northwest':'bco'}