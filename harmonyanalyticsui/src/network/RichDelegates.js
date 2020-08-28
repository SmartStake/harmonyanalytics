import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import paginationFactory from 'react-bootstrap-table2-paginator';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';

import HNetworkNav from './HNetworkNav';

import "./RichDelegates.css";

import SPCalc from '../util/SPCalc';
import ApiUtils from '../util/ApiUtils';
import Utilities from "../util/Utilities";
import UIUtils from "../util/UIUtils";
import SPUtilities from "../util/SPUtilities";
import HUtils from "../harmony/HUtils";

class RichDelegates extends React.Component {
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

    let allData = await ApiUtils.get("listData?type=richDelegates");
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
        {text: "Overall Rank",dataField: "rank", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(14)},
        {text: "Address",dataField: "address", formatter: HUtils.addressFormatterByLabel, sort: true, headerStyle: Utilities.width(24)},
        {text: "Validators",dataField: "validators", formatter: SPUtilities.csvFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(42)},
        {text: "Total Stake",dataField: "totalStake", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
      ];
    } else if (window.innerWidth < 1000) {
      columns = [
        {text: "Overall Rank",dataField: "rank", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "Address",dataField: "address", formatter: HUtils.addressFormatterByLabel, sort: true, headerStyle: Utilities.width(20)},
        {text: "Validators",dataField: "validators", formatter: SPUtilities.csvFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(35)},
        {text: "Total Stake",dataField: "totalStake", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "USD Value",dataField: "totalStake", formatter: SPCalc.calcTotalUSD, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(14)},
        {text: "BTC Value",dataField: "totalStake", formatter: SPCalc.calcTotalBTC, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(13)},
      ];
    } else {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(4)},
        {text: "Overall Rank",dataField: "rank", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(5)},
        {text: "",dataField: "address", formatter: HUtils.addressFormatterByLabelShort, filter: textFilter({placeholder: "Address"}), sort: true, headerStyle: Utilities.width(15)},
        {text: "Validators Staked With",dataField: "validators", formatter: SPUtilities.csvFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(40)},
        {text: "Total Stake",dataField: "totalStake", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "USD Value",dataField: "totalStake", formatter: SPCalc.calcTotalUSD, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(9)},
        {text: "BTC Value",dataField: "totalStake", formatter: SPCalc.calcTotalBTC, formatExtraData: this, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(9)},
      ];
    }

    const options = UIUtils.getPageOptions(this);

    // const expandRow = {
    //   onlyOneExpanding: true,
    //   renderer: row => (
    //     <div>
    //       <DelegateDetails address={row.address} />
    //       <hr/>
    //     </div>
    //   ), showExpandColumn: true
    // };
    // expandRow={ expandRow }

    return (
      <div>
        <p/>
        <h4 style={{align: "center"}}><span><strong>Harmony - Rich Delegates</strong></span>
          <span className="buttonWithText"><img src="/images/reload.svg" onClick={this.reload} title="Reload Screen"
            className="imgicon" width="32" height="32" /></span>
        </h4>
        <p/>
        <BootstrapTable keyField='address' data={ this.state.data }  filter={ filterFactory() }
          columns={ columns } striped expandableRow={ () => { return true; } } options={options}
          hover condensed noDataIndication="Loading" pagination={ paginationFactory(options) }/>
        <HNetworkNav />
      </div>
    );
  }

  reload() {
    window.location = "/richdel";
  }

}

export default RichDelegates;
