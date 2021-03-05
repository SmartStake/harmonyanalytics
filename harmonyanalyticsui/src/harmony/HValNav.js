import React from 'react';
import Table from 'react-bootstrap/Table';

import config from '../config';
import NetworkUtils from '../util/NetworkUtils';

class HValNav extends React.Component {
  render() {
    let hPoolId = this.props.hPoolId;
    if (!hPoolId) {
      hPoolId = this.props.hPoolId;
    }

    return (
      <div width="90%">
        <hr/>
        <p><b>Performance tools</b></p>
        <Table striped bordered hover variant="dark">
          <thead>
            <tr>
              <th><a className="white-a" href={"/val/" + hPoolId}>Summary</a></th>
              <th><a className="white-a" href={"/valstats/" + hPoolId}>Stats History</a></th>
              <th><a className="white-a" href={"/delegates/" + hPoolId}>Delegates</a></th>
            </tr>
            <tr>
              <th><a className="white-a" href={"/events/" + hPoolId}>Events</a></th>
              <th><a className="white-a" href={"/keys/" + hPoolId}>BLS Key Performance</a></th>
            </tr>
            {this.renderSpecialTools(hPoolId)}
          </thead>
        </Table>
      </div>
    );
  }


  renderSpecialTools(hPoolId) {
    if (!NetworkUtils.isDefaultPool(hPoolId)) {
      return "";
    }

    return (
      <tr>
        <th><a className="white-a" href={"/health/" + hPoolId}>Health</a></th>
        <th>&nbsp;</th>
      </tr>
    );
  }
}

export default HValNav;
