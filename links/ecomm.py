from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .redis3 import log_unserviced_city, log_completed_orders
from .forms import EcommCityForm

def show_ecomm_choices(request,*args,**kwargs):
	return render(request,"ecomm_choices.html",{})

def x32_details(request,*args,**kwargs):
	return render(request,"x32_details.html",{})

def x2lite_details(request,*args,**kwargs):
	return render(request,"x2lite_details.html",{})

@csrf_protect
def buyer_loc(request,*args,**kwargs):
	if request.method == 'POST':
		merch_id = request.POST.get("merch_id") #1 is x32, 2 is x2lite
		return render(request,"buyer_loc.html",{'merch_id':merch_id})
	else:
		return render(request,'404.html',{})

@csrf_protect
def process_city(request,*args,**kwargs):
	if request.method == 'POST':
		merch_id = request.POST.get('merch_id',None) #1 is x32, 2 is x2lite
		loc = request.POST.get('loc',None)
		if merch_id and loc:
			if loc == 'lhr' or loc == 'rwp' or loc == 'isb':
				# move on to asking the user their mobile numer and their real name
				return redirect("home")
			elif loc == 'khi':
				log_unserviced_city(request.user.id,'karachi',('x32' if merch_id == '1' else 'x2lite'))
				return render(request,"no_delivery.html",{'loc':'Karachi'})
			elif loc == 'other':
				form = EcommCityForm()
				return render(request,"enter_city.html",{'merch_id':merch_id,'form':form})
			else:
				form = EcommCityForm(request.POST)
				if form.is_valid():
					loc = form.cleaned_data.get("loc",None)
					if loc:
						log_unserviced_city(request.user.id,loc.lower(),('x32' if merch_id == '1' else 'x2lite'))
						return render(request,"no_delivery.html",{'loc':loc})
					else:
						return render(request,"ecomm_choices.html",{})			
				else:
					return render(request,"enter_city.html",{'merch_id':merch_id,'form':form})
		else:
			return render(request,"ecomm_choices.html",{})
	else:
		return render(request,'404.html',{})
