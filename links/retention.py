# from redis4 import 
from django.contrib.auth.models import User
from redis4 import retrieve_retention_ids, retrieve_retention_data
import csv
from django.shortcuts import render#, redirect

def export_logged_users_and_times(request,*args,**kwargs):
	if request.user.username == "mhb11":
		user_ids = retrieve_retention_ids()
		# retention_data below contains a list of tuples, containing user id, and a list of all the times that user showed up at
		retention_data = retrieve_retention_data(user_ids)
		with open('retention_data.csv','wb') as f:
			wtr = csv.writer(f, delimiter=',')
			wtr.writerow(['id','visit_unix_time']) # writing the columns
			for tup in retention_data:
				for time in tup[1]:
					to_write = [tup[0],time]
					wtr.writerows([to_write])
		return render(request,"contact.html",{})
	else:
		return render(request,"404.html",{})


	"""
	RETRIEVE "date_joined" FROM auth_user (GET IT FOR ALL USERS)
	Get this directly via the following:
	1) Log into PSQL
	2) Run the following (takes 1-2 seconds):
	\COPY (select id, date_joined from auth_user) to '/home/data/join_dates.csv' DELIMITER ',' CSV HEADER;
	3) use scp to transfer file locally:
	scp -P <port> <username>@<hostname>:/home/data/join_dates.csv .
	"""
	
