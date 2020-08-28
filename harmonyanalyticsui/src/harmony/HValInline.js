import React from 'react';
import Table from 'react-bootstrap/Table';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import Card from 'react-bootstrap/Card';
import {Button} from '@material-ui/core';

import CollapsibleSection from "../base/CollapsibleSection";

import HValNav from './HValNav';
import SPUtilities from "../util/SPUtilities";
import SPCalc from "../util/SPCalc";
import HUtils from "./HUtils";

class HValInline extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      width: window.innerWidth,
    }
    this.updateDimensions = this.updateDimensions.bind(this);
    this.renderShowMoreDetails = this.renderShowMoreDetails.bind(this);

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
  }

  render() {
    return (
      <div>
        <Table striped bordered size="sm">
          <tbody>
            <tr>
              <th align="left">Validator Name: </th>
              <td align="left"> {HUtils.nameFormatterLong(this.props.val.name, this.props.val)}</td>
            </tr>
            <tr>
              <th align="left">Website: </th>
              <td align="left"> {HUtils.websiteLink(this.props.val.website, this.props.val.website)}</td>
            </tr>
            <tr>
              <th align="left">Address: </th>
              <td align="left"> {HUtils.valAddressFormatterLong(this.props.val.address)}</td>
            </tr>
            <tr>
              <th align="left">Total Staked: </th>
              <td align="left"> {HUtils.coinCountCellFormatter(this.props.val.totalStaked, this.props.val)}</td>
            </tr>
            <tr>
              <th align="left">Bls Key Count: </th>
              <td align="left"> {this.props.val.blsKeyCount}</td>
            </tr>
            <tr>
              <th align="left">Bls Key Count by Median Stake: </th>
              <td align="left"> {this.props.val.optimalBlsKeyCount}</td>
            </tr>
            <tr>
              <th align="left">Bid per seat: </th>
              <td align="left"> {HUtils.coinCountCellFormatter(this.props.val.bidPerSeat, this.props.val)}</td>
            </tr>

            <tr>
              <th align="left">Self Stake: </th>
              <td align="left"> {HUtils.coinCountCellFormatter(this.props.val.selfStake, this.props.val)}</td>
            </tr>

            <tr>
              <th align="left">Unique Delegates: </th>
              <td align="left"> {this.props.val.uniqueDelegates}</td>
            </tr>
            <tr>
              <th align="left">Fee: </th>
              <td align="left"> {HUtils.getFee(this.props.val.fee, this.props.val, 0, this.props.coinStat.currentEpoch)}</td>
            </tr>
            <tr>
              <th align="left">Max Fee: </th>
              <td align="left"> {HUtils.convertPercentFormatter(this.props.val.maxFee)}</td>
            </tr>
            <tr>
              <th align="left">Fee Change Rate: </th>
              <td align="left"> {HUtils.convertPercentFormatter(this.props.val.feeChangeRate)}</td>
            </tr>
            <tr>
              <th align="left">Elected: </th>
              <td align="left"> {this.props.val.elected}</td>
            </tr>
            <tr>
              <th align="left">Status: </th>
              <td align="left"> {this.props.val.status}</td>
            </tr>
            <tr>
              <th align="left">Last Updated: </th>
              <td align="left"> {SPUtilities.getLastUpdatedFromEpoch(this.props.val.syncEpochTime)}</td>
            </tr>
          </tbody>
        </Table>
        <p align="center">{HUtils.stakeFormatterLarge(this.props.val.address, this.props.val)}</p>
        <hr/>
        <p><b>Validator Performance - Running Summary</b>
        <br/>This data does not use completed days and presents validator performance counted backwards from this moment</p>
        <Table striped bordered size="sm" >
          <thead>
            <tr>
              <th>Window</th>
              <th>Rewards</th>
              <th>Asked to sign</th>
              <th>Signed</th>
              <th>Sign %</th>
            </tr>
          </thead>

          <tbody>
            <tr>
              <td align="left">Current Epoch</td>
              <td align="left"> {SPCalc.formatIntCount(this.props.val.currentEpochRewards)}</td>
              <td align="left"> {this.props.val.currentEpochToSign}</td>
              <td align="left"> {this.props.val.currentEpochSigned}</td>
              <td align="left"> {this.props.val.currentEpochSignPer}</td>
            </tr>
            <tr>
              <td align="left">All</td>
              <td align="left"> {SPCalc.formatIntCount(this.props.val.totalRewards)}</td>
              <td align="left"> {this.props.val.lifetimeToSign}</td>
              <td align="left"> {this.props.val.lifetimeSigned}</td>
              <td align="left"> {HUtils.calcPercent(this.props.val.lifetimeSigned, this.props.val.lifetimeToSign)}</td>
            </tr>
          </tbody>
        </Table>
        <hr/>

        <p><b>Validator Performance - Expected Returns</b></p>
        <Table striped bordered size="sm" >
          <thead>
            <tr>
              <th>Window</th>
              <th>ER</th>
              <th>Net ER</th>
              <th>ER Index</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td align="left">Current Epoch</td>
              <td align="left"> {HUtils.showCurrentReturns(this.props.val.currentApr, this.props.val)}</td>
              <td align="left"> {HUtils.showCurrentReturns(this.props.val.currentNetApr, this.props.val)}</td>
              <td align="left"> {HUtils.showCurrentReturns(this.props.val.currentEri, this.props.val)}</td>
            </tr>
            <tr>
              <td align="left">Previous Epoch</td>
              <td align="left"> {this.props.val.prevEpochApr}</td>
              <td align="left"> {this.props.val.prevEpochNetApr}</td>
              <td align="left"> {this.props.val.prevEpochEri}</td>
            </tr>
            <tr>
              <td align="left">Average</td>
              <td align="left"> {this.props.val.avgApr}</td>
              <td align="left"> {this.props.val.avgNetApr}</td>
              <td align="left"> {this.props.val.avgEri}</td>
            </tr>
          </tbody>
        </Table>
        <hr/>

        <CollapsibleSection getSectionContent={this.renderShowMoreDetails}
          title="More Details" isVisible={false} sectionId="valShowMoreDetails" />

        {!this.state.isLoading && !this.props.hideNav && this.renderValNav()}
      </div>
    );
  }
  // <a href={"https://staking.harmony.one/validators/mainnet/" + this.props.val.address}
  //   target="_blank"><Button variant="contained" color="primary" id={"Stake" + this.props.val.address} size="small"
  //   >Stake</Button></a>

  renderShowMoreDetails() {
    return (
      <Card>
        <Card.Header>More Details</Card.Header>
        <Card.Body>
          <Card.Text>
            <Table striped bordered size="sm">
                <tbody>
                  <tr>
                    <th align="left">Identity: </th>
                    <td align="left"> {this.props.val.identity}</td>
                  </tr>
                  <tr>
                    <th align="left">Security Contact: </th>
                    <td align="left"> {this.props.val.securityContact}</td>
                  </tr>
                  <tr>
                    <th align="left">Details: </th>
                    <td align="left"> {this.props.val.details}</td>
                  </tr>
                  <tr>
                    <th align="left">Max Total Delegation: </th>
                    <td align="left"> {this.props.val.maxTotalDelegation}</td>
                  </tr>
                  <tr>
                    <th align="left">Total Rewards: </th>
                    <td align="left"> {this.props.val.totalRewards}</td>
                  </tr>
                </tbody>
              </Table>
          </Card.Text>
        </Card.Body>
      </Card>);
  }
  // <tr>
  //   <th align="left">Lifetime Apr: </th>
  //   <td align="left"> {this.props.val.lifetimeApr}</td>
  // </tr>

  renderValNav() {
    return (<HValNav hPoolId={this.props.val.hPoolId}/>);
  }
}


export default HValInline;
