import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import Table from 'react-bootstrap/Table';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import Card from 'react-bootstrap/Card';
import CardDeck from 'react-bootstrap/CardDeck';
import Breadcrumb from 'react-bootstrap/Breadcrumb';
import CollapsibleNote from "../base/CollapsibleNote";

import HNotes from "../harmony/HNotes";
import BaseLineChart from "../reports/BaseLineChart";
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

class Key extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      coinStat: {},
      keyDetails: {},
      val: {},
      lastUpdated: null,
      epoch: "",
      width: window.innerWidth,
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

    let params = "?type=key"
    var epoch = this.props.match.params.epoch;
    if (epoch != undefined) {
      params += "&epoch=" + epoch;
    }
    var blsKey = this.props.match.params.blsKey;
    if (epoch != undefined) {
      params += "&blsKey=" + blsKey;
    }

    const allData = await ApiUtils.get("listData" + params);
    // console.log("allData is:", allData);

    if (allData) {
      let val = allData["val"];
      let keyDetails = allData["keyDetails"];
      let data = Utilities.addIndex(allData["data"]);
      let lastUpdated = allData["lastUpdated"];

      this.setState({val: val, epoch: epoch, data: data,
        lastUpdated: lastUpdated, keyDetails: keyDetails,
        isLoading: false});
    }

    this.setState({isLoading: false});
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    const defaultSorted = [{
      dataField: 'title',
      order: 'desc' // desc or asc
    }];

    var columns;
    if (RespUtils.isMobileView()) {
      columns = [
        {text: "Sync Time", dataField: "title", sort: true, headerStyle: Utilities.width(40)},
        {text: "Reward Ratio",dataField: "groupRewardRatio", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "Perf Index",dataField: "keyPerfIndex", formatter: HUtils.keySignPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "Bad Perf?",dataField: "isBadPerf", sort: true, headerStyle: Utilities.width(20)},
      ];
    } else {
      columns = [
        {text: "Sync Time", dataField: "title", sort: true, headerStyle: Utilities.width(25)},
        {text: "Group % Stake",dataField: "groupPercentStake", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(14)},
        {text: "Group % Reward",dataField: "groupPercentReward", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(14)},
        {text: "Group Reward Ratio",dataField: "groupRewardRatio", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(14)},
        {text: "Performance Index",dataField: "keyPerfIndex", formatter: HUtils.keySignPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(19)},
        {text: "Under Performing?",dataField: "isBadPerf", sort: true, headerStyle: Utilities.width(14)},
      ];
    }

    const expandRow = {
      onlyOneExpanding: true,
      renderer: row => this.showRowDetails(row), showExpandColumn: false
    };
    const options = UIUtils.getPageOptionsSmall(this);
    let wrapperClasses = UITableUtils.isDefaultView() ? "table":"table-responsive";
    let heading = "Key Performance: " + SPUtilities.addressLabelShortFormatter(this.state.keyDetails.blsKey, null, true);
    let latestPerf = {};
    if (this.state.data.length > 0) {
      latestPerf = this.state.data[this.state.data.length - 1];
    }

    return (
      <div>
        <HValHeader val={this.state.val}
          title={heading}
          lastUpdated={this.state.lastUpdated} callerRef={this}/>

        {this.getKeysBreadCrumb()}
        <Table bordered hover variant="dark" size="sm" >
          <tbody>
            <tr>
              <td>Key</td>
              <th colspan="3">{SPUtilities.addressLabelShortFormatter(this.state.keyDetails.blsKey, null, RespUtils.isTabletView())}</th>
            </tr>
            <tr>
              <td>Shard:</td>
              <th> {this.state.keyDetails.shardId}</th>
              <td>Epoch:</td>
              <th> <a class="white-a" href={"/keys/" + this.state.val.hPoolId + "/" + this.state.epoch}>{this.state.epoch}</a></th>
            </tr>
            <tr>
              <td>Is Under Performing?:</td>
              <th> {latestPerf.isBadPerf}</th>
              <td>Performance Index:</td>
              <th>{latestPerf.keyPerfIndex}</th>
            </tr>
          </tbody>
        </Table>
        <p/>
        <p>Please read screen guide to understand how BLS Key Performance Analyzer works. Performance Index metric is a secondary metric. The best indicator for your sign rate is still the Sign Rate for current/given epoch.</p>

        <BaseLineChart title="Key Sign Percentage" xAxis="Time" yAxis="Sign Percentage"
          showVerticalLabel={true} valueAttr="keyPerfIndex" showTotalLabel={false} xAxisValueAttr="title"
          data={this.state.data} />

        <hr/>
        <p/>
        <BootstrapTable keyField='index' data={ this.state.data }
          columns={ columns } striped options={options}
          expandRow={ expandRow } expandableRow={ () => { return true; } }
          wrapperClasses={wrapperClasses} hover condensed
          defaultSorted={defaultSorted} noDataIndication="Loading data"/>
        <HValNav hPoolId={this.state.val.hPoolId}/>
        <CollapsibleNote getScreenGuide={HNotes.getBlsNote} />
      </div>
    );
  }

  showRowDetails(row) {
    return (<div>
      <Table striped bordered size="sm">
        <tbody>
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
            <td align="left"> {HUtils.signPerFormatter(row.keyPerfIndex, row)}</td>
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

  getKeysBreadCrumb() {
    return (
      <Breadcrumb>
        <Breadcrumb.Item href={"/keys/" + this.state.val.hPoolId}><img src="/images/left-arrow.svg" onClick={this.moveLeft} className="imgicon" width="16" height="16" /> All Keys</Breadcrumb.Item>
      </Breadcrumb>
    );
  }
}

export default Key;
