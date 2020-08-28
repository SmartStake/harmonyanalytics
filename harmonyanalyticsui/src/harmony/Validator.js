import React from 'react';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import BootstrapTable from 'react-bootstrap-table-next';
import Breadcrumb from 'react-bootstrap/Breadcrumb';

import BaseBarChart from "../reports/BaseBarChart";
import StackedBarChart from "../reports/StackedBarChart";
import HValInline from './HValInline';
import HValNav from './HValNav';
import HValHeader from './HValHeader';
import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import Utilities from '../util/Utilities';
import UINotes from "../util/UINotes";
import ChartUtils from "../util/ChartUtils";
import HUtils from "./HUtils";
import UIUtils from "../util/UIUtils";
import EventsInline from "./EventsInline";

class Validator extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      val: {},
      coinStat: {},
      hourlyChartData: [],
      dailyChartData: [],
      notification: {},
      events: [],
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
    let url = "listData?type=getPool&hPoolId=" + hPoolId;
    // const nodeData = await ApiUtils.get("listValidators?sortBy=stake");
    if (this.props.match && this.props.match.params.showMore) {
      url += "&showMore=" + this.props.match.params.showMore;
    }
    // console.log("showMore:", this.props.match.params.showMore);
    // console.log("url:", url);

    const allData = await ApiUtils.get(url);
    // console.log("allData is:", allData);

    if (allData) {
      let val = allData["val"];
      let coinStat = allData["coinStat"];
      this.setState({"val": val,
        "hourlyChartData": allData["hourlyChartData"],
        "dailyChartData": allData["dailyChartData"],
        "notification": allData["notification"],
        "coinStat": coinStat, "events": allData["events"],
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

    var columns;
    var dateColumns = [{text: "Date",dataField: "title", sort: true, headerStyle: Utilities.width(35)}];
    var epochColumns = [{text: "Epoch",dataField: "title", sort: true, headerStyle: Utilities.width(15)}];
    if (window.innerWidth < 600) {
      columns = [
        // {text: "Date",dataField: "title", sort: true, headerStyle: Utilities.width(34)},
        {text: "Signed", dataField: "signed", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "Missed", dataField: "notSigned", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
        {text: "Sign %", dataField: "signPer", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
      ];
    } else {
      columns = [
        // {text: "Date",dataField: "title", sort: true, headerStyle: Utilities.width(25)},
        {text: "Asked To Sign", dataField: "askedToSign", sort: true,  sortFunc: Utilities.sortNumeric,  headerStyle: Utilities.width(15)},
        {text: "Signed", dataField: "signed", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Missed", dataField: "notSigned", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Sign %", dataField: "signPer", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "Rewards", dataField: "rewards", sort: true,  sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
      ];
    }
    dateColumns = dateColumns.concat(columns);
    epochColumns = epochColumns.concat(columns);

    const options = UIUtils.getPageOptionsSmall(this, 10);

    const defaultSorted = [{
      dataField: 'title',
      order: 'desc' // desc or asc
    }];

    return (
      <div>
        <p/>
        <HValHeader val={this.state.val} notification={this.state.notification} title="Summary"/>
        <HValInline val={this.state.val} hideNav={true} coinStat={this.state.coinStat}/>

        <hr/>
        <BaseBarChart title="Hourly Signed Percentage (GMT)" xAxis="Date/Hour" yAxis="Sign Percentage"
          showVerticalLabel={true} valueAttr="signPer" showTotalLabel={false}
          data={this.state.hourlyChartData} />
        <hr/>
        <StackedBarChart title="Hourly Signatures" xAxis="Date/Hour" yAxis="Signatures"
          showVerticalLabel={true} valueAttr="signed" valueAttr2="notSigned" showTotalLabel={false}
          data={this.state.hourlyChartData} />
        <hr/>
        <StackedBarChart title="Epoch Signatures" xAxis="Epoch" yAxis="Signatures"
          showVerticalLabel={true} valueAttr="signed" valueAttr2="notSigned" showTotalLabel={false}
          data={this.state.dailyChartData} />

        <hr/>
        <p/><p><b>Hourly Performance Stats (GMT Time)</b> - {this.renderMore()}</p>
        <BootstrapTable keyField='hPoolPerfId' data={ this.state.hourlyChartData }
          columns={ dateColumns } striped options={options} defaultSorted={defaultSorted}
          condensed noDataIndication="Table is Empty/Loading"
          />
        <hr/>
        <p/><p><b>Epoch Performance Stats</b> - {this.renderMore()}</p>
        <BootstrapTable keyField='hPoolPerfId' data={ this.state.dailyChartData }
          columns={ epochColumns } striped options={options} defaultSorted={defaultSorted}
          condensed noDataIndication="Table is Empty/Loading"
          />
        <hr/>
        <p/>
        {this.state.events.length > 0 && this.renderEvents()}
        <HValNav hPoolId={this.state.val.hPoolId}/>
      </div>
    );
  }

  renderEvents() {
    return (
      <div>
        <p/>
        <p><b>Recent Events</b></p>
        {HUtils.renderEventTypes(this)}
        <EventsInline data={this.state.events} showValName={false} />
      </div>
    )
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

  renderMore() {
    // console.log(this.props.match.params.showMore)
    // console.log(this.props.match.params.showMore == 'true')
    if (this.props.match && this.props.match.params.showMore == 'true') {
      return (<a class="black-a" href={"/val/" + this.state.val.hPoolId + "/false"}>Show Less</a>);
    }

    return (<a class="black-a" href={"/val/" + this.state.val.hPoolId + "/true"}>Show More</a>);
  }
}

export default Validator;
