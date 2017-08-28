from score import NUMBER_VERIFICATION_BONUS
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from unauth_forms import ResetForgettersPasswordForm
from account_kit_config_manager import account_kit_handshake
from redis4 import save_careem_data, log_referrer#, save_number_verification_error_data
from tasks import save_consumer_credentials, set_user_binding_with_twilio_notify_service, increase_user_points
from redis3 import save_basic_ad_data, someone_elses_number, get_temporarily_saved_ad_data, get_buyer_snapshot, get_user_csrf, is_mobile_verified, \
get_user_verified_number

def get_requirements(request, csrf, careem=False, csrf_omitted=False):
	status = request.GET.get('status', None)
	auth_code = request.GET.get('code', None) #authorization code which our server may exchange for a user access token.
	state = request.GET.get('state', None) #to verify that FB's servers returned with the response
	if careem:
		return account_kit_handshake(csrf=request.session["csrf_careem"], state=state, status=status, auth_code=auth_code, csrf_omitted=csrf_omitted)
	else:
		return account_kit_handshake(csrf=csrf, state=state, status=status, auth_code=auth_code, csrf_omitted=csrf_omitted)


def verify_careem_applicant(request,*args,**kwargs):
	if 'phonenumber' in request.session:
		car_phonenumber = request.session['phonenumber']
		car_firstname = request.session['firstname']
		car_lastname = request.session['lastname']
		car_car = request.session['car']
		car_city = request.session['city']
		car_license = request.session['license']
		careem_data = {'firstname':car_firstname,'lastname':car_lastname,'car':car_car,\
		'city':car_city,'license':car_license,'phonenumber':car_phonenumber,'user_id':request.user.id}
		saved = save_careem_data(careem_data)
		request.session.pop('firstname',None) 
		request.session.pop('lastname',None)
		request.session.pop('car',None)
		request.session.pop('city',None)
		request.session.pop('license',None)
		request.session.pop('phonenumber',None)
		request.session.pop('csrf_careem',None)
		if saved:
			return render(request,"careem_application_submitted.html",{})
		else:
			return render(request,"careem_number_already_used.html",{})
	else:
		return render(request,"404.html",{})



def verify_forgetter_number(request,*args,**kwargs):
	log_referrer(referrer=request.META.get('HTTP_REFERER',None),loc='forgetter',user_id=None)
	user_id, MN_data, err = get_requirements(request=request,csrf=None, csrf_omitted=True)
	if user_id and MN_data:
		mob_nums = get_user_verified_number(user_id)
		if MN_data['national_number'] in mob_nums:
			# prompt user to change password
			return render(request,"set_new_password.html",{'user_id':user_id,'form':ResetForgettersPasswordForm()})
		else:
			return render(request,"unverified_number.html",{'referrer':'login'})
	elif user_id == 'generic' or user_id == 'used' or user_id == 'expired' or user_id == 'invalid':
		return render(request,"unverified_number.html",{'referrer':'login','reason':user_id})
	elif err['status'] == "NOT_AUTHENTICATED":
		return render(request,"dont_worry_just_authenticate.html",{'csrf':user_id,'referrer':'login','type':'forgetter'})
	else:
		return render(request, "try_again.html",{'type':'forgetter'})



def verify_user_number(request,*args,**kwargs):
	user_id = request.user.id
	##############################################################################################
	log_referrer(referrer=request.META.get('HTTP_REFERER',None),loc='user',user_id=user_id)
	##############################################################################################
	if is_mobile_verified(user_id):
		return render(request,"already_verified.html",{})
	else:
		csrf = get_user_csrf(user_id=str(user_id))
		if csrf:
			AK_ID, MN_data, err = get_requirements(request=request,csrf=csrf)
			if AK_ID and MN_data:
				if someone_elses_number(national_number=MN_data['national_number'], user_id=user_id):
					return render(request,"wrong_number.html",{'referrer':'home'})
				else:
					save_consumer_credentials.delay(AK_ID, MN_data, user_id)
					increase_user_points.delay(user_id=user_id, increment=NUMBER_VERIFICATION_BONUS)
					return render(request,"reward_earned.html",{})
			elif AK_ID == 'generic' or AK_ID == 'used' or AK_ID == 'expired' or AK_ID == 'invalid':
				return render(request,"unverified_number.html",{'referrer':'home','reason':AK_ID})
			elif err['status'] == "NOT_AUTHENTICATED":
				return render(request,"dont_worry_just_authenticate.html",{'csrf':csrf,'referrer':'home','type':'user'})
			else:
				return render(request,"unverified_number.html",{'referrer':'home'})
		else:
			return render(request,"try_again.html",{'type':'user'})


def verify_consumer_number(request,*args,**kwargs):
	user_id = request.user.id
	##############################################################################################
	log_referrer(referrer=request.META.get('HTTP_REFERER',None),loc='consumer',user_id=user_id)
	##############################################################################################
	data = get_buyer_snapshot(user_id=str(user_id))
	if data:
		AK_ID, MN_data, err = get_requirements(request=request,csrf=data["csrf"])
		if AK_ID and MN_data:
			if someone_elses_number(national_number=MN_data['national_number'], user_id=user_id):
				return render(request,"wrong_number.html",{'referrer':data["referrer"]})
			else:
				save_consumer_credentials.delay(AK_ID, MN_data, user_id)
				if data["redirect_to"]:
					return redirect("show_seller_number")
				else:
					return redirect("classified_listing")
		elif AK_ID == 'generic' or AK_ID == 'expired' or AK_ID == 'used' or AK_ID == 'invalid':
			return render(request,"unverified_number.html",{'referrer':'classified_listing','reason':AK_ID})
		elif err['status'] == "NOT_AUTHENTICATED":
			return render(request,"dont_worry_just_authenticate.html",{'csrf':data["csrf"],'referrer':data["referrer"],'type':'consumer'})
		else:
			# save_number_verification_error_data(user_id=user_id, err_data=err, err_type='1', on_fbs=request.META.get('HTTP_X_IORG_FBS',False), is_auth=request.user.is_authenticated(),which_flow='consumer')
			return render(request,"unverified_number.html",{'referrer':'classified_listing'})
	else:
		return render(request,"try_again.html",{'type':'consumer'})


def verify_basic_item_seller_number(request,*args,**kwargs):
	user_id = request.user.id
	##############################################################################################
	log_referrer(referrer=request.META.get('HTTP_REFERER',None),loc='seller',user_id=user_id)
	##############################################################################################
	CSRF = get_temporarily_saved_ad_data(user_id=str(user_id),only_csrf=True)
	AK_ID, MN_data, err = get_requirements(request=request, csrf=CSRF)
	if AK_ID and MN_data:
		if someone_elses_number(national_number=MN_data["national_number"],user_id=user_id):
			return render(request,"wrong_number.html",{'referrer':reverse_lazy("show_user_ads")})
		else:
			data = get_temporarily_saved_ad_data(user_id=str(user_id),full_ad=True)
			context={'desc':data["desc"],'is_new':data["is_new"], 'ask':data["ask"],'is_barter':data["is_barter"],'ad_id':data["ad_id"],\
			'seller_name':data["seller_name"],'city':data["city"],'AK_ID':AK_ID,'MN_data':MN_data,'user_id':user_id,'username':request.user.username,\
			'town':data["town"],'submission_device':data["submission_device"],'on_fbs':data["on_fbs"]}
			# register with Twilio's Notify service
			set_user_binding_with_twilio_notify_service.delay(user_id=user_id, phone_number=MN_data["number"])
			saved = save_basic_ad_data(context)
		if saved:
			return render(request,"basic_item_ad_submitted.html",{})
		else:
			pass
	elif AK_ID == 'expired' or AK_ID == 'used' or AK_ID == 'generic' or AK_ID == 'invalid':
		return render(request,"unverified_number.html",{'referrer':'classified_listing','reason':AK_ID})
	elif err['status'] == 'NOT_AUTHENTICATED':
		return render(request,"dont_worry_just_authenticate.html",{'csrf':CSRF,'type':'seller'})
	elif CSRF is None:
		return render(request,"try_again.html",{'type':'seller'})
	else:
		# save_number_verification_error_data(user_id=user_id, err_data=err, err_type='2', on_fbs=request.META.get('HTTP_X_IORG_FBS',False), is_auth=request.user.is_authenticated(),\
		# 	which_flow='seller')
		return render(request,"unverified_number.html",{'referrer':'classified_listing'})