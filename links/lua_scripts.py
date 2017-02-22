import redis
from location import REDLOC2
# from redis1 import POOL

# my_server = redis.Redis(connection_pool = POOL)
my_server = redis.StrictRedis(unix_socket_path=REDLOC2)

# -- Get logins from the last 10 minutes
lualatestlogins = """
local l = redis.call('ZRANGEBYSCORE', KEYS[1], ARGV[1]-600, '+inf') -- returns key:value pairs
local c = {}
for _, v in pairs(l) do
  local p = v:find(':')
  local i = v:sub(1,p-1)
  c[#c+1] = i
end
return c"""
getlatestlogins = my_server.register_script(lualatestlogins)

# -- "Evict" old logins
luacleanselogins = """
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', '(' .. ARGV[1]-600)"""
cleanselogins = my_server.register_script(luacleanselogins)

# -- Store the new login
luastorelogin = """
redis.call('ZADD', KEYS[1], ARGV[1], ARGV[2] .. ':' .. ARGV[3])
redis.call('SET',KEYS[2],ARGV[3])
redis.call('EXPIRE',KEYS[2],600)"""
storelogin = my_server.register_script(luastorelogin)

# -- retrieve collisions in IPs
luaretrieveclones = """
local q = redis.call('GET',KEYS[2]) -- gives ip associated to user ID
if q == nil or q == '' then
  return nil               -- the key holding user_ID's ip has expired, hence return nothing
else
  local l = redis.call('ZRANGEBYSCORE', KEYS[1], ARGV[1]-600, '+inf')
  local c = {}
  for _, v in pairs(l) do  -- pairs enables iterating over key:value pairs (score:value from sorted set in this case)
    local p = v:find(':')  -- finding location of ':' in string
    local i = v:sub(1,p-1) -- user id
    local n = v:sub(p+1)   -- user ip
    if n == q then         -- user_ip == user_id
      c[#c+1] = i          -- concatenate user_id to c
    end
  end

  return c
end"""
retrieveclones = my_server.register_script(luaretrieveclones)