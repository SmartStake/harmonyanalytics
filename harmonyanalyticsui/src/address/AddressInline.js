import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import Table from 'react-bootstrap/Table';
import {Button} from '@material-ui/core';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import paginationFactory from 'react-bootstrap-table2-paginator';
import {ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Label } from 'recharts';
import {BarChart, Bar } from 'recharts';

import tooltips from "../tooltips";
import SPCalc from '../util/SPCalc';
import ApiUtils from '../util/ApiUtils';
import UIUtils from '../util/UIUtils';
import Utilities from "../util/Utilities";
import UINotes from "../util/UINotes";
import SPUtilities from "../util/SPUtilities";

import EventsInline from "../harmony/EventsInline";
import CurrentRewards from './CurrentRewards';
import HUtils from '../harmony/HUtils';

import BaseBarChart from '../reports/BaseBarChart';

class AddressInline extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      width: window.innerWidth,
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
  }
  // rewardComparison: allData["rewardComparison"],

  render() {
    let btcPrice = this.props.coinStats.btcPrice;
    let usdPrice = this.props.coinStats.usdPrice;
    let usdValueTotal = SPCalc.multiplyAndFormat(this.props.addressDetails.totalBalance, usdPrice, 2);
    let btcValueTotal = SPCalc.multiplyAndFormat(this.props.addressDetails.totalBalance, btcPrice, 8);

    return (
      <div>
        <Table striped bordered size="sm" >
        <tbody>
          <tr>
            <th>Alias: </th>
            <td> {this.props.addressDetails.alias}</td>
          </tr>
          <tr>
            <th>Address: </th>
            <td> {HUtils.addressFormatterDel(this.props.addressDetails.address)}</td>
          </tr>
          <tr>
            <th>Richlist Rank: </th>
            <td> {this.props.addressDetails.ranking}</td>
          </tr>
          <tr>
            <th>Total Coins: </th>
            <td> {this.props.addressDetails.totalBalance}</td>
          </tr>
          <tr>
            <th>Total Not Staked: </th>
            <td> {this.props.addressDetails.addressBalance}</td>
          </tr>
          <tr>
            <th>Total Staked: </th>
            <td> {this.props.addressDetails.totalStake}</td>
          </tr>
          <tr>
            <th>Total Rewards: </th>
            <td> {this.props.addressDetails.totalRewards}</td>
          </tr>
          <tr>
            <th>Total in USD: </th>
            <td> ${usdValueTotal}</td>
          </tr>
          <tr>
            <th>Total in BTC: </th>
            <td> {String.fromCharCode(8383)}{btcValueTotal}</td>
          </tr>
        </tbody>
        </Table>
        <p/>
        <Button onClick={() => {document.location = "/rewards/" + this.props.addressDetails.address}} variant="contained" color="default" id="rewardsHistory" size="small">Rewards Details</Button>
        &nbsp;&nbsp;&nbsp;<Button onClick={() => {document.location = "/addressEvents/" + this.props.addressDetails.address}} variant="contained" color="default" id="rewardsHistory" size="small">Events</Button>
        &nbsp;&nbsp;&nbsp;{HUtils.addressLink(this.props.addressDetails.address)}
        {this.props.delegations.length > 0 && this.props.addressDetails.totalStake > 0 && this.renderRewardsSection()}
        <p/>
        {this.props.stakeHistory.length > 0 && this.props.addressDetails.totalStake > 0 && this.renderStakeHistory()}
        <p/>
        {this.props.events.length > 0 && this.renderEvents()}
      </div>
    );
  }

  showRewardsWithdrawal() {
    document.location = "/rewards/" + this.props.addressDetails.address;
  }

  renderStakeHistory() {
    return (<div>
        <hr/>
        <p/>
        <p><b>Stake History Summary</b></p>
        <BaseBarChart xAxis="Epoch" yAxis="Stake" desc={tooltips.address.stakeHistory}
          showVerticalLabel={true} valueAttr="totalStake" showTotalLabel={false}
          data={this.props.stakeHistory} xAxisValueAttr="epoch" />

        <p><b>Rewards Summary (Epoch Ending)</b></p>
        <BaseBarChart xAxis="Epoch" yAxis="Rewards" desc={tooltips.address.rewardsSummary}
          showVerticalLabel={true} valueAttr="totalReward" showTotalLabel={false}
          data={this.props.stakeHistory} xAxisValueAttr="epoch" />

        <hr/>
        {this.renderStakeHistoryTable()}
    </div>);
  }


  renderRewardsSection() {
    return (<div>
        <hr/>
        <p/>
        <p style={{align: "center"}}><span><strong>Delegation/Reward Summary</strong></span></p>
        <CurrentRewards rewards={this.props.delegations} coinStat={this.props.coinStats}/>
        <p/>
      </div>);
  }


  renderStakeHistoryTable() {
    var columns = [
      {text: "Epoch", dataField: "epoch", sort: true,  headerStyle: Utilities.width(20)},
      {text: "Stake",dataField: "totalStake", formatter: SPUtilities.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(30)},
      {text: "Reward",dataField: "totalReward", formatter: SPUtilities.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
      {text: "Balance",dataField: "totalBalance", formatter: SPUtilities.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(30)},
    ];

    const defaultSorted = [{
      dataField: 'epoch',
      order: 'desc' // desc or asc
    }];

    return (
      <div>
        <p><b>Stake History (Epoch Ending)</b></p>
        <BootstrapTable keyField='epoch' data={ this.props.stakeHistory } defaultSorted={defaultSorted}
           desc={tooltips.address.stakeHistory} columns={ columns } striped hover condensed noDataIndication="No data"/>
      </div>
    );
  }

  // <p style={{align: "center"}}><span><strong>Daily stake history for address</strong></span></p>
  // {this.renderBar(this.props.stakeHistory, "Date", "Stake", "stake")}
  // <p/>
  // <p style={{align: "center"}}><span><strong>Daily reward balance history for address</strong></span></p>
  // {this.renderLine(this.props.stakeHistory, "Date", "Reward", "reward")}
  // {this.renderRewardComparison()}
  renderEvents() {
    return (
      <div>
        <p/>
        <hr/>
        <p><b>Recent Events</b></p>
        <EventsInline data={this.props.events} showValName={true} context="address"/>
      </div>
    )
  }

}

export default AddressInline;
