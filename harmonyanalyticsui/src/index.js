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
			{name: 'mainnet', endpoint: config.apiGatewayMainnet.URL, region: config.apiGatewayMainnet.REGION},
			{name: 'testnet', endpoint: config.apiGatewayTestnet.URL, region: config.apiGatewayTestnet.REGION},
			{name: 'devnet', endpoint: config.apiGatewayDevnet.URL, region: config.apiGatewayDevnet.REGION},
		]
	}
});

ReactDOM.render(<App />, document.getElementById('root'));
registerServiceWorker();
