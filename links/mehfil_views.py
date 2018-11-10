import uuid
from operator import itemgetter
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control
from django.views.generic.edit import FormView, CreateView
from django.views.generic import ListView
from django.contrib.auth.models import User
from verified import FEMALES
from score import PRIVATE_GROUP_COST, PUBLIC_GROUP_COST
from tasks import rank_public_groups, public_group_attendance_tasks, queue_for_deletion
from redis1 import check_group_member, remove_group_member, remove_user_group, check_group_invite, remove_group_invite, add_group_member,\
add_user_group, add_group_invite, add_home_link, add_unfiltered_post, add_filtered_post, set_latest_group_reply, bulk_check_group_membership, bulk_check_group_invite
from redis2 import remove_group_notification, remove_group_object, get_attendance, create_notification, create_object
from redis4 import get_most_recent_online_users
from redis3 import get_ranked_public_groups
from mehfil_forms import GroupHelpForm, ReinviteForm, OpenGroupHelpForm, ClosedGroupHelpForm, MehfilForm, AppointCaptainForm, OwnerGroupOnlineKonForm,\
GroupOnlineKonForm, DirectMessageCreateForm, ClosedGroupCreateForm, OpenGroupCreateForm, DirectMessageForm, ReinvitePrivateForm, GroupListForm
from views import condemned, convert_to_epoch, valid_uuid
from models import Group, Reply, GroupCaptain, GroupTraffic, Link


########################## Mehfil Help #########################

class GroupHelpView(FormView):
	"""
	Renders the help page for mehfils
	"""
	form_class = GroupHelpForm
	template_name = "mehfil/group_help.html"

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

########################## Mehfil creation #########################

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

class GroupRankingView(ListView):
	"""
	Displays top public mehfils, sorted by 'stickiness'
	"""
	model = Group
	form_class = GroupListForm
	template_name = "group_ranking.html"
	paginate_by = 25

	def get_queryset(self):
		trending_groups = []
		group_ids_list = get_ranked_public_groups()
		group_ids_dict = dict(group_ids_list)
		group_ids = map(itemgetter(0), group_ids_list)
		groups = Group.objects.select_related('owner').filter(id__in=group_ids)
		for group in groups:
			group_id = str(group.id)
			trending_groups.append((group,group_ids_dict[group_id]))
		trending_groups.sort(key=itemgetter(1), reverse=True)
		trending_groups = map(itemgetter(0), trending_groups)
		return trending_groups



