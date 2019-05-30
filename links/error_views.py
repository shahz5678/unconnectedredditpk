import time
from django.shortcuts import render
from tasks import log_404
from redis3 import log_bot_user_agent

def server_error(request):
	return render(request, '500.html', status=500)

def not_found(request):
	type_of_url = request.path_info
	if type_of_url == '/robots.txt':
		log_bot_user_agent(user_agent=request.META.get('HTTP_USER_AGENT','unidentified'))
	log_404.delay(type_of_404='0',time_of_404=time.time(),type_of_url=type_of_url)
	return render(request, '404.html', status=404)
 
def permission_denied(request):
	# return render(request, '403.html')
	return render(request, '404.html', status=403)
 
def bad_request(request):
	# return render(request, 'errors/400.html')
	return render(request, '404.html', status=400 )