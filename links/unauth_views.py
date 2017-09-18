import shortuuid
from django.db import transaction
from django.contrib.auth import login as quick_login
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
######################################################################################
from django.contrib.auth.views import login as log_me_in
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.middleware import csrf
from tasks import registration_task
from redis1 import account_creation_disallowed
from redis3 import insert_nick
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from django.views.decorators.debug import sensitive_post_parameters
from redis3 import get_temp_id, nick_already_exists, is_mobile_verified#, log_forgot_password
from unauth_forms import CreateAccountForm, CreatePasswordForm, CreateNickNewForm, ResetForgettersPasswordForm, SignInForm
from forms import getip
from score import PW
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


# this enables a verified user who's forgotten their password to create a new one
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def set_forgetters_password(request, *args, **kwargs):
	if request.method == "POST":
		user_id = request.POST.get("user_id",None)
		if user_id:
			user = User.objects.get(id=user_id)
			form = ResetForgettersPasswordForm(data=request.POST, user=user)
			if form.is_valid():
				password = form.cleaned_data['password']
				form.save()
				user = authenticate(username=user.username,password=password)
				quick_login(request,user)
				request.user.session_set.exclude(session_key=request.session.session_key).delete() # logging the user out of everywhere else
				##############################################
				#log_forgot_password(user_id=user_id,username=user.username,flow_level='end')# it's okay if lots of dangling 'starts' remain. Dangling 'ends' should not exist though!
				##############################################
				return render(request,'new_password.html',{'new_pass':password})
			else:
				return render(request,"set_new_password.html",{'form':form,'user_id':user_id})
		else:
			# import time
			# log_forgot_password(user_id=time.time(),username='None',flow_level='bad-end') # logging instances where user_id didn't exist
			return render(request,"try_again.html",{'type':'forgetter'})
	else:
		return render(request, "404.html",{})


# this initiates the forgot password flow, and ensures the user's mobile number if verified
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def forgot_password(request, lang=None, *args, **kwargs):
	if request.method == "POST":
		form = CreateNickNewForm(data=request.POST)
		if form.is_valid():
			username = form.cleaned_data['username'][2] # the returned username is a tuple with 3 entries, pick the last one
			exists = nick_already_exists(username, exact=True)
			if exists:
				# the nickname exists
				user_id = User.objects.only('id').get(username=username).id
			elif exists is None:
				try:
					user_id = User.objects.only('id').get(username=username).id
				except User.DoesNotExist:
					# username is not taken
					if lang == 'ur':
						return render(request,"forgot_password_ur.html",{'form':form,'nick':username,'nick_does_not_exist':True})
					else:
						return render(request,"forgot_password.html",{'form':form,'nick':username,'nick_does_not_exist':True})
			elif exists is False:
				if lang == "ur":
					return render(request,"forgot_password_ur.html",{'form':form,'nick':username,'nick_does_not_exist':True})
				else:
					return render(request,"forgot_password.html",{'form':form,'nick':username,'nick_does_not_exist':True})
			###################################################################################################
			is_verified = is_mobile_verified(user_id)
			if is_verified:
				################################################
				#log_forgot_password(user_id=user_id,username=username,flow_level='start')#
				################################################
				if lang == "ur":
					return render(request,"verify_forgetters_account_ur.html",{'user_id':user_id, 'id_in_csrf':True})
				else:
					return render(request,"verify_forgetters_account.html",{'user_id':user_id, 'id_in_csrf':True})
			else:
				if lang == "ur":
					return render(request,"nick_unassociated_with_mobnum_ur.html",{'nick':username})
				else:
					return render(request,"nick_unassociated_with_mobnum.html",{'nick':username})
		else:
			if lang == "ur":
				return render(request,"forgot_password_ur.html",{'form':form})
			else:
				return render(request,"forgot_password.html",{'form':form})
	else:
		form = CreateNickNewForm()
		if lang == 'ur':
			return render(request,"forgot_password_ur.html",{'form':form})
		else:
			return render(request,"forgot_password.html",{'form':form})

######################################################################################

@csrf_exempt
def log_google_in(request, *args, **kwargs):
	if request.method == "POST":
		user = authenticate(username=request.POST.get("username",None),password=request.POST.get("password",None))
		quick_login(request,user)
		return redirect("ur_home", 'urdu')
	else:
		form = CreateAccountForm()
		return render(request,"login_backdoor.html",{'form':form})


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
@ratelimit(method='POST', rate='11/h')
def login(request, lang=None, *args, **kwargs):
	if request.user.is_authenticated():
		return redirect("home")
	else:
		was_limited = getattr(request, 'limits', False)
		if was_limited:
			if lang == "ur":
				return render(request, 'penalty_login_ur.html', {})
			else:
				return render(request, 'penalty_login.html', {})
		else:
			if request.method == 'POST':
				if not request.session.test_cookie_worked():
					context = {'referrer':request.META.get('HTTP_REFERER',None)}
					return render(request,"CSRF_failure.html",context)
				try:
					request.session.delete_test_cookie() #cleaning up
				except:
					pass
				form = SignInForm(data=request.POST)
				if form.is_valid():
					quick_login(request,form.cleaned_data)
					if lang == "ur":
						return redirect("ur_home", 'urdu')
					else:
						return redirect("home")
				else:
					request.session.set_test_cookie()
					if lang == 'ur':
						return render(request,"sign_in_ur.html",{'form':form})
					else:
						return render(request,"sign_in.html",{'form':form})
			else:
				form = SignInForm()
				request.session.set_test_cookie()
				if lang == 'ur':
					return render(request,"sign_in_ur.html",{'form':form})
				else:
					return render(request,"sign_in.html",{'form':form})


######################################################################################

def unauth_home_new_ur(request,*args,**kwargs):
	if request.user.is_authenticated():
		return redirect("home")
	else:
		form = CreateNickNewForm()
		return render(request,"unauth_home_ur.html",{'form':form})

def unauth_home_new(request,*args,**kwargs):
	if request.user.is_authenticated():
		return redirect("home")
	else:
		# guest_id = request.session.get('guest_id',None)
  # 		if not guest_id:
  # 			guest_id = get_temp_id()
  # 			request.session['guest_id'] = guest_id
  # 		mp.track(guest_id, 'new_signup_page')
		form = CreateNickNewForm()
		return render(request,"unauth_home.html",{'form':form})
		#########################################################################
		# print guest_id
		# print variation
		# if variation == 'with_loc':
		# 	# load new unauth_page (with Urdu translation)
		# 	return render(request,"unauth_home.html",{'form':form})
		# elif variation == 'without_loc':
		# 	return render(request,"unauth_home_old.html",{'form':form})
		# else:
		# 	return render(request,"unauth_home_old.html",{'form':form})
		#########################################################################

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def create_account(request,lang=None,slug1=None,length1=None,slug2=None,length2=None,*args,**kwargs):
	if account_creation_disallowed(getip(request)):
		if lang == "ur":
			return render(request,'penalty_account_create_ur.html',{})
		else:
			return render(request,'penalty_account_create.html',{})
	elif request.method == 'POST':
		form = CreateAccountForm(data=request.POST)
		if form.is_valid():
			# ensured username is unique, no one else has booked it
			password = slug2.decode("hex")
			username = slug1.decode("hex")
			form.save() # creating the user
			user = authenticate(username=username,password=password)
			login(request,user)
			registration_task.delay(getip(request),username,user.id)
			try:
				request.session.delete_test_cookie() #cleaning up
			except:
				pass
			request.session["first_time_user"] = 1
			return redirect("new_user_gateway",lang=lang)
			# return redirect("first_time_link")
			####################################################################################
			####################################################################################
			# return redirect("new_user_gateway",lang=lang)
			####################################################################################
			####################################################################################
		else:
			# user couldn't be created because while user was deliberating, someone else booked the nickname! OR user tinkered with the username/password values
			username = slug1.decode("hex")
			password = slug2.decode("hex")
			context={'no_credentials':False,'password':password,'username':username,'uhex':slug1,\
			'ulen':length1,'phex':slug2,'plen':length2,'form':form}
			if lang == 'ur':
				return render(request, 'create_account_ur.html', context)
			else:
				return render(request, 'create_account.html', context)
	else:
		# request.session.pop("new_id", None)
		if len(slug1) == int(length1) and len(slug2) == int(length2):
			form = CreateAccountForm()
			username = slug1.decode("hex")
			password = slug2.decode("hex")
			context={'no_credentials':False,'password':password,'username':username,'uhex':slug1,\
			'ulen':length1,'phex':slug2,'plen':length2,'form':form}
			# mp.track(request.session.get('tid',None), 'create_new_account')
			if lang == 'ur':
				return render(request, 'create_account_ur.html', context)
			else:
				return render(request, 'create_account.html', context)
		else:
			# some tinerking in the link has taken place
			if lang == 'ur':
				return render(request,'penalty_link_tinkered_ur.html',{})
			else:
				return render(request,'penalty_link_tinkered.html',{})

############################################################################################################

# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
@csrf_protect
def create_password_new(request,lang=None,slug=None,length=None,*args,**kwargs):
	if account_creation_disallowed(getip(request)):
		if lang == 'ur':
			return render(request,'penalty_account_create_ur.html',{})
		else:
			return render(request,'penalty_account_create.html',{})
	elif request.method == 'POST':
		form = CreatePasswordForm(data=request.POST,request=request)
		if form.is_valid():
			# show user the password in the next screen
			if int(length) == len(slug):
				password = form.cleaned_data['password']
				result = password.encode('utf-8').encode("hex")
				length1 = len(slug)
				length2 = len(result)
				# mp.track(request.session.get('guest_id',None), 'pass_finalized')
				if lang == "ur":
					return redirect('create_account',lang=lang,slug1=slug,length1=length1,slug2=result,length2=length2)
				else:
					return redirect('create_account',slug1=slug,length1=length1,slug2=result,length2=length2)
			else:
				# some tinerking in the link has taken place
				if lang == "ur":
					return render(request,'penalty_link_tinkered_ur.html',{})
				else:
					return render(request,'penalty_link_tinkered.html',{})
		else:
			###############################Logging Erroneous Password#####################################
			# try:
			# 	password = request.POST.get("password",None)
			# 	password = 'specificity' if password == '' else password
			# 	error_string = str(dict(form.errors)["password"]).split('<li>')[1].split('</li>')[0]
			# 	log_erroneous_passwords(password,error_string)
			# except:
			# 	pass
			##############################################################################################
			if int(length) == len(slug):
				username = slug.decode("hex")
				context={'form':form,'username':username,'uhex':slug,'length':length}
				if lang == "ur":
					return render(request, 'create_password_new_ur.html', context)
				else:
					return render(request, 'create_password_new.html', context)
			else:
				# some tinerking in the link has taken place
				if lang == "ur":
					return render(request,'penalty_link_tinkered_ur.html',{})
				else:
					return render(request,'penalty_link_tinkered.html',{})
	else:
		# mp.track(request.session.get('tid',None), 'load_pass')
		if request.session.test_cookie_worked():
			form = CreatePasswordForm()
			# mp.track(request.session.get('tid',None), 'create_new_pass')
			if int(length) == len(slug):
				username = slug.decode("hex")
				context={'form':form,'username':username,'uhex':slug,'length':length}
				if lang == "ur":
					return render(request, 'create_password_new_ur.html', context)
				else:
					return render(request, 'create_password_new.html', context)
			else:
				# some tinerking in the link has taken place
				if lang == "ur":
					return render(request,'penalty_link_tinkered_ur.html',{})
				else:
					return render(request,'penalty_link_tinkered.html',{})
		else:
			#cookies aren't being set in the browser, so can't make an account!
			if lang == "ur":
				return render(request, 'penalty_cookie_ur.html', {})
			else:
				return render(request, 'penalty_cookie.html', {})

# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
@csrf_protect		
def create_nick_new(request,lang=None,*args,**kwargs):
	if request.user.is_authenticated():
		return render(request,'404.html',{})
	elif account_creation_disallowed(getip(request)):
		if lang == 'ur':
			return render(request, 'penalty_account_create_ur.html',{})
		else:
			return render(request, 'penalty_account_create.html',{})
	elif request.method == 'POST':
		form = CreateNickNewForm(data=request.POST)
		sys_sugg = request.POST.get('system_suggestion',None)
		if sys_sugg:
			#process system suggestion
			result = sys_sugg.encode("hex")
			length = len(result)
			request.session.set_test_cookie()
			# mp.track(request.session.get('guest_id',None), 'name_finalized')
			if lang == "ur":
				return redirect('create_password_new', lang=lang, slug=result,length=length)
			else:
				return redirect('create_password_new', slug=result,length=length)
		else:
			if form.is_valid():
				alt_choices, altered, original = form.cleaned_data['username']
				if altered:
					if len(alt_choices) == 1:
						#show single suggestion
						if lang == "ur":
							return render(request,'recreate_nick_ur.html',{'original':original,'single':True,'alternatives':alt_choices,\
								'status':altered["status"]})
						else:
							return render(request,'recreate_nick.html',{'original':original,'single':True,'alternatives':alt_choices,\
								'status':altered["status"]})
					else:
						#show multiple suggestions
						if lang == "ur":
							return render(request,'recreate_nick_ur.html',{'original':original,'single':False,'alternatives':alt_choices,\
								'status':altered["status"]})
						else:
							return render(request,'recreate_nick.html',{'original':original,'single':False,'alternatives':alt_choices,\
								'status':altered["status"]})
				else:
					# divide between suggestion and actual nick
					result = original.encode("hex")
					length = len(result)
					request.session.set_test_cookie() #set it now, to test it in the next view
					# mp.track(request.session.get('guest_id',None), 'name_finalized')
					if lang == "ur":
						return redirect('create_password_new',lang=lang, slug=result,length=length)
					else:
						return redirect('create_password_new',slug=result,length=length)
			else:
				context = {'form':form}
				##########################Logging Erroneous Usernames##########################
				# try:
				# 	username = request.POST.get("username",None)
				# 	username = 'specificity' if username == '' else username
				# 	error_string = str(dict(form.errors)["username"]).split('<li>')[1].split('</li>')[0]
				# 	log_erroneous_passwords(username,error_string)
				# except:
				# 	pass
				###############################################################################	
				# mp.track(request.session.get('tid',None), 'retry_new_nick')
				if lang == 'ur':
					return render(request, 'create_nick_new_ur.html', context)
				else:
					return render(request, 'create_nick_new.html', context)
	else:
		form = CreateNickNewForm()
		# mp.track(request.session.get('tid',None), 'create_new_nick')
		if lang == 'ur':
			return render(request, 'create_nick_new_ur.html', {'form':form})
		else:
			return render(request, 'create_nick_new.html', {'form':form})
