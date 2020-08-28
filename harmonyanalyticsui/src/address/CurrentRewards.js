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
import paginationFactory from 'react-bootstrap-table2-paginator';
import Card from 'react-bootstrap/Card';
import CardDeck from 'react-bootstrap/CardDeck';
import Table from 'react-bootstrap/Table';

import ApiUtils from '../util/ApiUtils';
import UINotes from '../util/UINotes';
// import "./Rewards.css";
import Utilities from "../util/Utilities";
import SPUtilities from "../util/SPUtilities";
import SPCalc from "../util/SPCalc";
import Views from "./Views";

import FilterAddress from "./FilterAddress";
import HUtils from "../harmony/HUtils";

class CurrentRewards extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
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

  render() {
    let totalStake = SPCalc.getTotal(this.props.rewards, "stake", true);
    let totalRewards = SPCalc.getTotal(this.props.rewards, "reward", true);

    const expandRow = {
      onlyOneExpanding: true,
      renderer: row => this.showRowDetails(row), showExpandColumn: true
    };

    var columns;
    if (window.innerWidth < 600) {
      columns = [
        {text: "Validator", dataField: "name", formatter: HUtils.nameFormatter, sort: true,  headerStyle: Utilities.width(45)},
        {text: "Stake",dataField: "stake", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(30)},
        {text: "Rewards",dataField: "reward", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
      ];
    } else if (window.innerWidth < 1000) {
      columns = [
        {text: "Validator", dataField: "name", formatter: HUtils.nameFormatter, sort: true,  headerStyle: Utilities.width(25)},
        {text: "Stake",dataField: "stake", formatter: SPUtilities.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "% Stake (portfolio)",dataField: "stake", formatter: SPCalc.calcWeight, formatExtraData: totalStake, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Rewards",dataField: "reward", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "% Rewards (portfolio)", dataField: "reward", formatter: SPCalc.calcWeight, formatExtraData: totalRewards, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
      ];
    } else {
      columns = [
        {text: "Validator", dataField: "name", formatter: HUtils.nameFormatter, sort: true,  headerStyle: Utilities.width(20)},
        {text: "Fee", dataField: "fee", sort: true, formatter: HUtils.getFee, formatExtraData: this.props.coinStat.currentEpoch, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
        {text: "Avg Net ER", dataField: "avgNetApr", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Avg Sign %", dataField: "lifetimeSignPer", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Current Sign %", dataField: "currentEpochSignPer", formatter: HUtils.percentFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Val Total Stake", dataField: "totalStaked", formatter: HUtils.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Stake",dataField: "stake", formatter: HUtils.coinCountCellFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "% Stake (portfolio)",dataField: "stake", formatter: SPCalc.calcWeight, formatExtraData: totalStake, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
        {text: "Rewards",dataField: "reward", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "% Rewards (portfolio)",dataField: "reward", formatter: SPCalc.calcWeight, formatExtraData: totalRewards, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
      ];
    }

    return (<div>
      <BootstrapTable keyField='name' data={ this.props.rewards }
        columns={ columns } striped
        expandRow={ expandRow } expandableRow={ () => { return true; } }
        hover condensed noDataIndication="No results"/>
      </div>);
  }

  showRowDetails(row) {
    let totalStake = SPCalc.getTotal(this.props.rewards, "stake", true);
    let totalRewards = SPCalc.getTotal(this.props.rewards, "reward", true);

    return (<div>
      <Table striped bordered size="sm">
        <tbody>
          <tr>
            <th align="left">Validator: </th>
            <td align="left"> {HUtils.nameFormatter(row.name, row)}</td>
          </tr>
          <tr>
            <th align="left">Fee: </th>
            <td align="left"> {HUtils.getFee(row.fee, row, 0, this.props.coinStat.currentEpoch)}</td>
          </tr>
          <tr>
            <th align="left">Avg Net ER: </th>
            <td align="left"> {row.avgNetApr}</td>
          </tr>
          <tr>
            <th align="left">Avg Sign %: </th>
            <td align="left"> {row.lifetimeSignPer}%</td>
          </tr>
          <tr>
            <th align="left">Current Sign %: </th>
            <td align="left"> {HUtils.percentFormatter(row.currentEpochSignPer, row)}</td>
          </tr>
          <tr>
            <th align="left">Val Total Stake: </th>
            <td align="left"> {HUtils.coinCountCellFormatter(row.totalStaked, row)}</td>
          </tr>
          <tr>
            <th align="left">Delegated/Stake with the validator: </th>
            <td align="left"> {HUtils.coinCountCellFormatter(row.stake, row)}</td>
          </tr>
          <tr>
            <th align="left">% Stake (portfolio): </th>
            <td align="left"> {SPCalc.calcWeight(row.stake, row, 0, totalStake)}</td>
          </tr>
          <tr>
            <th align="left">Rewards: </th>
            <td align="left"> {row.reward}</td>
          </tr>
          <tr>
            <th align="left">% Rewards (portfolio): </th>
            <td align="left"> {SPCalc.calcWeight(row.reward, row, 0, totalRewards)}</td>
          </tr>
        </tbody>
      </Table>
      <hr/>
    </div>);
  }

}

export default CurrentRewards;
