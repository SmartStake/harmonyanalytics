# harmonyanalytics
Harmony Analytics dashboard by Smart Stake

Harmonly Analytics consists of three projects:
- harmonyanalyticslambda - Harmony Analytics AWS Lambda backend. It contains python based AWS Lambda functions and uses serverless framework for deployment. Configuration is required in the lambda project for MySQL database and other basic configuration aspects. Configuration file is haconfig.prod.json.
- harmonyanalyticsui - Harmony Analytics web application. It is based on react framework. Configuration is required in the user interface project to connect the frontend to AWS Lambda (AWS API Gateway) backend. Configuration file is harmonyanalyticsui -> src -> config.js.
- harmonyutils - Harmony Utils contains python utilities that are used for syncing up data from Harmony nodes/backend with Harmony Analytics backend. Configuration is required in the to connect the utilities to AWS Lambda (AWS API Gateway) backend. Configuration file is harmonyutils -> config.json.

Setup instructions are given within each project.
