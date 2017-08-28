import random
from links.tasks import save_online_user

class WhoseOnlineMiddleware(object):

    def process_request(self, request):
    	if random.random() < 0.12 and request.user.is_authenticated():
    		save_online_user.delay(user_id=request.session['_auth_user_id'], user_ip=request.META.get('X-IORG-FBS-UIP',request.META.get('REMOTE_ADDR')))
    	else:
    		pass