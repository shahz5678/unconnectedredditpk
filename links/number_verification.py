from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from account_kit_config_manager import account_kit_handshake
from redis4 import save_careem_data, save_number_verification_error_data
from tasks import save_consumer_credentials, set_user_binding_with_twilio_notify_service
from redis3 import save_basic_ad_data, someone_elses_number, get_temporarily_saved_ad_data, reset_temporarily_saved_ad, get_buyer_snapshot

def get_requirements(request, csrf, careem=False):
	status = request.GET.get('status', None)
	auth_code = request.GET.get('code', None) #authorization code which our server may exchange for a user access token.
	state = request.GET.get('state', None) #to verify that FB's servers returned with the response
	if careem:
		return account_kit_handshake(request.session["csrf_careem"], state, status, auth_code)
	else:
		return account_kit_handshake(csrf, state, status, auth_code)


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



def verify_consumer_number(request,*args,**kwargs):
	# if request.user.is_authenticated():
	user_id = request.user.id
	data = get_buyer_snapshot(user_id=str(user_id))
	if data:
		AK_ID, MN_data, err = get_requirements(request=request,csrf=data["csrf"])
		if AK_ID and MN_data:
			if someone_elses_number(MN_data['national_number'], user_id):
				return render(request,"wrong_number.html",{'referrer':data["referrer"]})
			else:
				save_consumer_credentials.delay(AK_ID, MN_data, user_id)
				if data["redirect_to"]:
					return redirect("show_seller_number")
				else:
					return redirect("classified_listing")
		else:
			save_number_verification_error_data(user_id, err, err_type='1', on_fbs=request.META.get('HTTP_X_IORG_FBS',False), is_auth=request.user.is_authenticated(),which_flow='consumer')
			return render(request,"unverified_number.html",{})
	else:
		save_number_verification_error_data(user_id, {}, err_type='2', on_fbs=request.META.get('HTTP_X_IORG_FBS',False), is_auth=request.user.is_authenticated(),which_flow='consumer')
		return render(request,"unverified_number.html",{})


def verify_basic_item_seller_number(request,*args,**kwargs):
	user_id = request.user.id
	AK_ID, MN_data, err = get_requirements(request=request, csrf=get_temporarily_saved_ad_data(str(user_id),only_csrf=True))
	if AK_ID and MN_data:
		if someone_elses_number(MN_data["national_number"],user_id):
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
			reset_temporarily_saved_ad(str(user_id))
			return render(request,"basic_item_ad_submitted.html",{})
		else:
			pass
	else:
		save_number_verification_error_data(user_id, err, err_type='2', on_fbs=request.META.get('HTTP_X_IORG_FBS',False), is_auth=request.user.is_authenticated(),which_flow='seller')
		return render(request,"unverified_number.html",{'err':err})