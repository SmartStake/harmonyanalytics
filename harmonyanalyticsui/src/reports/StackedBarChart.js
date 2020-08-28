import React from "react";
import {ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Label, Legend, LabelList } from 'recharts';
import {BarChart, Bar } from 'recharts';
import paginationFactory from 'react-bootstrap-table2-paginator';
import BootstrapTable from 'react-bootstrap-table-next';

import UIUtils from '../util/UIUtils';
import Utilities from '../util/Utilities';
import SPUtilities from '../util/SPUtilities';
import ChartUtils from '../util/ChartUtils';

class StackedBarChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      responsive: true,
    }

    this.flipResponsive = this.flipResponsive.bind(this);
    this.truncDate = this.truncDate.bind(this);
  }

  flipResponsive() {
    ChartUtils.flipResponsive(this);
  }

  renderBar() {
    // console.log("in render chart: " + (this.props.filter == true));
    // console.log(this.props);

    let width = UIUtils.getResponsiveWidth(this);
    // <Label value={this.props.xAxis} offset={-8} position="insideBottom"/>
    let height = UIUtils.getChartHeight(this);
    let showDataLabel = UIUtils.getShowDataLabel(this, this.props.data, 1000);

    // console.log("height is: " + height);
     // domain={['auto', 'auto']}7773ba
    return (
      <div>
        <ResponsiveContainer width={width} height={height}>
          <BarChart data={this.props.data} barCategoryGap={2}
                margin={{top: 5, right: 5, left: 15, bottom: 15}}>
            <CartesianGrid strokeDasharray="3 3"/>
            <XAxis dataKey="title" angle={-10}>
              <Label value={this.props.xAxis} offset={-3} position="insideBottom" />
            </XAxis>
            <YAxis domain={Utilities.getAddedRange(true, this.props.data, this.props.valueAttr, this.props.valueAttr2)}>
              <Label value={this.props.yAxis} offset={8} position="insideBottomLeft" angle={-90} />
            </YAxis>
            <Tooltip/>
            <Legend />
            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
            {showDataLabel && <Bar maxBarSize={50} dataKey={this.props.valueAttr} stackId="a" fill="#8884d8">
                <LabelList dataKey={this.props.valueAttr} position="center" />
              </Bar>}
            {!showDataLabel && <Bar maxBarSize={50} dataKey={this.props.valueAttr} stackId="a" fill="#8884d8" /> }

            {showDataLabel && <Bar maxBarSize={50} dataKey={this.props.valueAttr2} stackId="a" fill="#82ca9d">
                <LabelList dataKey={this.props.valueAttr2} position="top" />
              </Bar>}
            {!showDataLabel && <Bar maxBarSize={50} dataKey={this.props.valueAttr2} stackId="a" fill="#82ca9d" /> }
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  render () {
  	return (
      <div>
        <b><span align="left">{this.props.title}</span></b>
        <p>Data for the latest window (hour or date) is partial. All times are in GMT.</p>
        <p/>
        <div align="center">
          {this.props.showTotalLabel ? Utilities.getTotalWithLabel(this.props.data, this.props.valueAttr, this.props.totalLabel) : ""}.
          {this.renderBar()}
        </div>
        {ChartUtils.getLandscapeMsg()}
      </div>
    );
  }

  truncDate(val) {
    return ChartUtils.truncDate(val, this.props.chartType, this.props.filter)
  }

}

export default StackedBarChart;
