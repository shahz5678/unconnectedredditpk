class OperaMiniMiddleware(object):

    def process_request(self, request):
    	user_agent = request.META.get('HTTP_USER_AGENT',None)
    	if 'Presto' in user_agent and 'Opera Mini' in user_agent:
    		request.is_opera_mini = True
    	else:
    		request.is_opera_mini = False