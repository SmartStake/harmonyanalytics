import React from 'react';

import ApiUtils from '../util/ApiUtils';
import HValNav from '../harmony/HValNav';
import EventsInline from '../harmony/EventsInline';
import HValHeader from '../harmony/HValHeader';
import HUtils from '../harmony/HUtils';

import Utilities from "../util/Utilities";
import SPUtilities from "../util/SPUtilities";
import AddressHeader from './AddressHeader';

class AddressEvents extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      addressDetails: {},
      width: window.innerWidth,
      size: 10,
      isLoading: true,
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
    var url = "listData?type=addressEvents&size=500";

    if (address) {
      url += "&address=" + address;
    }

    if (this.props.match && this.props.match.params.subType) {
      url += "&subType=" + this.props.match.params.subType;
    }
    // console.log(url);
    const allData = await ApiUtils.get(url);
    // console.log("allData is:", allData);

    if (allData) {
      let data = Utilities.addIndex(allData["data"]);
      this.setState({data: data, addressDetails: allData["addressDetails"],
        lastUpdatedGap: allData["lastUpdated"], isLoading: false});
    }

    this.setState({isLoading: false});
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    return (
      <div>
        <p/>
        <AddressHeader addressDetails={this.state.addressDetails}
            lastUpdatedGap={this.state.lastUpdatedGap} title="Address Details"/>
        <EventsInline data={this.state.data} isWidget={false} context="address" pageSize="50" />
      </div>
    );
  }
  // {UIUtils.renderEventTypes(this)}
  // <EventsInline data={this.state.data} callerId="events" />

}

export default AddressEvents;
