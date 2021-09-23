from datetime import timedelta
from redis import Redis  
from action import ActionI




"""
Evaluate request to decide if to pass or ban using Generic Cell Rate Algorithm
""" 
def __evaluate_request(r: Redis, ip: str, metric_name:str, limit: int, period: int,track_rate,return_rate,action_duration,actions):
    try:
        key=ip #redis key
        period_in_seconds = int(period)
        t = r.time()[0]
        blocked_key=metric_name+"-blocked" #this is stored in hashset and let me know if metric is blocked or not
        separation = round(period_in_seconds / limit)
        full_metric=metric_name+"-"+str(limit)+"-"+str(period)
        r.hsetnx(key,full_metric,0)
        r.hsetnx(key,blocked_key,'False') 
        rate_obj={}
        
        with r.lock('lock:' + key, blocking_timeout=5) as lock:
            if track_rate:
                rate_1m=rate_tracker(r,key,metric_name,"1")
                rate_10m=rate_tracker(r,key,metric_name,"10")
                rate_60m=rate_tracker(r,key,metric_name,"60")
                rate_obj={"token_rate_1m":rate_1m,"token_rate_10m":rate_10m,"token_rate_60m":rate_60m}
            tat = max(int(r.hget(key,full_metric)), t)
            if tat - t <= period_in_seconds - separation:
                new_tat = max(tat, t) + separation
                r.hset(key,full_metric,new_tat)
                r.hset(key,blocked_key,'False')
                return (True,rate_obj) if return_rate else (True,{})
            else:
                
                if r.hget(key,blocked_key).decode("utf-8")=='False':
                    #in production level code, this should be decoupled and triggered by an event(observer pattern).  
                    # Else it will unneccesary block this function and cause unneeded delay
                    for action in actions:
                        ActionI.fireActionEvent(action,token=metric_name,key=key,duration=action_duration,window=period,limit=limit)
                    r.hset(key,blocked_key,'True')
                    new_tat = max(tat, t) + action_duration
                    r.hset(key,full_metric,new_tat)
                                        
                return (False,rate_obj) if return_rate else (False,{})
    except LockError:
        raise 
        return False    
 

"""
evaluate request  using GCRA based on BAN configuration
"""  
def evaluate_request_ban(r: Redis,Ban:dict, ip: str, metric_name:str, track_rate,return_rate): 
    try:
        thresholds=Ban[metric_name]['thresholds']  
        res=None
        for threshold in thresholds:
            limit=threshold['limit']
            window=threshold['window']
            action_duration=threshold['action_duration']
            actions=threshold['action']
            res=__evaluate_request(r, ip, metric_name, limit, window,track_rate,return_rate,action_duration,actions)
            if not res[0]:
                return res
        return  res
    except Exception as e:
        #log error e
        print("ensure ban setting confirms to expected standard")
        return None
    
     
    

""" this registers  the raquest rate to a redis set. rate_in_min parameter determines the rate at which its cummulated
options available based on requirement are 1m, 10m, 60m
"""
def rate_tracker(r:Redis,ip:str,metric_name:str,rate_in_min):
    try:
        key="counter-"+ip+"-"+metric_name+"-"+str(rate_in_min)
        if r.exists(key)==0:
            r.set(key,0)
            r.expire(key,int(rate_in_min)*60) 
        r.incr(key,1)
        return r.get(key)
    except Exception as e:
        #log this error
        return None

"""
return status from redis set given ip and metric_name
"""
def status(r:Redis,ip:str,metric_name:str):
    try:
      def getkey(rate_in_min):
          k= "counter-"+ip+"-"+metric_name+"-"+str(rate_in_min)
          return r.get(k).decode("utf-8")  if r.exists(k) else 0
      rate_1m=getkey(1)
      rate_10m=getkey(10)
      rate_60m=getkey(60)
      return {"token_rate_1m":rate_1m,"token_rate_10m":rate_10m,"token_rate_60m":rate_60m}
    except Exception as e:
        #log this error
      return None  

"""
return all status. This scan through redis set in O(n) and can likely be expensive 
depending on the number of key
"""
def status_all(r:Redis):
    count = 0
    statuses={}
    try:
         with r.lock('lock: status_all', blocking_timeout=35) as lock:
            for key in r.scan_iter(match='counter-*'):
                key=key.decode("utf-8")
                try:
                    count += 1
                    key_list=str(key).split("-")
                    if key_list[1] not in statuses:
                        statuses[key_list[1]]={}
                    if key_list[2] not in statuses[key_list[1]]:
                            statuses[key_list[1]][key_list[2]]={}
                    if key_list[3] not in statuses[key_list[1]][key_list[2]]:
                            statuses[key_list[1]][key_list[2]][key_list[3]]={}        
                    statuses[key_list[1]][key_list[2]][key_list[3]]=r.get(key)
                except:
                    pass 
    except LockError:  
        #log this error
        pass            
    return statuses    
"""
reset
"""   
def reset_counter(r:Redis,Ban:dict,ip:str,metric_name:str):
    try:
        key=ip #redis key
        thresholds=Ban[metric_name]['thresholds']
        t = r.time()[0]
        for threshold in thresholds:
            limit=threshold['limit']
            window=threshold['window']
            full_metric=metric_name+"-"+str(limit)+"-"+str(window)
            r.hset(key,full_metric,t)
    except Exception as e:
        #log this error e
        pass
           
        
def ban_now(r:Redis,Ban:dict,ip:str,metric_name:str,threshold=0):
    try:
        key=ip #redis key
        thresholds=Ban[metric_name]['thresholds']
        t = r.time()[0]
        
        if len(thresholds)>=threshold or threshold<0:
            raise Exception("invalid threshold  value passed")
        for th in thresholds:
            if th==threshold:
                limit=th['limit']
                window=th['window']
                action_duration=th['action_duration']
                full_metric=metric_name+"-"+str(limit)+"-"+str(window)
                r.hset(key,full_metric,t+int(action_duration))  
    except Exception as e:
        #log this error e
        pass        
