import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import Alert from 'react-bootstrap/Alert'
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import paginationFactory from 'react-bootstrap-table2-paginator';
import {Button} from '@material-ui/core';
import Card from 'react-bootstrap/Card';
import CardDeck from 'react-bootstrap/CardDeck';

import {CollapsibleComponent, CollapsibleHead, CollapsibleContent} from 'react-collapsible-component';

import CurrentRewards from './CurrentRewards';
import "./Rewards.css";
import FilterAddress from "./FilterAddress";
import Views from "./Views";
import HUtils from "../harmony/HUtils";

import AddressUtils from '../util/AddressUtils';
import ApiUtils from '../util/ApiUtils';
import UIUtils from '../util/UIUtils';
import UINotes from '../util/UINotes';
import Utilities from "../util/Utilities";
import SPUtilities from "../util/SPUtilities";
import SPCalc from "../util/SPCalc";

class Rewards extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      rewards: [],
      rewardsHistory: [],
      rewardsHistorySummary: [],
      rewardsHistorySummaryAnnual: [],
      filterState: {
        address: [],
        alias: "",
      },
      coinStat: {},
      smartStake: null,
      isLoading: true,
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

    var address = SPUtilities.getAddress(this);
    // console.log("componentDidMount - after address: ", address);

    var url = "listData?type=rewardsHistory&address=" + address;
    // console.log(url);
    const allData = await ApiUtils.get(url);
    // console.log(allData);

    if (allData) {
      this.setState({rewards: allData["data"], rewardsHistory: allData["history"],
        rewardsHistorySummary: allData["historySummary"], address: address,
        rewardsHistorySummaryAnnual: allData["historySummaryAnnual"],
        smartStake: allData["smartStake"], coinStat: allData["coinStat"], isLoading: false});
    }
  }

  renderRewardHeader(totalStake, totalRewards) {
    if (!this.state.coinStat) {
      return;
    }

    let totalStakeInt = parseFloat(totalStake);
    let totalRewardsInt = parseFloat(totalRewards);

    let totalOne = totalStakeInt + totalRewardsInt;
    let totalOneStr = totalOne.toLocaleString();
    let btcPrice = this.state.coinStat.btcPrice;
    let usdPrice = this.state.coinStat.usdPrice;

    let usdValueStaked = "N/A";
    let btcValueStaked = "N/A";
    let usdValueRewards = "N/A";
    let btcValueRewards = "N/A";
    let usdValueTotal = "N/A";
    let btcValueTotal = "N/A";

    if (!isNaN(totalOne) && !isNaN(usdPrice) && !isNaN(btcPrice) ) {
      usdValueTotal = SPCalc.multiplyAndFormat(totalOne, usdPrice, 2);
      btcValueTotal = SPCalc.multiplyAndFormat(totalOne, btcPrice, 8);

      usdValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, usdPrice, 2);
      btcValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, btcPrice, 8);

      usdValueStaked = SPCalc.multiplyAndFormat(totalStakeInt, usdPrice, 2);
      btcValueStaked = SPCalc.multiplyAndFormat(totalStakeInt, btcPrice, 8);
    }

    // Address - <span><a href={"/address/" + this.state.address} className="black-a">{this.state.address}</a></span>

    return (
      <div>
        <p/>
        <p/>
        <Alert variant="info">
          <Alert.Heading>Current Rewards Summary</Alert.Heading>
          Address - {HUtils.addressFormatterDel(this.state.address)}
        </Alert>
        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Total Stake</Card.Header>
            <Card.Body>
              <Card.Title>ONE {SPCalc.formatCoinCount(totalStake)}</Card.Title>
              <Card.Text>USD ${usdValueStaked} (${usdPrice} per ONE)</Card.Text>
              <Card.Text>BTC {String.fromCharCode(8383)}{btcValueStaked} ({String.fromCharCode(8383)}{SPUtilities.formatBtcPrice(btcPrice)} per ONE)</Card.Text>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Total Rewards</Card.Header>
            <Card.Body>
              <Card.Title>ONE {SPCalc.formatCoinCount(totalRewards)}</Card.Title>
              <Card.Text>USD ${usdValueRewards}</Card.Text>
              <Card.Text>BTC {String.fromCharCode(8383)}{btcValueRewards}</Card.Text>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Total One (Staked + Rewards)</Card.Header>
            <Card.Body>
              <Card.Title>ONE {totalOneStr}</Card.Title>
              <Card.Text>USD ${usdValueTotal}</Card.Text>
              <Card.Text>BTC {String.fromCharCode(8383)}{btcValueTotal}</Card.Text>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/>
      </div>);
  }

  renderRewards(totalStake, totalRewards) {
    // console.log("pool data is:", this.state);
    var columns;
    if (window.innerWidth < 1000) {
      columns = [
        {text: "Address",dataField: "address", formatter: SPUtilities.addressShortFormatter, sort: true, headerStyle: Utilities.width(30)},
        {text: "Pool Name", dataField: "poolName", formatter: SPUtilities.poolNameFormatter, sort: true,  headerStyle: Utilities.width(25)},
        {text: "Stake",dataField: "stake", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "Rewards",dataField: "reward", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
      ];
    } else {
      columns = [
        {text: "Address",dataField: "address", formatter: SPUtilities.addressShortFormatter, sort: true, headerStyle: Utilities.width(15)},
        {text: "Pool Name", dataField: "poolName", formatter: SPUtilities.poolNameFormatter, sort: true,  headerStyle: Utilities.width(20)},
        {text: "Pool Total Stake", dataField: "totalStake", formatter: SPUtilities.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Stake in Pool",dataField: "stake", formatter: SPUtilities.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "% Stake (portfolio)",dataField: "stake", formatter: SPCalc.calcWeight, formatExtraData: totalStake, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Rewards in Pool",dataField: "reward", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "% Rewards (portfolio)",dataField: "reward", formatter: SPCalc.calcWeight, formatExtraData: totalRewards, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
      ];
    }

    return (<div>
      <BootstrapTable keyField='poolName' data={ this.state.rewards }
        columns={ columns } striped expandableRow={ () => { return true; } }
        hover condensed noDataIndication="No results"/>
      </div>);
  }

  renderRewardsHistory() {
    let totalRewards = SPCalc.getTotal(this.state.rewardsHistory, "amount", true);

    let totalRewardsInt = parseFloat(totalRewards);
    let btcPrice = this.state.coinStat.btcPrice;
    let usdPrice = this.state.coinStat.usdPrice;
    let usdValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, usdPrice, 2);
    let btcValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, btcPrice, 8);
    const options = UIUtils.getPageOptionsSmall(this, 10);

    var columns = [
        {text: "Withdrawal Time", dataField: "withdrawalTime", formatter: SPUtilities.epochFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(50)},
        {text: "Rewards", dataField: "amount", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(50)},
    ];

    return (<div>
        <p/>
        <Alert variant="info">
          <Alert.Heading>Withdrawal History</Alert.Heading>
          <p/>Total Rewards Withdrawn - <span><strong>{SPCalc.formatCoinCount(totalRewards)}
            </strong></span> &nbsp;(BTC - <span><strong>{btcValueRewards}</strong></span>, USD -
            &nbsp;<span><strong>${usdValueRewards}</strong></span>)
          <br/>Total does not include outstanding rewards (yet to be withdrawn).
        </Alert>
        <p/>
        <BootstrapTable keyField='withdrawalTime' data={ this.state.rewardsHistory }
          columns={columns} striped
          hover condensed noDataIndication="No results" options={options}
          pagination={ paginationFactory(options)} expandableRow={ () => { return true; }} />
        <p/>
        <hr/>
      </div>);
  }

  getRewardsHistoryColumns(timeframe) {
    var columns = [
        {text: timeframe, dataField: "withdrawalTime", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(50)},
        {text: "Rewards", dataField: "amount", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(50)},
    ];

    return columns;
  }

  // <p/>Total Rewards Withdrawn - <span><strong>{SPCalc.formatCoinCount(totalRewards)}
  //   </strong></span> &nbsp;(BTC - <span><strong>{btcValueRewards}</strong></span>, USD -
  //   &nbsp;<span><strong>${usdValueRewards}</strong></span>)
  // <br/>Total does not include outstanding rewards (yet to be withdrawn).

  renderRewardsHistorySummary() {
    let totalRewards = SPCalc.getTotal(this.state.rewardsHistorySummary, "amount", true);

    let totalRewardsInt = parseFloat(totalRewards);
    let btcPrice = this.state.coinStat.btcPrice;
    let usdPrice = this.state.coinStat.usdPrice;
    let usdValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, usdPrice, 2);
    let btcValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, btcPrice, 8);

    return (<div>
      <p/>
      <p><b>Monthly Withdrawal History</b></p>
      <p/>
      <BootstrapTable keyField='withdrawalTime' data={ this.state.rewardsHistorySummary }
        columns={ this.getRewardsHistoryColumns("Month") } striped expandableRow={ () => { return true; } }
        hover condensed noDataIndication="No results"/>
      <p/>
      </div>);
  }


  // <p/>Total Rewards Withdrawn - <span><strong>{SPCalc.formatCoinCount(totalRewards)}
  //   </strong></span> &nbsp;(BTC - <span><strong>{btcValueRewards}</strong></span>, USD -
  //   &nbsp;<span><strong>${usdValueRewards}</strong></span>)
  // <br/>Total does not include outstanding rewards (yet to be withdrawn).

  renderRewardsHistorySummaryAnnual() {
    let totalRewards = SPCalc.getTotal(this.state.rewardsHistorySummaryAnnual, "amount", true);

    let totalRewardsInt = parseFloat(totalRewards);
    let btcPrice = this.state.coinStat.btcPrice;
    let usdPrice = this.state.coinStat.usdPrice;
    let usdValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, usdPrice, 2);
    let btcValueRewards = SPCalc.multiplyAndFormat(totalRewardsInt, btcPrice, 8);

    return (<div>
      <p/>
      <p><b>Annual Withdrawal History</b></p>
      <p/>
      <BootstrapTable keyField='withdrawalTime' data={ this.state.rewardsHistorySummaryAnnual }
        columns={ this.getRewardsHistoryColumns("Year") } striped expandableRow={ () => { return true; } }
        hover condensed noDataIndication="No results"/>
      <p/>
      </div>);
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    let totalStake = SPCalc.getTotal(this.state.rewards, "stake", true);
    let totalRewards = SPCalc.getTotal(this.state.rewards, "reward", true);

    //console.log("this.state.filterState : ", this.state.filterState); for {this.state.address}
    // <h4 style={{align: "center"}}><span><strong>Rewards History</strong></span></h4>
    return (
      <div>
        {HUtils.getBreadCrumb()}
        <h4 style={{align: "center"}}><span><strong>Rewards Details</strong></span></h4>
        {this.addView()}
        <p/>
        {this.renderRewardHeader(totalStake, totalRewards)}
        <p/>
        <CurrentRewards rewards={this.state.rewards} coinStat={this.state.coinStat} />
        <p/><hr/>
        {this.renderRewardsHistory()}
        <p/>
        {this.renderRewardsHistorySummary()}
        <p/><hr/>
        {this.renderRewardsHistorySummaryAnnual()}
      </div>
    );
  }

  addView() {
    return <Views viewType="account" smartStake={this.state.smartStake} />
  }
}

export default Rewards;
