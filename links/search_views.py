from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from redis3 import find_nickname, get_search_history, del_search_history, retrieve_history_with_pics, select_nick
from page_controls import ITEMS_PER_PAGE
from forms import SearchNicknameForm
from views import get_page_obj

@csrf_protect
def search_username(request):
	"""
	Renders (and handles) nickname search functionality
	"""
	own_id = request.user.id
	page_num = request.GET.get('page', '1')
	unames = get_search_history(own_id)
	page_obj = get_page_obj(page_num, unames, ITEMS_PER_PAGE)
	search_history = retrieve_history_with_pics(page_obj.object_list)
	if request.method == 'POST':
		#load the page WITH results
		form = SearchNicknameForm(request.POST,searched=True)
		if form.is_valid():
			nickname = form.cleaned_data.get("nickname")
			found_flag,exact_matches,similar = find_nickname(nickname,own_id)
			return render(request,'search/username_search.html',{'form':form,'exact_matches':exact_matches, 'similar':similar, 'found_flag':found_flag, \
				'orig_search':nickname,'search_history':search_history,'page':page_obj})
		else:
			return render(request,'search/username_search.html',{'form':form,'found_flag':None,'search_history':search_history,'page':page_obj})    
	else:
		# GET request. Load the page as it ought to be loaded (without any search results)
		return render(request,'search/username_search.html',{'form':SearchNicknameForm(),'found_flag':None,'search_history':search_history,'page':page_obj})


@csrf_protect
def go_to_username(request,nick,*args,**kwargs):
	if request.method == 'POST':
		dec = request.POST.get("dec")
		select_nick(nick,request.user.id)
		if dec == '1':
			# send to profile photos
			return redirect("profile", nick)
		elif dec == '2':
			# send to home history
			return redirect("user_activity", nick)
		elif dec == '3':
			# send to user profile
			return redirect("user_profile", nick)
		else:
			#send to profile photos
			return redirect("profile", nick)
	else:
		return redirect("missing_page")

@csrf_protect
def go_to_user_photo(request,nick,add_score=None,*args,**kwargs):
	"""
	TODO: May NOT be a good fit for this section - check what this function precisely does
	"""
	if request.method == 'POST':
		if add_score == '1':
			select_nick(nick,request.user.id)
		request.session["photograph_id"] = request.POST.get("pid",'')
		return redirect("profile", nick)
	else:
		return redirect("missing_page")		

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

