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

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def careem_ad(request,*args,**kwargs):
	if request.method == 'POST':
		print("in post request of careem_ad")
		form = CareemAdForm(request.POST)
		print ('outside form')
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
			# print firstname
			# print lastname
			cnic = form.cleaned_data.get("cnic",None)
			print cnic
			city = form.cleaned_data.get("city",None)
			# print show
			license = form.cleaned_data.get("license",None)
			# print license
			CSRF = csrf.get_token(request)
			request.session['firstname'] = firstname
			request.session['lastname'] = lastname
			request.session['cnic'] = cnic
			request.session['city'] = city
			request.session['license'] = license
			request.session['csrf_careem'] = CSRF
			return render(request,'verify_careem_number.html',{'form':form,'csrf':CSRF})
		else:
			# print ('in validation error')
			return render(request,'careem_ad.html',{'form':form})
	else:
		form = CareemAdForm()
		request.session.pop('firstname',None) 
		request.session.pop('lastname',None)
		request.session.pop('cnic',None)
		request.session.pop('city',None)
		request.session.pop('license',None)
		request.session.pop('csrf_careem',None)
		return render(request,'careem_ad.html',{'form':form})



def verify_careem_number(request):
	return render(request,'verify_careem_number.html')
# def printusername(request,*args,**kwargs):
# 		print request.GET.username
# 		print request.GET.phonenumber

#		else:
#			return render(request,'careem_ad.html',{'form':form})
#	else:
#		form = AdFeedbackForm()
#		mp.track(request.user.id, 'Clicked Careem ad')
#		print("in Aasandoc feedback")
#		return render(request,'careem_ad.html',{'form':form})
