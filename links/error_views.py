import time
from django.shortcuts import render
from tasks import log_404

def server_error(request):
	return render(request, '500.html', status=500)
 
def not_found(request):
	log_404.delay(type_of_404='0',time_of_404=time.time())
	return render(request, '404.html', status=404)
 
def permission_denied(request):
	# return render(request, '403.html')
	return render(request, '404.html', status=403)
 
def bad_request(request):
	# return render(request, 'errors/400.html')
	return render(request, '404.html', status=400 )