from django import template
from links.models import UserProfile

register = template.Library()

@register.assignment_tag(takes_context=True)
def own_score(context):
    return UserProfile.objects.only('score').get(user_id=context['request'].user.id).score