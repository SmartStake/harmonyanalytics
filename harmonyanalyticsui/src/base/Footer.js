import React from 'react';
import Table from 'react-bootstrap/Table';

import config from "../config";

class Footer extends React.Component {
  render() {
    // var hideFooter = false;
    // console.log("this.props: ", this.props);
    // console.log("this.props.location: ", this.props.location);
    // if (this.props && this.props.location) {
    //   // params = queryString.parse(this.props.location.search)
    //   let params = Utilities.parseParams(this)
    //   console.log("params are: ", params);
    //   if (params.hideFooter != undefined) {
    //     hideFooter = params.hideFooter;
    //     console.log("hideFooter: ", hideFooter);
    //   }
    // }

    // if ( window.location !== window.parent.location ) {
    //   return <p>This website is a copyright of SmartStake.io</p>;
    // }
    //
    // return (
    //   <div align="center">
    //     <p/>
    //     <hr/>
    //     <h4>Have questions? Contact Us!</h4>
    //     <p align="center">
    //         <a href="http://t.me/SmartStake" class="fa fa-telegram fa-lg"/>&nbsp;&nbsp;&nbsp;
    //         <a href="https://twitter.com/SmartStake" class="fa fa-twitter fa-lg"/>&nbsp;&nbsp;&nbsp;
    //         {this.renderBot()}
    //         &nbsp;&nbsp;<a class="black-a" href="https://www.SmartStake.io">Home</a>
    //     </p>
    //     <p>This website is a copyright of <a class="black-a" href="https://www.SmartStake.io">Smart Stake</a></p>
    //   </div>
    // );
    if ( window.location !== window.parent.location ) {
      return <p>Powered by SmartStake.io</p>;
    }

    return (
      <div align="center">
        <p/>
        <Table size="sm" >
          <tbody>
            <tr>
              <th><a href="http://t.me/SmartStake" class="fa fa-telegram fa-lg"/>&nbsp;&nbsp;&nbsp;
              <a href="https://twitter.com/SmartStake" class="fa fa-twitter fa-lg"/>&nbsp;&nbsp;&nbsp;</th>
              <th><span className="buttonWithText">Powered by <a class="black-a" href="https://www.SmartStake.io">Smart Stake</a></span></th>
            </tr>
          </tbody>
        </Table>
      </div>
    );
  }

  renderBot() {
    return <a class="black-a" href="http://t.me/HarmonyAnalyticsBot"><img width="24" height="24" src="/images/tgBot.png" alt="Harmony Analytics Telegram Bot" /></a>
  }
}

export default Footer;
