import random
from links.redis2 import set_online_users#,set_whose_online

class WhoseOnlineMiddleware(object):

    def process_request(self, request):
    	if request.user.is_authenticated() and random.random() < 0.4:
    		set_online_users(request.session['_auth_user_id'],request.META.get('X-IORG-FBS-UIP',request.META.get('REMOTE_ADDR')))
    	else:
    		pass