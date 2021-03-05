import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import paginationFactory from 'react-bootstrap-table2-paginator';

import ApiUtils from '../util/ApiUtils';
import HValNav from './HValNav';

import HValHeader from './HValHeader';
import "./Delegates.css";
import Utilities from "../util/Utilities";
import UIUtils from "../util/UIUtils";
import HUtils from "./HUtils";
import SPUtilities from "../util/SPUtilities";

class Delegates extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      data: [],
      val: {},
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

    var hPoolId = HUtils.getHPoolId(this);
    const allData = await ApiUtils.get("listData?type=delegates&hPoolId=" + hPoolId);
    // console.log("allData is:", allData);

    if (allData) {
      let val = allData["val"];
      let data = Utilities.addIndex(allData["data"]);

      this.setState({val: val,
        data: data, isLoading: false});
    }

    this.setState({isLoading: false});
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    var columns;
    if (window.innerWidth < 600) {
      columns = [
        {text: "Overall Rank",dataField: "ranking", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Address",dataField: "address", formatter: HUtils.addressFormatterDel, sort: true, headerStyle: Utilities.width(41)},
        {text: "Stake",dataField: "stake", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(26)},
        {text: "Reward",dataField: "reward", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(18)}
      ];
    } else {
      columns = [
        {text: "#",dataField: "index", sort: true, headerStyle: Utilities.width(5)},
        {text: "Overall Rank",dataField: "ranking", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Address",dataField: "address", formatter: HUtils.addressFormatterDel, sort: true, headerStyle: Utilities.width(40)},
        {text: "Stake",dataField: "stake", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
        {text: "Reward",dataField: "reward", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)}
      ];
    }

    const options = UIUtils.getPageOptionsSmall(this, 50);

    return (
      <div>
        <HValHeader val={this.state.val} title="Delegates" callerRef={this}/>
        <p>Total delegates: {this.state.data.length}.</p>
        <p/>
        <BootstrapTable keyField='address' data={ this.state.data }
          columns={ columns } striped expandableRow={ () => { return true; } } options={options}
          hover condensed noDataIndication="Table is Empty/Loading" pagination={ paginationFactory(options) }/>
        <HValNav hPoolId={this.state.val.hPoolId}/>
      </div>
    );
  }

  static dateFormatter(value, row) {
      return SPUtilities.getDateTimeAsText(value);
  }

}

export default Delegates;
