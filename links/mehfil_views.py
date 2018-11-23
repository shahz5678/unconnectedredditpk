import uuid, time, json
from operator import itemgetter
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from django.views.generic.edit import FormView, CreateView
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import F
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.debug import sensitive_post_parameters
from brake.decorators import ratelimit
from verified import FEMALES
from image_processing import clean_image_file
from score import PRIVATE_GROUP_COST, PUBLIC_GROUP_COST, PUBLIC_GROUP_MESSAGE, PRIVATE_GROUP_MESSAGE, MAX_OWNER_INVITES_PER_PUBLIC_GROUP,\
MAX_OFFICER_INVITES_PER_PUBLIC_GROUP, PRIVATE_GROUP_MAX_MEMBERSHIP, MAX_OWNER_INVITES_PER_PRIVATE_GROUP, MAX_MEMBER_INVITES_PER_PRIVATE_GROUP
from views import condemned, convert_to_epoch, valid_uuid
from models import Group, Reply, GroupCaptain, GroupTraffic, Link, GroupBanList, UserProfile
from tasks import rank_public_groups, public_group_attendance_tasks, queue_for_deletion, set_input_rate_and_history, group_notification_tasks,\
log_private_mehfil_session
from redis1 import check_group_member, remove_group_member, remove_user_group, check_group_invite, remove_group_invite, add_group_member,\
add_user_group, add_group_invite, add_home_link, add_unfiltered_post, add_filtered_post, set_latest_group_reply, bulk_check_group_membership,\
bulk_check_group_invite, get_user_groups, get_latest_group_replies, get_active_invites, get_group_members, add_refresher, first_time_refresher,\
remove_all_group_members, remove_latest_group_reply, remove_group_for_all_members
from redis2 import remove_group_notification, remove_group_object, get_attendance, create_notification, create_object, get_replies_with_seen, \
save_user_presence, get_latest_presence, update_notification, del_attendance, remove_group_object
from redis4 import get_most_recent_online_users, set_text_input_key, retrieve_uname
from redis3 import get_ranked_public_groups, del_from_rankings
from mehfil_forms import GroupHelpForm, ReinviteForm, OpenGroupHelpForm, ClosedGroupHelpForm, MehfilForm, AppointCaptainForm, OwnerGroupOnlineKonForm,\
GroupOnlineKonForm, DirectMessageCreateForm, ClosedGroupCreateForm, OpenGroupCreateForm, DirectMessageForm, ReinvitePrivateForm, GroupListForm, \
GroupPageForm, GroupTypeForm, ChangeGroupRulesForm, ChangePrivateGroupTopicForm, ChangeGroupTopicForm, PublicGroupReplyForm, PrivateGroupReplyForm
from redis6 import retrieve_cached_ranked_groups, cache_ranked_groups

########################## Mehfil Help #########################

class GroupHelpView(FormView):
	"""
	Renders the help page for mehfils
	"""
	form_class = GroupHelpForm
	template_name = "mehfil/group_help.html"

	def get_context_data(self, **kwargs):
		context = super(GroupHelpView, self).get_context_data(**kwargs)
		context["private_price"] = PRIVATE_GROUP_COST
		context["public_price"] = PUBLIC_GROUP_COST
		context["public_owner_invites"] = MAX_OWNER_INVITES_PER_PUBLIC_GROUP
		context["public_officer_invites"] = MAX_OFFICER_INVITES_PER_PUBLIC_GROUP
		context["private_max_members"] = PRIVATE_GROUP_MAX_MEMBERSHIP
		context["private_member_invites"] = MAX_MEMBER_INVITES_PER_PRIVATE_GROUP
		context["private_owner_invites"] = MAX_OWNER_INVITES_PER_PRIVATE_GROUP
		return context
		
#################### Inviting users to mehfils #####################

class ReinviteView(FormView):
	"""
	Renders error message if someone tries to 'double-invite' a user to a public mehfil

	Called from process_public_group_invite()
	"""
	form_class = ReinviteForm
	template_name = "mehfil/reinvite.html"

	def get_context_data(self, **kwargs):
		context = super(ReinviteView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.kwargs.get("slug")
			context["unique"] = unique
		return context

class ReinvitePrivateView(FormView):
	"""
	Renders error message if someone tries to 'double-invite' a user to a private mehfil

	Called from process_private_group_invite()
	"""
	form_class = ReinvitePrivateForm
	template_name = "mehfil/reinvite_private.html"

	def get_context_data(self, **kwargs):
		context = super(ReinvitePrivateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			unique = self.request.session["unique_id"]
			context["unique"] = unique
		return context

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def process_public_group_invite(request,*args, **kwargs):
	"""
	Sending a prospective user an invite to a public mehfil

	If prospective member was already invited, ensure invite not sent
	"""
	if request.user_banned:
		return redirect("group_page")
	elif request.method == "POST":	
		uuid = request.POST.get("puid",None)
		pk = request.POST.get("vid",None)
		try:
			group = Group.objects.get(unique=uuid)
			group_id = group.id
		except:
			group_id = -1
		if group_id > -1:
			invitee_username = User.objects.filter(id=pk).values_list('username',flat=True)[0]
			if check_group_invite(pk, group_id) or check_group_member(group_id, invitee_username):
				return redirect("reinvite_help", slug= uuid)
			else:#this person ought to be sent an invite
				#send a notification to this person to check out the group
				reply = Reply.objects.create(text=invitee_username, category='1', which_group_id=group_id,writer=request.user)
				add_group_invite(pk, group_id,reply.id)
		return redirect("invite")
	else:
		return redirect("group_page")



@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def process_private_group_invite(request, *args, **kwargs):
	"""
	Sending a prospective user an invite to a private mehfil

	If prospective member was already invited, ensure invite not sent
	"""
	if request.method=="POST":
		if request.user_banned:
			return redirect("group_page")
		else:
			uuid = request.POST.get("puid",None)
			pk = request.POST.get("vid",None)
			try:
				group = Group.objects.get(unique=uuid)
				group_id = group.id
			except:
				group_id = -1
			if group_id > -1:
				invitee_username = User.objects.filter(id=pk).values_list('username',flat=True)[0]
				if check_group_invite(pk, group_id) or check_group_member(group_id, invitee_username):
					return redirect("reinvite_private_help")
				else:#this person ought to be sent an invite
					#send a notification to this person to check out the group
					reply = Reply.objects.create(text=invitee_username, category='1', which_group_id=group_id,writer=request.user)
					reply_id = reply.id
					add_group_invite(pk, group_id,reply_id)
					set_latest_group_reply(group_id,reply_id)
			request.session["unique_id"] = None
			request.session.modified = True
			return redirect("invite_private", slug=uuid)
	else:
		return redirect("group_page")

def invite_private(request, slug=None, *args, **kwargs):
	"""
	A redirect to InviteUsersToPrivateGroupView()

	Is a legacy view and should be excised from the code, it's a superfluous redirect
	"""
	if valid_uuid(slug):
		request.session["unique_id"] = slug
		return redirect("invite_private_group")
	else:
		return redirect("score_help")


class InviteUsersToPrivateGroupView(ListView):
	"""
	Renders list of currently online users, and allows inviter to select users from there for their private mehfil
	"""
	# model = Session
	template_name = "mehfil/invite_for_private_group.html"
	paginate_by = 100

	def get_queryset(self):
		if self.request.user_banned:
			return []
		else:
			# cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			# 'LOCATION': MEMLOC, 'TIMEOUT': 30,
			# })
			global condemned
			user_ids = get_most_recent_online_users()#cache_mem.get('online')
			try:
				group = Group.objects.get(unique=self.request.session["unique_id"])
				users_purified = [pk for pk in user_ids if pk not in condemned]
				non_invited_online_ids = bulk_check_group_invite(users_purified,group.id)
				non_invited_non_member_online_ids = bulk_check_group_membership(non_invited_online_ids,group.id)
				return User.objects.filter(id__in=non_invited_non_member_online_ids).values('id','userprofile__score','userprofile__avatar','username')
			except:
				return []

	def get_context_data(self, **kwargs):
		context = super(InviteUsersToPrivateGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["legit"] = FEMALES
			try:	
				unique = self.request.session["unique_id"]
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["authorized"] = True
				context["group"] = group
			except:
				context["authorized"] = False
		return context				


class InviteUsersToGroupView(ListView):
	"""
	Renders list of currently online users, and allows inviter to select users from there for their public mehfil
	"""
	# model = Session
	template_name = "mehfil/invite_for_groups.html"
	paginate_by = 100
	
	def get_queryset(self):
		if self.request.user_banned:
			return []
		else:
			# cache_mem = get_cache('django.core.cache.backends.memcached.MemcachedCache', **{
			# 'LOCATION': MEMLOC, 'TIMEOUT': 30,
			# })	
			global condemned
			user_ids = get_most_recent_online_users()#cache_mem.get('online')
			try:
				group = Group.objects.get(unique=self.request.session["public_uuid"])
				users_purified = [pk for pk in user_ids if pk not in condemned]
				non_invited_online_ids = bulk_check_group_invite(users_purified,group.id)
				non_invited_non_member_online_ids = bulk_check_group_membership(non_invited_online_ids,group.id)
				return User.objects.filter(id__in=non_invited_non_member_online_ids).values('id','userprofile__score','userprofile__avatar','username')
			except:
				return []

	def get_context_data(self, **kwargs):
		context = super(InviteUsersToGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				context["legit"] = FEMALES
				unique = self.request.session["public_uuid"]
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
			except:
				context["group"] = None
		return context

#################################### Mehfil creation ######################################

class GroupTypeView(FormView):
	"""
	Renders a 'choice' form when user tries to create a mehfil from the group page
	"""
	form_class = GroupTypeForm
	template_name = "mehfil/group_type.html"

class OpenGroupHelpView(FormView):
	"""
	Renders form where user has to decide whether they are willing to pay the required price
	"""
	form_class = OpenGroupHelpForm
	template_name = "mehfil/open_group_help.html"


class ClosedGroupHelpView(FormView):
	"""
	Renders form where user has to decide whether they are willing to pay the required price
	"""
	form_class = ClosedGroupHelpForm
	template_name = "mehfil/closed_group_help.html"	


def mehfil_help(request, pk=None, num=None, *args, **kwargs):
	if pk.isdigit() and num.isdigit():
		request.session['user_pk'] = pk
		request.session['link_id'] = num
		return redirect("mehfil_help")
	else:
		return redirect("score_help")


class MehfilView(FormView):
	form_class = MehfilForm
	template_name = "mehfil/mehfil_help.html"

	def get_context_data(self, **kwargs):
		context = super(MehfilView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				target_id = self.request.session['user_pk']
				link_id = self.request.session['link_id']
				context["target"] = User.objects.get(id=target_id)
				context["link_id"] = link_id
			except:
				context["target"] = None
				context["link_id"] = None
				return context
		return context

	def form_valid(self, form):
		if self.request.method == 'POST':
			user = self.request.user
			report = self.request.POST.get("decision")
			target = self.request.session['user_pk']
			link_id = self.request.session['link_id']
			self.request.session['link_id'] = None
			self.request.session['user_pk'] = None
			if link_id and report == 'Haan':
				if user.userprofile.score < 500:
					context = {'pk': link_id}
					return render(self.request, 'mehfil/penalty_linkmehfil.html', context)
				else:
					user.userprofile.score = user.userprofile.score - 500
					target_user = User.objects.get(id=target)
					invitee = target_user.username
					topic = invitee+" se gupshup"
					unique = uuid.uuid4()
					try:
						group = Group.objects.create(topic=topic, rules='', owner=user, private='1', unique=unique)
						reply_list = []
						seen_list = []
						reply = Reply.objects.create(text=invitee, category='1', which_group_id=group.id, writer=user)
						add_group_member(group.id, user.username)
						add_group_invite(target, group.id,reply.id)
						add_user_group(user.id, group.id)
						user.userprofile.save()
						self.request.session["unique_id"] = unique
						return redirect("private_group_reply")#, slug=unique)
					except:
						self.request.session["link_pk"] = link_id
						self.request.session.modified = True
						return redirect("publicreply_view")
			else:
				return redirect("home")


class DirectMessageCreateView(FormView):
	model = Group
	form_class = DirectMessageCreateForm

	def form_valid(self, form):
		if self.request.method == 'POST':
			pk = self.kwargs["pk"]
			user = User.objects.get(id=pk)
			user_score = self.request.user.userprofile.score
			if user_score > 500:
				self.request.user.userprofile.score = self.request.user.userprofile.score - 500
				invitee = user.username
				topic = invitee+" se gupshup"
				unique = uuid.uuid4()
				try:
					group = Group.objects.create(topic=topic, rules='', owner=self.request.user, private ='1', unique=unique)
					self.request.user.userprofile.save()
					reply_list=[]
					seen_list=[]
					reply = Reply.objects.create(text=invitee, category='1', which_group_id=group.id, writer=self.request.user)
					add_group_member(group.id, self.request.user.username)
					add_group_invite(pk, group.id,reply.id)
					add_user_group(self.request.user.id, group.id)
					self.request.session["unique_id"] = unique
					return redirect("private_group_reply")#, slug=unique)
				except:
					return redirect("profile", slug=invitee)
			else:
				return redirect("profile",slug=user.username)

class ClosedGroupCreateView(CreateView):
	model = Group
	form_class = ClosedGroupCreateForm
	template_name = "mehfil/new_closed_group.html"

	def form_valid(self, form):
		if self.request.user.userprofile.score > (PRIVATE_GROUP_COST-1):
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			user = self.request.user
			user_id = user.id
			f.owner = user
			f.private = 1
			unique = uuid.uuid4()
			f.unique = unique
			f.rules = ''
			f.category = '1'
			# set_prev_retort(user_id,f.topic)
			f.save()
			creation_text = 'mein ne new mehfil shuru kar di'
			reply = Reply.objects.create(text=creation_text,which_group=f,writer_id=user_id)
			reply_time = convert_to_epoch(reply.submitted_on)
			try:
				url = user.userprofile.avatar.url
			except ValueError:
				url = None
			create_object(object_id=f.id, object_type='3',object_owner_id=user_id,object_desc=f.topic,lt_res_time=reply_time,\
				lt_res_avurl=url,lt_res_sub_name=user.username,lt_res_text=creation_text,group_privacy=f.private, slug=f.unique,\
				lt_res_wid=user_id)
			create_notification(viewer_id=user_id,object_id=f.id,object_type='3',seen=True,updated_at=reply_time,unseen_activity=True)
			f.owner.userprofile.score = f.owner.userprofile.score - PRIVATE_GROUP_COST
			f.owner.userprofile.save()
			add_group_member(f.id, self.request.user.username)
			add_user_group(user_id, f.id)
			try: 
				return redirect("invite_private", slug=f.unique)
			except:
				self.request.session["unique_id"] = f.unique
				return redirect("private_group_reply")#, slug=unique)
		else:
			return redirect("group_page")


class OpenGroupCreateView(CreateView):
	model = Group
	form_class = OpenGroupCreateForm
	template_name = "mehfil/new_open_group.html"

	def get_form_kwargs( self ):
		kwargs = super(OpenGroupCreateView,self).get_form_kwargs()
		kwargs['verified'] = self.request.mobile_verified
		return kwargs

	def form_valid(self, form):
		if self.request.user.userprofile.score > (PUBLIC_GROUP_COST-1):
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			user = self.request.user
			user_id = user.id
			f.owner = user
			f.private = 0
			unique = uuid.uuid4()
			f.unique = unique
			# set_prev_retort(user_id,f.topic)
			f.save()
			creation_text = 'mein ne new mehfil shuru kar di'
			reply = Reply.objects.create(text=creation_text,which_group=f,writer=user)
			reply_time = convert_to_epoch(reply.submitted_on)
			try:
				url = user.userprofile.avatar.url
			except ValueError:
				url = None
			f_id = f.id
			create_object(object_id=f_id, object_type='3',object_owner_id=user_id,object_desc=f.topic,lt_res_time=reply_time,\
				lt_res_avurl=url,lt_res_sub_name=user.username,lt_res_text=creation_text,group_privacy=f.private, slug=f.unique,\
				lt_res_wid=user_id)
			create_notification(viewer_id=user_id,object_id=f_id,object_type='3',seen=True,updated_at=reply_time,unseen_activity=True)
			rank_public_groups.delay(group_id=f_id,writer_id=user_id)
			public_group_attendance_tasks.delay(group_id=f_id, user_id=user_id)
			link = Link.objects.create(submitter=user, description=f.topic, cagtegory='2', url=unique)
			try:
				av_url = f.owner.userprofile.avatar.url
			except ValueError:
				av_url = None
			add_home_link(link_pk=link.id, categ='2', nick=f.owner.username, av_url=av_url, desc=f.topic, \
				scr=f.owner.userprofile.score, cc=1, writer_pk=user_id, device='1', meh_url=unique,\
				by_pinkstar = (True if f.owner.username in FEMALES else False))
			if self.request.user_banned:
				extras = add_unfiltered_post(link.id)
				if extras:
					queue_for_deletion.delay(extras)
			else:
				add_filtered_post(link.id)
				extras = add_unfiltered_post(link.id)
				if extras:
					queue_for_deletion.delay(extras)
			f.owner.userprofile.score = f.owner.userprofile.score - PUBLIC_GROUP_COST
			f.owner.userprofile.save()
			add_group_member(f_id, user.username)
			add_user_group(user_id, f_id)
			try: 
				return redirect("invite", slug=unique)
			except:
				return redirect("public_group", slug=unique)
		else:
			return redirect("group_page")

def direct_message(request, pk=None, *args, **kwargs):
	if pk.isdigit():
		request.session["dm"] = pk
		return redirect("direct_message_help")
	else:
		return redirect("score_help")

class DirectMessageView(FormView):
	form_class = DirectMessageForm
	template_name = "mehfil/direct_message_help.html"

	def get_context_data(self, **kwargs):
		context = super(DirectMessageView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["nopk"] = False
			try:
				pk = self.request.session["dm"]
				self.request.session["dm"] = None
				self.request.session.modified = True
			except:
				context["nopk"] = True
				context["target"] = None
				return context
			if pk:
				target = User.objects.get(id=pk)
				context["target"] = target
			else:
				context["nopk"] = True
				context["target"] = None
				return context
		return context


############################## Deleting or exiting public and private mehfils ##############################

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def leave_public_group(request):
	"""
	Displays public group abandonment options

	"""
	if request.method == "POST":
		pk = request.POST.get("gid",None)
		unique = request.POST.get("guuid",None)
		private = request.POST.get("prv",None)
		inside_grp = request.POST.get('insg',None)
		group = Group.objects.get(id=pk)
		if group.owner == request.user:
			context={'unique':unique, 'pk':pk, 'private':private,'topic':group.topic, 'inside_grp':inside_grp}
			return render(request, 'mehfil/delete_public_group.html', context)
		else:
			context={'unique':unique, 'pk':pk, 'private':private,'topic':group.topic, 'inside_grp':inside_grp}
			return render(request, 'mehfil/leave_public_group.html', context)
	else:
		return redirect("group_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def leave_private_group(request, *args, **kwargs):
	"""
	Displays private group abandonment options

	"""
	if request.method == "POST":
		pk = request.POST.get("gid",None)
		unique = request.POST.get("guuid",None)
		private = request.POST.get("prv",None)
		inside_grp = request.POST.get('insg',None)
		topic = Group.objects.get(id=pk).topic
		context={'unique':unique, 'pk':pk, 'private':private,'topic':topic, 'inside_grp':inside_grp}
		return render(request, 'mehfil/leave_private_group.html', context)
	else:
		return redirect("group_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def left_private_group(request, *args, **kwargs):
	"""
	Processes leaving a private mehfil
	"""
	if request.method=="POST":
		user_id = request.user.id
		pk = request.POST.get("gid",None)
		private = request.POST.get("prv",None)
		unique = request.POST.get("guid",None)
		if request.is_feature_phone:
			device = '1'
		elif request.is_phone:
			device = '2'
		elif request.is_tablet:
			device = '4'
		elif request.is_mobile:
			device = '5'
		else:
			device = '3'
		if check_group_member(pk, request.user.username):
			memcount = remove_group_member(pk, request.user.username) #group membership is truncated
			remove_user_group(user_id, pk) #user's groups are truncated
			remove_group_notification(user_id,pk) #group removed from user's notifications
			if memcount < 1:
				remove_group_object(pk)
			Reply.objects.create(which_group_id=pk, writer_id=user_id, text='leaving group', category='6', device=device)
		elif check_group_invite(user_id, pk):
			remove_group_invite(user_id, pk)
			Reply.objects.create(which_group_id=pk, writer_id=user_id, text='unaccepted invite', category='7', device=device)
		else:
			pass
	return redirect("group_page")


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def left_public_group(request, *args, **kwargs):
	"""
	Processes leaving a public mehfil
	"""
	if request.method == "POST":
		pk = request.POST.get("pk",None)
		inside_group = request.POST.get("igrp",None)
		unique = request.POST.get("slug",None)
		leaving_decision = request.POST.get("ldec",None)
		if leaving_decision == '1':
			username = request.user.username
			user_id = request.user.id
			if check_group_member(pk, username):
				remove_group_member(pk, username)
				remove_user_group(user_id, pk)
				remove_group_notification(user_id,pk)
			elif check_group_invite(user_id, pk):
				remove_group_invite(user_id, pk)
			else:
				pass
			return redirect("group_page")
		else:
			if inside_group == '1':
				return redirect("public_group", slug=unique)
			else:
				return redirect("group_page")
	return redirect("group_page")


def del_public_group(request, pk=None, unique=None, private=None, *args, **kwargs):
	"""
	Processes public mehfil deletion
	"""
	group = Group.objects.get(id=pk)
	member_ids = list(User.objects.filter(username__in=get_group_members(pk)).values_list('id',flat=True))
	if group.owner == request.user:
		remove_group_notification(user_id=request.user.id,group_id=pk)
		del_from_rankings(pk)
		del_attendance(pk)
		remove_group_object(pk)
		remove_all_group_members(pk)
		remove_latest_group_reply(pk)
		remove_group_for_all_members(pk,member_ids)
		GroupBanList.objects.filter(which_group_id=pk).delete()
		GroupCaptain.objects.filter(which_group_id=pk).delete()
		Group.objects.get(id=pk).delete()
		return redirect("group_page")
	else:
		context={'private':'0','unique':unique}
		return render(request,'mehfil/penalty_groupbanned.html', context)



############################## Public mehfil administration ##############################

def appoint_pk(request, pk=None, app=None, *args, **kwargs):
	if pk.isdigit() and app.isdigit():
		request.session["appoint_id"] = pk
		request.session["appoint_decision"] = app
		return redirect("appoint")
	else:
		return redirect("score_help")

class AppointCaptainView(FormView):
	form_class = AppointCaptainForm
	template_name = "mehfil/appoint_captain.html"

	def get_context_data(self, **kwargs):
		context = super(AppointCaptainView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				user_id = self.request.session["appoint_id"]
				unique_id = self.request.session["public_uuid"]
				decision = self.request.session["appoint_decision"]
				context["authorized"] = True
				context["candidate"] = User.objects.get(id=user_id)
				context["appoint"] = decision
				context["unique"] = unique_id
			except:
				context["authorized"] = False
				context["candidate"] = None
				context["appoint"] = None
				context["unique"] = None
		return context

	def form_valid(self, form):
		#f = form.save(commit=False)
		if self.request.user_banned:
			return render(self.request,'500.html',{}) #errorbanning
		else:
			candidate = self.request.session["appoint_id"]
			self.request.session["appoint_id"] = None
			unique = self.request.session["public_uuid"]
			group = Group.objects.get(unique=unique)
			appoint = self.request.session["appoint_decision"]
			self.request.session["appoint_decision"] = None
			self.request.session.modified = True
			if appoint == '1' and group.owner == self.request.user and not \
			GroupCaptain.objects.filter(which_user_id = candidate, which_group=group).exists():
				GroupCaptain.objects.create(which_user_id=candidate,which_group=group)
			elif appoint == '0' and group.owner == self.request.user:
				try:
					GroupCaptain.objects.get(which_user_id=candidate,which_group=group).delete()
				except:
					return redirect("owner_group_online_kon")
			else:
				return redirect("public_group", slug=unique)
			return redirect("owner_group_online_kon")

class OwnerGroupOnlineKonView(ListView):
	model = GroupTraffic
	form_class = OwnerGroupOnlineKonForm
	template_name = "mehfil/owner_group_online_kon.html"

	def get_context_data(self, **kwargs):
		context = super(OwnerGroupOnlineKonView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			global condemned
			context["unauthorized"] = False
			context["legit"] = FEMALES
			try:
				unique = self.request.session["public_uuid"]
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
			except:
				context["group"] = None
				context["unauthorized"] = True
				context["groupies"] = []
				return context
			if group.owner == self.request.user and group.private == '0':
				all_online_ids = get_attendance(group.id)
				visitors = User.objects.select_related('userprofile').filter(id__in=all_online_ids)
				captain_ids = GroupCaptain.objects.filter(which_user_id__in=all_online_ids, which_group=group).values_list("which_user_id",flat=True)
				captains = {captain:captain for captain in captain_ids}
				groupies = []
				for visitor in visitors:
					if visitor.id in captains.keys():
						groupies.append((visitor,visitor.id))
					else:
						groupies.append((visitor,None))
				context["groupies"] = groupies
			else:
				context["groupies"] = []
				context["unauthorized"] = True
		return context

class GroupOnlineKonView(ListView):
	model = GroupTraffic
	form_class = GroupOnlineKonForm
	template_name = "mehfil/group_online_kon.html"
	paginate_by = 75

	def get_context_data(self, **kwargs):
		context = super(GroupOnlineKonView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			global condemned
			context["unauthorized"] = False
			context["legit"] = FEMALES
			try:
				unique = self.request.session["public_uuid"]
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
			except:
				context["group"] = None
				context["unauthorized"] = True
				context["groupies"] = []
				return context
			if group.private == '0':
				all_online_ids = get_attendance(group.id)
				visitors = User.objects.select_related('userprofile').filter(id__in=all_online_ids)
				captain_ids = GroupCaptain.objects.filter(which_group=group, which_user_id__in=all_online_ids).values_list('which_user_id', flat=True)
				captains = {captain:captain for captain in captain_ids}
				groupies = []
				for visitor in visitors:
					if visitor.id in captains.keys():
						groupies.append((visitor,visitor.id))
					else:
						groupies.append((visitor,None))
				context["groupies"] = groupies
			else:
				context["group"] = None
				context["unauthorized"] = True
				context["groupies"] = []
		return context

########################## Popular mehfil list #########################

# def get_ranked_groups(request):
#     """
#     Displays top public mehfils, sorted by 'stickiness'
#     """
#     """
#     ('5',12) does not exist in test_list (used for testing purposes)
	
#     test_list = [('12',12),('54',11),('78',54),('11',12),('53',11),('77',54),('13',12),('55',11),('79',54),\
#     ('4',12),('56',11),('80',54),('5',12),('50',11),('81',54),('2',12),('44',11),('72',54),('1',12),('45',11)\
#     ,('10',54),('34',12),('35',11),('36',54),('39',54),('37',12),('38',11)]
	
#     group_ids_list = test_list
#     """
#     groups_data = retrieve_cached_ranked_groups()
#     if groups_data:
#         trending_groups = json.loads(groups_data)
#     else:
#         trending_groups = []
#         group_ids_list = get_ranked_public_groups()#get_ranked_mehfils()
#         group_ids_dict = dict(group_ids_list)
#         group_ids = map(itemgetter(0), group_ids_list)
#         groups = retrieve_group_owner_unames_and_uniques_and_topics_in_bulk(group_ids)
#         for group in groups:
#             if group['oun']:
#                 group_id = group['gi']
#                 trending_groups.append((group['oun'],group['tp'],group['u'],group_id,group_ids_dict[group_id]))#group_ids_dict[group_id] is group_score
#         trending_groups.sort(key=itemgetter(4), reverse=True)
#         cache_ranked_groups(json.dumps(trending_groups))
#     return render(request,"mehfil/group_ranking.html",{'object_list':trending_groups})

def get_ranked_groups(request):
	"""
	Displays top public mehfils, sorted by 'stickiness'
	"""
	groups_data = retrieve_cached_ranked_groups()
	if groups_data:
		trending_groups = json.loads(groups_data)
	else:
		trending_groups = []
		group_ids_list = get_ranked_public_groups()#get_ranked_mehfils()
		group_ids_dict = dict(group_ids_list)
		group_ids = map(itemgetter(0), group_ids_list)
		groups = Group.objects.select_related('owner').filter(id__in=group_ids)
		for group in groups:
			group_id = str(group.id)
			trending_groups.append((group,group_ids_dict[group_id]))
		trending_groups.sort(key=itemgetter(1), reverse=True)
		trending_groups = map(itemgetter(0), trending_groups)
		group_data = []
		for group in trending_groups:			
			group_list=[]
			group_list.append(group.owner.username)
			group_list.append(group.topic)
			group_list.append(group.unique) 
			group_data.append(group_list)		
		cache_ranked_groups(json.dumps(group_data))
		trending_groups = group_data
	return render(request,"mehfil/group_ranking.html",{'object_list':trending_groups})


#################### Rendering list of all mehfils #####################


class GroupPageView(ListView):
	"""
	Renders list of all joined and invited mehfils (public and private both)

	DEPRECATE LATER (ALONGWITH REDIS 1 GROUP FUNCTIONALITY)
	"""
	# model = Reply
	form_class = GroupPageForm
	template_name = "mehfil/group.html"
	paginate_by = 20

	def get_queryset(self):
		groups = []
		replies = []
		user_id = self.request.user.id
		group_ids = get_user_groups(user_id)
		replies = filter(None, get_latest_group_replies(group_ids))#'latest_group_reply' is the latest reply in any given group, saved with a TTL of TWO WEEKS
		invite_reply_ids = get_active_invites(user_id) #contains all current invites (they have associated replies to them)
		invite_reply_ids |= set(replies) #doing union of two sets. Gives us all latest reply ids, minus any deleted replies (e.g. if the group object had been deleted)
		replies_qset = Reply.objects.filter(id__in=invite_reply_ids).values('id','category','text','submitted_on','which_group','writer__username',\
			'which_group__topic','which_group__unique','writer__userprofile__avatar','which_group__private').order_by('-id')[:80]
		return get_replies_with_seen(group_replies=replies_qset,viewer_id=user_id,object_type='3')

	def get_context_data(self, **kwargs):
		context = super(GroupPageView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			context["verified"] = FEMALES
			context["own_uname"] = retrieve_uname(self.request.user.id, decode=True)
		return context


############################## Changing public and private mehfil topic ##############################


class ChangeGroupRulesView(CreateView):
	"""
	Renders public mehfil change rules form and processes new POST requests
	"""
	model = Group
	form_class = ChangeGroupRulesForm
	template_name = "mehfil/change_group_rules.html"

	def get_context_data(self, **kwargs):
		context = super(ChangeGroupRulesView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			unique = self.request.session["public_uuid"]
			context["unique"] = unique
			group = Group.objects.get(unique=unique)
			context["group"] = group
			if group.private == '0':
				if not group.owner == user:
					context["unauthorized"] = True
				else:
					context["unauthorized"] = False
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		user = self.request.user
		if self.request.user_banned:
			return redirect("profile", slug=user.username)
		else:
			rules = self.request.POST.get("rules")
			unique = self.request.session["public_uuid"]
			group = Group.objects.get(unique=unique)
			if group.private == '0' and group.owner != user:
				return redirect("score_help")
			group.rules = rules
			group.save()
			Reply.objects.create(text=rules ,which_group=group ,writer=user ,category='5')
			return redirect("public_group", slug=unique)	


class ChangePrivateGroupTopicView(CreateView):
	model = Group
	form_class = ChangePrivateGroupTopicForm
	template_name = "mehfil/change_private_group_topic.html"

	def get_context_data(self, **kwargs):
		context = super(ChangePrivateGroupTopicView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			# banned, ban_type, time_remaining, warned = private_group_posting_allowed(self.request.user.id)
			# banned = False
			unique = self.request.session.get("unique_id",None)
			if unique:# and not banned:	
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
				if group.private == '0' or group.private == '2':
					context["unauthorized"] = True
					context["group"] = None
					return context
			else:
				context["unauthorized"] = True
				context["group"] = None
				return context
		return context

	def form_valid(self, form):
		user = self.request.user
		if self.request.user_banned:
			return render(self.request,'500.html',{})
		else:
			# topic = self.request.POST.get("topic")
			topic = form.cleaned_data.get("topic")
			unique = self.request.session["unique_id"]
			group = Group.objects.get(unique=unique)
			if (group.private == '0' or group.private == '2') and group.owner != user:
				return redirect("score_help")
			group.topic = topic
			group.save()
			if self.request.is_feature_phone:
				device = '1'
			elif self.request.is_phone:
				device = '2'
			elif self.request.is_tablet:
				device = '4'
			elif self.request.is_mobile:
				device = '5'
			else:
				device = '3'
			Reply.objects.create(text=topic ,which_group=group , writer=user, category='4', device=device)
			self.request.session["unique_id"] = unique
			return redirect("private_group_reply")#, slug=unique)

class ChangeGroupTopicView(CreateView):
	"""
	Changes the topic of a public mehfil
	"""
	model = Group
	form_class = ChangeGroupTopicForm
	template_name = "mehfil/change_group_topic.html"

	def get_context_data(self, **kwargs):
		context = super(ChangeGroupTopicView, self).get_context_data(**kwargs)
		user = self.request.user
		context["unauthorized"] = False
		if user.is_authenticated():
			unique = self.request.session["public_uuid"]
			if unique:	
				context["unique"] = unique
				group = Group.objects.get(unique=unique)
				context["group"] = group
				if group.private == '0':
					if not group.owner == user:
						context["unauthorized"] = True
					else:
						context["unauthorized"] = False
			else:
				context["unauthorized"] = True
				return context
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		user = self.request.user
		if self.request.user_banned:
			return render(self.request,'500.html',{})
		else:
			# topic = self.request.POST.get("topic")
			topic = form.cleaned_data.get("topic")
			unique = self.request.session['public_uuid']
			group = Group.objects.get(unique=unique)
			if group.private == '0' and group.owner != user:
				return redirect("score_help")
			group.topic = topic
			group.save()
			Reply.objects.create(text=topic ,which_group=group , writer=user, category='4')
			return redirect("public_group", slug=unique)

############################## Rendering and posting to private mehfil ##############################


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@sensitive_post_parameters()
@csrf_protect
def priv_group(request,*args,**kwargs):
	"""
	Redirecting incoming to PrivateGroupView()
	"""	
	if request.method == 'POST':
		slug = request.POST.get("private_uuid")
		if valid_uuid(slug):
			request.session["unique_id"] = slug
			return redirect("private_group_reply")
		else:
			return redirect("group_page")	
	else:
		return redirect("group_page")


class PrivateGroupView(CreateView): #get_queryset doesn't work in CreateView (it's a ListView thing!)
	"""
	Renders and processes submissions to private mehfil
	"""
	model = Reply
	form_class = PrivateGroupReplyForm		
	template_name = "mehfil/private_group_reply.html"

	@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
	def dispatch(self, request, *args, **kwargs):
		# Try to dispatch to the right method; if a method doesn't exist,
		# defer to the error handler. Also defer to the error handler if the
		# request method isn't on the approved list.
		if request.method.lower() in self.http_method_names:
			handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
		else:
			handler = self.http_method_not_allowed
		self.request = request
		self.args = args
		self.kwargs = kwargs
		return handler(request, *args, **kwargs)

	def get_form_kwargs( self ):
		kwargs = super(PrivateGroupView,self).get_form_kwargs()
		kwargs['user_id'] = self.request.user.id
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(PrivateGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			try:
				unique = self.request.session['unique_id']
			except:
				context["switching"] = True
				return context
			if unique:
				context["unique"] = unique
			else:
				context["switching"] = True
				return context
			try:
				group = Group.objects.get(unique=unique)#get DB call
			except:
				context["switching"] = True
				return context
			context["group"] = group
			if 'private' in self.request.path and group.private=='1':
				user_id = self.request.user.id
				group_id = group.id
				secret_key = uuid.uuid4()
				context["sk"] = secret_key
				set_text_input_key(user_id, group_id, 'prv_grp', secret_key)
				on_fbs = self.request.META.get('HTTP_X_IORG_FBS',False)
				context["score"] = self.request.user.userprofile.score
				context["switching"] = False
				context["ensured"] = FEMALES
				context["mobile_verified"] = self.request.mobile_verified
				replies = Reply.objects.select_related('writer__userprofile').defer('writer__userprofile__attractiveness',\
					'writer__userprofile__mobilenumber','writer__userprofile__previous_retort','writer__userprofile__age',\
					'writer__userprofile__gender','writer__userprofile__bio','writer__userprofile__streak','writer__userprofile__media_score',\
					'writer__userprofile__shadi_shuda','writer__userprofile__id','writer__is_superuser','writer__first_name','writer__last_name',\
					'writer__last_login','writer__email','writer__date_joined','writer__is_staff','writer__is_active','writer__password').\
				filter(which_group_id=group_id).order_by('-submitted_on')[:25]
				time_now = timezone.now()
				updated_at = convert_to_epoch(time_now)
				log_private_mehfil_session.delay(group_id, user_id)
				save_user_presence(user_id,group.id,updated_at)
				pres_dict = get_latest_presence(group_id,set(reply.writer_id for reply in replies))
				context["replies"] = [(reply,reply.writer,pres_dict[reply.writer_id]) for reply in replies]
				context["unseen"] = False
				if not self.request.user_banned:#do the following ONLY if user isn't hell-banned
					members = get_group_members(group_id)
					context["members"] = members #contains members' usernames
					if members and replies and self.request.user.username in members:
						# flip "unseen" notification here
						context["unseen"] = True #i.e. the user is a member and replies exist; the prospect of unseen replies exists
						update_notification(viewer_id=user_id, object_id=group_id, object_type='3', seen=True, \
							updated_at=updated_at, single_notif=False, unseen_activity=True, priority='priv_mehfil',
							bump_ua=False) #just seeing means notification is updated, but not bumped up in ua:
						try:
							#finding latest time user herself replied
							context["reply_time"] = max(reply.submitted_on for reply in replies if str(reply.writer) == str(self.request.user))
						except:
							context["reply_time"] = None #i.e. it's the first reply in the last 25 replies (i.e. all were unseen)
					else:
						context["reply_time"] = None
			else:
				context["switching"] = True
		return context

	def form_valid(self, form): #this processes the form before it gets saved to the database
		if self.request.user_banned:
			return render(self.request,'500.html',{})
		else:
			user_id = self.request.user.id
			if self.request.user.userprofile.score < -25:
				HellBanList.objects.create(condemned=self.request.user)
				self.request.user.userprofile.score = random.randint(10,71)
				self.request.user.userprofile.save()
				return redirect("group_page")
			pk = self.request.POST.get('gp',None)
			which_group = Group.objects.get(pk=pk)
			which_group_id, unique = pk, which_group.unique
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			text = f.text #text of the reply
			UserProfile.objects.filter(user_id=user_id).update(score=F('score')+PRIVATE_GROUP_MESSAGE)
			if f.image:
				on_fbs = self.request.META.get('HTTP_X_IORG_FBS',False)
				if on_fbs:
					if f.image.size > 200000:
						context = {'pk':'pk'}
						return render(self.request,'big_photo_fbs.html',context)
					else:
						pass
				else:
					if f.image.size > 10000000:
						context = {'pk':'pk'}
						return render(self.request,'big_photo_regular.html',context)
					else:
						pass
				image_file = clean_image_file(f.image)
				if image_file is False:
					return render(self.request, 'big_photo.html', {'photo':'prv_grp'})
				else:
					f.image = image_file
			else: 
				f.image = None
			if self.request.is_feature_phone:
				device = '1'
			elif self.request.is_phone:
				device = '2'
			elif self.request.is_tablet:
				device = '4'
			elif self.request.is_mobile:
				device = '5'
			else:
				device = '3'
			set_input_rate_and_history.delay(section='prv_grp',section_id=which_group_id,text=text,user_id=user_id,time_now=time.time())
			reply = Reply.objects.create(writer=self.request.user, which_group=which_group, text=text, image=f.image, \
				device=device)
			add_group_member(which_group_id, self.request.user.username)
			remove_group_invite(user_id, which_group_id)
			add_user_group(user_id, which_group_id)
			reply_time = convert_to_epoch(reply.submitted_on)
			try:
				url=self.request.user.userprofile.avatar.url
			except ValueError:
				url=None
			try:
				image_url = reply.image.url
			except ValueError:
				image_url = None
			group_notification_tasks.delay(group_id=which_group_id,sender_id=user_id,group_owner_id=which_group.owner.id,\
				topic=which_group.topic,reply_time=reply_time,poster_url=url,poster_username=self.request.user.username,\
				reply_text=text,priv=which_group.private,slug=unique,image_url=image_url,priority='priv_mehfil',\
				from_unseen=False, reply_id=reply.id)
			self.request.session['unique_id'] = unique
			self.request.session.modified = True
			return redirect("private_group_reply")


############################## Rendering and posting to public mehfil ##############################


def public_group_request_denied(request):
	"""
	Renders errors resulting from posting in a public mehfil
	"""
	which_msg = request.session.pop("public_group_request_denied",None)
	if which_msg == '1':
		return render(request,'big_photo_fbs.html',{'pk':'pk'})
	elif which_msg == '2':
		return render(request,'big_photo_regular.html',{'origin':'pub_grp'})
	elif which_msg == '3':
		return render(request, 'big_photo.html', {'photo':'pub_grp'})
	else:
		return redirect("missing_page")


class PublicGroupView(CreateView):
	model = Reply
	form_class = PublicGroupReplyForm
	template_name = "mehfil/public_group_reply.html"

	@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
	def dispatch(self, request, *args, **kwargs):
		# Try to dispatch to the right method; if a method doesn't exist,
		# defer to the error handler. Also defer to the error handler if the
		# request method isn't on the approved list.
		if request.method.lower() in self.http_method_names:
			handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
		else:
			handler = self.http_method_not_allowed
		self.request = request
		self.args = args
		self.kwargs = kwargs
		return handler(request, *args, **kwargs)

	def get_form_kwargs(self):
		kwargs = super(PublicGroupView,self).get_form_kwargs()
		kwargs['user_id'] = self.request.user.id
		kwargs['is_mob_verified'] = self.request.mobile_verified
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(PublicGroupView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			# pk = self.request.POST.get('gp',None)
			unique = self.request.session.get("public_uuid",None)
			try:
				# group = Group.objects.get(pk=pk)
				group = Group.objects.get(unique=unique)
				context["unique"] = unique
			except Group.DoesNotExist:
				context["switching"] = True
				context["group_banned"] = False
				return context
			if 'awami' in self.request.path and group.private == '0': 
				user_id, group_id = self.request.user.id, group.id
				secret_key = uuid.uuid4()
				context["sk"] = secret_key
				set_text_input_key(user_id, group_id, 'pub_grp', secret_key)
				context["form"] = self.request.session.pop("public_group_form") if "public_group_form" in self.request.session else \
				PublicGroupReplyForm()
				context["score"] = self.request.user.userprofile.score
				context["switching"] = False
				context["group"] = group
				if GroupBanList.objects.filter(which_user_id=user_id,which_group_id=group_id).exists():
					context["group_banned"]=True
					culprit_username = self.request.user.username
					if check_group_member(group_id, culprit_username):
						remove_group_member(group_id, culprit_username)
						remove_group_notification(user_id,group_id)
						remove_user_group(user_id, group_id)
					elif check_group_invite(user_id, group_id):
						remove_group_invite(user_id, group_id)
					return context#no need to process more
				public_group_attendance_tasks.delay(group_id=group_id, user_id=user_id)
				context["ensured"] = FEMALES
				context["mobile_verified"] = self.request.mobile_verified
				replies = Reply.objects.select_related('writer__userprofile').filter(which_group_id=group_id).exclude(category='1').order_by('-submitted_on')[:25]#get DB call
				time_now = timezone.now()
				updated_at = convert_to_epoch(time_now)
				save_user_presence(user_id,group_id,updated_at)
				pres_dict = get_latest_presence(group_id,set(reply.writer_id for reply in replies))
				context["replies"] = [(reply,reply.writer,pres_dict[reply.writer_id]) for reply in replies]
				context["unseen"] = False
				context["on_fbs"] = self.request.META.get('HTTP_X_IORG_FBS',False)
				if not self.request.user_banned:#do the following ONLY if user isn't hell-banned
					members = get_group_members(group_id)
					if self.request.user.username in members and context["replies"]:
						update_notification(viewer_id=self.request.user.id, object_id=group_id, object_type='3', seen=True, \
							updated_at=updated_at, single_notif=False, unseen_activity=True, priority='public_mehfil', \
							bump_ua=False) #just seeing means notification is updated, but not bumped up in ua:
			else:
				context["switching"] = True
				context["group_banned"] = False
		return context

	def form_invalid(self, form):
		"""
		If the form is invalid, re-render the context data with the
		data-filled form and errors.
		"""
		self.request.session["public_group_form"] = form
		self.request.session.modified = True
		if self.request.is_ajax():
			return HttpResponse(json.dumps({'success':False,'message':reverse('public_group')}),content_type='application/json',)
		else:
			return self.render_to_response(self.get_context_data(form=form))

	def form_valid(self, form): #this processes the public form before it gets saved to the database
		"""
		If the form is valid, redirect to the supplied URL.
		"""
		is_ajax = self.request.is_ajax()
		if self.request.user_banned:
			if is_ajax:
				return HttpResponse(json.dumps({'success':False,'message':reverse('missing_page')}),content_type='application/json',)
			else:
				return redirect("missing_page")
		user_id = self.request.user.id
		pk = self.request.POST.get('gp',None)
		try:
			which_group = Group.objects.get(id=pk)
		except Group.DoesNotExist:
			if is_ajax:
				return HttpResponse(json.dumps({'success':False,'message':reverse('group_page')}),content_type='application/json',)
			else:
				return redirect("group_page")
		if GroupBanList.objects.filter(which_user_id=user_id, which_group_id=which_group.id).exists():
			if is_ajax:
				return HttpResponse(json.dumps({'success':False,'message':reverse('group_page')}),content_type='application/json',)
			else:
				return redirect("group_page")
		else:
			if self.request.user.userprofile.score < -25:#
				HellBanList.objects.create(condemned=self.request.user)
				self.request.user.userprofile.score = random.randint(10,71)
				self.request.user.userprofile.save()
				if is_ajax:
					return HttpResponse(json.dumps({'success':False,'message':reverse('group_page')}),content_type='application/json',)
				else:
					return redirect("group_page")
			f = form.save(commit=False) #getting form object, and telling database not to save (commit) it just yet
			set_input_rate_and_history.delay(section='pub_grp',section_id=which_group.id,text=f.text,user_id=user_id,time_now=time.time())
			UserProfile.objects.filter(user_id=user_id).update(score=F('score')+PUBLIC_GROUP_MESSAGE)
			self.request.session["public_uuid"] = which_group.unique
			self.request.session.modified = True
			if f.image and which_group.pics_ki_ijazat == '1':
				on_fbs = self.request.META.get('HTTP_X_IORG_FBS',False)
				if on_fbs:
					if f.image.size > 200000:
						self.request.session["public_group_request_denied"] = '1'
						self.request.session.modified = True
						if is_ajax:
							return HttpResponse(json.dumps({'success':False,'message':reverse('public_group_request_denied')}),content_type='application/json',)
						else:
							return redirect("public_group_request_denied")
				else:
					if f.image.size > 10000000:
						self.request.session["public_group_request_denied"] = '2'
						self.request.session.modified = True
						if is_ajax:
							return HttpResponse(json.dumps({'success':False,'message':reverse('public_group_request_denied')}),content_type='application/json',)
						else:
							return redirect("public_group_request_denied")
				image_file = clean_image_file(f.image, already_reoriented=self.request.POST.get('reoriented',None),\
					already_resized=self.request.POST.get('resized',None))
				if image_file is False:
					self.request.session["public_group_request_denied"] = '3'
					self.request.session.modified = True
					if is_ajax:
						return HttpResponse(json.dumps({'success':False,'message':reverse('public_group_request_denied')}),content_type='application/json',)
					else:
						return redirect('public_group_request_denied')
				else:
					f.image = image_file
			else: 
				f.image = None
			if self.request.is_feature_phone:
				device = '1'
			elif self.request.is_phone:
				device = '2'
			elif self.request.is_tablet:
				device = '4'
			elif self.request.is_mobile:
				device = '5'
			else:
				device = '3'
			which_group_id = which_group.id
			reply = Reply.objects.create(writer_id=user_id, which_group=which_group, text=f.text, image=f.image, device=device)#
			add_group_member(which_group_id, self.request.user.username)
			remove_group_invite(user_id, which_group_id)
			add_user_group(user_id, which_group_id)
			reply_time = convert_to_epoch(reply.submitted_on)
			try:
				url=self.request.user.userprofile.avatar.url
			except ValueError:
				url=None
			try:
				image_url = reply.image.url
			except ValueError:
				image_url = None
			rank_public_groups.delay(group_id=which_group_id,writer_id=user_id)
			public_group_attendance_tasks.delay(group_id=which_group_id, user_id=user_id)
			group_notification_tasks.delay(group_id=which_group_id,sender_id=user_id,group_owner_id=which_group.owner.id,\
				topic=which_group.topic,reply_time=reply_time,poster_url=url,poster_username=self.request.user.username,\
				reply_text=f.text,priv=which_group.private,slug=which_group.unique,image_url=image_url,priority='public_mehfil',\
				from_unseen=False, reply_id=reply.id)
			if is_ajax:
				return HttpResponse(json.dumps({'success':False,'message':reverse('public_group')}),content_type='application/json',)
			else:
				return redirect("public_group")


@ratelimit(rate='3/s')
def public_group(request, slug=None, *args, **kwargs):
	was_limited = getattr(request, 'limits', False)
	if not slug:
		slug = request.session.get("public_uuid",None)
	else:
		request.session["public_uuid"] = slug
		request.session.modified = True
	if valid_uuid(slug):
		if was_limited:
			return redirect("missing_page")
		else:
			return redirect("public_group_reply")
	else:
		return redirect("group_page")

#################### Refreshing mehfils #####################

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def first_time_public_refresh(request):
	"""
	Using the refresh button for the first time in a public mehfil
	"""
	if request.method == "POST":
		unique = request.POST.get('uid',None)
		if first_time_refresher(request.user.id):
			add_refresher(request.user.id)
			context = {'unique': unique}
			return render(request, 'mehfil/public_mehfil_refresh.html', context)
		else:
			return redirect("public_group", unique)
	else:
		return redirect("public_group")



@ratelimit(rate='3/s')
def first_time_refresh(request, unique=None, *args, **kwargs):
	"""
	Using the refresh button for the first time in a private mehfil
	"""
	was_limited = getattr(request, 'limits', False)
	if was_limited:
		# if request.user.is_authenticated():
		# 	deduction = 1 * -1
		# 	request.user.userprofile.score = request.user.userprofile.score + deduction
		# 	request.user.userprofile.save()
		# 	context = {'unique': unique}
		# 	return render(request, 'mehfil_refresh_penalty.html', context)
		# else:
		# 	context = {'unique': 'none'}
		# 	return render(request, 'mehfil_refresh_penalty.html', context)
		return redirect("missing_page")
	else:
		if first_time_refresher(request.user.id):
			add_refresher(request.user.id)
			context = {'unique': unique}
			return render(request, 'mehfil/mehfil_refresh.html', context)
		else:
			request.session["unique_id"] = unique
			return redirect("private_group_reply")#, slug=unique)


############################## Mehfil punishments ##############################

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def kick_pk(request, *args, **kwargs):
	"""
	Processing the kicking-out of an errant user from a public mehfil
	"""
	if request.user_banned:
		return redirect("missing_page")
	elif request.method == "POST":
		kick_decision = request.POST.get("kdec",None)
		decision = request.POST.get("dec",None)
		slug = request.POST.get("slug",None)
		writer_id = request.POST.get("pk",None)
		if decision == 'rem':
			context = {}
			context["unique"] = slug
			group = Group.objects.get(unique=slug)
			context["unauthorized"] = False
			if group.private != '0':
				context["unauthorized"] = True
			context["owner"] = group.owner
			if group.owner != request.user:
				context["culprit"] = request.user
			else:
				if Reply.objects.filter(writer_id=writer_id,which_group=group).exists():
					culprit_username = User.objects.filter(id=writer_id).values_list('username',flat=True)[0]
					context["culprit_username"] = culprit_username
					context["pk"] = writer_id
				else:
					context["unauthorized"] = True
			return render(request,"mehfil/kick.html",context)
		elif kick_decision == '1':
			if request.user.userprofile.score < -25:
				HellBanList.objects.create(condemned=request.user)
				request.user.userprofile.score = random.randint(10,71)
				request.user.userprofile.save()
				return redirect("group_page")
			else:
				try:
					group = Group.objects.get(unique=slug)
				except Group.DoesNotExist:
					return redirect("group_page")
				if group.private == '0':
					if group.owner != request.user:
						return redirect("public_group", slug=slug)
					elif writer_id == str(request.user.id):
						return redirect("public_group", slug=slug)
					else:
						group_id = group.id
						culprit_username = User.objects.filter(id=writer_id).values_list('username',flat=True)[0]
						is_member = check_group_member(group_id, culprit_username)
						recently_online_ids = get_attendance(group_id)
						if not is_member and writer_id not in recently_online_ids:
							return redirect("public_group", slug=slug)	
						if GroupBanList.objects.filter(which_user_id=writer_id, which_group_id=group_id).exists():# already kicked and banned
							return redirect("public_group", slug=slug)
						else:
							GroupBanList.objects.create(which_user_id=writer_id,which_group_id=group_id)#placing the person in ban list
							try:
								GroupCaptain.objects.get(which_user_id=writer_id, which_group_id=group_id).delete()
							except:
								pass
							if is_member:
								remove_group_member(group_id, culprit_username)
								remove_group_notification(writer_id,group_id)
								remove_user_group(writer_id, group_id)
								UserProfile.objects.filter(user_id=writer_id).update(score=F('score')-50) #punish the kickee
							elif check_group_invite(writer_id, group_id):
								remove_group_invite(writer_id, group_id)
							reply = Reply.objects.create(text=culprit_username, which_group_id=group_id, writer=request.user, category='2')
							return redirect("public_group", slug=slug)
				else:
					return redirect("group_page")			
		else:
			return redirect("public_group", slug=slug)
	else:
		return redirect("group_page")

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def groupreport_pk(request, *args, **kwargs):	
	"""
	Hide a submission in a public mehfil
	"""
	if request.method == 'POST':
		pk = request.POST.get("pk",None)
		slug = request.POST.get("slug",None)
		decision = request.POST.get("dec",None)
		report_decision = request.POST.get("repdec",None)
		if decision == 'rep':
			context = {}
			try:
				context["unique"] = slug
				reply_id = pk
				group = Group.objects.get(unique=slug)
			except:
				context["captain"] = False
				context["unique"] = None
				context["reply"] = None
			if GroupCaptain.objects.filter(which_user=request.user, which_group=group).exists() and Reply.objects.filter(pk=pk, which_group=group).exists():
				context["captain"] = True
				context["reply_pk"] = pk
			else:
				context["captain"] = False
			return render(request,"mehfil/group_report.html",context)
		elif report_decision == '1':
			try:
				group = Group.objects.get(unique=slug)
			except:
				return redirect("home")
			if group.private != '0' or request.user_banned:
				return redirect("missing_page")
			elif GroupBanList.objects.filter(which_user_id=request.user.id, which_group=group).exists():
				return redirect("group_page")
			elif request.user.userprofile.score < -25:
				HellBanList.objects.create(condemned=request.user)
				request.user.userprofile.score = random.randint(10,71)
				request.user.userprofile.save()
				return redirect("group_page")
			else:
				reply = get_object_or_404(Reply, pk=pk)
				if not GroupCaptain.objects.filter(which_user=request.user, which_group=group).exists() or reply.text == request.user.username \
				or reply.which_group_id != group.id:
					# not allowed
					pass
				elif reply.category == '3':
					# already hidden
					pass
				else: #i.e. the person requesting this is a group captain
					reply.category = '3'
					reply.text = request.user.username
					reply.writer.userprofile.score = reply.writer.userprofile.score - 5
					reply.writer.userprofile.save()
					reply.save()
				return redirect("public_group", slug=group.unique)
		else:
			return redirect("public_group", slug=slug)
	else:
		return redirect("home")


