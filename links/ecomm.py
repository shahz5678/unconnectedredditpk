from models import Photo
from tasks import upload_ecomm_photo
from redis4 import get_city_shop_listing
from redis1 import first_time_shopper, add_shopper
from image_processing import clean_image_file_with_hash
from score import CITIES, ON_FBS_PHOTO_THRESHOLD, OFF_FBS_PHOTO_THRESHOLD
from redis3 import log_unserviced_city, log_completed_orders, get_basic_item_ad_id
from ecomm_forms import EcommCityForm, AddShopForm, BasicItemDetailForm, BasicItemPhotosForm, SellerInfoForm, VerifySellerMobileForm

from django.middleware import csrf
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
#################################################################

def get_device(request):
	if request.is_feature_phone:
		return '1'
	elif request.is_phone:
		return '2'
	elif request.is_tablet:
		return '4'
	elif request.is_mobile:
		return '5'
	else:
		return '3'

def set_upload_status(upload_id, sess_dict):
	photo1, photo2, photo3 = (None, None, None)
	if upload_id == '1':
		photo1 = False
		if "photo2" in sess_dict:
			photo2 = True
		if "photo3" in sess_dict:
			photo3 = True
	elif upload_id == '2':
		photo2 = False
		if "photo1" in sess_dict:
			photo1 = True
		if "photo3" in sess_dict:
			photo3 = True
	elif upload_id == '3':
		photo3 = False
		if "photo2" in sess_dict:
			photo2 = True
		if "photo1" in sess_dict:
			photo1 = True
	return photo1, photo2, photo3

def get_photo_obj(photo1, photo2, photo3):
 	if photo1:
 		return photo1, "photo1", "photo1_hash", '1'	
 	if photo2:
 		return photo2, "photo2", "photo2_hash", '2'
 	if photo3:
 		return photo3, "photo3", "photo3_hash", '3'

def is_repeated(avghash,sess_dict):
	if "photo1_hash" in sess_dict:
		if sess_dict["photo1_hash"] == avghash:
			return True
	elif "photo2_hash" in sess_dict:
		if sess_dict["photo2_hash"] == avghash:
			return True
	elif "photo3_hash" in sess_dict:
		if sess_dict["photo3_hash"] == avghash:
			return True
	return False

def photo_size_exceeded(on_fbs,image):
	if on_fbs:
		if image.size > ON_FBS_PHOTO_THRESHOLD:
			return True, ON_FBS_PHOTO_THRESHOLD
		else:
			# return True, ON_FBS_PHOTO_THRESHOLD
			return False, 0
	else:
		if image.size > OFF_FBS_PHOTO_THRESHOLD:
			return True, OFF_FBS_PHOTO_THRESHOLD
		else:
			# return True, OFF_FBS_PHOTO_THRESHOLD
			return False, 0

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def post_seller_info(request,*args,**kwargs):
	if request.method == 'POST':
		form = SellerInfoForm(request.POST)
		if form.is_valid():
			seller_name = form.cleaned_data.get("seller_name",None)
			city = form.cleaned_data.get("city",None)
			request.session["seller_name"] = seller_name
			request.session["city"]  = city
			form = VerifySellerMobileForm()
			CSRF = csrf.get_token(request)
			request.session["csrf"] = CSRF
			request.session.modified = True
			return render(request,"verify_seller_number.html",{'form':form,'csrf':CSRF})
		else:
			return render(request,"post_seller_info.html",{'form':form})
	else:
		return render(request,"404.html",{})

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def post_basic_item_photos(request,*args,**kwargs):
	if request.method == 'POST':
		form = BasicItemPhotosForm(request.POST,request.FILES)
		if form.is_valid():
			if request.POST.get('next',None):
				form = SellerInfoForm()
				return render(request,"post_seller_info.html",{'form':form})
			else:
				photo1 = form.cleaned_data.get('photo1',None)
				photo2 = form.cleaned_data.get('photo2',None)
				photo3 = form.cleaned_data.get('photo3',None)
				###########################
				on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
				photo_object, photo_string, photo_hash_string, upload_id = get_photo_obj(photo1, photo2, photo3)
				####### If photo is too big #######
				is_excessive, size = photo_size_exceeded(on_fbs, photo_object)
				if is_excessive:
					photo1, photo2, photo3 = set_upload_status(upload_id,request.session)
					return render(request,"post_basic_item_photos.html",{'form':form, 'photo1':photo1,'photo2':photo2,'photo3':photo3,'size':size})
				else:
					image, avghash, pk = clean_image_file_with_hash(photo_object, 1, 'ecomm') # 1 means high quality image is returned, not over compressed
					if is_repeated(avghash,request.session):
						####### If photo is a repeat-upload within this ad #######
						photo1, photo2, photo3 = set_upload_status(upload_id,request.session)
						return render(request,"post_basic_item_photos.html",{'form':form, 'photo1':photo1,'photo2':photo2,'photo3':photo3,'repeated':True})
					else:
						####### If photo duplicated from another ad #######
						if isinstance(pk,float):
							photo1, photo2, photo3 = set_upload_status(upload_id,request.session)
							return render(request,"post_basic_item_photos.html",{'form':form, 'photo1':photo1,'photo2':photo2,'photo3':photo3,'duplicate':True})
						else:
							request.session[photo_hash_string] = avghash
							photo = Photo.objects.create(image_file = image, owner_id=request.user.id, caption=request.session["basic_item_description"][:30], \
								comment_count=0, device=get_device(request), avg_hash=avghash)
							upload_ecomm_photo.delay(photo.id, request.user.id, avghash, request.session["ad_id"]) #ensure only uplaoded once
							request.session[photo_string] = "inserted"
				###########################
				if "photo1" in request.session:
					photo1 = True
				if "photo2" in request.session:
					photo2 = True
				if "photo3" in request.session:
					photo3 = True
				request.session.modified = True
				return render(request,"post_basic_item_photos.html",{'form':form, 'photo1':photo1,'photo2':photo2,'photo3':photo3})
		else:
			return render(request,"post_basic_item_photos.html",{'form':form})
	else:
		return render(request,"404.html",{})

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def post_basic_item(request,*args,**kwargs):
	if request.method == 'POST':
		form = BasicItemDetailForm(request.POST)
		if form.is_valid():
			description = form.cleaned_data.get("description",None)
			new = form.cleaned_data.get("new",None)
			ask = form.cleaned_data.get("ask",None)
			barter = form.cleaned_data.get("barter",None)
			request.session["basic_item_description"] = description
			request.session["basic_item_new"] = new
			request.session["basic_item_ask"] = ask
			request.session["basic_item_barter"] = barter
			request.session["ad_id"] = get_basic_item_ad_id()
			form = BasicItemPhotosForm()
			context = {'form':form}#,'item_desc':description,'is_new':new,'ask':ask,'is_barter':barter}
			request.session.pop("photo1",None)
			request.session.pop("photo2",None)
			request.session.pop("photo3",None)
			request.session.pop("photo1_hash",None)
			request.session.pop("photo2_hash",None)
			request.session.pop("photo3_hash",None)
			request.session.pop("seller_name",None)
			request.session.pop("city",None)
			request.session.pop("csrf",None)
			request.session.modified = True
			return render(request,"post_basic_item_photos.html",context)
		else:
			return render(request,"post_basic_item.html",{'form':form})	
	else:
		return render(request,"404.html",{})

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def init_classified(request,*args,**kwargs):
	if request.method == 'POST':
		if request.POST.get('category',None) == '1':
			form = BasicItemDetailForm()
			request.session.pop("basic_item_description",None)
			request.session.pop("basic_item_new",None)
			request.session.pop("basic_item_ask",None)
			request.session.pop("basic_item_barter",None)
			request.session.pop("ad_id",None)
			return render(request,"post_basic_item.html",{'form':form})
		else:
			return render(request,"404.html",{})
	else:
		return render(request,"basic_classified_instructions.html",{})


#################################################################

@csrf_protect
def add_shop(request,*args,**kwargs):
	if request.method == 'POST':
		form = AddShopForm(data=request.POST)
	else:
		form = AddShopForm()
		return render(request,"add_shop.html",{'form':form})

def shops_by_city(request,city,*args,**kwargs):
	if city in CITIES:
		listing = get_city_shop_listing(city)
		return render(request,"shops_by_city.html",{'listing':listing})
	else:
		return redirect("ecomm")

@csrf_protect
def show_shop_choices(request,*args,**kwargs):
	if first_time_shopper(request.user.id):
		add_shopper(request.user.id)
		return render(request,"shops_welcome.html",{})
	else:
		if request.method == 'POST':
			if request.POST.get('listing',None):
				city = request.POST.get('city',None)
				return redirect("shops_by_city",city)
			else:
				return render(request,"shop_locations.html",{})
		else:
			return render(request,"shop_locations.html",{})

#################################################################

def x32_details(request,*args,**kwargs):
	return render(request,"x32_details.html",{})

def x2lite_details(request,*args,**kwargs):
	return render(request,"x2lite_details.html",{})

@csrf_protect
def buyer_loc(request,*args,**kwargs):
	if request.method == 'POST':
		merch_id = request.POST.get("merch_id") #1 is x32, 2 is x2lite
		return render(request,"buyer_loc.html",{'merch_id':merch_id})
	else:
		return render(request,'404.html',{})

@csrf_protect
def process_city(request,*args,**kwargs):
	if request.method == 'POST':
		merch_id = request.POST.get('merch_id',None) #1 is x32, 2 is x2lite
		loc = request.POST.get('loc',None)
		if merch_id and loc:
			if loc == 'lhr' or loc == 'rwp' or loc == 'isb':
				# move on to asking the user their mobile numer and their real name
				return redirect("home")
			elif loc == 'khi':
				log_unserviced_city(request.user.id,'karachi',('x32' if merch_id == '1' else 'x2lite'))
				return render(request,"no_delivery.html",{'loc':'Karachi'})
			elif loc == 'other':
				form = EcommCityForm()
				return render(request,"enter_city.html",{'merch_id':merch_id,'form':form})
			else:
				form = EcommCityForm(request.POST)
				if form.is_valid():
					loc = form.cleaned_data.get("loc",None)
					if loc:
						log_unserviced_city(request.user.id,loc.lower(),('x32' if merch_id == '1' else 'x2lite'))
						return render(request,"no_delivery.html",{'loc':loc})
					else:
						return render(request,"ecomm_choices.html",{})			
				else:
					return render(request,"enter_city.html",{'merch_id':merch_id,'form':form})
		else:
			return render(request,"ecomm_choices.html",{})
	else:
		return render(request,'404.html',{})
