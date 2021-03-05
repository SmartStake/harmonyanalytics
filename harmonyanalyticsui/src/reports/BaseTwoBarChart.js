import React from "react";
import {ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Label } from 'recharts';
import {BarChart, Bar } from 'recharts';
import paginationFactory from 'react-bootstrap-table2-paginator';
import BootstrapTable from 'react-bootstrap-table-next';

import UIUtils from '../util/UIUtils';
import Utilities from '../util/Utilities';
import SPUtilities from '../util/SPUtilities';
import ChartUtils from '../util/ChartUtils';

class BaseTwoBarChart extends React.Component {
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
    let showDataLabel = UIUtils.getShowDataLabel(this, this.props.data, 600);

    // console.log("height is: " + height);
     // domain={['auto', 'auto']}7773ba
    return (
      <div>
        <ResponsiveContainer width={width} height={height}>
          <BarChart data={this.props.data} barCategoryGap={2}
                margin={{top: 5, right: 5, left: 15, bottom: 15}}>
            <CartesianGrid vertical={false} horizontal={false} strokeDasharray="3 3"/>
            <XAxis dataKey={this.props.xAxisValueAttr} angle={-10}>
              <Label value={this.props.xAxis} offset={-3} position="insideBottom" />
            </XAxis>
            <YAxis domain={Utilities.getRange(true, this.props.data, this.props.valueAttr)}>
              <Label value={this.props.yAxis} offset={8} position="insideBottomLeft" angle={-90} />
            </YAxis>
            <Tooltip/>
            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
            <Bar maxBarSize={50} dataKey={this.props.value1Attr} label={{ angle: -90, position: 'center' }}/> }
            <Bar maxBarSize={50} dataKey={this.props.value2Attr} label={{ angle: -90, position: 'center' }}/> }
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  render () {
  	return (
      <div>
        <b><span align="left">{this.props.title}</span></b>
        <p/>
        <div align="center">
          {this.props.showTotalLabel ? Utilities.getTotalWithLabel(this.props.data, this.props.valueAttr, this.props.totalLabel) : ""}.
          {this.renderBar()}
        </div>
        {ChartUtils.getLandscapeMsg()}
      </div>
    );
  }
  // <p>Data for the latest window (hour or date) is partial. All times are in GMT.</p>

  truncDate(val) {
    return ChartUtils.truncDate(val, this.props.chartType, this.props.filter)
  }

}

export default BaseTwoBarChart;
