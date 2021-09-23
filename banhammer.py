from my_triggers import Bans
from datetime import timedelta
import base
import redis

class BanHammer:
    def __init__(self,Bans,redisInstance,**rates):
        self.Bans=Bans
        self.rates=rates
        if 'track_rates' not in self.rates:
            self.rates['track_rates']=False
        if 'return_rates' not in self.rates:
            self.rates['return_rates']=False
        self.redisInstance=redisInstance
        
    def incr(self,ip,metric_name,**rates):   
        track_rates=rates['track_rates'] if   'track_rates'  in rates else self.rates['track_rates']
        return_rates=rates['return_rates'] if  'return_rates'  in rates else self.rates['return_rates']
        ban_rules=self.Bans
        request_res=base.evaluate_request_ban(self.redisInstance,self.Bans, ip,metric_name, return_rates,return_rates)
        return request_res
    
    def now(self,ip,metric_name,threshold=0):
        base.ban_now(self.redisInstance,self.Bans,ip,metric_name,threshold)
        
    def reset(self,ip,metric_name):
        base.reset_counter(self.redisInstance,self.Bans,ip,metric_name)
        
    def status(self,ip,metric_name):
        return base.status(self.redisInstance,ip,metric_name)
    
    def status_all(self):
        return base.status_all(self.redisInstance)
        
           
        
        