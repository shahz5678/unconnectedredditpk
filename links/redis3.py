# coding=utf-8
import redis
from location import REDLOC3

POOL = redis.ConnectionPool(connection_class=redis.UnixDomainSocketConnection, path=REDLOC3, db=0)

#####################Process Nick#######################

def decode_nick(nickname):
	nick_and_code = nickname.split("**")
	lower_case_nick = nick_and_code[0]
	code = nick_and_code[1]
	upper_case_positions = [int(code[i:i+2]) for i in range(0, len(code), 2)]
	decoded_nick = ''.join(let.upper() if pos in upper_case_positions else let 
	                           for pos, let in enumerate(lower_case_nick))
	return decoded_nick

def get_nicknames(raw_nicknames):
	decoded_nicks = []
	encoded_nicks = []
	for nick in raw_nicknames:
		if "**" in nick:
			encoded_nicks.append(nick)
	for nick in encoded_nicks:
		decoded_nicks.append(decode_nick(nick))
	return decoded_nicks

def process_nick(nickname):
	generic_nick = nickname.lower()+"*"
	#############################################
	position = 0
	encoding = "**"
	for l in nickname.encode('utf-8'):
		if l.isupper():
			encoding += "{:0>2}".format(position)
		position += 1
	specific_nick = nickname.lower()+encoding
	#############################################
	return generic_nick, specific_nick

def get_nick_likeness(nickname):
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick, specific_nick = process_nick(nickname)
	rank = my_server.zrank("nicknames",specific_nick)
	if rank is None:
		my_server.zadd("nicknames",generic_nick,0)
		rank = my_server.zrank("nicknames",generic_nick)
	raw_nicknames = my_server.zrange("nicknames",max(rank-5,0),(rank+5))
	nicknames = get_nicknames(raw_nicknames)
	return nicknames

def nick_already_exists(nickname):
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick = nickname.lower()+"*"
	if not my_server.exists("nicknames"):
		return None
	elif my_server.zrank("nicknames",generic_nick) is None:
		# the nickname has not been used before
		return False
	else:
		# the nickname has been used before
		return True

def insert_nick(nickname):
	my_server = redis.Redis(connection_pool=POOL)
	generic_nick, specific_nick = process_nick(nickname)
	my_server.zadd("nicknames",generic_nick,0,specific_nick,0)

def insert_nick_list(nickname_list):
	my_server = redis.Redis(connection_pool=POOL)
	nicknames = []
	for nickname in nickname_list:
		generic_nick, specific_nick = process_nick(nickname)
		nicknames.append(generic_nick)
		nicknames.append(0)
		nicknames.append(specific_nick)
		nicknames.append(0)
	my_server.zadd("nicknames",*nicknames)