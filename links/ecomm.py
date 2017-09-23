from models import Photo, UserProfile
import ast, json, time, uuid, os
from views import get_page_obj
# from mixpanel import Mixpanel
# from send_sms import get_all_bindings_to_date
# from redis1 import first_time_shopper, add_shopper
# from unconnectedreddit.settings import MIXPANEL_TOKEN
from image_processing import clean_image_file_with_hash
from page_controls import ADS_TO_APPROVE_PER_PAGE, APPROVED_ADS_PER_PAGE
from redis4 import save_ad_desc, return_referrer_logs,get_order_id, save_order_data, show_new_orders,\
 place_order, get_temp_order_data, check_orders_processing#, get_city_shop_listing#, get_city_shop_listing
from score import CITIES, ON_FBS_PHOTO_THRESHOLD, OFF_FBS_PHOTO_THRESHOLD, LEAST_CLICKS, MOST_CLICKS, MEDIUM_CLICKS, LEAST_DURATION, MOST_DURATION
from tasks import upload_ecomm_photo, save_unfinished_ad, enqueue_sms, sanitize_unused_ecomm_photos, set_user_binding_with_twilio_notify_service, \
save_ecomm_photo_hash, detail_click_logger,enqueue_buyer_sms
from ecomm_forms import EcommCityForm, BasicItemDetailForm, BasicItemPhotosForm, SellerInfoForm, VerifySellerMobileForm, EditFieldForm#, AddShopForm 
from redis1 import add_exchange_visitor, first_time_exchange_visitor, add_photo_ad_visitor, first_time_photo_ads_visitor#, first_time_classified_contacter, add_classified_contacter
from redis3 import log_unserviced_city, log_completed_orders, get_basic_item_ad_id, get_unapproved_ads, edit_single_unapproved_ad, del_single_unapproved_ad, \
move_to_approved_ads, get_approved_ad_ids, get_ad_objects, get_all_user_ads, get_single_approved_ad, get_classified_categories, get_approved_places, namify, \
get_and_set_classified_dashboard_visitors, edit_unfinished_ad_field, del_orphaned_classified_photos, get_unfinished_photo_ids_to_delete, lock_unapproved_ad, \
unlock_unapproved_ad, who_locked_ad, get_user_verified_number, save_basic_ad_data, is_mobile_verified, get_city_ad_ids, get_all_pakistan_ad_count,\
string_tokenizer, ad_owner_id, process_ad_expiry, toggle_SMS_setting, get_SMS_setting, save_ad_expiry_or_sms_feedback, set_ecomm_photos_secret_key, \
get_and_delete_ecomm_photos_secret_key, reset_temporarily_saved_ad, temporarily_save_ad, get_temporarily_saved_ad_data, get_item_name, \
check_status_of_temporarily_saved_ad#, temporarily_save_buyer_snapshot, get_buyer_snapshot, get_seller_details, populate_ad_list, retrieve_spam_writers
from django.db.models import F

from links.ads_forms import BuyerForm
from django.middleware import csrf
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control

#################################################################

# from optimizely_config_manager import OptimizelyConfigManager
# from unconnectedreddit.optimizely_settings import PID

# config_manager = OptimizelyConfigManager(PID)

#################################################################

# mp = Mixpanel(MIXPANEL_TOKEN)
from mixpanel import Mixpanel
from unconnectedreddit.settings import MIXPANEL_TOKEN

mp = Mixpanel(MIXPANEL_TOKEN)
#################################################################

MERCH = { 
'1': {'price':'3600' ,'discounted_price':'3600', 'points_cost': '5000', 'discount':'Rs. 400', 'name':'Qmobile Noir X29' }, \
'2': {'price':'4500' ,'discounted_price':'4500', 'points_cost': '5000', 'discount':'Rs. 500', 'name':'QMobile Noir X33'}, \
'3': {'price':'6120' ,'discounted_price':'6120', 'points_cost': '5000', 'discount':'Rs. 680', 'name':'QMobile Noir i8i'}, \
'4': {'price':'6570' ,'discounted_price':'6570', 'points_cost': '5000', 'discount':'Rs. 730', 'name':'QMobile Noir i6 Metal One'}, \
'5': {'price':'8100','discounted_price':'8100', 'points_cost': '5000', 'discount':'Rs. 900', 'name':'Samsung J1 Mini Prime'}, \
'6': {'price':'9630','discounted_price':'9630', 'points_cost': '5000', 'discount':'Rs. 1070', 'name':'QMobile Noir S6'}, \
}

LOCATION = { 
'khi': 'Karachi', \
'lhr': 'Lahore', \
'isb': 'Islamabad', \
'rwp': 'Rawalpindi', \
'pes': 'Peshawar', \
'hyd': 'Hyderabad', \
'fsd': 'Faisalabad', \
'mul': 'Multan', \
'sbi': 'Swabi',\
'atk': 'Attock'
}


def get_photo_urls(photo_ids):
	return {x['id']:x['image_file'] for x in Photo.objects.filter(id__in=photo_ids).values('id','image_file')}


def insert_MN_data(ad_list):
	for ad in ad_list:
		ad["MN_data"] = ast.literal_eval(ad["MN_data"])
	return ad_list

# inserts actual objects for photo_ids in ad list (of dictionaries)
def insert_photo_urls(ad_list, photo_objs, photo_ids, tup=False, photo_tup=False, only_cover=False, must_eval_photo_list=False):
	if tup:
		for ad,ad_id in ad_list:
			if "photos" in ad:
				photo_list = ast.literal_eval(ad["photos"]) if must_eval_photo_list else ad["photos"]
				number_of_photos, counter = len(photo_list), 0
				while counter < number_of_photos:
					# /classified_approval_dashboard/
					index = int(photo_list[counter][0]) if photo_tup else int(photo_list[counter])
					ad["photos"][counter] = (photo_objs[index],photo_list[counter][1],index) if photo_tup else (photo_objs[index],photo_list[counter],index)
					counter += 1
	else:
		for ad in ad_list:
			if "photos" in ad:
				photo_list = ast.literal_eval(ad["photos"]) if must_eval_photo_list else ad["photos"]
				number_of_photos, counter = len(photo_list), 0
				while counter < number_of_photos:
					index = int(photo_list[counter][0]) if photo_tup else int(photo_list[counter])
					if str(index) in photo_ids:
						if only_cover:
							# /buy_and_sell/
							# only append cover photo (for ad listings - only ad detail pages have all photos)
							ad["photos"] = (photo_objs[index],photo_list[counter][1]) if photo_tup else (photo_objs[index],photo_list[counter])
							break
						else:
							# /meray_ads
							# append all photos (but only cover has 'url' attached)
							photo_list[counter] = (photo_objs[index],photo_list[counter][1]) if photo_tup else (photo_objs[index],photo_list[counter])
							ad["photos"] = photo_list
					counter += 1
	return ad_list


# extracts photo_ids from the body of the ad, returning the ids in a list
def get_photo_ids(ad_body, photo_tup=False, only_cover=False, must_eval_ad=False, must_eval_photo_list=False):
	photo_ids = []
	ad = ast.literal_eval(ad_body) if must_eval_ad else ad_body
	if "photos" in ad:
		if must_eval_photo_list:
			for entry in ast.literal_eval(ad["photos"]):
				if only_cover:
					# only append cover photo, rest not needed
					if entry[1] == True:
						photo_ids.append(entry[0]) if photo_tup else photo_ids.append(entry)
				else:
					photo_ids.append(entry[0]) if photo_tup else photo_ids.append(entry)
		else:
			for entry in ad["photos"]:
				if only_cover:
					# only append cover photo, rest not needed
					if entry[1] == True:
						photo_ids.append(entry[0]) if photo_tup else photo_ids.append(entry)
				else:
					photo_ids.append(entry[0]) if photo_tup else photo_ids.append(entry)
	return photo_ids


# preps ad list for display 
def process_ad_objects(ad_list, tup=False, photo_tup=False, only_cover=False, must_eval_ad=False, must_eval_photo_list=False, must_eval_MN_data=False):
	"""
	tup: is the ad_list a list of tuples of the form [(ad_body,ad_id),(ad_body,ad_id).....]
	photo_tup: is the "key" inside an ad a list of tuples of the form [(photo_id, True)(photo_id, False),......] True or False designates cover photo
	only_cover: should an image solely for the cover photo be returned, or for all photos connected to an ad?
	must_eval_ad: apply ast.literal_eval() in case the ad is made up of a string instead of a python dictionary
	must_eval_photo_list: apply ast.literal_eval() in case values in the "photo" key are a string, instead of a python list
	"""
	ads, photo_ids = [], []
	if tup:
		for obj in ad_list:
			photo_ids += get_photo_ids(ad_body=obj[0], must_eval_ad=must_eval_ad, photo_tup=photo_tup)
			ads.append((ast.literal_eval(obj[0]),obj[1])) # changing string ad body to evaluated ad body from ad_list
		if not photo_ids:
			return ads
		else:
			return insert_photo_urls(ads, get_photo_urls(photo_ids), photo_ids, tup=tup, photo_tup=photo_tup)
	else:
		for ad in ad_list:
			photo_ids += get_photo_ids(ad_body=ad, only_cover=only_cover, must_eval_photo_list=must_eval_photo_list, photo_tup=photo_tup)
		if must_eval_MN_data:
			ad_list = insert_MN_data(ad_list)
		if not photo_ids:
			return ad_list
		else:
			return insert_photo_urls(ad_list, get_photo_urls(photo_ids), photo_ids, only_cover=only_cover,must_eval_photo_list=must_eval_photo_list, photo_tup=photo_tup)

def get_device(request):
	# return '1'
	if request.is_feature_phone:
		return '1'
	elif request.is_phone:
		return '2'
	elif request.is_tablet:
		return '4'
	elif request.is_mobile:
		return '5'
	else:
		return '3' # probably desktop

def get_photo_strings(photo_list):
 	counter, photos = 1, []
 	for photo in photo_list:
 		if photo:
 			photos.append([photo,"photo"+str(counter),"photo"+str(counter)+"_hash"])
 		else:
 			photos.append([None, None, None])
 		counter += 1
 	return photos

def is_repeated(avghash,dict_):
	if dict_["photo1_hash"]:
		if ast.literal_eval(dict_["photo1_hash"])[1] == avghash:
			return True
	if dict_["photo2_hash"]:
		if ast.literal_eval(dict_["photo2_hash"])[1] == avghash:
			return True
	if dict_["photo3_hash"]:
		if ast.literal_eval(dict_["photo3_hash"])[1] == avghash:
			return True
	return False

def photo_size_exceeded(on_fbs,image):
	if on_fbs:
		if image.size > ON_FBS_PHOTO_THRESHOLD:
			return True, 'size_exceeded_on_fbs'
		else:
			# return True, ON_FBS_PHOTO_THRESHOLD
			return False, 0
	else:
		if image.size > OFF_FBS_PHOTO_THRESHOLD:
			return True, 'size_exceeded_off_fbs'
		else:
			# return True, OFF_FBS_PHOTO_THRESHOLD
			return False, 0

############################## Unregistered Users ###################################


def redirect_to_social_section(request):
	return render(request,"chat_and_photos.html",{})


############################## Buyer Functionality ###################################

@csrf_protect
def process_ad_expiry_or_sms_feedback(request,*args,**kwargs):
	if request.method == "POST":
		form = EditFieldForm(data=request.POST)
		ad_id = request.POST.get('ad_score',None)
		type_ = request.POST.get('type',None)
		if form.is_valid():
			feedback = form.cleaned_data['text_field']
			save_ad_expiry_or_sms_feedback(ad_id,feedback,type_)
			return redirect("show_user_ads")
		else:
			return render(request,"ad_expiry_or_sms_feedback.html",{'ad_id':ad_id,'form':form})
	else:
		return redirect("show_user_ads")


@csrf_protect
def change_my_sms_settings(request,*args,**kwargs):
	if request.method == "POST":
		ad_id = request.POST.get('ad_score',None)
		decision = request.POST.get('dec',None)
		own_ad = str(request.user.id) == ad_owner_id(str(float(ad_id)))
		if own_ad:
			if decision:
				if decision == '1':
					old_setting = toggle_SMS_setting(str(float(ad_id)))
					if old_setting == '1':
						# i.e. the service has been turned off, get feedback why
						form = EditFieldForm()
						return render(request,"ad_expiry_or_sms_feedback.html",{'ad_id':ad_id,'form':form,'type':'sms'})
					else:
						return redirect("show_user_ads")	
				elif decision == '0':
					return redirect("show_user_ads")
				else:
					return render(request,"404.html",{'from_ecomm':True})		
			else:
				current_setting = get_SMS_setting(str(float(ad_id)))
				return render(request,"change_ad_sms_settings.html",{'ad_id':ad_id,'current_setting':current_setting})
		else:
			return redirect("show_user_ads")
	else:
		return redirect("show_user_ads")

@csrf_protect
def expire_my_ad(request,*args,**kwargs):
	if request.method == "POST":
		ad_id = request.POST.get('ad_score',None)
		decision = request.POST.get('dec',None)
		own_ad = str(request.user.id) == ad_owner_id(str(float(ad_id)))
		if own_ad:
			if decision:
				if decision == '1' and str(request.user.id) == ad_owner_id(str(float(ad_id))):
					process_ad_expiry(str(float(ad_id)),type_list = False)
					form = EditFieldForm()
					return render(request,"ad_expiry_or_sms_feedback.html",{'ad_id':ad_id,'form':form,'type':'expiry'})
			else:
				return render(request,"confirm_ad_expiry.html",{'ad_id':ad_id})
		return redirect("show_user_ads")
	else:
		return redirect("show_user_ads")

def ad_detail(request,ad_id,*args,**kwargs):
	ad_body = get_single_approved_ad(float(ad_id))
	if ad_body:
		approved_user_ad = process_ad_objects(ad_list = [ad_body],must_eval_photo_list=True,photo_tup=True, must_eval_MN_data=True)[0]
		detail_click_logger.delay(ad_id, request.user.id)
		return render(request,"classified_detail.html",{'is_feature_phone':get_device(request),'ad_body':approved_user_ad,'referrer':request.META.get('HTTP_REFERER',None)})
	else:
		# id ad_id doesn't exist (E.g. deleted, or never existed)
		return redirect("classified_listing")

@csrf_protect
def process_unfinished_ad(request,*args,**kwargs):
	next_step = request.POST.get('next_step',None)
	ad_id = request.POST.get('ad_score',None)
	editor_id = request.POST.get('EID',None)
	user_id = request.user.id
	editor_id = int(editor_id)
	if editor_id == user_id:
		if next_step == 'delete':
			photo_ids = get_unfinished_photo_ids_to_delete(ad_id)
			del_orphaned_classified_photos(user_id=str(user_id),ad_id=ad_id)
			if photo_ids:
				sanitize_unused_ecomm_photos.delay(photo_ids)
			# reset_temporarily_saved_ad(str(user_id)) # already deleted in del_orphaned_classified_photos
			return redirect("show_user_ads")
		elif next_step == 'verify mobile':
			form = VerifySellerMobileForm()
			CSRF = csrf.get_token(request)
			temporarily_save_ad(user_id=str(user_id),csrf=CSRF,description=request.POST.get('desc',None),ask=request.POST.get('ask',None),\
				is_new=request.POST.get('is_new',None),is_barter=request.POST.get('is_barter',None),seller_name=request.POST.get('seller_name',None),\
				city=request.POST.get('city',None),town=request.POST.get('town',None))
			from_meray_ads = request.POST.get('from_meray_ads',None)
			return render(request,"verify_seller_number.html",{'csrf':CSRF,'form':form,'from_meray_ads':from_meray_ads})
		else:
			return render(request,"404.html",{'from_ecomm':True})
	else:
		return render(request,"404.html",{'from_ecomm':True})


def show_user_ads(request,*args,**kwargs):
	unapproved_user_ads = []
	locations_and_counts = get_approved_places(withscores=True)
	ads = get_all_user_ads(request.user.id)
	unfinished_user_ad, unapproved_user_ads, approved_user_ads, expired_user_ads = ads[0], ads[1], ads[2], ads[3]
	unapproved_count, approved_count, expired_count = 0, 0, 0
	if unfinished_user_ad:
		unfinished_user_ad = process_ad_objects(ad_list = [unfinished_user_ad],must_eval_photo_list=True,photo_tup=False)[0]
	if unapproved_user_ads:
		unapproved_user_ads = process_ad_objects(ad_list = unapproved_user_ads,must_eval_photo_list=False,photo_tup=True)
		unapproved_count = len(unapproved_user_ads)
	else:
		unapproved_user_ads = []
		unapproved_count = 0
	approved_count = 0
	if approved_user_ads:
		approved_user_ads = process_ad_objects(ad_list = approved_user_ads,must_eval_photo_list=True,photo_tup=True)
		approved_count = len(approved_user_ads)
	if expired_user_ads:
		expired_user_ads = process_ad_objects(ad_list = expired_user_ads,must_eval_photo_list=True,photo_tup=True)
		expired_count = len(expired_user_ads)
	return render(request,"own_classifieds.html",{'unfinished':unfinished_user_ad,'unapproved':unapproved_user_ads,'approved':approved_user_ads,\
		'unapproved_count':unapproved_count, 'approved_count':approved_count, 'top_3_locs':locations_and_counts[:3], 'other_cities':len(locations_and_counts[3:]),\
		'ad_count':get_all_pakistan_ad_count(),'is_feature_phone':get_device(request),'expired':expired_user_ads,'expired_count':expired_count})

############################### Display Approved Ads ##############################


# can a person get here WITHOUT verifying?
# @csrf_protect
# def classified_tutorial_dec(request,*args,**kwargs):
# 	if request.method == 'POST':
# 		dec = request.POST.get('dec',None)
# 		ad_id = request.POST.get('ad_id',None)
# 		referrer = request.POST.get('referrer',None)
# 		if dec == 'Theek hai':
# 			temporarily_save_buyer_snapshot(user_id=str(request.user.id), referrer=referrer,redirect_to=ad_id)
# 			return redirect("show_seller_number")
# 		elif dec == 'Rehnay do':
# 			if referrer:
# 				return redirect(referrer)
# 			else:
# 				return redirect("classified_listing")
# 		else:
# 			return render(request,"404.html",{'from_ecomm':True})
# 	else:
# 		return render(request,"404.html",{'from_ecomm':True})


# @csrf_protect
# def show_seller_number(request,*args,**kwargs):
# 	user_id = request.user.id
# 	is_verified = is_mobile_verified(user_id)
# 	if request.method == 'POST':
# 		ad_id = request.POST.get('ad_id',None)
# 		if not is_verified:
# 			# verify this person' mobile
# 			CSRF = csrf.get_token(request)
# 			temporarily_save_buyer_snapshot(user_id=str(user_id), referrer=request.META.get('HTTP_REFERER',None), redirect_to=ad_id, csrf=CSRF, uid=user_id)
# 			return render(request,"ecomm_newbie_verify_mobile.html",{'ad_id':ad_id,'csrf':CSRF})
# 		elif is_verified and first_time_classified_contacter(user_id):
# 			# show first_time tutorial and set number exchange expectation
# 			add_classified_contacter(user_id)
# 			referrer = request.META.get('HTTP_REFERER',None)
# 			return render(request,"classified_contacter_tutorial.html",{'ad_id':ad_id, 'referrer':referrer})
# 		elif is_verified:
# 			seller_details, is_unique_click, buyer_number, is_expired = get_seller_details(request.user.id, ad_id)
# 			MN_data = ast.literal_eval(seller_details["MN_data"])
# 			if is_unique_click:
# 				# enqueue sms
# 				if is_expired:
# 					enqueue_sms.delay(mobile_number=MN_data["number"], ad_id=int(float(ad_id)), status='unique_click_plus_expiry', buyer_number=buyer_number)
# 				else:
# 					send_sms = get_SMS_setting(str(float(ad_id)))
# 					if send_sms == '1':
# 						enqueue_sms.delay(mobile_number=MN_data["number"], ad_id=int(float(ad_id)), status='unique_click', buyer_number=buyer_number)
# 			return render(request,"show_seller_number.html",{'seller_details':seller_details, "MN_data":MN_data, 'device':get_device(request),\
# 				'referrer':request.META.get('HTTP_REFERER',None)})
# 		else:
# 			return render(request,"404.html",{'from_ecomm':True})
# 	else:
# 		buyer_snapshot = get_buyer_snapshot(user_id=str(user_id))
# 		if "redirect_to" in buyer_snapshot:
# 			ad_id = buyer_snapshot.get("redirect_to",None)
# 			referrer = buyer_snapshot.get("referrer",None)
# 			if is_verified and first_time_classified_contacter(user_id):
# 				add_classified_contacter(user_id)
# 				return render(request,"classified_contacter_tutorial.html",{'ad_id':ad_id, 'referrer':referrer})	
# 			elif is_verified:
# 				seller_details, is_unique_click, buyer_number, is_expired = get_seller_details(user_id, ad_id)
# 				MN_data = ast.literal_eval(seller_details["MN_data"])
# 				if is_unique_click:
# 					# enqueue sms
# 					if is_expired:
# 						enqueue_sms.delay(mobile_number=MN_data["number"], ad_id=int(float(ad_id)), status='unique_click_plus_expiry', buyer_number=buyer_number)
# 					else:
# 						send_sms = get_SMS_setting(str(float(ad_id)))
# 						if send_sms == '1':
# 							enqueue_sms.delay(mobile_number=MN_data["number"], ad_id=int(float(ad_id)), status='unique_click', buyer_number=buyer_number)
# 				return render(request,"show_seller_number.html",{'seller_details':seller_details, "MN_data":MN_data, 'device':get_device(request),\
# 					'referrer':referrer})#request.META.get('HTTP_REFERER',None)})
# 			else:
# 				return render(request,"404.html",{'from_ecomm':True})
# 		else:
# 			return render(request,"404.html",{'from_ecomm':True})


def classified_listing(request,city=None,*args,**kwrags):
	url_name = request.resolver_match.url_name
	exchange = True if (url_name == 'exchange_classified_listing' or url_name == 'city_exchange_classified_listing') else False
	if exchange and request.user.is_authenticated():
		if first_time_exchange_visitor(request.user.id):
			add_exchange_visitor(request.user.id)
			return render(request,"exchange_classified_tutorial.html",{'url_name':url_name,'city':city})
	page_num = request.GET.get('page', '1')
	all_ad_ids = get_city_ad_ids(city_name=city, exchange=exchange, photos=False) if city else get_approved_ad_ids(exchange=exchange, photos=False)
	page_obj = get_page_obj(page_num,all_ad_ids,APPROVED_ADS_PER_PAGE)
	ads = get_ad_objects(page_obj.object_list)
	submissions = process_ad_objects(ad_list=ads, only_cover=True, must_eval_photo_list=True, photo_tup=True, must_eval_MN_data=True)
	if city:
		city = string_tokenizer(city)
		origin = city
	else:
		city, origin = None, 'global'
	return render(request,"classifieds.html",{'ads':submissions,'page':page_obj,'city':city,'origin':origin,'is_feature_phone':get_device(request), \
			'exchange':exchange, 'photos':None, 'variation':'ads_and_badla'})


def city_list(request,*args,**kwargs):
	locs_and_ad_counts = get_approved_places(withscores=True)
	return render(request,"city_list.html",{'cities':locs_and_ad_counts,'ad_count':get_all_pakistan_ad_count(),'num_of_cities':len(locs_and_ad_counts)})


############################### Ad Approval & Editing ###############################

# all functions within this section are gated by the who_locked_ad function

def get_field(query_dict):
	edit_desc = query_dict.get('edit_desc',None)
	edit_is_new = query_dict.get('edit_is_new',None)
	edit_is_barter = query_dict.get('edit_is_barter',None)
	edit_town = query_dict.get('edit_town',None)
	edit_ask = query_dict.get('edit_ask',None)
	edit_name = query_dict.get('edit_name',None)
	edit_city = query_dict.get('edit_city',None)
	edit_title = query_dict.get('edit_title',None)
	edit_categ = query_dict.get('edit_categ',None)
	# city name is needed in one special case (for ascertaining towns). Other than that, this is a waste
	ad_city = query_dict.get('ad_city',None)
	if edit_desc:
		return edit_desc, 'desc', ad_city
	if edit_is_new:
		return edit_is_new, 'is_new', ad_city
	if edit_is_barter:
		return edit_is_barter, 'is_barter', ad_city
	if edit_town:
		return edit_town, 'town', ad_city
	if edit_ask:
		return edit_ask, 'ask', ad_city
	if edit_name:
		return edit_name, 'seller_name', ad_city
	if edit_city:
		return edit_city, 'city', ad_city
	if edit_title:
		return edit_title, 'title', ad_city
	if edit_categ:
		return edit_categ, 'categ', ad_city

def get_help_text(text,admin_mode):
	if text == 'desc':
		return 'Edit ad description' if admin_mode else 'Baichnay wali cheez ki tafseel'
	elif text == 'is_new':
		return 'Edit item condition' if admin_mode else 'Yeh istamal shuda hai ya bilkul new hai'
	elif text == 'is_barter':
		return 'Edit barter condition' if admin_mode else 'Sirf paisey chahiyen ya badley mein koi cheez bhi le lo gey'
	elif text == 'town':
		return 'Edit locality' if admin_mode else 'Apna ilaka ya mohalla likho'
	elif text == 'ask':
		return 'Edit asking price' if admin_mode else 'Kitni price ka baichna chahtey ho'
	elif text == 'seller_name':
		return 'Edit seller name' if admin_mode else 'Apna naam likho'
	elif text == 'city':
		return 'Edit city' if admin_mode else 'Apna city likho'
	elif text == 'title':
		return 'Edit title' if admin_mode else 'Apne ad ka aik acha sa unwaan rakho'
	elif text == 'categ':
		return 'Edit category' if admin_mode else 'Apne ad ki category chunno'

@csrf_protect
def edit_classified(request,*args,**kwargs):
	if request.method == "POST":
		ad_id = request.POST.get('ad_score',None)
		only_locked = request.POST.get('only_locked',None)
		locked_by = who_locked_ad(ad_id)
		if locked_by and locked_by != request.user.username:
			return render(request,"cant_lock_ad.html",{'locked_by':locked_by,'only_locked':only_locked})
		elif request.POST.get('edited',None):
			# ad_id = request.POST.get('ad_id',None)
			field = request.POST.get('which_field',None)
			unfinished = request.POST.get('unfinished',None)
			if field == "is_new" or field == "is_barter":
				status = request.POST.get('status',None)
				if unfinished:
					edit_unfinished_ad_field(ad_id,request.user.id,field,status)
					return redirect("show_user_ads")
				else:
					edit_single_unapproved_ad(ad_id, field, status)
					return redirect("approve_classified", only_locked)
			else:
				form = EditFieldForm(data=request.POST)
				if form.is_valid():
					new_text = form.cleaned_data['text_field']
					if unfinished:
						edit_unfinished_ad_field(ad_id,request.user.id,field,new_text)
						return redirect("show_user_ads")
					else:
						edit_single_unapproved_ad(ad_id, field, new_text)
						return redirect("approve_classified", only_locked)
				else:
					return render(request,"500.html",{})
		else:
			# ad_id = request.POST.get('ad_score',None)
			editor_id = request.POST.get('EID',None)
			if editor_id == 'admin' or int(editor_id) == request.user.id:
				admin_mode = 1 if editor_id == 'admin' else 0
				which_field, text_string, city = get_field(request.POST)
				help_text = get_help_text(text_string,admin_mode)
				f = EditFieldForm(initial={'text_field': which_field})
				if text_string == 'city':
					locs = get_approved_places()
					return render(request,"edit_classified_field.html",{'form':f,'ad_id':ad_id,'name':text_string,'help_text':help_text,'locs':locs,'admin_mode':admin_mode,\
						'only_locked':only_locked})
				elif text_string == 'town':
					towns = get_approved_places(city=city)
					return render(request,"edit_classified_field.html",{'form':f,'ad_id':ad_id,'name':text_string,'help_text':help_text,'towns':towns,'mother_ship':city,\
						'admin_mode':admin_mode, 'only_locked':only_locked})
				elif text_string == 'categ':
					categs = get_classified_categories()
					return render(request,"edit_classified_field.html",{'form':f,'ad_id':ad_id,'name':text_string,'help_text':help_text,'categs':categs,'admin_mode':admin_mode, \
						'only_locked':only_locked})
				return render(request,"edit_classified_field.html",{'form':f,'ad_id':ad_id,'name':text_string,'help_text':help_text,'admin_mode':admin_mode, \
					'only_locked':only_locked})
			else:
				return render(request,"404.html",{'from_ecomm':True})
	else:
		return render(request,"404.html",{'from_ecomm':True})


@csrf_protect
def ad_locked_by_agent(request,*args,**kwargs):
	if request.method == "POST":
		ad_id = request.POST.get('ad_score',None)
		only_locked = request.POST.get('only_locked',None)
		locked_by = who_locked_ad(ad_id)
		if locked_by and locked_by != request.user.username:
			return render(request,"cant_lock_ad.html",{'locked_by':locked_by,'only_locked':only_locked})
		editor_id = request.POST.get('EID',None)
		action = request.POST.get('action',None)
		if editor_id == 'admin' and action == 'lock':
			# lock the ad 
			locked = lock_unapproved_ad(ad_id,request.user.username, request.user.id)
			if locked:
				return redirect("approve_classified", only_locked)
			else:
				return render(request,"cant_lock_ad.html",{'locked_by':locked[1],'only_locked':only_locked})
		elif editor_id == 'admin' and action == 'unlock':
			unlocked = unlock_unapproved_ad(ad_id, request.user.username, request.user.id)
			if unlocked:
				return redirect("approve_classified", only_locked)
			else:
				# the ad isn't locked by anyone, but you still don't have unlocking privilege
				if unlocked[1] == False:
					return render(request,"500.html",{})
				# the ad is locked by someone else - you don't have unlocking privilege
				else:
					return redirect(request,"cant_lock_ad.html",{'locked_by':unlocked[1],'only_locked':only_locked})
		else:
			return render(request,"404.html",{'from_ecomm':True})
		return redirect("approve_classified", only_locked)
	else:
		return render(request,"404.html",{'from_ecomm':True})


@csrf_protect
def change_cover_photo(request,*args,**kwargs):
	if request.method == "POST":
		ad_id = request.POST.get('ad_score',None)
		only_locked = request.POST.get('only_locked',None)
		locked_by = who_locked_ad(ad_id)
		if locked_by and locked_by != request.user.username:
			return render(request,"cant_lock_ad.html",{'locked_by':locked_by,'only_locked':only_locked})
		photo_id = request.POST.get('dec',None)
		edit_single_unapproved_ad(ad_id,'photos',photo_id)
		return redirect("approve_classified", only_locked)
	else:
		return render(request,"404.html",{'from_ecomm':True})


@csrf_protect
def process_ad_approval(request,*args,**kwargs):
	if request.method == "POST":
		ad_id = request.POST.get('ad_score',None)
		only_locked = request.POST.get('only_locked',None)
		locked_by = who_locked_ad(ad_id)
		if locked_by and locked_by != request.user.username:
			return render(request,"cant_lock_ad.html",{'locked_by':locked_by,'only_locked':only_locked})
		dur = request.POST.get('dur',None) # in hours
		if dur == str(MOST_DURATION) or dur == str(LEAST_DURATION):
			time_flag, click_flag = True, False
			expiration_time = time.time() + (int(dur)*60*60)
		elif dur == str(MOST_CLICKS) or dur == str(LEAST_CLICKS) or dur == str(MEDIUM_CLICKS):
			time_flag, click_flag = False, True
			expiration_clicks = int(dur)
		if time_flag:
			mobile_number = move_to_approved_ads(ad_id=ad_id, expiration_time=expiration_time, closed_by=request.user.username, closer_id=str(request.user.id))
		elif click_flag:
			mobile_number = move_to_approved_ads(ad_id=ad_id, expiration_clicks=expiration_clicks, closed_by=request.user.username, closer_id=str(request.user.id))
		if mobile_number:
			# enqueue sms
			status = 'forward'
			enqueue_sms.delay(mobile_number=mobile_number, ad_id=int(float(ad_id)), status=status, item_name=get_item_name(ad_id))
			status = 'approved'
			enqueue_sms.delay(mobile_number=mobile_number, ad_id=int(float(ad_id)), status=status)
		else:
			return render(request,"500.html",{})
		return redirect("approve_classified", only_locked)
	else:
		return render(request,"404.html",{'from_ecomm':True})


@csrf_protect
def approve_classified(request,only_locked,*args,**kwargs):
	if request.method == "POST":
		ad_id = request.POST.get('ad_score',None)
		locked_by = who_locked_ad(ad_id)
		if locked_by and locked_by != request.user.username:
			return render(request,"cant_lock_ad.html",{'locked_by':locked_by})
		approve = request.POST.get('approve',None)
		decline = request.POST.get('decline',None)
		if approve:
			return render(request,"approve_classified.html",{'score':ad_id,'least_clicks':LEAST_CLICKS,'most_clicks':MOST_CLICKS,\
				'medium_clicks':MEDIUM_CLICKS,'least_dur':LEAST_DURATION,'most_dur':MOST_DURATION, 'only_locked':only_locked})
		else:
			del_single_unapproved_ad(ad_id, str(request.user.id))
			return redirect("approve_classified", only_locked)
	else:
		page_num = request.GET.get('page', '1')
		photos, submissions = [], []
		ads = get_unapproved_ads(request.user.id, withscores=True, only_locked=only_locked)
		page_obj = get_page_obj(page_num,ads,ADS_TO_APPROVE_PER_PAGE)
		submissions = process_ad_objects(ad_list=page_obj.object_list, tup=True, must_eval_ad=True, photo_tup=True)
		checkers = get_and_set_classified_dashboard_visitors(request.user.username,withtime=True)
		return render(request,"unapproved_ads.html",{'submissions':submissions,'page':page_obj, 'checkers':checkers,'count':len(ads),'only_locked':only_locked})


############################ Ad Posting Process ###################################


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def post_seller_info(request,*args,**kwargs):
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	user_id = request.user.id
	if request.method == 'POST':	
		mob_nums = get_temporarily_saved_ad_data(str(user_id),mob_nums=True)
		if mob_nums:
			# setting 'nums' ensures the mobile field is created and processed. Otherwise, it's entirely ignored (for the case where we don't have the user's numbers)
			form = SellerInfoForm(request.POST,nums=mob_nums)
		else:
			form = SellerInfoForm(request.POST)
		if form.is_valid():
			seller_name = form.cleaned_data.get("seller_name",None)
			city = form.cleaned_data.get("city",None)
			town = form.cleaned_data.get("town",None)
			mobile = form.cleaned_data.get("mobile",None)
			device = get_device(request)
			# save uploaded photo hashes at this point - ad content is finalized (only verification remains)
			photo_hashes = get_temporarily_saved_ad_data(str(user_id),photo_hashes=True)
			save_ecomm_photo_hash.delay(photo_hashes["photo1_hash"], photo_hashes["photo2_hash"], photo_hashes["photo3_hash"])
			#############################################################################################################
			if mobile is None or mobile == 'Kisi aur number pe':
				# time to verify a new number
				CSRF = csrf.get_token(request)
				temporarily_save_ad(user_id=str(user_id),seller_name=seller_name,city=city,town=town,submission_device=device,on_fbs=on_fbs,csrf=CSRF)
				form = VerifySellerMobileForm()
				save_unfinished_ad.delay(get_temporarily_saved_ad_data(user_id=str(user_id),full_ad=True))
				return render(request,"verify_seller_number.html",{'form':form,'csrf':CSRF,'new_seller_num':mobile})
			else:
				# a number from file was picked, just create ad now
				mobile = mobile[-10:]
				data = get_temporarily_saved_ad_data(user_id=str(user_id),half_ad=True)
				context={'desc':data["desc"],'is_new':data["is_new"],'ask':data["ask"],'is_barter':data["is_barter"],'ad_id':data["ad_id"],\
				'seller_name':namify(seller_name),'city':namify(city), 'town':namify(town), 'AK_ID':'just_number','MN_data':mobile,'user_id':user_id,\
				'username':request.user.username,'submission_device':device,'on_fbs':str(on_fbs)}
				# register with Twilio's Notify service
				set_user_binding_with_twilio_notify_service.delay(user_id=user_id, phone_number="+92"+mobile)
				save_basic_ad_data(context)
				return render(request,"basic_item_ad_submitted.html",{})
		else:
			return render(request,"post_seller_info.html",{'form':form,'mobile_num':mob_nums})
	else:
		is_step_one_saved = check_status_of_temporarily_saved_ad(user_id=str(user_id),check_step_one=True)
		if is_step_one_saved:
			mob_nums = get_user_verified_number(user_id)
			# check if we have any of the user's nums on file
			if mob_nums:
				temporarily_save_ad(user_id=str(user_id),mob_nums=mob_nums) # mob_nums is a list
			form = SellerInfoForm(nums=mob_nums)
			return render(request,"post_seller_info.html",{'form':form,'mobile_num':mob_nums})
		else:
			return render(request,"dont_click_again_and_again.html",{'from_ecomm':True})

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def post_basic_item_photos(request,*args,**kwargs):
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	user_id = request.user.id
	if request.method == 'POST':
		decision = request.POST.get("dec",None)
		if decision == 'Skip':
			mob_nums = get_user_verified_number(user_id)
			# check if we have any of the user's nums on file
			if mob_nums:
				temporarily_save_ad(user_id=str(user_id),mob_nums=mob_nums)
			form = SellerInfoForm(nums=mob_nums)
			return render(request,"post_seller_info.html",{'form':form,'mobile_num':mob_nums})
		else:
			secret_key_from_form, secret_key_from_session = request.POST.get('sk','0'), get_and_delete_ecomm_photos_secret_key(user_id)
			if str(secret_key_from_form) != str(secret_key_from_session):
				return render(request,"dont_click_again_and_again.html",{'from_ecomm_ad_creation':True,'from_ecomm':True})
			form = BasicItemPhotosForm(request.POST,request.FILES)
			if form.is_valid():	
				photo1, photo2, photo3 = form.cleaned_data.get('photo1',None), form.cleaned_data.get('photo2',None), form.cleaned_data.get('photo3',None)
				counter, exception, on_fbs, photos = 0, [], request.META.get('HTTP_X_IORG_FBS',False), get_photo_strings([photo1, photo2, photo3])
				for photo_list in photos:
					if photo_list[0]:
						is_excessive, size = photo_size_exceeded(on_fbs, photo_list[0])
						if is_excessive:
							exception.append(True)
							if counter == 0:
								photo1 = size
							elif counter == 1:
								photo2 = size
							elif counter ==2:
								photo3 = size
						else:
							image, avghash, pk = clean_image_file_with_hash(photo_list[0], 1, 'ecomm') # 1 means high quality image is returned, not over compressed
							if is_repeated(avghash,get_temporarily_saved_ad_data(str(user_id),photo_hashes=True)):
								exception.append(True)
								if counter == 0:
									photo1 = 'repeated'
								elif counter == 1:
									photo2 = 'repeated'
								elif counter == 2:
									photo3 = 'repeated'
							else:
								if isinstance(pk,float):
									exception.append(True)
									if counter == 0:
										photo1 = 'duplicate'
									elif counter == 1:
										photo2 = 'duplicate'
									elif counter == 2:
										photo3 = 'duplicate'
								else:
									photo = Photo.objects.create(image_file = image, owner_id=user_id, caption='caption', comment_count=0, \
										device=get_device(request), avg_hash=avghash, category='9')
									photo_id = photo.id
									upload_ecomm_photo.delay(photo_id, user_id, get_temporarily_saved_ad_data(str(user_id),id_only=True))
									temporarily_save_ad(user_id=str(user_id), which_photo_hash=photo_list[2], photo_id=photo_id, photo_hash=avghash, \
										photo_number=photo_list[1])
					counter += 1
				p1, p2, p3 = get_temporarily_saved_ad_data(str(user_id),all_photo_numbers=True)
				if p1:
					photo1 = True
				if p2:
					photo2 = True
				if p3:
					photo3 = True
				if exception: # e.g. pressed 'Agey', but uploaded photos didn't upload correctly
					secret_key = uuid.uuid4()
					set_ecomm_photos_secret_key(user_id, secret_key)
					return render(request,"post_basic_item_photos.html",{'form':form, 'photo1':photo1,'photo2':photo2,'photo3':photo3,'sk':secret_key,'on_fbs':on_fbs})
				elif (photo1 and photo2 and photo3) or (decision == 'Agey'): # e.g. pressed "Agey" and all/any photos uploaded correctly
					mob_nums = get_user_verified_number(user_id)
					# check if we have any of the user's nums on file
					if mob_nums:
						temporarily_save_ad(user_id=str(user_id),mob_nums=mob_nums) # mob_nums is a list
					form = SellerInfoForm(nums=mob_nums)
					return render(request,"post_seller_info.html",{'form':form,'mobile_num':mob_nums})
				else: # e.g. uploading photos 1 by 1
					secret_key = uuid.uuid4()
					set_ecomm_photos_secret_key(user_id, secret_key)
					return render(request,"post_basic_item_photos.html",{'form':form, 'photo1':photo1,'photo2':photo2,'photo3':photo3,'sk':secret_key,'on_fbs':on_fbs})
			else:
				secret_key = uuid.uuid4()
				set_ecomm_photos_secret_key(user_id, secret_key)
				return render(request,"post_basic_item_photos.html",{'form':form,'sk':secret_key,'on_fbs':on_fbs})
	else:
		is_step_one_saved, is_step_two_saved = check_status_of_temporarily_saved_ad(user_id=str(user_id),check_step_one=True,check_step_two=True)
		if is_step_one_saved and is_step_two_saved:
			mob_nums = get_user_verified_number(user_id)
			# check if we have any of the user's nums on file
			if mob_nums:
				temporarily_save_ad(user_id=str(user_id),mob_nums=mob_nums) # mob_nums is a list
			form = SellerInfoForm(nums=mob_nums)
			return render(request,"post_seller_info.html",{'form':form,'mobile_num':mob_nums})
		elif is_step_one_saved:
			form = BasicItemPhotosForm()
			secret_key = uuid.uuid4()
			set_ecomm_photos_secret_key(user_id, secret_key)
			context = {'form':form,'sk':secret_key,'on_fbs':request.META.get('HTTP_X_IORG_FBS',False)}
			return render(request,"post_basic_item_photos.html",context)
		else:
			return redirect("init_classified")

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def post_basic_item(request,*args,**kwargs):
	user_id = request.user.id
	if request.method == 'POST':
		form = BasicItemDetailForm(request.POST)
		if form.is_valid():
			description = form.cleaned_data.get("description",None)
			new = form.cleaned_data.get("new",None)
			ask = form.cleaned_data.get("ask",None)
			barter = form.cleaned_data.get("barter",None)
			temporarily_save_ad(user_id=str(user_id), description=description, is_new=new, ask=ask, is_barter=barter, ad_id=get_basic_item_ad_id(), uid=user_id)
			form = BasicItemPhotosForm()
			secret_key = uuid.uuid4()
			set_ecomm_photos_secret_key(user_id, secret_key)
			context = {'form':form,'sk':secret_key,'on_fbs':request.META.get('HTTP_X_IORG_FBS',False)}
			return render(request,"post_basic_item_photos.html",context)
		else:
			return render(request,"post_basic_item.html",{'form':form})	
	else:
		is_step_one_saved, is_step_two_saved = check_status_of_temporarily_saved_ad(user_id=str(user_id),check_step_one=True,check_step_two=True)
		if is_step_one_saved and is_step_two_saved:
			mob_nums = get_user_verified_number(user_id)
			# check if we have any of the user's nums on file
			if mob_nums:
				temporarily_save_ad(user_id=str(user_id),mob_nums=mob_nums) # mob_nums is a list
			form = SellerInfoForm(nums=mob_nums)
			return render(request,"post_seller_info.html",{'form':form,'mobile_num':mob_nums})
		elif is_step_one_saved:
			form = BasicItemPhotosForm()
			secret_key = uuid.uuid4()
			set_ecomm_photos_secret_key(user_id, secret_key)
			context = {'form':form,'sk':secret_key,'on_fbs':request.META.get('HTTP_X_IORG_FBS',False)}
			return render(request,"post_basic_item_photos.html",context)
		else:
			return redirect("init_classified")

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def init_classified(request,*args,**kwargs):
	if request.method == 'POST':
		if request.user.is_authenticated():
			if request.POST.get('category',None) == '1':
				form = BasicItemDetailForm()
				reset_temporarily_saved_ad(str(request.user.id))
				return render(request,"post_basic_item.html",{'form':form})
			else:
				return render(request,"404.html",{'from_ecomm':True})
		else:
			return redirect("initiate_seller_verification_process")
	else:
		return render(request,"basic_classified_instructions.html",{})


def initiate_seller_verification_process(request):
	form = VerifySellerMobileForm()
	# CSRF = csrf.get_token(request)
	# temporarily_save_ad(user_id=str(user_id),csrf=CSRF,description=request.POST.get('desc',None),ask=request.POST.get('ask',None),\
	# 	is_new=request.POST.get('is_new',None),is_barter=request.POST.get('is_barter',None),seller_name=request.POST.get('seller_name',None),\
	# 	city=request.POST.get('city',None),town=request.POST.get('town',None))
	# from_meray_ads = request.POST.get('from_meray_ads',None)
	# return render(request,"verify_seller_number.html",{'csrf':CSRF,'form':form,'from_meray_ads':from_meray_ads})


#################################################################

# @csrf_protect
# def add_shop(request,*args,**kwargs):
# 	if request.method == 'POST':
# 		form = AddShopForm(data=request.POST)
# 	else:
# 		form = AddShopForm()
# 		return render(request,"add_shop.html",{'form':form})

# def shops_by_city(request,city,*args,**kwargs):
# 	if city in CITIES:
# 		listing = get_city_shop_listing(city)
# 		return render(request,"shops_by_city.html",{'listing':listing})
# 	else:
# 		return redirect("ecomm")

# @csrf_protect
# def show_shop_choices(request,*args,**kwargs):
# 	if first_time_shopper(request.user.id):
# 		add_shopper(request.user.id)
# 		return render(request,"shops_welcome.html",{})
# 	else:
# 		if request.method == 'POST':
# 			if request.POST.get('listing',None):
# 				city = request.POST.get('city',None)
# 				return redirect("shops_by_city",city)
# 			else:
# 				return render(request,"shop_locations.html",{})
# 		else:
# 			return render(request,"shop_locations.html",{})

#################################################################

def x32_details(request,*args,**kwargs):
	return render(request,"x32_details.html",{})

def x2lite_details(request,*args,**kwargs):
	return render(request,"x2lite_details.html",{})

def i6metal_details(request,*args,**kwargs):
	user_score = 0
	user_score = request.user.userprofile.score
	score_diff = 5000-int(user_score)
	return render(request,"qmobile_i6_metal.html",{'user_score':user_score,'score_diff':score_diff})


def x33_details(request,*args,**kwargs):
	user_score = 0
	user_score = request.user.userprofile.score
	score_diff = 5000-int(user_score)
	return render(request,"qmobile_x33.html",{'user_score':user_score,'score_diff':score_diff})

def x29_details(request,*args,**kwargs):
	user_score = 0
	user_score = request.user.userprofile.score
	score_diff = 5000-int(user_score)
	return render(request,"qmobile_x29.html",{'user_score':user_score,'score_diff':score_diff})

def i8i_details(request,*args,**kwargs):
	user_score = 0
	user_score = request.user.userprofile.score
	score_diff = 5000-int(user_score)
	return render(request,"qmobile_i8i.html",{'user_score':user_score,'score_diff':score_diff})

def s6_details(request,*args,**kwargs):
	user_score = 0
	user_score = request.user.userprofile.score
	score_diff = 5000-int(user_score)
	return render(request,"qmobile_s6.html",{'user_score':user_score,'score_diff':score_diff})

def j1_details(request,*args,**kwargs):
	user_score = 0
	user_score = request.user.userprofile.score
	score_diff = 5000-int(user_score)
	return render(request,"samsung_j1.html",{'user_score':user_score,'score_diff':score_diff})

def delivery(request,origin,*args,**kwargs):
	context = {}
	context["origin"] = origin
	return render(request,"delivery.html",context)

def warranty(request,origin,*args,**kwargs):
	context = {}
	context["origin"] = origin
	return render(request,"warranty.html",context)



@csrf_protect
def buyer_loc(request,*args,**kwargs):
	user_id = request.user.id
	if request.method == 'POST':
		mobile_verified = is_mobile_verified(user_id)
		request.session['mobile_verified']=mobile_verified
		merch_id = request.POST.get("merch_id") #1 is x32, 2 is x2lite
		request.session["which_phone"] = merch_id
		request.session.modified = True
		mp.track(request.user.id, 'M_S_2 On_location')
		return render(request,"buyer_loc.html",{'merch_id':merch_id,'mobile_verified':mobile_verified})
	else:
		try:
			merch_id = request.session["which_phone"]
		except:
			merch_id = None
		if merch_id:
			mp.track(request.user.id, 'M_S_2 On_location')
			return render(request,"buyer_loc.html",{'merch_id':merch_id,'mobile_verified':is_mobile_verified(user_id)})
		else:
			user_score = 0
			user_score = request.user.userprofile.score
			score_diff = 5000-int(user_score)
			mp.track(request.user.id, 'M_S_1.1 came to shop')
			return render(request,"ecomm_choices.html",{'user_score':user_score,'score_diff':score_diff})


@csrf_protect
def mobile_shop(request,*args,**kwargs):
	if request.method == 'POST':
		user_id = request.user.id
		request.session.pop('mobile_verified',None)
		mobile_verified = is_mobile_verified(user_id)
		request.session['mobile_verified']=mobile_verified
		merch_id = request.POST.get('merch_id',None) #1 is x32, 2 is x2lite
		loc = request.POST.get('loc',None)
		if loc == None or merch_id == None:
				return render(request,"buyer_loc.html",{'merch_id':merch_id,"mobile_verified":mobile_verified})
		else:
			if loc == 'lhr' or loc == 'rwp' or loc == 'isb' or loc == 'khi' or loc == 'fsd' or loc == 'hyd' or loc == 'pes' or loc == 'mul'\
			or loc == 'sbi' or loc == 'atk':
	 			# move on to asking the user their mobile numer and their real name
	 			request.session['mobile_buyer_city'] = loc
	 			request.session['merch_id'] = merch_id
	 			request.session.modified = True
	 			mp.track(request.user.id, 'M_S_3 relevant_location')
	 			return redirect("buyer_details")
			else:
				mp.track(request.user.id, 'M_S_4 No_service_city')
				return render(request,"service_unavailable.html",{}) 	
	else:
		user_id=request.user.id
		order_in_process = check_orders_processing(user_id)
		user_score = 0
		user_score = request.user.userprofile.score
		score_diff = 5000-int(user_score)
		mp.track(request.user.id, 'M_S_1 came to shop')
		return render(request,"ecomm_choices.html",{'user_score':user_score,'score_diff':score_diff,'order_in_process':order_in_process})

@csrf_protect
def buyer_details(request,*args,**kwargs):
	if request.method == 'POST':
		form = BuyerForm(request.POST)
		if form.is_valid():
			mp.track(request.user.id, 'M_S_5.1 correct buyer detail')
			username = form.cleaned_data.get("username",None)
			name = username.strip().title()
			i=0
			firstname, lastname = '',''
			for word in name.split():
				if i==0:
					firstname=word
					i+=1
				else:
					lastname+=word
					lastname+=' '
					i+=1
			address = form.cleaned_data.get("address",None)
			ON_AZURE = os.environ.get('ON_AZURE',None)
			user_id = request.user.id
			request.session['mobile_buyer_id'] = user_id
			request.session.modified = True
			city = LOCATION[request.session['mobile_buyer_city']]
			merch_id = request.session['merch_id']
 			phonenumber = ''
 			price = MERCH[merch_id]['price']
 			model = MERCH[merch_id]['name']
 			order_data = {'firstname':firstname,'lastname':lastname,'city':city,'address':address,'user_id':user_id,\
 			'phonenumber':phonenumber, 'merch_id':merch_id, 'price':price, 'model':model} 

			if is_mobile_verified(user_id):

				number = get_user_verified_number(user_id)
				request.session['buyer_phonenumber']=number[0]
				request.session.modified = True
				order_data['phonenumber']=number[0]
				saved = save_order_data(order_data)
				
				if saved:
					mp.track(request.user.id, 'M_S_7 On confirm order')
					return redirect("confirm_order")
				else:
					return render(request,"404.html",{})
			else:
				mp.track(request.user.id, 'M_S_7.1 on confirm Phone`')
				CSRF = csrf.get_token(request)
				request.session["csrf"] = CSRF
				request.session.modified = True	
				saved = save_order_data(order_data)
			 	if saved:
			 		return render(request,'verify_buyer.html',{'ON_AZURE':ON_AZURE,'csrf':CSRF})
		 		else:
					mp.track(request.user.id, 'M_S_E phone verification')
		 			return render(request,"404.html",{})	
		else:
			mp.track(request.user.id, 'M_S_5 on buyer detail')
			return render(request,'buyer_detail.html',{'form':form,'device':get_device(request)})
	else:
		form = BuyerForm()
		mobile_verified = request.session['mobile_verified']
		mp.track(request.user.id, 'M_S_6 entered incorrect info')
		return render(request,'buyer_detail.html',{'form':form,'device':get_device(request),'mobile_verified':mobile_verified})


@csrf_protect
def confirm_order(request):

	if request.method == 'POST':
		user_id = request.session['mobile_buyer_id']
		check = check_orders_processing(user_id)
		if check:
			mp.track(request.user.id, 'M_S_8 ordering second')
			return redirect("in_process")
		else:
			merch_id = request.session['merch_id']
			score_cost = 5000
			saved = place_order(user_id)
			if saved:
				user_score = request.user.userprofile.score			
				UserProfile.objects.filter(user_id=user_id).update(score=F('score')-int(score_cost))
				enqueue_buyer_sms.delay('+923455885441', saved["order_id"], saved, None)
				enqueue_buyer_sms.delay('+923335196812', saved["order_id"], saved, None)
				mp.track(request.user.id, 'M_S_9 order placed')				
				return redirect("order_successful")
			else:
				return render(request,"404.html",{})
	else:
		user_id = request.session['mobile_buyer_id']
		order_data = get_temp_order_data(user_id)
		if order_data:
			model = order_data['model']
			price = order_data['price']
			user_score = request.user.userprofile.score			
			merch_id = order_data['merch_id']
			score_charge = 5000
			remaining_score = user_score - 5000
			buy_possible=0
			mobile_verified = request.session['mobile_verified']
			if int(score_charge) <= int(user_score):
				buy_possible = 1
			return render(request,"confirm_order.html",{'model':model,'price':price, 'buy_possible':buy_possible,\
			 'score_cost':score_charge,'user_score':user_score,'mobile_verified':mobile_verified, 'remaining_score':remaining_score })
		else:
			return render(request,"404.html",{})

# def buy_possbile(user_id):
# 	order_data = get_temp_order_data(user_id)
# 	if order_data:
# 		model = order_data['model']
# 		price = order_data['price']
# 		user_score = request.user.userprofile.score			
# 		merch_id = order_data['merch_id']
# 		score_cost = MERCH[merch_id]['points_cost']
# 		if score_cost > user_score:
# 			buy_possible = 0
# 		else:
# 			buy_possible = 1 
	
def order_successful(request):
	mp.track(request.user.id, 'M_S_9.1 order placed shown')	
	return render(request,"order_placed_successfully.html",{})

def in_process(request):
	return render(request,"in_process.html")

def get_new_orders(request):
	orders = show_new_orders()
	return render(request,'new_orders.html', {'orders':orders})

def buyer_verify():
	return render(request,"buyer_verification.html",{})

def show_city(request):
	form = EcommCityForm()
	return render(request,'enter_city.html',{'form':form})

def print_referrer_logs(request):
	logs = return_referrer_logs('referrer')
	readable_logs = []
	for log in logs:
		readable_logs.append(ast.literal_eval(log))
	import csv
	filename = 'referrer.csv'
	with open(filename,'wb') as f:
		wtr = csv.writer(f)
		for log in readable_logs:
			user_id = log["user_id"] if "user_id" in log else None
			origin = log["origin"]
			referrer = log["referrer"]
			time = log["time_stamp"] if "time_stamp" in log else 0
			to_write = [user_id, origin, referrer, time]
			wtr.writerows([to_write])
	return render(request, "404.html", {'from_ecomm':True})

#def populate_photo_ads(request):
	# populate_ad_list(which_list="photos")
	# return render(request,'404.html',{'from_ecomm':True})