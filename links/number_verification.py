from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from redis3 import save_basic_ad_data, someone_elses_number
from account_kit_config_manager import account_kit_handshake
from tasks import save_consumer_credentials, set_user_binding_with_twilio_notify_service

def get_requirements(request):
	status = request.GET.get('status', None)
	auth_code = request.GET.get('code', None) #authorization code which our server may exchange for a user access token.
	state = request.GET.get('state', None) #to verify that FB's servers returned with the response
	return account_kit_handshake(request.session["csrf"], state, status, auth_code)


def verify_consumer_number(request,*args,**kwargs):
	AK_ID, MN_data = get_requirements(request)
	# request.session.pop("csrf",None) # only pop "csrf" key once consumer credentials have been created
	if AK_ID and MN_data:
		if someone_elses_number(MN_data['national_number'], request.user.id):
			if "redirect_to" in request.session:
				request.session.pop("redirect_to",None) # this contained an ad_id that's not needed any more
			return render(request,"wrong_number.html",{'referrer':request.session.pop("referrer",None)})
		else:
			request.session.pop("csrf",None)
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
			'AK_ID':AK_ID,'MN_data':MN_data,'user_id':user_id,'username':request.user.username,'town':request.session["town"],'submission_device':request.session["submission_device"],\
			'on_fbs':request.session["on_fbs"]}
			# register with Twilio's Notify service
			set_user_binding_with_twilio_notify_service.delay(user_id=user_id, phone_number=MN_data["number"])
			saved = save_basic_ad_data(context)
		if saved:
			request.session.pop("basic_item_description",None)
			request.session.pop("basic_item_new",None)
			request.session.pop("basic_item_ask",None)
			request.session.pop("basic_item_barter",None)
			request.session.pop("ad_id",None)
			request.session.pop("city",None)
			request.session.pop("town",None)
			request.session.pop("csrf",None)
			request.session.pop("seller_name",None)
			request.session.pop("submission_device",None)
			request.session.pop("on_fbs",None)
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