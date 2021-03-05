import React from 'react';

import ApiUtils from '../util/ApiUtils';
import HNetworkNav from './HNetworkNav';
import EventsInline from '../harmony/EventsInline';

import NetworkHeader from './NetworkHeader';
import Utilities from "../util/Utilities";
import SPUtilities from "../util/SPUtilities";
import UIUtils from "../util/UIUtils";
import HUtils from "../harmony/HUtils";

class NetworkEvents extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      width: window.innerWidth,
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

    var url = "listData?type=events&size=500";

    if (this.props.match && this.props.match.params.subType) {
      url += "&subType=" + this.props.match.params.subType;
    }
    // console.log(url);
    const allData = await ApiUtils.get(url);
    // console.log("allData is:", allData);

    if (allData) {
        this.setState({data: Utilities.addIndex(allData), isLoading: false});
    }

    this.setState({isLoading: false});
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    return (
      <div>
        <NetworkHeader title="Network Events" />
        {HUtils.renderNetworkEventTypes()}
        <EventsInline pageSize="50" data={this.state.data} isWidget={false} showValName={true} context="network"/>
        <HNetworkNav />
      </div>
    );
  }

}

export default NetworkEvents;
