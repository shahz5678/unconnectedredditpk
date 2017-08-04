from django.http import HttpResponse
from django.shortcuts import render, redirect
from django import forms
from forms import AdFeedbackForm
from links.ads_forms import CareemAdForm
from django.utils import timezone
from views import convert_to_epoch
from django.core.exceptions import ValidationError
from django.middleware import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from ecomm import get_device
from redis4 import export_careem_data, del_careem_data
import os, time
from mixpanel import Mixpanel
from unconnectedreddit.settings import MIXPANEL_TOKEN

mp = Mixpanel(MIXPANEL_TOKEN)

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def careem_ad(request,*args,**kwargs):
	if request.method == 'POST':
		form = CareemAdForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get("username",None)
			name = username.strip()
			name = name.title()		
			i=0
			firstname = ''
			lastname = ''		
			for word in name.split():
				if i==0:
					firstname=word
					i+=1
				else:
					lastname+=word
					lastname+=' '
					i+=1
			phonenumber = form.cleaned_data.get("phonenumber",None)
			city = form.cleaned_data.get("city",None)
			license = form.cleaned_data.get("license",None)
			car = form.cleaned_data.get("car",None)
			CSRF = csrf.get_token(request)
			ON_AZURE = os.environ.get('ON_AZURE',None)
			request.session['firstname'] = firstname
			request.session['lastname'] = lastname
			request.session['phonenumber'] = phonenumber
			request.session['city'] = city
			request.session['license'] = license
			request.session['car'] = car
			request.session['csrf_careem'] = CSRF						
			request.session['ON_AZURE'] = ON_AZURE
			return redirect("verify_careem_applicant")
		else:
			return render(request,'careem_ad.html',{'form':form,'device':get_device(request)})
	else:
		form = CareemAdForm()
		mp.track(request.user.id, 'Clicked Careem Ad')
		request.session.pop('firstname',None) 
		request.session.pop('lastname',None)
		request.session.pop('phonenumber',None)
		request.session.pop('city',None)
		request.session.pop('license',None)
		request.session.pop('car',None)
		request.session.pop('csrf_careem',None)
		request.session.pop('ON_AZURE',None)
		return render(request,'careem_ad.html',{'form':form,'device':get_device(request)})

def verify_careem_number(request):
	return render(request,'verify_careem_number.html')

def s_test(request):
	import csv
	result1 = export_careem_data()
	total_users=0;
	if result1 == False:
		return render(request,'404.html')
	else:
		filename = 'careem_'+str(int(time.time()))+'.csv'
		with open(filename,'wb') as f:
			wtr = csv.writer(f)
			columns = ["Firstname","Lastname","Mobile","City","License","Car Ownership"]
			wtr.writerow(columns)
			for user in result1:
				total_users+=1
				firstname,lastname,phonenumber,city,license,car = user['firstname'],user['lastname'],user['phonenumber'],\
				user['city'],user['license'],user['car']
				if ( car == 'Yes' or license == 'Yes' ) and (city != 'Koi aur'): 
					to_write = [firstname,lastname,phonenumber,city,license,car]
					wtr.writerows([to_write])
				else:
					pass
			to_write = ["Total ="+str(total_users)]
			wtr.writerows([to_write])	
		del_careem_data()		
		return render(request,'s_test.html')

