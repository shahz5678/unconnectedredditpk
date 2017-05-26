from .redis1 import get_website_feedback
from django.shortcuts import redirect, render
import csv

def export_website_feedback(request,*args,**kwargs):
	feedback = get_website_feedback()
	keys = feedback[0].keys()
	with open('website_feedback.csv', 'wb') as output_file:
	    dict_writer = csv.DictWriter(output_file, keys)
	    dict_writer.writeheader()
	    dict_writer.writerows(feedback)
	return redirect("home")