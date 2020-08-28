# Harmony Analytics UI
Harmony Analytics is a react based web application.

To run the application in a local environment, do the following:
```
install npm
install react
clone this repository
go to the repository folder -> harmonyanalyticsui
modify src -> config.js and setup AWS API Gateway URL and other settings as needed
Run the command "npm install"
Run the command "npm start"
````

Your browser should open a new window for http://localhost:3000

Template for config.js

    export default {
      constants: {
        APP_HARMONY: "HARMONY",
      },
    
      apiGateway: {
        REGION: "<API_GATEWAY_REGION>",
        URL: '<ENTER_API_GATEWAY_URL>',
        GA_ID: "<GOOGLE_ANALYTICS_ID>",
        ENV: "prod",
        APP: "HARMONY",
        KEY: "<ENTER_API_GATEWAY_BACKEND_KEY>",
        DEFAULT_POOL_ID: <DEFAULT_VALIDATOR_ID>,
      },
    };
    


Note that the application will work only if the backend application, database, and data sync jobs are setup.
