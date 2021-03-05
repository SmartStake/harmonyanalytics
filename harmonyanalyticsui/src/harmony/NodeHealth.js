import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import Alert from 'react-bootstrap/Alert'
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import {Button} from '@material-ui/core';
import {Link} from 'react-router-dom';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';

import ApiUtils from '../util/ApiUtils';
import HValNav from './HValNav';

import "./NodeHealth.css";
import Utilities from "../util/Utilities";
import UIUtils from "../util/UIUtils";
import SPUtilities from "../util/SPUtilities";

class NodeHealth extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      activities: [],
      val: {},
      width: window.innerWidth,
      // showSmallBalance: true,
      size: 10,
    }
    this.updateDimensions = this.updateDimensions.bind(this);
    // this.reload = this.reload.bind(this);
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

    // var poolId = UIUtils.getPoolId(this);
    // + poolId &poolId=1
    const allData = await ApiUtils.get("listData?type=health");
    // console.log(allData);
    if (!allData) {
      this.setState({error: true, isLoading: false});
      return;
    }

    this.setState({val: allData["pool"],
      activities: allData["activities"], isLoading: false});
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    var columns;
    if (window.innerWidth < 600) {
      columns = [
        {text: "Mins Elapsed",dataField: "elapsedTime", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
        {text: "Gap",dataField: "heightGap", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Node Name",dataField: "nodeName", sort: true, headerStyle: Utilities.width(30)},
        // {text: "Timestamp",dataField: "epochTimestamp", formatter: SPUtilities.epochFormatter, sort: true, headerStyle: Utilities.width(50)},
        {text: "Block Height",dataField: "nodeBlockHeight", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(30)},
      ];
    } else if (window.innerWidth < 1000) {
      columns = [
        {text: "Mins Elapsed",dataField: "elapsedTime", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
        {text: "Block Gap",dataField: "heightGap", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Node Name",dataField: "nodeName", sort: true, headerStyle: Utilities.width(12)},
        {text: "Timestamp",dataField: "epochTimestamp", formatter: SPUtilities.epochFormatter, sort: true, headerStyle: Utilities.width(22)},
        {text: "Network Block Height", dataField: "networkBlockHeight", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(17)},
        {text: "Node Block Height",dataField: "nodeBlockHeight", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(17)},
      ];
    } else {
      columns = [
        {text: "Mins Elapsed",dataField: "elapsedTime", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
        {text: "Block Gap",dataField: "heightGap", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Node Name",dataField: "nodeName", sort: true, headerStyle: Utilities.width(12)},
        {text: "Timestamp",dataField: "epochTimestamp", formatter: SPUtilities.epochFormatter, sort: true, headerStyle: Utilities.width(26)},
        {text: "Network Block Height", dataField: "networkBlockHeight", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Node Block Height",dataField: "nodeBlockHeight", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Shard ID",dataField: "shardId", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
      ];
    }

    const options = UIUtils.getPageOptions(this);

    const expandRow = {
      renderer: row => (
        <div>
          <table>
            <tbody>
              <tr>
                <th align="left">Node Name: </th>
                <td align="left"> {row.nodeName}</td>
              </tr>
              <tr>
                <th align="left">Checkup Time: </th>
                <td align="left"> {SPUtilities.epochFormatter(row.checkupTime)}</td>
              </tr>
              <tr>
                <th align="left">Network Block Height: </th>
                <td align="left"> {row.networkBlockHeight}</td>
              </tr>
              <tr>
                <th align="left">Node Block Height: </th>
                <td align="left"> {row.nodeBlockHeight}</td>
              </tr>
              <tr>
                <th align="left">Gap: </th>
                <td align="left"> {row.heightGap}</td>
              </tr>
              <tr>
                <th align="left">Elapsed Time (min): </th>
                <td align="left"> {row.elapsedTime}</td>
              </tr>
              <tr>
                <th align="left">Node Shard ID: </th>
                <td align="left"> {row.shardId}</td>
              </tr>
            </tbody>
          </table>
        </div>
      ), showExpandColumn: false
    };

    var elapsedTime = Utilities.getFirstRecordAttribute(this.state.activities, "elapsedTime");
    var gap = Utilities.getFirstRecordAttribute(this.state.activities, "heightGap");

    var statusAndStatusDesc = this.getStatusAndStatusDesc(elapsedTime, gap);
    // console.log("pool is: ", this.state.pool)

    return (
      <div>
        <p/>
        <h4 style={{align: "center"}}><span>Smart Stake Node Health</span>
          <span className="buttonWithText"><img src="/images/reload.svg" onClick={this.reload} title="Reload Screen"
            className="imgicon" width="32" height="32" />&nbsp;&nbsp;&nbsp;</span>
        </h4>
        <p/>
        <Alert variant={statusAndStatusDesc[0]}>
          <Alert.Heading>{statusAndStatusDesc[1]}</Alert.Heading>
          <hr />
          <ul>
            <li>Time since last check: {elapsedTime} minutes.</li>
            <li>Latest block gap between validator node and Harmony network: {gap} blocks.</li>
          </ul>
        </Alert>
        <p/>
        <p><b><strong>Health Check Details</strong></b></p>
        <BootstrapTable keyField='healthid' data={ this.state.activities }
          columns={ columns } expandRow={ expandRow } striped expandableRow={ () => { return true; } }
          filter={ filterFactory() } hover condensed noDataIndication="Table is Empty/Loading"/>

        <HValNav hPoolId="42"/>
        <div>
          <p><b>Screen Guide</b></p>
          <ul className="mb-0">
            <li>Gap of &lt;5 means that 'Smart Stake' validator is essentially in sync with the Harmony Network.</li>
            <li>Time elapsed of &lt;10 minutes means that health reporting is working.</li>
            <li>Click anywhere on a record to see more details.</li>
            <li><a href='https://t.me/SmartStake' target='_blank'>Contact Validator</a> to report issues.</li>
          </ul>
        </div>
      </div>
    );
  }

  getStatusAndStatusDesc(elapsedTime, gap) {
    // console.log("activities are:");
    // console.log(this.state.activities);
    if (this.state.activities === undefined || this.state.activities.length == 0) {
      return ["danger", "Monitoring tool is not working."];
    }

    var elapsedTimeMsg = "Health check was performed recently.";
    var gapMsg = "Smart Stake node and Harmony Network are in sync at the time of last health check.";
    var danger = false;
    var warning = false;

    if (elapsedTime > 10) {
      elapsedTimeMsg = "Health check not performed for " + elapsedTime + " minutes. Monitoring tool may not be working correctly.";
      warning = true;
    }

    if (gap > 10 || gap < -10 ) {
      gapMsg = "Block gap between validator node and Harmony network is " + gap + " (high).";
      danger = true;
    } else if (gap > 5 || gap < -5 ) {
      gapMsg = "Block gap between validator node and Harmony network is " + gap + ".";
      warning = true;
    }

    var status = "success";
    var message;
    if (danger) {
      message = elapsedTimeMsg + " " + gapMsg + " Contact pool operator to report the issue.";
      status = "danger";
    } else if (warning) {
      message = elapsedTimeMsg + " " + gapMsg + " There may be some issue or it may be just a reporting glitch. Keep watching.";
      status = "warning";
    } else {
      message = elapsedTimeMsg + " " + gapMsg;
      status = "success";
    }

    return [status, message];
  }


  styleGap(cell, row, rowIndex, colIndex) {
    if (cell < -5) {
      return {backgroundColor: 'yellow'};
    } else if (cell > -5 && cell < 5) {
      return {backgroundColor: 'green'};
    } else if (cell > 5) {
      return {backgroundColor: 'yellow'};
    } else if (cell > 15) {
      return {backgroundColor: 'red'};
    }
  }


  static dateFormatter(value, row) {
      return SPUtilities.getDateTimeAsText(value);
  }

  // reload() {
  //   window.location = "/health/1";
  //   // + this.state.pool.poolId;
  // }

}

export default NodeHealth;
