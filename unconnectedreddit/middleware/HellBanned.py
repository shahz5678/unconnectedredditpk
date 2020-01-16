from links.redis4 import is_user_hell_banned
# from links.models import HellBanList

class HellBannedMiddleware(object):

    def process_request(self, request):
       	"""
       	adds hell_ban status for each user
       	"""
        request.user_banned = is_user_hell_banned(target_id=request.user.id) if request.user.is_authenticated() else 0