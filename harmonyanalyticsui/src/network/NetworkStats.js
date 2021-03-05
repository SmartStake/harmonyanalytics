import React from 'react';
import {Link} from 'react-router-dom';

import Card from 'react-bootstrap/Card';
import CardDeck from 'react-bootstrap/CardDeck';
import constants from "../constants";

import NetworkHeader from './NetworkHeader';
import HNetworkNav from './HNetworkNav';
import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import UIUtils from '../util/UIUtils';
import SPCalc from '../util/SPCalc';
import HUtils from '../harmony/HUtils';

class NetworkStats extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      coinStat: {},
      pool: {},
      isLoading: true
    }
  }

  async componentDidMount() {
    const allData = await ApiUtils.get("listData?type=networkStats");
    // console.log("coinStat is:", coinStat);

    this.setState({coinStat: allData["coinStat"], shardData: allData["shardData"],
      isLoading: false});
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading Network Stats</div>;
    }

    var bgColor = "dark";
    var fontColor = "white";
    let lastUpdated = this.state.coinStat.lastUpdatedGap ? (this.state.coinStat.lastUpdatedGap/60).toFixed(0) : "N/A";

    return (
      <div>
        <NetworkHeader title="Network Stats" />
        <p>Latest Block - <b>{this.state.coinStat.recentBlock}</b></p>
        <hr/>

        <p><strong>Staking Stats</strong></p>
        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Percent Staked</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(this.state.coinStat.percentStaked + "%")}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Unique Delegates</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(this.state.coinStat.uniqueDelegates)}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Median Raw Stake</Card.Header>
            <Card.Body>
              <Card.Title>{HUtils.formatBigCoinCount(this.state.coinStat.medianRawStake)}</Card.Title>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/>
        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header># of Validators</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(this.state.coinStat.stakingPools)}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Total Staked Supply</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(HUtils.formatBigCoinCount(this.state.coinStat.totalStake))}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Total Staked USD</Card.Header>
            <Card.Body>
              <Card.Title>{HUtils.formatBigCoinCount(this.state.coinStat.usdStaked)}</Card.Title>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/>
        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Overall Network Sign Rate</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(this.state.coinStat.signRate + "%")}</Card.Title>
              <Card.Text>Data represents last completed epoch</Card.Text>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Min. # of validators to halt network</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.coinStat.valForNetworkHalt}</Card.Title>
              <Card.Text>Network can be halted by 33.34% of stake weight</Card.Text>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Expected Annual Reward Rate</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(this.state.coinStat.currentRewardRate + "%")}</Card.Title>
              <Card.Text><a className="white-a" href="/calc">Rewards Calculator</a></Card.Text>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/>
        <br/>

        <p><strong>Network Stats</strong></p>
        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>$ONE Price BTC</Card.Header>
            <Card.Body>
              <Card.Title>{SPUtilities.formatBtcPrice(this.state.coinStat.btcPrice)}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>$ONE Price USD</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.coinStat.usdPrice}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Market Cap USD</Card.Header>
            <Card.Body>
              <Card.Title>{HUtils.formatBigCoinCount(this.state.coinStat.usdMcap)}</Card.Title>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/>

        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>24h Price Change USD</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.coinStat.priceChangeUsd}%</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Total Transactions</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(HUtils.formatBigCoinCount(this.state.coinStat.totalTransactions))}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Annual Inflation</Card.Header>
            <Card.Body>
              <Card.Title>441m*</Card.Title>
              <Card.Text>*Inflation = 441m - annual tx fees</Card.Text>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/>

        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Total Supply</Card.Header>
            <Card.Body>
              <Card.Title>{HUtils.formatBigCoinCount(this.state.coinStat.totalSupply)}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Circulating Supply</Card.Header>
            <Card.Body>
              <Card.Title>{this.getHistoryLink(HUtils.formatBigCoinCount(this.state.coinStat.circulatingSupply))}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Shard 0 Block Production Rate</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.shardData["0"].blockRate} Seconds</Card.Title>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/>

        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Shard 1 Block Production Rate</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.shardData["1"].blockRate} Seconds</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Shard 2 Block Production Rate</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.shardData["2"].blockRate} Seconds</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Shard 3 Block Production Rate</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.shardData["3"].blockRate} Seconds</Card.Title>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/><br/>

        <p><strong>Epoch Stats</strong></p>
        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Current Epoch</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.coinStat.currentEpoch}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Next Epoch Start Time</Card.Header>
            <Card.Body>
              <Card.Title>{SPUtilities.epochFormatter(this.state.coinStat.nextEpochTime)}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Epoch Last Block</Card.Header>
            <Card.Body>
              <Card.Title>{this.state.coinStat.epochLastBlock}</Card.Title>
              <Card.Text>Block Time: {constants.BLOCK_TIME} seconds</Card.Text>
            </Card.Body>
          </Card>
        </CardDeck>
        <p/><br/>

        <HNetworkNav />
      </div>
    );
  }

  getHistoryLink(value) {
    return (<Link className="white-a" activeClassName="white-a" to="/history">{value}</Link>)
  }


}
/*
*/
export default NetworkStats;
