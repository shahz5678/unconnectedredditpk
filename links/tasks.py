import os
from unconnectedreddit import celery_app1
import time
from links.models import Link

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")

@celery_app1.task(name='tasks.rank_all')
def rank_all():
    for link in Link.with_votes.all():
        link.set_rank()
    
    