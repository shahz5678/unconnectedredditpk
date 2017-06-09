from django.contrib.auth.views import login as log_me_in
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from unauth_forms import CreateAccountForm, CreatePasswordForm, CreateNickNewForm
from redis1 import account_creation_disallowed
from redis3 import get_temp_id
from tasks import registration_task
from forms import getip
from mixpanel import Mixpanel
from unconnectedreddit.settings import MIXPANEL_TOKEN

mp = Mixpanel(MIXPANEL_TOKEN)

######################################################################################

# from optimizely_config_manager import OptimizelyConfigManager
# from unconnectedreddit.optimizely_settings import PID

# config_manager = OptimizelyConfigManager(PID)

######################################################################################

def login(request, lang=None, *args,**kwargs):
	if request.user.is_authenticated():
		return redirect("home")
	else:
		if request.method == 'POST':
			# opportunity to block entry here
			if lang == 'ur':
				return log_me_in(request=request,template_name='login_ur.html')
			else:
				return log_me_in(request=request,template_name='login.html')
		else:
			if lang == 'ur':
				return log_me_in(request=request,template_name='login_ur.html')
			else:
				return log_me_in(request=request,template_name='login.html')

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
  		# mp.track(guest_id, 'new_home_page')
		form = CreateNickNewForm()
		return render(request,"unauth_home.html",{'form':form})
		#########################################################################
		# variation = config_manager.get_obj().activate('reg_with_i8ln', guest_id)
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
		# print "recieved data"
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
			###############################################################
			# config_manager.get_obj().track('reg', request.session.get('guest_id',None))
			# print request.session.pop("guest_id", None)
			###############################################################
			mp.track(user.id,'sign_ups')
			# mp.alias(request.user.id, unreg_id)
			###############################################################
			return redirect("first_time_link") #REDIRECT TO A DIFFERENT PAGE
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
				# mp.track(request.session.get('unauth',None), 'password_finalized')
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
			# mp.track(request.session.get('unauth',None), 'nick_finalized')
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
					# mp.track(request.session.get('unauth',None), 'nick_finalized')
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

# @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
# @sensitive_post_parameters()
# @csrf_protect
# def create_account_ur(request,slug1=None,length1=None,slug2=None,length2=None,*args,**kwargs):
# 	pass

# @csrf_protect
# def create_password_new_ur(request,slug=None,length=None,*args,**kwargs):
# 	pass

# @csrf_protect
# def create_nick_new_ur(request,*args,**kwargs):
# 	pass
