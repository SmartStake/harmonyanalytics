import React from 'react';

import ApiUtils from '../util/ApiUtils';
import Utilities from "../util/Utilities";
import SPUtilities from "../util/SPUtilities";

import AddressHeader from './AddressHeader';
import AddressInline from './AddressInline';

class Address extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      delegations: [],
      smartStake: null,
      events: [],
      rewards: [],
      stakeHistory: [],
      addressDetails: {},
      coinStats: {},

      width: window.innerWidth,
      lastUpdatedGap: null,

      responsive: true,
      size: 10,
    }
    this.updateDimensions = this.updateDimensions.bind(this);
  }

  updateDimensions() {
    this.setState({width: window.innerWidth});
  }

  componentWillMount() {
    this.updateDimensions();
  }

  componentWillUnmount() {
    window.removeEventListener("resize", this.updateDimensions);
  }

  async componentDidMount() {
    window.addEventListener("resize", this.updateDimensions);

    var address = SPUtilities.getAddress(this);
    // console.log("componentDidMount - after address: ", address);

    const allData = await ApiUtils.get("listData?type=addressDetails&address=" + address);
    // console.log("allData is:", allData);

    if (allData) {
      this.setState({delegations: Utilities.addIndex(allData["delegations"]),
        addressDetails: allData["addressDetails"], rewards: allData["rewards"],
        lastUpdatedGap: allData["lastUpdated"], stakeHistory: allData["stakeHistory"],
        coinStats: allData["coinStats"], events: Utilities.addIndex(allData["events"]),
        smartStake: allData["smartStake"], isLoading: false});
    }
  }
  // rewardComparison: allData["rewardComparison"],

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    return (<div>
          <AddressHeader addressDetails={this.state.addressDetails}
              lastUpdatedGap={this.state.lastUpdatedGap} title="Address Details"/>
          <AddressInline addressDetails={this.state.addressDetails} delegations={this.state.delegations}
            lastUpdatedGap={this.state.lastUpdatedGap} events={this.state.events} stakeHistory={this.state.stakeHistory}
            coinStats={this.state.coinStats} rewards={this.state.rewards}/>
        </div>
      );
  }
}

export default Address;
