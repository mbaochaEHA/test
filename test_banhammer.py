from banhammer import BanHammer
from my_triggers import Bans
import unittest
import redis
from datetime import timedelta
import base



r = redis.Redis(host='localhost', port=6379, db=0)
ip="127.0.0.17"
metric_name="login_failed"

class TestBanhammer(unittest.TestCase):

        
    def test_incr(self):
        #test that incr returns false after limit is exceeded
        b=BanHammer(Bans,r) 
        for i in range(11):
            self.assertTrue(True,b.incr(ip,metric_name)[0])
            if i==11:
                self.assertTrue(False,b.incr(ip,metric_name)[0])
        
        #test that incr returns rates when return rate is set to true
        k="counter-"+ip+"-"+metric_name+"-"
        rate_1ms= 1 if not r.get(k+"1") else int(r.get(k+"1").decode("utf-8")) +1
        rate_10ms= 1 if not r.get(k+"10") else int(r.get(k+"10").decode("utf-8"))+1
        rate_60ms= 1 if not r.get(k+"60") else int(r.get(k+"60").decode("utf-8"))+1
        b=BanHammer(Bans,r) 
        res_obj=b.incr(ip,metric_name,track_rates=True,return_rates=True)
        self.assertEqual(int(res_obj[1]["token_rate_1m"].decode("utf-8")),rate_1ms)
        self.assertEqual(int(res_obj[1]["token_rate_10m"].decode("utf-8")),rate_10ms)
        self.assertEqual(int(res_obj[1]["token_rate_60m"].decode("utf-8")),rate_60ms)
        
        #test that incr returns rates =None when track_rate =false is passed to function
        res_obj=b.incr(ip,metric_name,track_rates=False,return_rates=False)
        self.assertEqual(res_obj[1],{})
        
        
        #test that incr returns rates =None when track_rate =false is passed to class declaration
        b=BanHammer(Bans,r,track_rates=False,return_rates=False) 
        res_obj=b.incr(ip,metric_name)
        #self.assertIsInstance(res_obj,bool)
        
         #test that incr returns rates  when track_rate =true is passed to class declaration
        b=BanHammer(Bans,r,track_rates=True,return_rates=True) 
        res_obj=b.incr(ip,metric_name)
        self.assertIsInstance(res_obj,tuple)
      
    def test_ban_now(self):
        #test that request cant be process after ban now is called
         b=BanHammer(Bans,r) 
         b.now(ip,metric_name)
         res=b.incr(ip,metric_name)
         self.assertFalse(res[0])
    
    def test_reset_counter(self):
        #test that request can be process when reset is called even after threshold is exhausted
         b=BanHammer(Bans,r) 
         # this loop exhausts the call and lead to a ban
         for i in range(11):
            self.assertTrue(True,b.incr(ip,metric_name)[0])
            if i==11:
                self.assertTrue(False,b.incr(ip,metric_name)[0]) 
         #reset the ban
         b.reset(ip,metric_name)
         #make a new call
         res=b.incr(ip,metric_name)
         self.assertTrue(res[0]) 
        
    def test_status(self):
        #test that status return the required object
         b=BanHammer(Bans,r) 
       
         status=b.status(ip,metric_name)
         self.assertIn('token_rate_1m',status)
         self.assertIn('token_rate_10m',status)
         self.assertIn('token_rate_60m',status)
         
    def test_status_all(self):
        #test that status return the required object
         b=BanHammer(Bans,r) 
         status_a=b.status_all()
            
    def moreTest(self):
        requests = 2000
        for i in range(requests):
            if base.evaluate_request_ban(r,Bans, '127.0.0.27',"login_failed",True,True)[0]:
                print ('✅ Request is allowed')
            else:
                
                print ('🛑 Request is limited')  

test=TestBanhammer()
test.test_incr()
# test.test_ban_now()       
# test.test_reset_counter() 
# test.test_status()    
# test.test_status_all() 
#test.moreTest()
        