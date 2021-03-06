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
	return return_to_content(request=request,origin=orig,obj_id=obid,link_id=lid,target_uname=oun)


def return_to_content(request,origin,obj_id=None,link_id=None,target_uname=None,source_origin=None):
	"""
	Decides where to redirect user to

	This is merely a redirect view and needs no url pattern (request is passed from other views, e.g. redirect_to_content())
	"""
	if origin in ('1','20'):
		# originated from fresh photos page
		if origin == '20':
			# single notification on fresh photos 
			return redirect("photo",list_type='fresh-list')
		else:
			return redirect(reverse_lazy("redirect_to_photo",kwargs={'list_type': 'fresh-list','pk':obj_id}))
	elif origin in ('2','21'):
		# originated from best photos
		if origin == '21':
			# single notification on best photos
			return redirect("photo",list_type='best-list')
		else:
			return redirect(reverse_lazy("redirect_to_photo",kwargs={'list_type': 'best-list','pk':obj_id}))
	elif origin in ('3','19'):
		if origin == '19':
			# single notification on 'fresh_text'
			return redirect("fresh_text")
		# originated from home
		else:
			request.session["home_hash_id"] = link_id
			request.modified = True
			return redirect("redirect_to_home")
	elif origin == '4':
		# originated from user profile
		request.session["photograph_id"] = obj_id
		request.modified = True
		return redirect("profile_photos_redirect",target_uname,'fotos')
		# return redirect("profile", target_uname, 'fotos')
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
		# originated from fresh photos page
		return redirect("photo",list_type='fresh-list')
	elif origin == '8':
		# originated from home history
		if target_uname:
			return redirect("user_activity", target_uname)
		else:
			return redirect("fresh_text")
	elif origin == '9':
		# originated from a publicreply
		if source_origin:
			url = reverse_lazy("publicreply_view",kwargs={'parent_id':obj_id, 'origin':source_origin})+"#reply"	
		else:
			url = reverse_lazy("publicreply_view",kwargs={'parent_id':obj_id})+"#reply"
		return redirect(url)
	elif origin == '10':
		# originated from user profile (About page)
		return redirect("user_profile", target_uname)
	elif origin == '11':
		# originated from the comments page
		if source_origin:
			url = reverse_lazy("comment",kwargs={'pk':obj_id, 'origin':source_origin})+"#reply"	
		else:
			url = reverse_lazy("comment",kwargs={'pk':obj_id})+"#reply"
		return redirect(url)
	elif origin == '12' or origin == '13':
		# originated from 'best home'
		if origin == '12':
			# best home
			request.session["home_hash_id"] = link_id
			request.modified = True
			return redirect("best_home_redirect")
		else:
			# best home (from "direct-reply" notification)
			return redirect("best_home_page")
	elif origin == '14':
		# originated from a user's trending posts list
		return redirect("display_trending_history",target_uname=target_uname)
	elif origin == '15':
		# originated from a private group
		request.session["unique_id"] = obj_id#obj_id contains group_uuid, otherwise it won't work
		url = reverse_lazy("private_group_reply")+"#sectionJ"
		return redirect(url)
	elif origin == '16':
		# originated from a public group
		url = reverse_lazy("public_group",kwargs={'slug': obj_id})#obj_id contains group_uuid, otherwise it won't work
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
	elif origin == '24':
		# originated from direct response page
		return redirect(reverse_lazy("retrieve_direct_responses"))
	elif origin == '25':
		# originated from 'upvoting' history page
		return redirect('user_vote_history')
	elif origin in ('26','38'):
		# originated from single notif on 'for_me'
		if origin == '38':
			return redirect("custom_feed_redirect")
		# originated from 'my home'
		else:
			if link_id:
				return redirect(reverse_lazy("custom_feed_redirect",kwargs={'obj_hash':link_id}))
			else:
				return redirect("custom_feed_redirect")
	elif origin == '27':
		# originated from 'followers list'
		var = request.session.pop('page_num',None)		
		if var:
			url = reverse_lazy("show_follower_list",kwargs={})+"?page="+var
		else:
			url = reverse_lazy("show_follower_list",kwargs={})
		return redirect(url)
	elif origin == '28':
		# originated from 'followers list'
		var = request.session.pop('page_num',None)		
		if var:
			url = reverse_lazy("show_following_list",kwargs={})+"?page="+str(var)
		else:
			url = reverse_lazy("show_following_list",kwargs={})
		return redirect(url)
	elif origin == '29':
		# originated from 'publicly shared item history'
		var = request.session.pop('page_num',None)	
		if var:
			url = reverse_lazy("display_user_public_feed_history",kwargs={'target_uname':target_uname})+"?page="+str(var)
		else:
			url = reverse_lazy("display_user_public_feed_history",kwargs={'target_uname':target_uname})
		# return redirect("display_user_public_feed_history", target_uname)
		return redirect(url)
	elif origin == '30':
		# originated from 'publicly shared follower history'
		var = request.session.pop('page_num',None)	
		if var:
			url = reverse_lazy("display_user_follower_feed_history",kwargs={'target_uname':target_uname})+"?page="+str(var)
		else:
			url = reverse_lazy("display_user_follower_feed_history",kwargs={'target_uname':target_uname})
		# return redirect("display_user_public_feed_history", target_uname)
		return redirect(url)
	elif origin == '31':
		# originated from 'privately shared follower history'
		var = request.session.pop('page_num',None)	
		if var:
			url = reverse_lazy("display_user_private_feed_history",kwargs={'target_uname':target_uname})+"?page="+str(var)
		else:
			url = reverse_lazy("display_user_private_feed_history",kwargs={'target_uname':target_uname})
		# return redirect("display_user_public_feed_history", target_uname)
		return redirect(url)
	elif origin == '32':
		# originated from 'new followers list'
		url = reverse_lazy("show_new_followers",kwargs={})
		return redirect(url)
	elif origin == '33':
		# originated from 'upvoting' history page (admin view)
		return redirect('vote_history_admin_view', user_id=obj_id)
	elif origin == '34':
		# originated from content detail (specifically - an image, i.e. obj_type is 'g')
		return redirect("content_detail_view", pk=obj_id, obj_type='g')
	elif origin == '35':
		# originated from 'reply' history page
		return redirect('retrieve_direct_response_activity')
	elif origin == '36':
		# originated from 'popular mehfil' list 
		# DEPRECATED
		return redirect('get_ranked_groups')
	elif origin == '37':
		# originated from 'Red Stars' list 
		return redirect('top_photo')
	############
	# origin '38' is also used up
	############	
	else:
		# when no origin, redirect to 'for_me'
		if link_id:
			return redirect(reverse_lazy("custom_feed_redirect",kwargs={'obj_hash':link_id}))
		else:
			return redirect("custom_feed_redirect")


def main_navbar(request):
	"""
	Handles navigation of the bottom menu
	"""
	decision = request.GET.get('dec', None)
	if decision == '1':
		# redirect to 'for me'
		return redirect("for_me")
	elif decision == '2a':
		# redirect to inbox replies
		return redirect("retrieve_direct_responses")
	elif decision == '2b':
		# redirect to inbox activity
		return redirect("retrieve_direct_response_activity")
	elif decision == '3':
		# redirect to content sharing page
		return redirect("share_content")
	elif decision == '4':
		# redirect to best photos
		return redirect("photo",list_type='best-list')
	elif decision == '5':
		# redirect to best text
		return redirect("best_home_page")
	elif decision == '6':
		# redirect to sign up
		return redirect("unauth_home_new")
	elif decision == '7':
		# redirect to login
		return redirect("login")
	elif decision == '8':
		# redirect to user's profile
		username = request.user.username
		if username:
			return redirect("user_profile",request.user.username)
		else:
			# in case the user was logged out in the special circumstance of having changed their password
			return redirect("login")
	elif decision == '9':
		# redirect to top stars
		return redirect("top_photo")
	elif decision == '10':
		# redirect to privacy_policy
		return redirect("privacy_policy")
	elif decision == '11':
		# redirect to mehfils list
		return redirect("group_page")
	elif decision == '12':
		# redirect to online
		return redirect("online_kon")
	elif decision == '13':
		# redirect to topics
		return redirect("topic_listing")
	elif decision == '14':
		# redirect to more
		return redirect("more_options")
	elif decision == '15a':
		# redirect to 1on1 list
		return redirect("personal_group_user_listing")
	elif decision == '15b':
		# redirect to 1on1 invites received
		return redirect("show_personal_group_invite_list",'received')
	elif decision == '16':
		# redirect to help
		return redirect("help")
	elif decision == '17':
		# redirect to about
		return redirect("about")
	elif decision == '18':
		# redirect to logout
		return redirect("bahirniklo")
	elif decision == '19':
		# redirect to user_verification
		return redirect("verify_user_mobile_unpaid")
	elif decision == '20':
		# redirect to search
		return redirect("search_username")
	else:
		# default redirect
		return redirect("home")