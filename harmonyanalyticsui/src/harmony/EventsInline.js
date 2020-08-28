import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import filterFactory, { selectFilter } from 'react-bootstrap-table2-filter';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import paginationFactory from 'react-bootstrap-table2-paginator';
import Table from 'react-bootstrap/Table';

import SPCalc from "../util/SPCalc";
import SPUtilities from "../util/SPUtilities";
import Utilities from "../util/Utilities";
import RespUtils from "../util/RespUtils";
import AddressUtils from "../util/AddressUtils";
import UIUtils from "../util/UIUtils";
import HUtils from "./HUtils";

class EventsInline extends React.Component {
  constructor(props) {
    super(props);
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

  render() {

    var columns;
    if (RespUtils.isMobileView()) {
      columns = [
        {text: "Time Passed",dataField: "elapsedTime", formatter: SPCalc.formatElapsedTime, sort: true, headerStyle: Utilities.width(23)},
        {text: "Event Type",dataField: "eventType", formatter: HUtils.formatEventType, sort: true, headerStyle: Utilities.width(26)},
        {text: "Address", dataField: "address", formatter: SPUtilities.addressReallyShortFormatterVisibleLink, sort: true, headerStyle: Utilities.width(23)},
        {text: "Value", dataField: "amount", sort: true, formatter: HUtils.convert2DigitsDecimal, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(28)},
      ];
    } else if (RespUtils.isTabletView()) {
      columns = [
        {text: "Time Passed",dataField: "elapsedTime", formatter: SPCalc.formatElapsedTime, sort: true, headerStyle: Utilities.width(17)},
        {text: "Event Type",dataField: "eventType", sort: true, headerStyle: Utilities.width(22)},
        {text: "Address", dataField: "address", formatter: SPUtilities.addressShortFormatter, sort: true, headerStyle: Utilities.width(20)},
        {text: "Value", dataField: "amount", sort: true, formatter: HUtils.convert2DigitsDecimal, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
      ];
    } else {
      columns = [
        {text: "Time Passed",dataField: "elapsedTime", formatter: SPCalc.formatElapsedTime, sort: true, headerStyle: Utilities.width(10)},
        {text: "Event Type",dataField: "eventType", sort: true, headerStyle: Utilities.width(10)},
        {text: "Block Number",dataField: "blockNumber", sort: true, headerStyle: Utilities.width(10)},
        {text: "Timestamp",dataField: "epochBlockTime", formatter: SPUtilities.epochFormatter, sort: true, headerStyle: Utilities.width(20)},
        {text: "Address", dataField: "address", formatter: SPUtilities.addressShortFormatter, sort: true, headerStyle: Utilities.width(15)},
        {text: "Value", dataField: "amount", sort: true, formatter: HUtils.convert2DigitsDecimal, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(10)},
      ];
    }

    if(RespUtils.isNotMobileView() && this.props.showValName === true) {
      columns.splice(3, 0, {text: "Validator", dataField: "name", formatter: HUtils.nameFormatterShort, sort: true, headerStyle: Utilities.width(25),});
    }

    const options = UIUtils.getPageOptionsSmall(this, 10);

    const expandRow = {
      onlyOneExpanding: true,
      renderer: row => this.showRowDetails(row), showExpandColumn: true
    };

    return (
      <div style={{"overflow-x": "hidden"}}>
        <p>Latest {this.props.data.length} events.</p>
        <BootstrapTable keyField='eventId' data={ this.props.data }
          columns={ columns } striped filter={ filterFactory() }
          expandRow={ expandRow } expandableRow={ () => { return true; } }
          options={options}
          hover condensed noDataIndication="Table is Empty/Loading"
          pagination={paginationFactory(options)} />
      </div>
    );
  }

  showRowDetails(row) {
    return (<div>
      <Table striped bordered size="sm">
        <tbody>
          <tr>
            <th align="left">Time Passed: </th>
            <td align="left"> {SPCalc.formatElapsedTime(row.elapsedTime, row)}</td>
          </tr>
          <tr>
            <th align="left">Event Type: </th>
            <td align="left"> {row.eventType}</td>
          </tr>
          <tr>
            <th align="left">Block Number: </th>
            <td align="left"> {row.blockNumber}</td>
          </tr>
          <tr>
            <th align="left">Timestamp: </th>
            <td align="left"> {SPUtilities.epochFormatter(row.epochBlockTime, row)}</td>
          </tr>
          <tr>
            <th align="left">Address: </th>
            <td align="left"> {AddressUtils.addressFormatterSimple(row.address)}</td>
          </tr>
          <tr>
            <th align="left">Validator: </th>
            <td align="left"> {row.name}</td>
          </tr>
          <tr>
            <th align="left">Other Address: </th>
            <td align="left"> {row.otherAddress}</td>
          </tr>
          <tr>
            <th align="left">Amount: </th>
            <td align="left"> {row.amount}</td>
          </tr>
        </tbody>
      </Table>
      <hr/>
    </div>);
  }

}

export default EventsInline;
