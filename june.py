from datetime import time as time_object

#JUNE
prefajr_least_before = time_object(hour=0, minute=0)
prefajr_most_before = time_object(hour=3, minute=2) #i.e. between 00:00 and 03:02
fajr_least_before = time_object(hour=3, minute=2) 
fajr_most_before = time_object(hour=5, minute=45) #i.e. between 03:02 and 05:45
prezuhr_least_before = time_object(hour=5, minute=45)
prezuhr_most_before = time_object(hour=12, minute=0) #i.e. between 05:45 and 12:00
zuhr_least_before = time_object(hour=12, minute=0)
zuhr_most_before = time_object(hour=14, minute=45) #i.e. between 12:00 and 14:45
preasr_least_before = time_object(hour=14, minute=45)
preasr_most_before = time_object(hour=15, minute=49) #i.e. between 14:45 and 15:49
asr_least_before = time_object(hour=15, minute=49)
asr_most_before = time_object(hour=17, minute=20) #i.e. between 12:00 and 17:00
premaghrib_least_before = time_object(hour=17, minute=20)
premaghrib_most_before = time_object(hour=19, minute=3) #i.e. between 17:00 and 19:03
maghrib_least_before = time_object(hour=19, minute=3)
maghrib_most_before = time_object(hour=20, minute=10) #i.e. between 19:03 and 20:10
preisha_least_before = time_object(hour=20, minute=10)
preisha_most_before = time_object(hour=21, minute=0) #i.e. between 20:10 and 21:00
isha_least_before = time_object(hour=21, minute=0)
isha_most_before = time_object(hour=23, minute=59) #i.e. between 21:00 and 23:59

#goes to 
prefajr_least_after = time_object(hour=0, minute=0)
prefajr_most_after = time_object(hour=3, minute=2) 
fajr_least_after = time_object(hour=3, minute=2)
fajr_most_after = time_object(hour=5, minute=45)
prezuhr_least_after = time_object(hour=5, minute=45)
prezuhr_most_after = time_object(hour=12, minute=6)
zuhr_least_after = time_object(hour=12, minute=6)
zuhr_most_after = time_object(hour=14, minute=55) #i.e. between 12:06 and 14:56
preasr_least_after = time_object(hour=14, minute=55)
preasr_most_after = time_object(hour=15, minute=55)
asr_least_after = time_object(hour=15, minute=55)
asr_most_after = time_object(hour=17, minute=35)
premaghrib_least_after = time_object(hour=17, minute=35)
premaghrib_most_after = time_object(hour=19, minute=23)
maghrib_least_after = time_object(hour=19, minute=23)
maghrib_most_after = time_object(hour=20, minute=20)
preisha_least_after = time_object(hour=20, minute=20)
preisha_most_after = time_object(hour=21, minute=11)
isha_least_after = time_object(hour=21, minute=11)
isha_most_after = time_object(hour=23, minute=59)