import React from 'react';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import BootstrapTable from 'react-bootstrap-table-next';
import Breadcrumb from 'react-bootstrap/Breadcrumb';

import BaseAreaChart from "../reports/BaseAreaChart";
import HNetworkNav from './HNetworkNav';

import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import Utilities from '../util/Utilities';
import UINotes from "../util/UINotes";
import ChartUtils from "../util/ChartUtils";
import HUtils from "../harmony/HUtils";
import UIUtils from "../util/UIUtils";

class NetworkStake extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: {},
      coinStat: {},
      width: window.innerWidth,
      size: 10,
      responsive: true,
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

    let url = "listData?type=networkStake";

    const allData = await ApiUtils.get(url);
    // console.log("allData is:", allData);

    if (allData) {
      let data = allData["data"];
      this.setState({"data": data, "coinStat": allData["coinStat"],
        isLoading: false});
    }
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    return (
      <div>
        <p/>
        <h4 style={{align: "center"}}><span><strong>Harmony - Stake History</strong></span>
          <span className="buttonWithText"><img src="/images/reload.svg" onClick={this.reload} title="Reload Screen"
            className="imgicon" width="32" height="32" /></span>
        </h4>
        <hr/>
        <p>Total Stake (at this time): {HUtils.coinCountCellFormatter(this.state.coinStat.totalStake)} ONE. Chart shows staked amount at beginning of each epoch.</p>
        <BaseAreaChart title="" xAxis="Epoch" yAxis="Total Staked (millions)"
          showVerticalLabel={false} valueAttr="totalStakeInMillions"
          data={this.state.data} />

        <HNetworkNav />
      </div>
    );
  }
}

export default NetworkStake;
