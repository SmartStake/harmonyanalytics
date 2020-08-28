import React from 'react';
import {ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Label, Legend } from 'recharts';

import SPCalc from './SPCalc';
import config from '../config';

import Utilities from './Utilities';
import UIUtils from './UIUtils';
import RespUtils from './RespUtils';

class ChartUtils extends React.Component {

  static flipResponsive(thisObj) {
    if(thisObj.state.responsive) {
      // console.log("setting chart to not responsive")
      thisObj.setState({responsive: false});
    } else {
      // console.log("setting chart to responsive")
      thisObj.setState({responsive: true});
    }
  }

  static getLandscapeMsg() {
    let specialMessage = RespUtils.getSpecialMessage();
  }

  static truncDate(val, chartType, filter) {
    if (chartType == "hour" && filter != null) {
      return val.substring(11, 13) + ":00";
    }

    if (filter == null && val.length > 10) {
      return val.substring(0, 10);
    }

    return val;
  }

  static renderLines(thisObj, title, data, yAxisLabel, valueAttr1, valueAttr2, valueAttr3, rangeAttr) {
    let width = UIUtils.getResponsiveWidth(thisObj);
    let margin = UIUtils.getChartMargin(thisObj);

    return (
      <div>
        <p><b>{title}</b></p>
        <ResponsiveContainer width={width} height={250}>
          <LineChart data={data} margin={margin}>
            <XAxis dataKey="title" angle={-10}>
              <Label value="Date" offset={-3} position="insideBottom" />
            </XAxis>
            <YAxis domain={Utilities.getRange(true, data, rangeAttr)}>
              <Label value={yAxisLabel} offset={8} position="insideBottomLeft" angle={-90} />
            </YAxis>
            <Tooltip/>
            <Legend />
            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
            <Line type="monotone" dataKey={valueAttr1} connectNulls={true}
              label={false} dot={false} stroke="red" />
            <Line type="monotone" dataKey={valueAttr2} connectNulls={true}
              label={false} dot={false} stroke="green" />
            <Line type="monotone" dataKey={valueAttr3} connectNulls={true}
              label={false} dot={false} stroke="blue" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  static render2Lines(thisObj, title, data, xAxisLabel, yAxisLabel, valueAttr1, valueAttr2, rangeAttr) {
    let width = UIUtils.getResponsiveWidth(thisObj);
    let margin = UIUtils.getChartMargin(thisObj);

    return (
      <div>
        <p><b>{title}</b></p>
        <ResponsiveContainer width={width} height={250}>
          <LineChart data={data} margin={margin}>
            <XAxis dataKey="title" angle={-10}>
              <Label value={xAxisLabel} offset={-3} position="insideBottom" />
            </XAxis>
            <YAxis domain={Utilities.getRange(true, data, rangeAttr)}>
              <Label value={yAxisLabel} offset={8} position="insideBottomLeft" angle={-90} />
            </YAxis>
            <Tooltip/>
            <Legend />
            <CartesianGrid stroke="#eee" strokeDasharray="5 5"/>
            <Line type="monotone" dataKey={valueAttr1} connectNulls={true}
              label={false} dot={false} stroke="red" />
            <Line type="monotone" dataKey={valueAttr2} connectNulls={true}
              label={false} dot={false} stroke="green" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

}

export default ChartUtils;
