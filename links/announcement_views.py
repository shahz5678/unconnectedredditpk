from django.shortcuts import render

def coming_soon(request):
	"""
	Renders the detail of an announcement
	"""
	return render(request,"announcement/coming_soon_detail.html",{})