import redis, time
import ujson as json
from collections import defaultdict
from retention_experiments import EXP
from redis3 import exact_date
from location import REDLOC8

ONE_HOUR= 3600# in seconds
TWO_WEEKS = 1209600# in seconds

COHORT_TIME_LENGTH = 86400#i.e. set to '1 day' (in secs)

USER_ACTION_STORE = 'uas'#global sorted set that logs all post requests by users (useful for segment analysis)
GLOBAL_EXP_USERS = 'geu'#global sorted set containing all users who're part of an experiment
UVAR = 'u:'# holds an identifier for every user, used to identify the said user within the said variation (useful for retention analysis)

d1 = {0:'d0',1:'d1',2:'d2',3:'d3',4:'d4',5:'d5',6:'d6',7:'d7',8:'d8',9:'d9',10:'d10',11:'d11',12:'d12'}
DAY_NAMES = defaultdict(lambda: 'd13+', d1)# populates DAY_NAMES by d1, and then uses 'd13+' as default value ('d13+' means 'd13 or more' - where d13 is included)

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC8, db=0)

def retrieve_cohort(time_now):
	"""
	Determine what cohort_id the current time falls into

	It divides (seconds since epoch) by (seconds in one day). That gives days since epoch.
	Next, it takes the mathematical floor of 'days since epoch' to return the cohort_id.
	Example values can be 18019, 18020, 18021, etc
	"""
	return int(time_now/COHORT_TIME_LENGTH)


def set_variation_wise_retention(user_id, which_var=None):
	"""
	Setting cohort-wise daily retention levels for visitors coming into a given experimental variation (defined by 'which_var' parameter)

	This enables us to extract 'd1'-retention type metrics for the said experiment
	Experiments could be first-time visitors coming into 'trending fotos', 'home', '1_on_1', etc
	"""
	time_now, user_id = time.time(), str(user_id)
	my_server = redis.Redis(connection_pool=POOL)
	variation = my_server.get(UVAR+user_id)
	if variation:
		which_var = variation
	#######################################################
	# only proceed if user is part of any variation, otherwise ignore the user entirely (they're not part of any experimental variation)
	if which_var:

		# the cohort active right now
		cohort_id_now = retrieve_cohort(time_now)

		# the cohort this user originally belonged to
		cohort_id = my_server.zscore(GLOBAL_EXP_USERS,user_id)

		# if user_registration_time:
		if cohort_id:
			
			cohort_id = int(cohort_id)

			# the user of variation 'which_var' is returning on 'which_day'
			which_day = DAY_NAMES[cohort_id_now-cohort_id]

			if which_day != 'd13+' and not my_server.exists(EXP[which_var+'rl']+user_id):

				# increment 'dN' (e.g. d1, d5, d11, etc) of this particular time_cohort
				my_server.hincrby(EXP[which_var+'r']+str(cohort_id), which_day, amount=1)

				# rate limit user_id from being 'seen again' in this experiment (for the next COHORT_TIME_LENGTH - ie. 24 hours)
				my_server.setex(EXP[which_var+'rl']+user_id, '1', COHORT_TIME_LENGTH)
		else:
			pipeline1 = my_server.pipeline()

			# user is 'new', so 'register' them into the current cohort
			pipeline1.zadd(GLOBAL_EXP_USERS,user_id,cohort_id_now)

			# next, increment 'd0' of the current cohort (and set its expiry time)
			cohort = EXP[which_var+'r']+str(cohort_id_now)
			pipeline1.hincrby(cohort,'d0',amount=1)# counting as having hit 'd0'
			pipeline1.expire(cohort,TWO_WEEKS)# remove this cohort after TWO_WEEKS, since we only care about the previous 13 cohorts (i.e. days)

			# next, rate limit user_id from being used again for the next 'COHORT_TIME_LENGTH' (or 24 hours)
			pipeline1.setex(EXP[which_var+'rl']+user_id,'1',COHORT_TIME_LENGTH)# rate limit till: 'COHORT_TIME_LENGTH' (or 24 hrs) from the time of registration

			# finally, save the variation the user is a part of for retrieval later
			pipeline1.setex(UVAR+user_id,which_var,TWO_WEEKS)# kill the key after 2 weeks, since we only care about the prev 13 cohorts (i.e. days)

			pipeline1.execute()


def report_section_wise_retention(which_var):
	"""
	Reporting: calculates (via raw data captured by set_variation_wise_retention()) and presents the daily retention data of a given section
	
	We report 12 days worth of data - calculated 'd1' retention is the respective 'd1' averaged out for all these days
	"""
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(EXP[which_var+'cr'])
	if cached_data:
		cohort_data = json.loads(cached_data)
	else:
		time_now = time.time()
		cohort_id_today = retrieve_cohort(time_now)

		cohorts_to_display = range(cohort_id_today-11,cohort_id_today+1,1)
		stringified_cohorts = map(str,cohorts_to_display)
		cohort_names = ['11 days ago','10 days ago','9 days ago','8 days ago','7 days ago','6 days ago','5 days ago','4 days ago',\
		'3 days ago','2 days ago','Yesterday','Today']
		cohort_names_dict = dict(zip(stringified_cohorts,cohort_names))
		cohort_dates = exact_date(cohorts_to_display,in_bulk=True)
		cohort_dates_dict = dict(zip(stringified_cohorts,cohort_dates))
		days_dict = {'d0':0,'d1':1,'d2':2,'d3':3,'d4':4,'d5':5,'d6':6,'d7':7,'d8':8,'d9':9,'d10':10,'d11':11}
		
		# extracting logged cohort-based data from redis DB
		pipeline1 = my_server.pipeline()
		for cohort_id in stringified_cohorts:
			pipeline1.hgetall(EXP[which_var+'r']+cohort_id)
		cohorts = pipeline1.execute()
		
		# re-sort retrieved cohorts according to days (i.e. 'd0' ought to be first, 'd1' second, and so forth)
		sorted_cohorts = []
		for cohort in cohorts:
			if cohort:
				sorted_cohort = sorted(cohort.items(),key=lambda x: days_dict[x[0]])
				sorted_cohorts.append(sorted_cohort)
			else:
				sorted_cohorts.append(cohort)
		
		# enrich retention raw numbers with '% of d0' metrics
		final_retention_data = []
		for cohort_retention_data in sorted_cohorts:
			try:
				num_visitors_in_d0_of_that_cohort = int(cohort_retention_data[0][1]) if cohort_retention_data else 0
			except IndexError:
				num_visitors_in_d0_of_that_cohort = 0
			enriched_retention_data = []
			if cohort_retention_data:
				for retention_type, num_visitors in cohort_retention_data:
					num_visitors = int(num_visitors) if num_visitors else num_visitors
					if num_visitors_in_d0_of_that_cohort:
						enriched_retention_data.append((retention_type,num_visitors,format((100.0*num_visitors/num_visitors_in_d0_of_that_cohort),'.2f')))
					else:
						enriched_retention_data.append((retention_type,num_visitors,'0.00'))
			else:
				enriched_retention_data.append(())#empty tuple is appended
			final_retention_data.append(enriched_retention_data)

		# prepare data for the template
		cohort_data, counter = [], 0
		for cohort_id in stringified_cohorts:
			cohort_data.append((cohort_id, cohort_dates_dict[cohort_id],cohort_names_dict[cohort_id],final_retention_data[counter]))
			counter += 1

		my_server.setex(EXP[which_var+'cr'],json.dumps(cohort_data),ONE_HOUR)
	return cohort_data


def retention_clean_up(which_var):
	"""
	Just a testing function, used to cleanse retention data for a given experiment

	Retention data will scrub itself in production
	"""
	if which_var:
		pass
		# user_id = '172'
		# my_server = redis.Redis(connection_pool=POOL)
		# my_server.delete(UVAR+user_id)
		# list_of_keys = my_server.keys(EXP[which_var]+user_id+"*")
		# for item in list_of_keys:
		# 	my_server.delete(item)
		# list_of_keys = my_server.keys(EXP[which_var+'r']+'*')
		# for item in list_of_keys:
		# 	my_server.delete(item)
		# list_of_keys = my_server.keys(EXP[which_var+'rl']+'*')
		# for item in list_of_keys:
		# 	my_server.delete(item)
		# list_of_keys = my_server.keys(EXP[which_var+'cr'])
		# for item in list_of_keys:
		# 	my_server.delete(item)


##################################################################################################################################
######################################################## Segment Analysis ########################################################
##################################################################################################################################


def log_segment_action(user_id, segment_age, action_categ, action_sub_categ, action_liq, time_of_action):
	"""
	Logs actions taken by users at various world ages

	Useful for mapping user journeys from 0 to inifinity
	User journeys can shed light on what are most frequent actions taken by retained users
	"""
	payload = str(user_id)+":"+str(segment_age)+":"+action_categ+":"+action_sub_categ+":"+action_liq+":"+str(time_of_action)
	redis.Redis(connection_pool=POOL).zadd(USER_ACTION_STORE, payload, time_of_action)


def retrieve_all_logged_actions(start_idx=0, end_idx=-1):
	"""
	Retrieves all logged actions, useful for exporting data into a CSV
	"""
	return redis.Redis(connection_pool=POOL).zrange(USER_ACTION_STORE,start_idx,end_idx)


