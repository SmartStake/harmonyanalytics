import { Route, Switch } from 'react-router-dom';
import React from 'react';

import Address from './address/Address';
import MyAccount from './address/MyAccount';
import Rewards from './address/Rewards';

import UnauthRoute from "./util/UnauthRoute";
import NotFound from './base/NotFound';

import Richlist from './network/Richlist';
import RichDelegates from './network/RichDelegates';
import NetworkEvents from './network/NetworkEvents';
import Calculator from './network/Calculator';
import NetworkStake from './network/NetworkStake';

import Events from './harmony/Events';
import NodeHealth from './harmony/NodeHealth';
import Validators from './harmony/Validators';
import Validator from './harmony/Validator';

import Delegates from './harmony/Delegates';
import ValStats from './harmony/ValStats';


export default ({ childProps }) => (
	<Switch>
		<UnauthRoute exact={true} path='/' component={Validators} props={childProps} />
		<UnauthRoute path='/health' component={NodeHealth} props={childProps} />

		<UnauthRoute exact={true} path='/validators/:status' component={Validators} props={childProps} />
		<UnauthRoute exact={true} path='/validators' component={Validators} props={childProps} />

		<UnauthRoute path='/valstats/:hPoolId' component={ValStats} props={childProps} />
		<UnauthRoute path='/val/:hPoolId/:showMore' component={Validator} props={childProps} />
		<UnauthRoute path='/val/:hPoolId' component={Validator} props={childProps} />
		<UnauthRoute path='/val' component={Validator} props={childProps} />
		<UnauthRoute path='/events/:hPoolId/:subType' component={Events} props={childProps} />
		<UnauthRoute path='/events/:hPoolId' component={Events} props={childProps} />
		<UnauthRoute path='/events' component={Events} props={childProps} />


		<UnauthRoute path='/delegates/:hPoolId' component={Delegates} props={childProps} />
		<UnauthRoute path='/delegates' component={Delegates} props={childProps} />
		<UnauthRoute path='/richlist/:count' component={Richlist} props={childProps} />
		<UnauthRoute path='/richlist' component={Richlist} props={childProps} />

		<UnauthRoute path='/address/:address' component={Address} props={childProps} />
		<UnauthRoute path='/account/:address' component={MyAccount} props={childProps} />
		<UnauthRoute path='/account' component={MyAccount} props={childProps} />
		<UnauthRoute path='/rewards/:address' component={Rewards} props={childProps} />

		<UnauthRoute path='/networkEvents/:subType' component={NetworkEvents} props={childProps} />
		<UnauthRoute path='/networkEvents' component={NetworkEvents} props={childProps} />
		<UnauthRoute path='/stake' component={NetworkStake} props={childProps} />
		<UnauthRoute path='/calc' component={Calculator} props={childProps} />
		<UnauthRoute path='/richdel' component={RichDelegates} props={childProps} />

		{/* Finally, catch all unmatched routes */}
		<Route component={NotFound} />
	</Switch>
);
