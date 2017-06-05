from .redis1 import get_website_feedback
from .redis3 import retrieve_erroneous_passwords
from django.shortcuts import redirect, render
import csv

def export_error_feedback(request,*args,**kwargs):
	retrieve_erroneous_passwords()
	return redirect("home")

def export_website_feedback(request,*args,**kwargs):
	feedback = get_website_feedback()
	# remove answer6, question6 when reverting back to 5 question format
	keys = ['username', 'answer1', 'answer2', 'answer3', 'answer4', 'answer5', 'answer6',\
	'question1', 'question2', 'score', 'question3', 'question4', 'question5', 'question6',\
	'device', 'time_of_feedback', 'date_joined', 'city','gender','age','mobile']
	with open('website_feedback.csv', 'wb') as output_file:
	    dict_writer = csv.DictWriter(output_file, keys)
	    dict_writer.writeheader()
	    dict_writer.writerows(feedback)
	return redirect("home")