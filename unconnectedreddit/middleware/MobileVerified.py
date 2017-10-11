from links.redis3 import is_mobile_verified

class HellBannedMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
        	if is_mobile_verified(request.user.id):
        		return True
        	else:
        		return False	
    	else:
    		return False