from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from redis3 import save_basic_ad_data, someone_elses_number
from redis4 import save_careem_data
from account_kit_config_manager import account_kit_handshake
from tasks import save_consumer_credentials, set_user_binding_with_twilio_notify_service

def get_requirements(request, careem=False):
	status = request.GET.get('status', None)
	auth_code = request.GET.get('code', None) #authorization code which our server may exchange for a user access token.
	state = request.GET.get('state', None) #to verify that FB's servers returned with the response
	if careem:
		return account_kit_handshake(request.session["csrf_careem"], state, status, auth_code)
	else:
		return account_kit_handshake(request.session["csrf"], state, status, auth_code)


def verify_careem_applicant(request,*args,**kwargs):
	AK_ID, MN_data = get_requirements(request, careem=True)
	# print "AK_ID is: %s" % AK_ID
	# print "MN_data is: %s" % MN_data
	# print request.session['firstname']
	# print request.session['lastname']
	# print request.session['cnic']
	# print request.session['city']
	# print request.session['license']
	print MN_data['number']
	car_phonenumber = MN_data['number']
	car_firstname = request.session['firstname']
	car_lastname = request.session['lastname']
	car_cnic = request.session['cnic']
	car_city = request.session['city']
	car_license = request.session['license']

	# print car_phonenumber
	# print car_firstname  
	# print car_lastname 
	# print car_cnic  
	# print car_city 
	# print car_license  
	# print request.user.id
	careem_data = {'firstname':car_firstname,'lastname':car_lastname,'cnic':car_cnic,\
	'city':car_city,'license':car_license,'phonenumber':car_phonenumber,'user_id':request.user.id}
	# print careem_data

	saved = save_careem_data(careem_data)
	print saved
	request.session.pop('firstname',None) 
	request.session.pop('lastname',None)
	request.session.pop('cnic',None)
	request.session.pop('city',None)
	request.session.pop('license',None)
	request.session.pop('csrf_careem',None)
	if saved:
		return render(request,"careem_application_submitted.html",{})
	else:
		return render(request,"careem_number_already_used.html",{})
	# print
	# print



def verify_consumer_number(request,*args,**kwargs):
	AK_ID, MN_data = get_requirements(request)
	if AK_ID and MN_data:
		if someone_elses_number(MN_data['national_number'], request.user.id):
			if "redirect_to" in request.session:
				request.session.pop("redirect_to",None) # this contained an ad_id that's not needed any more
			return render(request,"wrong_number.html",{'referrer':request.session.pop("referrer",None)})
		else:
			save_consumer_credentials.delay(AK_ID, MN_data, request.user.id)
			if "redirect_to" in request.session:
				return redirect("show_seller_number")
			else:
				return redirect("classified_listing")
	else:
		return render(request,"unverified_number.html",{})


def verify_basic_item_seller_number(request,*args,**kwargs):
	AK_ID, MN_data = get_requirements(request)
	if AK_ID and MN_data:
		if someone_elses_number(MN_data["national_number"],request.user.id):
			return render(request,"wrong_number.html",{'referrer':reverse_lazy("show_user_ads")})
		else:
			user_id = request.user.id
			context={'desc':request.session["basic_item_description"],'is_new':request.session["basic_item_new"], 'ask':request.session["basic_item_ask"],\
			'is_barter':request.session["basic_item_barter"],'ad_id':request.session["ad_id"],'seller_name':request.session["seller_name"],'city':request.session["city"],\
			'AK_ID':AK_ID,'MN_data':MN_data,'user_id':user_id,'username':request.user.username}#,'outer_leads':request.session["outer_leads_allowed"]}
			# register with Tilio's Notify service
			set_user_binding_with_twilio_notify_service.delay(user_id=user_id, phone_number=MN_data["number"])
			saved = save_basic_ad_data(context)
		if saved:
			request.session.pop("basic_item_description",None)
			request.session.pop("basic_item_new",None)
			request.session.pop("basic_item_ask",None)
			request.session.pop("basic_item_barter",None)
			request.session.pop("ad_id",None)
			request.session.pop("city",None)
			request.session.pop("csrf",None)
			request.session.pop("seller_name",None)
			request.session.pop("photo1",None)
			request.session.pop("photo2",None)
			request.session.pop("photo3",None)
			request.session.pop("photo1_hash",None)
			request.session.pop("photo2_hash",None)
			request.session.pop("photo3_hash",None)
			request.session.modified = True
			return render(request,"basic_item_ad_submitted.html",{})
		else:
			pass
	else:
		return render(request,"unverified_number.html",{})