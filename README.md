# test
"""
BANHAMMER DOCUMENTATION
BANHAMMER  is a rate limitter libry based on defined requirements. The requirements for this libry is documented here
https://github.com/IMI-challenges/banhammer-v2-Godswill.Mbaocha


Approach
Because performance is critical and this should potentially process millions of request in seconds, 
I opted to use a memory cache called Redis. 
The code is documented to provide clarity and  help any developer follow through with the thought process

base.py : This is the  business layer that implements the core functionalities.
    evaluate_request : This evaluates request to determine if it should pass or not. It is a private method and used by evaluate_request_ban
        It does the following
        1. registers request in a redis hashset using ip as the key
        2. based on GCRA algorithm, deterimines if the request should pass through or not
        3. determine if rates should be persisted in redis based on 'track_rate' 
        4. determine what data is returned based on 'return type'. Return type is a tuple  (bool,rates). rates is a dictionary and will return an empty dictionary if 
        return_rate is false
        5. Call escalate whenever request is blocked. Escalate is a higher order function which calls 'action'(report_central,block_local or record_local)
           In production, this shoud be executed as an event (observer pattern). This is for decoupling and performance reason
         
    
evaluate_request_ban: This enforces the BAN and its a public method referenced by banhammer.py. It loops through metric threshold and evaluate based o
    configured limit 
    
rate_tracker: This tracks the request by persisting request counts in redis set. Enabling us know total request in 1min,10min,60min (request_in_min). 
The set is reset after request_in_min is exhausted

status : Return dictionary of status in the format {"token_rate_1m":rate_1m,"token_rate_10m":rate_10m,"token_rate_60m":rate_60m}

status_all: Returns array of dictionary of status based on requirements

reset_counter : reset counter request. If a request is banned, this reset the ban. If a request have exhausted say 45 hits in 1 min, this resets it.
The algorithm is to set the Theoritical arrival time to current time

ban_request: ban a request. The algorithm is to set the Theoritical arrival time to current time + 'action duration' as defined in ban




banhammer.py : This implements neccessary function defined by https://github.com/IMI-challenges/banhammer-v2-Godswill.Mbaocha

Scaling
The following are recommendation to scale the performance of this libry

1. partition the data and scale the redis horizontally
2. Have an event trigger execution of action call(report_central,record_local,block_local).
This calls doesnt impact on the return value and should be decoupled
    

""""
