# coding=utf-8
import json as json_backup
import time
import ujson as json
from brake.decorators import ratelimit
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.middleware import csrf
from models import Link, Photo
from colors import COLOR_GRADIENTS
from judgement_views import get_usernames
from redis3 import tutorial_unseen, exact_date
from redirection_views import return_to_content
from page_controls import VOTE_HISTORY_ITEMS_PER_PAGE
from utilities import convert_to_epoch, beautiful_date
from views import secs_to_mins, get_indices, retrieve_user_env
from tasks import vote_tasks, cache_voting_history, log_user_activity
from redis4 import retrieve_uname, retrieve_credentials#, retrieve_mehfil_replier_rate
from redis7 import get_obj_owner, voted_for_single_photo, voted_for_link, can_vote_on_obj, get_voting_details,retrieve_voting_records,\
in_defenders, get_votes, check_content_and_voting_ban, is_obj_trending, retrieve_handpicked_photos_count, retrieve_global_voting_records,\
retrieve_users_voting_relationships, retrieve_detailed_voting_data, retrieve_old_detailed_voting_data, log_section_wise_voting_liquidity,\
is_image_star
from score import SEGMENT_STARTING_USER_ID


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
		topic = request.session.pop("vote_topic",None)
		lid = request.session.pop("vote_lid",None)
		orig = request.session.pop("vote_origin",None)
		vote_obj_id = request.session.pop("vote_obj_id",None)
		time_remaining = request.session.pop("time_remaining_to_vote",None)
		return render(request,'voting/vote_cool_down.html',{'time_remaining':time_remaining,'lid':lid,'obid':vote_obj_id,'orig':orig,'topic':topic})
	elif which_msg == '5':
		return redirect('home')
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

	1) Only 'like' and reversing the like 'unlike' is allowed
	2) If link no longer has redis-object, we don't cast vote (redis7 ensures it)
	3) Can't vote on self posts
	4) Can't double-vote
	5) Can't vote if not verified
	6) Can only 'unlike' if previously 'liked'
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
			obj_id, obj_owner_id, is_pht, origin = data[0], data[1], data[2], data[3]
		except (AttributeError,KeyError,IndexError):
			obj_id, obj_owner_id, is_pht, origin = None, None, None, None
		# it's a vote, carry on
		if (is_pht == '1' and origin in ('1','2','3','12','22','26')) or (is_pht == '0' and origin in ('3','12','22','26')):
			# voted on a photo and from a photo origin OR voted on a textual link and from a textual origin
			# 1 is fresh photos, 2 is best photos, 3 is home photos, 12 is trending home, 22 is a certain topic
			# 3 is also home links
			topic = request.POST.get("tp",None)# in case a 'topic' parameter was passed also
			request.session["origin_topic"] = topic
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
			if origin in ('3','12'):
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
			time_now = time.time()
			mob_verified = request.mobile_verified
			if not mob_verified:
				###################### Retention activity logging ######################
				if own_id > SEGMENT_STARTING_USER_ID:
					if is_pht == '1':
						photo = Link.objects.only('image_file','description').get(id=obj_id)
						activity_dict = {'m':'POST','act':'V.u','t':time_now,'ot':'img','pc':photo.description,'pi':photo.image_file.url}# defines what activity just took place
						print activity_dict
					else:
						description = Link.objects.only('description').get(id=obj_id).description
						activity_dict = {'m':'POST','act':'V.u','t':time_now,'ot':'tx','pc':description}# defines what activity just took place
					log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
				########################################################################
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

						#process the vote
						if already_voted is False:
							# this is a fresh vote
							# check if the user banned from voting completely?
							time_remaining, can_vote = can_vote_on_obj(own_id, is_pht)
						else:
							# should always be able to revert old deeds, even if rate limited!
							time_remaining, can_vote = 0, True
						
						if can_vote:
							###################### Retention activity logging ######################
							if own_id > SEGMENT_STARTING_USER_ID:
								if is_pht == '1':
									photo = Link.objects.only('image_file','description').get(id=obj_id)
									activity_dict = {'m':'POST','act':'V','t':time_now,'ot':'img','pc':photo.description,'pi':photo.image_file.url}# defines what activity just took place
								else:
									description = Link.objects.only('description').get(id=obj_id).description
									activity_dict = {'m':'POST','act':'V','t':time_now,'ot':'tx','pc':description}# defines what activity just took place
								log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
							########################################################################
							# votes cast in fresh lists are considered 'editorial' votes - handpickers build their reputation by voting here
							# votes cast in best lists are considered 'audience' votes - voters vote on curated stuff and validate curators' choice
							if origin == '1':
								# vote_type = 'fresh images'
								editorial_vote = True# this is an 'editorial vote'
							elif origin == '2':
								# vote_type = 'trending images'
								editorial_vote = False# this is an 'audience vote'
							elif origin == '3':
								# vote_type = 'fresh text'
								editorial_vote = True# this is an 'editorial vote'
							elif origin == '22':
								# vote_type = 'topic'
								editorial_vote = True# this is an 'editorial vote'
							elif origin == '12':
								# vote_type = 'trending text'
								editorial_vote = False# this is an 'audience vote'	
							elif origin == '26':
								# vote_type = 'custom_feed'
								editorial_vote = False# this is an 'audience vote'
							#####################################################
							# Logging voting liquidity in 'fresh' and 'trending'#
							#####################################################
							# if is_pht == '1':
							# 	if origin == '1':
							# 		vote_type = 'fresh'
							# 	elif origin == '2':
							# 		vote_type = 'trending'
							# 	elif origin == '3':
							# 		vote_type = 'home'
							# 	elif origin == '22':
							# 		vote_type = 'topic'
							# 	log_section_wise_voting_liquidity(from_=vote_type, vote_value=value, voter_id=own_id)
							#####################################################
							#####################################################
							#####################################################
							vote_tasks.delay(own_id=own_id, target_user_id=target_user_id,target_obj_id=obj_id,revert_prev=already_voted,\
								is_pht=is_pht, time_of_vote=time_now, is_editorial_vote=editorial_vote)
							message = 'old' if already_voted else 'new'#used to do some validation checks on the JS front-end, nothing more
							if is_ajax:
								# JS voting
								return HttpResponse(json.dumps({'success':True,'message':message,'type':'text'}),\
									content_type='application/json',)
							else:
								# non JS voting
								return return_to_content(request,origin,obj_id,'img:'+obj_id if is_pht=='1' else 'tx:'+obj_id)
						elif time_remaining:
							###################### Retention activity logging ######################
							if own_id > SEGMENT_STARTING_USER_ID:
								if is_pht == '1':
									photo = Link.objects.only('image_file','description').get(id=obj_id)
									activity_dict = {'m':'POST','act':'V.i','t':time_now,'ot':'img','pc':photo.description,'pi':photo.image_file.url}# defines what activity just took place
								else:
									description = Link.objects.only('description').get(id=obj_id).description
									activity_dict = {'m':'POST','act':'V.i','t':time_now,'ot':'tx','pc':description}# defines what activity just took place
								log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
							########################################################################
							request.session["vote_topic"] = request.POST.get("tp",None)
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
					# voting is closed on the object (it's no longer in the home, in topics, in fresh or trending photo queue(s))
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
	own_id = request.user.id
	if pht is None:
		raise Http404("No obj type provided")
	elif pht == '1':
		# it's a photo (saved in the Link() model)
		try:
			# obj = Photo.objects.get(id=pk)
			obj = Link.objects.get(id=pk)
		except Link.DoesNotExist:
			raise Http404("No such photo obj exists in the Link() model")
		try:
			purl = obj.image_file.url
		except ValueError:
			purl = ''
		ooid = obj.submitter_id
		oun = retrieve_uname(ooid,decode=True)
		if ooid != request.user.id:
			is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
			if not is_super_defender:
				raise Http404("Not authorized to view this")
		trending_status, time_of_selection = is_obj_trending(prefix='img:', obj_id=pk, with_trending_time=True)
		lid = None
		tp = "img"
		if orig in ('3','22'):
			lid = tp+":"+pk
			request.session["home_hash_id"] = lid
			request.session.modified = True
	elif pht == '0':
		# it's a link
		try:
			obj = Link.objects.get(id=pk)
		except Link.DoesNotExist:
			raise Http404("No such text obj exists in the Link() model")
		ooid = obj.submitter_id
		oun = retrieve_uname(ooid,decode=True)
		if ooid != own_id:
			is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
			if not is_super_defender:
				raise Http404("Not authorized to view this")
		# trending_status, time_of_selection = is_obj_trending(prefix='img:', obj_id=pk, with_trending_time=True)# not needed yet
		trending_status, time_of_selection = False, None
		purl = None #not applicable, it's not a photo object
		lid = None
		tp = "tx"
		if orig in ('3','22'):
			lid = tp+":"+pk
			request.session["home_hash_id"] = lid
			request.session.modified = True
	else:
		# not a link neither a photo
		return redirect('home')
	topic = request.session.pop("origin_topic",'')
	defender, voter_id_names_status_and_votes = False, []
	is_star = is_image_star(user_id=ooid)
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
		'obj_id':pk,'pht':pht,'is_star':is_star,'defender':defender,'voter_id_names_status_and_votes':voter_id_names_status_and_votes,\
		'tp':tp,'first_time_voting_judger':tutorial_unseen(user_id=own_id, which_tut='12', renew_lease=True) if exists else False, 'ooid':ooid,\
		'oun':oun,'purl':purl,'lid':lid, 'show_banning_prompt':show_banning_prompt,'orig':orig,'own_id':str(own_id),'is_trending':trending_status,\
		'time_of_trending':time_of_selection,'origin_topic':topic})


def show_handpicked_count(request):
	"""
	Renders a page where outstanding number of handpicked photos are displayed

	Helps super defenders 'refill' the handpicked queue in a coordinated way
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		count = retrieve_handpicked_photos_count()
		hours_remaining = 0 if count == 0 else ((count*3.5)/60)
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
		# data_to_write_to_csv = retrieve_global_voting_records()# list of lists (where each list is a list of dictionaries)
		# if data_to_write_to_csv:
		# 	import csv
		# 	filename = 'voting_data.csv'
		# 	with open(filename,'wb') as f:
		# 		wtr = csv.writer(f)
		# 		columns = ["Voting time (human)","voter ID","target user ID","vote value","target obj type","target obj ID"]
		# 		wtr.writerow(columns)
		# 		for vote_data, voting_time in data_to_write_to_csv:
		# 			# vote_data contains voter_id+":"+str(target_user_id)+":"+vote_value+":"+target_obj_tp+":"+target_obj_id
		# 			data_list = vote_data.split(":")
		# 			voter_id, target_user_id, vote_value, target_obj_tp, target_obj_id = data_list[0],data_list[1],data_list[2],\
		# 			data_list[3], data_list[4]
		# 			to_write = [exact_date(voting_time),voter_id,target_user_id,vote_value,target_obj_tp,target_obj_id]
		# 			wtr.writerows([to_write])
		#####################################################
		data_to_write_to_csv = []#retrieve_mehfil_replier_rate()
		if data_to_write_to_csv:
			import csv

			filename = 'mehfil_replies.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				columns = ["Reply time (epoch)","Target ID","Replier ID","Mehfil type","Text"]
				wtr.writerow(columns)
				for reply_data, replier_id in data_to_write_to_csv:

					data_1 = reply_data.partition(":")
					reply_time = data_1[0]
					data_2 = data_1[-1].rpartition(":")
					mehfil_type = data_2[-1]
					data_3 = data_2[0].rpartition(":")
					target_id = data_3[-1]
					text = data_3[0]
						
					to_write = [reply_time,target_id,replier_id,mehfil_type,text]

					wtr.writerows([to_write])
	raise Http404("Completed ;)")


def export_voting_reputation_records(request):
	"""
	Exports all voting reputation-related records into a CSV file for analysis
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		# data_to_write_to_csv = None
		# if data_to_write_to_csv:
		# 	import csv
		# 	filename = 'voting_and_content_reputation_data.csv'
		# 	with open(filename,'wb') as f:
		# 		wtr = csv.writer(f)
		# 		columns = []
				
		# 		wtr.writerow(columns)
		# 		for data in data_to_write_to_csv:
		# 			to_write = [data['vid'], data['wad'], 'upvote', data['vt'], data['ss'], data.get('num_sybs','-'),\
		# 			data['toid'], data['tuid'], data['tv'], data.get('hp','-'), data.get('tos','-')]
		# 			wtr.writerows([to_write])
		#################################################
		from redis4 import retrieve_home_post_logs
		data_to_write_to_csv = retrieve_home_post_logs()
		if data_to_write_to_csv:
			import csv
			filename = 'home_post_logs.csv'
			with open(filename,'wb') as f:
				wtr = csv.writer(f)
				# columns = ["posting time (human)","posting time (epoch)","uploader_id","username","is_fbs","is_opera_mini","img_width","img_height"]
				columns = ["posting time (human)","trending time (human)","posting time (epoch)","trending time (epoch)","user_id","username","is_fbs",\
				"is_urdu","upvotes","text_length","ascii_len","eng_len","urdu_len","digit_len","text"]
				wtr.writerow(columns)
				for json_data, submitter_id in data_to_write_to_csv:
					try:
						data = json.loads(json_data)
					except:
						data = json_backup.loads(json_data)
					
					posting_epoch_time = data['posting_time']
					posting_human_time = exact_date(float(posting_epoch_time))
					trending_epoch_time = data['trending_time']
					trending_human_time = exact_date(float(trending_epoch_time))
					
					to_write = [posting_human_time,trending_human_time,posting_epoch_time,trending_epoch_time,submitter_id,\
					data['username'].encode('utf-8'),data.get('on_fbs',''),data['is_urdu'], data['uv'],data['text_length'],\
					data['ascii_len'],data['readable_eng_len'],data['readable_urdu_len'],data['digit_len'],data['text'].encode('utf-8')]

					wtr.writerows([to_write])
	raise Http404("Completed ;)")


def vote_history_admin_view(request,user_id):
	"""
	Displays a user's voting history to super defenders

	Could be helpful in tracking voting activities of sybils
	"""
	defender_id = request.user.id 
	is_defender, is_super_defender = in_defenders(defender_id, return_super_status=True)
 	if is_super_defender:
 		own_id = user_id
		page_num, final_data = request.GET.get('page', '1'), []
		json_data = retrieve_detailed_voting_data(page_num=page_num, user_id=own_id)
		if json_data:
			try:
				final_data_list = json.loads(json_data)
			except:
				final_data_list = json_backup.loads(json_data)
			final_enriched_data, max_pages, all_submitters = final_data_list[0], final_data_list[1], final_data_list[2]
		else:
			start_index, end_index = get_indices(page_num, VOTE_HISTORY_ITEMS_PER_PAGE)
			voting_data, list_total_size = retrieve_voting_records(voter_id=own_id, start_idx=start_index, end_idx=end_index, \
				upvotes=True, with_total_votes=True)
			num_pages = list_total_size/VOTE_HISTORY_ITEMS_PER_PAGE
			max_pages = num_pages if list_total_size % VOTE_HISTORY_ITEMS_PER_PAGE == 0 else (num_pages+1)
			text_ids, img_ids = [], []
			for data, vote_time in voting_data:
				# 'data' contains: voter_id+":"+str(target_user_id)+":"+vote_value+":"+target_obj_tp+":"+target_obj_id
				data_list = data.split(":")
				obj_type, obj_id = data_list[3], data_list[4]
				human_vote_time = beautiful_date(vote_time)#exact_date(vote_time)
				text_ids.append(obj_id) if obj_type == 'tx' else img_ids.append(obj_id)
				obj = {'tp':obj_type,'obid':obj_id,'ooid':data_list[1],'vid':own_id,'vt':human_vote_time}
				final_data.append(obj)
			##############################################################
			final_text_objs = {}
			text_objs = Link.objects.only('id','description','submitted_on','net_votes','url','cagtegory','reply_count','submitter','expire_at').filter(id__in=text_ids,is_visible=False).\
			values('id','description','submitted_on','net_votes','url','cagtegory','reply_count','submitter_id','expire_at') if text_ids else []
			for text_obj in text_objs:
				final_text_objs[str(text_obj['id'])] = text_obj
			final_img_objs = {}
			# img_objs = Photo.objects.only('id','image_file','upload_time','comment_count','vote_score','device','caption','owner').filter(id__in=img_ids).\
			# values('id','image_file','upload_time','comment_count','vote_score','device','caption','owner') if img_ids else []
			img_objs = Link.objects.only('id','image_file','submitted_on','reply_count','net_votes','trending_status','description','submitter','expire_at').\
			filter(id__in=img_ids,is_visible=False).values('id','image_file','submitted_on','reply_count','net_votes','trending_status','description','submitter_id','expire_at') if img_ids else []

			for img_obj in img_objs:
				final_img_objs[str(img_obj['id'])] = img_obj
			##############################################################
			all_submitters, final_enriched_data = set(), []
			# enriching data with more fields
			for final_obj in final_data:
				obj_id = final_obj['obid']
				if final_obj['tp'] == 'tx':
					obj_data = final_text_objs.get(obj_id,None)
					if obj_data:
						submitter_id = obj_data['submitter_id']
						all_submitters.add(str(submitter_id))
						tgt_uname, tgt_avurl = retrieve_credentials(submitter_id, decode_uname=True)
						final_obj['ou'] = tgt_uname
						final_obj['av'] = tgt_avurl
						final_obj['d'] = obj_data['description']
						final_obj['nv'] = obj_data['net_votes']
						final_obj['cc'] = obj_data['reply_count']
						final_obj['mt'] = obj_data['submitted_on']
						final_obj['t'] = convert_to_epoch(final_obj['mt'])
						final_obj['c'] = obj_data['cagtegory']
						final_obj['ex'] = obj_data['expire_at']
						url = obj_data['url']
						if url:
							payload = url.split(":")
							try:
								theme, final_obj['tn'], final_obj['url'] = payload[0], payload[1], payload[2]
								color_grads = COLOR_GRADIENTS[theme]
								final_obj['c1'], final_obj['c2'] = color_grads[0], color_grads[1]
							except:
								final_obj['tn'], final_obj['url'] = '', ''
								final_obj['c1'], final_obj['c2'] = '', ''
						final_enriched_data.append(final_obj)
					else:
						# this obj was not found in the DB (although it was voted on) - thus remove from final data
						pass

				elif final_obj['tp'] == 'img':
					obj_data = final_img_objs.get(obj_id,None)
					if obj_data:
						submitter_id = obj_data['submitter_id']
						all_submitters.add(str(submitter_id))
						tgt_uname, tgt_avurl = retrieve_credentials(submitter_id, decode_uname=True)
						final_obj['ou'] = tgt_uname
						final_obj['av'] = tgt_avurl
						final_obj['id'] = obj_data['id']
						final_obj['i'] = obj_data['image_file']
						final_obj['mt'] = obj_data['submitted_on']
						final_obj['t'] = convert_to_epoch(final_obj['mt'])
						final_obj['nv'] = obj_data['net_votes']
						final_obj['cc'] = obj_data['reply_count']
						final_obj['tr'] = obj_data['trending_status']
						final_obj['cp'] = obj_data['description']
						final_obj['ex'] = obj_data['expire_at']
						final_enriched_data.append(final_obj)
					else:
						# this obj was not found in the DB (although it was voted on) - thus remove from final data
						pass
			cache_voting_history.delay(user_id=own_id, page_num=page_num, json_data=json.dumps([final_enriched_data,max_pages,all_submitters]))
		##############################################################
		page_num = int(page_num)
		on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
		on_opera = request.is_opera_mini
		is_js_env = retrieve_user_env(opera_mini=on_opera, fbs = on_fbs)
		# on_opera = True if (not on_fbs and not is_js_env) else False

		return render(request,"voting/admin_voting_history_view.html",{'data':final_enriched_data,'slug':retrieve_uname(own_id,decode=True), \
			'own_profile':False,'page':{'number':page_num,'has_previous':True if page_num>1 else False,'has_next':True if page_num<max_pages else False,\
			'previous_page_number':page_num-1,'next_page_number':page_num+1},'own_id':own_id,'on_opera':on_opera,'defender_id':defender_id,\
			'on_fbs':on_fbs})
	else:
		raise Http404("Not authorized to view user voting histories")


def user_vote_history(request):
	"""
	Renders the voting history of the user

	Shows all upvotes or downvotes (in separate pages) cast within last 1 month
	"""
	time_now = time.time()
	own_id, page_num = request.user.id, request.GET.get('page', '1')
	json_data = retrieve_detailed_voting_data(page_num=page_num, user_id=own_id)
	if json_data:
		try:
			final_data_list = json.loads(json_data)
		except:
			final_data_list = json_backup.loads(json_data)
		final_enriched_data, max_pages, all_submitters = final_data_list[0], final_data_list[1], final_data_list[2]
	else:
		start_index, end_index = get_indices(page_num, VOTE_HISTORY_ITEMS_PER_PAGE)
		voting_data, list_total_size = retrieve_voting_records(voter_id=own_id, start_idx=start_index, end_idx=end_index, \
			upvotes=True, with_total_votes=True)
		num_pages = list_total_size/VOTE_HISTORY_ITEMS_PER_PAGE
		max_pages = num_pages if list_total_size % VOTE_HISTORY_ITEMS_PER_PAGE == 0 else (num_pages+1)
		text_ids, img_ids, final_data = [], [], []
		for data, vote_time in voting_data:
			# 'data' contains: voter_id+":"+str(target_user_id)+":"+vote_value+":"+target_obj_tp+":"+target_obj_id
			data_list = data.split(":")
			obj_type, obj_id = data_list[3], data_list[4]
			human_vote_time = beautiful_date(vote_time)#exact_date(vote_time)
			text_ids.append(obj_id) if obj_type == 'tx' else img_ids.append(obj_id)
			obj = {'tp':obj_type,'obid':obj_id,'ooid':data_list[1],'vid':own_id,'vt':human_vote_time}
			final_data.append(obj)# created list of dictionaries
		##############################################################
		final_text_objs = {}
		text_objs = Link.objects.only('id','description','submitted_on','net_votes','url','cagtegory','reply_count','submitter','expire_at').\
		filter(id__in=text_ids,is_visible=False).exclude(delete_status='1').values('id','description','submitted_on','net_votes',\
			'url','cagtegory','reply_count','submitter_id','expire_at') if text_ids else []
		for text_obj in text_objs:
			final_text_objs[str(text_obj['id'])] = text_obj
		##############################################################
		final_img_objs = {}
		# img_objs = Photo.objects.only('id','image_file','upload_time','comment_count','vote_score','device','caption','owner').\
		# filter(id__in=img_ids,is_public=False).values('id','image_file','upload_time','comment_count','vote_score','device','caption','owner') if img_ids else []
		img_objs = Link.objects.only('id','image_file','submitted_on','reply_count','net_votes','trending_status','description','submitter','expire_at').\
		filter(id__in=img_ids,is_visible=False).exclude(delete_status='1').values('id','image_file','submitted_on','reply_count',\
			'net_votes','trending_status','description','submitter_id','expire_at') if img_ids else []

		for img_obj in img_objs:
			final_img_objs[str(img_obj['id'])] = img_obj
		##############################################################
		all_submitters, final_enriched_data = set(), []
		
		# enriching data with more fields
		for final_obj in final_data:
			obj_id = final_obj['obid']
			if final_obj['tp'] == 'tx':
				obj_data = final_text_objs.get(obj_id,None)
				if obj_data:
					submitter_id = obj_data['submitter_id']
					all_submitters.add(str(submitter_id))
					tgt_uname, tgt_avurl = retrieve_credentials(submitter_id, decode_uname=True)
					final_obj['ou'] = tgt_uname
					final_obj['av'] = tgt_avurl
					final_obj['d'] = obj_data['description']
					final_obj['nv'] = obj_data['net_votes']
					final_obj['cc'] = obj_data['reply_count']
					final_obj['mt'] = obj_data['submitted_on']
					final_obj['t'] = convert_to_epoch(final_obj['mt'])
					final_obj['c'] = obj_data['cagtegory']
					final_obj['ex'] = obj_data['expire_at']
					url = obj_data['url']
					if url:
						payload = url.split(":")
						try:
							theme, final_obj['tn'], final_obj['url'] = payload[0], payload[1], payload[2]
							color_grads = COLOR_GRADIENTS[theme]
							final_obj['c1'], final_obj['c2'] = color_grads[0], color_grads[1]
						except:
							final_obj['tn'], final_obj['url'] = '', ''
							final_obj['c1'], final_obj['c2'] = '', ''
					final_enriched_data.append(final_obj)
				else:
					# this obj was not found in the DB (although it was voted on) - thus remove from final data
					pass
			
			elif final_obj['tp'] == 'img':
				obj_data = final_img_objs.get(obj_id,None)
				if obj_data:
					submitter_id = obj_data['submitter_id']
					all_submitters.add(str(submitter_id))
					tgt_uname, tgt_avurl = retrieve_credentials(submitter_id, decode_uname=True)
					final_obj['ou'] = tgt_uname
					final_obj['av'] = tgt_avurl
					final_obj['id'] = obj_data['id']
					final_obj['i'] = obj_data['image_file']
					final_obj['mt'] = obj_data['submitted_on']
					final_obj['t'] = convert_to_epoch(final_obj['mt'])
					final_obj['nv'] = obj_data['net_votes']
					final_obj['cc'] = obj_data['reply_count']
					final_obj['tr'] = obj_data['trending_status']
					final_obj['cp'] = obj_data['description']
					final_obj['ex'] = obj_data['expire_at']
					final_enriched_data.append(final_obj)
				else:
					# this obj was not found in the DB (although it was voted on) - thus remove from final data
					pass
		cache_voting_history.delay(user_id=own_id, page_num=page_num, json_data=json.dumps([final_enriched_data,max_pages,all_submitters]))
	##############################################################
	page_num = int(page_num)
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	on_opera = request.is_opera_mini
	is_js_env = retrieve_user_env(opera_mini=on_opera, fbs = on_fbs)
	# on_opera = True if (not on_fbs and not is_js_env) else False
	###################### Retention activity logging ######################
	if own_id > SEGMENT_STARTING_USER_ID:
		time_now = time.time()
		act = 'IL' if request.mobile_verified else 'IL.u'
		activity_dict = {'m':'GET','act':act,'t':time_now,'pg':page_num}# defines what activity just took place
		log_user_activity.delay(user_id=own_id, activity_dict=activity_dict, time_now=time_now)
	########################################################################

	return render(request,"voting/voting_history.html",{'slug':retrieve_uname(own_id,decode=True), 'own_profile':True,\
		'page':{'number':page_num,'has_previous':True if page_num>1 else False,'has_next':True if page_num<max_pages else False,\
		'previous_page_number':page_num-1,'next_page_number':page_num+1},'own_id':own_id,'on_opera':on_opera,'data':final_enriched_data,\
		'time_now':time_now,'on_fbs':on_fbs})


def user_sybil_history(request, user_id, hist_type):
	"""
	Renders suspected sybils and haters in an HTML template for super defenders
	"""
	own_id = request.user.id
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if is_super_defender:
		if hist_type == 'sybils':
			return render(request,"voting/voting_sybils.html",{'data':retrieve_users_voting_relationships(user_id, 'sybils'),\
				'tgt_uname':retrieve_uname(user_id,decode=True),'target_id':user_id,'own_id':own_id,'hist_type':hist_type})
		elif hist_type == 'reverse-sybils':
			return render(request,"voting/voting_sybils.html",{'data':retrieve_users_voting_relationships(user_id, 'reverse-sybils'),\
				'tgt_uname':retrieve_uname(user_id,decode=True),'target_id':user_id,'own_id':own_id,'hist_type':hist_type})
		else:
			raise Http404("Unrecognized sybil string")
	else:
		raise Http404("Not authorized to view sybils")
		

#######################################################################################
##################################### Legacy code #####################################

"""
This code supports 'old' data liked by users
"""


def user_old_vote_history(request):
	"""
	Renders the voting history of the user

	Shows all upvotes or downvotes (in separate pages) cast within last 1 month
	"""
	own_id, page_num = request.user.id, request.GET.get('page', '1')
	json_data = retrieve_old_detailed_voting_data(page_num=page_num, user_id=own_id)
	if json_data:
		try:
			final_data_list = json.loads(json_data)
		except:
			final_data_list = json_backup.loads(json_data)
		final_enriched_data, max_pages, all_submitters = final_data_list[0], final_data_list[1], final_data_list[2]
	else:
		start_index, end_index = get_indices(page_num, VOTE_HISTORY_ITEMS_PER_PAGE)
		voting_data, list_total_size = retrieve_voting_records(voter_id=own_id, start_idx=start_index, end_idx=end_index, \
			upvotes=True, with_total_votes=True)
		num_pages = list_total_size/VOTE_HISTORY_ITEMS_PER_PAGE
		max_pages = num_pages if list_total_size % VOTE_HISTORY_ITEMS_PER_PAGE == 0 else (num_pages+1)
		text_ids, img_ids, final_data = [], [], []
		for data, vote_time in voting_data:
			# 'data' contains: voter_id+":"+str(target_user_id)+":"+vote_value+":"+target_obj_tp+":"+target_obj_id
			data_list = data.split(":")
			obj_type, obj_id = data_list[3], data_list[4]
			human_vote_time = beautiful_date(vote_time)#exact_date(vote_time)
			text_ids.append(obj_id) if obj_type == 'tx' else img_ids.append(obj_id)
			obj = {'tp':obj_type,'obid':obj_id,'ooid':data_list[1],'vid':own_id,'vt':human_vote_time}
			final_data.append(obj)# created list of dictionaries
		##############################################################
		final_text_objs = {}
		text_objs = Link.objects.only('id','description','submitted_on','net_votes','url','cagtegory','reply_count','submitter').\
		filter(id__in=text_ids,is_visible=True).values('id','description','submitted_on','net_votes','url','cagtegory','reply_count','submitter') if text_ids else []
		for text_obj in text_objs:
			final_text_objs[str(text_obj['id'])] = text_obj
		##############################################################
		final_img_objs = {}
		img_objs = Photo.objects.only('id','image_file','upload_time','comment_count','vote_score','device','caption','owner').\
		filter(id__in=img_ids,is_public=True).values('id','image_file','upload_time','comment_count','vote_score','caption','device','owner') if img_ids else []
		
		for img_obj in img_objs:
			final_img_objs[str(img_obj['id'])] = img_obj
		##############################################################
		all_submitters, final_enriched_data = set(), []
		# enriching data with more fields
		for final_obj in final_data:
			obj_id = final_obj['obid']
			if final_obj['tp'] == 'tx':
				obj_data = final_text_objs.get(obj_id,None)
				if obj_data:
					submitter_id = obj_data['submitter']
					all_submitters.add(str(submitter_id))
					tgt_uname, tgt_avurl = retrieve_credentials(submitter_id, decode_uname=True)
					final_obj['ou'] = tgt_uname
					final_obj['av'] = tgt_avurl
					final_obj['d'] = obj_data['description']
					final_obj['nv'] = obj_data['net_votes']
					final_obj['cc'] = obj_data['reply_count']
					final_obj['mt'] = obj_data['submitted_on']
					final_obj['t'] = convert_to_epoch(final_obj['mt'])
					final_obj['c'] = obj_data['cagtegory']
					url = obj_data['url']
					if url:
						payload = url.split(":")
						try:
							theme, final_obj['tn'], final_obj['url'] = payload[0], payload[1], payload[2]
							color_grads = COLOR_GRADIENTS[theme]
							final_obj['c1'], final_obj['c2'] = color_grads[0], color_grads[1]
						except:
							final_obj['tn'], final_obj['url'] = '', ''
							final_obj['c1'], final_obj['c2'] = '', ''
					final_enriched_data.append(final_obj)
				else:
					# this obj was not found in the DB (although it was voted on) - thus remove from final data
					pass
			
			elif final_obj['tp'] == 'img':
				obj_data = final_img_objs.get(obj_id,None)
				if obj_data:
					submitter_id = obj_data['owner']
					all_submitters.add(str(submitter_id))
					tgt_uname, tgt_avurl = retrieve_credentials(submitter_id, decode_uname=True)
					final_obj['ou'] = tgt_uname
					final_obj['av'] = tgt_avurl
					final_obj['id'] = obj_data['id']
					final_obj['i'] = obj_data['image_file']
					final_obj['mt'] = obj_data['upload_time']
					final_obj['t'] = convert_to_epoch(final_obj['mt'])
					final_obj['nv'] = obj_data['vote_score']
					final_obj['cc'] = obj_data['comment_count']
					final_obj['tr'] = '1' if obj_data['device'] == '6' else '0'
					final_obj['cp'] = obj_data['caption']
					final_enriched_data.append(final_obj)
				else:
					# this obj was not found in the DB (although it was voted on) - thus remove from final data
					pass
		cache_voting_history.delay(user_id=own_id, page_num=page_num, json_data=json.dumps([final_enriched_data,max_pages,all_submitters]),\
			data_type='old')
	##############################################################
	page_num = int(page_num)
	on_fbs = request.META.get('HTTP_X_IORG_FBS',False)
	on_opera = request.is_opera_mini
	is_js_env = retrieve_user_env(opera_mini=on_opera, fbs = on_fbs)
	# on_opera = True if (not on_fbs and not is_js_env) else False

	return render(request,"legacy/old_voting_history.html",{'slug':retrieve_uname(own_id,decode=True), 'own_profile':True,\
		'page':{'number':page_num,'has_previous':True if page_num>1 else False,'has_next':True if page_num<max_pages else False,\
		'previous_page_number':page_num-1,'next_page_number':page_num+1},'own_id':own_id,'on_opera':on_opera,'data':final_enriched_data,\
		'on_fbs':on_fbs})


def show_old_voting_summary(request,pk,orig,pht):
	"""
	Displays 'net_votes' for each obj

	Only applicable to 'old' history
	"""
	own_id = request.user.id
	if pht is None:
		raise Http404("No obj type provided")
	elif pht == '1':
		# it's a photo
		try:
			obj = Photo.objects.get(id=pk)
			purl = obj.image_file.url
			oun = obj.owner.username
			ooid = obj.owner_id
		except Photo.DoesNotExist:
			raise Http404("Photo object does not exist in our DB")
		if ooid != request.user.id:
			is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
			if not is_super_defender:
				raise Http404("Not authorized to view this")
		trending_status, time_of_selection = is_obj_trending(prefix='img:', obj_id=pk, with_trending_time=True)
		lid = None
		tp = "img"
		if orig in ('3','22'):
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
			raise Http404("Text object does not exist in our DB")
		if ooid != own_id:
			is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
			if not is_super_defender:
				raise Http404("Not authorized to view this")
		# trending_status, time_of_selection = is_obj_trending(prefix='img:', obj_id=pk, with_trending_time=True)# not needed yet
		trending_status, time_of_selection = False, None
		purl = None #not applicable, it's not a photo object
		lid = None
		tp = "tx"
		if orig in ('3','22'):
			lid = tp+":"+pk
			request.session["home_hash_id"] = lid
			request.session.modified = True
	else:
		# not a link neither a photo
		return redirect('home')
	topic = request.session.pop("origin_topic",'')
	defender, voter_id_names_status_and_votes = False, []
	is_star = is_image_star(user_id=ooid)
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
		'obj_id':pk,'pht':pht,'is_star':is_star,'defender':defender,'voter_id_names_status_and_votes':voter_id_names_status_and_votes,\
		'tp':tp,'first_time_voting_judger':tutorial_unseen(user_id=own_id, which_tut='12', renew_lease=True) if exists else False, 'ooid':ooid,\
		'oun':oun,'purl':purl,'lid':lid, 'show_banning_prompt':show_banning_prompt,'orig':orig,'own_id':str(own_id),'is_trending':trending_status,\
		'time_of_trending':time_of_selection,'origin_topic':topic})

