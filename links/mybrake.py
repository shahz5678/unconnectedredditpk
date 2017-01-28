from brake.backends import cachebe

class MyBrake(cachebe.CacheBackend):
	def get_ip(self,request):
		ip = request.META.get('X-IORG-FBS-UIP',
			request.META.get('REMOTE_ADDR')
		)
		return ip