import random
from links.tasks import save_online_user, set_user_age, set_variation_retention

class WhoseOnlineMiddleware(object):

	def process_request(self, request):
		ran_num = random.random()
		####################################################################################
		if ran_num <= 0.06 and request.user.is_authenticated():
			# called between 0% - 6%
			# set "online" list of users
			save_online_user.delay(user_id=request.user.id, user_ip=request.META.get('X-IORG-FBS-UIP',request.META.get('REMOTE_ADDR')))
		####################################################################################
		elif ran_num >= 0.94 and request.user.is_authenticated():
			# called between 94% - 100%
			# set user world age
			set_user_age.delay(user_id=request.user.id)
		####################################################################################
		elif 0.25 <= ran_num < 0.75 and request.user.is_authenticated():
			# 50% chance this is going to be called
			# log d1 retention of the user
			set_variation_retention.delay(request.user.id)