# coding=utf-8
import shortuuid, requests, uuid, time
from django.db import transaction
from django.contrib.auth import login as quick_login
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
######################################################################################
from django.contrib.auth.views import login as log_me_in
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.middleware import csrf
from redis7 import account_creation_disallowed
from tasks import registration_task, send_user_pin
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from django.views.decorators.debug import sensitive_post_parameters
from redis3 import get_temp_id, nick_already_exists, is_mobile_verified, insert_nick, temporarily_save_user_csrf, set_forgot_password_rate_limit, \
is_forgot_password_rate_limited, twiliolog_user_verified, twiliolog_pin_sms_sent, log_post_banned_username, save_user_account_kit_server_secret, \
someone_elses_number, log_ak_user_verification_outcome,retrieve_user_account_kit_secret,log_fp_ak_entered, log_fp_ak_user_verification_outcome#, log_forgot_password, is_sms_sending_rate_limited
from unauth_forms import CreateAccountForm, CreatePasswordForm, CreateNickNewForm, ForgettersNicknameForm, ResetForgettersPasswordForm, SignInForm,\
ForgettersMobileNumber, ForgettersPin
from verification_views import get_requirements
from forms import getip
from score import PW#, SEGMENT_STARTING_USER_ID
from brake.decorators import ratelimit

######################################################################################

# from mixpanel import Mixpanel
# from unconnectedreddit.settings import MIXPANEL_TOKEN

# mp = Mixpanel(MIXPANEL_TOKEN)

######################################################################################

# from optimizely_config_manager import OptimizelyConfigManager
# from unconnectedreddit.optimizely_settings import PID

# config_manager = OptimizelyConfigManager(PID)

######################################################################################

# this enables an unregistered user to access limited functionality on Damadam (e.g. creating an ad)
def create_dummy_user(request):
	uname = shortuuid.uuid()
	user = User(username=uname)
	user.set_password(PW)
	with transaction.commit_on_success():
		user.save()
		insert_nick(uname)
	return uname

######################################################################################


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def logout_then_login(request):
	if request.method == "POST":
		logout(request)
		request.session["logged_out"] = '1'
		request.session.modified = True
		return redirect("login")
	else:
		return redirect('for_me')

###################################### Forgot password flow ######################################


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def forgot_password(request, lang=None, *args, **kwargs):
	"""
	This initiates the 'forgot password' flow

	It takes user's username and phone number (one-by-one) as an input
	"""
	if request.user.is_authenticated():
		return redirect('for_me')
	elif request.method == "POST":
		form = ForgettersNicknameForm(data=request.POST, lang=lang)
		if form.is_valid():
			username, user_id = form.cleaned_data.get("username")
			if is_mobile_verified(user_id):
				request.session["forgetters_username"] = username
				request.session["forgetters_userid"] = user_id
				request.session.modified = True
				template_name = "unauth/verify_forgetters_account_ur.html" if lang == 'ur' else "unauth/verify_forgetters_account.html"
				return render(request,template_name,{'form':ForgettersMobileNumber()})
			else:
				template_name = "unauth/nick_unassociated_with_mobnum_ur.html" if lang == 'ur' else "unauth/nick_unassociated_with_mobnum.html"
				return render(request,template_name,{'nick':username})
		else:
			template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
			return render(request,template_name,{'form':form})
	else:
		template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
		return render(request,template_name,{'form':ForgettersNicknameForm()})


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def prelim_mobile_verification(request, lang=None, *args, **kwargs):
	"""
	This sends the user to Account Kit after performing preliminary check that the user's provided mobile number is indeed correct
	
	Can be removed if Account Kit is no longer in use
	"""
	if request.user.is_authenticated():
		return redirect('for_me')
	elif request.method == "POST":
		username = request.session.get('forgetters_username',None)
		user_id = request.session.get('forgetters_userid',None)
		form = ForgettersMobileNumber(request.POST,user_id=user_id, lang=lang)
		if form.is_valid():
			fg_ttl = is_forgot_password_rate_limited(user_id)
			if fg_ttl:
				log_fp_ak_user_verification_outcome("ratelimited_before_ak")
				# user 'recently' successfully used forgot password to retrieve their password - don't let them do it again
				template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
				return render(request,template_name,{'form':ForgettersNicknameForm(),'fg_rate_limit':time.time()-fg_ttl if lang == 'ur' else fg_ttl})
			else:
				phonenumber, sms_ttl = form.cleaned_data.get("phonenumber")
				# sms_ttl is always none when Account Kit is used (it's useful when inhouse SMS services are deployed)
				target_number = phonenumber[-11:]
				# send GET request to Account Kit url
				user_account_kit_server_secret = str(uuid.uuid4())# save locally
				log_fp_ak_entered()
				save_user_account_kit_server_secret(target_number, user_account_kit_server_secret, mob_num_as_key=True)
				URL = "https://www.accountkit.com/v1.0/basic/dialog/sms_login/"
				PARAMS = {'counter_code':'PK','app_id':'1758220174446684','state':user_account_kit_server_secret,\
				'redirect':'https://damadam.pk/forgot-password/set-new-pass/','phone_number':target_number,\
				'fbAppEventsEnabled':'true','debug':'false'}
				r = requests.get(url = URL, params = PARAMS) 
				return redirect(r.url)
		else:
			template_name = "unauth/verify_forgetters_account_ur.html" if lang == 'ur' else "unauth/verify_forgetters_account.html"
			return render(request,template_name,{'form':form})
	else:
		# not a POST request
		return redirect("forgot_password")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def set_forgetters_password(request, lang=None, *args, **kwargs):
	"""
	This enables a verified user (who's forgotten their password) to simply type a new one

	It uses Account Kit
	"""
	if request.user.is_authenticated():
		return redirect('for_me')
	elif request.method == "POST":
		user_id = request.session.get('forgetters_userid',None)
		if user_id:
			user = User.objects.get(id=user_id)
			form = ResetForgettersPasswordForm(data=request.POST, user=user, lang=lang)
			if form.is_valid():
				fg_ttl = is_forgot_password_rate_limited(user_id)
				if fg_ttl:
					# user 'recently' successfully used forgot password to retrieve their password - don't let them do it again'
					import time
					log_fp_ak_user_verification_outcome("ratelimited_after_ak")
					template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
					request.session.pop('forgetters_userid',None)
					request.session.pop('forgetters_username',None)
					return render(request,template_name,{'form':ForgettersNicknameForm(),'fg_rate_limit':time.time()-fg_ttl if lang == 'ur' else fg_ttl})
				else:
					password = form.cleaned_data['password']
					form.save()
					user = authenticate(username=user.username,password=password)
					quick_login(request,user)
					request.user.session_set.exclude(session_key=request.session.session_key).delete() # logging the user out of everywhere else
					request.session.pop('forgetters_userid',None)
					request.session.pop('forgetters_username',None)
					log_fp_ak_user_verification_outcome("verified")
					set_forgot_password_rate_limit(user_id)
					return render(request,'change_password/new_password.html',{'new_pass':password})
			else:
				template_name = "unauth/set_new_password_ur.html" if lang == 'ur' else "unauth/set_new_password.html"
				return render(request,template_name,{'form':form})
		else:
			request.session.pop('forgetters_username',None)
			template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
			log_fp_ak_user_verification_outcome("forgetters_userid_missing")
			return render(request,template_name,{'form':ForgettersNicknameForm(),"did_not_work":True})
	else:
		# account kit handshake takes place here (cater for various failure/success cases)
		AK_ID, MN_data, err = get_requirements(request=request, secret='', secret_omitted=True)
		if AK_ID and MN_data:
			# process the results
			mob_num = MN_data['national_number']
			original_secret = retrieve_user_account_kit_secret(identifier="0"+str(mob_num),from_forgot_pass=True)
			returned_secret = request.GET.get('state', None)
			if returned_secret and original_secret == returned_secret:
				user_id = request.session.get('forgetters_userid',None)
				if someone_elses_number(national_number=mob_num, user_id=user_id):
					request.session.pop('forgetters_username',None)
					request.session.pop('forgetters_userid',None)
					request.session["account_kit_verification_failed"] = '1'
					log_fp_ak_user_verification_outcome("forgetter_using_someone_elses_number")
					request.session["account_kit_verification_failure_reason"] = '8'#someone elses number, trying to dupe forgot password
					request.session.modified = True
					return redirect("account_kit_forgot_pass_verification_failed")
				else:
					# let the user set a new password
					# template_name = "unauth/set_new_password_ur.html" if lang == 'ur' else "unauth/set_new_password.html"
					# return render(request,template_name,{'form':ResetForgettersPasswordForm()})
					request.session["allwd_set_new_pass"] = '1'
					request.session.modified = True
					return redirect("account_kit_forgot_pass_verification_successful")
			else:
				# this user's mobile number is questionable, make them do everything again
				request.session.pop('forgetters_username',None)
				request.session.pop('forgetters_userid',None)
				log_fp_ak_user_verification_outcome("forgetters_number_questionable")
				request.session["account_kit_verification_failed"] = '1'
				request.session["account_kit_verification_failure_reason"] = '7'#someone elses number, trying to dupe forgot password
				return redirect("account_kit_forgot_pass_verification_failed")
		else:
			# something went wrong, do it again
			log_fp_ak_user_verification_outcome("forgetter_ran_into_unknown_error")
			request.session.pop('forgetters_username',None)
			request.session.pop('forgetters_userid',None)
			request.session["account_kit_verification_failed"] = '1'
			request.session["account_kit_verification_failure_reason"] = '7'#someone elses number, trying to dupe forgot password
			return redirect("account_kit_forgot_pass_verification_failed")


def render_set_new_password(request):
	"""
	Renders form where user can set a new password (part of the forgot password flow)
	"""
	if request.user.is_authenticated():
		return redirect('for_me')
	else:
		if request.session.get("allwd_set_new_pass",'') == '1':
			log_fp_ak_user_verification_outcome("forgetter_on_setting_pass_screen")
			request.session.pop("allwd_set_new_pass",'')
			return render(request,'unauth/set_new_password.html',{'form':ResetForgettersPasswordForm()})
		else:
			return redirect("login")


# Functions below are used when inhouse SMS systems are deployed for password retrieval

# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
# @csrf_protect
# def send_SMS_to_forgetter(request, lang=None, *args, **kwargs):
# 	"""
# 	This sends pin code to forgetter's number for password recovery purposes
# 	"""
# 	print "func inside send sms to forgetter"
# 	if request.user.is_authenticated():
# 		return redirect('for_me')
# 	elif request.method == "POST":
# 		username = request.session.get('forgetters_username',None)
# 		user_id = request.session.get('forgetters_userid',None)
# 		form = ForgettersMobileNumber(request.POST,user_id=user_id, lang=lang)
# 		if form.is_valid():
# 			fg_ttl = is_forgot_password_rate_limited(user_id)
# 			if fg_ttl:
# 				# user 'recently' successfully used forgot password to retrieve their password - don't let them do it again
# 				import time
# 				template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
# 				return render(request,template_name,{'form':ForgettersNicknameForm(),'fg_rate_limit':time.time()-fg_ttl if lang == 'ur' else fg_ttl})
# 			else:
# 				phonenumber, sms_ttl = form.cleaned_data.get("phonenumber")
# 				if sms_ttl:
# 					# SMS sending is rate limited (because SMS already sent)
# 					template_name = "unauth/verify_forgetters_pin_ur.html" if lang == 'ur' else "unauth/verify_forgetters_pin.html"
# 					return render(request,template_name,{'form':ForgettersPin(),'reentry_instr':True})
# 				else:
# 					target_number = '+92'+phonenumber[-10:]
# 					# generate and send a pin code to the given mobile number
# 					send_user_pin.delay(user_id, target_number)
# 					twiliolog_pin_sms_sent(forgot_pass=True)
# 					template_name = "unauth/verify_forgetters_pin_ur.html" if lang == 'ur' else "unauth/verify_forgetters_pin.html"
# 					return render(request,template_name,{'form':ForgettersPin()})
# 		else:
# 			template_name = "unauth/verify_forgetters_account_ur.html" if lang == 'ur' else "unauth/verify_forgetters_account.html"
# 			return render(request,template_name,{'form':form})
# 	else:
# 		# not a POST request
# 		return redirect("forgot_password")


# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
# @csrf_protect
# def verify_forgetters_pin(request, lang=None, *args, **kwargs):
# 	"""
# 	Verify's whether the pin code entered by the forgetter is the correct one
# 	"""
# 	if request.user.is_authenticated():
# 		return redirect('for_me')
# 	elif request.method == "POST":
# 		username = request.session.get('forgetters_username',None)
# 		user_id = request.session.get('forgetters_userid',None)
# 		form = ForgettersPin(request.POST,user_id=user_id, lang=lang)
# 		if form.is_valid():
# 			fg_ttl = is_forgot_password_rate_limited(user_id)
# 			if fg_ttl:
# 				# user 'recently' successfully used forgot password to retrieve their password - don't let them do it again
# 				import time
# 				template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
# 				return render(request,template_name,{'form':ForgettersNicknameForm(),'fg_rate_limit':time.time()-fg_ttl if lang == 'ur' else fg_ttl})
# 			else:
# 				pin_state = form.cleaned_data.get("pinnumber")
# 				if pin_state == 'pin_matched':
# 					# pin verified - now allow the user to change their password
# 					twiliolog_user_verified(forgot_pass=True)
# 					request.session.pop('forgetters_username',None)
# 					template_name = "unauth/set_new_password_ur.html" if lang == 'ur' else "unauth/set_new_password.html"
# 					return render(request,template_name,{'form':ResetForgettersPasswordForm()})
# 				else:
# 					# pin_state is 'invalid' or 'expired' - start from scratch
# 					template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
# 					return render(request,template_name,{'form':ForgettersNicknameForm(),'pin_expired':True})
# 		else:
# 			template_name = "unauth/verify_forgetters_pin_ur.html" if lang == 'ur' else "unauth/verify_forgetters_pin.html"
# 			return render(request,template_name,{'form':form})
# 	else:
# 		# not a POST request
# 		return redirect("forgot_password")


# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
# @csrf_protect
# def set_forgetters_password(request, lang=None, *args, **kwargs):
# 	"""
# 	This enables a verified user (who's forgotten their password) to simply type a new one
# 	"""
# 	if request.user.is_authenticated():
# 		return redirect('for_me')
# 	elif request.method == "POST":
# 		user_id = request.session.get('forgetters_userid',None)
# 		if user_id:
# 			user = User.objects.get(id=user_id)
# 			form = ResetForgettersPasswordForm(data=request.POST, user=user, lang=lang)
# 			if form.is_valid():
# 				fg_ttl = is_forgot_password_rate_limited(user_id)
# 				if fg_ttl:
# 					# user 'recently' successfully used forgot password to retrieve their password - don't let them do it again'
# 					import time
# 					template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
# 					return render(request,template_name,{'form':ForgettersNicknameForm(),'fg_rate_limit':time.time()-fg_ttl if lang == 'ur' else fg_ttl})
# 				else:
# 					password = form.cleaned_data['password']
# 					form.save()
# 					user = authenticate(username=user.username,password=password)
# 					quick_login(request,user)
# 					request.user.session_set.exclude(session_key=request.session.session_key).delete() # logging the user out of everywhere else
# 					request.session.pop('forgetters_userid',None)
# 					set_forgot_password_rate_limit(user_id)
# 					return render(request,'change_password/new_password.html',{'new_pass':password})
# 			else:
# 				template_name = "unauth/set_new_password_ur.html" if lang == 'ur' else "unauth/set_new_password.html"
# 				return render(request,template_name,{'form':form})
# 		else:
# 			template_name = "unauth/forgot_password_ur.html" if lang == 'ur' else "unauth/forgot_password.html"
# 			return render(request,template_name,{'form':ForgettersNicknameForm(),"did_not_work":True})
# 	else:
# 		return redirect("forgot_password")


######################## Used to log in Google (enable when required) ############################


@csrf_exempt
def log_google_in(request, *args, **kwargs):
	"""
	Enable POST commented lines when required
	"""
	if request.method == "POST":
		# user = authenticate(username=request.POST.get("username",None),password=request.POST.get("password",None))
		# quick_login(request,user)
		return redirect('photo','best-list')
	else:
		return render(request,"unauth/login_backdoor.html",{'form':CreateAccountForm()})


########################################## Logging In ############################################


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
@ratelimit(method='POST', rate='21/h')
def login(request, lang=None, *args, **kwargs):
	"""
	Renders and processes the returning user login form
	"""
	if request.user.is_authenticated():
		return redirect('for_me')
	else:
		was_limited = getattr(request, 'limits', False)
		if was_limited:
			template_name = 'unauth/penalty_login_ur.html' if lang == 'ur' else 'unauth/penalty_login.html'
			return render(request, template_name, {})
		else:
			if request.method == 'POST':
				if not request.session.test_cookie_worked():
					return render(request,"CSRF_failure.html",{'referrer':request.META.get('HTTP_REFERER',None)})
				try:
					request.session.delete_test_cookie() #cleaning up
				except:
					pass
				form = SignInForm(data=request.POST, lang=lang)
				if form.is_valid():
					quick_login(request,form.cleaned_data)
					return redirect('for_me')
				else:
					request.session.set_test_cookie()
					template_name = "unauth/sign_in_ur.html" if lang == 'ur' else "unauth/sign_in.html"
					return render(request,template_name,{'form':form})
			else:
				just_logged_out = request.session.pop("logged_out",None)
				request.session.set_test_cookie()
				template_name = "unauth/sign_in_ur.html" if lang == 'ur' else "unauth/sign_in.html"
				return render(request,template_name,{'form':SignInForm(),'just_logged_out':True if just_logged_out == '1' else False})


############################################ Account Creation ##########################################



@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def create_account(request,lang=None,slug1=None,length1=None,slug2=None,length2=None,*args,**kwargs):
	if request.user.is_authenticated():
		return redirect('for_me')
	elif account_creation_disallowed(getip(request)):
		template_name = 'unauth/penalty_account_create_ur.html' if lang == 'ur' else 'unauth/penalty_account_create.html'
		return render(request,template_name,{})
	elif request.method == 'POST':
		form = CreateAccountForm(data=request.POST, lang=lang)
		err = request.POST.get("err",None)
		if err is not None:
			return redirect("unauth_home_new", lang)
		else:
			if form.is_valid():
				# ensured username is unique, no one else has booked it
				password = slug2.decode("hex")
				username = slug1.decode("hex")
				form.save() # creating the user
				user = authenticate(username=username,password=password)
				login(request,user)
				registration_task.delay(getip(request),username)
				try:
					request.session.delete_test_cookie() #cleaning up
				except:
					pass
				request.session["first_time_user"] = 1
				#############
				#############
				#############
				tried_banned_word = request.session.pop("banned_word_caught",None)
				if tried_banned_word == '1':
					log_post_banned_username(username)
				#############
				#############
				#############
				return redirect("new_user_gateway",lang=lang)
			else:
				# user couldn't be created because while user was deliberating, someone else booked the nickname! OR user tinkered with the username/password values
				username = slug1.decode("hex")
				password = slug2.decode("hex")
				template_name = 'unauth/create_account_ur.html' if lang == 'ur' else 'unauth/create_account.html'
				return render(request,template_name,{'password':password,'username':username,'uhex':slug1,'ulen':length1,'phex':slug2,\
					'plen':length2,'form':form})
	else:
		# request.session.pop("new_id", None)
		if len(slug1) == int(length1) and len(slug2) == int(length2):
			form = CreateAccountForm()
			username = slug1.decode("hex")
			password = slug2.decode("hex")
			context={'password':password,'username':username,'uhex':slug1,'ulen':length1,'phex':slug2,'plen':length2,'form':form}
			template_name = 'unauth/create_account_ur.html' if lang == 'ur' else 'unauth/create_account.html'
			return render(request,template_name, context)
		else:
			# some tinerking in the link has taken place
			template_name = 'unauth/penalty_link_tinkered_ur.html' if lang == 'ur' else 'unauth/penalty_link_tinkered.html'
			return render(request,template_name,{})

############################################################################################################

# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
@csrf_protect
def create_password_new(request,lang=None,slug=None,length=None,*args,**kwargs):
	if request.user.is_authenticated():
		return redirect('for_me')
	elif account_creation_disallowed(getip(request)):
		template_name = 'unauth/penalty_account_create_ur.html' if lang == 'ur' else 'unauth/penalty_account_create.html'
		return render(request,template_name,{})
	elif request.method == 'POST':
		form = CreatePasswordForm(data=request.POST,lang=lang)
		if form.is_valid():
			# show user the password in the next screen
			if int(length) == len(slug):
				password = form.cleaned_data['password']
				result = password.encode('utf-8').encode("hex")
				length1 = len(slug)
				length2 = len(result)
				if lang == "ur":
					return redirect('create_account',lang=lang,slug1=slug,length1=length1,slug2=result,length2=length2)
				else:
					return redirect('create_account',slug1=slug,length1=length1,slug2=result,length2=length2)
			else:
				# some tinerking in the link has taken place
				template_name = 'unauth/penalty_link_tinkered_ur.html' if lang == 'ur' else 'unauth/penalty_link_tinkered.html'
				return render(request,template_name,{})
		else:
			if int(length) == len(slug):
				username = slug.decode("hex")
				template_name = 'unauth/create_password_new_ur.html' if lang == 'ur' else 'unauth/create_password_new.html'
				return render(request, template_name, {'form':form,'username':username,'uhex':slug,'length':length})
			else:
				# some tinerking in the link has taken place
				template_name = 'unauth/penalty_link_tinkered_ur.html' if lang == 'ur' else 'unauth/penalty_link_tinkered.html'
				return render(request,template_name,{})
	else:
		# mp.track(request.session.get('tid',None), 'load_pass')
		if request.session.test_cookie_worked():
			form = CreatePasswordForm()
			if int(length) == len(slug):
				username = slug.decode("hex")
				template_name = 'unauth/create_password_new_ur.html' if lang == 'ur' else 'unauth/create_password_new.html'
				return render(request, template_name, {'form':form,'username':username,'uhex':slug,'length':length})
			else:
				# some tinerking in the link has taken place
				template_name = 'unauth/penalty_link_tinkered_ur.html' if lang == 'ur' else 'unauth/penalty_link_tinkered.html'
				return render(request,template_name,{})
		else:
			#cookies aren't being set in the browser, so can't make an account!
			template_name = 'unauth/penalty_cookie_ur.html' if lang == 'ur' else 'unauth/penalty_cookie.html'
			return render(request, template_name, {})


# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
@csrf_protect		
def create_nick_new(request,lang=None,*args,**kwargs):
	if request.user.is_authenticated():
		return redirect('for_me')
	elif account_creation_disallowed(getip(request)):
		template_name = 'unauth/penalty_account_create_ur.html' if lang == 'ur' else 'unauth/penalty_account_create.html'
		return render(request, template_name,{})
	elif request.method == 'POST':
		form = CreateNickNewForm(data=request.POST,lang=lang)
		sys_sugg = request.POST.get('system_suggestion',None)
		if sys_sugg:
			#process system suggestion
			result = sys_sugg.encode("hex")
			length = len(result)
			request.session.set_test_cookie()
			if lang == "ur":
				return redirect('create_password_new', lang=lang, slug=result,length=length)
			else:
				return redirect('create_password_new', slug=result,length=length)
		else:
			if form.is_valid():
				alt_choices, altered, original = form.cleaned_data['username']
				if altered:
					single = True if len(alt_choices) == 1 else False# whether to show a single suggestion, or multiple suggestions
					template_name = 'unauth/recreate_nick_ur.html' if lang == 'ur' else 'unauth/recreate_nick.html'
					return render(request,template_name,{'original':original,'single':single,'alternatives':alt_choices,'status':altered["status"]})
				else:
					# divide between suggestion and actual nick
					result = original.encode("hex")
					length = len(result)
					request.session.set_test_cookie() #set it now, to test it in the next view
					if lang == "ur":
						return redirect('create_password_new',lang=lang, slug=result,length=length)
					else:
						return redirect('create_password_new',slug=result,length=length)
			else:
				template_name = 'unauth/create_nick_new_ur.html' if lang == 'ur' else 'unauth/create_nick_new.html'
				##################
				##################
				##################
				try:
					err_string = form.errors.as_text().split("*")[2]
					if err_string[-5:].encode("utf-8") in ('sakta','ڈالیں'):
						request.session["banned_word_caught"] = '1'
						request.session.modified = True
				except (IndexError,TypeError):
					pass
				##################
				##################
				##################
				return render(request, template_name, {'form':form})
	else:
		template_name = 'unauth/create_nick_new_ur.html' if lang == 'ur' else 'unauth/create_nick_new.html'
		return render(request, template_name, {'form':CreateNickNewForm()})


def unauth_home_new(request,lang=None,*args,**kwargs):
	"""
	Renders English and Urdu versions of the landing page
	"""
	if request.user.is_authenticated():
		return redirect('for_me')
	else:
		template_name = "unauth/unauth_home_ur.html" if lang == 'ur' else "unauth/unauth_home.html"
		return render(request,template_name,{'form':CreateNickNewForm()})