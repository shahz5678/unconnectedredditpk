from django.shortcuts import render

def show_ecomm_choices(request,*args,**kwargs):
	return render(request,"ecomm_choices.html",{})