#Contains locations of memcached/redis in various OSes.
import os
ON_MAC = os.environ.get('ON_MAC')

if ON_MAC == '1':
	MEMLOC = 'unix:/usr/local/var/run/memcached/memcached.sock'
	REDLOC1 = '/usr/local/var/run/redis/redis.sock'
	REDLOC2 = '/usr/local/var/run/redis/redis2.sock' 
	REDLOC3 = '/usr/local/var/run/redis/redis3.sock'
	REDLOC4 = '/usr/local/var/run/redis/redis4.sock'
	# REDLOC5 = '/usr/local/var/run/redis/redis5.sock'
	# REDLOC6 = '/usr/local/var/run/redis/redis6.sock'
	# REDLOC7 = '/usr/local/var/run/redis/redis7.sock'
	# REDLOC8 = '/usr/local/var/run/redis/redis8.sock'
	# REDLOC9 = '/usr/local/var/run/redis/redis9.sock'
else:
	MEMLOC = 'unix:/var/run/memcached/memcached.sock'
	REDLOC1 = '/var/run/redis/redis.sock'
	REDLOC2 = '/var/run/redis/redis2.sock'
	REDLOC3 = '/var/run/redis/redis3.sock'
	REDLOC4 = '/var/run/redis/redis4.sock'
	# REDLOC5 = '/var/run/redis/redis5.sock'
	# REDLOC6 = '/var/run/redis/redis6.sock'
	# REDLOC7 = '/var/run/redis/redis7.sock'
	# REDLOC8 = '/var/run/redis/redis8.sock'
	# REDLOC9 = '/var/run/redis/redis9.sock'