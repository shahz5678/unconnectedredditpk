import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
from links.models import HellBanList

class HellBannedMiddleware(object):

    def process_request(self, request):
        print request.META
        if request.user.is_authenticated():
        	request.user_banned = HellBanList.objects.filter(condemned=request.user).exists()
    	else:
    		request.user_banned = 0