import redis

r = redis.Redis(
  host= 'us1-helping-kid-37014.upstash.io',
  port= '37014',
  password= 'b9220b8dc4414d83a03ce2bf3727620c', ssl=True)

r.set('foo','bar')
print(r.get('foo'))