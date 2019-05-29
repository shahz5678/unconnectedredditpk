import random
from links.tasks import save_online_user, set_user_age

class WhoseOnlineMiddleware(object):

	def process_request(self, request):
		ran_num = random.random()
		####################################################################################
		if ran_num <= 0.05 and request.user.is_authenticated():
			# called between 0% - 5%
			# set "online" list of users
			save_online_user.delay(user_id=request.user.id, user_ip=request.META.get('X-IORG-FBS-UIP',request.META.get('REMOTE_ADDR')))
		####################################################################################
		elif ran_num >= 0.95 and request.user.is_authenticated():
			# called between 95% - 100%
			# set user world age
			set_user_age.delay(user_id=request.user.id)