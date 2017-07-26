import base64
from django.contrib.auth import authenticate, login
from django.http import HttpResponse #,JsonResponse
from .redisads import put_ad, suspend_ad, delete_ad, resume_ad
# from core.models import Locations,Ad
from target_urls import call_aasan_api
import json
from django.views.decorators.csrf import csrf_exempt

#uname = aasanads
#password = asdasdASFDA234

# def enqueue_ad(ad_dict):
# 	'''
# 	create ad object in hash
# 	add ad in relevant location list
# 	return True
# 	'''
# 	try:
# 		return put_ad(ad_dict)
# 	except:
# 		return False

def authenticate_req(request,realm="",*args,**kwargs):
	# print request.META.keys()
	# print request.POST.keys()
	# print request.body
	if 'HTTP_AUTHORIZATION' in request.META:
		auth = request.META['HTTP_AUTHORIZATION'].split()
		if len(auth) == 2:
			# NOTE: We are only support basic authentication for now.
			if auth[0].lower() == "basic":
				uname, passwd = base64.b64decode(auth[1]).split(':')
				user = authenticate(username=uname, password=passwd)
				if user is not None:
					if user.groups.filter(name='api_access').exists():
						return True
					else:
						return HttpResponse('Bad authentication')
				else:
					return HttpResponse('No such user')
	response = HttpResponse()
	response.status_code = 401
	response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
	return response

@csrf_exempt
def resume_req(request,realm="",*args,**kwargs):
	auth_result = authenticate_req(request)
	if auth_result == True:
		if request.body:
			#json.loads converts string to dictionary object
			ad_id_dict = json.loads(request.body)
			success = resume_ad(str(ad_id_dict['tid']))
			if success:
				return HttpResponse('Ad resumed')
			else:
				return HttpResponse('Ad resumption failed')
		else:
			return HttpResponse('request body empty')
	else:
		return auth_result

@csrf_exempt
def delete_req(request,realm="",*args,**kwargs):
	auth_result = authenticate_req(request)
	if auth_result == True:
		if request.body:
			#json.loads converts string to dictionary object
			ad_id_dict = json.loads(request.body)
			success = delete_ad(str(ad_id_dict['tid']))
			if success:
				return HttpResponse('Ad deleted')
			else:
				return HttpResponse('Ad deletion failed')
		else:
			return HttpResponse('request body empty')
	else:
		return auth_result

@csrf_exempt
def suspend_req(request,realm="",*args,**kwargs):
	auth_result = authenticate_req(request)
	if auth_result == True:
		if request.body:
			# print request.body
			#json.loads converts string to dictionary object
			ad_id_dict = json.loads(request.body)
			# print ad_id_dict
			success = suspend_ad(str(ad_id_dict['tid']))
			if success:
				return HttpResponse('Ad suspended')
			else:
				return HttpResponse('Ad suspension failed')
		else:
			return HttpResponse('request body empty')
	else:
		return auth_result

@csrf_exempt
def process_req(request,realm="", *args, **kwargs):
	auth_result = authenticate_req(request)
	if auth_result == True:
		'''
		example payload:
		{"phone_number": "03334404403", "status": 1, "contact_preference": 0, "description": "My second advert", 
		"title": "An Ad", "clicks": 10, "location": [1, 2, 3, 4], "only_ladies": false, 
		"address": "Arfa Software Technology Park", "id": 26}
		'''
		ad_url = 'http://www.damadam.pk/nick/ad/pin_code' # the ad can be previewed here
		if request.body:
			#json.loads converts string to dictionary object
			# print request.body
			# ad_id=put_ad(request.body)
			ad_id = put_ad(json.loads(request.body))
			# print ad_id
			if ad_id:
				data = {'tid':str(ad_id),'sms_url':'http://example.com/ad_location'}
				try:
					response = call_aasan_api(data,'send_sms')
					# print response
					# print response.content 
					return HttpResponse('SMS sent') #sending back the ad_url that appears in the SMS
				except:
					return HttpResponse('SMS not sent')
			else:
				return HttpResponse('Cannot put ad. No SMS sent')
		else:
			return HttpResponse('Ad body empty')
	else:
		return auth_result

# @csrf_exempt
# def sms_payload(request,realm="", payload=None,*args, **kwargs)