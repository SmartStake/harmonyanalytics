import React from 'react';

import ApiUtils from './ApiUtils';

class Cache extends React.Component {
  static EXPIRY_TIME = 3600000;
  static TIME_KEY = "Time";

  static listCodes(category) {
    let data = Cache.getCachedSessionData(category);
    console.log("returned data from cache is: ");
    console.log(data);

    if (data === null) {
      data = ApiUtils.get("listCodes?codeType=" + category).then(response => {
        console.log("setting cached data to: ");
        console.log(response);
        Cache.setCachedSessionData(category, response)
      });

      // data = ApiUtils.get("listCodes?codeType=" + category);
      // Cache.setCachedSessionData(category, data);
      console.log("returned data from backend is: ");
      console.log(data);
    }

    return data;
  }

  static getCachedSessionData(key) {
    let data = sessionStorage.getItem(key);
    console.log("cached data is: ");
    console.log(data);

    if (data === '' || data == null) {
      console.log("returning data from empty clause")
      return null;
    }

    let cacheTime = sessionStorage.getItem(key + Cache.TIME_KEY);
    if (cacheTime < Date.now() + Cache.EXPIRY_TIME) {
      console.log("returning data from expiry clause")
      return null;
    }

    let parsedData = JSON.parse(data);

    console.log("cached data after parsing is: ");
    console.log(parsedData);
    return parsedData
  }

  static setCachedSessionData(key, data) {
    sessionStorage.setItem(key, JSON.stringify(data));
    sessionStorage.setItem(key + Cache.TIME_KEY, Date.now());
  }

  static setUserData(data) {
    console.log(" in setUserData:")
    console.log(data)
    sessionStorage.setItem('userDetails', JSON.stringify(data));
    sessionStorage.setItem('userid', data.userid);
  }
}

export default Cache;
