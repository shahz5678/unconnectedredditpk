from django.http import HttpResponse
from django.shortcuts import render
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
import os

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
			cnic = form.cleaned_data.get("cnic",None)
			city = form.cleaned_data.get("city",None)
			license = form.cleaned_data.get("license",None)
			CSRF = csrf.get_token(request)
			request.session['firstname'] = firstname
			request.session['lastname'] = lastname
			request.session['cnic'] = cnic
			request.session['city'] = city
			request.session['license'] = license
			request.session['csrf_careem'] = CSRF
			ON_MAC = os.environ.get('ON_MAC')
			print ON_MAC
			return render(request,'verify_careem_number.html',{'form':form,'csrf':CSRF,'ON_MAC':ON_MAC})
		else:
			return render(request,'careem_ad.html',{'form':form,'device':get_device(request)})
	else:
		form = CareemAdForm()
		request.session.pop('firstname',None) 
		request.session.pop('lastname',None)
		request.session.pop('cnic',None)
		request.session.pop('city',None)
		request.session.pop('license',None)
		request.session.pop('csrf_careem',None)
		return render(request,'careem_ad.html',{'form':form,'device':get_device(request)})



def verify_careem_number(request):
	return render(request,'verify_careem_number.html')
