from .redis1 import get_website_feedback
from django.shortcuts import redirect, render
import csv

def export_website_feedback(request,*args,**kwargs):
	feedback = get_website_feedback()
	# keys = feedback[0].keys()
	keys = ['username', 'answer5', 'answer4', 'answer1', 'answer3', 'answer2', \
	'question5', 'question4', 'score', 'question1', 'question3', 'question2', \
	'device', 'time_of_feedback', 'date_joined', 'city','gender','age','mobile']
	with open('website_feedback.csv', 'wb') as output_file:
	    dict_writer = csv.DictWriter(output_file, keys)
	    dict_writer.writeheader()
	    dict_writer.writerows(feedback)
	return redirect("home")