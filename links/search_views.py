import time
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from redis3 import find_nickname, get_search_history, del_search_history, bump_up_selected_nick_in_search_history
# from score import SEGMENT_STARTING_USER_ID
from redis4 import retrieve_bulk_credentials
from page_controls import ITEMS_PER_PAGE
from forms import SearchNicknameForm
from tasks import log_user_activity
from views import get_page_obj

@csrf_protect
def search_username(request):
	"""
	Renders (and handles) nickname search functionality
	"""
	time_now = time.time()
	own_id = request.user.id
	page_num = request.GET.get('page', '1')
	unames = get_search_history(own_id)

	page_obj = get_page_obj(page_num, unames, ITEMS_PER_PAGE)
	searched_user_ids = page_obj.object_list
	searched_user_credentials = retrieve_bulk_credentials(user_ids=searched_user_ids, decode_unames=False)

	search_history = [(searched_user_credentials[int(user_id)]['uname'],searched_user_credentials[int(user_id)]['avurl']) \
	for user_id in searched_user_ids]

	if request.method == 'POST':
		#load the page WITH results
		form = SearchNicknameForm(request.POST,searched=True)
		if form.is_valid():
			################### Retention activity logging ###################
			# if own_id > SEGMENT_STARTING_USER_ID:
			# 	act = 'G' if request.mobile_verified else 'G.u'
			# 	activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
			# 	log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
			##################################################################
			nickname = form.cleaned_data.get("nickname")
			found_flag, exact_matches, similar = find_nickname(nickname,own_id)
			return render(request,'search/username_search.html',{'form':form,'exact_matches':exact_matches, 'similar':similar, \
				'found_flag':found_flag, 'orig_search':nickname,'on_fbs':request.META.get('HTTP_X_IORG_FBS',False), \
				'search_history':search_history,'page':page_obj})
		else:
			################### Retention activity logging ###################
			# if own_id > SEGMENT_STARTING_USER_ID:
			# 	act = 'G.i' if request.mobile_verified else 'G.u.i'
			# 	activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
			# 	log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
			##################################################################
			return render(request,'search/username_search.html',{'form':form,'found_flag':None,'search_history':search_history,'page':page_obj,\
				'on_fbs':request.META.get('HTTP_X_IORG_FBS',False)})    
	else:
		################### Retention activity logging ###################
		# if own_id > SEGMENT_STARTING_USER_ID:
		# 	act = 'Z4' if request.mobile_verified else 'Z4.u'
		# 	activity_dict = {'m':'GET','act':act,'t':time_now}# defines what activity just took place
		# 	log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
		##################################################################
		# GET request. Load the page as it ought to be loaded (without any search results)
		return render(request,'search/username_search.html',{'form':SearchNicknameForm(),'found_flag':None,'search_history':search_history,\
			'page':page_obj,'on_fbs':request.META.get('HTTP_X_IORG_FBS',False)})


@csrf_protect
def go_to_searched_username(request,nick,*args,**kwargs):
	"""
	Bumps up the selected username in the search history
	"""
	if request.method == 'POST':
		dec = request.POST.get("dec",'')
		if dec == '1':
			# send to user profile
			bump_up_selected_nick_in_search_history(nick,request.user.id)
			return redirect("user_profile", nick)

		elif dec == '2':
			# send to public history
			bump_up_selected_nick_in_search_history(nick,request.user.id)
			return redirect("display_user_public_feed_history", nick)

		elif dec == '3':
			# send to follower profile
			bump_up_selected_nick_in_search_history(nick,request.user.id)
			return redirect("display_user_follower_feed_history", nick)
		
		else:
			#send to profile photos
			return redirect("user_profile", nick)
	else:
		return redirect("missing_page")


def go_to_user_photo(request,nick,add_score=None,*args,**kwargs):
	"""
	TODO: May NOT be a good fit for this section - check what this function precisely does
	"""
	pass
	# if request.method == 'POST':
	# 	if add_score == '1':
	# 		select_nick(nick,request.user.id)
	# 	request.session["photograph_id"] = request.POST.get("pid",'')
	# 	return redirect("user_profile", nick)
	# else:
	# 	return redirect("missing_page")		


@csrf_protect
def remove_searched_username(request,nick,*args,**kwargs):
	"""
	Removes a nickname from 'search history' rendered in the search template
	"""
	if request.method == 'POST':
		searcher_id = request.POST.get("uid",'')
		del_search_history(searcher_id,nick)
		return redirect("search_username")
	else:
		return redirect("missing_page")

