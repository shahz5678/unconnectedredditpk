from django.contrib import admin
from .models import Link, Vote, ChatPic, ChatPicMessage, UserProfile, UserSettings, Publicreply, GroupBanList, HellBanList, Seen, Unseennotification, Group, Reply, GroupInvite, GroupSeen
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
#these will appear in the admin panel
class LinkAdmin(admin.ModelAdmin): pass
admin.site.register(Link, LinkAdmin)

class GroupCreateAdmin(admin.ModelAdmin): pass
admin.site.register(Group, GroupCreateAdmin)

class GroupBanListAdmin(admin.ModelAdmin): pass
admin.site.register(GroupBanList, GroupBanListAdmin)

class HellBanListAdmin(admin.ModelAdmin): pass
admin.site.register(HellBanList, HellBanListAdmin)

class GroupInviteAdmin(admin.ModelAdmin): pass
admin.site.register(GroupInvite, GroupInviteAdmin)

class GroupSeenAdmin(admin.ModelAdmin): pass
admin.site.register(GroupSeen, GroupSeenAdmin)

class UnseennotificationAdmin(admin.ModelAdmin): pass
admin.site.register(Unseennotification, UnseennotificationAdmin)

class ReplyAdmin(admin.ModelAdmin): pass
admin.site.register(Reply, ReplyAdmin)

class PublicreplyAdmin(admin.ModelAdmin): pass
admin.site.register(Publicreply, PublicreplyAdmin)

class SeenAdmin(admin.ModelAdmin): pass
admin.site.register(Seen, SeenAdmin)

class VoteAdmin(admin.ModelAdmin): pass
admin.site.register(Vote, VoteAdmin)

class ChatPicAdmin(admin.ModelAdmin): pass
admin.site.register(ChatPic, ChatPicAdmin)

class ChatPicMessageAdmin(admin.ModelAdmin): pass
admin.site.register(ChatPicMessage, ChatPicMessageAdmin)

class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False

class UserSettingsInline(admin.StackedInline):
	model = UserSettings
	can_delete = False

class UserProfileSettingsAdmin(UserAdmin):
	inlines=[
	UserProfileInline,
	UserSettingsInline, 
	]

admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserProfileSettingsAdmin)