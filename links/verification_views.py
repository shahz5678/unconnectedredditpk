import uuid
from django.db.models import F
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from verification_forms import AddVerifiedUserForm, rate_limit_artificial_verification
from redis3 import save_consumer_number
from redis4 import retrieve_uname
from models import UserProfile

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