import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import Table from 'react-bootstrap/Table';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import {Form, FormGroup, ControlLabel} from 'react-bootstrap';
import CollapsibleNote from "../base/CollapsibleNote";

import HNotes from "../harmony/HNotes";
import ErrorMessageBox from "../components/ErrorMessageBox";
import ApiUtils from '../util/ApiUtils';
import RespUtils from '../util/RespUtils';
import UITableUtils from '../util/UITableUtils';
import HValNav from './HValNav';

import HValHeader from './HValHeader';
import "./Delegates.css";
import Utilities from "../util/Utilities";
import UIUtils from "../util/UIUtils";
import HUtils from "./HUtils";
import SPUtilities from "../util/SPUtilities";

class Keys extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      coinStat: {},
      val: {},
      lastUpdated: null,
      epoch: 0,
      noData: false,
      isLoading: true,
      width: window.innerWidth,
    }
    this.updateDimensions = this.updateDimensions.bind(this);
    this.moveLeft = this.moveLeft.bind(this);
    this.moveRight = this.moveRight.bind(this);
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
    let params = "?type=keys&hPoolId=" + hPoolId
    var epoch = this.props.match.params.epoch;
    if (epoch != undefined) {
      params += "&epoch=" + epoch;
    }

    const allData = await ApiUtils.get("listData" + params);
    // console.log("allData is:", allData);

    if (allData) {
      let val = allData["val"];
      let data = Utilities.addIndex(allData["data"]);
      let lastUpdated = allData["lastUpdated"];

      let coinStat = allData["coinStat"];

      if (allData["data"] != null && allData["data"].length === 0) {
        this.setState({error: "Data not available for this epoch. Please use prev/next epoch arrows to load data for a more current epoch."});
        this.setState({val: val, epoch: allData["epoch"], data: data,
          coinStat: coinStat, lastUpdated: lastUpdated, isLoading: false});
      } else if (allData) {
        this.setState({val: val, epoch: allData["epoch"], data: data,
          coinStat: coinStat, lastUpdated: lastUpdated});
      }
    }

    this.setState({isLoading: false});
  }

  render() {
    if (this.state.isLoading === true) {
      return <div>Loading</div>;
    }

    var columns;
    if (RespUtils.isMobileView()) {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(5)},
        {text: "BLS Key",dataField: "blsKey", formatter: HUtils.blsKeyFormatter, sort: true, headerStyle: Utilities.width(35)},
        {text: "Shard ID",dataField: "shardId", sort: true, headerStyle: Utilities.width(10)},
        {text: "Perf Index",dataField: "keyPerfIndex", formatter: HUtils.signPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "Bad Perf?",dataField: "isBadPerf", sort: true, headerStyle: Utilities.width(20)},
      ];
    } else if (RespUtils.isTabletView()) {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(5)},
        {text: "BLS Key",dataField: "blsKey", formatter: HUtils.blsKeyFormatter, sort: true, headerStyle: Utilities.width(30)},
        {text: "Shard ID",dataField: "shardId", sort: true, headerStyle: Utilities.width(10)},
        {text: "Group Reward Ratio",dataField: "groupRewardRatio", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(22)},
        {text: "Performance Index",dataField: "keyPerfIndex", formatter: HUtils.keySignPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(22)},
        {text: "Under Performing?",dataField: "isBadPerf", sort: true, headerStyle: Utilities.width(21)},
      ];
    } else {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(5)},
        {text: "BLS Key",dataField: "blsKey", formatter: HUtils.blsKeyFormatter, sort: true, headerStyle: Utilities.width(10)},
        {text: "Node Version",dataField: "nodeVersion", sort: true, headerStyle: Utilities.width(18)},
        {text: "Shard ID",dataField: "shardId", sort: true, headerStyle: Utilities.width(8)},
        {text: "Group % Stake",dataField: "groupPercentStake", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(11)},
        {text: "Group % Reward",dataField: "groupPercentReward", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(11)},
        {text: "Group Reward Ratio",dataField: "groupRewardRatio", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(13)},
        {text: "Performance Index",dataField: "keyPerfIndex", formatter: HUtils.keySignPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
        {text: "Under Performing?",dataField: "isBadPerf", sort: true, headerStyle: Utilities.width(23)},
      ];
    }

    const expandRow = {
      onlyOneExpanding: true,
      renderer: row => this.showRowDetails(row), showExpandColumn: false
    };
    const options = UIUtils.getPageOptionsSmall(this);
    let wrapperClasses = UITableUtils.isDefaultView() ? "table":"table-responsive";

    return (
      <div>
        <HValHeader val={this.state.val} title="BLS Keys"
          lastUpdated={this.state.lastUpdated} callerRef={this}/>
        {this.state.error != null && (<ErrorMessageBox message={this.state.error} />)}
        <Table bordered hover variant="dark" size="sm" >
          <tbody>
            <tr>
              <td>Total keys:</td>
              <th> {this.state.data.length}</th>
              <td>Epoch:</td>
              <th> <a class="white-a" href={"/keys/" + this.state.val.hPoolId + "/" + this.state.epoch}>{this.state.epoch}</a></th>
            </tr>
            <tr>
              <td>Current Sign %:</td>
              <th> <font color="red">{this.state.val.currentEpochSignPer}</font></th>
              <td>Current ERI:</td>
              <th>{this.state.val.currentEri}</th>
            </tr>
            <tr>
              <td>Asked to sign:</td>
              <th> {this.state.val.currentEpochToSign}</th>
              <td>Signed:</td>
              <th>{this.state.val.currentEpochSigned}</th>
            </tr>
          </tbody>
        </Table>
        <p>Please read screen guide to understand how BLS Key Performance Analyzer works. Performance Index metric is a secondary metric. The best indicator for your sign rate is still the Sign Rate for current/given epoch.</p>
        <hr/>
        <div>
            <span><a><img src="/images/left-arrow.svg" onClick={this.moveLeft} className="imgicon" width="32" height="32" /></a></span>
            <span className="buttonWithText"><a><img src="/images/right-arrow.svg" onClick={this.moveRight} className="imgicon" width="32" height="32" /></a>{'   '}</span>
        </div>

        <BootstrapTable keyField='index' data={ this.state.data }
          columns={ columns } striped options={options}
          expandRow={ expandRow } expandableRow={ () => { return true; } }
          wrapperClasses={wrapperClasses} hover condensed
          noDataIndication="Loading data"/>
        <HValNav hPoolId={this.state.val.hPoolId}/>
        <CollapsibleNote getScreenGuide={HNotes.getBlsNote} />
      </div>
    );
  }
  // } else if (this.state.noData === true) {
  //   return <div>No data available for the chose Epoch.</div>;

  moveLeft() {
    window.location = "/keys/" + this.state.val.hPoolId + "/" + (this.state.epoch - 1)
  }

  moveRight() {
    window.location = "/keys/" + this.state.val.hPoolId + "/" + (this.state.epoch + 1)
  }

  showRowDetails(row) {
    return (<div>
      <Table striped bordered size="sm">
        <tbody>
          <tr>
            <th align="left">BLS Key: </th>
            <td align="left"> {HUtils.blsKeyFormatterLarge(row.blsKey, row)}</td>
          </tr>
          <tr>
            <th>Node Version:</th>
            <td> {row.nodeVersion}</td>
          </tr>
          <tr>
            <th align="left">Shard ID: </th>
            <td align="left"> {row.shardId}</td>
          </tr>
          <tr>
            <th align="left">Epoch Number: </th>
            <td align="left"> {row.epochNumber}</td>
          </tr>
          <tr>
            <th align="left">Effective Stake: </th>
            <td align="left"> {row.effectiveStake}</td>
          </tr>
          <tr>
            <th align="left">Raw Stake: </th>
            <td align="left"> {row.rawStake}</td>
          </tr>
          <tr>
            <th align="left">Earned Reward: </th>
            <td align="left"> {row.reward}</td>
          </tr>
          <tr>
            <th align="left">Overall Percent Stake: </th>
            <td align="left"> {row.overallPercentStake}</td>
          </tr>
          <tr>
            <th align="left">Overall Percent Reward: </th>
            <td align="left"> {row.overallPercentReward}</td>
          </tr>
          <tr>
            <th align="left">Group % Stake: </th>
            <td align="left"> {row.groupPercentStake}</td>
          </tr>
          <tr>
            <th align="left">Group % Reward: </th>
            <td align="left"> {row.groupPercentReward}</td>
          </tr>
          <tr>
            <th align="left">Group Reward Ratio: </th>
            <td align="left"> {row.groupRewardRatio}</td>
          </tr>
          <tr>
            <th align="left">Key Performance Index: </th>
            <td align="left"> {HUtils.keySignPerFormatter(row.keyPerfIndex, row)}</td>
          </tr>
          <tr>
            <th align="left">Under Performing?: </th>
            <td align="left"> {row.isBadPerf}</td>
          </tr>
        </tbody>
      </Table>
      <hr/>
    </div>);
  }
}

export default Keys;
