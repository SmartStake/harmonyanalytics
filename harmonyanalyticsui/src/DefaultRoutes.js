import { Route, Switch } from 'react-router-dom';
import React from 'react';

import Address from './address/Address';
import AddressEvents from './address/AddressEvents';
import MyAccount from './address/MyAccount';
import Rewards from './address/Rewards';

import UnauthRoute from "./util/UnauthRoute";
import NotFound from './base/NotFound';

import Election from './network/Election';
import Richlist from './network/Richlist';
import RichDelegates from './network/RichDelegates';
import NetworkEvents from './network/NetworkEvents';
import NetworkStats from './network/NetworkStats';
import NetworkHistory from './network/NetworkHistory';
import Calculator from './network/Calculator';
import VersionStats from './network/VersionStats';

import Key from './harmony/Key';
import Keys from './harmony/Keys';
import Events from './harmony/Events';
import NodeHealth from './harmony/NodeHealth';
import Validators from './harmony/Validators';
import Validator from './harmony/Validator';

import Delegates from './harmony/Delegates';
import ValStats from './harmony/ValStats';

export default ({ childProps }) => (
	<Switch>
		<UnauthRoute exact={true} path='/' component={Validators} props={childProps} />
		<UnauthRoute path='/election' component={Election} props={childProps} />
		<UnauthRoute path='/health' component={NodeHealth} props={childProps} />

		<UnauthRoute exact={true} path='/validators/:status' component={Validators} props={childProps} />
		<UnauthRoute exact={true} path='/validators' component={Validators} props={childProps} />

		<UnauthRoute path='/valstats/:hPoolId/:showMore' component={ValStats} props={childProps} />
		<UnauthRoute path='/valstats/:hPoolId' component={ValStats} props={childProps} />
		<UnauthRoute path='/val/:hPoolId/:showMore' component={Validator} props={childProps} />
		<UnauthRoute path='/val/:hPoolId' component={Validator} props={childProps} />
		<UnauthRoute path='/val' component={Validator} props={childProps} />
		<UnauthRoute path='/events/:hPoolId/:subType' component={Events} props={childProps} />
		<UnauthRoute path='/events/:hPoolId' component={Events} props={childProps} />
		<UnauthRoute path='/events' component={Events} props={childProps} />
		<UnauthRoute path='/addressEvents/:address' component={AddressEvents} props={childProps} />


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
		<UnauthRoute path='/stats' component={NetworkStats} props={childProps} />
		<UnauthRoute path='/history' component={NetworkHistory} props={childProps} />
		<UnauthRoute path='/version' component={VersionStats} props={childProps} />
		<UnauthRoute path='/calc' component={Calculator} props={childProps} />
		<UnauthRoute path='/richdel' component={RichDelegates} props={childProps} />

		<UnauthRoute path='/keys/:hPoolId/:epoch' component={Keys} props={childProps} />
		<UnauthRoute path='/keys/:hPoolId' component={Keys} props={childProps} />

		<UnauthRoute path='/key/:blsKey/:epoch' component={Key} props={childProps} />

		{/* Finally, catch all unmatched routes */}
		<Route component={NotFound} />
	</Switch>
);
