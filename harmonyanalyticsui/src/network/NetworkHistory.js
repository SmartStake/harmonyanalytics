import React from 'react';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import BootstrapTable from 'react-bootstrap-table-next';
import Breadcrumb from 'react-bootstrap/Breadcrumb';
import {Container, Row, Col} from 'react-bootstrap';
import BaseBarChart from '../reports/BaseBarChart';
import StackedBarChart from "../reports/StackedBarChart";

import BaseAreaChart from "../reports/BaseAreaChart";
import BasePieChart from "../reports/BasePieChart";

import HNetworkNav from './HNetworkNav';
import NetworkHeader from './NetworkHeader';

import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import Utilities from '../util/Utilities';
import UINotes from "../util/UINotes";
import ChartUtils from "../util/ChartUtils";
import HUtils from "../harmony/HUtils";
import UIUtils from "../util/UIUtils";
import tooltips from "../tooltips";

class NetworkHistory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: {},
      coinStat: {},
      blockRate: [],
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

    let url = "listData?type=networkHistory";

    const allData = await ApiUtils.get(url);
    // console.log("allData is:", allData);

    if (allData) {
      let data = allData["data"];
      let uniqueDelegatesData = Utilities.removeEmptyRecords(data, "uniqueDelegates");
      let otherValidData = Utilities.removeEmptyRecords(data, "circulatingSupply");
      let networkSignRate = Utilities.removeEmptyRecords(data, "signRate");
      let nodeVersionSummary = Utilities.calcPercent(allData["nodeVersionSummary"], "total")
      // console.log("nodeVersionSummary is:", nodeVersionSummary);

      this.setState({"data": data, "coinStat": allData["coinStat"],
        "uniqueDelegatesData": uniqueDelegatesData, "blockRate": allData["blockRate"],
        "otherValidData": otherValidData, "networkSignRate": networkSignRate,
        "txSummary": allData["txSummary"], "shardTxSummary": allData["shardTxSummary"],
        "nodeVersionSummary": nodeVersionSummary, isLoading: false});
    }
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    // <p/>
    // <h4 style={{align: "center"}}><span><strong>Harmony - Network Stats</strong></span>
    //   <span className="buttonWithText"><img src="/images/reload.svg" onClick={this.reload} title="Reload Screen"
    //     className="imgicon" width="32" height="32" /></span>
    // </h4>
    let lastEpochBlockRate = Utilities.getSecondLastRecordAttribute(this.state.blockRate, "shard0BlockRate");
    let lastEpochBlockRateLabel = "Last Epoch Block Production Rate: " + lastEpochBlockRate;

    return (
      <div>
        <NetworkHeader title="Network History" />
        <hr/>
        <Container fluid>
          <Row>
            <Col md className="chartBg"><BaseAreaChart title="Transaction Growth" xAxis="Date" yAxis="Transactions"
              desc={tooltips.networkCharts.transactionGrowth} showVerticalLabel={false} valueAttr="cumulativeTxs" defaultRange="false"
              data={this.state.txSummary} latestLabelPrefix="Total Transactions" showLatestLabel={true} /></Col>
            <Col md className="chartBg">
              {ChartUtils.render2Lines(this, "Staking vs Non-Staking Transaction Growth", this.state.txSummary,
                "Date", "Transactions", "cumulativeNonStakingTxs", "cumulativeStakingTxs", "cumulativeNonStakingTxs",
                null, tooltips.networkCharts.txComparison)}
            </Col>
          </Row>
          <hr/>
          <Row>
            <Col md className="chartBg"><BaseAreaChart title="Daily Transactions" xAxis="Date" yAxis="Daily Transactions"
              desc={tooltips.networkCharts.dailyTransactions} showVerticalLabel={false} valueAttr="transactions" defaultRange={true}
              data={this.state.txSummary} latestLabelPrefix="Latest Transactions" showPrevLabel={true} /></Col>
            <Col md className="chartBg">
              <BaseBarChart xAxis="Shard" yAxis="Transactions" title="Shard Transaction Distribution"
                desc={tooltips.networkCharts.shardDistribution} showVerticalLabel={true} valueAttr="transactions" showTotalLabel={false}
                data={this.state.shardTxSummary} xAxisValueAttr="title" />
            </Col>
          </Row>
          <hr/>
          <Row>
            <Col md className="chartBg"><BaseAreaChart title="Stake History" xAxis="Epoch" yAxis="Total Staked (millions)"
              desc={tooltips.networkCharts.stakeHistory} showVerticalLabel={false} valueAttr="totalStakeInMillions"
              data={this.state.data} /></Col>
            <Col md className="chartBg"><BaseAreaChart title="Active Address History" xAxis="Epoch" yAxis="Total Addresses"
              desc={tooltips.networkCharts.activeAddress} showVerticalLabel={false} valueAttr="totalAddresses"
              data={this.state.uniqueDelegatesData} /></Col>
          </Row>
          <hr/>
          <Row>
            <Col md className="chartBg">
              <BaseAreaChart title="Unique Delegates History" xAxis="Epoch" yAxis="Unique Delegates"
                desc={tooltips.networkCharts.uniqueDelegates} showVerticalLabel={false} valueAttr="uniqueDelegates"
                data={this.state.uniqueDelegatesData} />
            </Col>
            <Col md className="chartBg"><BaseAreaChart title="Circulating Supply History" xAxis="Epoch" yAxis="Circulating Supply (millions)"
              desc={tooltips.networkCharts.circulatingSupply} showVerticalLabel={false} valueAttr="circulatingSupplyInMillions"
              data={this.state.otherValidData} /></Col>
          </Row>
          <hr/>
          <Row>
            <Col md className="chartBg"><BaseAreaChart title="Median Raw Stake History" xAxis="Epoch" yAxis="Median Raw Stake (millions)"
              desc={tooltips.networkCharts.medianRawStake} showVerticalLabel={false} valueAttr="medianRawStakeInMillions"
              data={this.state.otherValidData} /></Col>
            <Col md className="chartBg"><BaseAreaChart title="Validator Count History" xAxis="Epoch" yAxis="Total Validators"
              desc={tooltips.networkCharts.validatorCount} showVerticalLabel={false} valueAttr="totalValidators"
              data={this.state.otherValidData} /></Col>
          </Row>
          <hr/>
          <Row>
            <Col md className="chartBg"><BaseAreaChart title="Network Sign Rate" xAxis="Epoch" yAxis="Sign percentage"
              desc={tooltips.networkCharts.signPercentage} showVerticalLabel={false} valueAttr="signRate" defaultRange="false"
              data={this.state.networkSignRate} /></Col>
            <Col md className="chartBg"><BaseAreaChart title="Expected Returns (%)" xAxis="Epoch" yAxis="Expected Returns (%)"
              desc={tooltips.networkCharts.expectedReturns} showVerticalLabel={false} valueAttr="rewardRate"
              data={this.state.otherValidData} /></Col>
          </Row>
          <hr/>
          <Row>
            <Col md className="chartBg">
              {ChartUtils.render4Lines(this, "Shard Block Production Rate", this.state.blockRate,
                "Epoch", "Seconds per block", ["shard0BlockRate", "shard1BlockRate", "shard2BlockRate", "shard3BlockRate"],
                null, lastEpochBlockRateLabel, tooltips.networkCharts.blockRate)}
            </Col>
            <Col md className="chartBg">
              <BasePieChart title="Node Software Versions" customTooltip={this.nodeVersionTooltip}
                desc={tooltips.networkCharts.nodeVersionSummary} countAttr="percent" labelAttr="nodeVersion"
                data={this.state.nodeVersionSummary} />
            </Col>
          </Row>
        </Container>
        <HNetworkNav />
      </div>
    );
  }

  nodeVersionTooltip(data) {
    return (<div style={{"backgroundColor": "#f2f2f2"}}>
        Version: <font color="red"><b>{data.nodeVersion}</b></font>
        <br/>BLS Keys using this version: <b>{data.total}</b>
        <br/>Percentage of BLS Keys using this version: <b>{data.percent}%</b>
      </div>);
   }
}

export default NetworkHistory;
