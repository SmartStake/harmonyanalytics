import React from "react";
import {ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Label } from 'recharts';
import {AreaChart, Area} from 'recharts';
import {BarChart, Bar } from 'recharts';
import paginationFactory from 'react-bootstrap-table2-paginator';
import BootstrapTable from 'react-bootstrap-table-next';

import HValNav from '../harmony/HValNav';
import ApiUtils from '../util/ApiUtils';
import UIUtils from '../util/UIUtils';
import Utilities from '../util/Utilities';
import SPUtilities from '../util/SPUtilities';
import ChartUtils from '../util/ChartUtils';
import RespUtils from '../util/RespUtils';

class BaseLineChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      responsive: true,
      data: {},
      pool: {}
    }

    this.flipResponsive = this.flipResponsive.bind(this);
    this.truncDate = this.truncDate.bind(this);
  }

  getBaseUrl() {
    let url = "reportData";
    return url;
  }

  async loadData(url) {
    let allData = await ApiUtils.get(url);
    // console.log("BaseLineChart.js: allData: ", allData);

    this.setState({data: allData, isLoading: false});
  }

  async componentDidMount() {
    if (this.props.data) {
      this.setState({pool: this.props.pool, data: this.props.data,
        isLoading: false});
      return;
    }

    let url = this.getBaseUrl() + "?name=" + this.props.chartName
      + "&type=" + this.props.chartType

    // if (this.props.showRecent != null) {
    //   url += "&showRecent=" + this.props.showRecent
    // }
    if (this.props.filter != null) {
      url += "&filter=" + this.props.filter;
    }

    if (this.props.hPoolId == null) {
      this.loadData(url);
      return;
    }

    url += "&hPoolId=" + this.props.hPoolId;

    // console.log(url);
    let allData = await ApiUtils.get(url);
    // console.log("BaseLineChart.js: allData: ", allData);

    let poolData = allData["pool"];
    this.setState({pool: poolData});
    let data = allData["data"];
    // console.log("BaseLineChart.js: data: ", data);

    // if (typeof this.props.showRecent != 'undefined' && this.props.showRecent) {
    //   let recentBlocks = allData["recentBlocks"];
    //   // console.log("BaseLineChart.js: recentBlocks: ", recentBlocks);
    //   this.setState({recentBlocks: recentBlocks});
    // }
    this.setState({data: data, isLoading: false});
    // console.log("BaseLineChart.js: pool: ", poolData);

/*    if (this.props.filter != null) {
        if (data) {
          data = data.slice(data.length - this.props.filter, data.length);
        }
    }*/
  }

  flipResponsive() {
    ChartUtils.flipResponsive(this);
  }

  renderLine() {
    // console.log("in render chart: " + (this.props.filter == true));
    // console.log(this.props);

    let width = RespUtils.getResponsiveWidth(this);
    let margin = UIUtils.getChartMargin(this);
    // <Label value={this.props.xAxis} offset={-8} position="insideBottom"/>
     // domain={['auto', 'auto']}
    return (
      <div>
        <ResponsiveContainer width={width} height={250}>
          <LineChart data={this.state.data}
                margin={margin}>
            <XAxis dataKey="title" angle={-10} tickFormatter={this.truncDate}>
            </XAxis>
            <YAxis domain={Utilities.getRange(true, this.state.data, "value")}>
              <Label value={this.props.yAxis} offset={8} position="insideBottomLeft" angle={-90} />
            </YAxis>
            <Tooltip/>
            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
            <Line type="monotone" dataKey="value" connectNulls={true}
              label={this.props.label ? true : false}
              dot={this.props.dot ? true: (this.props.filter ? true : false)} stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  renderBar() {
    // console.log("in render chart: " + (this.props.filter == true));
    // console.log(this.props);

    let width = RespUtils.getResponsiveWidth(this);
    // <Label value={this.props.xAxis} offset={-8} position="insideBottom"/>
    let height = RespUtils.getChartHeight(this);
    let showDataLabel = UIUtils.getShowDataLabel(this, this.state.data);

    // console.log("height is: " + height);
     // domain={['auto', 'auto']}7773ba
    return (
      <div>
        <ResponsiveContainer width={width} height={height}>
          <BarChart data={this.state.data} barCategoryGap={2}
                margin={{top: 5, right: 5, left: 15, bottom: 15}}>
            <CartesianGrid strokeDasharray="3 3"/>
            <XAxis dataKey="title" angle={-10}>
              <Label value={this.props.xAxis} offset={-3} position="insideBottom" />
            </XAxis>
            <YAxis domain={Utilities.getRange(true, this.state.data, "value")}>
              <Label value={this.props.yAxis} offset={8} position="insideBottomLeft" angle={-90} />
            </YAxis>
            <Tooltip/>
            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
            {showDataLabel && <Bar maxBarSize={50} dataKey="value" fill="#8884d8" onClick={this.barOnClick} label={{ angle: -90, position: 'center' }}/> }
            {!showDataLabel && <Bar maxBarSize={50} dataKey="value" fill="#8884d8" onClick={this.barOnClick} /> }
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  renderAreaChart() {
    // console.log("in render chart: " + (this.props.filter == true));
    // console.log(this.props);

    let width = RespUtils.getResponsiveWidth(this);
    // <Label value={this.props.xAxis} offset={-8} position="insideBottom"/>
    let height = RespUtils.getChartHeight(this);
    let showDataLabel = UIUtils.getShowDataLabel(this, this.state.data);


    // console.log("height is: " + height);
     // domain={['auto', 'auto']}7773ba
    return (
      <div>
        <ResponsiveContainer width={width} height={height}>
          <AreaChart data={this.state.data} barCategoryGap={2}
                margin={{top: 5, right: 5, left: 15, bottom: 15}}>
            <CartesianGrid strokeDasharray="3 3"/>
            <XAxis dataKey="title" angle={-10}>
              <Label value={this.props.xAxis} offset={-3} position="insideBottom" />
            </XAxis>
            <YAxis domain={Utilities.getRange(true, this.state.data, "value")}>
              <Label value={this.props.yAxis} offset={8} position="insideBottomLeft" angle={-90} />
            </YAxis>
            <Tooltip/>
            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
            {showDataLabel && <Area dataKey="value" fill="#8884d8" label={{ angle: -90, position: 'center' }}/> }
            {!showDataLabel && <Area dataKey="value" fill="#8884d8" /> }
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // {!this.state.isLoading && this.renderTable()}
  renderTable() {
    if (!this.props.showRecent || this.state.recentBlocks == undefined) {
      return "";
    }

    const defaultSorted = [{
      dataField: 'blockNumber',
      order: 'desc'
    }];

    const options = UIUtils.getPageOptionsSmall(this);
    const columns = [
      {text: "Timestamp", dataField: "blockTimestamp", sort: true},
      {text: "Block Number", dataField: "blockNumber", sort: true, sortFunc: Utilities.sortNumeric}
    ];

    return (
      <div>
        <h3>Recent Blocks</h3>
        <BootstrapTable keyField='blockNumber' data={ this.state.recentBlocks }
          columns={ columns } striped defaultSorted={ defaultSorted }
          hover condensed pagination={ paginationFactory(options) }
          noDataIndication="No data available"/>
      </div>
    );
  }

  render () {
    if (this.state.isLoading) {
      return "Loading";
    }

  	return (
      <div align="center">
        {this.renderTitle()}
        <p>Data for today's date may be partial. All times are in GMT.</p>
        <p/>
        {!this.props.hideSummary && Utilities.getTotalWithLabel(this.state.data, "value", "Total Blocks")}.
        {!this.props.hideSummary && !this.state.isLoading && !this.props.isBarChart && this.renderLastBlock()}
        {!this.props.isBarChart && !this.props.isAreaChart && this.renderLine()}
        {this.props.isBarChart && this.renderBar()}
        {this.props.isAreaChart && this.renderAreaChart()}
        {ChartUtils.getLandscapeMsg()}
        {!this.props.hideNav && this.props.hPoolId != null && this.renderPoolNav()}
      </div>
    );
  }

  renderTitle() {
    // if (this.props.hideNav) {
    //   if (this.props.hPoolId != null) {
    //     return (<p><b><u>{this.state.pool.poolName} - {this.props.title}</u></b></p>);
    //   } else {
    //     return (<p><b><u>{this.props.title}</u></b></p>);
    //   }
    // } else {
      if (this.props.hPoolId != null) {
        return (<h4 style={{align: "center"}}>{this.state.pool.poolName} - {this.props.title}</h4>);
      } else {
        return (<h4 style={{align: "center"}}>{this.props.title}</h4>);
      }
    // }
  }

  renderLastBlock() {
    return (
      <span> Synced till block # {this.state.pool.valSyncTillBlock}.</span>
    );
  }

  renderPoolNav() {
    return (<HValNav hPoolId={this.state.pool.hPoolId} />);
  }

  truncDate(val) {
    return ChartUtils.truncDate(val, this.props.chartType, this.props.filter)
  }

}

export default BaseLineChart;
