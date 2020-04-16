from django.contrib.auth.models import User
from score import NUMBER_VERIFICATION_BONUS
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from unauth_forms import ResetForgettersPasswordForm
from account_kit_config_manager import account_kit_handshake
from redis4 import save_careem_data, get_temp_order_data, place_order, save_order_data, retrieve_uname #log_referrer, save_number_verification_error_data
from tasks import save_consumer_credentials, set_user_binding_with_twilio_notify_service, increase_user_points
from redis3 import save_basic_ad_data, someone_elses_number, get_temporarily_saved_ad_data, get_user_csrf, get_user_verified_number#, get_buyer_snapshot
from redis5 import get_personal_group_target_id_and_csrf, get_personal_group_anon_state, set_personal_group_mobile_num_cooloff, can_change_number
from group_views import enter_personal_group
from models import UserProfile
	

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
	user_id, MN_data, err = get_requirements(request=request,csrf=None, csrf_omitted=True)
	if user_id and MN_data:
		mob_nums = get_user_verified_number(user_id)
		if MN_data['national_number'] in mob_nums:
			# prompt user to change password
			return render(request,"unauth/set_new_password.html",{'user_id':user_id,'form':ResetForgettersPasswordForm()})
		else:
			return render(request,"unverified_number.html",{'referrer':'login','from_ecomm':False})
	elif user_id == 'generic' or user_id == 'used' or user_id == 'expired' or user_id == 'invalid':
		return render(request,"unverified_number.html",{'referrer':'login','reason':user_id,'from_ecomm':False})
	elif err['status'] == "NOT_AUTHENTICATED":
		return render(request,"dont_worry_just_authenticate.html",{'csrf':user_id,'referrer':'login','type':'forgetter','from_ecomm':False})
	else:
		return render(request, "try_again.html",{'type':'forgetter','from_ecomm':False})



def verify_user_number(request,*args,**kwargs):
	if request.mobile_verified:
		return render(request,"already_verified.html",{})
	else:
		user_id = request.user.id
		csrf = get_user_csrf(user_id=str(user_id))
		if csrf:
			AK_ID, MN_data, err = get_requirements(request=request,csrf=csrf)
			if AK_ID and MN_data:
				if someone_elses_number(national_number=MN_data['national_number'], user_id=user_id):
					return render(request,"wrong_number.html",{'referrer':'home','from_ecomm':False})
				else:
					save_consumer_credentials.delay(AK_ID, MN_data, user_id)
					increase_user_points.delay(user_id=user_id, increment=NUMBER_VERIFICATION_BONUS)
					return render(request,"verification/reward_earned.html",{})
			elif AK_ID == 'generic' or AK_ID == 'used' or AK_ID == 'expired' or AK_ID == 'invalid':
				return render(request,"unverified_number.html",{'referrer':'home','reason':AK_ID,'from_ecomm':False})
			elif err['status'] == "NOT_AUTHENTICATED":
				return render(request,"dont_worry_just_authenticate.html",{'csrf':csrf,'referrer':'home','type':'user','from_ecomm':False})
			elif err['status'] == "PARTIALLY_AUTHENTICATED":
				return render(request,"try_again.html",{'type':'user','from_ecomm':False})
			else:
				return render(request,"unverified_number.html",{'referrer':'home','from_ecomm':False})
		else:
			return render(request,"try_again.html",{'type':'user','from_ecomm':False})


# def verify_consumer_number(request,*args,**kwargs):
# 	user_id = request.user.id
# 	data = get_buyer_snapshot(user_id=str(user_id))
# 	if data:
# 		AK_ID, MN_data, err = get_requirements(request=request,csrf=data["csrf"])
# 		if AK_ID and MN_data:
# 			if someone_elses_number(national_number=MN_data['national_number'], user_id=user_id):
# 				return render(request,"wrong_number.html",{'referrer':data["referrer"],'from_ecomm':True})
# 			else:
# 				save_consumer_credentials.delay(AK_ID, MN_data, user_id)
# 				if data["redirect_to"]:
# 					return redirect("show_seller_number")
# 				else:
# 					return redirect("classified_listing")
# 		elif AK_ID == 'generic' or AK_ID == 'expired' or AK_ID == 'used' or AK_ID == 'invalid':
# 			return render(request,"unverified_number.html",{'referrer':'classified_listing','reason':AK_ID,'from_ecomm':True})
# 		elif err['status'] == "NOT_AUTHENTICATED":
# 			return render(request,"dont_worry_just_authenticate.html",{'csrf':data["csrf"],'referrer':data["referrer"],'type':'consumer','from_ecomm':True})
# 		else:
# 			return render(request,"unverified_number.html",{'referrer':'classified_listing','from_ecomm':True})
# 	else:
# 		return render(request,"try_again.html",{'type':'consumer','from_ecomm':True})


def verify_basic_item_seller_number(request,*args,**kwargs):
	user_id = request.user.id
	CSRF = get_temporarily_saved_ad_data(user_id=str(user_id),only_csrf=True)
	AK_ID, MN_data, err = get_requirements(request=request, csrf=CSRF)
	if AK_ID and MN_data:
		if someone_elses_number(national_number=MN_data["national_number"],user_id=user_id):
			return render(request,"wrong_number.html",{'referrer':reverse_lazy("show_user_ads"),'from_ecomm':True})
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
		return render(request,"unverified_number.html",{'referrer':'classified_listing','reason':AK_ID,'from_ecomm':True})
	elif err['status'] == 'NOT_AUTHENTICATED':
		return render(request,"dont_worry_just_authenticate.html",{'csrf':CSRF,'type':'seller','from_ecomm':True})
	elif CSRF is None:
		return render(request,"try_again.html",{'type':'seller','from_ecomm':True})
	else:
		return render(request,"unverified_number.html",{'referrer':'classified_listing','from_ecomm':True})

####################################################################################


def verify_personal_group_user(request):
	"""
	Processes mobile verification of personal group user
	"""
	user_id = request.user.id
	tid, csrf = get_personal_group_target_id_and_csrf(user_id)
	if csrf:
		AK_ID, MN_data, err = get_requirements(request=request,csrf=csrf)
		if AK_ID and MN_data:
			if someone_elses_number(national_number=MN_data['national_number'], user_id=user_id):
				return render(request,"wrong_number.html",{'referrer':'personal_group','tid':tid,'from_ecomm':False})
			elif not can_change_number(user_id):
				return render(request,"already_verified.html",{'from_personal_group':True,'tid':target_id})
			else:
				save_consumer_credentials.delay(AK_ID, MN_data, user_id)
				set_personal_group_mobile_num_cooloff(user_id)
				own_anon_status, their_anon_status, group_id = get_personal_group_anon_state(user_id, tid)
				if their_anon_status is None:
					return redirect('home')
				else:
					return render(request,"personal_group/sms_settings/personal_group_successful_mob_verification.html",{'tid':tid,\
						'avatar':None if their_anon_status else UserProfile.objects.filter(user_id=tid).values_list('avatar',flat=True)[0],\
						'their_anon':their_anon_status,'name':retrieve_uname(tid,decode=True)})
		elif AK_ID == 'generic' or AK_ID == 'used' or AK_ID == 'expired' or AK_ID == 'invalid':
			return render(request,"unverified_number.html",{'referrer':'personal_group','tid':tid,'reason':AK_ID,'from_ecomm':False})
		elif err['status'] == "NOT_AUTHENTICATED":
			return render(request,"dont_worry_just_authenticate.html",{'csrf':csrf,'tid':tid,'type':'personal_group_chatter','from_ecomm':False})
		elif err['status'] == "PARTIALLY_AUTHENTICATED":
			return render(request,"try_again.html",{'type':'personal_group_chatter','from_ecomm':False,'tid':tid})
		else:
			return render(request,"unverified_number.html",{'referrer':'personal_group','tid':tid,'from_ecomm':False})
	else:
		return render(request,"try_again.html",{'type':'personal_group_chatter','from_ecomm':False,'tid':tid})

	

####################################################################################
def verify_buyer_number(request):
	# try:
	# 	csrf = request.session["csrf"]
	# except:
	# 	return redirect("mobile_shop")
	csrf = request.session["csrf"]	
	AK_ID, MN_data, err = get_requirements(request=request,csrf=csrf)
	if AK_ID and MN_data:
		user_id = request.user.id
		if someone_elses_number(national_number=MN_data['national_number'], user_id=user_id):
			# mp.track(request.user.id, 'M_S_7.2 someelses Phone')
			return render(request,"wrong_number.html",{'referrer':'mobile_shop'})
		else:
			# mp.track(request.user.id, 'M_S_7.3 Phone confirmed')
			save_consumer_credentials.delay(AK_ID, MN_data, user_id)
			order_data =  get_temp_order_data(user_id)
			order_data['phonenumber']=MN_data['number']
			merch_id = order_data['merch_id']
			saved = save_order_data(order_data)
			if saved:
				# mp.track(request.user.id, 'M_S_7 On confirm order')
				return redirect("confirm_order")#,{'merch_id':merch_id})
			else:
				# mp.track(request.user.id, 'M_S_E phone verification 2')
				return render(request,"404.html",{})
	else:
		# mp.track(request.user.id, 'M_S_7.4 canceled phone verification')
		return render(request,"dont_worry_just_authenticate.html",{'csrf':csrf,'type':'mobile_buyer','from_ecomm':False})

		####replace with page reminding importance of number verification

	# next step: now check if this is a uniquely new number, or is this someone else's number (use func someone_elses_number from redis3)
	# next step: now that you're sure the number hasn't been used before, use save_consumer_number (redis3) to save the number to our DB
	# next step: render the template that helps use complete the order

	# else:
	# 	print "data not received"
	# 	return render(request,"careem_number_already_used.html",{})

#			if someone_elses_number(national_number=MN_data['national_number'], user_id=user_id):
#				return render(request,"wrong_number.html",{'referrer':data["referrer"]})
#			else:
#			save_consumer_credentials.delay(AK_ID, MN_data, user_id)
#			if data["redirect_to"]:
	# 			return redirect("show_seller_number")
	# 		else:
	# 			return redirect("classified_listing")
	# 	elif err['status'] == "NOT_AUTHENTICATED":
	# 		return render(request,"dont_worry_just_authenticate.html",{'csrf':data["csrf"],'referrer':data["referrer"],'type':'consumer'})
	# 	else:
	# 		save_number_verification_error_data(user_id=user_id, err_data=err, err_type='1', on_fbs=request.META.get('HTTP_X_IORG_FBS',False), is_auth=request.user.is_authenticated(),which_flow='consumer')
	# 		return render(request,"unverified_number.html",{})
	# else:
	# 	return render(request,"try_again.html",{'type':'consumer'})


#	return render(request,"buyer_verification.html")




