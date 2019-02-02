from django.shortcuts import render

def coming_soon(request):
	"""
	Renders the detail of an announcement
	"""
	return render(request,"announcement/coming_soon_detail.html",{})


def maintainance_notice(request):
	"""
	Renders the detail of an announcement
	"""
	return render(request,"announcement/maintainance_detail.html",{})	