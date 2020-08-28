import React from 'react';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import BootstrapTable from 'react-bootstrap-table-next';
import Breadcrumb from 'react-bootstrap/Breadcrumb';

import BaseAreaChart from "../reports/BaseAreaChart";
import BaseBarChart from '../reports/BaseBarChart';

import HValNav from './HValNav';
import HValHeader from './HValHeader';
import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import Utilities from '../util/Utilities';
import UINotes from "../util/UINotes";
import ChartUtils from "../util/ChartUtils";
import HUtils from "./HUtils";
import UIUtils from "../util/UIUtils";

class ValStats extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      val: {},
      perfData: [],
      width: window.innerWidth,
      size: 10,
      responsive: true,
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

    var hPoolId = HUtils.getHPoolId(this);
    // console.log("hPoolId is:", hPoolId);
    let url = "listData?type=valPerf&hPoolId=" + hPoolId;

    const allData = await ApiUtils.get(url);
    // console.log("allData is:", allData);

    if (allData) {
      let val = allData["val"];
      this.setState({"val": val,
        "perfData": allData["perfData"],
        isLoading: false});
    }
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    if (this.state.val.hPoolId === undefined) {
      return <div>Still loading</div>;
    }

    var columns = [
      {text: "Epoch",dataField: "title", sort: true, headerStyle: Utilities.width(25)},
      {text: "ER", dataField: "er", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
      {text: "Net ER", dataField: "netEr", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
      {text: "ERI", dataField: "eri", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
    ];

    var otherStatsColumns;
    if (window.innerWidth < 600) {
      otherStatsColumns = [
        {text: "Epoch",dataField: "title", sort: true, headerStyle: Utilities.width(15)},
        {text: "Keys", dataField: "blsKeyCount", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Delegates", dataField: "uniqueDelegates", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
        {text: "Stake (millions)", dataField: "totalStaked", formatter: SPUtilities.stakeFormatterRounded, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(25)},
        {text: "Elected", dataField: "elected", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
      ];
    } else {
      otherStatsColumns = [
        {text: "Epoch",dataField: "title", sort: true, headerStyle: Utilities.width(15)},
        {text: "BLS Keys", dataField: "blsKeyCount", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Delegates", dataField: "uniqueDelegates", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "Self Stake", dataField: "selfStake", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Stake", dataField: "totalStaked", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Bid", dataField: "bidPerSeat", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Fee", dataField: "fee", formatter: HUtils.convertPercentFormatter, sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
        {text: "Elected", dataField: "elected", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
      ];
    }

    const options = UIUtils.getPageOptionsSmall(this, 10);

    const defaultSorted = [{
      dataField: 'title', // if dataField is not match to any column you defined, it will be ignored.
      order: 'desc' // desc or asc
    }];

    return (
      <div>
        <p/>
        <HValHeader val={this.state.val} notification={this.state.notification} title="Validator Stats"/>

        <hr/>
        {ChartUtils.render2Lines(this, "Expected Returns Index (ERI) by Epoch", this.state.perfData,
          "Epoch", "Expected Returns", "eri", "average", "eri")}
        <hr/>
        {ChartUtils.render2Lines(this, "Expected Returns (ER) by Epoch", this.state.perfData,
          "Epoch", "Expected Returns", "er", "netEr", "er")}

        <hr/>
        <BaseAreaChart title="Stake History" xAxis="Epoch" yAxis="Total Staked (millions)"
          showVerticalLabel={false} valueAttr="totalStakeInMillions"
          data={this.state.perfData} />

        <hr/>
        <p><b>Delegate Count History</b></p>
        <BaseBarChart xAxis="Epoch" yAxis="# of Delegates"
          showVerticalLabel={true} valueAttr="uniqueDelegates" showTotalLabel={false}
          data={this.state.perfData} xAxisValueAttr="title" />
        <hr/>

        <p/><p><b>Epoch Performance Summary</b></p>
        <BootstrapTable keyField='epoch' data={ this.state.perfData }
          columns={ columns } striped options={options} defaultSorted={defaultSorted}
          condensed noDataIndication="Table is Empty/Loading"
          />

        <hr/>
        <p/><p><b>Other Stats</b></p>
        <BootstrapTable keyField='epoch' data={ this.state.perfData }
          columns={ otherStatsColumns } striped options={options} defaultSorted={defaultSorted}
          condensed noDataIndication="Table is Empty/Loading"
          />

        <HValNav hPoolId={this.state.val.hPoolId}/>
      </div>
    );
  }

  getBreadCrumb() {
    if (window.innerWidth < 1000) {
      return (
        <Breadcrumb>
          <Breadcrumb.Item href="/">Validators</Breadcrumb.Item>
        </Breadcrumb>
      );
    } else {
      return "";
    }
  }

  // reload() {
  //   window.location = "/val/" + this.state.val.hPoolId;
  // }

}

export default ValStats;
