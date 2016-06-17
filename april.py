from datetime import time as time_object

#APRIL
prefajr_least_before = time_object(hour=0, minute=0)
prefajr_most_before = time_object(hour=4, minute=21) #i.e. between  and 
fajr_least_before = time_object(hour=4, minute=21) 
fajr_most_before = time_object(hour=6, minute=24)
prezuhr_least_before = time_object(hour=6, minute=24)
prezuhr_most_before = time_object(hour=12, minute=15)
zuhr_least_before = time_object(hour=12, minute=15)
zuhr_most_before = time_object(hour=14, minute=15)
preasr_least_before = time_object(hour=14, minute=15)
preasr_most_before = time_object(hour=15, minute=40)
asr_least_before = time_object(hour=15, minute=40)
asr_most_before = time_object(hour=17, minute=15)
premaghrib_least_before = time_object(hour=17, minute=15)
premaghrib_most_before = time_object(hour=18, minute=25)
maghrib_least_before = time_object(hour=18, minute=25)
maghrib_most_before = time_object(hour=19, minute=59)
preisha_least_before = time_object(hour=19, minute=59)
preisha_most_before = time_object(hour=20, minute=16)
isha_least_before = time_object(hour=20, minute=16)
isha_most_before = time_object(hour=23, minute=59)

#goes to 
prefajr_least_after = time_object(hour=0, minute=0)
prefajr_most_after = time_object(hour=3, minute=36) 
fajr_least_after = time_object(hour=3, minute=36)
fajr_most_after = time_object(hour=5, minute=36)
prezuhr_least_after = time_object(hour=5, minute=36)
prezuhr_most_after = time_object(hour=12, minute=0)
zuhr_least_after = time_object(hour=12, minute=0)
zuhr_most_after = time_object(hour=14, minute=20) #i.e. between  and 
preasr_least_after = time_object(hour=14, minute=20)
preasr_most_after = time_object(hour=15, minute=45)
asr_least_after = time_object(hour=15, minute=45)
asr_most_after = time_object(hour=17, minute=30)
premaghrib_least_after = time_object(hour=17, minute=30)
premaghrib_most_after = time_object(hour=18, minute=49)
maghrib_least_after = time_object(hour=18, minute=49)
maghrib_most_after = time_object(hour=20, minute=30)
preisha_least_after = time_object(hour=20, minute=30)
preisha_most_after = time_object(hour=20, minute=35)
isha_least_after = time_object(hour=20, minute=35)
isha_most_after = time_object(hour=23, minute=59)