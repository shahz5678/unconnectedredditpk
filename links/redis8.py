import redis, time
import ujson as json
from collections import defaultdict
from retention_experiments import EXP
from redis3 import exact_date
from location import REDLOC8

ONE_HOUR= 10
TWO_WEEKS = 1209600# in seconds
THREE_MONTHS = 7776000# in seconds

COHORT_TIME_LENGTH = 86400#i.e. set to '1 day'

d1 = {0:'d0',1:'d1',2:'d2',3:'d3',4:'d4',5:'d5',6:'d6',7:'d7',8:'d8',9:'d9',10:'d10',11:'d11',12:'d12'}
COHORT_NAMES_ = defaultdict(lambda: 'd13+', d1)# populates COHORT_NAMES_ by d1, and then uses 'd13+' as default value ('d13+' means 'd13 or more' - where d13 is included)

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC8, db=0)

def retrieve_cohort(time_now):
	"""
	Determine what cohort_id the current time falls into

	It divides (seconds since epoch) by (seconds in one day). That gives days since epoch.
	Next, it takes the mathematical floor of 'days since epoch' to return the cohort_id.
	Example values can be 18019, 18020, 18021, etc
	"""
	return int(time_now/COHORT_TIME_LENGTH)


def set_section_wise_retention(which_exp, user_id):
	"""
	Setting cohort wise daily retention levels for visitors coming into a given experiment (defined by 'which_exp' parameter)

	This enables us to extract 'd1'-retention type metrics for the said experiment
	Experiments could be first-time visitors coming into 'trending fotos', 'home', '1_on_1', etc
	"""
	time_now, user_id = time.time(), str(user_id)
	visitor_key = EXP[which_exp]+user_id#holds the first time 'user_id' visited a specific cohort
	my_server = redis.Redis(connection_pool=POOL)
	user_registration_time = my_server.get(visitor_key)# what's the first time this user visited this 'section'
	if user_registration_time:
		
		# this user is returning to the experiment!
		cohort_name = COHORT_NAMES_[int((time_now - float(user_registration_time))/COHORT_TIME_LENGTH)]# int((time_now - float(user_registration_time))/COHORT_TIME_LENGTH) gives the time passed since user registered in this experiment
		if cohort_name != 'd13+' and not my_server.exists(EXP[which_exp+'rl']+user_id):
			
			# increment 'dN' (e.g. d1, d5, d11, etc) of this particular time_cohort
			my_server.hincrby(EXP[which_exp+'r']+str(retrieve_cohort(float(user_registration_time))), cohort_name, amount=1)# retrieve_cohort(float(user_registration_time)) gives the original time_cohort the user belongs to
			
			# rate limit user_id from being 'seen again' in this experiment (for the next COHORT_TIME_LENGTH - ie. 24 hours)
			my_server.setex(EXP[which_exp+'rl']+user_id,'1',COHORT_TIME_LENGTH)
			
			# extending expiry to ensure the user remains a 'known user' for THREE_MONTHS more (from time_now)
			my_server.expire(visitor_key,THREE_MONTHS)
	else:

		# user is 'new', so 'register' them as a 'known visitor' in the experiment for the next 3 months
		my_server.setex(visitor_key,time_now,THREE_MONTHS)

		# next, increment 'd0' of the current time_cohort, and set its expiry time
		retention_key = EXP[which_exp+'r']+str(retrieve_cohort(time_now))
		my_server.hincrby(retention_key,'d0',amount=1)# counting as having hit 'd0'
		my_server.expire(retention_key,TWO_WEEKS)# removing this time_cohort after TWO_WEEKS, since we only care about the previous 13 cohorts

		# finally, rate limit user_id from being used again for the next COHORT_TIME_LENGTH (or 24 hours)
		my_server.setex(EXP[which_exp+'rl']+user_id,'1',COHORT_TIME_LENGTH)# rate limit till: COHORT_TIME_LENGTH (or 24 hrs) from the time of registration


def report_section_wise_retention(which_exp):
	"""
	Reporting: calculates (via raw data captured by set_section_wise_retention()) and presents the daily retention data of a given section
	
	We report 12 days worth of data - calculated 'd1' retention is the respective 'd1' averaged out for all these days
	"""
	my_server = redis.Redis(connection_pool=POOL)
	cached_data = my_server.get(EXP[which_exp+'cr'])
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
			pipeline1.hgetall(EXP[which_exp+'r']+cohort_id)#pipeline1.zrange(EXP[which_exp+'r']+cohort_id,0,-1,withscores=True)# returns a list of tuples [(d0,123),(d1,100),...(d12,12)]
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

		my_server.setex(EXP[which_exp+'cr'],json.dumps(cohort_data),ONE_HOUR)
	return cohort_data

	# task5: can retention logging be moved away from Whoseonline(), into the views?
	# task1: try to give exact dates via searching for 'Karachi'
	# task2: retention numbers ought to be shown as a % of num users in d0
	# task3: cache the results in case users try viewing these results again and again
	# task4: ensure it's easy to change daily retention to hourly, minutely, etc. Change "COHORT_TIME_LENGTH" to equal 60 seconds in set_section_wise_retention(), retrieve_cohort() and retrieve_retention_type()


##################################################################################################################################
######################################################## Segment Analysis ########################################################
##################################################################################################################################

USER_ACTION_STORE = 'uas'#global sorted set that logs all post requests by users


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


