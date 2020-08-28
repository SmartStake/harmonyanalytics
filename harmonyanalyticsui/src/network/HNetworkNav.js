import React from 'react';
import Table from 'react-bootstrap/Table';

class HNetworkNav extends React.Component {
  render() {
    return (
      <div width="90%">
        <hr/>
        <Table striped bordered hover variant="dark" >
          <thead>
            <tr>
              <th><a className="white-a" href="/">Validators</a></th>
              <th><a className="white-a" href="/networkEvents">Events</a></th>
              <th><a className="white-a" href="/richlist">Richlist</a></th>
            </tr>
            <tr>
              <th><a className="white-a" href="/calc">Calculator</a></th>
              <th><a className="white-a" href="/stake">Network Stake</a></th>
              <th>&nbsp;</th>
            </tr>
          </thead>
        </Table>
      </div>
    );
  }
}
// <th><a className="white-a" href="/networkStake">Stake History</a></th>
// <th><a className="white-a" href="/topSigners">Top Signers</a></th>

export default HNetworkNav;
