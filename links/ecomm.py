from django.shortcuts import render

def show_ecomm_choices(request,*args,**kwargs):
	return render(request,"ecomm_choices.html",{})

def x32_details(request,*args,**kwargs):
	return render(request,"x32_details.html",{})

def x2lite_details(request,*args,**kwargs):
	return render(request,"x2lite_details.html",{})	