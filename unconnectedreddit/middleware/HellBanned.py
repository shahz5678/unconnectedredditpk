from links.models import HellBanList

class HellBannedMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
        	request.user_banned = HellBanList.objects.filter(condemned=request.user).exists()
    	else:
    		request.user_banned = 0