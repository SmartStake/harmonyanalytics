import React from "react";
import {ResponsiveContainer, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Label } from 'recharts';
import paginationFactory from 'react-bootstrap-table2-paginator';
import BootstrapTable from 'react-bootstrap-table-next';
import InfoIcon from '@material-ui/icons/Info';
import ReactTooltip from 'react-tooltip';

import UIUtils from '../util/UIUtils';
import Utilities from '../util/Utilities';
import SPUtilities from '../util/SPUtilities';
import ChartUtils from '../util/ChartUtils';

class BasePieChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      responsive: true,
    }

    this.flipResponsive = this.flipResponsive.bind(this);
  }

  flipResponsive() {
    ChartUtils.flipResponsive(this);
  }


  renderPieChart() {
    const CustomTooltip = ({ active, payload, label }) => {
      if (active) {
        if (payload === null || payload.length === 0) {
          return null;
        }
        let data = payload[0].payload;
        return this.props.customTooltip(data);
      }

      return null;
    };

    let width = UIUtils.getResponsiveWidth(this);
    let height = UIUtils.getChartHeight(this);
    const COLORS = ['#0088FE', '#FFBB28', '#00C49F', '#FF8042'];


    return (
      <div>
        <ResponsiveContainer width={width} height={height}>
          <PieChart margin={{top: 5, right: 5, left: 15, bottom: 15}}>
            <Pie data={this.props.data} cx="50%" cy="50%" outerRadius={100}
              fill="#8884d8" dataKey={this.props.countAttr} label={({cx, cy, midAngle, innerRadius, outerRadius, value, index}) => {
                const RADIAN = Math.PI / 180;
                const radius = 25 + innerRadius + (outerRadius - innerRadius);
                const x = cx + radius * Math.cos(-midAngle * RADIAN);
                const y = cy + radius * Math.sin(-midAngle * RADIAN);

                return (
                    <text x={x} y={y} fill="#8884d8" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" >
                      {Utilities.getFirstXChars(this.props.data[index][this.props.labelAttr], 10)} - {value}%
                    </text>
                );
              }}>
                {
                  this.props.data.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)
                }
            </Pie>
            {this.props.customTooltip != null ? <Tooltip content={<CustomTooltip />} /> : <Tooltip/>}
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  render () {
  	return (
      <div>
        <ReactTooltip id="main" place="top" type="dark" effect="float" multiline={true} />
        <b>
          <span align="left">{this.props.title}</span>
          <span className="buttonWithText"><span data-for="main" data-tip={this.props.desc} data-iscapture="true"><InfoIcon color="action"/></span></span>
        </b>
        <p/>
        <div align="center">
          {this.renderPieChart()}
        </div>
        {ChartUtils.getLandscapeMsg()}
      </div>
    );
  }
}

export default BasePieChart;
