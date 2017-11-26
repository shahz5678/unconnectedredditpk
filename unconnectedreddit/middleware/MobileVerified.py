from links.redis3 import is_mobile_verified

class MobVerifiedMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
        	request.mobile_verified = True if is_mobile_verified(request.user.id) else False	
    	else:
    		request.mobile_verified = False