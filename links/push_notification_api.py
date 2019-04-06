import time
import ujson as json
from pywebpush import webpush, WebPushException
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse, reverse_lazy
from unconnectedreddit.env import PRIVATE_KEY
from redis4 import save_push_subscription
from redis5 import personal_group_already_exists, save_1on1_push_subscription

# TODO: must run 'pip install pywebpush' for this thing to work
# TODO: must run 'pip install -U cryptography==2.5' for pywebpush to work (i.e. upgrade from cryptography 1.9 to 2.5 basically)

@csrf_protect
def save_subscription(request):
	"""
	Saving the push notification subscription data to a database for use later on
	"""
	if request.method == "POST":
		is_ajax = request.is_ajax()
		if is_ajax:
			target_id = request.POST.get('target_id','')
			fail_url = request.POST.get('furl','')
			is_first_time_subscriber = True if request.POST.get('first_time_subscriber','') == '1' else False
			if target_id:
				own_id = request.user.id
				group_id, already_exists = personal_group_already_exists(own_id, target_id)
				if already_exists:
					endpoint = request.POST.get('endpoint','')# This endpoint URL needs to be kept secret, or other applications might be able to send push messages to your application.
					auth_key = request.POST.get('auth','')# secret - never to be shared outside the application
					p256dh_key = request.POST.get('p256dh','')# a public key
					if target_id and endpoint and auth_key and p256dh_key:
						subscription_info = {'endpoint':endpoint,'auth':auth_key,'p256dh':p256dh_key}
						save_push_subscription(own_id, subscription_info, time.time(), first_time=is_first_time_subscriber)# store it referenced to the user who requested the push capability
						save_1on1_push_subscription(receiver_id=own_id, sender_id=target_id)
						return HttpResponse(json.dumps({'data':{'success': True},'redirect':reverse('personal_group_subscription_success')}),\
						content_type='application/json',status=200)# format of json response is prescribed by https://developers.google.com/web/fundamentals/push-notifications/subscribing-a-user
					else:
						# something went wrong - return with a failure message
						return HttpResponse(json.dumps({'data':{'success': False},'redirect':fail_url}),content_type='application/json',status=400)# format of json response is prescribed by https://developers.google.com/web/fundamentals/push-notifications/subscribing-a-user
				else:
					# such a group doesn't exist (where own_id and target_id are friends)
					raise Http404("This group does not exist!")
			else:
				raise Http404("Target ID is none")
		else:
			raise Http404("Unable to successfully subscribe")
	else:
		raise Http404("Unable to save notification subscription on GET")


def send_single_push_notification(subscription_info, payload):
	"""
	Sending a single push notification containing 'payload' to a subscribed browser
	"""
	try:
		# this takes a while, so put a preloader in the window (for JS clients)
		response = webpush(
			subscription_info=subscription_info,
			data=json.dumps(payload),
			vapid_private_key=PRIVATE_KEY,
			vapid_claims={"sub": "mailto:hassan.baig@alumni.duke.edu",},
			timeout=35,#timeout of POST request
			ttl=120#the ttl of how long the message should live
		)
		# print response.status_code
		# print "---------------------"
		# print response.json
		# print "---------------------"
		# print response.headers
		# print "---------------------"
		# print dir(response)
		return True, response.status_code
	except WebPushException as ex:
		# This may contain the requests response
		# print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
		# Mozilla returns additional information in the body of the response.
		# print dir(ex.response)
		# if ex.response and ex.response.json():
		# 	extra = ex.response.json()
		# 	print("Remote service replied with a {}:{}, {}",
		# 		  extra.code,
		# 		  extra.errno,
		# 		  extra.message
		# 		  )
		# print ex.response.status_code
		return False, ex.response.status_code


def push_notification_permission_denied(request):
	"""
	This fires if user initially presses 'Allow' for notifications, but eventually pressed 'block' within the same flow

	The 'redirect_url' needs to be made more generic if push notifications can be permitted from sections other than 1 on 1
	"""
	return render(request,"push_notifications/push_notification_subscription_prompts.html",{'redirect_url':reverse_lazy("enter_personal_group"),\
		'denied':True})


def push_notification_permission_temporarily_denied(request):
	"""
	This fires if user initially presses 'Allow' for notifications, but eventually crosses the screen within the same flow

	The 'redirect_url' needs to be made more generic if push notifications can be permitted from sections other than 1 on 1
	"""
	return render(request,"push_notifications/push_notification_subscription_prompts.html",{'redirect_url':reverse_lazy("enter_personal_group"),\
		'temp_denied':True})


def push_notification_not_available(request):
	"""
	This fires if internet isn't available (or the app isn't) when the user tries to access the notifications area
	"""
	return render(request,"push_notifications/push_notification_subscription_prompts.html",{'redirect_url':reverse_lazy("enter_personal_group"),\
		'unavailable':True})


def push_notification_not_working(request):
	"""
	This fires if target_id couldn't correctly be retrieved (to whom the notif was to be sent)
	"""
	return render(request,"push_notifications/push_notification_subscription_prompts.html",{'redirect_url':reverse_lazy("enter_personal_group")})