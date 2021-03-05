import React from 'react';
import Table from 'react-bootstrap/Table';
import BootstrapTable from 'react-bootstrap-table-next';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import {Button} from '@material-ui/core';
import paginationFactory from 'react-bootstrap-table2-paginator';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';
import constants from "../constants";

import NetworkUtils from "../util/NetworkUtils";
import UITableUtils from "../util/UITableUtils";
import NetworkHeader from './NetworkHeader';
import HNetworkNav from './HNetworkNav';
import "./Election.css";
import FavUtils from "../util/FavUtils";
import RespUtils from "../util/RespUtils";

import HUtils from '../harmony/HUtils';
import ElectionUtils from './ElectionUtils';

// import CDTimer from '../base/CDTimer';

import LogoUtils from '../util/LogoUtils';
import SPCalc from '../util/SPCalc';
import ApiUtils from '../util/ApiUtils';
import Utilities from "../util/Utilities";
import UIUtils from "../util/UIUtils";
import SPUtilities from "../util/SPUtilities";

class Election extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      electionDetails: null,
      slots: null,
      validators: [],
      coinStat: {},
      timeRemaining: "",
      blockRemaining: "",
      changeStyle: "highlight-default",
      width: window.innerWidth,
      loading: true,
    }
    this.updateDimensions = this.updateDimensions.bind(this);
    this.getHeader = this.getHeader.bind(this);
    this.favourite = this.favourite.bind(this);
    this.unfavourite = this.unfavourite.bind(this);
    this.getTimeAndBlockRemaining = this.getTimeAndBlockRemaining.bind(this);
    this.calcTimeRemaining = this.calcTimeRemaining.bind(this);
    this.processLatestBlock = this.processLatestBlock.bind(this);
    this.processTimeRemaining = this.processTimeRemaining.bind(this);

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

    const allData = await ApiUtils.get("listData?type=listPoolsSummary");
    // console.log(allData);
    if (!allData) {
      return;
    }

    this.setState({validators: allData["data"], coinStat: allData["coinStat"]});

    this.processLatestBlock();

    // console.log("fetching election data");
    let url = NetworkUtils.getElectionUrl();
    fetch(url)
      .then(res => res.json())
      .then((data) => {
        // console.log(data);
        // let slots = Utilities.addIndex(data.live_table);
        let slots = this.addDetails(data.live_table);
        // slots = FavUtils.filterData(this, slots);
        let electionData = {currentEpoch: data.current_epoch,
          totalSeats: data.total_seats,
          epochLastBlock: data["epoch-last-block"],
          liveExternalShards: data.liveExternalShards,
        };
        this.setState({ electionData: electionData, slots: slots, loading: false });
      }).catch(console.log)

    // console.log("after calling fetch election data");
    //reload realtime stats every minute
    setTimeout(SPUtilities.refresh, 60000);
    setTimeout(this.calcTimeRemaining, 2000);
    setTimeout(this.processLatestBlock, 5000);
  }

  processLatestBlock() {
    const requestOptions = {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          method: 'hmyv2_blockNumber',
          params: [],
          jsonrpc: '2.0',
          id: 1})
    };
    fetch('https://api.s0.t.hmny.io/hmyv2_blockNumber', requestOptions)
        .then(response => response.json())
        .then(data => {
          this.setState({latestBlock: data["result"], changeStyle: "highlight-change"})
          this.processTimeRemaining();
        });

    setTimeout(this.processLatestBlock, 5000);
  }

  processTimeRemaining() {
    let tbRemaining = this.getTimeAndBlockRemaining();
    // console.log("timeRemaining: ", tbRemaining, ", this.state.timeRemaining: ", this.state.timeRemaining);
    if (tbRemaining[0] === this.state.timeRemaining) {
      this.setState({changeStyle: "highlight-default"});
    } else {
      this.setState({timeRemaining: tbRemaining[0], blockRemaining: tbRemaining[1], });
    }
  }

  calcTimeRemaining() {
    this.processTimeRemaining();
    // if (timeRemaining === this.state.timeRemaining && this.state.changeStyle === "highlight-default") {
    //   this.setState({changeStyle: "highlight-change"});
    // } else {
    //   this.setState({timeRemaining: timeRemaining, changeStyle: "highlight-default"});
    // }
    setTimeout(this.calcTimeRemaining, 1000);
  }

  addDetails(listData) {
    // console.log("in addDetails: ", listData);
    if (!listData) {
      return [];
    }

    let validators = this.state.validators;
    let details = [];
    for (let i = 0, tableDataLen = listData.length; i < tableDataLen; i++) {
      let data = listData[i];
      let validator = this.getValidator(validators, data["address"]);
      // console.log(data);
      let detail = {}
      detail.index = i + 1;
      detail.name = data.name;
      detail.hPoolId = validator.hPoolId;
      detail.slot = data.slot;
      detail.address = data.address;
      detail.hasLogo = data.hasLogo;
      detail.bid = SPUtilities.divByPower18(data.bid, data);
      detail.effectiveStake = SPUtilities.divByPower18(data.effective_stake, data);
      detail.totalStake = SPUtilities.divByPower18(data.total_stake, data);
      detail.actualStake = validator.totalStaked;
      detail.slotsRequested = Math.round(detail.actualStake / SPUtilities.divByPower18(data.bid, data));
      // console.log("slots requested: ", detail.slotsRequested, Math.round(detail.actualStake / detail.bid), detail.actualStake, detail.bid);
      detail.slotDetails = ElectionUtils.getSlotCountAndStatus(data.slot, detail);
      detail.slotDetails.bid = SPUtilities.divByPower18(data.bid, data)
      detail.totalSlots = detail.slotDetails.slotCount;
      // let countAndStatus = ElectionUtils.getSlotCountAndStatus(data.slot, detail);
      // console.log("countAndStatus: ", countAndStatus);
      // detail.totalSlots = countAndStatus[0];
      // detail.status = countAndStatus[1];
      // console.log("addDetails: ", i, " - ");
      // console.log(detail);
      details.push(detail);
    }

    details = ElectionUtils.processForWhatIf(details)
    // console.log(details);
    let finalData = FavUtils.filterData(this, details);
    // console.log(finalData);
    return finalData;
  }

  getValidator(validators, address) {
    for(let i=0; i < validators.length; i++) {
      if (validators[i].address === address) {
        return validators[i];
      }
    }

    return {};
  }

  render() {
    if (this.state.isLoading || this.state.slots === null) {
      return <div>Loading</div>;
    }

    var columns;
    if (RespUtils.isMobileView()) {
      columns = [
        {text: "",dataField: "hPoolId", sort: true, formatter: FavUtils.favoriteFormatter, formatExtraData: this, headerStyle: Utilities.width(5)},
        {text: "Slot", dataField: "index", formatter: HUtils.slotFormatter, sort: true, style: ElectionUtils.slotStyle, headerStyle: Utilities.width(15)},
        {text: "Name", dataField: "name", formatter: HUtils.nameFormatterShort, sort: true, headerStyle: Utilities.width(20)},
        {text: "Bid", dataField: "bid", formatter: SPUtilities.stakeFormatterRoundedTwo, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "BLS +1", dataField: "slotRangePlusOne", style: ElectionUtils.slotStylePlusOne, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "BLS -1", dataField: "slotRangeMinusOne", style: ElectionUtils.slotStyleMinusOne, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
      ];
    } else if (RespUtils.isTabletView()) {
      columns = [
        {text: "",dataField: "hPoolId", sort: true, formatter: FavUtils.favoriteFormatter, formatExtraData: this, headerStyle: Utilities.width(4)},
        {text: "Slot", dataField: "index", formatter: HUtils.slotFormatter, sort: true, style: ElectionUtils.slotStyle, headerStyle: Utilities.width(12)},
        {text: "Name", dataField: "name", formatter: HUtils.nameFormatterShort, sort: true, headerStyle: Utilities.width(15)},
        {text: "Bid", dataField: "bid", formatter: SPUtilities.formatCoins, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Eff. Stake", dataField: "effectiveStake", formatter: SPUtilities.formatCoins, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "BLS +1", dataField: "slotRangePlusOne", style: ElectionUtils.slotStylePlusOne, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "BLS -1", dataField: "slotRangeMinusOne", style: ElectionUtils.slotStyleMinusOne, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
      ];
    } else {
      columns = [
        {text: "",dataField: "hPoolId", sort: true, formatter: FavUtils.favoriteFormatter, formatExtraData: this, headerStyle: Utilities.width(3)},
        {text: "Slot", dataField: "index", formatter: HUtils.slotFormatter, sort: true, style: ElectionUtils.slotStyle, headerStyle: Utilities.width(6)},
        {text: "", dataField: "address", sort: true, formatter: LogoUtils.formatLogoFlag, headerStyle: Utilities.width(3)},
        {text: "Name", dataField: "name", formatter: HUtils.nameFormatter, sort: true, headerStyle: Utilities.width(12)},
        {text: "Bid", dataField: "bid", sort: true, formatter: SPUtilities.formatCoins,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "Effective Stake", dataField: "effectiveStake", formatter: SPUtilities.formatCoins, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "Slots Requested", dataField: "slotsRequested", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
        {text: "Slots Allotted", dataField: "totalSlots", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(6)},
        {text: "Used Stake", dataField: "totalStake", formatter: SPUtilities.formatCoins, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "Actual Stake", dataField: "actualStake", formatter: SPUtilities.formatCoins, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "BLS +2", dataField: "slotRangePlusTwo", style: ElectionUtils.slotStylePlusTwo, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "BLS +1", dataField: "slotRangePlusOne", style: ElectionUtils.slotStylePlusOne, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "BLS -1", dataField: "slotRangeMinusOne", style: ElectionUtils.slotStyleMinusOne, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "BLS -2", dataField: "slotRangeMinusTwo", style: ElectionUtils.slotStyleMinusTwo, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
      ];
    }

    const options = UIUtils.getPageOptionsLarge(this);
    let wrapperClasses = UITableUtils.isDefaultView() ? "table":"table-responsive";
    const expandRow = {
      renderer: row => (
        this.getInlineDetails(row)
      ), showExpandColumn: false
    };

    return (
      <div>
        <NetworkHeader title="Next Election" />
        <p><a target="_blank" href="https://staking.harmony.one/analytics/mainnet">Harmony Elections Website</a></p>
        {this.getHeader()}
        <hr/>
        <p><strong>Bid Slots</strong></p>
        <BootstrapTable keyField='address' data={this.state.slots} filter={ filterFactory() }
          columns={ columns } striped expandableRow={ () => { return true; } } options={options}
          expandRow={ expandRow } hover condensed noDataIndication="Table is Empty/Loading" wrapperClasses={wrapperClasses}/>
        <HNetworkNav />
        {RespUtils.getSpecialMessage()}
        <p>The slots allocation is a very dynamic aspect of Harmony EPoS and can change rapidly. If you are making changes to BLS keys, please consider all aspects and don't use the information provided here blindly. Actual Stake is reported from Smart Stake backend and may not have last couple of minutes of delegations/undelegations.</p>
      </div>
    );
  }

  getHeader() {
    if (this.state.electionData == null) {
      return "";
    }

    if (RespUtils.isMobileView()) {
      return (<div>
        <Table bordered hover size="sm" >
          <tbody>
            <tr>
              <td>Epoch</td>
              <th>{this.state.electionData.currentEpoch}</th>
              <td>Next Epoch</td>
              <th className={this.state.changeStyle}>{this.state.timeRemaining}</th>
            </tr>
            <tr>
              <td>Last Block</td>
              <th className={this.state.changeStyle}>{this.state.latestBlock}</th>
              <td>Blocks Remaining</td>
              <th className={this.state.changeStyle}>{this.state.blockRemaining}</th>
            </tr>
          </tbody>
        </Table>
        {this.getShardSeatsDisplay()}
      </div>);
    }

    return (<div>
      <Table bordered hover size="sm" >
        <tbody>
          <tr>
            <td>Current Epoch</td>
            <th>{this.state.electionData.currentEpoch}</th>
            <td>Current Block</td>
            <th className={this.state.changeStyle}>{this.state.latestBlock}</th>
            <td>Time till Next Epoch</td>
            <th className={this.state.changeStyle}>{this.state.timeRemaining}</th>
          </tr>
          <tr>
            <td>Total Seats</td>
            <th>{this.state.electionData.totalSeats}</th>
            <td>Last Block in Epoch</td>
            <th>{this.state.electionData.epochLastBlock}</th>
            <td>Blocks Remaining</td>
            <th className={this.state.changeStyle}>{this.state.blockRemaining}</th>
          </tr>
        </tbody>
      </Table>
      {this.getShardSeatsDisplay()}
    </div>);
  }

  getShardSeatsDisplay() {
    if (RespUtils.isMobileView()) {
      return (<Table bordered hover size="sm" >
        <tbody>
          <tr>
            <td>Shard 0:</td><th> {this.getShardSeats(0)}</th>
            <td>Shard 1:</td><th> {this.getShardSeats(1)}</th>
          </tr>
          <tr>
            <td>Shard 2:</td><th> {this.getShardSeats(2)}</th>
            <td>Shard 3:</td><th> {this.getShardSeats(3)}</th>
          </tr>
        </tbody>
      </Table>);
    }

    return (<Table bordered hover size="sm" >
      <tbody>
        <tr>
          <td>Shard 0:</td><th> {this.getShardSeats(0)}</th>
          <td>Shard 1:</td><th> {this.getShardSeats(1)}</th>
          <td>Shard 2:</td><th> {this.getShardSeats(2)}</th>
          <td>Shard 3:</td><th> {this.getShardSeats(3)}</th>
        </tr>
      </tbody>
    </Table>);
  }

  getShardSeats(shardNum) {
    // console.log("in getShardSeats");
    let shard = this.state.electionData.liveExternalShards[shardNum];
    // console.log(shards);
    // console.log(shards.length + " - " + shardNum);
    if(shard === null) {
      return 0;
    }
    // console.log(shard + " - moving on for shardNum: ", shardNum);
    let seats = shard.external;
    // let seats = this.state.electionData.externalShards[shardNum].external;
    // console.log(seats)
    if (seats < 160) {
      return <span className="seats-under">{seats}</span>;
    } else if (seats > 160) {
      return <span className="seats-over">{seats}</span>;
    }

    return <span className="seats">{seats}</span>;
  }

  unfavourite(e) {
    FavUtils.unfavourite(e, this);
  }

  favourite(e) {
    FavUtils.favourite(e, this);
  }

  getInlineDetails(row) {
    return (<div>
      <Table bordered hover size="sm" >
        <tbody>
          <tr>
            <th align="left">Validator Name: </th>
            <td align="left"> {HUtils.nameFormatterLong(row.name, row)}</td>
          </tr>
          <tr>
            <th align="left">Slot Range: </th>
            <td align="left"> {row.slot}</td>
          </tr>
          <tr>
            <th align="left">Bid: </th>
            <td align="left"> {SPUtilities.formatCoins(row.bid)}</td>
          </tr>
          <tr>
            <th align="left">Effective Stake: </th>
            <td align="left"> {SPUtilities.formatCoins(row.effectiveStake)}</td>
          </tr>
          <tr>
            <th align="left">Slots Requested: </th>
            <td align="left"> {row.slotsRequested}</td>
          </tr>
          <tr>
            <th align="left">Slots Allotted: </th>
            <td align="left"> {row.totalSlots}</td>
          </tr>
          <tr>
            <th align="left">Used Stake: </th>
            <td align="left"> {row.totalStake}</td>
          </tr>
          <tr>
            <th align="left">Actual Stake: </th>
            <td align="left"> {row.actualStake}</td>
          </tr>
        </tbody>
      </Table>
      <p><strong>Slots Impact</strong></p>
      <Table bordered hover size="sm" >
        <tbody>
          <tr>
            <th>Rule</th>
            <th>Slot Count</th>
            <th>Slot Range</th>
            <th>Bid</th>
          </tr>
          <tr>
            <td> Current + 3</td>
            <td> {row.slotDetailsPlusThree.slotCount}</td>
            <td style={ElectionUtils.slotStyleByStatus(row.slotDetailsPlusThree.status)}> {row.slotDetailsPlusThree.slotRange}</td>
            <td> {row.slotDetailsPlusThree.bid}</td>
          </tr>
          <tr>
            <td> Current + 2</td>
            <td> {row.slotDetailsPlusTwo.slotCount}</td>
            <td style={ElectionUtils.slotStyleByStatus(row.slotDetailsPlusTwo.status)}> {row.slotDetailsPlusTwo.slotRange}</td>
            <td> {row.slotDetailsPlusTwo.bid}</td>
          </tr>
          <tr>
            <td> Current + 1</td>
            <td> {row.slotDetailsPlusOne.slotCount}</td>
            <td style={ElectionUtils.slotStyleByStatus(row.slotDetailsPlusOne.status)}> {row.slotDetailsPlusOne.slotRange}</td>
            <td> {row.slotDetailsPlusOne.bid}</td>
          </tr>
          <tr>
            <td> Current</td>
            <td> {row.slotDetails.slotCount}</td>
            <td style={ElectionUtils.slotStyleByStatus(row.slotDetails.status)}> {row.slot}</td>
            <td> {row.bid}</td>
          </tr>
          <tr>
            <td> Current - 1</td>
            <td> {row.slotDetailsMinusOne.slotCount}</td>
            <td style={ElectionUtils.slotStyleByStatus(row.slotDetailsMinusOne.status)}> {row.slotDetailsMinusOne.slotRange}</td>
            <td> {row.slotDetailsMinusOne.bid}</td>
          </tr>
          <tr>
            <td> Current - 2</td>
            <td> {row.slotDetailsMinusTwo.slotCount}</td>
            <td style={ElectionUtils.slotStyleByStatus(row.slotDetailsMinusTwo.status)}> {row.slotDetailsMinusTwo.slotRange}</td>
            <td> {row.slotDetailsMinusTwo.bid}</td>
          </tr>
          <tr>
            <td> Current - 3</td>
            <td> {row.slotDetailsMinusThree.slotCount}</td>
            <td style={ElectionUtils.slotStyleByStatus(row.slotDetailsMinusThree.status)}> {row.slotDetailsMinusThree.slotRange}</td>
            <td> {row.slotDetailsMinusThree.bid}</td>
          </tr>
        </tbody>
      </Table>
    </div>);
  }

  getTimeAndBlockRemaining() {
    if (this.state.electionData == null || isNaN(this.state.electionData.epochLastBlock) || isNaN(this.state.latestBlock)) {
      return "";
    }
    // let dtTime = new Date(this.state.electionData.time_next_epoch * 1000).toISOString();
    let blocksRemaining = this.state.electionData.epochLastBlock - this.state.latestBlock;
    let timeRemaining = blocksRemaining * constants.BLOCK_TIME;
    // console.log(timeRemaining);
    let dtTime = new Date(timeRemaining * 1000).toISOString();

    let hour = dtTime.substr(11, 2);
    let minute = dtTime.substr(14, 2);
    let seconds = dtTime.substr(17, 2);

    return [hour + " h " + minute + " m " + seconds + "s", blocksRemaining];

  }
}

export default Election;
/*
slotStyle(cell, row) {
  let color = "#ccffcc";
  console.log(row.slot);
  let slots = row.slot;

  if (slots != null) {
    if (slots.indexOf("-") == -1) {
      console.log("parseInt(slots): ", parseInt(slots));
      if (parseInt(slots) > 640) {
        // return {"background-image": "linear-gradient(to right, red, #ffffff)"};
        color = "#ff9999";
      }
    } else {
      let slotsList = slots.split("-");
      console.log("parseInt(slots): ", parseInt(slotsList[1]));
      if (parseInt(slotsList[1]) > 640) {
        //FIXME - partial election
        // return {"background-image": "linear-gradient(to right, red, #ffffff)"};
        color = "#ff9999";
      }
    }
    return {"background-image": "linear-gradient(to right, " + color + ", #ffffff)"};
  }
}
*/
