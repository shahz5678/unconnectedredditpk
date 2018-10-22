from django.shortcuts import render

def server_error(request):
	return render(request, '500.html')
 
def not_found(request):
	return render(request, '404.html')
 
def permission_denied(request):
	# return render(request, '403.html')
	return render(request, '404.html')
 
def bad_request(request):
	# return render(request, 'errors/400.html')
	return render(request, '404.html')