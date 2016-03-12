import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
import re
from mobileesp import mdetect

class MobileDetectionMiddleware(object):
    """
    Useful middleware to detect if the user is
    on a mobile device.
    """
    def process_request(self, request):
        is_mobile = False
        is_tablet = False
        is_phone = False

        user_agent = request.META.get("HTTP_USER_AGENT")
        http_accept = request.META.get("HTTP_ACCEPT")
        if user_agent and http_accept:
            agent = mdetect.UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
            is_tablet = agent.detectTierTablet()
            is_phone = agent.detectTierIphone()
            is_feature_phone = agent.detectSymbianOS() or agent.detectOperaMobile() \
            or agent.detectWapWml() or agent.detectMidpCapable() or agent.detectTierOtherPhones() 
            is_mobile = is_tablet or is_phone or agent.detectMobileLong()

        request.is_tablet = is_tablet
        request.is_phone = is_phone
        request.is_feature_phone = is_feature_phone
        request.is_mobile = is_mobile