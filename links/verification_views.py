import time
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from verification_forms import AddVerifiedUserForm, rate_limit_artificial_verification, MobileVerificationForm, PinVerifyForm
from redis3 import save_consumer_number, is_mobile_verified, is_sms_sending_rate_limited, twiliolog_pin_sms_sent, twiliolog_user_verified,\
twiliolog_reverification_pin_sms_sent, twiliolog_user_reverified, log_fbs_please_wait, log_fbs_user_verification
from redis5 import can_change_number, get_personal_group_target_id, get_personal_group_anon_state, set_personal_group_mobile_num_cooloff
from tasks import send_user_pin, save_consumer_credentials, increase_user_points
from score import NUMBER_VERIFICATION_BONUS, FBS_VERIFICATION_WAIT_TIME
from views import convert_to_epoch
from redis4 import retrieve_uname
from models import UserProfile


############################## Artificial user number verification #################################


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def verify_user_artificially(request):
	"""
	This renders a template where user_ids can be artificially verified (mobile)

	This also processes the verification step
	"""
	if retrieve_uname(request.user.id,decode=True) in ['pathan-e-khan','Damadam-Feedback','mhb11']:
		if request.method == "POST":
			processed_form = AddVerifiedUserForm(request.POST)
			if processed_form.is_valid():
				success = rate_limit_artificial_verification()
				if success:
					import uuid
					from django.db.models import F
					valid_user_id = processed_form.cleaned_data.get("user_id")
					random_string = str(uuid.uuid4())
					account_kid_id = 'artificial_verification'		
					mobile_data = {'national_number':random_string,'number':random_string,'country_prefix':'92'}
					with_points = request.POST.get("wth_pts",None)
					save_consumer_number(account_kid_id,mobile_data,valid_user_id)
					if with_points == '1':
						UserProfile.objects.filter(user_id=valid_user_id).update(score=F('score')+500)
					
					return render(request,"verification/artificial_verification.html",{'form':AddVerifiedUserForm(),\
						'verified_id':valid_user_id})
				else:
					return redirect('missing_page')
			else:
				return render(request,"verification/artificial_verification.html",{'form':processed_form})
		else:
			# it's a GET request
			return render(request,"verification/artificial_verification.html",{'form':AddVerifiedUserForm()})
	else:
		return redirect('missing_page')


############################## User number verification #################################


def number_verification_help(request):
	"""
	Renders help page showing the advantages of verification
	"""
	return render(request,"verification/num_verification_help.html",{})

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def wait_before_verifying(request):
	"""
	Prompt shown to FBS based would-be verifiers, chiding them to wait 24 hours before dipping their beaks in the verification bucket
	"""
	user_id = request.user.id
	if request.method == "POST":
		if is_mobile_verified(user_id):
			return redirect("home")
		else:
			on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
			if on_fbs:
				joining_epoch_time = convert_to_epoch(request.user.date_joined)
				expire_at = joining_epoch_time + FBS_VERIFICATION_WAIT_TIME
				ttw = expire_at - time.time()
				if ttw > 0:
					# expiry of this lock is a 'future' event
					return render(request,'verification/wait_before_verifying.html',{'redirect_to_paid_internet':True})
				else:
					# this lock has expired!
					return redirect("verify_user_mobile")
			else:
				return redirect("verify_user_mobile")
	else:
		try:
			joining_epoch_time = convert_to_epoch(request.user.date_joined)
			expire_at = joining_epoch_time + FBS_VERIFICATION_WAIT_TIME
			ttw = expire_at - time.time()
			if ttw > 0:
				# expiry of this lock is a 'future' event
				log_fbs_please_wait(user_id=user_id, expire_at=int(expire_at))
				return render(request, "verification/wait_before_verifying.html", {'time_to_wait':int(ttw)})
			else:
				# this lock has expired!
				return redirect("verify_user_mobile")
		except (ValueError, TypeError):
			return redirect('missing_page')				

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def verify_user_mobile(request):
	"""
	This renders a template where user puts her number that she wants verified

	"""
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	user_id = request.user.id
	if on_fbs:
		joining_epoch_time = convert_to_epoch(request.user.date_joined)
		if joining_epoch_time + FBS_VERIFICATION_WAIT_TIME - time.time() > 0:
			# rate limited from verifying currently, inform accordingly
			return redirect("wait_before_verifying")
	######################################
	if is_mobile_verified(user_id): 
		if can_change_number(user_id) and get_personal_group_target_id(user_id):
			# allow this user to proceed, even though (s)he is already verified
			if request.method == "POST":
				form = MobileVerificationForm(request.POST,user_id=user_id,allow_reverification=True)
				ttl = is_sms_sending_rate_limited(user_id)
				if ttl:
					return render(request,"verification/enter_pin_code.html",{'form':PinVerifyForm(),'ttl':ttl,'reentry_instr':True})
				elif form.is_valid():
					phonenumber = form.cleaned_data.get("phonenumber")
					target_number = '+92'+phonenumber[-10:]
					# generate and send a pin code to the given mobile number
					send_user_pin.delay(user_id, target_number)
					twiliolog_reverification_pin_sms_sent()
					request.session['phonenumber'+str(user_id)] = phonenumber
					request.session['for_personal_group'] = '1'
					request.session.modified = True
					return render(request,"verification/enter_pin_code.html",{'form':PinVerifyForm()})
				else:
					return render(request,'verification/user_mobile_verification.html',{'form':form})
			else:
				# it's a GET request
				ttl = is_sms_sending_rate_limited(user_id)
				if ttl:
					return render(request,"verification/enter_pin_code.html",{'form':PinVerifyForm(),'ttl':ttl,'reentry_instr':True})
				else:
					return render(request,'verification/user_mobile_verification.html',{'form':MobileVerificationForm(),\
						'pin_expired':request.session.pop("start_verification_again"+str(user_id),None),'for_personal_group':True})
		else:
			# not allowed to proceed
			return redirect("missing_page")
	else:
		# is allowed to proceed
		if request.method == "POST":
			form = MobileVerificationForm(request.POST,user_id=user_id,allow_reverification=False)
			ttl = is_sms_sending_rate_limited(user_id)
			if ttl:
				return render(request,"verification/enter_pin_code.html",{'form':PinVerifyForm(),'ttl':ttl,'reentry_instr':True})
			elif form.is_valid():
				phonenumber = form.cleaned_data.get("phonenumber")
				target_number = '+92'+phonenumber[-10:]
				# generate and send a pin code to the given mobile number
				send_user_pin.delay(user_id, target_number)
				twiliolog_pin_sms_sent()
				request.session['phonenumber'+str(user_id)] = phonenumber    
				request.session.modified = True
				return render(request,"verification/enter_pin_code.html",{'form':PinVerifyForm()})
			else:
				return render(request,'verification/user_mobile_verification.html',{'form':form})
		else:
			# it's a GET request
			ttl = is_sms_sending_rate_limited(user_id)
			if ttl:
				return render(request,"verification/enter_pin_code.html",{'form':PinVerifyForm(),'ttl':ttl,'reentry_instr':True})
			else:
				return render(request,'verification/user_mobile_verification.html',{'form':MobileVerificationForm(),\
					'pin_expired':request.session.pop("start_verification_again"+str(user_id),None)})
	


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def pin_verification(request):
	"""
	This will verify the pin entered by the user
	"""
	if request.method == "POST":
		on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
		if on_fbs:
			joining_epoch_time = convert_to_epoch(request.user.date_joined)
			if joining_epoch_time + FBS_VERIFICATION_WAIT_TIME - time.time() > 0:
				# rate limited from verifying currently, inform accordingly
				return redirect("wait_before_verifying")
		###########################################################################
		user_id = request.user.id
		if is_mobile_verified(user_id):
			target_id = get_personal_group_target_id(user_id)
			if can_change_number(user_id) and target_id:
				form = PinVerifyForm(request.POST,user_id=user_id,allow_reverification=True)
				phonenumber = request.session.get('phonenumber'+str(user_id),None)
				if form.is_valid():
					pin_state = form.cleaned_data.get("pinnumber")
					if pin_state == 'pin_matched':
						request.session.pop("newbie_flag",None)# verified users aren't newbies by definition
						request.session.pop("newbie_lang",None)# verified users aren't newbies by definition
						for_personal_group = request.session.pop("for_personal_group",None)
						own_anon_status, their_anon_status, group_id = get_personal_group_anon_state(user_id, target_id)
						if for_personal_group == '1':
							request.session.pop('phonenumber'+str(user_id),None)
							account_kid_id = 'twilio_verification'
							national_number = phonenumber[-10:]
							number ='+92'+national_number	
							mobile_data = {'national_number':national_number,'number':number,'country_prefix':'92'}
							save_consumer_credentials.delay(account_kid_id, mobile_data, user_id)
							set_personal_group_mobile_num_cooloff(user_id)
							if their_anon_status is None:
								return redirect("home")
							else:
								twiliolog_user_reverified()
								log_fbs_user_verification(user_id, on_fbs=on_fbs, time_now=time.time())
								return render(request,"personal_group/sms_settings/personal_group_successful_mob_verification.html",\
									{'tid':target_id,'their_anon':their_anon_status,'name':retrieve_uname(target_id,decode=True),\
									'avatar':None if their_anon_status else UserProfile.objects.filter(user_id=target_id).values_list('avatar',flat=True)[0]})
						else:
							# maybe the key has already been popped, send the person back to the relevant personal group
							request.session["personal_group_gid_key:"+target_id] = group_id#checked
							request.session.modified = True
							return redirect("enter_personal_group")
					else:
						# pin_state is 'invalid' or 'expired'
						request.session['start_verification_again'+str(user_id)] = '1'
						request.session.modified = True
						return redirect("verify_user_mobile")
				else:
					return render(request,"verification/enter_pin_code.html",{'form':form})
			else:
				return redirect('missing_page')
		else:
			form = PinVerifyForm(request.POST,user_id=user_id,allow_reverification=False)
			phonenumber = request.session.get('phonenumber'+str(user_id),None)
			if form.is_valid():
				pin_state = form.cleaned_data.get("pinnumber")
				if pin_state == 'pin_matched':
					request.session.pop("newbie_flag",None)# verified users aren't newbies by definition
					request.session.pop("newbie_lang",None)# verified users aren't newbies by definition
					request.session.pop('phonenumber'+str(user_id),None)
					account_kid_id = 'twilio_verification'
					national_number = phonenumber[-10:]
					number ='+92'+national_number	
					mobile_data = {'national_number':national_number,'number':number,'country_prefix':'92'}
					save_consumer_credentials.delay(account_kid_id, mobile_data, user_id)
					increase_user_points.delay(user_id=user_id, increment=NUMBER_VERIFICATION_BONUS)
					twiliolog_user_verified()
					log_fbs_user_verification(user_id, on_fbs=on_fbs, time_now=time.time())
					return render(request,"verification/reward_earned.html",{})
				else:
					# pin_state is 'invalid' or 'expired'
					request.session['start_verification_again'+str(user_id)] = '1'
					request.session.modified = True
					return redirect("verify_user_mobile")
			else:
				return render(request,"verification/enter_pin_code.html",{'form':form})
	else:
		# not a POST request
		return redirect('missing_page')

	
############################## Pink star verification #################################