# -*- coding: utf-8 -*-
from django import template
from links.redis5 import retrieve_personal_group_invite_count, allot_bucket_to_user

register = template.Library()

@register.assignment_tag(takes_context=True)
def check_invite_count(context):
    ############################
    BENCHMARK_ID = 1646458
    user_id = context['request'].user.id
    # sort people into buckets
    """
    'N1': New user bucket, with invite count.
    'NC': New user bucket, control group.
    'O1': Old user bucket, with invite count.
    'OC': Old user bucket, control group.
    """
    if user_id > BENCHMARK_ID:
        # user is either N1 or NC
        if user_id % 2 == 0:
            # even
            bucket_type='N1'
        else:
            # odd
            bucket_type='NC'
    else:
        # user is either O1 or OC
        if user_id % 2 == 0:
            # even
            bucket_type='O1'
        else:
            # odd
            bucket_type = 'OC'
    allot_bucket_to_user(user_id, bucket_type)
    ############################
    try:
    	payload = {'bucket_type':bucket_type, 'invite_count':int(retrieve_personal_group_invite_count(user_id))}
        return payload
    except (KeyError,TypeError):
        return 0