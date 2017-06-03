# coding=utf-8
import redis
from location import REDLOC3

'''
##########Redis Namespace##########

###########
'''

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC3, db=0)

def set_test_payload(payload_list):
	my_server = redis.Redis(connection_pool=POOL)
	try:
		return my_server.lpush("my_test",payload_list)
	except:
		return None