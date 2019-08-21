from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from redis7 import in_defenders


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def redirect_to_content(request):
	"""
	Helper function for return_to_content()
	"""
	orig = request.POST.get("orig",None)
	topic = request.POST.get("topic",None)
	obid = request.POST.get("obid",None)
	oun = request.POST.get("oun",None)
	lid = request.POST.get("lid",None)
	if topic:
		request.session["origin_topic"] = topic
	return return_to_content(request,orig,obid,lid,oun)


def return_to_content(request,origin,obj_id=None,link_id=None,target_uname=None):
	"""
	Decides where to redirect user to

	This is merely a redirect view and needs no url pattern (request is passed from other views, e.g. redirect_to_content())
	"""
	if origin == '1' or origin == '20':
		# originated from taza photos page
		if origin == '20':
			# single notification on fresh photos 
			return redirect("photo",list_type='fresh-list')
		else:
			return redirect(reverse_lazy("redirect_to_photo",kwargs={'list_type': 'fresh-list','pk':obj_id}))
	elif origin == '2' or origin == '21':
		# originated from best photos
		if origin == '21':
			# single notification on best photos
			return redirect("photo",list_type='best-list')
		else:
			return redirect(reverse_lazy("redirect_to_photo",kwargs={'list_type': 'best-list','pk':obj_id}))
	elif origin == '3' or origin == '19':
		if origin == '19':
			# single notification on home
			return redirect("home")
		# originated from home
		else:
			request.session["home_hash_id"] = link_id
			request.modified = True
			return redirect("redirect_to_home")
	elif origin == '4':
		# originated from user profile
		request.session["photograph_id"] = obj_id
		request.modified = True
		return redirect("profile", target_uname, 'fotos')
	elif origin == '5':
		# originated from photo detail
		return redirect("photo_detail", obj_id)
	elif origin == '6':
		# originated from 'cull_content' (a defender view)
		if in_defenders(request.user.id):
			return redirect("cull_content")
		else:
			return redirect("photo",list_type='fresh-list')
	elif origin == '7':
		# originated from shared photos page
		if target_uname:
			return redirect("show_shared_photo_metrics", target_uname)
		else:
			return redirect("photo",list_type='fresh-list')
	elif origin == '8':
		# originated from home history
		if target_uname:
			return redirect("user_activity", target_uname)
		else:
			return redirect("home")
	elif origin == '9':
		# originated from a publicreply
		# request.session["link_pk"] = obj_id
		# request.modified = True
		return redirect("publicreply_view",obj_id)
	elif origin == '10':
		# originated from user profile (About page)
		return redirect("user_profile", target_uname)
	elif origin == '11':
		# originated from the comments page
		return redirect("comment_pk", obj_id)
	elif origin == '12':
		# originated from user's own fan list
		return redirect("fan_list", obj_id)
	elif origin == '13':
		# originated from user's own star list
		return redirect("star_list")
	elif origin == '14':
		# originated from user's own unseen activity
		return redirect("unseen_activity", target_uname)
	elif origin == '15':
		# originated from a private group
		request.session["unique_id"] = obj_id#obj_id contains group_uuid, otherwise it won't work
		url = reverse_lazy("private_group_reply")+"#sectionJ"
		return redirect(url)
	elif origin == '16':
		# originated from a public group
		url = reverse_lazy("public_group",kwargs={'slug': obj_id})
		return redirect(url)
	elif origin == '17':
		# originated from private chat list
		return redirect("personal_group_user_listing")
	elif origin == '18':
		# originated from received invites' list
		return redirect("show_personal_group_invite_list",'received')
	elif origin == '22':
		# originated from a topic page
		topic_url = request.session.pop("origin_topic",'')
		url = reverse_lazy("topic_redirect",kwargs={'topic_url':topic_url, 'obj_hash':link_id}) if link_id else reverse_lazy("topic_redirect",kwargs={'topic_url':topic_url})
		return redirect(url)
	elif origin == '23':
		# originated from online kon
		url = reverse_lazy("online_kon")+"#top"
		return redirect(url)
	# elif origin == '24':
	# 	# originated from direct response page
	# 	url = reverse_lazy("retrieve_direct_responses")
	# 	return redirect(url)
	elif origin == '25':
		# originated from 'upvoting' history page
		return redirect('user_vote_history')
	else:
		# take the voter to best photos by default
		return redirect(reverse_lazy("redirect_to_photo",kwargs={'list_type': 'best-list'}))
