import random
from links.redis2 import set_whose_online

class WhoseOnlineMiddleware(object):

    def process_request(self, request):
    	if request.user.is_authenticated() and random.random() < 0.4:
    		set_whose_online(request.session['_auth_user_id'])
    	else:
    		pass