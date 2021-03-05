import React from 'react';
import {Container, Row, Col} from 'react-bootstrap';
import Card from 'react-bootstrap/Card';
import CardDeck from 'react-bootstrap/CardDeck';
import {Button} from '@material-ui/core';
import {Redirect} from 'react-router-dom';
import {PageHeader} from 'react-bootstrap';
import {FormControl, Form, FormGroup, ControlLabel} from 'react-bootstrap';
import ReactAutocomplete from 'react-autocomplete';

import NetworkUtils from '../util/NetworkUtils';
import Dropdown from '../base/Dropdown';
import constants from '../constants';
import config from '../config';

import NetworkHeader from './NetworkHeader';
import HNetworkNav from './HNetworkNav';
import ApiUtils from '../util/ApiUtils';
import SPUtilities from '../util/SPUtilities';
import Utilities from '../util/Utilities';
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
      validator: "",
      validators: [],
      rewardRate: 0,
      isLoading: true
    }
    this.handleCalculate = this.handleCalculate.bind(this);
    this.calculateStakingRewards = this.calculateStakingRewards.bind(this);
    this.handleCalculateByVal = this.handleCalculateByVal.bind(this);
    this.handleStakedAmtChange = this.handleStakedAmtChange.bind(this);
    this.handleRewardRateChange = this.handleRewardRateChange.bind(this);
    this.handleFeeChange = this.handleFeeChange.bind(this);

  }

  resetForm() {
    window.location.reload();
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
    let data = Utilities.moveElementToTop(allData["data"], "code", NetworkUtils.getDefaultPool());
    let coinStat = allData["coinStat"];

    let rewardRate = coinStat.currentRewardRate;
    let fee = coinStat.smartStakeFee;
    let stakedAmount = "100000";

    this.setState({validators: data, coinStat: coinStat, rewardRate: rewardRate,
      fee: fee, stakedAmount: stakedAmount, isLoading: false});
    this.calculateStakingRewards();
  }

  onValSelect = (e) => {
    // alert(e.target.value)
    // console.log(e.target.value);
    let val = Utilities.getElementByAttribute(this.state.validators, "code", e.target.value);
    // console.log(val);
    let rewardRate = val.avgApr;
    let fee = val.fee;

    this.setState({rewardRate: rewardRate, fee: fee});
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
  		alert("'$ONE delegated by you' must be a number between 1 and 1 billion");
      message = "'$ONE delegated by you' must be a number between 1 and 1 billion";
      status = "error";
  		return;
  	} else if (isNaN(rewardRate) || rewardRate < 0 || rewardRate > 5000) {
  		alert("Reward rate must be between 0 and 5000");
      message = "Reward rate must be between 0 and 5000";
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
      monthlyRewardInt: monthlyReward,
      stakedAmount: stakedAmountInt, feeInt: feeInt, rewardRateInt: rewardRateInt
    };

    // let rewardData = this.getRewardData(calcStats);
    // this.setState({calcStats: calcStats, rewardData: rewardData});

    this.setState({calcStats: calcStats});
	}

  getRewardData(calcStats) {
    let rewardData = [];

    let prevRecord = {"month": 0, "stake": calcStats.stakedAmount,
      "stakeWeeklyCompound": calcStats.stakedAmount,
      "stakeMonthlyCompound": calcStats.stakedAmount,
      "stakeAnnualCompound": calcStats.stakedAmount,
      "stakeAnnualPrevValid": calcStats.stakedAmount};
    console.log(prevRecord)
    rewardData.push(prevRecord);
    for (let month=1; month <= 60; month++) {
      let stake = prevRecord.stake + calcStats.monthlyRewardInt
      let stakeMonthlyCompoundRewards = this.getRewardAmountByFactor(prevRecord.stakeMonthlyCompound,
        calcStats.feeInt, calcStats.rewardRateInt, 1, 12);
      let stakeWeeklyCompoundRewards = this.getRewardAmountByFactor(prevRecord.stakeWeeklyCompound,
        calcStats.feeInt, calcStats.rewardRateInt, 4, 52);
      stakeWeeklyCompoundRewards += stakeWeeklyCompoundRewards * (52/12 - 4);
      let stakeWeeklyCompound = prevRecord.stake + stakeWeeklyCompoundRewards;
      let stakeMonthlyCompound = prevRecord.stake + stakeMonthlyCompoundRewards;
      let stakeAnnualCompound = null;
      let stakeAnnualPrevValid = null;
      if (month % 12 === 0) {
        stakeAnnualCompound = this.getRewardAmountByFactor(prevRecord.stakeAnnualCompound,
          calcStats.feeInt, calcStats.rewardRateInt, month/12, 1);
        stakeAnnualPrevValid = prevRecord.stakeAnnualPrevValid;
      }

      let record = {"month": month, "stake": stake,
        "stakeWeeklyCompound": stakeWeeklyCompound,
        "stakeMonthlyCompound": stakeMonthlyCompound,
        "stakeAnnualPrevValid": stakeAnnualPrevValid,
        "stakeAnnualCompound": stakeAnnualCompound};
      console.log(record);
      rewardData.push(record);
      prevRecord = record;
    }

    console.log(rewardData);
    return rewardData;
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

  handleCalculateByVal(e) {
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

  getRewardAmountByFactor(stakedAmount, fee, rewardRate, totalReinvestments, annualFactor) {
  	var amount = stakedAmount;
  	for (var i = 0; i < totalReinvestments; i++) {
  		amount += amount * ((100 - fee)/100) * (rewardRate/100) / annualFactor;
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
        <NetworkHeader title="Rewards Calculator" />
        <p>All calculations assume <a className="black-a" href="https://explorer.harmony.one" target="_blank">1 block per 2 seconds</a>. Rewards calculations are based on total stake ({this.state.coinStat.totalStake}) and annual issuance (441 million ONE) and do not consider individual validator performance. Smart Stake charges {this.state.coinStat.smartStakeFee}% fee.</p>
        <MessageBox type={this.state.message.type} message={this.state.message.body}/>
        <Container fluid>
          <Row>
            <Col md>
              <Card>
                <Card.Header>Rewards Calculator</Card.Header>
                <Card.Body>
                  <Card.Text>
                    <Form>
                      <Form.Group as={Row} controlId="stakedAmount">
                        <Form.Label column sm={6}>$ONE delegated by you: </Form.Label>
                        <Col sm={6}><Form.Control type="text" placeholder="Enter staked amount"
                          onChange={this.handleStakedAmtChange} defaultValue={this.state.stakedAmount}/></Col>
                      </Form.Group>
                      <Form.Group as={Row} controlId="rewardRate">
                        <Form.Label column sm={6}>Reward Rate (%): </Form.Label>
                        <Col sm={6}><Form.Control type="text" placeholder="Annual reward rate in %"
                          onChange={this.handleRewardRateChange} defaultValue={this.state.rewardRate}/></Col>
                      </Form.Group>
                      <Form.Group as={Row} controlId="fee">
                        <Form.Label column sm={6}>Validator Fee: </Form.Label>
                        <Col sm={6}><Form.Control type="text" placeholder="Fee paid to Validator in %"
                          onChange={this.handleFeeChange} defaultValue={this.state.coinStat.smartStakeFee}/></Col>
                      </Form.Group>
                      <FormGroup as={Row}>
                        <Col sm={3}><Button variant="contained" color="primary" id="calcButton" type="submit" onClick={this.handleCalculate}>Calculate</Button>&nbsp;</Col>
                        <Col sm={3}><Button variant="contained" color="secondary" id="resetButton1" type="button" onClick={this.resetForm}>Reset</Button></Col>
                      </FormGroup>
                    </Form>
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md>
              <Card>
                <Card.Header>Rewards Calculator by Validator</Card.Header>
                <Card.Body>
                  <Card.Text>
                    <Form>
                      <Form.Group as={Row} controlId="stakedAmount">
                        <Form.Label column sm={6}>$ONE delegated by you: </Form.Label>
                        <Col sm={6}><Form.Control type="text" placeholder="Enter staked amount"
                          onChange={this.handleStakedAmtChange} defaultValue={this.state.stakedAmount}/></Col>
                      </Form.Group>
                      <FormGroup as={Row} controlId="validatorControlId">
                        <Form.Label column sm={6}>Validator (Name, Status & APR): </Form.Label>
                        <Col sm={6}><Dropdown onSelect={this.onValSelect} values={this.state.validators} addAll={false} addBlank={true} /></Col>
                      </FormGroup>
                      <FormGroup as={Row} controlId="validatorControlId">
                        <Form.Label column sm={6}>Reward Rate (%): </Form.Label>
                        <Col sm={6}><Form.Control plaintext readOnly value={this.state.rewardRate} /></Col>
                      </FormGroup>

                      <FormGroup as={Row}>
                        <Col sm={3}><Button variant="contained" color="primary" id="calcButton2" type="submit" onClick={this.handleCalculateByVal}>Calculate</Button>&nbsp;</Col>
                        <Col sm={3}><Button variant="contained" color="secondary" id="resetButton2" type="button" onClick={this.resetForm}>Reset</Button></Col>
                      </FormGroup>
                    </Form>
                  </Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
        <p/>
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
  <FormGroup controlId="currencyControlId">
    <Form.Label column sm={3}>Validators: </Form.Label>
    <Col sm={3}><ReactAutocomplete items={this.state.validators} menuStyle={constants.menuStyle}
      shouldItemRender={(item, value) => item.description.toLowerCase().indexOf(value.toLowerCase()) > -1}
      getItemValue={item => item.description} renderItem={(item, highlighted) =>
        <div key={item.code} style={{ backgroundColor: highlighted ? '#eee' : 'transparent'}}>{item.description}</div>
      } value={this.state.validator} onChange={e => this.setState({ validator: e.target.value })}
      onSelect={value => this.setState({ validator: value })} /></Col>
  </FormGroup>

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
