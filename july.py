from datetime import time as time_object

#JULY
prefajr_least_before = time_object(hour=0, minute=0)
prefajr_most_before = time_object(hour=3, minute=2) #i.e. between  and 
fajr_least_before = time_object(hour=3, minute=2) 
fajr_most_before = time_object(hour=5, minute=45)
prezuhr_least_before = time_object(hour=5, minute=45)
prezuhr_most_before = time_object(hour=12, minute=6)
zuhr_least_before = time_object(hour=12, minute=6)
zuhr_most_before = time_object(hour=14, minute=55)
preasr_least_before = time_object(hour=14, minute=55)
preasr_most_before = time_object(hour=15, minute=57)
asr_least_before = time_object(hour=15, minute=57)
asr_most_before = time_object(hour=17, minute=45)
premaghrib_least_before = time_object(hour=17, minute=45)
premaghrib_most_before = time_object(hour=19, minute=23)
maghrib_least_before = time_object(hour=19, minute=25)
maghrib_most_before = time_object(hour=20, minute=35)
preisha_least_before = time_object(hour=20, minute=35)
preisha_most_before = time_object(hour=21, minute=13)
isha_least_before = time_object(hour=21, minute=13)
isha_most_before = time_object(hour=23, minute=59)

#goes to 
prefajr_least_after = time_object(hour=0, minute=0)
prefajr_most_after = time_object(hour=3, minute=31) 
fajr_least_after = time_object(hour=3, minute=31)
fajr_most_after = time_object(hour=6, minute=0)
prezuhr_least_after = time_object(hour=6, minute=0)
prezuhr_most_after = time_object(hour=12, minute=9)
zuhr_least_after = time_object(hour=12, minute=9)
zuhr_most_after = time_object(hour=14, minute=59) #i.e. between  and 
preasr_least_after = time_object(hour=14, minute=59)
preasr_most_after = time_object(hour=15, minute=59)
asr_least_after = time_object(hour=15, minute=59)
asr_most_after = time_object(hour=17, minute=55)
premaghrib_least_after = time_object(hour=17, minute=5)
premaghrib_most_after = time_object(hour=19, minute=8)
maghrib_least_after = time_object(hour=19, minute=8)
maghrib_most_after = time_object(hour=20, minute=25)
preisha_least_after = time_object(hour=20, minute=25)
preisha_most_after = time_object(hour=20, minute=50)
isha_least_after = time_object(hour=20, minute=50)
isha_most_after = time_object(hour=23, minute=59)