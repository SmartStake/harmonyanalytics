import React from 'react';

import ApiUtils from '../util/ApiUtils';
import Utilities from "../util/Utilities";
import SPUtilities from "../util/SPUtilities";
import UIUtils from "../util/UIUtils";
import AddressUtils from "../util/AddressUtils";

import ErrorMessageBox from "../components/ErrorMessageBox";
import CollapsibleNote from "../base/CollapsibleNote";

import HNotes from "../harmony/HNotes";
import AddressFilterUtils from "./AddressFilterUtils";
import AddressHeader from './AddressHeader';
import AddressInline from './AddressInline';
import Views from "./Views";
import FilterAddress from "./FilterAddress";

// import RewardComparison from '../reports/RewardComparison';

class MyAccount extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      filterState: {
        address: "",
        alias: "",
      },
      showFilter: true,
      delegations: [],
      smartStake: null,
      events: [],
      rewards: [],
      stakeHistory: [],
      addressDetails: {},
      coinStats: {},
      width: window.innerWidth,
      lastUpdatedGap: null,

      showView: true,
      responsive: true,
      size: 10,
    }
    this.filterData = this.filterData.bind(this);
    this.saveAlias = this.saveAlias.bind(this);
    this.addView = this.addView.bind(this);
    this.updateDimensions = this.updateDimensions.bind(this);
    this.switchFilter = this.switchFilter.bind(this);
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

    let filterState = AddressFilterUtils.getFilterState(this);
    // console.log("componentDidMount - filterState is: ", filterState);
    this.setState({filterState: filterState});

    if (filterState.address.length != 0 || (filterState.alias != null && filterState.alias != "")) {
      this.setState({showFilter: false});
      this.loadData(filterState);
    }

    this.setState({isLoading: false});
  }

  switchFilter() {
    let showFilter = !this.state.showFilter;
    this.setState({showFilter: showFilter});
  }

  async filterData() {
    await this.loadData(this.state.filterState);
  }

  async saveAlias() {
    await AddressFilterUtils.saveAlias(this);
  }

  onAliasChange = (value) => {
    // console.log(value);
    AddressFilterUtils.onAliasChange(this, value);
  }

  onAddressSelect = (value) => {
    // console.log("onAddressSelect = " + value);
    AddressFilterUtils.onAddressChange(this, value);
    // AddressFilterUtils.updateFilterState("address", value, this);
    // Utilities.updateFilterState("address", Utilities.toLowerCaseArray(value), this);
  }
  // <h5 style={{align: "center"}}><span><strong>My Account</strong></span>
  // {UIUtils.renderPageActions(this, false, false)}</h5>

  async loadData(filterState) {
    this.setState({showView: false, error: null});
    // console.log("loadData - in load data: ", filterState);

    let finalUrl = AddressFilterUtils.getBackendUrl(this, filterState, "listData?type=addressDetails&subType=myAccount");
    // console.log("loadData - my account: in loadData: finalUrl - ", finalUrl);
    const allData = await ApiUtils.get(finalUrl);
    // console.log("loadData - address response is:");
    // console.log(data);
    //
    // var address = SPUtilities.getAddress(this);
    // console.log("componentDidMount - after address: ", address);
    //
    // const allData = await ApiUtils.get("listData?type=addressDetails&address=" + address);
    // console.log("allData is:", allData);
    // console.log((allData["error"] != null));
    // console.log(allData["error"]);

    if (allData["error"] != null) {
      // alert(allData["error"]);
      this.setState({error: allData["error"]});
    } else if (allData) {
      this.setState({delegations: Utilities.addIndex(allData["delegations"]),
        addressDetails: allData["addressDetails"], rewards: allData["rewards"],
        lastUpdatedGap: allData["lastUpdated"], stakeHistory: allData["stakeHistory"],
        coinStats: allData["coinStats"], events: Utilities.addIndex(allData["events"]),
        smartStake: allData["smartStake"], isLoading: false});
    }

    // console.log("calling saveLastCriteria with filterState: ", filterState)
    AddressFilterUtils.saveLastCriteria(filterState);
    if (filterState.alias != undefined && filterState.alias != "") {
      AddressFilterUtils.saveLocally(filterState.alias);
    }

    this.timeout = setTimeout(() => {
        this.setState({showView: true});
      }, 300);
  }

  addView() {
    if (this.state.showView) {
      return <Views viewType="account" smartStake={this.state.smartStake} />
    }
    return "";
  }

  render() {
    // window.localStorage.removeItem("alias");
    // window.localStorage.removeItem("lastAlias");
    // window.localStorage.removeItem("lastAddress");
    if (this.state.isLoading) {
      return <div>Loading</div>;
    }

    return (<div>
        {AddressUtils.getBreadCrumb()}

        {this.state.error != null && (<ErrorMessageBox message={this.state.error} />)}
        <FilterAddress filterData={this.filterData} filterState={this.state.filterState}
          onAddressSelect ={this.onAddressSelect} saveAlias ={this.saveAlias}
          onAliasChange ={this.onAliasChange} showFilter={this.state.showFilter} switchFilter={this.switchFilter} />
        {this.addView()}
        {SPUtilities.getLastUpdatedGap(this.state.lastUpdatedGap)}
        {!this.state.addressDetails && (<p><br/><b><span>No address found</span></b></p>)}
        {this.state.addressDetails && (<AddressInline addressDetails={this.state.addressDetails} delegations={this.state.delegations}
          lastUpdatedGap={this.state.lastUpdatedGap} events={this.state.events} stakeHistory={this.state.stakeHistory}
          coinStats={this.state.coinStats} rewards={this.state.rewards}/>)}
        <CollapsibleNote getScreenGuide={HNotes.getFilterHelp} />
      </div>
    );
  }

}

export default MyAccount;
