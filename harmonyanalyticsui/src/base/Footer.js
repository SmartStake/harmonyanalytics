import React from 'react';
import Table from 'react-bootstrap/Table';

import config from "../config";

class Footer extends React.Component {
  render() {

    if ( window.location !== window.parent.location ) {
      return <p>Powered by SmartStake.io</p>;
    }

    return (
      <div align="center">
        <p/>
        <Table size="sm" >
          <tbody>
            <tr>
              <th><a href="http://t.me/bigb4ever" class="fa fa-telegram fa-lg"/>&nbsp;&nbsp;&nbsp;
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
