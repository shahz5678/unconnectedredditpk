import csv
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.models import User
from redis8 import report_section_wise_retention, retrieve_all_logged_actions#, retention_clean_up
from redis4 import retrieve_retention_ids, retrieve_retention_data
from retention_experiments import EXPERIMENTS_CURRENTLY_BEING_RUN
from redis3 import exact_date
from redis7 import in_defenders

def export_logged_users_and_times(request,*args,**kwargs):
	raise Http404("This doesn't exist")
	# if request.user.username == "mhb11":
	# 	user_ids = retrieve_retention_ids()
	# 	# retention_data below contains a list of tuples, containing user id, and a list of all the times that user showed up at
	# 	retention_data = retrieve_retention_data(user_ids)
	# 	with open('retention_data.csv','wb') as f:
	# 		wtr = csv.writer(f, delimiter=',')
	# 		wtr.writerow(['id','visit_unix_time']) # writing the columns
	# 		for tup in retention_data:
	# 			for time in tup[1]:
	# 				to_write = [tup[0],time]
	# 				wtr.writerows([to_write])
	# 	return render(request,"contact.html",{})
	# else:
	# 	return render(request,"404.html",{})


	"""
	RETRIEVE "date_joined" FROM auth_user (GET IT FOR ALL USERS)
	Get this directly via the following:
	1) Log into PSQL
	2) Run the following (takes 1-2 seconds):
	\COPY (select id, date_joined from auth_user) to '/home/data/join_dates.csv' DELIMITER ',' CSV HEADER;
	3) use scp to transfer file locally:
	scp -P <port> <username>@<hostname>:/home/data/join_dates.csv .
	"""

#################################################

def display_retention(request,section):
	"""
	Displays retention of any ongoing experiment
	"""
	raise Http404("This doesn't exist")
	# is_defender, is_super_defender = in_defenders(request.user.id, return_super_status=True)
	# if is_super_defender and section in EXPERIMENTS_CURRENTLY_BEING_RUN:
	# 	return render(request,"retention/section_retention.html",{'section':section,'retention_data':report_section_wise_retention(section)})
	# else:
	# 	# such a section does not exist
	# 	raise Http404("This doesn't exist")
	
def reset_retention_counters(request):
	"""
	"""
	raise Http404("This doesn't exist")
	# retention_clean_up()


def export_logged_actions(request):
	"""
	Exports all logged actions into a CSV file for analysis
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		data_to_write_to_csv = retrieve_all_logged_actions()# list of lists (where each list is a list of dictionaries)
		if data_to_write_to_csv:
			import csv
			filename = 'action_data.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				#  payload = str(user_id)+":"+user_age+":"+action_categ+":"+action_sub_categ+":"+action_liq+":"+str(time_of_action)
				columns = ["voter ID","hours since segment init","parent category","sub category","action liquidity","time of logging"]
				wtr.writerow(columns)
				for action_data in data_to_write_to_csv:
					data_list = action_data.split(":")
					user_id, hrs_since_segment_init, action_categ, action_sub_categ, liquidity, time_of_action = data_list[0],\
					data_list[1],data_list[2],data_list[3], data_list[4], data_list[5]
					to_write = [user_id, hrs_since_segment_init, action_categ, action_sub_categ, liquidity, exact_date(float(time_of_action))]
					wtr.writerows([to_write])
	raise Http404("Completed logging ;)")


