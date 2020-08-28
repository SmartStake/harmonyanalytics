# Harmony Analytics Utils
Harmony Analytics Utils project is a python project for syncing network data with Harmony Analytics backend database.

Instructions for setting up the project in a node:
```
- install python 3.8
- clone source code
- configure config.json
- run the sync up jobs as needed
````

Template for config.json:

    {
        "general": {
            "key": "<security-key-for-backend-lambda>",
            "app": "HARMONY",
            "DEFAULT_POOL_ID": <DEFAULT_POOL_DB_ID>,
            "ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC": 12000,
            "ADDRESS_MAX_RANK_FOR_TOP_SYNC": 2000,
            "MAX_LIMIT_EVENT_SYNC": 1000,
            "EVENT_SYNC_MAX_LOOPS": 5,
            "SLEEP_TIME_FOR_MORE": 0.05,
            "BLOCK_TIME": 5
        },
        "paths": {
            "HARMONY_HOME_RELATIVE_DIR": "/harmony/",
            "appEnvDev": "<AWS_API_GATEWAY_ENDPOINT_FOR_DEV>",
            "appEnvProd": "<AWS_API_GATEWAY_ENDPOINT_FOR_PROD>",
            "ADDRESS_URL": "https://harmony-explorer-mainnet.firebaseio.com/one-holder.json",
            "HARMONY_BASE_URL": "https://api0.s0.t.hmny.io"
        }
    }


Sync up jobs:
    
    - python harmonySync dev/prod logsPath val/add
    - python harmonyAddressSync dev/prod logsPath TOP/ALL
    - python harmonyEventsSync dev/prod logsPath
    

Note that the application will work only if the backend application, database, and data sync jobs are setup.
