from action import Action


#Bans=# configure ban types
Bans = {
    # arbitrary `metric` name to be used in banhammer arguments
    "login_failed": {
        # hierarchical threshold triggers
        "thresholds": [
            {
                # how many calls of this metric?
                "limit": 10,
                # how long should the window be?
                "window": 30,
                # what action to take (if any) and how long that "block" should persist
                # for example: if another event occurs during this window (different from the above window)
                # instantly run action
                "action": [ Action.block_local ],
                "action_duration": 30,
            },
            {
                "limit": 100,
                "window": 3600,
                "action": [ Action.report_central ],
                "action_duration": 86400
            }
        ],
    },
    # local metric only
    "login_successful": {
        "thresholds": [
            {
                "limit": 10,
                "window": 60,
                "action": [ Action.record_local ],
                "action_duration": 60
            },
        ]
    }
}       
        
#print(Bans("10 in 1 hr","100 in 1 hr"))



    