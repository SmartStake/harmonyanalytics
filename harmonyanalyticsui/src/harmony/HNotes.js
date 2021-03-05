import React from 'react';
import {CollapsibleComponent, CollapsibleHead, CollapsibleContent} from 'react-collapsible-component';
import {Collapse} from 'react-collapse';

import text from "../text";

class HNotes extends React.Component {

  static getBlsNote() {
    return (<Collapse isOpened={true}>
        <ul>
          <li>BLS Key Performance Analyzer provides means to identify underperforming BLS keys. There are no direct ways of identifying a BLS key that is under performing. The tool works by assessing the BLS key performance by relying on the rewards earned by a given BLS key in a given shard and comparing the returns with the best performing BLS key in the same shard. Here is an explanation of the terms/metrics introduced:</li>
          <li>Node Version - "lowest" version of the node software associated with a given BLS Key.</li>
          <li>Group % Stake - Ratio of the effective stake of a specific BLS key against the whole shard.</li>
          <li>Group % Reward - Ratio of the earned reward of a specific BLS key against total reward earned by the whole shard.</li>
          <li>Group Reward Ratio - Ratio of the Group % Reward against Group % Stake. A value of 1 indicates that the earned reward is average. A value &gt;1 will generally mean that there are some other under performing keys in the shard due to which the key is earning more rewards. A value greater than or equal to 1 is not a guarantee that the key is not losing any signs (e.g. because of some other non-performing keys belonging to another validator).</li>
          <li>Performance Index - Ratio of Group Reward Ratio of a specific BLS key as compared to the best Group Reward Ratio. The best Group Reward Ratio will generally be for the BLS key that has signed 100%. Do not panic by seeing a lower value of the Performance Index. This metric must be used in the context of your overall Sign Rate.</li>
          <li>Performance Index color codes - Green &gt;0.99, Orange &gt;0.98, Red &lt;0.98</li>
          <li>Under Performing indicator - a key is marked as under performing if the performance index is less than 0.99.</li>
          <li>Left & Right Arrows - see keys performance for the previous epoch or next epoch.</li>
        </ul>
      </Collapse>);
      // <li>Legend - <font style={{ backgroundColor: 'gainsboro' }}>Favorite</font>
      //   &nbsp;&nbsp;<font style={{ backgroundColor: 'oldlace'}}>Not eligible at this time for election in next epoch</font></li>
  }

  static getPoolNote() {
    return (<Collapse isOpened={true}>
        <ul>
          <li>Last Epoch ER - Expected Return (ER) calculated based on rewards received in last completed epoch</li>
          <li>Current ER/Current Epoch ER - ER calculated based on performance in current epoch. It is assumed that the node will continue to operate at same level as it has so far in the current epoch.</li>
          <li>Avg ER - Average ER based on last 30 completed epochs performance.</li>
          <li>{text.eri}{text.eriDetails}</li>
          <li>Election Rate: Election rate indicates how often a validator got elected in the last 30 epochs. A value of 100 means the validator was elected every single time.</li>
          <li>Status - Not eligible for election - it means that the validator is not eligible for election in next epoch due to not enough self stake (10k ONE) or bad performance in previous epoch or because it got jailed.</li>
          <li>Past metrics are not an indicator of future performance. Overal stake percentage increase, effective stake, validator node performance and other factors can affect the staking rewards.</li>
          <li>Current ER/ERI: Data is synced every 5 min. First sync of epoch will have up to 5 min of previous epoch's performance data and may skew the results to some degree. Cross shard delay (generally ~200 blocks) can result in delayed status of nodes operating on shards.</li>
          <li>Click anywhere on a record to see further details.</li>
        </ul>
      </Collapse>);
      // <li>Legend - <font style={{ backgroundColor: 'gainsboro' }}>Favorite</font>
      //   &nbsp;&nbsp;<font style={{ backgroundColor: 'oldlace'}}>Not eligible at this time for election in next epoch</font></li>
  }

/*  static getPoolNote() {
    return (<div align="left">
      <hr/>
      <CollapsibleComponent name="note">
        <CollapsibleHead isExpanded={false}><font color="black"><b>Screen Guide</b> - click here for details</font>
        </CollapsibleHead>
        <CollapsibleContent isExpanded={false}>
          <ul>
            <li>Last Epoch ER - Expected Return (ER) calculated based on rewards received in last completed epoch</li>
            <li>Current ER/Current Epoch ER - ER calculated based on performance in current epoch. It is assumed that the node will continue to operate at same level as it has so far in the current epoch.</li>
            <li>Avg ER - Average ER based on last 30 completed epochs performance.</li>
            <li><font color="red">ERI (Expected Return Index)</font> - is a ratio of the Expected Returns/ER of a validator as compared to the Average ER of all validators in a given time window. A ratio of 1 means that a validator is performing at an average level. A value &lt;1 means that it performing worse than average and a value &gt;1 means that it is performing better than average.</li>
            <li>Status - Not eligble for election - it means that the validator is not eligible for election in next epoch due to not enough self stake (10k ONE) or bad performance in previous epoch or because it got jailed.</li>
            <li>Past metrics are not an indicator of future performance. Overal stake percentage increase, effective stake, validator node performance and other factors can affect the staking rewards.</li>
          </ul>
        </CollapsibleContent>
      </CollapsibleComponent>
    </div>);
  }
*/
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
            <li>Search Results - Reward Ratio - Indicates the relative performance of a delegation as compared to rest of the delegations for the address. A ratio of 1 means that performance is average. A ratio &gt;1 means that a delegation performed better than average and a ratio &lt;1 means that a delegation performed worse than average.</li>
            <li>This screen can be used for relative performance assessment only when all delegations start off with 0 rewards at the same time i.e. works best when new delegations have not been added after the last rewards claim.</li>
          </ul>
        </div>
      </Collapse>
    </div>);
  }


}
export default HNotes;
