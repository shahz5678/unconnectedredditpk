#!/usr/bin/env python
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")
from links.models import Link

def rank_all():
    for link in Link.with_votes.all():
        link.set_rank()

if __name__=="__main__":
        rank_all()
        