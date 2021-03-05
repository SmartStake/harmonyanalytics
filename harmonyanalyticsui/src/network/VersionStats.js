import React from 'react';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import BootstrapTable from 'react-bootstrap-table-next';
import Breadcrumb from 'react-bootstrap/Breadcrumb';
import {ResponsiveContainer, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Label } from 'recharts';
import {Container, Row, Col} from 'react-bootstrap';
import BaseBarChart from '../reports/BaseBarChart';
import StackedBarChart from "../reports/StackedBarChart";

import BaseAreaChart from "../reports/BaseAreaChart";
import HNetworkNav from './HNetworkNav';
import NetworkHeader from './NetworkHeader';

import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import Utilities from '../util/Utilities';
import UINotes from "../util/UINotes";
import ChartUtils from "../util/ChartUtils";
import HUtils from "../harmony/HUtils";
import UIUtils from "../util/UIUtils";
import tooltips from "../tooltips";

class VersionStats extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      nodeVersions: {},
      nodeVersionSummary: {},
      width: window.innerWidth,
      size: 10,
      responsive: true,
      isLoading: true,
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

    let url = "listData?type=versionStats";

    const allData = await ApiUtils.get(url);
    console.log("allData is:", allData);

    if (allData) {
      this.setState({"nodeVersionSummary": allData["nodeVersionSummary"],
        "nodeVersions": allData["nodeVersions"], isLoading: false});
    }
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    let width = UIUtils.getResponsiveWidth(this);
    let height = UIUtils.getChartHeight(this);
    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    return (
      <div>
        <NetworkHeader title="Node Versions" />
        <hr/>
        <Container fluid>
          <Row>
            <Col md className="chartBg">
              <ResponsiveContainer width={width} height={height}>
                <PieChart height={250}>
                  <Pie data={this.state.nodeVersionSummary} cx="50%" cy="50%" outerRadius={100}
                    fill="#8884d8" dataKey="total" label={({cx, cy, midAngle, innerRadius, outerRadius, value, index}) => {
                      const RADIAN = Math.PI / 180;
                      const radius = 25 + innerRadius + (outerRadius - innerRadius);
                      const x = cx + radius * Math.cos(-midAngle * RADIAN);
                      const y = cy + radius * Math.sin(-midAngle * RADIAN);
                      let summary = this.state.nodeVersionSummary;
                      // console.log(summary);
                      // console.log(index);
                      // console.log(summary[index]);

                      return (
                        <text x={x} y={y} fill="#8884d8" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" >
                          {summary[index].nodeVersion} ({value})
                        </text>
                      );
                    }}
                  >
                    {
        						  this.state.nodeVersionSummary.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)
          					}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </Col>
          </Row>
        </Container>
        <HNetworkNav />
      </div>
    );
  }

  // getPieLabel(cx, cy, midAngle, innerRadius, outerRadius, value, index) {
  //   console.log("handling label?");
  //   const RADIAN = Math.PI / 180;
  //   const radius = 25 + innerRadius + (outerRadius - innerRadius);
  //   const x = cx + radius * Math.cos(-midAngle * RADIAN);
  //   const y = cy + radius * Math.sin(-midAngle * RADIAN);
  //   let summary = this.state.nodeVersionSummary;
  //   console.log(summary);
  //   console.log(index);
  //   console.log(summary[index]);
  //
  //   return (
  //     <text x={x} y={y} fill="#8884d8" textAnchor={x > cx ? "start" : "end"} dominantBaseline="central" >
  //       {summary[index].nodeVersion} ({value})
  //     </text>
  //   );
  // }
}
// {this.state.versionSummary.data[index].nodeVersion} ({value})

export default VersionStats;
