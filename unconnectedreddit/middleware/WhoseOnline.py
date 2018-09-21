import random
from links.tasks import save_online_user, set_user_age

class WhoseOnlineMiddleware(object):

    def process_request(self, request):
    	ran_num = random.random()
    	if ran_num < 0.12 and request.user.is_authenticated():
    		save_online_user.delay(user_id=request.session['_auth_user_id'], user_ip=request.META.get('X-IORG-FBS-UIP',request.META.get('REMOTE_ADDR')))
    	if ran_num < 0.1:
			set_user_age.delay(user_id=request.session['_auth_user_id'])    	
