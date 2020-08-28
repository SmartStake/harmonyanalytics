import React from 'react';
import ReactDOM from 'react-dom';

import './index.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';
import Amplify from 'aws-amplify';
import config from './config';

Amplify.configure({
	API: {
		endpoints: [
			{
				name: 'stakingService',
				endpoint: config.apiGateway.URL,
				region: config.apiGateway.REGION
			}
		]
	}
});

ReactDOM.render(<App />, document.getElementById('root'));
registerServiceWorker();
