from django import template
from unconnectedreddit.env import BUCKET_ADDR

register = template.Library()

@register.filter(name='thumb_to_img')
def thumb_to_img(filename):
    """
    Doing the reverse of what the s3 template tag does
    """
    if not filename or filename == 'empty':
        return ''
    else:
        filename = str(filename)
        return BUCKET_ADDR+"photos/"+filename[-40:]