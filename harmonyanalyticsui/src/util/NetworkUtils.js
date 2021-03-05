import React from 'react';

import config from '../config';

class NetworkUtils extends React.Component {
  static keys = {network: "network",};

  static switchNetwork(e) {
    e.preventDefault();
    // window.localStorage.removeItem(FavUtils.getFavPoolsKey());
    console.log("in favourite: " + e.target.id);
    let newNetwork = e.target.value;
    console.log("switching to: ", newNetwork);

    // let networkObject = window.localStorage.getItem(NetworkUtils.keys.network);
    window.localStorage.setItem(NetworkUtils.keys.network, newNetwork);
    console.log(window.localStorage.getItem(NetworkUtils.keys.network))
    // console.log("favourite - favs: " + window.localStorage.getItem(FavUtils.getFavPoolsKey()));
    window.location.reload();
  }

  static isDevnet() {
    return NetworkUtils.isNetwork(config.apiGatewayDevnet.NETWORK);
  }

  static isTestnet() {
    return NetworkUtils.isNetwork(config.apiGatewayTestnet.NETWORK);
  }

  static isMainnet() {
    return NetworkUtils.isNetwork(config.apiGatewayMainnet.NETWORK);
  }

  static isNetwork(networkType) {
    // console.log("isNetwork: ", networkType);
    let networkObject = window.localStorage.getItem(NetworkUtils.keys.network);
    // console.log("networkObject: ", networkObject);
    // console.log(typeof networkObject);

    if (networkObject === undefined || networkObject === "undefined") {
      // console.log("in if clause");
      networkObject = config.apiGatewayMainnet.NETWORK;
      window.localStorage.setItem(NetworkUtils.keys.network, networkObject);
    }

    // console.log("checking networkType === networkObject: ", (networkType === networkObject));
    return networkType === networkObject;
  }

  static getGaId() {
    let configDetails = NetworkUtils.getNetworkSettings()
    return configDetails.GA_ID
  }

  static getEndpoint() {
    let configDetails = NetworkUtils.getNetworkSettings()
    return configDetails.NETWORK;
  }

  static isDefaultPool(hPoolId) {
    return (hPoolId === NetworkUtils.getDefaultPool());
  }

  static getDefaultPool() {
    let configDetails = NetworkUtils.getNetworkSettings()
    return configDetails.DEFAULT_POOL_ID;
  }

  static getCurrentNetwork() {
    let configDetails = NetworkUtils.getNetworkSettings()
    return configDetails.NETWORK;
  }

  static getNetworks() {
    return config.networks;
  }

  static getNetworkSettings() {
    if (NetworkUtils.isMainnet()) {
      return config.apiGatewayMainnet;
    } else if (NetworkUtils.isTestnet()) {
      return config.apiGatewayTestnet;
    } else if (NetworkUtils.isDevnet()) {
      return config.apiGatewayDevnet;
    } else {
      //should never happen but just in case it does, return mainnet
      console.log("couldnt figure out network")
      return config.apiGatewayMainnet;
    }
  }

  static getElectionUrl() {
    let configDetails = NetworkUtils.getNetworkSettings()
    return configDetails.ELECTION_URL;
  }

}

export default NetworkUtils;
