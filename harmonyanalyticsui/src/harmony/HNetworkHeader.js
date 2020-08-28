import React from 'react';
import Table from 'react-bootstrap/Table';

import SPUtilities from '../util/SPUtilities';
import SPCalc from '../util/SPCalc';
import HUtils from './HUtils';

class HNetworkHeader extends React.Component {
  render() {
    let totalStakedLabel = "Total Staked";
    let percentStakedLabel = "Percent Staked";
    let circulatingSupplyLabel = "Circulating Supply";
    let medianStakeLabel = "Median Raw Stake";
    let totalSupplyLabel = "Total Supply";
    let uniqueDelegatesLabel = "Unique Delegates";
    let latestBlockLabel = "Synced Till";
    if (window.innerWidth < 600) {
      totalStakedLabel = "Staked";
      percentStakedLabel = "% Staked";
      circulatingSupplyLabel = "Circulation";
      medianStakeLabel = "M. Stake";
      totalSupplyLabel = "Total";
      uniqueDelegatesLabel = "Delegates";
      latestBlockLabel = "Synced Till";
    }

    return (
      <Table bordered hover variant="dark" size="sm" >
        <tbody>
          <tr>
            <td>{totalStakedLabel}</td>
            <th>{HUtils.formatBigCoinCount(this.props.coinStat.totalStake)}</th>
            <td>{percentStakedLabel}</td>
            <th>{this.props.coinStat.percentStaked}%</th>
          </tr>
          <tr>
            <td>{circulatingSupplyLabel}</td>
            <th>{HUtils.formatBigCoinCount(this.props.coinStat.circulatingSupply)}</th>
            <td>{medianStakeLabel}</td>
            <th alt="Median Raw Stake">{SPCalc.formatCoinCount(this.props.coinStat.medianRawStake)}</th>
          </tr>
          <tr>
            <td>{totalSupplyLabel}</td>
            <th>{HUtils.formatBigCoinCount(this.props.coinStat.totalSupply)}</th>
            <td>{uniqueDelegatesLabel}</td>
            <th>{this.props.coinStat.uniqueDelegates}</th>
          </tr>
          <tr>
            <td>{latestBlockLabel}</td>
            <th>{this.props.coinStat.recentBlock} </th>
            <td>Next Epoch</td>
            <th>{SPUtilities.epochFormatter(this.props.coinStat.nextEpochTime)} / {this.props.coinStat.epochLastBlock}</th>
          </tr>
        </tbody>
      </Table>
    );
  }
}

export default HNetworkHeader;
