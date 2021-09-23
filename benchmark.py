from banhammer import BanHammer
from my_triggers import Bans
import unittest
import redis
from datetime import timedelta
import base


r = redis.Redis(host='localhost', port=6379, db=0)
ip="127.0.0.17"
metric_name="login_failed"


#further benchmarking script can be written here
def incr(n):
    for i in range(n):
      b=BanHammer(Bans,r) 
      b.incr(ip,metric_name)
            
if __name__ == '__main__':
    import timeit
    print(timeit.timeit("incr(10)", globals=locals()))