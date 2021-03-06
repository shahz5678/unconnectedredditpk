from datetime import time as time_object

#JANUARY
prefajr_least_before = time_object(hour=0, minute=0)
prefajr_most_before = time_object(hour=5, minute=42) #i.e. between  and 
fajr_least_before = time_object(hour=5, minute=42) 
fajr_most_before = time_object(hour=6, minute=59)
prezuhr_least_before = time_object(hour=6, minute=59)
prezuhr_most_before = time_object(hour=12, minute=30)
zuhr_least_before = time_object(hour=12, minute=30)
zuhr_most_before = time_object(hour=14, minute=15)
preasr_least_before = time_object(hour=14, minute=15)
preasr_most_before = time_object(hour=14, minute=41)
asr_least_before = time_object(hour=14, minute=41)
asr_most_before = time_object(hour=16, minute=29)
premaghrib_least_before = time_object(hour=16, minute=29)
premaghrib_most_before = time_object(hour=17, minute=0)
maghrib_least_before = time_object(hour=17, minute=0)
maghrib_most_before = time_object(hour=18, minute=15)
preisha_least_before = time_object(hour=18, minute=15)
preisha_most_before = time_object(hour=18, minute=45)
isha_least_before = time_object(hour=18, minute=45)
isha_most_before = time_object(hour=23, minute=59)

#goes to 
prefajr_least_after = time_object(hour=0, minute=0)
prefajr_most_after = time_object(hour=5, minute=42) 
fajr_least_after = time_object(hour=5, minute=42)
fajr_most_after = time_object(hour=6, minute=55)
prezuhr_least_after = time_object(hour=6, minute=55)
prezuhr_most_after = time_object(hour=12, minute=41)
zuhr_least_after = time_object(hour=12, minute=41)
zuhr_most_after = time_object(hour=14, minute=26) #i.e. between  and 
preasr_least_after = time_object(hour=14, minute=26)
preasr_most_after = time_object(hour=14, minute=50)
asr_least_after = time_object(hour=14, minute=50)
asr_most_after = time_object(hour=17, minute=5)
premaghrib_least_after = time_object(hour=17, minute=5)
premaghrib_most_after = time_object(hour=17, minute=30)
maghrib_least_after = time_object(hour=17, minute=30)
maghrib_most_after = time_object(hour=19, minute=10)
preisha_least_after = time_object(hour=19, minute=10)
preisha_most_after = time_object(hour=19, minute=30)
isha_least_after = time_object(hour=19, minute=30)
isha_most_after = time_object(hour=23, minute=59)