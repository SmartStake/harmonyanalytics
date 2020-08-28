import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import {Button} from '@material-ui/core';
import paginationFactory from 'react-bootstrap-table2-paginator';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';

import HNetworkNav from './HNetworkNav';

import "./Richlist.css";
import HUtils from '../harmony/HUtils';

import SPCalc from '../util/SPCalc';
import ApiUtils from '../util/ApiUtils';
import Utilities from "../util/Utilities";
import UIUtils from "../util/UIUtils";
import SPUtilities from "../util/SPUtilities";

class Richlist extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      width: window.innerWidth,
      size: 10,
      coinStat: {},
    }
    this.updateDimensions = this.updateDimensions.bind(this);
    this.reload = this.reload.bind(this);
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

    let count = 200;
    if (this.props.match.params.count != undefined) {
      count = this.props.match.params.count;
    }

    let allData = await ApiUtils.get("listData?type=richlist&count=" + count);
    // console.log("data is:", data);

    if (allData) {
      let data = allData["data"];
      let newData = Utilities.addIndex(data);

      let coinStat = allData["coinStat"];
      this.setState({data: newData, isLoading: false, coinStat: coinStat});
    }
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    var columns;
    if (window.innerWidth < 600) {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(13)},
        {text: "Address",dataField: "address", formatter: HUtils.addressFormatterByLabel, sort: true, headerStyle: Utilities.width(40)},
        {text: "Total",dataField: "totalBalance", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(26)},
        {text: "Staked",dataField: "totalStake", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(21)},
      ];
    } else if (window.innerWidth < 1000) {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(8)},
        {text: "Address",dataField: "address", formatter: HUtils.addressFormatterByLabel, filter: textFilter({placeholder: "Search loaded results"}), sort: true, headerStyle: Utilities.width(23)},
        {text: "Total $ONE",dataField: "totalBalance", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(13)},
        {text: "Staked Amount",dataField: "totalStake", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
        {text: "Not Staked",dataField: "addressBalance", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(14)},
        {text: "USD Value",dataField: "totalBalance", formatter: SPCalc.calcTotalUSD, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "BTC Value",dataField: "totalBalance", formatter: SPCalc.calcTotalBTC, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
      ];
    } else {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(5)},
        {text: "Address",dataField: "address", formatter: HUtils.addressFormatterByLabel, filter: textFilter({placeholder: "Search loaded results"}),
          sort: true, headerStyle: Utilities.width(35)},
        {text: "Total $ONE",dataField: "totalBalance", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Staked Amount",dataField: "totalStake", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Not Staked",dataField: "addressBalance", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "USD Value",dataField: "totalBalance", formatter: SPCalc.calcTotalUSD, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "BTC Value",dataField: "totalBalance", formatter: SPCalc.calcTotalBTC, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
      ];
    }

    const options = UIUtils.getPageOptionsLarge(this);

    // const expandRow = {
    //   onlyOneExpanding: true,
    //   renderer: row => (
    //     <div>
    //       <p/>
    //       <DelegateDetails address={row.address} />
    //     </div>
    //   ), showExpandColumn: true
    // };

    return (
      <div>
        <p/>
        <h4 style={{align: "center"}}><span><strong>Harmony - Overall Richlist</strong></span>
          <span className="buttonWithText"><img src="/images/reload.svg" onClick={this.reload} title="Reload Screen"
            className="imgicon" width="32" height="32" /></span>
        </h4>
        <p>Top <b>{this.state.data.length}</b> addresses. Sync up happens every 1 hour. Want alias for any of the address? <a href="https://t.me/bigb4ever">Contact here</a> with the address and alias.</p>
        <p><span className="buttonWithText"><Button variant="contained" color="primary" id="top200"
          onClick={ event => { window.location = "/richlist/200";}}
            >200</Button>&nbsp;<Button variant="contained" color="primary" id="top1000"
            onClick={ event => { window.location = "/richlist/1000";}}
            >1000</Button>&nbsp;<Button variant="contained" color="primary" id="top2000"
            onClick={ event => { window.location = "/richlist/2000";}}
            >2000</Button>&nbsp;<Button variant="contained" color="primary" id="all"
            onClick={ event => { window.location = "/richlist/10000000";}}>All</Button>{' '}
        </span></p>&nbsp;
        <BootstrapTable keyField='address' data={ this.state.data } filter={ filterFactory() }
          columns={ columns } striped expandableRow={ () => { return true; } } options={options}
          hover condensed noDataIndication="Table is Empty/Loading" pagination={ paginationFactory(options) }/>
        <HNetworkNav />
      </div>
    );
  }

  reload() {
    window.location = "/richlist";
  }

}

export default Richlist;
