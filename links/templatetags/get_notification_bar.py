from django import template
from links.views import GetLatest
from links.models import UserProfile
from links.forms import UnseenActivityForm
from django.contrib.auth.models import User

register = template.Library()

@register.inclusion_tag(file_name='notification_bar.html')
def notification_bar(notification, origin, notif_form, user, user_id, females, static_url, random, newest_user, salat_timings, lang=None, sort_by=None, is_home=None):
	context = {'notification':notification}
	if notification:
		context ={'ident':user_id,'lang':lang,'sort_by':sort_by,'checked':females,'static_url':static_url, 'random':random, 'newest_user':newest_user,\
		'is_home':is_home, 'origin':origin,'form':notif_form}
		object_type, freshest_reply, is_link, is_photo, is_groupreply, is_salat = GetLatest(user)
		if not is_link and not is_photo and not is_groupreply and not is_salat:
			context["latest_reply"] = []
			context["notification"] = 0
			context["parent"] = []
			context["parent_pk"] = 0
			context["first_time_user"] = False
		elif not freshest_reply:
			context["latest_reply"] = []
			context["notification"] = 0
			context["parent"] = []
			context["parent_pk"] = 0
			context["first_time_user"] = False
		elif is_groupreply:
			if object_type == '1':
				# private mehfil
				context["type_of_object"] = '3a'
				context["notification"] = 1
				context["banned"] = False
				context["parent"] = freshest_reply
				context["parent_pk"] = freshest_reply['oi'] #group id
			elif object_type == '0':
				# public mehfil
				context["type_of_object"] = '3b'
				context["notification"] = 1
				context["banned"] = False
				context["first_time_user"] = False
				context["parent"] = freshest_reply
				context["parent_pk"] = freshest_reply['oi'] #group id
			else:
				context["latest_reply"] = []
				context["notification"] = 0
				context["parent"] = []
				context["parent_pk"] = 0
				context["first_time_user"] = False
				context["banned"] = False
		elif is_salat:
			salat_invite = freshest_reply
			context["type_of_object"] = '4'
			context["notification"] = 1
			try:
				context["first_time_user"] = UserProfile.objects.get(id=freshest_reply['ooi']).streak
			except:
				context["first_time_user"] = 0
			context["banned"] = False
			context["parent"] = salat_invite
			context["namaz"] = salat_timings['namaz'] 
		elif is_link:
			context["type_of_object"] = '2'
			if freshest_reply:
				parent_link_writer_username = freshest_reply['oon']#parent_link_writer.username
				WELCOME_MESSAGE1 = parent_link_writer_username+" welcum damadam pe! Kiya hal hai? Barfi khao aur mazay urao (barfi)"
				WELCOME_MESSAGE2 = parent_link_writer_username+" welcome! Kesey ho? Yeh zalim barfi try kar yar (barfi)"
				WELCOME_MESSAGE3 = parent_link_writer_username+" assalam-u-alaikum! Is barfi se mu meetha karo (barfi)"
				WELCOME_MESSAGE4 = parent_link_writer_username+" Damadam pe welcome! One plate laddu se life set (laddu)"
				WELCOME_MESSAGE5 = parent_link_writer_username+" kya haal he? Ye laddu aap ke liye (laddu)"
				WELCOME_MESSAGE6 = parent_link_writer_username+" welcum! Life set hei? Laddu khao, jaan banao (laddu)"
				WELCOME_MESSAGE7 = parent_link_writer_username+" welcomeee! Yar kya hal he? Jalebi khao aur ayashi karo (jalebi)"
				WELCOME_MESSAGE8 = parent_link_writer_username+" kaisey ho? Jalebi meri pasandida hai! Tumhari bhi? (jalebi)"
				WELCOME_MESSAGE9 = parent_link_writer_username+" salam! Is jalebi se mu meetha karo (jalebi)"
				WELCOME_MESSAGES = [WELCOME_MESSAGE1, WELCOME_MESSAGE2, WELCOME_MESSAGE3, WELCOME_MESSAGE4, WELCOME_MESSAGE5,\
				WELCOME_MESSAGE6, WELCOME_MESSAGE7, WELCOME_MESSAGE8, WELCOME_MESSAGE9]
			else:
				parent_link_writer = User()
				WELCOME_MESSAGES = []
			try:
				context["latest_reply"] = freshest_reply
				context["notification"] = 1
				context["parent"] = freshest_reply
				context["parent_pk"] = freshest_reply['oi']
				# print user.username == parent_link_writer_username
				# print user.username
				# print isinstance(user.username,unicode)
				# print unicode(parent_link_writer_username,"utf-8")
				# print isinstance(unicode(parent_link_writer_username,"utf-8"),unicode)
				if user.username==unicode(parent_link_writer_username,"utf-8") and any(freshest_reply['lrtx'] in s for s in WELCOME_MESSAGES):
					context["first_time_user"] = True
				else:
					context["first_time_user"] = False
			except:
				context["latest_reply"] = []
				context["notification"] = 0
				context["parent"] = []
				context["parent_pk"] = 0
				context["first_time_user"] = False
		elif is_photo:
			if object_type == '1':
				# photo = Photo.objects.get(id=freshest_reply)
				context["type_of_object"] = '1'
				context["notification"] = 1
				context["parent"] = freshest_reply
				context["parent_pk"] = freshest_reply['oi']
				context["first_time_user"] = False
				context["banned"] = False
			elif object_type == '0':
				context["latest_comment"] = freshest_reply
				context["type_of_object"] = '0'
				context["notification"] = 1
				context["parent"] = freshest_reply
				context["parent_pk"] = freshest_reply['oi']#.which_photo_id
				context["first_time_user"] = False
				context["banned"] = False						
			else:
				context["latest_comment"] = []
				context["notification"] = 0
				context["parent"] = []
				context["parent_pk"] = 0
				context["first_time_user"] = False
				context["banned"] = False
	else:
		pass
	return context