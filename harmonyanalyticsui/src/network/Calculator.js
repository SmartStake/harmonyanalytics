import React from 'react';

import Card from 'react-bootstrap/Card';
import CardDeck from 'react-bootstrap/CardDeck';
import {Button} from '@material-ui/core';
import {Redirect} from 'react-router-dom';
import {PageHeader} from 'react-bootstrap';
import {Row, FormControl, Col, Form, FormGroup, ControlLabel} from 'react-bootstrap';
import ReactAutocomplete from 'react-autocomplete';

import HNetworkNav from './HNetworkNav';
import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import MessageBox from "../components/MessageBox";
import ValidationUtils from "../util/ValidationUtils";

class Calculator extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      message: {type: undefined, body: undefined},
      calc: {},
      coinStat: {},
      calcStats: {},
      isLoading: true
    }
    this.handleCalculate = this.handleCalculate.bind(this);
    this.calculateStakingRewards = this.calculateStakingRewards.bind(this);
    this.handleStakedAmtChange = this.handleStakedAmtChange.bind(this);
    this.handleRewardRateChange = this.handleRewardRateChange.bind(this);
    this.handleFeeChange = this.handleFeeChange.bind(this);

  }

  handleFeeChange(event) {
    let value = event.target.value;
    if (value != '') {
      value = value.replace("%","");
    }

    this.setState({fee: value});
    // this.calculateStakingRewards();
  }

  handleRewardRateChange(event) {
    let value = event.target.value;
    if (value != '') {
      value = value.replace("%","");
    }

    // let input = this.state.input;
    // input.rewardRate = rewardRate.value;
    this.setState({rewardRate: value});
    // this.calculateStakingRewards();
  }

  handleStakedAmtChange(event) {
    // if (amount.value != '') {
    //   amount = amount.value.trim();
    // }

    // let input = this.state.input;
    // input.stakedAmount = amount.value;
    this.setState({stakedAmount: event.target.value});
    // this.calculateStakingRewards();
  }

  async componentDidMount() {
    const allData = await ApiUtils.get("listData?type=listApr");

    // console.log("allData is:");
    // console.log(allData);

    if (!allData) {
      return;
    }
    let data = allData["data"];
    let coinStat = allData["coinStat"];

    let rewardRate = coinStat.currentRewardRate;
    let fee = 4;
    let stakedAmount = "100000";

    this.setState({validators: data, coinStat: coinStat});
    this.setState({rewardRate: rewardRate, fee: fee, stakedAmount: stakedAmount, isLoading: false});
    this.calculateStakingRewards();
  }

  calculateStakingRewards() {
    // console.log(this.state);
    // console.log(this.state.stakedAmount);
    let stakedAmount = this.state.stakedAmount;
    if (stakedAmount) {
      stakedAmount = stakedAmount.split(",").join("");
    }
    let rewardRate = this.state.rewardRate;
    let fee = this.state.fee;

    let message = "";
    let status = "success";

    if (isNaN(stakedAmount) || stakedAmount < 1 || stakedAmount > 1000000000) {
  		alert("'Harmony delegated by you' must be a number between 1 and 1 billion");
      message = "'Harmony delegated by you' must be a number between 1 and 1 billion";
      status = "error";
  		return;
  	} else if (isNaN(rewardRate) || rewardRate < 0 || rewardRate > 100) {
  		alert("Reward rate must be between 0 and 100");
      message = "Reward rate must be between 0 and 100";
      status = "error";
  		return;
    } else if (isNaN(fee) || fee < 0 || fee > 100) {
  		alert("Fee must be between 0 and 100");
      message = "Fee must be between 0 and 100";
      status = "error";
  		return;
    }

  	let stakedAmountInt = parseFloat(stakedAmount);
  	let rewardRateInt = parseFloat(rewardRate);
  	let feeInt = parseFloat(fee);

  	let reward = stakedAmountInt * ((100 - feeInt)/100) * (rewardRateInt/100);

    let feePaid = stakedAmountInt * ((feeInt)/100) * (rewardRateInt/100);
    let feePaidSmartStake = stakedAmountInt * ((fee)/100) * (rewardRateInt/100);

    let dailyReward = reward / this.getDaysInYear();

    let weeklyReward = reward * 7/ this.getDaysInYear();

    let monthlyReward = reward / 12;

    let calcStats = {
      feePaid: feePaid.toFixed(2),
      feePaidSmartStake: feePaidSmartStake.toFixed(2),
      annualReward: reward.toFixed(2),
      monthlyAIReward: this.getCompoundReward(stakedAmountInt, feeInt, rewardRateInt, 12).toFixed(2),
      weeklyAIReward: this.getCompoundReward(stakedAmountInt, feeInt, rewardRateInt, 52).toFixed(2),
      dailyAIReward: this.getCompoundReward(stakedAmountInt, feeInt, rewardRateInt, this.getDaysInYear()).toFixed(2),
      dailyReward: dailyReward.toFixed(2),
      weeklyReward: weeklyReward.toFixed(2),
      monthlyReward: monthlyReward.toFixed(2),
    };

    this.setState({calcStats: calcStats});
	}

  getDaysInYear() {
    let today = new Date();
    let year = today.getFullYear();
    return this.isLeapYear(year) ? 366 : 365;
  }

  isLeapYear(year) {
    return year % 400 === 0 || (year % 100 !== 0 && year % 4 === 0);
  }

  handleCalculate(e) {
    e.preventDefault();
    this.calculateStakingRewards();
  }

  getCompoundReward(stakedAmount, fee, rewardRate, totalReinvestments) {
  	var amount = stakedAmount;
  	for (var i = 0; i < totalReinvestments; i++) {
  		amount += amount * ((100 - fee)/100) * (rewardRate/100) / totalReinvestments;
  		// console.log(i + " - amount is: " + amount);
  	}

  	amount = amount - stakedAmount;

  	return amount;
  }

  render() {
    if (this.state.isLoading) {
      return <div>Loading Calculator</div>;
    }

    return (
      <div>
        <p/>
        <h4 style={{align: "center"}}><span><strong>Harmony Staking Calculator</strong></span></h4>
        <p>All calculations assume <a className="black-a" href="https://explorer.harmony.one" target="_blank">1 block per 5 seconds</a>. Rewards calculations are based on total stake ({this.state.coinStat.totalStake}) and annual issuance (441 million ONE) and do not consider individual validator performance. Smart Stake charges 4% fee (0% promotion in August).</p>
        <MessageBox type={this.state.message.type} message={this.state.message.body}/>
        <Form>
          <Form.Group as={Row} controlId="stakedAmount">
            <Form.Label column sm={3}>Harmony delegated by you: </Form.Label>
            <Col sm={3}><Form.Control type="text" placeholder="Enter staked amount"
              onChange={this.handleStakedAmtChange} defaultValue={this.state.stakedAmount}/></Col>
          </Form.Group>
          <Form.Group as={Row} controlId="rewardRate">
            <Form.Label column sm={3}>Reward Rate (%): </Form.Label>
            <Col sm={3}><Form.Control type="text" placeholder="Annual reward rate in %"
              onChange={this.handleRewardRateChange} defaultValue={this.state.rewardRate}/></Col>
          </Form.Group>
          <Form.Group as={Row} controlId="fee">
            <Form.Label column sm={3}>Validator Fee: </Form.Label>
            <Col sm={3}><Form.Control type="text" placeholder="Fee paid to Validator in %"
              onChange={this.handleFeeChange} defaultValue={this.state.fee}/></Col>
          </Form.Group>
          <FormGroup>
            <Button variant="contained" color="primary" id="calcButton" type="submit" onClick={this.handleCalculate}>Calculate</Button>
          </FormGroup>
        </Form>
        <CardDeck>
          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Annual Fee paid to validator</Card.Header>
            <Card.Body>
              <Card.Title>Fee for inputs used - {this.state.calcStats.feePaid}</Card.Title>
              <Card.Title>Fee with Smart Stake - {this.state.calcStats.feePaidSmartStake}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Rewards</Card.Header>
            <Card.Body>
              <Card.Title>Daily - {this.state.calcStats.dailyReward}</Card.Title>
              <Card.Title>Weekly - {this.state.calcStats.weeklyReward}</Card.Title>
              <Card.Title>Monthly - {this.state.calcStats.monthlyReward}</Card.Title>
              <Card.Title>Annual - {this.state.calcStats.annualReward}</Card.Title>
            </Card.Body>
          </Card>

          <Card border="danger" bg="dark" text="white" style={{ width: '18rem' }}>
            <Card.Header>Compound Annual Rewards*</Card.Header>
            <Card.Body>
              <Card.Title>Annual - {this.state.calcStats.annualReward}</Card.Title>
              <Card.Title>Monthly - {this.state.calcStats.monthlyAIReward}</Card.Title>
              <Card.Title>Weekly - {this.state.calcStats.weeklyAIReward}</Card.Title>
            </Card.Body>
          </Card>
        </CardDeck>
        <br/>
        <p>* Compound Annual Rewards - "Annual" means rewards earned are reinvested once a year. "Monthly" means rewards earned are reinvested once every month. "Weekly" means rewards earned are reinvested once every week.</p>
        <HNetworkNav />
      </div>
    );
  }
  /*
  <Card.Title>Daily - {this.state.calcStats.dailyAIReward}</Card.Title>
 "Daily" means rewards earned are reinvested once every day.
*/

  validate(key, value, callerObj, msg) {
    let valid = ValidationUtils.isNotNull(value);

    if (!valid || !ValidationUtils.isValidAmount(value)) {
      callerObj.setState({[key]: msg});
      valid = false;
    } else {
      callerObj.setState({[key]: ""});
    }

    return valid;
  }

}

export default Calculator;
