import random
from links.redis4 import set_online_users

class WhoseOnlineMiddleware(object):

    def process_request(self, request):
    	if random.random() < 0.15 and request.user.is_authenticated():
    		set_online_users(request.session['_auth_user_id'],request.META.get('X-IORG-FBS-UIP',request.META.get('REMOTE_ADDR')))
    	else:
    		pass