import time
import ujson as json
from datetime import datetime, timedelta
from operator import itemgetter
from django.db.models import F
from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect
from django.middleware import csrf
from django.utils import timezone
from templatetags.s3 import get_s3_object
from models import Photo, UserProfile, Link
from page_controls import ITEMS_PER_PAGE, ITEMS_PER_PAGE_IN_ADMINS_LEDGER
from views import get_price, get_addendum, get_page_obj, convert_to_epoch, return_to_content
from judgement_forms import PhotoReportForm, DefenderBlockingReasonForm, AddDefenderIDForm, RemDefenderIDForm
from tasks import process_reporter_payables, sanitize_expired_bans, post_banning_tasks, remove_target_users_posts_from_all_feeds,\
delete_temporarily_saved_content_data
from redis3 import set_inter_user_ban, temporarily_save_user_csrf, remove_single_ban, is_already_banned, get_banned_users, \
save_ban_target_credentials, get_ban_target_credentials, delete_ban_target_credentials, tutorial_unseen
from score import PHOTO_REPORT_PROMPT,TEXT_REPORT_PROMPT,REPORTED_CASE_COMPLETION_BONUS, HOURS_LOOKBACK_FOR_CHECKING_CONTENT_CLONES,\
MEHFIL_REPORT_PROMPT, PROFILE_REPORT_PROMPT, GET_TEXT_REPORT_HELP_LABEL, GET_PHOTO_REPORT_HELP_LABEL, GET_PROFILE_REPORT_HELP_LABEL,\
GET_MEHFIL_REPORT_HELP_LABEL
from redis7 import get_complaint_details, has_super_privilege, get_content_complaints, delete_complaint, \
get_num_complaints, in_defenders, get_votes, rate_limit_complainer, in_defs_forever, get_complainer_ids, retrieve_top_complainer_reputation, \
log_banning, get_defenders_ledger, get_global_admins_ledger, is_content_voting_closed, remove_defender, get_payables, retrieve_all_defenders, \
temporarily_save_content_details, retrieve_temporary_saved_content_details, enrich_temporarily_saved_content_details_with_duration, \
complaint_exists, impose_content_and_voting_ban, check_content_and_voting_ban, get_complainer_case_history, log_case_and_incr_reputation, \
add_defender, filter_ids_with_content_and_voting_ban, retrieve_user_content_and_vote_ban_dictionary, remove_content_and_voting_ban, \
edit_content_and_voting_ban, is_ban_editing_locked, set_complaint, are_ids_unbannable,log_case_closure, COMPLAINT
from redis6 import retrieve_group_reqd_data, freeze_reported_group_functionality, retrieve_group_owner_id, retrieve_group_creation_time, \
retrieve_group_rules, get_reported_group_info
from redis4 import return_referrer_logs, retrieve_uname, retrieve_bulk_unames, freeze_critical_profile_functionality, retrieve_credentials
from redis2 import update_object
from verified import FEMALES


SEVEN_MINS = 7*60
TWENTY_MINS = 20*60

#####################################################Intra User Banning#####################################################


def ban_underway(request):
	"""
	Renders a notice that certain actions can't be taken since the target user has been banned (by ther requesting user)

	Actions include fanning someone, writing a reply on their post, etc.
	"""
	banned_by_yourself = request.session.pop("banned_by_yourself",None)
	target_username = request.session.pop("target_username",None)
	banned_by = request.session.pop("banned_by",None)
	ban_time = request.session.pop("ban_time",None)
	origin = request.session.pop("where_from",None)
	uname = request.session.pop("own_uname",None)
	obid = request.session.pop("obj_id",None)
	lid = request.session.pop('lid',None)
	# if origin == '12':#this is outdated now
	#   return render(request,"judgement/cant_fan.html",{'own_id':str(request.user.id),'target_username':target_username,'ban_time':ban_time,\
	#       'banned_by_yourself':banned_by_yourself})
	# else:
	return render(request,"judgement/ban_system_check.html",{'own_id':str(request.user.id),'banned_by':banned_by,'ban_time':ban_time, \
		'origin':origin,'uname':uname,'target_username':target_username,'obid':obid,'lid':lid})


def banned_users_list(request):
	"""
	Renders a list of users banned by a certain user, giving options of unbanning them or editing the ban
	"""
	banned_ids_to_show_with_ttl, banned_ids_to_show, banned_ids_to_unban, own_id = {}, [], [], request.user.id
	all_banned_ids_with_ttl = get_banned_users(own_id)
	if all_banned_ids_with_ttl:
		for banned_id, ttl in all_banned_ids_with_ttl:
			if ttl < 5:
				banned_ids_to_unban.append(banned_id)
			else:
				banned_ids_to_show.append(banned_id)
				banned_ids_to_show_with_ttl[int(banned_id)] = ttl
		sanitize_expired_bans.delay(own_id, banned_ids_to_unban)
		banned_users = User.objects.select_related('userprofile').filter(id__in=banned_ids_to_show)
		banned_users_with_ttl = []
		for user in banned_users:
			banned_users_with_ttl.append((user,banned_ids_to_show_with_ttl[user.id]))
		return render(request,"judgement/banned_users_list.html",{'banned_users_with_ttl':banned_users_with_ttl,'females':FEMALES,\
			'status':request.session.pop("user_ban_change_status",None),'cooloff_ttl':request.session.pop("user_ban_cooloff_ttl",None),\
			'target_username':request.session.pop("user_ban_cooloff_username",None)})
	else:
		return render(request,"judgement/banned_users_list.html",{'status':request.session.pop("user_ban_change_status",None),\
			'females':None,'cooloff_ttl':request.session.pop("user_ban_cooloff_ttl",None),'banned_users_with_ttl':[],\
			'target_username':request.session.pop("user_ban_cooloff_username",None)})


def first_time_inter_user_banner(request):
	"""
	Flashes a helpful message to first time users that they successfully blocked so and so
	"""
	user_id = request.user.id
	target_username = get_ban_target_credentials(own_id=user_id, username_only=True, destroy=True)
	if not target_username:
		raise Http404("Target username does not exist")
	elif not request.mobile_verified:
		return render(request,"verification/unable_to_submit_without_verifying.html",{'ban_user':True})
	else:
		return render(request,"judgement/inter_user_ban.html",{'first_time_banner_instructions':True,'target_username':target_username,\
			'own_username':retrieve_uname(user_id,decode=True)})


def inter_user_ban_not_permitted(request):
	"""
	Notifying unverified accounts that user-banning permission requires mobile verification
	"""
	delete_ban_target_credentials(request.user.id)
	if request.mobile_verified:
		raise Http404("Inter user ban is actually permitted!")
	else:
		return render(request,"verification/unable_to_submit_without_verifying.html",{'ban_user':True})


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def enter_inter_user_ban(request,*args,**kwargs):
	"""
	Responsible for setting the ban on a certain target_id

	Test case: Unban a user and then quickly try to reban them (i.e. testing the REBAN ratelimit)
	"""
	if request.method == "POST":
		can_unban = request.POST.get("can_unban",None)
		second_decision = request.POST.get("sec_dec",None)
		initial_decision = request.POST.get("init_dec",None)
		user_id = request.user.id
		if second_decision:
			if second_decision == '0':
				if can_unban:
					# unbanning user
					credentials = get_ban_target_credentials(own_id=user_id, destroy=True)
					try:
						target_user_id, target_username = credentials["target_id"], credentials["target_username"]
					except KeyError:
						return redirect("banned_users_list")
					banned, rate_limit_ttl = False, None
					if target_user_id and target_username:
						banned, rate_limit_ttl = remove_single_ban(user_id, target_user_id)
					if rate_limit_ttl:
						request.session["user_ban_cooloff_username"] = target_username
						request.session["user_ban_change_status"] = '4'#can't unblock since they banned user recently
						request.session["user_ban_cooloff_ttl"] = rate_limit_ttl
					else:
						request.session["user_ban_change_status"] = '0' if banned else '2'
					request.session.modified = True
					return redirect("banned_users_list")
				else:
					orig = request.POST.get("orig",None)
					obid = request.POST.get("obid",None)
					lid = request.POST.get("lid",None)
					tunm = request.POST.get("tunm",None)
					return return_to_content(request,orig,obid,lid,tunm)
			else:
				# set ban on user
				credentials = get_ban_target_credentials(own_id=user_id)
				try:
					target_user_id, target_username = credentials["target_id"], credentials["target_username"]
				except KeyError:
					return redirect("banned_users_list")
				CONVERT_DUR_CODE_TO_DURATION = {'1':604800,'2':604800,'3':604800,'4':2628000,'5':7884000}
				if target_user_id and target_username:
					time_now = time.time()
					banned, ttl = set_inter_user_ban(own_id=user_id, target_id=target_user_id, target_username=target_username, \
						ttl=CONVERT_DUR_CODE_TO_DURATION[second_decision], time_now=time_now, can_unban=can_unban)
					if banned is None and ttl:
						request.session["user_ban_cooloff_username"] = target_username
						request.session["user_ban_cooloff_ttl"] = ttl
						request.session["user_ban_change_status"] = '3'
						request.session.modified = True
						return redirect("banned_users_list")
					elif can_unban and banned:
						delete_ban_target_credentials(user_id)
						post_banning_tasks.delay(own_id=user_id, target_id=target_user_id)
						request.session["user_ban_change_status"] = '1'
						request.session.modified = True
						return redirect("banned_users_list")
					elif can_unban and not banned:
						delete_ban_target_credentials(user_id)
						request.session["user_ban_change_status"] = '2'
						request.session.modified = True
						return redirect("banned_users_list")
					elif tutorial_unseen(user_id=user_id, which_tut='9', renew_lease=True) and banned:
						post_banning_tasks.delay(own_id=user_id, target_id=target_user_id)
						return redirect("first_time_inter_user_banner")
					elif banned:
						delete_ban_target_credentials(user_id)
						post_banning_tasks.delay(own_id=user_id, target_id=target_user_id)
						return redirect("banned_users_list")
					else:
						# could be malicious
						delete_ban_target_credentials(user_id)
						return redirect("home")
				else:
					return redirect("banned_users_list")
		elif initial_decision:
			orig = request.POST.get("orig",None)
			obid = request.POST.get("obid",None)
			lid = request.POST.get("lid",None)
			if initial_decision == '1':
				is_verified = request.mobile_verified
				if not is_verified:
					return redirect("inter_user_ban_not_permitted")
				elif is_verified:
					return render(request,"judgement/inter_user_ban.html",{'target_username':get_ban_target_credentials(own_id=user_id, username_only=True),\
						'decide_time':True,'orig':orig,'obid':obid,'lid':lid})
				else:
					return redirect("inter_user_ban_not_permitted")
			elif initial_decision == '0':
				delete_ban_target_credentials(user_id)
				tunm = request.POST.get("tunm",None)
				return return_to_content(request,orig,obid,lid,tunm)
		else:
			target_user_id = int(request.POST.get("tuid",None)[2:-2],16) #converting hex number to int
			if target_user_id == user_id:
				# cannot block self
				return redirect("home")
			elif target_user_id != user_id:
				target_username = retrieve_uname(target_user_id,decode=True)
				if target_username:
					save_ban_target_credentials(own_id=user_id, target_id=target_user_id, target_username=target_username)
					banner_id, existing_ttl = is_already_banned(own_id=user_id, target_id=target_user_id, return_banner=True)# already banned by the user
					orig = request.POST.get("orig",None)
					obid = request.POST.get("obid",None)
					tunm = request.POST.get("tunm",None)
					lid = request.POST.get("lid",None)
					if existing_ttl is None or existing_ttl is False:
						return render(request,"judgement/inter_user_ban.html",{'target_username':target_username,'to_ban':True,'orig':orig,'lid':lid,\
							'tunm':tunm,'obid':obid})
					else:
						if banner_id == str(user_id):
							return render(request,"judgement/inter_user_ban.html",{'target_username':target_username,'target_user_id':target_user_id,\
								'already_banned':True, 'banned_by':'self'})
						else:
							return render(request,"judgement/inter_user_ban.html",{'target_username':target_username,'target_user_id':target_user_id,\
								'already_banned':True, 'banned_by':'other','tunm':tunm,'obid':obid,'orig':orig,'lid':lid})
				else:
					raise Http404("Target username does not exist")
			else:
				return redirect("home")
	else:
		return redirect("banned_users_list")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def change_ban_time(request):
	"""
	Setting or editing the time of an inter user ban
	"""
	if request.method == "POST":
		banned_user_id, banned_username = request.POST.get("buid",None), request.POST.get("bun",None)
		if banned_user_id and banned_username:
			save_ban_target_credentials(own_id=request.user.id, target_id=banned_user_id, target_username=banned_username)
			return render(request,"judgement/inter_user_ban.html",{'target_username':banned_username,'decide_time':True, 'can_unban':True})
		else:
			return redirect("banned_users_list")
	else:
		return redirect("banned_users_list")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def user_ban_help(request):
	"""
	Renders help text regarding the extent of user-to-user blocking
	"""
	if request.method == 'POST':
		target_username = request.POST.get('tunm',None)
		target_origin = request.POST.get('orig',None)
		target_linkid = request.POST.get('lid',None)
		target_obj_id = request.POST.get('obid',None)
		return render(request,"judgement/user_ban_help.html",{'tunm':target_username,'decide_time':True,'orig':target_origin,\
			'lid':target_linkid,'obid':target_obj_id})
	else:
		# not a POST request
		return render(request,"judgement/user_ban_help.html",{})


##############################################Report/Block button (page shows both blocking and reporting)###############################################


def report_or_block(request):
	"""
	Processes content report or user block (i.e. "Do you want to report content, or block this user?")

	This is called in the absense of JS modal
	"""
	if request.method == "POST":
		payload = request.POST.get("report",None)
		if payload:
			## added extra parameter at the start of the string 'img' or 'txt'.
			try:
				prefix = payload[:2]
			except (TypeError,NameError):
				return redirect("missing_page")
			if prefix == "tx":
				report_type = "tx"
			elif prefix == "im":
				report_type = "img"
			elif prefix == "pf":
				report_type = "pf"
			else:
				# no 4th type of content
				return redirect("missing_page")
			if report_type == 'pf':
				# if profile is reported
				data = payload.split("#",4)
				target_id, own_id = int(data[2]), request.user.id
				if target_id == own_id:
					return render(request,"judgement/report_or_block.html",{'type':report_type, 'allwd':False,'org':data[1],'oun':data[3],\
						'obid':data[2],'thumb_url':data[4]})
				else:
					return render(request,"judgement/report_or_block.html",{'type':report_type,'allwd':True,'org':data[1],'oun':data[3],\
						'ooid':data[2],'thumb_url':data[4],'obid':data[2],'hid':'7f'+hex(target_id)+":a"})
			elif report_type == 'tx':
				# text type report
				data = payload.split("#",7)
				target_id, own_id = int(data[4]), request.user.id
				if target_id == own_id:
					return render(request,"judgement/report_or_block.html",{'type':report_type, 'allwd':False,'cap':data[7],'oun':data[3],\
						'org':data[1],'obid':data[2],'lid':data[6]})
				else:
					return render(request,"judgement/report_or_block.html",{'type':report_type,'allwd':True,'org':data[1],'lid':data[6],'oun':data[3],\
						'ooid':data[4],'cap':data[7],'av_url':data[5],'obid':data[2],'hid':'7f'+hex(target_id)+":a"})
			elif report_type == 'img':
				# photo type report
				data = payload.split("#",7)
				target_id, own_id = int(data[4]), request.user.id
				if target_id == own_id:
					return render(request,"judgement/report_or_block.html",{'type':report_type,'allwd':False,'thumb_url':data[5],'oun':data[3],\
						'org':data[1],'obid':data[2],'lid':data[6]})
				else:
					context = {'type':report_type,'allwd':True,'org':data[1],'lid':data[6],'oun':data[3],'ooid':data[4],\
					'cap':data[7],'thumb_url':data[5],'obid':data[2],'hid':'7f'+hex(target_id)+":a"}
					return render(request,"judgement/report_or_block.html",context)
			else:
				# no other report type exists within this loop (mehfils aren't part of this reporting loop - they have their own loop - they can be absorbed here for better maintenance)
				return redirect("missing_page")
		else:
			return redirect("missing_page")    
	else:
		return redirect("missing_page")


######################################################## Defender Banning and Reported Content #######################################################


def get_usernames(vote_id_and_values, ban_status=False):
	"""
	Retrieves usernames of voters

	if ban_status is True, also reverts ban status of users
	"""
	voter_ids = [i[0] for i in vote_id_and_values]
	voter_names = User.objects.filter(id__in=voter_ids).values('id','username')
	voter_name_dict = {}
	for data in voter_names:
		voter_name_dict[data["id"]] = data["username"]
	if ban_status:
		# return (username, ban_status and vote_value) tuple
		users_with_bans_dict = retrieve_user_content_and_vote_ban_dictionary(voter_ids)#returns { voter_id : ban_status }
		voter_username_ban_status_and_vote_values = []
		for id_,vote_val in vote_id_and_values:
			voter_username_ban_status_and_vote_values.append((id_,voter_name_dict[int(id_)],users_with_bans_dict[id_],vote_val))
		return voter_username_ban_status_and_vote_values
	else:
		# return (username, vote_value) tuple
		voter_usernames_and_values = []
		for id_,vote_val in vote_id_and_values:
			voter_usernames_and_values.append((id_,voter_name_dict[int(id_)],vote_val))
		return voter_usernames_and_values


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def ban_content_submitter_or_voters(request,*args,**kwargs):
	"""
	Defender view where a piece of content is judged upon

	A defender can unilaterally come here by reporting any content they don't like
	A defender also ends up here when passing judgement on user-reported content
	"""
	if request.method == 'POST':
		own_id = request.user.id
		if in_defenders(own_id):
			own_uname = request.user.username#mhb11
			dec = request.POST.get('dec',None)#2
			obid = request.POST.get('obid',None)#1260
			oun = request.POST.get('oun',None)#gordon
			orig = request.POST.get('orig',None)#1
			lid = request.POST.get('lid',None)#None
			purl = request.POST.get('purl',None)#purl
			ooid = request.POST.get('ooid',None)#4
			tp = request.POST.get('tp',None)# 'img' or 'tx'
			cap = request.POST.get('cap',None)#
			if dec == '1':
				# imposing submission + voting ban on a single target
				dur = request.POST.get('dur',None)#dur denotes ban duration
				ban_dur = dur in ('1','2','3','4','5','6')
				if complaint_exists(obid, tp) and ban_dur:
					# already reported and can be found in reported_content list, so redirect_user there
					request.session["report_already_exists"] = '1'
					request.session.modified = True
					return redirect("cull_content")
				elif ban_dur:
					ban_type = request.POST.get('bt',None)# see get_ban_type() for detailed ban types
					if ban_type in ('1a','1b'):
						pass
						# action = enforce_ban_type(ban_type=ban_type,target_user_id=ooid,target_uname=oun,duration=dur,own_uname=own_uname,obj_type=tp,\
						#     obj_id=obid,reference=cap if tp == 'tx' else purl)
					else:
						#ban type should be nothing else
						return return_to_content(request,orig,obid,lid,oun)
				elif dur == '0':
					# unban, i.e. remove submission + voting ban
					# action = drop_ban(ban_type='1a',obj_owner_id=ooid)
					pass
				else:
					# didn't take an action
					return return_to_content(request,orig,obid,lid,oun)
			else:
				# 'dec' was other than '1' and '2'
				return return_to_content(request,orig,obid,lid,oun)
			# '1' and '2' were handled - proceed to the 'reason' step
			return render(request,"judgement/feedback_by_defender_for_banned_user.html",{'orig':orig,'obid':obid,'lid':lid,'oun':oun,\
				'form':DefenderBlockingReasonForm(),'ooid':ooid,'dur':dur,'previous_reasons':get_defenders_ledger(own_id),'action':action,\
				'purl':purl,'tp':tp,'cap':cap,'bt':ban_type})
		else:
			#user not a defender!
			return redirect("missing_page")
	else:
		#no GET requests allowed, redirect user
		return redirect("missing_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def log_banning_reason_given_by_defender(request):
	"""
	Processes banning reason given by defender (content or vote ban)

	Blocked user is shown the reason on their profile
	A trail is kept for the defender responsible for the blocking
	Another trail is kept for global admin to view (who blocked whom and why)
	"""
	if request.method == 'POST':
		form = DefenderBlockingReasonForm(request.POST)
		orig = request.POST.get("orig",None)
		obid = request.POST.get("obid",None)
		lid = request.POST.get("lid",None)
		oun = request.POST.get("oun",None)
		ooid = request.POST.get("ooid",None)
		dur = request.POST.get("dur",None)
		action = request.POST.get("action",None)
		purl = request.POST.get("purl",None)
		cap = request.POST.get("cap",None)
		obj_type = request.POST.get("tp",None)
		ban_type = request.POST.get("bt",None)
		if form.is_valid():
			own_id = request.user.id
			reason = form.cleaned_data.get("text")
			# if action == 'banned_voter':
			#     target_ids = request.session.pop('vote_ban_target_ids'+obid,None)
			#     if target_ids:
			#         unames = User.objects.filter(id__in=target_ids).values_list('username',flat=True)
			#         add_multiban_feedback(target_user_ids=target_ids, reason_text=reason, action=action)#adding banning reason so that banned users get constructive feedback
			#         log_banning(target_uname=unames,reason_of_ban=reason,action=action,dur_of_ban=dur,time_of_ban=time.time(),banned_by_id=own_id,\
			#             banned_by_uname=retrieve_uname(own_id,decode=True),photo_thumb=purl,obj_id=obid, owner_id=ooid, oun=oun, cap=cap, ban_type=ban_type,\
			#             obj_type=obj_type)
			#         increment_defender_case_file(own_id,action)
			#     return return_to_content(request,orig,obid,lid,oun)
			if action in ('banned_content_submitter_and_voter','undo_content_and_voting_ban'):
				# add_ban_feedback(target_user_id=ooid, reason_text=reason, action=action)#so that reason is visible to user who got banned, and saved for posterity
				log_banning(target_uname=oun,reason_of_ban=reason,action=action,dur_of_ban=dur,time_of_ban=time.time(),banned_by_id=own_id,\
					banned_by_uname=retrieve_uname(own_id,decode=True),photo_thumb=purl,obj_id=obid, owner_id=ooid, oun=oun, cap=cap, ban_type=ban_type,\
					obj_type=obj_type)
				# increment_defender_case_file(own_id,action)
				if action == 'undo_content_ban':
					# no need to call 'ban voters' prompt
					return return_to_content(request,orig,obid,lid,oun)    
			else:
				# there is no other kind of banning currently
				pass
			if is_content_voting_closed(obj_id=obid,obj_type=obj_type):
				# cannot ban voters when 'voter list' is kaput
				return return_to_content(request,orig,obid,lid,oun)
			else:
				# impose short bans on voters too (if you want to)
				vote_id_and_values = get_votes(obid,obj_type=obj_type)
				if vote_id_and_values:
					# bannable voters exist, so now show voter banning options
					number_of_voters = len(vote_id_and_values)
					vote_id_names_status_and_votes = get_usernames(vote_id_and_values, ban_status=True)
					context={'voter_payload':vote_id_names_status_and_votes,'purl':purl,'oun':oun,'num':number_of_voters,'obid':obid,'origin':orig,\
					'link_id':lid,'ooid':ooid,'dec':'2','tp':'img'}
					return render(request,'judgement/ban_content_submitter_or_voters.html',context)
				else:
					#can't ban voters since no votes dropped on photo ever
					return return_to_content(request,orig,obid,lid,oun)
		else:
			# when form is invalid
			return render(request,"judgement/feedback_by_defender_for_banned_user.html",{'orig':orig,'obid':obid,'lid':lid,'oun':oun,'form':form,\
				'dur':dur,'ooid':ooid,'previous_reasons':get_defenders_ledger(request.user.id),'purl':purl,'action':action})
	else:
		return redirect("missing_page")


def content_culling_instructions(request):
	"""
	Displays intructions to defenders regarding how to judge list of reported content (e.g. defenders who're going through the list of reported photos)
	"""
	if in_defenders(request.user.id):
		return render(request,"judgement/photo_culler_tutorial.html",{})
	else:
		return redirect("missing_page")


#######################################
#######################################
#######################################


def cull_content_loc(request,obj_id,obj_type):
	"""
	Helps in landing back at exact spot when defender checks out object details in cull list (e.g. to see what the pixellated image actually is)
	"""
	complaints = get_content_complaints()
	try:
		index = complaints.index(COMPLAINT+obj_type+":"+str(obj_id))
	except (TypeError,ValueError,AttributeError):
		index = 0
	page_num, addendum = get_addendum(index,ITEMS_PER_PAGE)
	page_obj = get_page_obj(page_num,complaints,ITEMS_PER_PAGE)
	detailed_complaints = get_complaint_details(page_obj.object_list)
	object_list = sorted(detailed_complaints,key=itemgetter('n'),reverse=True) #sorting by the number of complaints
	url = reverse_lazy("cull_content")+addendum
	request.session['page_object'] = page_obj
	request.session['oblst'] = object_list
	request.session['total'] = len(complaints)
	return redirect(url)


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def cull_content(request,*args,**kwargs):
	"""
	Defender view that shows all reported content in a list, and allows case-by-case resolution
	"""
	is_defender, is_super_defender = in_defenders(request.user.id, return_super_status=True)
	if is_defender:
		own_id = request.user.id
		delete_temporarily_saved_content_data.delay(own_id)# cleansing temporary cache
		if request.method == 'POST':
			# decision making on cull-list
			tp = request.POST.get("tp",None)#'img', 'tx', 'pf', 'mf'
			obid = request.POST.get("obid",None)#obj_id
			
			if tp == 'tx':
				#type is 'text'
				text = request.POST.get("txt",None)
				img_url, topic, rules, tgt_uname, tgt_avurl = None, None, None, None, None
				ooid = str(Link.objects.only('submitter').get(id=obid).submitter_id) #obj owner id
			
			elif tp == 'mf':
				# type is 'mehfil'
				topic, rules = request.POST.get("topic",None), request.POST.get("rules",None)
				img_url, text, tgt_uname, tgt_avurl = None, None, None, None
				ooid = retrieve_group_owner_id(group_id=obid)#mehfil owner ID
			
			elif tp == 'pf':
				# type is 'profile'
				form_uname, form_avurl = request.POST.get("nick",None), request.POST.get("avurl",None)
				tgt_uname, tgt_avurl = retrieve_credentials(obid, decode_uname=True)#user ID
				if tgt_uname != form_uname:
					# obid or nick was tinkered?
					raise Http404("Data was tinkered")
				else:
					# proceed
					img_url, text, topic, rules = None, None, None, None
					ooid = obid
			else:
				# type is 'image' (by default)
				img_url, text = request.POST.get("purl",None), request.POST.get("txt",None)
				topic, rules, tgt_uname, tgt_avurl = None, None, None, None
				ooid = str(Photo.objects.only('owner').get(id=obid).owner_id)# obj owner id

			#################
			already_banned, time_remaining, ban_detail = check_content_and_voting_ban(ooid, with_details=True)
			if already_banned:
				can_edit, reason = can_edit_ban(own_id, ban_detail['did'], ooid)
			else:
				can_edit, reason = True, None
			#################
			if reason == 'not_defender':
				raise Http404("You are not an authorized defender")
			elif ooid == str(own_id):
				# don't allow deciding own reported content
				return render(request,'judgement/judging_own_item.html',{'purl':img_url,'text':text,'group_topic':topic,'group_rules':rules,\
					'tgt_uname':tgt_uname,'tgt_avurl':tgt_avurl, 'obid':obid, 'tp':tp})
			elif not can_edit:
				# the target is already banned (because of a previous report) - and you lack the permissions to edit their ban
				request.session["cannot_edit_ban"] = '1'
				request.session.modified = True
				return redirect("cull_content")
			elif not complaint_exists(obid, tp):
				# this report was handled by someone else already! (OR defender maliciously changed the obid)
				request.session["report_already_handled"] = '1'
				request.session.modified = True
				return redirect("cull_content")
			else:
				# kill_obj = True
				# report_types = ['3']
				# proceed with handling the report
				reporter_ids, time_now = get_complainer_ids(obid, tp), time.time()
				correct_complaints, incorrect_complaints, malicious_complaints = [], [], []
				reporter_id_and_report_type_dict = {}
				kill_obj, report_types = False, []
				for reporter_id in reporter_ids:
					report_type = request.POST.get("rt"+str(reporter_id),None)
					dec = request.POST.get(str(reporter_id),None)
					if dec == '1':
						# this content deserves to be killed since the complaints were deemed 'correct'
						kill_obj = True
						report_types.append(report_type)# if this ends up containing ONLY '9' or '10', factor in jealousy and take action accordingly
						correct_complaints.append(reporter_id)
					elif dec == '2':
						incorrect_complaints.append(reporter_id)
						reporter_id_and_report_type_dict[reporter_id] = report_type
					elif dec == '3':
						malicious_complaints.append(reporter_id)
						reporter_id_and_report_type_dict[reporter_id] = report_type
				# rate limit malicious complainer (i.e. someone who deliberately submitted a wrong complaint)
				rate_limit_complainer(malicious_complaints)
				
				# return everyone else's points. Needs to be sent a (user_id,payable) tuple list
				process_reporter_payables.delay(get_payables(correct_complaints+incorrect_complaints,obid,tp))
				
				# tweak reputation of reporters and log everything in case file:
				log_case_and_incr_reputation(correct_complaints,incorrect_complaints, malicious_complaints, time_now, obid, own_id, \
					retrieve_uname(own_id,decode=True), tp)
				
				# give defender their bonus score (but this will give away the fact that someone is a DEFENDER by visibly increasing their score by 15!)
				if REPORTED_CASE_COMPLETION_BONUS > 0:
					UserProfile.objects.filter(user_id=own_id).update(score=F('score')+REPORTED_CASE_COMPLETION_BONUS)
				
				# delete the report in the end (so that other defenders can't process a punishment again, nor does it appear in cull list)
				delete_complaint(obid, own_id, tp)

				# kill the object (obj_type includes 'img', 'tx', 'mf' and 'pf')
				if kill_obj:
					# i.e. at least one report was correct, so it's time to kill the object
					report_types = list(set(report_types))# this contains report indices obtained from score.py (e.g. '1', '3', or '9', etc.)
					cleanse_feeds = True
					#############################################################
					if tp in ('tx','img'):
						# for report in report_types:
						#     if report not in ('9','10'):
						#         # if offense solely of the type '9' or '10', do NOT cleanse feeds - just ban the person without changing anything in the feeds
						#         cleanse_feeds = True
						#         break
						context, template_name = initiate_content_submission_and_voting_ban(obj_owner_id=ooid, obj_id=obid, purl=img_url, caption=text, \
							obj_type=tp, owner_uname=retrieve_uname(ooid,decode=True), banner_id=own_id, origin='6', link_id='')
						if context:
							context['first_time_cull_list_judger'] = True if tutorial_unseen(user_id=own_id, which_tut='10', renew_lease=True) else False
							context['from_cull'] = '1'
							request.session['cleanse_feeds:'+obid+":"+tp+":"+str(own_id)] = '1' if cleanse_feeds else '0'
							request.session.modified = True
							return render(request, template_name, context)
						else:
							raise Http404("You are not an authorized defender")
					#############################################################
					elif tp == 'mf':
						context, template_name = initiate_mehfil_ban(obj_owner_id=ooid, obj_id=obid, topic=topic, rules=rules, obj_type=tp, \
							owner_uname=retrieve_uname(ooid,decode=True), banner_id=own_id,origin='')
						if context:
							context['first_time_cull_list_judger'] = True if tutorial_unseen(user_id=own_id, which_tut='10', renew_lease=True) else False
							context['from_cull'] = '1'
							request.session['cleanse_feeds:'+obid+":"+tp+":"+str(own_id)] = '1' if cleanse_feeds else '0'
							request.session.modified = True
							return render(request, template_name, context)
						else:
							raise Http404("You are not an authorized defender")
					#############################################################
					elif tp == 'pf':
						cleanse_feeds = True
						# initiate_profile_ban()
					#############################################################
					else:
						# obj_type (tp) doesn't make sense
						raise Http404("Unrecognized object type")
				else:
					# log the cancelled report for super admins to view in their global ledger
					reporter_uname_report_type_and_result = []# list of tuples of the sort [(repoter_uname, report_reason, report_result), ...]
					incorrect_and_malicious_unames_dict = retrieve_bulk_unames(reporter_id_and_report_type_dict.keys(),decode=True)
					for reporter_id, report_type in reporter_id_and_report_type_dict.iteritems():
						reporter_uname_report_type_and_result.append((incorrect_and_malicious_unames_dict[int(reporter_id)],TEXT_REPORT_PROMPT[report_type] \
							if tp == 'tx' else PHOTO_REPORT_PROMPT[report_type],'incorrect' if reporter_id in incorrect_complaints else 'malicious'))
					if tp == 'tx':
						# type is text
						payload = Link.objects.only('description').get(id=obid).description
					elif tp == 'img':
						# type is 'image'
						payload = Photo.objects.only('image_file').get(id=obid).image_file.url
					log_case_closure(defender_id=own_id, defender_uname=retrieve_uname(own_id,decode=True), obj_id=obid, obj_type=tp,\
						owner_uname=retrieve_uname(ooid,decode=True), reporter_data=reporter_uname_report_type_and_result, obj_data=payload, \
						time_now=time.time())
					#######################################################################################################
					# ensures defender gets the 'thank you' prompt when they eventually return to the cull screen
					request.session["report_judged"] = '1'
					request.session["cull_header"] = 'no_corrective_action'
					request.session.modified = True
					return redirect("cull_content")
		else:
			# rendering list of reported content to be culled (GET request)
			if 'page_object' in request.session and 'oblst' in request.session and 'total' in request.session:
				if request.session['page_object'] and request.session['oblst'] and request.session['total']:
					page_obj = request.session['page_object']
					object_list = request.session['oblst']
					total = request.session['total']
				else:
					complaints = get_content_complaints()
					page_num = request.GET.get('page', '1')
					page_obj = get_page_obj(page_num,complaints,ITEMS_PER_PAGE)
					detailed_complaints = get_complaint_details(page_obj.object_list)
					object_list = sorted(detailed_complaints,key=itemgetter('n'),reverse=True) #sorting by the number of complaints
					total = len(complaints)
				del request.session["page_object"]
				del request.session["oblst"]
				del request.session["total"]
			else:
				complaints = get_content_complaints()
				page_num = request.GET.get('page', '1')
				page_obj = get_page_obj(page_num,complaints,ITEMS_PER_PAGE)
				detailed_complaints = get_complaint_details(page_obj.object_list)
				object_list = sorted(detailed_complaints,key=itemgetter('n'),reverse=True) #sorting by the number of complaints
				total = len(complaints)
			own_id = str(own_id)
			cull_header = request.session.pop('cull_header','no_header')
			##########
			if not is_super_defender:
				# regular defenders are not permitted to change each others bans, hence 'lock' reports if report target was banned by someone else
				isolated_owner_ids = []
				for item in object_list:
					if item['tp'] in ('tx','img'):
						isolated_owner_ids.append(item['ooid'])
				unbannable_ids = are_ids_unbannable(defender_id=own_id, target_id_list=set(isolated_owner_ids))
				if unbannable_ids:
					for item in object_list:
						if item['ooid'] in unbannable_ids:
							item['cant_ban'] = True
			##########
			context = {'complaints':object_list, 'instr_unseen':tutorial_unseen(user_id=own_id, which_tut='8', renew_lease=True),\
			'total':total, 'already_handled':True if request.session.pop("report_already_handled",None) == '1' else False,\
			'force_into_list':True if request.session.pop('report_already_exists',None) == '1' else False, \
			'report_judged':True if request.session.pop('report_judged',None) == '1' else False, cull_header:True , \
			'cannot_edit':True if request.session.pop('cannot_edit_ban',None) == '1' else False, 'page':page_obj, \
			'orig':request.session.pop('redirect_orig'+own_id,None), 'lid':request.session.pop('redirect_lid'+own_id,None),\
			'oun':request.session.pop('redirect_oun'+own_id,None), 'obid':request.session.pop('redirect_obid'+own_id,None),\
			'purl':request.session.pop('redirect_purl'+own_id,None), 'ooid':request.session.pop('redirect_ooid'+own_id,None),\
			'obj_type':request.session.pop('redirect_obj_type'+own_id,None), 'cap':request.session.pop('redirect_cap'+own_id,None),\
			'from_cull':request.session.pop("redirect_from_cull"+own_id,None) }
			return render(request,'judgement/content_complaints.html',context)
	else:
		raise Http404("You are not an authorized defender")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def cull_content_post(request):
	"""
	Redirects to 'cull_content' and loads the required variables in session
	"""
	obid = request.POST.get("obid",None)
	purl = request.POST.get("purl",None)
	oun = request.POST.get("oun",None)
	ooid = request.POST.get("ooid",None)
	orig = request.POST.get("orig",None)
	lid = request.POST.get("lid",None)
	obj_type = request.POST.get("obj_type",None)
	cap = request.POST.get("cap",None)
	from_cull = request.POST.get("from_cull",None)
	own_id = str(request.user.id)
	request.session["redirect_orig"+own_id] = orig
	request.session["redirect_oun"+own_id] = oun
	request.session["redirect_lid"+own_id] = lid
	request.session["redirect_obid"+own_id] = obid
	request.session["redirect_purl"+own_id] = purl
	request.session["redirect_ooid"+own_id] = ooid
	request.session["redirect_obj_type"+own_id] = obj_type
	request.session["redirect_cap"+own_id] = cap
	request.session["redirect_from_cull"+own_id] = from_cull
	request.session.modified = True
	return redirect("cull_content")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def voting_ban_defender_help(request):
	"""
	Displays helpful instructions to defenders who want to ban malicious voters

	These intructions are ever-present via a navbar appearing at the top of points summary of items currently being voted on
	"""
	if request.method == "POST":
		own_id = request.user.id
		if in_defenders(own_id):
			vote_score = request.POST.get("vsc",None)
			is_pht = request.POST.get("is_pht",None)
			origin = request.POST.get("orig",None)
			obj_id = request.POST.get("obid",None)
			return render(request,"judgement/voting_ban_defender_help.html",{'is_pht':is_pht,'orig':origin,'obid':obj_id,'vsc':vote_score})
		else:
			# not authorized to see this 'help' page
			return redirect("missing_page")
	else:
		# not a POST request
		return redirect("home")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def judge_content_voters(request):
	"""
	Handles banning of voters on content

	It's a 2-screen flow, i.e. the banner has to go through 2 screens:
	Screen 1) Decide which voters to ban and how long to ban them for
	Screen 2) Give a textual reason visible to all the ban target(s)
	"""
	if request.method == "POST":
		own_id = request.user.id
		if in_defenders(own_id):
			ban_reason_given = request.POST.get("rsn",'')# gotten from Screen 2
			target_ids = request.POST.getlist("tids",[])# gotten from Screen 1
			orig = request.POST.get("orig",None)
			oun = request.POST.get("oun",None)
			lid = request.POST.get("lid",None)
			obid = request.POST.get("obid",None)
			from_cull = request.POST.get("from_cull",None)
			sin = 'bad_voting'
			##############################################################################################################
			if ban_reason_given == '1':
				# final screen: we have received a ban reason - now impose ban
				form = DefenderBlockingReasonForm(request.POST)
				if form.is_valid():
					reason = form.cleaned_data.get("text")
					data = retrieve_temporary_saved_content_details(own_id)
					if data:
						tp, oun, obj_id, saved_sin = data['tp'], data['oun'], data['obid'], data['sin']
						delete_temporarily_saved_content_data.delay(own_id)
						if saved_sin != sin:
							# tinkering has occurred, abort:
							if from_cull == '1':
								request.session["report_judged"] = '1'
								request.session["cull_header"] = 'temp_data_missing'
								request.session.modified = True
								return redirect("cull_content")
							else:
								own_id = str(own_id)
								request.session["redirect_reason"+own_id] = 'temp_data_missing'
								request.session["redirect_orig"+own_id] = orig
								request.session["redirect_oun"+own_id] = oun
								request.session["redirect_lid"+own_id] = lid
								request.session["redirect_obid"+own_id] = obj_id
								request.session.modified = True
								return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
						elif tp == 'tx':
							try:
								obj_owner_id = Link.objects.only('submitter').get(id=obj_id).submitter_id
								reference = data['cap']
							except Link.DoesNotExist:
								# cannot ban item that doesnt exist
								raise Http404("Object does not exist")
						else:
							try:
								obj_owner_id = Photo.objects.only('owner').get(id=obj_id).owner_id
								reference = data['purl']
							except Photo.DoesNotExist:
								# cannot ban item that doesnt exist
								raise Http404("Object does not exist")
						target_ids = data['tids']
						voting_ban_dur = data['vdur']
						own_id = str(own_id)
						if own_id in target_ids:
							# cannot ban self - user probably used 'inspect element' to rig the form against themselves
							if from_cull == '1':
								request.session["report_judged"] = '1'
								request.session["cull_header"] = 'cannot_ban_self'
								request.session.modified = True
								return redirect("cull_content")
							else:
								request.session["redirect_reason"+own_id] = 'cannot_ban_self'
								request.session["redirect_orig"+own_id] = orig
								request.session["redirect_oun"+own_id] = oun
								request.session["redirect_lid"+own_id] = lid
								request.session["redirect_obid"+own_id] = obj_id
								request.session.modified = True
								return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
						elif data['ooid'] != str(obj_owner_id):
							# data is corrupted, maybe it was tinkered with? (just an additional check)
							if from_cull == '1':
								request.session["report_judged"] = '1'
								request.session["cull_header"] = 'temp_data_missing'
								request.session.modified = True
								return redirect("cull_content")
							else:
								request.session["redirect_reason"+own_id] = 'temp_data_missing'
								request.session["redirect_orig"+own_id] = orig
								request.session["redirect_oun"+own_id] = oun
								request.session["redirect_lid"+own_id] = lid
								request.session["redirect_obid"+own_id] = obj_id
								request.session.modified = True
								return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
						else:
							# proceed
							unbanned_ids, banned_ids = filter_ids_with_content_and_voting_ban(target_ids)
							if unbanned_ids and banned_ids:
								# ban the unbanned ones, decline the banned ones
								unbanned_usernames_dictionary = retrieve_bulk_unames(unbanned_ids,decode=True)
								banned_usernames_dictionary = retrieve_bulk_unames(banned_ids,decode=True)
								target_usernames = unbanned_usernames_dictionary.values()#list of values
								already_banned_usernames = banned_usernames_dictionary.values()
								ban_time = impose_content_and_voting_ban(target_user_ids=unbanned_ids, target_usernames=target_usernames,ban_duration=voting_ban_dur, \
									current_time=time.time(), banner_uname=retrieve_uname(own_id, decode=True), obj_type=tp, obj_id=obj_id, obj_owner_uname=oun, \
									obj_owner_id=obj_owner_id, ban_reason=reason, reference=reference, banner_id=own_id, sin=saved_sin)
								if ban_time:
									if from_cull == '1':
										request.session["report_judged"] = '1'
										request.session["cull_header"] = 'multi_ban_imposed'
										request.session.modified = True
										return redirect("cull_content")
									else:
										request.session["redirect_reason"+own_id] = 'multi_ban_imposed'
										request.session["redirect_orig"+own_id] = data['orig']
										request.session["redirect_lid"+own_id] = data['lid']
										request.session["redirect_obid"+own_id] = obj_id
										request.session["redirect_oun"+own_id] = oun
										request.session["redirect_ban_time"+own_id] = ban_time
										request.session["redirect_tunm"+own_id] = json.dumps(target_usernames)
										request.session["redirect_iun"+own_id] = json.dumps(already_banned_usernames)
										request.session.modified = True
										return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
								else:
									if from_cull == '1':
										request.session["report_judged"] = '1'
										request.session["cull_header"] = 'temp_data_missing'
										request.session.modified = True
										return redirect("cull_content")
									else:
										request.session["redirect_reason"+own_id] = 'temp_data_missing'
										request.session["redirect_orig"+own_id] = data['orig']
										request.session["redirect_lid"+own_id] = data['lid']
										request.session["redirect_obid"+own_id] = obj_id
										request.session["redirect_oun"+own_id] = oun
										request.session.modified = True
										return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
							elif unbanned_ids:
								# everyone's status is 'unbanned' - so ban them
								usernames_dictionary = retrieve_bulk_unames(unbanned_ids,decode=True)
								target_usernames = usernames_dictionary.values()
								ban_time = impose_content_and_voting_ban(target_user_ids=unbanned_ids, target_usernames=target_usernames,ban_duration=voting_ban_dur, \
									current_time=time.time(), banner_uname=retrieve_uname(own_id, decode=True), obj_type=tp, obj_id=obj_id, obj_owner_uname=oun, \
									obj_owner_id=obj_owner_id, ban_reason=reason, reference=reference, banner_id=own_id, sin=saved_sin)
								if ban_time:
									if from_cull == '1':
										request.session["report_judged"] = '1'
										request.session["cull_header"] = 'multi_ban_imposed'
										request.session.modified = True
										return redirect("cull_content")
									else:
										request.session["redirect_reason"+own_id] = 'multi_ban_imposed'
										request.session["redirect_orig"+own_id] = data['orig']
										request.session["redirect_lid"+own_id] = data['lid']
										request.session["redirect_obid"+own_id] = obj_id
										request.session["redirect_oun"+own_id] = oun
										request.session["redirect_ban_time"+own_id] = ban_time
										request.session["redirect_tunm"+own_id] = json.dumps(target_usernames)
										request.session.modified = True
										return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
								else:
									# something unforeseen went wrong
									if from_cull == '1':
										request.session["report_judged"] = '1'
										request.session["cull_header"] = 'temp_data_missing'
										request.session.modified = True
										return redirect("cull_content")
									else:
										request.session["redirect_reason"+own_id] = 'temp_data_missing'
										request.session["redirect_orig"+own_id] = data['orig']
										request.session["redirect_oun"+own_id] = oun
										request.session["redirect_lid"+own_id] = data['lid']
										request.session["redirect_obid"+own_id] = obj_id
										request.session.modified = True
										return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
							elif banned_ids:
								# everyone is banned - can't ban anyone
								if from_cull == '1':
									request.session["report_judged"] = '1'
									request.session["cull_header"] = 'multi_already_banned'
									request.session.modified = True
									return redirect("cull_content")
								else:
									request.session["redirect_reason"+own_id] = 'multi_already_banned'
									request.session["redirect_orig"+own_id] = orig
									request.session["redirect_oun"+own_id] = oun
									request.session["redirect_lid"+own_id] = lid
									request.session["redirect_obid"+own_id] = obj_id
									request.session.modified = True
									return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
							else:
								# both lists are empty, something unforeseen went wrong!
								if from_cull == '1':
									request.session["report_judged"] = '1'
									request.session["cull_header"] = 'temp_data_missing'
									request.session.modified = True
									return redirect("cull_content")
								else:
									own_id = str(own_id)
									request.session["redirect_reason"+own_id] = 'temp_data_missing'
									request.session["redirect_orig"+own_id] = orig
									request.session["redirect_oun"+own_id] = oun
									request.session["redirect_lid"+own_id] = lid
									request.session["redirect_obid"+own_id] = obj_id
									request.session.modified = True
									return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
					else:
						# data has expired
						if from_cull == '1':
							request.session["report_judged"] = '1'
							request.session["cull_header"] = 'temp_data_missing'
							request.session.modified = True
							return redirect("cull_content")
						else:
							own_id = str(own_id)
							request.session["redirect_reason"+own_id] = 'temp_data_missing'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = obid
							request.session.modified = True
							return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
				else:
					# form is invalid
					purl = request.POST.get("purl",None)
					cap = request.POST.get("cap",None)
					tp = request.POST.get("tp",None)
					is_pht = request.POST.get("pht",None)
					net_votes = request.POST.get("nv",None)
					return render(request,"judgement/set_content_submission_and_voting_ban_reason.html",{'oun':oun,'purl':purl,\
						'cap':cap,'form':form,'lid':lid,'orig':orig,'obid':obid,'previous_reasons':get_defenders_ledger(own_id),\
						'tp':tp,'sin':sin,'pht':is_pht,'nv':net_votes,'no_hyperlinks':True, 'from_cull':from_cull})
			##############################################################################################################
			elif target_ids:
				# ban all targets, their sin being 'bad_voting'
				voting_ban_dur = request.POST.get('vdur','')
				if voting_ban_dur in ('1','2','3','4','5','6'):
					is_pht = request.POST.get("pht",None)
					net_votes = request.POST.get("nv",None)
					ooid = request.POST.get("ooid",None)
					purl = request.POST.get("purl",None)
					cap = request.POST.get("cap",None)
					tp = request.POST.get("tp",None)
					saved = temporarily_save_content_details(obj_id=obid, owner_id=ooid, photo_url=purl, caption=cap, obj_type=tp, origin=orig, \
						owner_uname=oun, link_id=lid, banner_id=own_id, sin=sin, target_ids=target_ids, voting_ban_dur=voting_ban_dur)
					if saved:
						# directly jump to the 'reason' template (no need to go to the 'duration' template - it's already been set)
						return render(request,"judgement/set_content_submission_and_voting_ban_reason.html",{'oun':oun,'purl':purl,'cap':cap,\
							'tp':tp,'form':DefenderBlockingReasonForm(),'obid':obid, 'previous_reasons':get_defenders_ledger(own_id),'sin':sin,\
							'pht':is_pht,'nv':net_votes,'no_hyperlinks':True,'lid':lid,'orig':orig,'from_cull':from_cull})
					else:
						# something unforeseen went wrong
						if from_cull == '1':
							request.session["report_judged"] = '1'
							request.session["cull_header"] = 'temp_data_missing'
							request.session.modified = True
							return redirect("cull_content")
						else:
							own_id = str(own_id)
							request.session["redirect_reason"+own_id] = 'temp_data_missing'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = obid
							request.session.modified = True
							return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
				else:
					# probably canceled the decision to levy a voting ban - revert
					delete_temporarily_saved_content_data.delay(own_id)
					if from_cull == '1':
						request.session["report_judged"] = '1'
						request.session["cull_header"] = 'no_corrective_action'
						request.session.modified = True
						return redirect("cull_content")
					else:
						return return_to_content(request,orig,obid,lid,oun)
			##############################################################################################################
			else:
				# no targeted data, just revert to post (e.g. if the entire list was already banned and there was no 'target_id' or 'target_ids')
				return return_to_content(request,orig,obid,lid,oun)
		else:
			# not a defender
			raise Http404("You are not an authorized defender")
	else:
		# not a POST request
		return redirect("missing_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def judge_content_submitters(request):
	"""
	Handles banning of submitters of content ('tx' or 'img')

	It's a 3-screen flow, i.e. the banner has to go through 3 screens:
	Screen 1) Decide whether to ban a piece of content (or return)
	Screen 2) Decide what duration the ban is to last
	Screen 3) Give a textual reason visible to the ban target
	"""
	if request.method == "POST":
		own_id = request.user.id
		if in_defenders(own_id):
			ban_reason = request.POST.get("rsn",'')# gotten from Screen 3
			duration = request.POST.get("dur",'')# gotten from Screen 2
			decision = request.POST.get("dec",'')# gotten from Screen 1
			orig = request.POST.get("orig",None)
			oun = request.POST.get("oun",None)
			lid = request.POST.get("lid",None)
			obid = request.POST.get("obid",None)
			from_cull = request.POST.get("from_cull",None)
			sin = 'bad_submission'
			##############################################################################################################
			if ban_reason == '1':
				# Third screen: final screen, we have received a ban reason - now impose the ban after performing some sanity checks
				form = DefenderBlockingReasonForm(request.POST)
				if form.is_valid():
					own_id = str(own_id)
					reason = form.cleaned_data.get("text")
					data = retrieve_temporary_saved_content_details(own_id)
					if data:
						tp, oun, obj_id, saved_sin = data['tp'], data['oun'], data['obid'], data['sin']
						delete_temporarily_saved_content_data.delay(own_id)
						if saved_sin != sin:
							# tinkering has occurred, abort:
							if from_cull == '1':
								request.session["report_judged"] = '1'
								request.session["cull_header"] = 'temp_data_missing'
								request.session.modified = True
								return redirect("cull_content")
							else:
								request.session["redirect_reason"+own_id] = 'temp_data_missing'
								request.session["redirect_orig"+own_id] = orig
								request.session["redirect_oun"+own_id] = oun
								request.session["redirect_lid"+own_id] = lid
								request.session["redirect_obid"+own_id] = obj_id
								request.session.modified = True
								return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
						elif tp == 'tx':
							try:
								obj_owner_id = Link.objects.only('submitter').get(id=obj_id).submitter_id
								reference = data['cap']
							except Link.DoesNotExist:
								# cannot ban item that doesnt exist
								raise Http404("Object does not exist")
						else:
							try:
								obj_owner_id = Photo.objects.only('owner').get(id=obj_id).owner_id
								reference = data['purl']
							except Photo.DoesNotExist:
								# cannot ban item that doesnt exist
								raise Http404("Object does not exist")
						#############################################################################
						target_id = data['tid']
						obj_owner_id = str(obj_owner_id)
						if obj_owner_id == own_id:
							# cannot ban self
							if from_cull == '1':
								# this block should never fire, since cull-list stops defender from deciding own reports very early
								request.session["report_judged"] = '1'
								request.session["cull_header"] = 'cannot_ban_self'
								request.session.modified = True
								return redirect("cull_content")
							else:
								request.session["redirect_reason"+own_id] = 'cannot_ban_self'
								request.session["redirect_orig"+own_id] = orig
								request.session["redirect_oun"+own_id] = oun
								request.session["redirect_lid"+own_id] = lid
								request.session["redirect_obid"+own_id] = obj_id
								request.session.modified = True
								return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
						elif data['ooid'] != obj_owner_id:
							# data is corrupted
							if from_cull == '1':
								# this block should never fire, since cull-list stops defender from deciding own reports very early
								request.session["report_judged"] = '1'
								request.session["cull_header"] = 'temp_data_missing'
								request.session.modified = True
								return redirect("cull_content")
							else:
								request.session["redirect_reason"+own_id] = 'temp_data_missing'
								request.session["redirect_orig"+own_id] = orig
								request.session["redirect_oun"+own_id] = oun
								request.session["redirect_lid"+own_id] = lid
								request.session["redirect_obid"+own_id] = obj_id
								request.session.modified = True
								return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
						else: 
							already_banned, time_remaining = check_content_and_voting_ban(obj_owner_id)
							if already_banned:
								# target user got banned while defender was going through the various screens
								if from_cull == '1':
									request.session["report_judged"] = '1'
									request.session["cull_header"] = 'already_banned'
									request.session.modified = True
									return redirect("cull_content")
								else:
									request.session["redirect_reason"+own_id] = 'already_banned'
									request.session["redirect_orig"+own_id] = orig
									request.session["redirect_oun"+own_id] = oun
									request.session["redirect_lid"+own_id] = lid
									request.session["redirect_obid"+own_id] = obj_id
									request.session["redirect_time_remaining"+own_id] = time_remaining
									request.session.modified = True
									return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
							else:
								# impose the ban on the bad 'submitter'!
								ban_time = impose_content_and_voting_ban(target_user_ids=[obj_owner_id], target_usernames=[oun],ban_duration=data['dur'], \
									current_time=time.time(), banner_uname=retrieve_uname(own_id, decode=True), obj_type=tp, obj_id=obj_id, obj_owner_uname=oun, \
									obj_owner_id=obj_owner_id, ban_reason=reason, reference=reference, banner_id=own_id, sin=saved_sin)
								if ban_time:
									# since it's a bad content submission sin, cut votes from the target submission as well
									if tp  == 'tx':
										is_pht = '0'
										Link.objects.filter(id=obj_id).update(net_votes=-100)#ensuring the text object will remain censored even after unbanning
									else:
										is_pht = '1'
										Photo.objects.filter(id=obj_id).update(vote_score=-100)#ensuring the photo object will remain censored even after unbanning
									if from_cull == '1':
										# Do not cleanse_feeds when report category is '9' or '10' (and defender originates from cull_list)
										remove_target_users_posts_from_all_feeds.delay(target_user_id=obj_owner_id, post_type=tp, \
										cleanse_feeds=request.session.pop('cleanse_feeds:'+obid+":"+tp+":"+own_id,'1'))# tp is 'img' or 'tx'
									else:
										remove_target_users_posts_from_all_feeds.delay(target_user_id=obj_owner_id, post_type=tp, cleanse_feeds='1')# tp is 'img' or 'tx'
									#####################################################################
									vote_id_and_values, net_votes = get_votes(obj_id,obj_type=tp, with_net_score=True)
									if vote_id_and_values:
										# if bannable voters exist (i.e. voting is open and there are actual votes), call forth vote banning
										number_of_voters = len(vote_id_and_values)
										voter_id_names_status_and_votes = get_usernames(vote_id_and_values, ban_status=True)
										context = {'obj_type':tp,'cap':data.get('cap',''),'oun':oun,'purl':data.get('purl',''),'pht':is_pht,\
										'obj_id':obj_id,'ooid':obj_owner_id,'voter_id_names_status_and_votes':voter_id_names_status_and_votes,\
										'first_time_voting_judger':tutorial_unseen(user_id=own_id, which_tut='12', renew_lease=True),\
										'orig':orig,'lid':data.get('lid',''),'nv':net_votes,'own_id':own_id,'from_cull':from_cull}
										return render(request,'judgement/ban_content_voters.html',context)
									else:
										# redirect to 'successfully banned' page (reconfigure this when originating from 'cull' list)
										if from_cull == '1':
											request.session["report_judged"] = '1'
											request.session["cull_header"] = 'ban_imposed'
											request.session.modified = True
											return redirect("cull_content")
										else:
											request.session["redirect_reason"+own_id] = 'ban_imposed'
											request.session["redirect_orig"+own_id] = data['orig']
											request.session["redirect_oun"+own_id] = oun
											request.session["redirect_lid"+own_id] = data['lid']
											request.session["redirect_obid"+own_id] = obj_id
											request.session["redirect_ban_time"+own_id] = ban_time
											request.session.modified = True
											return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
								else:
									# due to some unforeseen error
									if from_cull == '1':
										request.session["report_judged"] = '1'
										request.session["cull_header"] = 'temp_data_missing'
										request.session.modified = True
										return redirect("cull_content")
									else:
										request.session["redirect_reason"+own_id] = 'temp_data_missing'
										request.session["redirect_orig"+own_id] = data['orig']
										request.session["redirect_oun"+own_id] = oun
										request.session["redirect_lid"+own_id] = data['lid']
										request.session["redirect_obid"+own_id] = obj_id
										request.session.modified = True
										return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
					else:
						# data has expired
						if from_cull == '1':
							request.session["report_judged"] = '1'
							request.session["cull_header"] = 'temp_data_missing'
							request.session.modified = True
							return redirect("cull_content")
						else:
							request.session["redirect_reason"+own_id] = 'temp_data_missing'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = obid
							request.session.modified = True
							return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
				else:
					# form is invalid
					purl = request.POST.get("purl",None)
					cap = request.POST.get("cap",None)
					tp = request.POST.get("tp",None)
					is_pht = request.POST.get("pht",None)
					net_votes = request.POST.get("nv",None)
					return render(request,"judgement/set_content_submission_and_voting_ban_reason.html",{'oun':oun,'purl':purl,\
						'cap':cap,'form':form,'lid':lid,'orig':orig,'obid':obid,'previous_reasons':get_defenders_ledger(own_id),\
						'tp':tp,'sin':sin,'pht':is_pht,'nv':net_votes,'no_hyperlinks':True,'from_cull':from_cull})
			##############################################################################################################
			elif duration in ('1','2','3','4','5','6'):
				# Second screen: the duration screen, where length of punishment is set
				enriched, data = enrich_temporarily_saved_content_details_with_duration(own_id, duration, return_credentials=True)
				if enriched:
					# take to the reason screen now
					return render(request,"judgement/set_content_submission_and_voting_ban_reason.html",{'oun':data['oun'],'purl':data['purl'],\
						'cap':data['cap'],'form':DefenderBlockingReasonForm(),'lid':data['lid'],'orig':data['orig'],'obid':data['obid'],\
						'tp':data['tp'],'previous_reasons':get_defenders_ledger(own_id),'sin':data['sin'],'no_hyperlinks':True, \
						'from_cull':from_cull})
				else:
					# maybe the person was too late - the temporarily saved data could not be retrieved - just show user an error screen
					if from_cull == '1':
						request.session["report_judged"] = '1'
						request.session["cull_header"] = 'temp_data_missing'
						request.session.modified = True
						return redirect("cull_content")
					else:
						own_id = str(own_id)
						request.session["redirect_reason"+own_id] = 'temp_data_missing'
						request.session["redirect_orig"+own_id] = orig
						request.session["redirect_oun"+own_id] = oun
						request.session["redirect_lid"+own_id] = lid
						request.session["redirect_obid"+own_id] = obid
						request.session.modified = True
						return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
			##############################################################################################################
			elif decision == '1':
				# First screen: decide whether to ban a user's content
				target_id = request.POST.get("tid",None)
				if target_id:
					# target_id exists - i.e. the defender has decided to ban target - proceed
					ooid = request.POST.get("ooid",None)
					purl = request.POST.get("purl",None)
					cap = request.POST.get("cap",None)
					tp = request.POST.get("tp",None)
					offender_score = UserProfile.objects.only('score').get(id=target_id).score
					saved = temporarily_save_content_details(obj_id=obid, owner_id=ooid, photo_url=purl, caption=cap, obj_type=tp, origin=orig, \
						owner_uname=oun, link_id=lid, banner_id=own_id, sin=sin, target_id=ooid)
					if saved:
						# proceed to second screen - the 'duration' template
						return render(request,'judgement/set_content_submission_and_voting_ban_duration.html',{'oun':oun,'purl':purl,'cap':cap,'tp':tp,\
							'lid':lid,'orig':orig,'obid':obid,'from_cull':from_cull,'offender_score':offender_score})
					else:
						# something unforeseen went wrong
						if from_cull == '1':
							request.session["report_judged"] = '1'
							request.session["cull_header"] = 'temp_data_missing'
							request.session.modified = True
							return redirect("cull_content")
						else:
							own_id = str(own_id)
							request.session["redirect_reason"+own_id] = 'temp_data_missing'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = obid
							request.session.modified = True
				else:
					# no targeted data exists (error?), just revert to post
					delete_temporarily_saved_content_data.delay(own_id)
					if from_cull == '1':
						request.session["report_judged"] = '1'
						request.session["cull_header"] = 'temp_data_missing'
						request.session.modified = True
						return redirect("cull_content")
					else:
						return return_to_content(request,orig,obid,lid,oun)
			##############################################################################################################
			else:
				# decided not to levy ban - redirect back (and purge temporarily saved data)
				delete_temporarily_saved_content_data.delay(own_id)
				return return_to_content(request,orig,obid,lid,oun)
		else:
			# not a defender
			raise Http404("You are not an authorized defender")
	else:
		# not a POST request
		return redirect("missing_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def edit_content_submission_and_voting_ban(request):
	"""
	Handles the entire funnel for editing (or removing) the ban of a user already slapped with a content_submission_and_voting_ban
	
	It's a 3-screen flow, i.e. the ban editor has to go through 3 screens:
	Screen 1) Decide whether "Change" ban time, "Remove" ban or "Do nothing" (or if you don't have the permission to edit, just return)
	Screen 2) If Change ban time (or remove ban) was selected, set a new ban time (for an existing ban)
	Screen 3) Give a textual reason visible to the original creator of the now edited (or removed) ban
	
	This also updates relevant banning_activity for super admin
	"""
	own_id = request.user.id
	if request.method=="POST":
		is_defender = in_defenders(own_id)
		if is_defender:
			edit_reason = request.POST.get("ersn",None)#Screen 3: Providing reason for the change (or removal)
			dur_dec = request.POST.get("ddec",None)# Screen 2: deciding new duration of ban (get here via "Change")
			edit_dec = request.POST.get("edec",None)# Screen 1: deciding whether to "Change", "Remove", or "Do nothing" (if no perms to edit, just return)
			origin = request.POST.get("orig",None)
			obj_id = request.POST.get("obid",None)
			owner_uname = request.POST.get("oun",None)
			link_id = request.POST.get("lid",None)# if it exists
			from_cull = request.POST.get("from_cull",None)# if it exists
			##############################################################################################################
			if edit_reason == '1':
				# reason for editing is now provided - process it and do what's necessary
				new_ban_duration = request.session.get("ban_editing_by"+str(own_id),None)
				if new_ban_duration in ('1','2','3','4','5','6','remove'):
					data = retrieve_temporary_saved_content_details(own_id)
					unbanned_tid = data['tid']
					is_banned, time_remaining, ban_detail = check_content_and_voting_ban(unbanned_tid, with_details=True)
					if is_banned:
						can_edit, reason = can_edit_ban(own_id, ban_detail['did'],unbanned_tid)
						if reason == 'not_defender':
							raise Http404("You are not an authorized defender")
						else:
							form = DefenderBlockingReasonForm(request.POST)
							if form.is_valid():
								if can_edit:
									reason = form.cleaned_data.get("text")
									####### cleansing saved data #######
									request.session.pop("ban_editing_by"+str(own_id),None)
									delete_temporarily_saved_content_data.delay(own_id)
									####################################
									usernames_dictionary = retrieve_bulk_unames([own_id,unbanned_tid],decode=True)
									# change ban ('remove 'if new_ban_duration == 'remove', otherwise 'change' according to encoded number)
									if new_ban_duration == 'remove':
										# remove ban and include action in defender's own banning activity
										otr = remove_content_and_voting_ban(target_user_id=unbanned_tid, target_username=usernames_dictionary[int(unbanned_tid)], \
											removal_reason=reason, time_now=time.time(), editor_id=own_id, editor_uname=usernames_dictionary[own_id])
										if otr == 'key_does_not_exist':
											if from_cull == '1':
												request.session["report_judged"] = '1'
												request.session["cull_header"] = 'do_nothing'
												request.session.modified = True
												return redirect("cull_content")
											else:
												return return_to_content(request,origin,obj_id,link_id,owner_uname)
										else:
											if from_cull == '1':
												# shows a prompt within 'cull' page
												request.session["report_judged"] = '1'
												request.session["cull_header"] = 'ban_removed'
												request.session.modified = True
												return redirect("cull_content")
											else:
												own_id = str(own_id)
												request.session["redirect_reason"+own_id] = 'ban_removed'
												request.session["redirect_orig"+own_id] = origin
												request.session["redirect_oun"+own_id] = owner_uname
												request.session["redirect_lid"+own_id] = link_id
												request.session["redirect_obid"+own_id] = obj_id
												request.session["redirect_otr"+own_id] = otr
												request.session.modified = True
												return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
									else:
										# change ban time and include action in defender's own banning activity
										ntr, otr = edit_content_and_voting_ban(target_user_id=unbanned_tid, target_username=usernames_dictionary[int(unbanned_tid)],\
											edit_reason=reason, new_dur=new_ban_duration, time_now=time.time(), editor_id=own_id, editor_uname=usernames_dictionary[own_id])
										if otr == 'key_does_not_exist':
											if from_cull == '1':
												request.session["report_judged"] = '1'
												request.session["cull_header"] = 'do_nothing'
												request.session.modified = True
												return redirect("cull_content")
											else:
												return return_to_content(request,origin,obj_id,link_id,owner_uname)
										else:
											#######################################
											tp = data['tp']
											vote_id_and_values, net_votes = get_votes(obj_id,obj_type=tp, with_net_score=True)
											if vote_id_and_values:
												# if bannable voters exist (i.e. voting is open and there are actual votes), call forth vote banning
												number_of_voters = len(vote_id_and_values)
												voter_id_names_status_and_votes = get_usernames(vote_id_and_values, ban_status=True)
												context = {'obj_type':tp,'cap':data['cap'],'oun':data['oun'],'purl':data['purl'],'pht':'0' if tp == 'tx' else '1',\
												'obj_id':obj_id,'ooid':data['ooid'],'voter_id_names_status_and_votes':voter_id_names_status_and_votes,\
												'first_time_voting_judger':tutorial_unseen(user_id=own_id, which_tut='12', renew_lease=True),\
												'orig':origin,'lid':link_id,'nv':net_votes,'own_id':own_id,'from_cull':from_cull}
												return render(request,'judgement/ban_content_voters.html',context)
											else:
												if from_cull == '1':
													# shows a prompt within 'cull' page
													request.session["report_judged"] = '1'
													request.session["cull_header"] = 'ban_edited'
													request.session.modified = True
													return redirect("cull_content")
												else:
													own_id = str(own_id)
													request.session["redirect_reason"+own_id] = 'ban_edited'
													request.session["redirect_orig"+own_id] = origin
													request.session["redirect_oun"+own_id] = owner_uname
													request.session["redirect_lid"+own_id] = link_id
													request.session["redirect_obid"+own_id] = obj_id
													request.session["redirect_ntr"+own_id] = ntr
													request.session["redirect_otr"+own_id] = otr
													request.session.modified = True
													return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
								else:
									# not own ban, or is not super (and super changed the ban)
									delete_temporarily_saved_content_data.delay(own_id)
									if from_cull == '1':
										# shows a prompt within 'cull' page
										request.session["report_judged"] = '1'
										request.session["cull_header"] = reason
										request.session.modified = True
										return redirect("cull_content")
									else:
										own_id = str(own_id)
										request.session.pop("ban_editing_by"+own_id,None)
										request.session["redirect_reason"+own_id] = reason
										request.session["redirect_orig"+own_id] = origin
										request.session["redirect_oun"+own_id] = owner_uname
										request.session["redirect_lid"+own_id] = link_id
										request.session["redirect_obid"+own_id] = obj_id
										request.session.modified = True
										return redirect("judge_not_and_red")#judgement modules notify_and_redirect function
							else:
								# form is invalid - render again (with error)
								obj_type = request.POST.get("tp",None)
								caption = request.POST.get("cap",None)
								photo_url = request.POST.get("purl",None)
								to_remove = True if new_ban_duration == 'remove' else False
								own_ban = True if ban_detail['did']==str(own_id) else False
								if is_banned:
									return render(request,"judgement/provide_reason_for_editing_content_submission_and_voting_ban.html",{'form':form, \
										'removing_ban':to_remove,'previous_reasons':get_defenders_ledger(own_id),'no_hyperlinks':True, 'orig':origin, \
										'prev_ban_by_self':own_ban,'obid':obj_id,'oun':owner_uname,'lid':link_id,'purl':photo_url,'cap':caption, \
										'tp':obj_type,'ooid':unbanned_tid,'from_cull':from_cull})
								else:
									# not banned any more
									delete_temporarily_saved_content_data.delay(own_id)
									request.session.pop("ban_editing_by"+str(own_id),None)
									if from_cull == '1':
										request.session["report_judged"] = '1'
										request.session["cull_header"] = 'do_nothing'
										request.session.modified = True
										return redirect("cull_content")
									else:
										return return_to_content(request,origin,obj_id,link_id,owner_uname)
									
					else:
						# no longer banned - probably time expired - thus can't 'edit' ban any more
						delete_temporarily_saved_content_data.delay(own_id)
						request.session.pop("ban_editing_by"+str(own_id),None)
						if from_cull == '1':
							request.session["report_judged"] = '1'
							request.session["cull_header"] = 'do_nothing'
							request.session.modified = True
							return redirect("cull_content")
						else:
							return return_to_content(request,origin,obj_id,link_id,owner_uname)
				else:
					# new duration data is not sane, abort
					delete_temporarily_saved_content_data.delay(own_id)
					request.session.pop("ban_editing_by"+str(own_id),None)
					if from_cull == '1':
						request.session["report_judged"] = '1'
						request.session["cull_header"] = 'do_nothing'
						request.session.modified = True
						return redirect("cull_content")
					else:
						return return_to_content(request,origin,obj_id,link_id,owner_uname)
			##############################################################################################################
			elif dur_dec == '1':
				# Processing the case where defender decided to "Change" ban time (for an existing ban)
				new_duration = request.POST.get("dur",None) 
				obj_type = request.POST.get("tp",None)
				if new_duration in ('1','2','3','4','5','6'):
					request.session["ban_editing_by"+str(own_id)] = new_duration
					request.session.modified = True
					obj_owner_id = request.POST.get("ooid",None)
					caption = request.POST.get("cap",None)
					photo_url = request.POST.get("purl",None)
					# ensure target is still banned, otherwise changing ban duration doesn't make sense
					is_banned, time_remaining, ban_detail = check_content_and_voting_ban(obj_owner_id, with_details=True)
					if is_banned:
						# now transport user to 'reason' screen
						return render(request,"judgement/provide_reason_for_editing_content_submission_and_voting_ban.html",{'cap':caption,'tp':obj_type, \
							'previous_reasons':get_defenders_ledger(own_id),'form':DefenderBlockingReasonForm(),'no_hyperlinks':True,'removing_ban':False,\
							'prev_ban_by_self':True if ban_detail['did']==str(own_id) else False,'obid':obj_id,'oun':owner_uname,'orig':origin,'lid':link_id,\
							'purl':photo_url,'ooid':obj_owner_id,'from_cull':from_cull})
					else:
						# this user isn't banned any more - revert
						delete_temporarily_saved_content_data.delay(own_id)
						if from_cull == '1':
							request.session["report_judged"] = '1'
							request.session["cull_header"] = 'do_nothing'
							request.session.modified = True
							return redirect("cull_content")
						else:
							return return_to_content(request,origin,obj_id,link_id,owner_uname)
				else:
					# lead defender back (they tinkered with the duration value?)
					delete_temporarily_saved_content_data.delay(own_id)
					if from_cull == '1':
						request.session["report_judged"] = '1'
						request.session["cull_header"] = 'do_nothing'
						request.session.modified = True
						return redirect("cull_content")
					else:
						return return_to_content(request,origin,obj_id,link_id,owner_uname)
			##############################################################################################################
			elif edit_dec in ('1','2'):
				# Processing input where defender decided "Change" or "Remove" the current ban
				obj_owner_id = request.POST.get("ooid",None)
				target_id = request.POST.get("tid",None)# should be same as obj_owner_id in this case
				photo_url = request.POST.get("purl",None)# if it exists
				caption = request.POST.get("cap",None)# if it exists
				obj_type = request.POST.get("tp",None)
				# ensure target is still banned, otherwise "Change" or "Remove" doesn't make sense
				is_banned, time_remaining, ban_detail = check_content_and_voting_ban(obj_owner_id, with_details=True)
				if is_banned:
					if edit_dec == '1':
						# "Remove" current ban entirely
						request.session["ban_editing_by"+str(own_id)] = 'remove'
						request.session.modified = True
						return render(request,"judgement/provide_reason_for_editing_content_submission_and_voting_ban.html",{'removing_ban':True,\
							'form':DefenderBlockingReasonForm(),'prev_ban_by_self':True if ban_detail['did']==str(own_id) else False,'obid':obj_id,\
							'oun':owner_uname,'no_hyperlinks':True,'orig':origin,'lid':link_id,'purl':photo_url,'cap':caption,'tp':obj_type, \
							'ooid':obj_owner_id,'previous_reasons':get_defenders_ledger(own_id),'from_cull':from_cull})
					else:
						# "Change" current ban's timing
						return render(request,"judgement/edit_content_submission_and_voting_ban_duration.html",{'obid':obj_id,'oun':owner_uname,\
							'orig':origin,'lid':link_id,'cap':caption,'purl':photo_url,'ban_data':ban_detail, 'time_remaining':time_remaining, \
							'ooid':obj_owner_id,'tp':obj_type,'target_uname':retrieve_uname(obj_owner_id,decode=True),'from_cull':from_cull})
				else:
					# this user is not banned any more - revert
					delete_temporarily_saved_content_data.delay(own_id)
					if from_cull == '1':
						request.session["report_judged"] = '1'
						request.session["cull_header"] = 'do_nothing'
						request.session.modified = True
						return redirect("cull_content")
					else:
						return return_to_content(request,origin,obj_id,link_id,owner_uname)
			##############################################################################################################
			else:
				# return the user to origin
				request.session.pop("ban_editing_by"+str(own_id),None)
				delete_temporarily_saved_content_data.delay(own_id)
				if from_cull == '1':
					request.session["report_judged"] = '1'
					request.session["cull_header"] = 'no_corrective_action'
					request.session.modified = True
					return redirect("cull_content")
				else:
					return return_to_content(request,origin,obj_id,link_id,owner_uname)
		else:
			# not a defender, thus not authorized
			delete_temporarily_saved_content_data.delay(own_id)
			raise Http404("You are not an authorized defender")
	else:
		# not a POST request
		delete_temporarily_saved_content_data.delay(own_id)
		return redirect("missing_page")

	
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def render_ban_details(request):
	"""
	Show ban details of a singular ban
	"""
	own_id = request.user.id
	removed_or_edited = request.POST.get("roe",None)
	if removed_or_edited in ('r','e'):
		if in_defenders(own_id):
			owner_uname = request.POST.get("oun",None)
			banned_uname = request.POST.get("utunm",None)# same as owner_uname if sin == bad_submission, but different if sin == bad_voting
			ban_dur = request.POST.get("dur",None)
			ban_init_time = request.POST.get("t",None)
			sin = request.POST.get("sin",None)
			obj_type = request.POST.get("tp",None)
			obj_txt = request.POST.get("txt",None)
			photo_url = request.POST.get("pu",None)
			obj_id = request.POST.get("obid",None)
			defender_remark = request.POST.get("remark",None)
			change_time = request.POST.get("rt",None)
			defender_uname = request.POST.get("dunm",None)
			defender_id = request.POST.get("did",None)
			old_editor_id = request.POST.get("oeid",None)
			old_editor_uname = request.POST.get("oeunm",None)
			roe = 'removed' if removed_or_edited == 'r' else 'edited' 
			return render(request,"judgement/view_ban_details.html",{'b':ban_dur,'t':ban_init_time,'sin':sin,'tp':obj_type,'oun':owner_uname,\
				'txt':obj_txt,'pu':photo_url,'obid':obj_id,'remark':defender_remark,'rt':change_time,'dunm':defender_uname,'did':defender_id,\
				'utunm':banned_uname,'removed_or_edited':roe,'oeid':old_editor_id,'oeunm':old_editor_uname})
		else:
			# only defenders can access this page
			return redirect("missing_page")
	else:
		# data incomplete
		return redirect("missing_page") 


def initiate_content_submission_and_voting_ban(obj_owner_id, obj_id, purl, caption, obj_type, owner_uname, banner_id, origin=None, link_id=None):
	"""
	Helps render content submission and voting ban options to defender

	Also checks if target is already banned from submitting content and voting - and renders a different template in that case
	"""
	already_banned, time_remaining, ban_detail = check_content_and_voting_ban(obj_owner_id, with_details=True)
	offender_score = UserProfile.objects.only('score').get(id=obj_owner_id).score
	status = 'banned_content_submitter_and_voter' if already_banned else ''
	# show banning options according to value of 'already_banned'
	if already_banned:
		can_edit, reason = can_edit_ban(banner_id, ban_detail['did'], obj_owner_id)
		if reason == 'not_defender':
			return None, None
		else:
			temporarily_save_content_details(obj_id=obj_id, owner_id=obj_owner_id, photo_url=purl, caption=caption, obj_type=obj_type, \
				origin=origin, owner_uname=owner_uname, link_id=link_id, banner_id=banner_id, sin=status, target_id=obj_owner_id)
			template_name = "judgement/initiate_already_imposed_content_submission_and_voting_ban.html"
			context = {'orig':origin, 'complaints':get_num_complaints(),'oun':owner_uname,'time_remaining':time_remaining,'ban_data':ban_detail,\
			'obid':obj_id,'purl':purl,'ooid':obj_owner_id,'lid':link_id,'offender_score':offender_score,'cap':caption,'tp':obj_type, reason:True,'can_edit':can_edit, \
			'target_uname':retrieve_uname(obj_owner_id,decode=True)}
			return context, template_name
	else:
		context = {'obid':obj_id,'purl':purl,'oun':owner_uname,'ooid':obj_owner_id,'orig':origin,'lid':link_id,'complaints':get_num_complaints(),\
		'obj_type':obj_type,'cap':caption,'offender_score':offender_score}
		template_name = 'judgement/initiate_content_submission_and_voting_ban.html'
		return context, template_name


def can_edit_ban(own_id, banner_id, target_id):
	"""
	Returns whether a ban is editable by 'own_id' or not
	"""
	created_by_self = True if str(own_id) == str(banner_id) else False
	is_defender, is_super_defender = in_defenders(own_id, return_super_status=True)
	if not is_defender:
		# has no business being here
		return False, 'not_defender'
	elif is_super_defender:
		# can edit per se
		if created_by_self:
			return True, 'ban_creator'
		else:
			return True, 'is_super'
	else:
		# not a super defender, but a defender
		locked_by_super_defender = is_ban_editing_locked(target_id)
		if created_by_self:
			if locked_by_super_defender:
				return False, 'locked_by_super'
			else:
				return True, 'ban_creator'
		else:
			return False, 'not_your_ban'


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def report_content(request,*args,**kwargs):
	"""
	This fires when a user presses the report button next to each piece of content

	Handles full report submission by regular users
	Also handles defender routing to relevant screens
	"""
	if request.method == 'POST':
		if request.user_banned:
			# not for hell-banned users
			return redirect("error")
		else:
			own_id = request.user.id
			is_defender = in_defenders(own_id)#, return_super_status=True)
			lid = request.POST.get("lid",'')
			if lid:
				request.session["target_id"] = lid
				request.session.modified = True
			if is_defender:
				# handle the case for a defender
				obj_type = request.POST.get("tp",None)
				cap = request.POST.get("cap",None)
				obj_id = request.POST.get("report",None)
				ooid = request.POST.get("ooid",None)
				orig = request.POST.get("orig",None)
				purl = request.POST.get("purl",None)#photo thumb or avatar thumb, depending on obh_type
				oun = request.POST.get("oun",None)
				from_cull = request.POST.get("from_cull",None)
				if not obj_id or not ooid or obj_id == 'None' or ooid == 'None':
					# critical data missing - cannot proceed
					return render(request,'judgement/initiate_content_submission_and_voting_ban.html',{'not_enough_data':True,\
						'complaints':get_num_complaints()})
				elif tutorial_unseen(user_id=own_id, which_tut='6', renew_lease=True):
					context = {'obid':obj_id,'purl':purl,'oun':oun,'ooid':ooid,'orig':orig,'lid':lid,'obj_type':obj_type,'cap':cap}
					return render(request, 'judgement/content_defender_tutorial.html', context)
				else:
					own_id = str(own_id)
					# is defender trying to ban self?
					if ooid == own_id:
						request.session["redirect_reason"+own_id] = 'reporting_own_content'
						request.session["redirect_orig"+own_id] = orig
						request.session["redirect_oun"+own_id] = oun
						request.session["redirect_lid"+own_id] = lid
						request.session["redirect_obid"+own_id] = obj_id
						return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
					else:
						# render content submission and voting ban options for the defender
						context, template_name = initiate_content_submission_and_voting_ban(obj_owner_id=ooid, obj_id=obj_id, purl=purl, caption=cap, \
							obj_type=obj_type, owner_uname=oun, banner_id=own_id, origin=orig, link_id=lid)
						if context:
							context["from_cull"] = from_cull
							return render(request, template_name, context)
						else:
							raise Http404("You are not an authorized defender")
			else:
				# regular user (not defender)
				posted_from_screen = request.POST.get("scr",None)
				if tutorial_unseen(user_id=own_id, which_tut='7', renew_lease=True):
				#'first time object reporter'
					ooid = request.POST.get("ooid",None)
					return render(request,'judgement/content_reporter_tutorial.html',{'obid':request.POST.get("report",None),\
						'cap':request.POST.get("cap",None),'purl':request.POST.get("purl",None),'orig':request.POST.get("orig",None),\
						'ooid':ooid,'oun':request.POST.get("oun",None),'tp':request.POST.get("tp",None),'lid':lid})
				elif posted_from_screen == '3':
				# finalize user report of duplicates
					ooid = request.POST.get("ooid",None)
					orig = request.POST.get("orig",None) #origin
					dec = request.POST.get("dec",None)
					oun = request.POST.get("oun",None)
					dup_obid = request.POST.get("obid",None) #dup_obid - accused of being a duplicate
					if dec == '0':
						return return_to_content(request,orig,dup_obid,lid,oun)
					else:
						# first check if report should be allowed (i.e. the time of the duplicate was AFTER the time of the so-called original)
						orig_obid = request.POST.get("oobid",None) # the so-called 'original' content (obid:oburl or obid:caption)
						tp = request.POST.get("tp",None)
						if not orig_obid or not dup_obid:
							return return_to_content(request,orig,dup_obid,lid,oun)
						elif tp == 'tx':
							orig_link = Link.objects.only('submitted_on','submitter').get(id=orig_obid)
							dup_link = Link.objects.only('submitted_on','submitter').get(id=dup_obid)
							orig_submitter_id = orig_link.submitter_id
							dup_submitter_id = dup_link.submitter_id
							orig_time = orig_link.submitted_on
							dup_time = dup_link.submitted_on
						elif tp == 'img':
							orig_img = Photo.objects.only('upload_time','owner').get(id=orig_obid)
							dup_img = Photo.objects.only('upload_time','owner').get(id=dup_obid)
							orig_submitter_id = orig_img.owner_id
							dup_submitter_id = dup_img.owner_id
							orig_time = orig_img.upload_time
							dup_time = dup_img.upload_time
						else:
							return return_to_content(request,orig,dup_obid,lid,oun)
						if orig_time > dup_time:
							# sanity check failed: the so-called original came LATER than the duplicate - it's a false report
							own_id = str(own_id)
							request.session["redirect_reason"+own_id] = 'not_original'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = dup_obid
							return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
						elif own_id == dup_submitter_id:
							# cannot report self
							own_id = str(own_id)
							request.session["redirect_reason"+own_id] = 'reporting_own_content'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = dup_obid
							return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
						elif str(dup_submitter_id) != ooid:
							# the 'ooid' variable was tinkered with
							own_id = str(own_id)
							request.session["redirect_reason"+own_id] = 'report_tinkered'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = dup_obid
							return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
						elif dec in ('9','10'):
							# file report - our required data is complete (and sane)
							prc = get_price(request.user.userprofile.score)#don't rely on price POST parameter - get it again
							if tp == 'tx':
								orig_description = Link.objects.only('description').get(id=orig_obid).description
								dup_description = Link.objects.only('description').get(id=dup_obid).description
								ttl = set_complaint(report_desc=TEXT_REPORT_PROMPT[dec], rep_type=dec, obj_id=dup_obid, obj_owner_id=dup_submitter_id, \
									obj_type=tp, price_paid=prc, reporter_id=own_id, time_now=time.time(), obj_txt=dup_description, orig_obid=orig_obid, \
									orig_txt=orig_description,reported_item_ct=convert_to_epoch(dup_time), orig_item_ct=convert_to_epoch(orig_time))
							else:
								orig_image = get_s3_object(Photo.objects.only('image_file').get(id=orig_obid).image_file)#full fledged image file, not thumb
								data = Photo.objects.filter(id=dup_obid).values_list('image_file','caption')[0]#do not rely on 'purl' and 'cap' POST variables
								dup_image = get_s3_object(data[0],category="thumb")
								ttl = set_complaint(report_desc=PHOTO_REPORT_PROMPT[dec], rep_type=dec, obj_id=dup_obid, obj_owner_id=dup_submitter_id, \
									obj_type=tp, price_paid=prc, reporter_id=own_id, time_now=time.time(), img_caption=data[1], obj_url=dup_image, \
									orig_obid=orig_obid, orig_url=orig_image, reported_item_ct=convert_to_epoch(dup_time), \
									orig_item_ct=convert_to_epoch(orig_time))
							if ttl:
								# the person is either rate limited from reporting, or is reporting the same item again
								own_id = str(own_id)
								request.session["redirect_reason"+own_id] = 'already_reported'
								request.session["redirect_orig"+own_id] = orig
								request.session["redirect_oun"+own_id] = oun
								request.session["redirect_lid"+own_id] = lid
								request.session["redirect_obid"+own_id] = dup_obid
								request.session["redirect_report_ttl"+own_id] = ttl
								return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
							else:
								#charge the price and send the report
								UserProfile.objects.filter(user_id=request.user.id).update(score=F('score')-prc)
								return render(request,'judgement/content_report_sent.html',{'orig':orig,'obid':dup_obid,'oun':oun,'prc':prc,'tp':tp,\
									'payload':dup_description if tp == 'tx' else dup_image,'lid':lid})
						else:
							return return_to_content(request,orig,dup_obid,lid,oun)    
				elif posted_from_screen == '2':
				# finalize regular user report. This does NOT handle duplicates report, that is posted_from_screen == '3'
				# Get all variables, charge the reporting user, and submit the report!
					dec = request.POST.get("dec",None) #decision (radio button number)
					orig = request.POST.get("orig",None) #origin
					obid = request.POST.get("obid",None) #obj_id
					oun = request.POST.get("oun",None) #username (if originating from a profile)
					if not dec:
						# the user 'canceled'
						return return_to_content(request,orig,obid,lid,oun)
					else:
						purl = request.POST.get("purl",None) #photo_url
						tp = request.POST.get("tp",None)# type of item ('tx' or 'img')
						cap = request.POST.get("cap",None) #caption
						form = PhotoReportForm(request.POST)
						if form.is_valid():
							prc = get_price(request.user.userprofile.score)#don't rely on price post parameter - recalculate it
							feedback_text = form.cleaned_data.get("description")
							try:
								if tp == 'tx':
									data = Link.objects.only('submitted_on','description','submitter').get(id=obid)#do not rely on 'cap' POST variable
									creation_time, description, submitter_id = convert_to_epoch(data.submitted_on), data.description, data.submitter_id
									ttl = set_complaint(report_desc=TEXT_REPORT_PROMPT[dec], rep_type=dec, obj_id=obid, obj_owner_id=submitter_id, obj_type=tp, \
										price_paid=prc, reporter_id=own_id, time_now=time.time(),feedback_text=feedback_text, obj_txt=description, \
										reported_item_ct=creation_time)
								elif tp == 'img':
									data = Photo.objects.only('image_file','caption','upload_time','owner').get(id=obid)#do not rely on 'purl' and 'cap' POST variables
									img_thumb = get_s3_object(data.image_file,category="thumb")
									ttl = set_complaint(report_desc=PHOTO_REPORT_PROMPT[dec], rep_type=dec, obj_id=obid, obj_owner_id=data.owner_id, obj_type=tp, \
										price_paid=prc, reporter_id=own_id, time_now=time.time(),feedback_text=feedback_text, img_caption=data.caption, \
										obj_url=img_thumb, reported_item_ct=convert_to_epoch(data.upload_time))
								elif tp == 'pf':
									# reported profile
									data = User.objects.filter(id=obid).values_list('date_joined','username')[0]
									avatar = UserProfile.objects.only('avatar').get(user_id=obid).avatar
									av_img = get_s3_object(avatar,category="thumb")
									payload_tp = 'nick' if dec in ('1','2','3') else 'foto'
									# 'mehfil_report_tp' carries profile_reporting type (i.e. 'nick' or 'foto')
									ttl = set_complaint(report_desc=PROFILE_REPORT_PROMPT[dec], rep_type=dec, obj_id=obid, obj_owner_id=obid, obj_type=tp, \
										price_paid=prc, reporter_id=own_id, time_now=time.time(),feedback_text=feedback_text, img_caption=data[1], \
										obj_url=av_img, mehfil_report_tp=payload_tp, reported_item_ct=convert_to_epoch(data[0]))
									# If profile was reported, freeze critical user profile functionality, and unfreeze when case processed
									if not ttl:
										freeze_critical_profile_functionality(obid)
								else:
									return return_to_content(request,orig,obid,lid,oun)
								if ttl:
									own_id = str(own_id)
									request.session["redirect_reason"+own_id] = 'already_reported'
									request.session["redirect_orig"+own_id] = orig
									request.session["redirect_oun"+own_id] = oun
									request.session["redirect_lid"+own_id] = lid
									request.session["redirect_obid"+own_id] = obid
									request.session["redirect_report_ttl"+own_id] = ttl
									return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
								else:
									#go ahead and charge the price
									UserProfile.objects.filter(user_id=request.user.id).update(score=F('score')-prc)
									return render(request,'judgement/content_report_sent.html',{'orig':orig,'obid':obid,'oun':oun,'prc':prc,'tp':tp,\
										'payload':description if tp == 'tx' else purl,'lid':lid})
							except (TypeError,AttributeError):
								return return_to_content(request,orig,obid,lid,oun)
						else:
							# form is invalid, reload
							prc = request.POST.get("prc",None) #price of reporting
							context={'dec':dec, 'orig':orig, 'prc':prc, 'obid':obid, 'lid':lid, 'oun':oun, 'form':form, 'purl':purl,'tp':tp,\
							'cap':cap,'reason':TEXT_REPORT_PROMPT[dec] if tp == 'tx' else PHOTO_REPORT_PROMPT[dec]}
							return render(request,'judgement/content_report_text.html',context)
				elif posted_from_screen == '1':
				# progress user to screen 2 (one where they input text report). Include variables gotten from screen 1
					dec = request.POST.get("dec",None) #decision (radio button number)
					orig = request.POST.get("orig",None)
					obid = request.POST.get("obid",None)
					oun = request.POST.get("oun",None)
					tp = request.POST.get("tp",None)
					purl = request.POST.get("purl",None) #photo_url
					cap = request.POST.get("cap",None) #caption
					prc = request.POST.get("prc",None) #price of reporting
					if dec == '0':
						# they decided against reporting
						return return_to_content(request,orig,obid,lid,oun)
					elif tp in ('tx','img'):
						# text or image reported
						if dec in ('9','10'):
							# reporting duplication of own content, or target's content
							# if tp == 'tx', pull recent 'text history', else pull recent 'fotos'. Then ask user to select the copied one
							ooid = request.POST.get("ooid",None)
							qset = get_content_history(own_id if dec == '9' else obid, tp, dec)
							return render(request,'judgement/duplicate_content_report.html',{'object_list':qset,'dec':dec, 'orig':orig, 'prc':prc,\
								'obid':obid, 'lid':lid, 'oun':oun, 'purl':purl,'cap':cap,'tp':tp,'ooid':ooid})
						else:
							report_options = TEXT_REPORT_PROMPT if tp == 'tx' else PHOTO_REPORT_PROMPT
							context={'dec':dec, 'orig':orig, 'prc':prc, 'obid':obid, 'lid':lid, 'oun':oun, 'form':PhotoReportForm(), 'purl':purl,\
							'cap':cap,'reason':report_options[dec],'tp':tp}
							return render(request,'judgement/content_report_text.html',context)
					elif tp == 'pf':
						context={'dec':dec, 'orig':orig, 'prc':prc, 'obid':obid, 'lid':lid, 'oun':oun, 'form':PhotoReportForm(), 'purl':purl,\
						'reason':PROFILE_REPORT_PROMPT[dec],'tp':tp}
						return render(request,'judgement/content_report_text.html',context)
					else:
						# if 'tp' was tinkered with
						return return_to_content(request,orig,obid,lid,oun)
				else:
				# show options with radio buttons to reporting user (this is screen 1, it's the default people land on)
					own_id = str(own_id)
					score = request.user.userprofile.score
					price_of_report = get_price(score)
					obj_id = request.POST.get("report",None)
					orig = request.POST.get("orig",None) #origin 
					purl = request.POST.get("purl",None) #photo_url
					oun = request.POST.get("oun",None)#owner_username
					ooid = str(request.POST.get("ooid",None))
					type_of_content = request.POST.get("tp",None)# either 'img', 'tx' or 'pf'
					reporting_self = (True if own_id == ooid else False)
					if reporting_self:
						request.session["redirect_reason"+own_id] = 'reporting_own_content'
						request.session["redirect_orig"+own_id] = orig
						request.session["redirect_oun"+own_id] = oun
						request.session["redirect_lid"+own_id] = lid
						request.session["redirect_obid"+own_id] = obj_id
						return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
					else:
						if type_of_content == 'tx':
							content_points = Link.objects.only('net_votes').get(id=obj_id).net_votes
							report_options = TEXT_REPORT_PROMPT
						elif type_of_content == 'img':
							content_points = Photo.objects.only('vote_score').get(id=obj_id).vote_score
							report_options = PHOTO_REPORT_PROMPT
						else:
							# if profile being reported - currently there is no way to stop double reporting
							content_points = 0 #TODO: ensure double reporting of profiles cant happen
							report_options = PROFILE_REPORT_PROMPT
						if content_points < -98:
							# disallow reporting (content already has really low score - probably already banned before)
							request.session["redirect_reason"+own_id] = 'item_already_downgraded'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = obj_id
							return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
						elif price_of_report > score:
							#disallow reporting (user doesn't have requisite score)
							request.session["redirect_reason"+own_id] = 'not_enough_score'
							request.session["redirect_orig"+own_id] = orig
							request.session["redirect_oun"+own_id] = oun
							request.session["redirect_lid"+own_id] = lid
							request.session["redirect_obid"+own_id] = obj_id
							return redirect("judge_not_and_red")#judgement module's notify_and_redirect function
						else:
							# show all report options to user
							context={'price':price_of_report,'obj_id':obj_id, 'reporting_self':reporting_self,'orig':orig,'purl':purl,\
							'owner_uname':oun,'lid':lid,'rep_opt':ordered_list_of_tup(report_options),'cap':request.POST.get("cap",None),\
							'tp':type_of_content,'oid':ooid}
							return render(request,"judgement/content_report.html",context)
	else:
		return redirect("missing_page")



def notify_and_redirect(request):
	"""
	Redirects user to the notify_and_redirect template
	"""
	own_id = str(request.user.id)
	reason = request.session.pop("redirect_reason"+own_id,None)
	origin = request.session.pop("redirect_orig"+own_id,None)
	owner_uname = request.session.pop("redirect_oun"+own_id,None)
	link_id = request.session.pop("redirect_lid"+own_id,None)
	obj_id = request.session.pop("redirect_obid"+own_id,None)
	if reason in ('not_your_ban','locked_by_super','reporting_own_content','temp_data_missing','cannot_ban_self','not_enough_score',\
		'item_already_downgraded','not_original','report_tinkered'):
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'lid':link_id,'obid':obj_id})
	elif reason == 'ban_edited':
		ntr = request.session.pop("redirect_ntr"+own_id,None)
		otr = request.session.pop("redirect_otr"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'lid':link_id,'obid':obj_id,
			'new_time_remaining':ntr,'old_time_remaining':otr})
	elif reason == 'ban_removed':
		otr = request.session.pop("redirect_otr"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'obid':obj_id,'lid':link_id,\
			'old_time_remaining':otr})
	elif reason == 'multi_already_banned':
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'lid':link_id,'obid':obj_id})
	elif reason == 'ban_imposed':
		ban_time = request.session.pop("redirect_ban_time"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'obid':obj_id,'lid':link_id,\
			'ban_time':ban_time})
	elif reason == 'already_banned':
		time_remaining = request.session.pop("redirect_time_remaining"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'lid':link_id,'obid':obj_id,\
			'time_remaining':time_remaining})
	elif reason == 'multi_ban_imposed':
		ban_time = request.session.pop("redirect_ban_time"+own_id,None)
		target_usernames = request.session.pop("redirect_tunm"+own_id,None)
		banned_usernames = request.session.pop("redirect_iun"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'obid':obj_id,'lid':link_id,\
			'tunm':json.loads(target_usernames) if target_usernames else [],'iun':json.loads(banned_usernames) if banned_usernames else [],\
			'ban_time':ban_time})
	elif reason == 'already_reported':
		ttl = request.session.pop("redirect_report_ttl"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'orig':origin,'oun':owner_uname,'lid':link_id,'obid':obj_id,\
			'ttl':ttl})
	elif (reason == 'not_enough_score_to_report_mehfil') or (reason == 'mehfil_does_not_exist') or (reason == 'mehfil_report_ttl'):
		group_uuid = request.session.pop("redirect_guid"+own_id,None)
		ttl = request.session.pop("redirect_report_ttl"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'unique':group_uuid,'ttl':ttl})
	elif reason == 'reporting_own_mehfil':
		group_uuid = request.session.pop("redirect_guid"+own_id,None)
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'unique':group_uuid})
	elif reason == 'reporting_own_profile':
		return render(request,"judgement/notify_and_redirect.html",{reason:True,'uname':retrieve_uname(own_id,decode=True)})
	else:
		return render(request,"judgement/notify_and_redirect.html",{'orig':origin,'oun':owner_uname,'lid':link_id,'obid':obj_id})



@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def report_content_help(request):
	"""
	Displays helpful instructions to users who want to report content

	These instructions are ever-present via a navbar appearing at the top of reported content
	Tied to report_navbar.html (distinct from 'first time' instructions tutorial)
	"""
	if request.method == "POST":
		item_type = request.POST.get("tp",None)
		origin = request.POST.get("orig",None)
		caption = request.POST.get("cap",None)
		photo_url = request.POST.get("purl",None)
		link_id = request.POST.get("lid",None)
		owner_uname = request.POST.get("oun",None)
		obj_id = request.POST.get("obid",None)
		oid = request.POST.get("oid",None)
		delete_temporarily_saved_content_data.delay(request.user.id)
		return render(request,"judgement/content_report_help.html",{'tp':item_type,'orig':origin,'cap':caption,'purl':photo_url,\
			'lid':link_id,'oun':owner_uname,'obid':obj_id,'oid':oid,'complaints':get_num_complaints()})
	else:
		# not a POST request
		return redirect("website_rules")


def get_content_history(target_id,type_of_content,decision):
	"""
	Return content history for target_id

	Useful when spotting duplicated content in report_content()
	Decision '10' implies own content was copied
	Decision '11' implies user is duplicating their content again and again
	"""
	days_ago = datetime.utcnow()-timedelta(hours=HOURS_LOOKBACK_FOR_CHECKING_CONTENT_CLONES)# currently set to 50 hours ago
	if decision == '9':
		# target_id is own id
		if type_of_content == 'tx':
			# get own links of past 2 days ordered by time (max: 40 objects)
			qset = Link.objects.filter(submitter_id=target_id,submitted_on__gte=days_ago).order_by('-id').values_list('description','submitted_on','id')
		else:
			# get photos of past 2 days (max: 40 objects)
			qset = Photo.objects.filter(owner_id=target_id,upload_time__gte=days_ago).order_by('-id').values_list('image_file','upload_time','id')
	else:
		# target_id is their object's id, use it to retrieve owner id
		if type_of_content == 'tx':
			# first get owner id
			submitter_id = Link.objects.only('submitter').get(id=target_id).submitter_id
			# get this user's links of past 2 days (max: 40 objects)
			# exclude the link obh itself that's being reported
			qset = Link.objects.filter(submitter_id=submitter_id,submitted_on__gte=days_ago).exclude(id=target_id).order_by('-id')\
			.values_list('description','submitted_on','id')
		else:
			# first get owner id
			submitter_id = Photo.objects.only('owner').get(id=target_id).owner_id
			# get this user's photos of past 2 days (max: 40 objects)
			# exclude the foto obj itself that's being reported
			qset = Photo.objects.filter(owner_id=submitter_id,upload_time__gte=days_ago).exclude(id=target_id).order_by('-id')\
			.values_list('image_file','upload_time','id')
	return qset


#################################################################################################################
#################################################################################################################

def ordered_list_of_tup(dictionary):
	"""
	Gets report_options (either TEXT_REPORT_PROMPT, PHOTO_REPORT_PROMPT or MEHFIL_REPORT_PROMPT) and returns a list of tuples ordered by 'key'

	PHOTO_REPORT_PROMPT values are:
		'0':'Report rehne dein'
		'1':'Foto mein nudity ya vulgarity hai'
		'2':'Foto mein mazhabi fasad hai'
		'3':'Foto mein khoon kharaba ya aziyat hai'
		'4':'Foto takhreeb karoon ka sath de rahi hai'
		'5':'Foto Damadam ki screenshot hai'
		'6':'Foto hadd se ziyada dhundhli hain'
		'7':'Title ka foto se taluq nahi hai'
		'8':'Title mein vote or comments ki bheek hai'
	"""
	return sorted([(k,v) for (k,v) in dictionary.iteritems()], key=lambda tup: int(tup[0]))     


def show_report_help(request,rtp,ridx):
	"""
	Renders a page with a description of reporting reason to help users make a better decision
	"""
	if not rtp or not ridx:
		return redirect("missing_page")
	else:
		if rtp == 'mf':
			label = GET_MEHFIL_REPORT_HELP_LABEL[ridx]
		elif rtp == 'pf':
			label = GET_PROFILE_REPORT_HELP_LABEL[ridx]
		elif rtp == 'img':
			label = GET_PHOTO_REPORT_HELP_LABEL[ridx]
		else:
			label = GET_TEXT_REPORT_HELP_LABEL[ridx]
		return render(request,"judgement/single_report_help.html",{'rep_type':rtp,'label':label})


def spamming_definition(request):
	"""
	Gives the definition of "spam"
	"""
	return render(request,"judgement/spamming_definition.html",{})


############################################## Adding and removing Defenders ###############################################


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def add_new_defender(request):
	"""
	Control panel for adding new defender

	Accessible to all defenders - ought to be made more secure
	"""
	own_id = request.user.id
	if has_super_privilege(own_id):
		if request.method == "POST":
			form = AddDefenderIDForm(request.POST, user_id=own_id)
			if form.is_valid():
				is_super = request.POST.get("is_sup",None)
				defender_id = form.cleaned_data.get("defender_id")
				add_defender(own_id, defender_id,time.time(),is_super=True if is_super == '1' else False)
				#################################################################
				curr_defenders, all_defenders, curr_defenders_with_priv = retrieve_all_defenders(mark_super=True)
				old_defenders = [item for item in all_defenders if item not in curr_defenders]
				return render(request,"judgement/add_defender.html",{'successful':True,'form':AddDefenderIDForm(),'old_defenders':old_defenders,\
					'curr_defenders':curr_defenders_with_priv,'added_username':retrieve_uname(defender_id,decode=True)})
			else:
				curr_defenders, all_defenders,curr_defenders_with_priv = retrieve_all_defenders(mark_super=True)
				old_defenders = [item for item in all_defenders if item not in curr_defenders]
				return render(request,"judgement/add_defender.html",{'form':form,'curr_defenders':curr_defenders_with_priv,'old_defenders':old_defenders})
		else:
			curr_defenders, all_defenders,curr_defenders_with_priv = retrieve_all_defenders(mark_super=True)
			old_defenders = [item for item in all_defenders if item not in curr_defenders]
			return render(request,"judgement/add_defender.html",{'form':AddDefenderIDForm(),'curr_defenders':curr_defenders_with_priv,'old_defenders':old_defenders})
	else:
		return redirect("missing_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def remove_current_defender(request):
	"""
	Can remove any current defender except self

	Accessible to all defenders - ought to be made more secure
	"""
	own_id = request.user.id
	if has_super_privilege(own_id):
		if request.method == "POST":
			form = RemDefenderIDForm(request.POST, user_id=own_id)
			if form.is_valid():
				defender_id = form.cleaned_data.get("defender_id")
				remove_defender(defender_id)
				curr_defenders, all_defenders, curr_defenders_with_priv = retrieve_all_defenders(mark_super=True)
				old_defenders = [item for item in all_defenders if item not in curr_defenders]
				return render(request,"judgement/remove_defender.html",{'successful':True,'form':RemDefenderIDForm(),'old_defenders':old_defenders,\
					'curr_defenders':curr_defenders_with_priv,'form':form,'removed_username':retrieve_uname(defender_id,decode=True)})
			else:
				curr_defenders, all_defenders, curr_defenders_with_priv = retrieve_all_defenders(mark_super=True)
				old_defenders = [item for item in all_defenders if item not in curr_defenders]
				return render(request,"judgement/remove_defender.html",{'form':form,'old_defenders':old_defenders,'curr_defenders':curr_defenders_with_priv,\
					'form':form})
		else:
			curr_defenders, all_defenders, curr_defenders_with_priv = retrieve_all_defenders(mark_super=True)
			old_defenders = [item for item in all_defenders if item not in curr_defenders]
			return render(request,"judgement/remove_defender.html",{'old_defenders':old_defenders,'curr_defenders':curr_defenders_with_priv,\
				'form':RemDefenderIDForm()})
	else:
		return redirect("missing_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def defender_instructions(request):
	"""
	Displays instructins available to a defender
	"""
	if in_defenders(request.user.id):
		if request.method == "POST":
			obid = request.POST.get("obid",None)
			purl = request.POST.get("purl",None)
			oun = request.POST.get("oun",None)
			ooid = request.POST.get("ooid",None)
			orig = request.POST.get("orig",None)
			lid = request.POST.get("lid",None)
			obj_type = request.POST.get("obj_type",None)
			cap = request.POST.get("cap",None)
			from_cull = request.POST.get("from_cull",None)
			context = {'complaints':get_num_complaints(),'obid':obid,'purl':purl,'oun':oun,'ooid':ooid,'orig':orig,'lid':lid,'obj_type':obj_type,'cap':cap,\
			'from_cull':from_cull}
			return render(request,"judgement/defender_help.html",context)
		else:
			# not a POST request
			return render(request,"judgement/defender_help.html",{'complaints':get_num_complaints()})
	else:
		return redirect("missing_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def defender_instruction_failure(request):
	"""
	Automatically remove defender since they failed to follow provided instructions

	Should have pressed 'Cancel' instead of 'OK' (trick to ensure they read everything closely)
	"""
	if request.method == "POST":
		remove_defender(request.user.id)
		return render(request,"judgement/cannot_become_defender.html",{})
	else:
		return redirect("missing_page")


##################################### Shows reports of various reporting and banning activity #####################################


def defender_history_super_admin_view(request, defender_id):
	"""
	Displays defender's banning history to super admin(s)

	TODO: export to csv
	"""
	if has_super_privilege(request.user.id):
		block_data, ledger_ttl = get_defenders_ledger(defender_id, with_ttl=True)
		if block_data:
			currently_defender = True
			previously_defender = True
		else:
			currently_defender = in_defenders(defender_id)
			if currently_defender:
				previously_defender = False
			else:
				previously_defender = in_defs_forever(defender_id)
		defender_username = retrieve_uname(defender_id,decode=True)
		if block_data:
			return render(request,"judgement/defenders_blocking_history.html",{'block_data':block_data,'defender_username':defender_username,\
				'currently_defender':currently_defender,'previously_defender':previously_defender,'super_admin':True, 'ledger_ttl':ledger_ttl,\
				'super_view_of_def':True})
		else:
			return render(request,"judgement/defenders_blocking_history.html",{'block_data':None,'defender_username':defender_username,\
				'currently_defender':currently_defender,'previously_defender':previously_defender,'super_admin':True, 'ledger_ttl':ledger_ttl,\
				'super_view_of_def':True})
	else:
		# this user has no business here
		return redirect("missing_page")


def show_your_banning_history(request):
	"""
	Displays defender's own banning history (to defender herself)
	"""
	own_id = request.user.id
	is_def = in_defenders(own_id)
	if is_def:
		if request.method == "POST":
			obid = request.POST.get("obid",None)
			purl = request.POST.get("purl",None)
			oun = request.POST.get("oun",None)
			ooid = request.POST.get("ooid",None)
			orig = request.POST.get("orig",None)
			lid = request.POST.get("lid",None)
			obj_type = request.POST.get("obj_type",None)
			cap = request.POST.get("cap",None)
			from_cull = request.POST.get("from_cull",None)
			delete_temporarily_saved_content_data.delay(own_id)
			block_data, own_username = get_defenders_ledger(own_id), retrieve_uname(own_id,decode=True)
			if block_data:
				return render(request,"judgement/defenders_blocking_history.html",{'block_data':block_data,'defender_username':own_username,\
					'currently_defender':True,'complaints':get_num_complaints(),'obid':obid,'purl':purl,'oun':oun,'ooid':ooid,'orig':orig, \
					'lid':lid,'obj_type':obj_type,'cap':cap,'from_cull':from_cull})
			else:
				return render(request,"judgement/defenders_blocking_history.html",{'block_data':None,'defender_username':own_username,\
					'currently_defender':True,'complaints':get_num_complaints(),'obid':obid,'purl':purl,'oun':oun,'ooid':ooid,'orig':orig, \
					'lid':lid,'obj_type':obj_type,'cap':cap,'from_cull':from_cull})
		else:
			# show 'vanilla' banning ledger
			block_data, own_username = get_defenders_ledger(own_id), retrieve_uname(own_id,decode=True)
			if block_data:
				return render(request,"judgement/defenders_blocking_history.html",{'block_data':block_data,'defender_username':own_username,\
					'currently_defender':True,'complaints':get_num_complaints()})
			else:
				return render(request,"judgement/defenders_blocking_history.html",{'block_data':None,'defender_username':own_username,\
					'currently_defender':True,'complaints':get_num_complaints()})
	else:
		# this user has no business here
		return redirect("missing_page")


def show_blocking_history_of_defenders(request):
	"""
	Super admin view that displays who blocked who (and why)

	Paginated by 50 objects (ITEMS_PER_PAGE_IN_ADMINS_LEDGER = 50)
	TODO: export to csv
	"""
	if has_super_privilege(request.user.id):
		page_num = int(request.GET.get('page', '1'))
		data, total_items = get_global_admins_ledger(page_num)
		return render(request,"judgement/blocking_history.html",{'block_data':data,'current_page':page_num,'next_page':page_num+1,'num_items':total_items,\
			'prev_page':None if page_num == 1 else page_num-1, 'items_per_page':ITEMS_PER_PAGE_IN_ADMINS_LEDGER,'num_displayed':len(data),'super_admin':True})
	else:
		return redirect("missing_page")


def show_rejecton_history_of_defenders(request):
	"""
	Super admin view that displays which defender rejected what report /from cull-content

	Paginated by 50 objects (ITEMS_PER_PAGE_IN_ADMINS_LEDGER = 50)
	TODO: export to csv
	"""
	if has_super_privilege(request.user.id):
		page_num = int(request.GET.get('page', '1'))
		data, total_items = get_global_admins_ledger(page_num,rejection_history=True)
		return render(request,"judgement/report_rejection_history.html",{'rejection_data':data,'current_page':page_num,'next_page':page_num+1,'num_items':total_items,\
			'prev_page':None if page_num == 1 else page_num-1, 'items_per_page':ITEMS_PER_PAGE_IN_ADMINS_LEDGER,'num_displayed':len(data),'super_admin':True})
	else:
		raise Http404("You are not an authorized defender")


def get_top_50_reporters(request):
	"""
	Super admin view that displays top 50 complaint reporters sorted by number of successful reports

	1) Only those users are considered who have at least 1 correct report
	2) Users who haven't filed a report in 2 months are removed from the list
	"""
	if has_super_privilege(request.user.id):
		top_50_reporters_data = retrieve_top_complainer_reputation()
		top_50_reporters, total_correct_reporters = top_50_reporters_data[0], top_50_reporters_data[1]
		only_ids = [i[0] for i in top_50_reporters]
		ids_and_usernames = User.objects.filter(id__in=only_ids).values_list('id','username')
		usernames = {}
		for user_id, username in ids_and_usernames:
			usernames[str(user_id)] = username
		top_reporters = []
		for reporter_id, num_correct, num_total in top_50_reporters:
			top_reporters.append((reporter_id, usernames[reporter_id],int(num_correct),int(num_total),"{0:.2f}".format(num_correct/num_total)))
		return render(request,"judgement/top_50_reporters.html",{'top_50_reporters':top_reporters, 'total_correct':total_correct_reporters})
	else:
		return redirect("missing_page")


def get_reporter_history(request, reporter_id):
	"""
	Super admin view that allows super admin to drill down into exact cases filed by a regular reporter

	Can help determine report quality of a particular reporter
	"""
	if has_super_privilege(request.user.id):
		case_data = get_complainer_case_history(reporter_id)
		num_cases = len(case_data)
		return render(request,"judgement/reporter_history.html",{'target_uname':retrieve_uname(reporter_id,decode=True),'all_cases':case_data,\
			'num_cases':num_cases})
	else:
		return redirect("missing_page")


