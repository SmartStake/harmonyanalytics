# Harmony Analytics Lambda
Harmony Analytics Lambda project is a python project for AWS Lambda based API development

Instructions for setting up the project in a local environment:
```
- install python 3.8
- install serverless framework
- clone source code
- configure aws in local environment
- setup mysql database in aws
- create database objects by running harmony-mysql-ddl.sql (root folder)
- configure haconfig.dev.json and haconfig.prod.json (root folder/one level above lambda project)
- deploy lambda functions using "serverless deploy --stage <stage-name>" where stage-name is dev or prod
- note down the endpoints generated. you will need them in harmonyanalyticsui and harmonyanalyticsutils
````

Template for haconfig.dev.json or haconfig.prod.json:

    {
      "DB_SCHEMA_NAME": "<FILL_IT>",
      "DB_ENDPOINT": "<FILL_IT>",
      "H_TELEGRAM_TOKEN": "<FILL_IT>",
      "DB_USERNAME": "<FILL_IT>",
      "DB_PASSWORD": "<FILL_IT>",
      "SECURITY_KEY_1": "<FILL_IT>",
      "SECURITY_KEY_2": "<FILL_IT>",
      "DEFAULT_POOL_ID": <FILL_IT>,
      "REGION": "us-east-1"
    }

Note that the application will work only if the database, and other AWS resources are setup properly.
