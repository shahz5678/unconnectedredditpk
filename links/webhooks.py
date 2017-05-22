import json
from optimizely_config_manager import OptimizelyConfigManager
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from unconnectedreddit.optimizely_settings import PID

config_manager = OptimizelyConfigManager(PID)

@csrf_exempt
def webhook_event(request,*args,**kwargs):
	if request.method == 'POST':
		data = json.loads(request.body)
		event_type = data['event']
		# use CDN URL from webhook payload
		if event_type == 'project.datafile_updated':
			url = data['data']['cdn_url']
			config_manager.set_obj(url)
			response_data = {}
			response_data['success'] = True
			# return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
		response_data = {}
		response_data['success'] = False
		# return json.dumps({'success':False}), 400, {'ContentType':'application/json'}
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	else:
		return render(request,"404.html",{})