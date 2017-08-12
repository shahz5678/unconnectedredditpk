import ast, time
from operator import itemgetter
from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from page_controls import WEEKLY_ECOMM_METRICS_HISTORY_LIMIT, DAILY_ECOMM_METRICS_HISTORY_LIMIT
from redis3 import get_and_reset_daily_ecomm_clicks, get_and_reset_weekly_ecomm_clicks, return_all_ad_data
from redis4 import get_and_reset_daily_ecomm_visits, get_and_reset_weekly_ecomm_visits, insert_metrics, return_all_metrics_data


def get_unique_clicks_per_unique_visitor(metrics_obj):
	try:
		return "{0:.2f}".format(metrics_obj.unique_click_count/float(metrics_obj.unique_visits_count)) # resulted rounded to 2 decimal places using inbuilt 'format' method
	except ZeroDivisionError:
		return None


def get_unique_clicks_per_unique_clicker(metrics_obj):
	try:
		return "{0:.2f}".format(metrics_obj.unique_click_count/float(metrics_obj.unique_clickers_count))
	except ZeroDivisionError:
		return None


def get_proportion_of_clickers_to_visitors(metrics_obj):
	try:
		return "{0:.2f}".format(metrics_obj.unique_clickers_count/float(metrics_obj.unique_visits_count))
	except ZeroDivisionError:
		return None

def get_unique_new_clickers_per_unique_new_visitors(metrics_obj):
	try:
		return "{0:.2f}".format(metrics_obj.unique_new_clicker_count/float(metrics_obj.unique_new_visitor_count))
	except ZeroDivisionError:
		return None


def get_unique_new_clicks_per_unique_new_visitor(metrics_obj):
	try:
		return "{0:.2f}".format(metrics_obj.unique_new_click_count/float(metrics_obj.unique_new_visitor_count))
	except ZeroDivisionError:
		return None

def get_total_unique_visitors(metrics_obj):
	return metrics_obj.unique_visits_count


def get_total_unique_clicks(metrics_obj):
	return metrics_obj.unique_click_count

############################################################################################

def unique_new_users(ids_and_joining_dates):
	unique_new_visitors = []
	for id_, date_joined in ids_and_joining_dates:
		if date_joined > (datetime.utcnow()-timedelta(days=1)):
			unique_new_visitors.append(id_)
	return unique_new_visitors

def unique_new_clicks_over_all_ads(unique_clicks, unique_new_visitors):
	# calculate clicks only by new users
	unique_new_clicks_over_all_ads = []
	for id_,ad_id in unique_clicks:
		if int(id_) in unique_new_visitors:
			unique_new_clicks_over_all_ads.append((id_,ad_id))
	return unique_new_clicks_over_all_ads


def retrieve_values_from_list_of_tuples(list_of_tuples):
	return map(itemgetter(0), list_of_tuples)


class EcommTrackingManager(object):
	obj = None

	def __init__(self, gross_visits, gross_clicks, metric_type=None):
		clicks, visits = [], []
		for click in gross_clicks:
			clicks.append(ast.literal_eval(click))
		self.gross_clicks = clicks
		for visit in gross_visits:
			visits.append(ast.literal_eval(visit))
		self.gross_visits = visits # a list of all visits in the past 24 hours
		self.unique_visits = set(visits) # using set() makes the list unique
		self.unique_clicks = set(clicks)
		self.unique_visits_count = len(self.unique_visits) # len() gives the number of elements in the list (or set)
		self.unique_click_count = len(self.unique_clicks)
		self.unique_clickers = set(retrieve_values_from_list_of_tuples(list_of_tuples=clicks))
		self.unique_clickers_count = len(self.unique_clickers)
		#########################################################################################
		if metric_type == 'daily':
			self.unique_new_visitors = unique_new_users(ids_and_joining_dates=User.objects.filter(id__in=self.unique_visits).values_list('id','date_joined'))
			self.unique_new_clickers = unique_new_users(ids_and_joining_dates=User.objects.filter(id__in=self.unique_clickers).values_list('id','date_joined'))
			self.unique_new_visitor_count = len(self.unique_new_visitors)
			self.unique_new_clicker_count = len(self.unique_new_clickers)
			self.unique_new_clicks = unique_new_clicks_over_all_ads(unique_clicks=self.unique_clicks, unique_new_visitors=self.unique_new_visitors)
			self.unique_new_click_count = len(self.unique_new_clicks)
		else:
			self.unique_new_visitors = None
			self.unique_new_clickers = None
			self.unique_new_visitor_count = None
			self.unique_new_clicker_count = None
			self.unique_new_clicks = None
			self.unique_new_click_count = None

def calc_ecomm_metrics():
	most_recent_days_gross_clicks = get_and_reset_daily_ecomm_clicks()
	most_recent_days_gross_visits, num_days = get_and_reset_daily_ecomm_visits()
	daily_metrics_obj = EcommTrackingManager(gross_visits=most_recent_days_gross_visits, gross_clicks=most_recent_days_gross_clicks, metric_type='daily')
	
	daily_payload = [get_unique_clicks_per_unique_visitor(daily_metrics_obj), \
	get_unique_clicks_per_unique_clicker(daily_metrics_obj), \
	get_proportion_of_clickers_to_visitors(daily_metrics_obj), \
	get_unique_new_clickers_per_unique_new_visitors(daily_metrics_obj), \
	get_unique_new_clicks_per_unique_new_visitor(daily_metrics_obj), \
	get_total_unique_visitors(daily_metrics_obj), \
	get_total_unique_clicks(daily_metrics_obj)]
	
	###################
	if num_days > 6:
		weekly_gross_visits = get_and_reset_weekly_ecomm_visits()
		weekly_gross_clicks = get_and_reset_weekly_ecomm_clicks()
		weekly_metrics_obj = EcommTrackingManager(gross_visits=weekly_gross_visits, gross_clicks=weekly_gross_clicks, metric_type='weekly')
		weekly_unique_clicks_per_unique_visitor = get_unique_clicks_per_unique_visitor(weekly_metrics_obj)
		weekly_unique_clicks_per_unique_clicker = get_unique_clicks_per_unique_clicker(weekly_metrics_obj)
		weekly_proportion_of_clickers_to_visitors = get_proportion_of_clickers_to_visitors(weekly_metrics_obj)
		weekly_unique_visitors = get_total_unique_visitors(weekly_metrics_obj)
		weekly_unique_clicks = get_total_unique_clicks(weekly_metrics_obj)
	else:
		weekly_unique_clicks_per_unique_visitor = None
		weekly_unique_clicks_per_unique_clicker = None
		weekly_proportion_of_clickers_to_visitors = None
		weekly_unique_visitors = None
		weekly_unique_clicks = None
	
	weekly_payload = [weekly_unique_clicks_per_unique_visitor, \
	weekly_unique_clicks_per_unique_clicker, \
	weekly_proportion_of_clickers_to_visitors, \
	weekly_unique_visitors, \
	weekly_unique_clicks]
	
	###################
	return daily_payload, weekly_payload


def insert_latest_metrics():
	calculation_time = time.time()
	latest_daily_metrics, latest_weekly_metrics = calc_ecomm_metrics()
	insert_metrics(ecomm_metrics=latest_daily_metrics, reporting_time=calculation_time, period='daily')
	if latest_weekly_metrics[0]:
		insert_metrics(ecomm_metrics=latest_weekly_metrics, reporting_time=calculation_time, period='weekly')


def make_reported_metrics_readable(metrics_type, metrics_history, cut_off):
	metrics = []
	for row in metrics_history[:cut_off]:
		row = ast.literal_eval(row) # making 'string' dictionaries readable
		row["entry_time"] = datetime.fromtimestamp(row["entry_time"])
		metrics.append(row)
	return metrics

def get_latest_metrics(metrics_type=None):
	daily_metrics_history, weekly_metrics_history = return_all_metrics_data()# 'metrics_history' contains unusable 'stringified' dictionaries
	if metrics_type == 'daily':
		CUT_OFF = DAILY_ECOMM_METRICS_HISTORY_LIMIT
		if daily_metrics_history:
			daily_metrics = make_reported_metrics_readable(metrics_type=metrics_type, metrics_history=daily_metrics_history, cut_off=CUT_OFF)
			template_context = {'unique_clicks_per_unique_visitor':daily_metrics[0]["unique_clicks_per_unique_visitor"], 'metrics_type':metrics_type,\
			'unique_clicks_per_unique_clicker':daily_metrics[0]["unique_clicks_per_unique_clicker"],'proportion_of_clickers_to_visitors':daily_metrics[0]["proportion_of_clickers_to_visitors"],\
			'unique_new_clickers_per_unique_new_visitors':daily_metrics[0]["unique_new_clickers_per_unique_new_visitors"],\
			'unique_new_clicks_per_unique_new_visitor':daily_metrics[0]["unique_new_clicks_per_unique_new_visitor"], 'reporting_time':daily_metrics[0]["entry_time"], \
			'total_unique_visitors':daily_metrics[0]["total_unique_visitors"],'total_unique_clicks':daily_metrics[0]["total_unique_clicks"],'history':daily_metrics}
		else:
			template_context = {}
		return template_context
	elif metrics_type == 'weekly':
		CUT_OFF = WEEKLY_ECOMM_METRICS_HISTORY_LIMIT
		if weekly_metrics_history:
			weekly_metrics = make_reported_metrics_readable(metrics_type=metrics_type, metrics_history=weekly_metrics_history, cut_off=CUT_OFF)
			template_context = {'weekly_unique_clicks_per_unique_visitor':weekly_metrics[0]["weekly_unique_clicks_per_unique_visitor"], \
			'weekly_unique_clicks_per_unique_clicker':weekly_metrics[0]["weekly_unique_clicks_per_unique_clicker"],'metrics_type':metrics_type,\
			'weekly_proportion_of_clickers_to_visitors':weekly_metrics[0]["weekly_proportion_of_clickers_to_visitors"],\
			'reporting_time':weekly_metrics[0]["entry_time"], 'weekly_unique_visitors':weekly_metrics[0]["weekly_unique_visitors"],\
			'weekly_unique_clicks':weekly_metrics[0]["weekly_unique_clicks"],'history':weekly_metrics}
		else:
			template_context = {}
		return template_context


def display_latest_metrics(request, metrics_type):
	return render(request,"ecomm_metrics.html",get_latest_metrics(metrics_type))


#########################################################################################################################################################################



def get_all_ads_data():
	current_ads, expired_ads = return_all_ad_data() #results two lists (of dictionaries)
	for ad in expired_ads:
		ad["is_expired"] = 1 # appending 1 in expired_ads
	for ad in current_ads:
		ad["is_expired"] = 0 # appending 0 in current_ads
	all_ads = current_ads + expired_ads
	return all_ads

def get_click_distribution(request):
	all_ads = get_all_ads_data()
	real_clicks = []
	for ad in all_ads:
		if ad["is_expired"] == 1:
			own_number = "0"+ast.literal_eval(ad["MN_data"])["national_number"] if "MN_data" in ad else None
			if "click_details" in ad:
				for num, click_time in ast.literal_eval(ad["click_details"]):
					if num != own_number:
						days_since_submission = "{0:.4f}".format(((click_time - float(ad["submission_time"]))/86400))
						real_clicks.append((ad["ad_id"], num, click_time, days_since_submission))
	if real_clicks:
		import csv
		filename = 'clicks_'+str(int(time.time()))+'.csv'
		with open(filename,'wb') as f:
			wtr = csv.writer(f)
			columns = "ad_id days_since_submission time_of_click mobile_number".split()
			wtr.writerow(columns)
			for click in real_clicks:
				ad_id = click[0]
				days_since_submission = click[3]
				time_of_click = click[2]
				mobile_number = click[1]
				to_write = [ad_id,days_since_submission, time_of_click, mobile_number]
				wtr.writerows([to_write])
	return render(request,"404.html",{})


def get_ad_export(request):
	all_ads = get_all_ads_data()
	import csv
	filename = 'ads_'+str(int(time.time()))+'.csv'
	with open(filename,'wb') as f:
		wtr = csv.writer(f)
		columns = \
		"ad_id submission_time(epoch) sub_time_human fbs device expiration_time(epoch) exp_time_human expiration_clicks is_expired username user_id seller_name seller_number seller_city seller_town is_new is_barter ask category title title_char_count num_unique_clicks clicked_own_ad num_unique_detail_clicks photo_count description desc_char_count SMS_setting AK_ID closed_by".split()
		wtr.writerow(columns)
		for current_ad in all_ads:
			ad_id = current_ad["ad_id"] if "ad_id" in current_ad else None
			submission_time = current_ad["submission_time"] if "submission_time" in current_ad else None
			sub_time_human = datetime.fromtimestamp(float(current_ad["submission_time"])) if "submission_time" in current_ad else None
			fbs = current_ad["on_fbs"] if "on_fbs" in current_ad else None
			device = current_ad["submission_device"] if "submission_device" in current_ad else None
			expiration_time = current_ad["expiration_time"] if "expiration_time" in current_ad else None
			exp_time_human = datetime.fromtimestamp(float(current_ad["expiration_time"])) if "expiration_time" in current_ad else None
			expiration_clicks = current_ad["expiration_clicks"] if "expiration_clicks" in current_ad else None
			is_expired = current_ad["is_expired"] if "is_expired" in current_ad else None
			username = current_ad["username"] if "username" in current_ad else None
			user_id = current_ad["user_id"] if "user_id" in current_ad else None
			seller_name = current_ad["seller_name"] if "seller_name" in current_ad else None
			seller_number = ast.literal_eval(current_ad["MN_data"])["national_number"] if "MN_data" in current_ad else None
			seller_city = current_ad["city"] if "city" in current_ad else None
			seller_town = current_ad["town"] if "town" in current_ad else None
			is_new = current_ad["is_new"] if "is_new" in current_ad else None
			is_barter = current_ad["is_barter"] if "is_barter" in current_ad else None
			ask = current_ad["ask"] if "ask" in current_ad else None
			title = current_ad["title"] if "title" in current_ad else None
			title_char_count = len(title) if title else 0
			num_unique_clicks = current_ad["unique_clicks"] if "unique_clicks" in current_ad else 0
			# if is_expired:
			# 	unique_clicks_per_day = int(num_unique_clicks)/((float(expiration_time)-float(submission_time))/86400)
			# else:
			# 	unique_clicks_per_day = int(num_unique_clicks)/((time.time()-float(submission_time))/86400)
			if num_unique_clicks:
				nums = retrieve_values_from_list_of_tuples(ast.literal_eval(current_ad["click_details"]))
				if "0"+seller_number in nums:
					clicked_own_ad = 'Yes'
				else:
					clicked_own_ad = 'No'
			else:
				clicked_own_ad = 'No'
			photo_count = current_ad["photo_count"] if "photo_count" in current_ad else None
			description = current_ad["desc"] if "desc" in current_ad else None
			desc_char_count = len(description) if description else 0
			num_unique_detail_clicks = current_ad["unique_detail_clicks"] if "unique_detail_clicks" in current_ad else None
			SMS_setting = current_ad["SMS_setting"] if "SMS_setting" in current_ad else None
			AK_ID = current_ad["AK_ID"] if "AK_ID" in current_ad else None
			closed_by = current_ad["closed_by"] if "closed_by" in current_ad else None
			category = current_ad["categ"] if "categ" in current_ad else None
			to_write = [ad_id,submission_time, sub_time_human, fbs,device,expiration_time,exp_time_human,expiration_clicks, is_expired, username, user_id, seller_name, seller_number, seller_city, seller_town, is_new, is_barter, \
			ask, category, title, title_char_count, num_unique_clicks, clicked_own_ad, num_unique_detail_clicks, photo_count, description, desc_char_count, SMS_setting, AK_ID, closed_by]
			wtr.writerows([to_write])
	return render(request, "404.html", {})