import React from 'react';

import ApiUtils from '../util/ApiUtils';
import HValNav from './HValNav';
import EventsInline from './EventsInline';
import HValHeader from './HValHeader';
import HUtils from './HUtils';

import Utilities from "../util/Utilities";

class Events extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      val: {},
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

    var hPoolId = HUtils.getHPoolId(this);
    var url = "listData?type=events&size=500";

    if (hPoolId) {
      url += "&hPoolId=" + hPoolId;
    }

    if (this.props.match && this.props.match.params.subType) {
      url += "&subType=" + this.props.match.params.subType;
    }
    console.log(url);
    const allData = await ApiUtils.get(url);
    console.log("allData is:", allData);

    if (allData) {
      let val = allData["val"];
      let data = Utilities.addIndex(allData["data"]);

      this.setState({val: val,
        data: data, isLoading: false});
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
        <HValHeader val={this.state.val} notification={this.state.notification} desktopView={true} title="Events"/>
        {HUtils.renderEventTypes(this)}
        <EventsInline data={this.state.data} hPoolId={this.state.val.hPoolId} isWidget={false} />
        <HValNav hPoolId={this.state.val.hPoolId}/>
      </div>
    );
  }

}

export default Events;
