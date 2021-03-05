import React from 'react';
import BootstrapTable from 'react-bootstrap-table-next';
import Table from 'react-bootstrap/Table';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';
import ReactTooltip from "react-tooltip";

import Contact from "../base/Contact";
import UITableUtils from "../util/UITableUtils";
import constants from "../constants";
import CollapsibleNote from "../base/CollapsibleNote";

import HNotes from "../harmony/HNotes";
import UIUtils from "../util/UIUtils";
import LogoUtils from "../util/LogoUtils";
import ApiUtils from '../util/ApiUtils';
import "./Validators.css";
import SPCalc from '../util/SPCalc';
import Utilities from "../util/Utilities";
import SPUtilities from "../util/SPUtilities";
import FavUtils from "../util/FavUtils";
import RespUtils from "../util/RespUtils";

import HUtils from "./HUtils";
import HValInline from "./HValInline";
import HNetworkHeader from "./HNetworkHeader";

class Validators extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      validators: [],
      coinStat: {},
      statusSummary: {},
      blockRate: {},
      notification: {"message": null},
      width: window.innerWidth,
      size: 10,
      lastUpdated: "",
      isLoading: true,
    }
    this.updateDimensions = this.updateDimensions.bind(this);
    this.reload = this.reload.bind(this);
    this.favourite = this.favourite.bind(this);
    this.unfavourite = this.unfavourite.bind(this);
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

    // var hPoolId = UIUtils.getNodeId(this);
    let url = "listData?type=listPools"
    // const nodeData = await ApiUtils.get("listValidators?sortBy=stake");
    if (this.props.match && this.props.match.params.status) {
      url += "&status=" + this.props.match.params.status;
    } else {
      url += "&status=Elected"
    }
    // console.log(url);

    const allData = await ApiUtils.get(url);
    // console.log(allData)
    if (!allData) {
      this.setState({error: true, isLoading: false});
      return;
    }

    let validators = allData["data"];
    let lastUpdated = allData["lastUpdated"];
    if (validators) {
      let newValidators = Utilities.addIndex(validators);
      let finalData = FavUtils.filterData(this, newValidators);

      let cumulativeWeight = 0
      for(let i=0;i < finalData.length; i++) {
        let val = finalData[i];
        cumulativeWeight += val.stakeWeight;
        val.cumulativeWeight = cumulativeWeight;
      }

      let newLastUpdated = lastUpdated;
      if (lastUpdated == null) {
        newLastUpdated = 0;
      }

      let notification = allData["notification"];
      let statusSummary = allData["statusSummary"];
      let coinStat = allData["coinStat"];
      this.setState({lastUpdated: newLastUpdated, notification: notification,
        statusSummary: statusSummary, validators: finalData, coinStat: coinStat});
    }

    this.setState({isLoading: false});
  }

  unfavourite(e) {
    FavUtils.unfavourite(e, this);
  }

  favourite(e) {
    FavUtils.favourite(e, this);
  }

  render() {
    let loadMsg = UIUtils.getLoading(this);
    if (loadMsg) return loadMsg;

    var columns;
    if (RespUtils.isMobileView()) {
      columns = [
        {text: "",dataField: "hPoolId", sort: true, style: HUtils.consensusStyleFormatter, formatter: FavUtils.favoriteFormatter, formatExtraData: this, headerStyle: Utilities.width(5)},
        {text: "Name", dataField: "name", formatter: HUtils.nameFormatterShort, sort: true, headerStyle: Utilities.width(24)},
        {text: "Staked", dataField: "totalStaked", sort: true, formatter: SPUtilities.stakeFormatterRounded, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(15)},
        {text: "ERI", dataField: "avgEri", formatter: HUtils.eriFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(19)},
        {text: "Sign %", dataField: "currentEpochSignPer", formatter: HUtils.signPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(20)},
      ];
    } else if (RespUtils.isTabletView()) {
      columns = [
        {text: "",dataField: "hPoolId", sort: true, style: HUtils.consensusStyleFormatter, formatter: FavUtils.favoriteFormatter, formatExtraData: this, headerStyle: Utilities.width(5)},
        {text: "",dataField: "address", sort: true, formatter: LogoUtils.formatLogo, headerStyle: Utilities.width(4)},
        {text: "Name", dataField: "name", formatter: HUtils.nameFormatterShort, sort: true, headerStyle: Utilities.width(13)},
        {text: "Staked", dataField: "totalStaked", sort: true, formatter: SPUtilities.stakeFormatterRounded, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
        {text: "Status", dataField: "status", formatter: HUtils.statusFormatter, sort: true, headerStyle: Utilities.width(16)},
        {text: "Fee", dataField: "fee", sort: true, formatter: HUtils.getFee, formatExtraData: this.state.coinStat.currentEpoch, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(9)},
        {text: "Avg ERI", dataField: "avgEri", formatter: HUtils.eriFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
        {text: "Current ERI", dataField: "currentEri", formatter: HUtils.eriFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(18)},
        {text: "Sign %", dataField: "currentEpochSignPer", formatter: HUtils.signPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(12)},
      ];
    } else {
      columns = [
        {text: "",dataField: "hPoolId", sort: true, formatter: FavUtils.favoriteFormatter, formatExtraData: this, headerStyle: Utilities.width(2)},
        {text: "",dataField: "address", sort: true, formatter: LogoUtils.formatLogo, headerStyle: Utilities.width(2)},
        {text: "Name", dataField: "name", formatter: HUtils.nameFormatter, sort: true, headerStyle: Utilities.width(10)},
        {text: "Total Staked", dataField: "totalStaked", sort: true, formatter: SPUtilities.formatCoins, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(8)},
        {text: "Fee", dataField: "fee", sort: true, formatter: HUtils.getFee, formatExtraData: this.state.coinStat.currentEpoch, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(5)},
        {text: "Stake Weight", dataField: "stakeWeight", sort: true, formatter: HUtils.progressFormatter, style: HUtils.progressStyle, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
        {text: "Status", dataField: "status", formatter: HUtils.statusFormatter, sort: true, headerStyle: Utilities.width(8)},
        {text: "Delegates", dataField: "uniqueDelegates", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(6)},
        {text: "Election Rate", dataField: "electionRate", formatter: HUtils.intFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(6)},
        {text: "Avg ER", dataField: "avgApr", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(5)},
        {text: "Avg ERI", dataField: "avgEri", sort: true, formatter: HUtils.eriFormatter, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(5)},
        {text: "Avg Sign %", dataField: "avgSignPer", formatter: HUtils.signPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
        // {text: "Last ER", dataField: "prevEpochApr", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(6)},
        {text: "Last ERI", dataField: "prevEpochEri", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(5)},
        // {text: "Current ER", dataField: "currentApr", formatter: HUtils.showCurrentReturns, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
        {text: "Current ERI", dataField: "currentEri", formatter: HUtils.eriFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
        {text: "Current Sign %", dataField: "currentEpochSignPer", formatter: HUtils.signPerFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(9)},
        {text: "Stake", dataField: "address", sort: false, formatter: HUtils.stakeFormatter, headerStyle: Utilities.width(4)},
      ];
    }
    // {text: "",dataField: "logoPath", sort: true, formatter: HUtils.logoFormatter, formatExtraData: this, headerStyle: Utilities.width(3)},
    // , filter: textFilter({placeholder: "Name"})
    // {text: "Address", dataField: "address", formatter: HUtils.addressFormatter, formatExtraData: this, sort: true, headerStyle: Utilities.width(12)},
    // {text: "Self Stake", dataField: "selfStake", sort: true, formatter: HUtils.coinCountCellFormatter, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
    // {text: "BLS Key Count", dataField: "blsKeyCount", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(7)},
    // {text: "BLS # by Median Stake", dataField: "optimalBlsKeyCount", formatter: HUtils.blsKeyCountFormatter, sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(6)},
    // {text: "Bid per seat", dataField: "bidPerSeat", sort: true, formatter: HUtils.coinCountCellFormatter, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(6)},
    // {text: "Avg Net ER", dataField: "avgNetApr", sort: true, sortFunc: Utilities.sortNumeric, headerStyle: Utilities.width(6)},

    const options = {
      onlyOneExpanding: true
    };

    let specialMessage = "";
    if (window.innerWidth < 600) {
      specialMessage = "Tip: This screen is best viewed in landscape mode (Rotate your mobile device for a better view)";
    }

    const expandRow = {
      renderer: row => (
        <div>
          <HValInline val={row} coinStat={this.state.coinStat}/>
          <hr/>
        </div>
      ), showExpandColumn: false
    };

    const rowStyle = (row, rowIndex) => {
      // console.log(row.nodeName, " - ", row.status);
      if (row.status == constants.notEligibleStatus) {
        // console.log(row.active);
        return { backgroundColor: 'oldlace' };
      }

      if (FavUtils.isFavourite(row.hPoolId)) {
        return { backgroundColor: 'gainsboro' };
      }

    };

    let lastUpdated = this.state.lastUpdated ? (this.state.lastUpdated/60).toFixed(0) : "N/A";
    let wrapperClasses = UITableUtils.isDefaultView() ? "table":"table-responsive";
    //{UITableUtils.renderSwitchView(this)}
    // <a className="regular-b-a" target="_blank"
    //     href="https://harmony.one/"><img src="/images/logo/harmony.png" width="28"
    //     height="28" className="d-inline-block align-top" alt="Harmony"
    //     /><strong>Harmony</strong></a>
    return (
      <div>
        <p/>
        <h4 style={{align: "center"}}><span><strong>Validators</strong></span>
            {UIUtils.renderPageActions(this, true, true)}
        </h4>
        {HUtils.renderRewards()}
        <HNetworkHeader coinStat={this.state.coinStat} />
        <p>Last updated - <b>{lastUpdated}</b> minutes ago. Try our telegram bot <a target="_blank" class="black-a" href="https://t.me/HarmonyAnalyticsBot">HarmonyAnalyticsBot</a>. <a href="https://talk.harmony.one/t/how-to-use-harmony-analytics-dashboard/911" class="black-a" target="_blank">Click here</a> to learn how to use the dashboard. <a href="https://staking.harmony.one" class="black-a" target="_blank">Harmony Staking Dashboard</a></p>
        {this.renderStatusTags()}
        {UIUtils.getNotification(this.state.notification)}
        <p/>
        <ReactTooltip id="main" place="top" type="dark" effect="float" multiline={true} />
        <BootstrapTable keyField='hPoolId' data={ this.state.validators } filter={ filterFactory() }
          columns={ columns } hover striped expandRow={ expandRow }
          expandableRow={ () => { return true; } }  rowStyle={rowStyle}
          condensed noDataIndication="Table is Empty/Loading" wrapperClasses={wrapperClasses}
          />
        <p/>
        <CollapsibleNote getScreenGuide={HNotes.getPoolNote} />
        {HUtils.getSupportUs()}
        {specialMessage}
        <Contact />
      </div>
    );
  }

  // <td className="view-tag"><a href={"/validators/AllEligible"}>{this.formatView("All elig " + (this.state.statusSummary.Elected + this.state.statusSummary.Eligible), "AllEligible")}</a> </td>

  renderStatusTags() {
    if (this.state.isLoading) return "";
    // <td className="view-tag"><a href={"/validators/All"}>{this.formatView("All " + this.state.statusSummary.Total, "All")}</a> </td>
    // <td className="view-tag"><a href={"/validators/All"}>{this.formatView("All - " + this.state.statusSummary.Total, "All")}</a> </td>
    // console.log(RespUtils.isMobileView());
    if (RespUtils.isMobileView()) {
      return (<div><table><tbody><tr>
          <td className="view-tag"><a className="white-a" href={"/validators/AllEligible"}>{this.formatView("All ", (this.state.statusSummary.Elected + (this.state.statusSummary.Eligible?this.state.statusSummary.Eligible:0)), "AllEligible")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/Elected"}>{this.formatView("Ele ", this.state.statusSummary.Elected, "Elected")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/Eligible"}>{this.formatView("Eli ", this.state.statusSummary.Eligible, "Eligible")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/NotEligible"}>{this.formatView("Not eli ", this.state.statusSummary.NotEligible, "NotEligible")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/FeeIncrease"}>{this.formatView("Fee+ ", this.state.statusSummary.FeeIncrease, "FeeIncrease")}</a> </td>
        </tr></tbody></table></div>);
    } else {
      return (<div><table><tbody><tr>
          <td className="view-tag"><a className="white-a" href={"/validators/AllEligible"}>{this.formatView("All Eligible ", (this.state.statusSummary.Elected + (this.state.statusSummary.Eligible?this.state.statusSummary.Eligible:0)), "AllEligible")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/Elected"}>{this.formatView("Elected ", this.state.statusSummary.Elected, "Elected")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/Eligible"}>{this.formatView("Eligible ", this.state.statusSummary.Eligible, "Eligible")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/FeeIncrease"}>{this.formatView("Fee Increase ", this.state.statusSummary.FeeIncrease, "FeeIncrease")}</a> </td>
          <td className="view-tag"><a className="white-a" href={"/validators/NotEligible"}>{this.formatView("Not Eligible ", this.state.statusSummary.NotEligible, "NotEligible")}</a> </td>
        </tr></tbody></table></div>);
    }
  }

  formatView(label, count, status) {
    if (count != null) {
      label = label + count;
    } else {
      label = label + "0";
    }

    // console.log("in formatView for: ", label, status);
    if (this.props.match && this.props.match.params.status) {
      if (this.props.match.params.status == status) {
        // console.log("status matched: ", this.props.match.params.status, status);
        return <b><u>{label}</u></b>
      } else {
        return label;
      }
    } else if (status == "Elected") {
      // console.log("returning from AllEligible");
      return <b><u>{label}</u></b>
    } else if (status != null) {
      // console.log("returning from status not null");
      return label;
    }

    // console.log("returning from end");
    return <b><u>{label}</u></b>
  }

  reload() {
    window.location = "/";
  }
}

export default Validators;
