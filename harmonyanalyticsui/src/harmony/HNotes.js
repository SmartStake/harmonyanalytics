import React from 'react';
import {CollapsibleComponent, CollapsibleHead, CollapsibleContent} from 'react-collapsible-component';
import {Collapse} from 'react-collapse';


class HNotes extends React.Component {

  static getPoolNote() {
    return (<Collapse isOpened={true}>
        <ul>
          <li>Last Epoch ER - Expected Return (ER) calculated based on rewards received in last completed epoch</li>
          <li>Current ER/Current Epoch ER - ER calculated based on performance in current epoch. It is assumed that the node will continue to operate at same level as it has so far in the current epoch.</li>
          <li>Avg ER - Average ER based on last 20 completed epochs performance. Smart Stake data collection has started on 27th May and as a result it will use data for the available epochs (upto 20 epochs).</li>
          <li>ERI (Expected Return Index) - is a ratio of the Expected Returns/ER of a validator as compared to the Average ER of all validators in a given time window. A ratio of 1 means that a validator is performing at an average level. A value &lt;1 means that it performing worse than average and a value &gt;1 means that it is performing better than average.</li>
          <li>Status - Not eligble for election - it means that the validator is not eligible for election in next epoch due to not enough self stake (10k ONE) or bad performance in previous epoch or because it got jailed.</li>
          <li>Past metrics are not an indicator of future performance. Overal stake percentage increase, effective stake, validator node performance and other factors can affect the staking rewards.</li>
          <li>Click anywhere on a record to see details.</li>
          <li>Current ER/ERI: Data is synced every 5 min. First sync of epoch will have up to 5 min of previous epoch's performance data and may skew the results to some degree. Cross shard delay (generally ~200 blocks) can result in delayed status of nodes operating on shards.</li>

        </ul>
      </Collapse>);
  }

  static getFilterHelp() {
    return (<div>
      <hr/>
      <Collapse isOpened={true}>
        <div><p><b>My Account Search Help</b></p>
          <ul>
            <li>Input - $ONE Address - enter your $ONE address.</li>
            <li>Input - Nickname/Alias - an easy to remember nick name or alias. Save once and search across devices in future. A shortcut is also placed automatically on this page for nicknames/aliases used on current device. Please do not use your or other people's names.</li>
            <li>Input - Search - save the alias (if entered) in browser and perform the search. If address is not entered and alias is not known to the backend, search will not work.</li>
            <li>Input - Save & Search - save the search criteria with the entered nickname for future use and perform the search.</li>
            <li>Remove Aliases link - remove all aliases from this device and Smart Stake backend.</li>
            <li>Summary - Total Stake - Total $ONE staked.</li>
            <li>Summary - Total Reward - Total outstanding $ONE reward across all validators.</li>
            <li>Search Results - Address - Address for which rewards are being searched.</li>
            <li>Search Results - Validator Name - Staking validator for the current record.</li>
            <li>Search Results - Validator Total Stake - Total $ONE staked with the validator by all delegates.</li>
            <li>Search Results - Stake in Validator - Total $ONE staked by the address in a given validator.</li>
            <li>Search Results - % Stake (portfolio) - for a given address, this is %age of all $ONE staked with current validator.</li>
            <li>Search Results - Rewards in Validator - Total $ONE reward oustanding for the address in a given validator.</li>
            <li>Search Results - % Rewards (portfolio) - for a given address, this is %age of all $ONE rewards outstanding with current validator.</li>
          </ul>
        </div>
      </Collapse>
    </div>);
  }


}
export default HNotes;
