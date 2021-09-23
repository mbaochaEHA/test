import datetime
    

class Action:
    """ define actions to be executed """
    @staticmethod
    def block_local(token, duration, *args):
        print("block local fired at",datetime.datetime.now(), " with attributes token {} duration {} args {} ".format(token,duration,args))

    @staticmethod
    def report_central(token, duration, *args):
        print("report central fired at",datetime.datetime.now(), " with attributes token {} duration {} args {} ".format(token,duration,args))

    @staticmethod
    def record_local(token, duration, key, window, limit):
        print("report local fired at",datetime.datetime.now(), " with attributes token {} duration {} key {} window {} limit {} ".format(token,duration,key,window,limit))
    
   

class ActionI:
    """ higher order function to execute neecessary Action """   
    @staticmethod    
    def fireActionEvent(fn,**kwargs):
        fn(kwargs['token'],kwargs['duration'],kwargs['key'],kwargs['window'],kwargs['limit'])
              

    

