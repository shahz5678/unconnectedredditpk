from django.shortcuts import render
from redis3 import save_basic_ad_data
from links.account_kit_config_manager import account_kit_handshake

def get_requirements(request):
	status = request.GET.get('status', None)
	auth_code = request.GET.get('code', None) #authorization code which our server may exchange for a user access token.
	state = request.GET.get('state', None) #to verify that FB's servers returned with the response
	return account_kit_handshake(request.session["csrf"], state, status, auth_code)

# def verify_new_user_number(request,*args,**kwargs):
# 	AK_ID, MN_data = get_requirements(request)

def verify_basic_item_seller_number(request,*args,**kwargs):
	AK_ID, MN_data = get_requirements(request)
	if AK_ID and MN_data:
		context={'desc':request.session["basic_item_description"],'is_new':request.session["basic_item_new"], 'ask':request.session["basic_item_ask"],\
		'is_barter':request.session["basic_item_barter"],'ad_id':request.session["ad_id"],'seller_name':request.session["seller_name"],'city':request.session["city"],\
		'AK_ID':AK_ID,'MN_data':MN_data,'user_id':request.user.id,'username':request.user.username} #{'national_number': '3335196812', 'number': '+923335196812', 'country_prefix': '92'}
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
		# couldn't verify phone number, decline user action
		# unverified_seller_number.html
		pass