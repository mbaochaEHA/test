import base
from my_triggers import Bans
import unittest
import redis
from datetime import timedelta




r = redis.Redis(host='localhost', port=6379, db=0)
ip="127.0.0.17"
metric_name="login_failed"

class TestBase(unittest.TestCase):
    def evaluate_request(self):
        #test that incr returns false after limit is exceeded
        for i in range(11):
            self.assertTrue(True,base.evaluate_request_ban(r,Bans,ip,metric_name,True,True) [0])
            if i==11:
                self.assertTrue(False,base.evaluate_request_ban(r,Bans,ip,metric_name,True,True) [0])
        
        #test that incr returns rates when return rate is set to true
        k="counter-"+ip+"-"+metric_name+"-"
        rate_1ms= 1 if not r.get(k+"1") else int(r.get(k+"1").decode("utf-8")) +1
        rate_10ms= 1 if not r.get(k+"10") else int(r.get(k+"10").decode("utf-8"))+1
        rate_60ms= 1 if not r.get(k+"60") else int(r.get(k+"60").decode("utf-8"))+1
        res_obj=base.evaluate_request_ban(r,Bans,ip,metric_name,True,True)
        self.assertEqual(int(res_obj[1]["token_rate_1m"].decode("utf-8")),rate_1ms)
        self.assertEqual(int(res_obj[1]["token_rate_10m"].decode("utf-8")),rate_10ms)
        self.assertEqual(int(res_obj[1]["token_rate_60m"].decode("utf-8")),rate_60ms)
        
        #test that incr returns rates =None when track_rate =false is passed to function
        res_obj=base.evaluate_request_ban(r,Bans,ip,metric_name,False,False)
        self.assertEqual(res_obj[1],{})        
      
   
test=TestBase()
test.evaluate_request()
# test.test_incr()
# test.test_ban_now()       
# test.test_reset_counter() 
# test.test_status()    
# test.test_status_all() 
#test.moreTest()
        