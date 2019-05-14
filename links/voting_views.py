# coding=utf-8
import time
import ujson as json
from datetime import timedelta
from brake.decorators import ratelimit
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.middleware import csrf
from verified import FEMALES
from tasks import vote_tasks
from models import Link, Photo
from redis4 import retrieve_uname
from redis3 import tutorial_unseen, exact_date
from judgement_views import get_usernames
from views import secs_to_mins, get_indices, beautiful_date
from redirection_views import return_to_content
from redis7 import get_obj_owner, voted_for_single_photo, voted_for_link, can_vote_on_obj, get_voting_details,\
in_defenders, get_votes, check_content_and_voting_ban, is_obj_trending, retrieve_handpicked_photos_count, retrieve_global_voting_records,\
retrieve_voting_records, retrieve_users_voting_relationships#, get_vote_ban_details, check_vote_ban
from page_controls import VOTE_HISTORY_ITEMS_PER_PAGE

def vote_result(request):
	"""
	Helper view for cast_vote

	Redirects to relevant location once vote has been cast
	"""
	which_msg = request.session.pop("vote_result",None)
	if which_msg == '1':
		return render(request, 'verification/unable_to_submit_without_verifying.html', {'vote':True})
	elif which_msg == '2':
		# was trying to vote for self
		orig = request.session.pop("vote_origin",None)
		obid = request.session.pop("vote_obj_id",None)
		lid = request.session.pop("vote_lid",None)
		return render(request, 'voting/penalty_self_vote.html', {'lid':lid,'obid':obid,'orig':orig})
	elif which_msg == '3':
		#trying to double vote (already voted)
		lid = request.session.pop("vote_lid",None)
		obid = request.session.pop("vote_obj_id",None)
		orig = request.session.pop("vote_origin",None)
		return render(request,'voting/already_voted.html',{'lid':lid,'obid':obid,'orig':orig})
	elif which_msg == '4':
		lid = request.session.pop("vote_lid",None)
		orig = request.session.pop("vote_origin",None)
		vote_obj_id = request.session.pop("vote_obj_id",None)
		time_remaining = request.session.pop("time_remaining_to_vote",None)
		return render(request,'voting/vote_cool_down.html',{'time_remaining':time_remaining,'lid':lid,'obid':vote_obj_id,'orig':orig})
	elif which_msg == '5':
		return redirect("home")
	# elif which_msg == '6':
	# 	return redirect("home_loc")
	# elif which_msg == '7':
	# 	return redirect("cric_loc")
	# elif which_msg == '8':
	# 	lang = request.session.pop("vote_lang",None)
	# 	return redirect("home_loc_ur", lang)
	# elif which_msg == '9':
	# 	return redirect("home_loc_best")
	# elif which_msg == '10':
	# 	lang = request.session.pop("vote_lang",None)
	# 	return redirect("home_loc_ur_best", lang)
	elif which_msg == '11':
		return redirect("error")
	elif which_msg == '12':
		# this person banned by a defender, can't vote on text or image posts (the .html file is erroneously named)
		own_id = request.user.id
		banned, time_remaining, ban_details = check_content_and_voting_ban(own_id, with_details=True)
		origin = request.session.pop("vote_origin",None)
		obj_id = request.session.pop("vote_obj_id",None)
		context = {'time_remaining':time_remaining,'origin':origin, 'pk':obj_id,'ban_details':ban_details,'uname':retrieve_uname(own_id,decode=True),\
		'own_profile':True,'defender':None,'is_profile_banned':True}
		return render(request, 'voting/photovote_disallowed.html', context)
	else:
		return redirect("missing_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def cast_vote(request,*args,**kwargs):
	"""
	Casts vote on home posts

	1) Up and down votes allowed. No super votes (e.g. by pink stars)
	2) If link no longer has redis-object, we don't cast vote (redis1 ensures it)
	3) Can't vote on self posts
	4) Can't double-vote
	5) Can't vote if not verified
	"""    
	is_ajax = request.is_ajax()
	if request.method == 'POST':
		if request.user_banned:
			if is_ajax:
				request.session["vote_result"] = '11'
				request.session.modified = True
				return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),content_type='application/json',)
			else:
				return redirect('vote_result')
		data = request.POST.get("vote",None)
		try:
			data = data.split(":")
			value, obj_id, obj_owner_id, is_pht, origin = data[0], data[1], data[2], data[3], data[4]
		except (AttributeError,KeyError,IndexError):
			value, obj_id, obj_owner_id, is_pht, origin = '', None, None, None, None
		if value == '2':
			# show points page
			if is_ajax:
				return HttpResponse(json.dumps({'success':True,'message':reverse("show_voting_summary", kwargs={"pk": obj_id, "orig":origin,'pht':is_pht}),\
					'type':'redirect'}),content_type='application/json',)
			else:
				return redirect("show_voting_summary",pk=obj_id,orig=origin,pht=is_pht)
		elif value not in ('1','0'):
			# disallow
			request.session["vote_result"] = '11'
			request.session.modified = True
			if is_ajax:
				return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),content_type='application/json',)
			else:
				return redirect('vote_result')
		else:
			# it's a vote, carry on
			if (is_pht == '1' and origin in ('1','2','3')) or (is_pht == '0' and origin == '3'):
				# voted on a photo and from a photo origin OR voted on a textual link and from a textual origin
				# 1 is fresh photos, 2 is best photos, 3 is home photos
				# 3 is home links
				pass
			else:
				# disallow all other patterns
				request.session["vote_result"] = '11'
				request.session.modified = True
				if is_ajax:
					return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),content_type='application/json',)
				else:
					return redirect('vote_result')
			own_id = request.user.id
			banned_by_defender, time_of_ban = check_content_and_voting_ban(own_id) #was this person banned by a defender? Banned from all voting (text and images both)
			if banned_by_defender:
				# not allowed to vote - notify
				if origin == '3':
					request.session["target_id"] = 'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id
				request.session["vote_origin"] = origin
				request.session["vote_obj_id"] = obj_id
				request.session["vote_result"] = '12'
				request.session.modified = True
				if is_ajax:
					return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),content_type='application/json',)
				else:
					return redirect('vote_result')
			elif obj_id:
				# cast vote (on text or photo object)
				mob_verified = request.mobile_verified
				if not mob_verified:
					request.session["vote_result"] = '1'
					request.session.modified = True
					if is_ajax:
						return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),\
							content_type='application/json',)
					else:
						return redirect('vote_result')
				elif mob_verified:
					target_user_id = str(get_obj_owner(obj_id=obj_id, obj_type='img' if is_pht == '1' else 'tx'))
					if target_user_id:
						# voting is not yet closed on the object (i.e. it's still in home, fresh or top photos queue(s) and has a redis object)
						if str(own_id) == target_user_id:
							#voting for own self
							request.session["vote_origin"] = origin
							request.session["vote_obj_id"] = obj_id
							request.session["vote_lid"] = 'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id
							request.session["vote_result"] = '2'
							request.session.modified = True
							if is_ajax:
								return HttpResponse(json.dumps({'success':False,'message':'Apni post pe vote nahi karein','type':'text',\
									'offence':'2'}),content_type='application/json',)
							else:
								return redirect('vote_result')
						else:
							#legit vote - proceed
							already_voted = voted_for_single_photo(obj_id, own_id) if is_pht == '1' else voted_for_link(obj_id,own_id)
							if already_voted is False:
								disallowed = False
								revert_old = None
							else:
								# has already voted - thus, reverting the vote
								disallowed = True
								revert_old = False
								if (value == '0' and already_voted > 0.0) or (value == '1' and already_voted <= 0.0):
									disallowed = False
									revert_old = True #revert user's vote - send this flag to redis
							if disallowed:
								#trying to double vote (already voted)
								request.session["vote_origin"] = origin
								request.session["vote_obj_id"] = obj_id
								request.session["vote_lid"] = 'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id
								request.session["vote_result"] = '3'
								request.session.modified = True
								if is_ajax:
									return HttpResponse(json.dumps({'success':False,'message':'Ap aik hi vote 2 bar nahi dal saktey','type':'text',\
										'offence':'3'}),content_type='application/json',)
								else:
									return redirect('vote_result')
							elif not disallowed:
								#process the vote
								if revert_old:
									# should always be able to revert old deeds, even if rate limited!
									time_remaining, can_vote = 0, True
								else:
									# this is a fresh vote
									# check if the user banned from voting completely?
									time_remaining, can_vote = can_vote_on_obj(own_id, is_pht)
								if can_vote:
									own_name = request.user.username
									vote_tasks.delay(own_id, target_user_id,obj_id,value,(True if own_name in FEMALES else False),own_name, revert_old,is_pht,time.time())
									message = 'old' if revert_old else 'new'#used to do some validation checks on the JS front-end, nothing more
									if is_ajax:
										# JS voting
										return HttpResponse(json.dumps({'success':True,'message':message,'type':'text'}),content_type='application/json',)
									else:
										# non JS voting
										return return_to_content(request,origin,obj_id,'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id)
								elif time_remaining:
									request.session["vote_origin"] = origin
									request.session["vote_obj_id"] = obj_id
									request.session["vote_lid"] = 'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id
									request.session["time_remaining_to_vote"] = time_remaining
									request.session["vote_result"] = '4'
									request.session.modified = True
									if is_ajax:
										return HttpResponse(json.dumps({'success':False,'message':'Please wait {}'.format(secs_to_mins(time_remaining)),\
											'type':'text','offence':'4'}),content_type='application/json',)
									else:
										return redirect('vote_result')
								else:
									request.session["vote_origin"] = origin
									request.session["vote_obj_id"] = obj_id
									request.session["vote_lid"] = 'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id
									request.session["vote_result"] = '5'
									request.session.modified = True
									if is_ajax:
										return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),\
											content_type='application/json',)
									else:
										return redirect('vote_result')
							else:
								request.session["vote_result"] = '5'
								request.session.modified = True
								if is_ajax:
									return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),\
										content_type='application/json',)
								else:
									return return_to_content(request,origin,obj_id,'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id)
					else:
						# voting is closed on the object (it's no longer in the home, fresh or top photos queue(s))
						# redirect this user to home
						request.session["vote_result"] = '5'
						request.session.modified = True
						if is_ajax:
							return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),\
								content_type='application/json',)
						else:
							return return_to_content(request,origin,obj_id,'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id)
				else:
					request.session["vote_result"] = '1'
					request.session.modified = True
					if is_ajax:
						return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),\
							content_type='application/json',)
					else:
						return redirect('vote_result')
			else:
				request.session["vote_result"] = '5'
				request.session.modified = True
				if is_ajax:
					return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),\
						content_type='application/json',)
				else:
					return return_to_content(request,origin,obj_id,'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id)
	else:
		request.session["vote_result"] = '5'
		request.session.modified = True
		if is_ajax:
			return HttpResponse(json.dumps({'success':False,'message':reverse('vote_result'),'type':'redirect'}),\
				content_type='application/json',)
		else:
			return redirect('vote_result')


def show_voting_summary(request,pk,orig,pht):
	"""
	Displays for each home link: net_votes, num of upvotes, num of downvotes, and num of votes by pinkstars

	If link data expired, merely shows its total score
	"""
	# was_limited = getattr(request, 'limits', False)
	# if was_limited:
	#     return redirect("missing_page")
	# else:
	if pht is None:
		return redirect("missing_page")
	elif pht == '1':
		# it's a photo
		try:
			obj = Photo.objects.get(id=pk)
			purl = obj.image_file.url
			oun = obj.owner.username
			ooid = obj.owner_id
		except Photo.DoesNotExist:
			return redirect("missing_page")
		trending_status, time_of_selection = is_obj_trending(prefix='img:', obj_id=pk, with_trending_time=True)
		lid = None
		tp = "img"
		if orig == '3':
			lid = tp+":"+pk
			request.session["home_hash_id"] = lid
			request.session.modified = True
	elif pht == '0':
		# it's a link
		try:
			obj = Link.objects.get(id=pk)
			oun = obj.submitter.username
			ooid = obj.submitter_id
		except Link.DoesNotExist:
			return redirect("missing_page")
		# trending_status, time_of_selection = is_obj_trending(prefix='img:', obj_id=pk, with_trending_time=True)# not needed yet
		trending_status, time_of_selection = False, None
		purl = None #not applicable, it's not a photo object
		lid = None
		tp = "tx"
		if orig == '3':
			lid = tp+":"+pk
			request.session["home_hash_id"] = lid
			request.session.modified = True
	else:
		# not a link neither a photo
		return redirect("home")
	own_id = request.user.id
	defender, voter_id_names_status_and_votes = False, []
	is_pinkstar = True if oun in FEMALES else False
	exists, net_votes, upvotes, downvotes, pink_votes = get_voting_details(pk,pht)
	show_banning_prompt = False
	if exists:
		# dont show anything if content posted by defender herself!
		net_votes = net_votes if net_votes else 0
		upvotes = upvotes if upvotes else 0
		downvotes = downvotes if downvotes else 0
		pink_votes = pink_votes if pink_votes else 0
		if own_id != ooid:
			# not own content, so can show voter details and banning options (otherwise strictly prohibited)
			defender = in_defenders(own_id)
			voters_and_votes = get_votes(pk,tp)
			voter_id_names_status_and_votes = get_usernames(voters_and_votes, ban_status=True) if defender else []
			show_banning_prompt = True if request.session.pop('show_banning_prompt',None) == '1' else False
	return render(request,"voting/voting_summary.html",{'obj':obj,'exists':exists,'nv':net_votes,'uv':upvotes,'dv':downvotes,'pv':pink_votes,\
		'obj_id':pk,'pht':pht,'is_pinkstar':is_pinkstar,'defender':defender,'voter_id_names_status_and_votes':voter_id_names_status_and_votes,\
		'tp':tp,'first_time_voting_judger':tutorial_unseen(user_id=own_id, which_tut='12', renew_lease=True) if exists else False, 'ooid':ooid,\
		'oun':oun,'purl':purl,'lid':lid, 'show_banning_prompt':show_banning_prompt,'orig':orig,'own_id':str(own_id),'is_trending':trending_status,\
		'time_of_trending':time_of_selection})


def show_handpicked_count(request):
	"""
	Renders a page where outstanding number of handpicked photos are displayed

	Helps super defenders 'refill' the handpicked queue in a coordinated way
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		count = retrieve_handpicked_photos_count()
		hours_remaining = 0 if count == 0 else ((count*5.0)/60)
		hours = int(hours_remaining//1) if hours_remaining else 0
		minutes = int((hours_remaining%1)*60) if hours_remaining else 0
		return render(request,"voting/handpicked_count.html",{'count':count,'hours':hours,'minutes':minutes})
	else:
		raise Http404("Refreshing too fast!")


def export_voting_records(request):
	"""
	Exports all available voting records into a CSV file for analysis
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		data_to_write_to_csv = retrieve_global_voting_records()# list of lists (where each list is a list of dictionaries)
		if data_to_write_to_csv:
			import csv
			filename = 'voting_data.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				columns = ["Voting time (human)","voter ID","target user ID","vote value","target obj type","target obj ID"]
				wtr.writerow(columns)
				for vote_data, voting_time in data_to_write_to_csv:
					# vote_data contains voter_id+":"+str(target_user_id)+":"+vote_value+":"+target_obj_tp+":"+target_obj_id
					data_list = vote_data.split(":")
					voter_id, target_user_id, vote_value, target_obj_tp, target_obj_id = data_list[0],data_list[1],data_list[2],\
					data_list[3], data_list[4]
					to_write = [exact_date(voting_time),voter_id,target_user_id,vote_value,target_obj_tp,target_obj_id]
					wtr.writerows([to_write])
	raise Http404("Completed ;)")


def user_vote_history(request,vote):
	"""
	Renders the voting history of the user

	Shows all upvotes or downvotes (in separate pages) cast within last 1 month
	"""
	if vote in ('upvote','downvote'):
		own_id, page_num, upvote_listing = request.user.id, request.GET.get('page', '1'), True if vote == 'upvote' else False
		start_index, end_index = get_indices(page_num, VOTE_HISTORY_ITEMS_PER_PAGE)
		voting_data, list_total_size = retrieve_voting_records(voter_id=own_id, start_idx=start_index, end_idx=end_index, \
			upvotes=upvote_listing, with_total_votes=True)
		num_pages = list_total_size/VOTE_HISTORY_ITEMS_PER_PAGE
		max_pages = num_pages if list_total_size % VOTE_HISTORY_ITEMS_PER_PAGE == 0 else (num_pages+1)
		page_num = int(page_num)
		final_data = []
		for data, vote_time in voting_data:
			# data contains: voter_id+":"+str(target_user_id)+":"+vote_value+":"+target_obj_tp+":"+target_obj_id
			data_list = data.split(":")
			human_vote_time = beautiful_date(vote_time)#exact_date(vote_time)
			final_data.append((data_list[1], data_list[2], data_list[3], data_list[4], human_vote_time))
		return render(request,"voting/voting_history.html",{'data':final_data,'slug':retrieve_uname(own_id,decode=True), 'own_profile':True,\
			'page':{'number':page_num,'has_previous':True if page_num>1 else False,'has_next':True if page_num<max_pages else False,\
			'previous_page_number':page_num-1,'next_page_number':page_num+1},'history_type':vote})
	else:
		raise Http404("No other type of voting exists")


def user_sybil_history(request, user_id):
	"""
	Renders suspected sybils and haters in an HTML template for super defenders
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		return render(request,"voting/voting_sybils.html",{'sybil_data':retrieve_users_voting_relationships(user_id),\
			'tgt_uname':retrieve_uname(user_id,decode=True)})
	else:
		raise Http404("Not athorized to view sybils")

