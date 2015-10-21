from django.contrib import admin
from .models import Link, Vote, UserProfile, UserSettings, Publicreply, Seen, Unseennotification
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
#these will appear in the admin panel
class LinkAdmin(admin.ModelAdmin): pass
admin.site.register(Link, LinkAdmin)

class UnseennotificationAdmin(admin.ModelAdmin): pass
admin.site.register(Unseennotification, UnseennotificationAdmin)

class PublicreplyAdmin(admin.ModelAdmin): pass
admin.site.register(Publicreply, PublicreplyAdmin)

class SeenAdmin(admin.ModelAdmin): pass
admin.site.register(Seen, SeenAdmin)

class VoteAdmin(admin.ModelAdmin): pass
admin.site.register(Vote, VoteAdmin)

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