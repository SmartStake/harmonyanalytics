import React from 'react';
import {CopyToClipboard} from 'react-copy-to-clipboard';

import config from '../config';
import constants from "../constants";

import ApiUtils from '../util/ApiUtils';
import RespUtils from '../util/RespUtils';
import SPUtilities from '../util/SPUtilities';
import SPCalc from '../util/SPCalc';
import Utilities from "../util/Utilities";

class AddressFilterUtils extends React.Component {
  static getFilterState(thisObj) {
    // console.log("in getFilterState: ", thisObj.props);
    var address = thisObj.props.match.params.address;
    //console.log("getFilterState - address from url: ", address);
    if (address != undefined) {
      let params = {address: address, alias: ""};
      // let params = {address: [], alias: ""};
      // params.address[0] = address;
      //console.log("getFilterState - params: ", params);
      return params;
    }

    //console.log("getFilterState - not returning here")
    let params = {}
    if (thisObj.props && thisObj.props.location) {
      //console.log("getFilterState - calling parse params")
      params = Utilities.parseParams(thisObj)
      //console.log("getFilterState - after calling parse params: ", params)
      if (params.alias != undefined || params.address != undefined) {
        if (params.address == undefined) {
          params.address = "";
          // params.address = [];
        }
        //console.log("getFilterState - returning params: ", params)
        return params;
      }
    }

    if (params.clear === "true") {
      window.localStorage.removeItem("alias");
    }

    //console.log("params are : ", params);
    // if (Utilities.isEmpty(params)) {
    // alert(params.address);
    if (params.address == null) {
      //console.log("getFilterState - params are empty. setting to default");
      // if params are empty, load the last criteria
      params = AddressFilterUtils.initParamsFromStorage();
    } else {
      // let aliasData = params.alias;
      if (!Array.isArray(params.address)) {
        params.address = AddressFilterUtils.getParamAddress(params.address);
      }
    }

    //console.log("getFilterState - final params: ", params)
    return params;
  }

  static getParamAddress(inputAddress) {
      // console.log("address is array, no need to do anything");
    // } else {
    let address = inputAddress;
    // console.log("params.address: before: ");
    // console.log(address);
    // if (address.indexOf(",") == -1) {
    //   address = [address];
    // } else {
    //   address = address.split(",");
    // }
    //console.log("params.address: after: ");
    //console.log(address);
    return address;
  }

  static initParamsFromStorage() {
    // console.log("initParamsFromStorage - in method");
    let params = {address: "", alias: ""};
    // let params = {address: [], alias: ""};

    let lastAlias = window.localStorage.getItem("lastAlias");
    //console.log("lastAlias: ", lastAlias);
    if (lastAlias != null) {
      params.alias = lastAlias;
    }

    let lastAddress = window.localStorage.getItem("lastAddress");
    // console.log("lastAddress: ", lastAddress);
    if (lastAddress != null) {
      params.address = AddressFilterUtils.getParamAddress(lastAddress);
    }

    // console.log("initParamsFromStorage - params are: ", params);
    return params;
  }

  static saveLastCriteria(fs) {
    let alias = fs.alias;
    let address = fs.address;

    // console.log("in saveLastCriteria: ", fs);
    if (alias == undefined || alias == null || alias == "" || typeof alias == "undefined") {
      // console.log("removing last alias");
      window.localStorage.removeItem("lastAlias");
    } else {
      // console.log("setting last alias: ", alias);
      window.localStorage.setItem("lastAlias", alias);
    }

    if (address == undefined || address == null || address == "" || typeof address == "undefined") {
      // console.log("removing last address");
      window.localStorage.removeItem("lastAddress");
    } else {
      // console.log("setting last address: ", address);
      window.localStorage.setItem("lastAddress", address);
    }
  }

  static saveLocally(alias) {
    let aliases = window.localStorage.getItem("alias");
    if (aliases == undefined || aliases == null || aliases == "" || typeof aliases == "undefined") {
      aliases = alias
      // aliases = ;
    } else {
      let temp = aliases.split(",");
      for(var i = 0; i < temp.length; i++) {
          if (temp[i] == alias) {
              return;
          }
      }

      aliases += "," + alias;
      //) += "," +
    }
    // console.log("saveLocally: ", aliases)
    window.localStorage.setItem("alias", aliases);
    // console.log(window.localStorage.getItem("alias"))
  }


  static async saveAlias(thisObj) {
    // console.log("in save alias");
    let aliasDetails = {alias: thisObj.state.filterState.alias, address: thisObj.state.filterState.address};
    // console.log("alias details: ", aliasDetails);
    await ApiUtils.post("harmonyUpdateData?type=saveAlias", {type: "saveAlias", data: {alias: aliasDetails}}, "An error occurred").then(response => {
      // console.log(response);
      if (response["result"] != undefined && response["result"] != "successful") {
        alert(response["result"]);
      }
    }).catch(function(error) {
       console.log("error received is: ", error);
    });
  }

  static onAliasChange(thisObj, value) {
    let alias = value.target.value;

    if (alias != null) {
      alias = alias.toLowerCase();
    }
    // console.log("onAliasChange: value is: ", alias);
    AddressFilterUtils.updateFilterState("alias", alias, thisObj)
  }

  static onAddressChange(thisObj, value) {
    let address = value.target.value;

    // console.log("onAliasChange: value is: ", alias);
    AddressFilterUtils.updateFilterState("address", address, thisObj)
  }


  static getBackendUrl(thisObj, filterState, baseUrl) {
    //console.log("getRewardsUrl - : ", filterState);
    let url = baseUrl;

    let params = "";
    let found = false;

    if (thisObj.state.showHistory) {
      params = "&showHistory=True";
      found = true;
    }

    if (typeof filterState.address != 'undefined' && filterState.address != '') {
      params += "&address=" + filterState.address;
      found = true;
    }

    if (typeof filterState.alias != 'undefined' && filterState.alias != '') {
      params += "&alias=" + filterState.alias;
      found = true;
    }

    // if (typeof filterState.showCompletedItems != 'undefined' && filterState.showCompletedItems != '') {
    //   params += "&showCompletedItems=" + filterState.showCompletedItems;
    //   found = true;
    // }

    let finalUrl = url;
    if(found) {
      finalUrl += params;
    }

    //console.log("filterState - url is: ", finalUrl);
    return finalUrl;
  }

  static updateFilterState(key, value, callerObj) {
    // console.log("in updateFilterState before: ", callerObj.state.filterState);
    // console.log("key: ", key, ", value: ", value);
    // console.log(value);
    let filterState=callerObj.state.filterState;
    filterState[key] =  value;
    callerObj.setState({filterState: filterState});
    // console.log("in updateFilterState filterState: ", filterState);
    // console.log("in updateFilterState after: ", callerObj.state.filterState);
  }


}

export default AddressFilterUtils;
