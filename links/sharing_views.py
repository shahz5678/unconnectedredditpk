from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.http import HttpResponse
from tasks import log_sharing_click

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
@csrf_protect
def log_sharing(request):
	"""
	Logs image sharing attempts
	"""
	if request.method == 'POST':
		if request.user.is_authenticated():
			# only logging logged in sharers currently
			photo_id = request.POST.get("pid",None)
			photo_owner_id = request.POST.get("oid",None)
			sharer_id = request.POST.get("sid",None)
			share_type = request.POST.get("st",None)
			origin_key = request.POST.get("org",None)
			if photo_id and photo_owner_id!=sharer_id:
				log_sharing_click.delay(photo_id, photo_owner_id, sharer_id, share_type, origin_key)
		# 204 response means "The server has successfully fulfilled the request and there is no additional content to send in the response payload body."
		return HttpResponse(status=204)
	else:
		referrer = request.META.get('HTTP_REFERER',None)
		if referrer:
			return redirect(referrer)
		else:
			return redirect("missing_page")