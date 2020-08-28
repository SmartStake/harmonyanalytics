import { API} from 'aws-amplify';
import React from 'react';

import config from '../config';

class ApiUtils extends React.Component {
  static errorMsg = "The website is not available to process your request at this time. Please contact website operator.";
  static errorMsgProc = "The website is having difficulty in processing your request at this time. Please contact website operator.";

  static async get(url) {
    window.localStorage.removeItem("DENIED");
    // console.log("window.location.href: " + window.location.href);
    let data = "";
    try {
      if(!ApiUtils.checkAccess()) {
        return;
      }
      // console.log("in api get data util method. calling get url: " + url);
      data =  await API.get('stakingService', ApiUtils.addKey(url));
      if(!ApiUtils.processAccess(data)) {
        return null;
      }
    } catch (e) {
      console.log(url + " - call failed. error is: " + e);
      console.log(e);
      // alert(e);
    }

    return data;
  }

  static async post(url, postDataObj, error) {
    let data = "";
    try {
      if(!ApiUtils.checkAccess()) {
        return;
      }

      // console.log("in api post data util method. calling post url: " + url);
      data = await API.post('stakingService', ApiUtils.addKey(url), {
        body: postDataObj
      });

      if(!ApiUtils.processAccess(data)) {
        return null;
      }
    } catch (e) {
      console.log(url + " - call failed. error is: " + e);
      console.log(e);
      // alert(error);
    }

    return data;
  }

  static addKey(url) {
    let separator = (url.indexOf("?") != -1) ? "&" : "?";
    const token = Math.round(new Date().getTime() / 1000);
    let finalUrl = url + separator + "key=" + config.apiGateway.KEY;
    finalUrl += "&token=" + token + "&app=" + config.apiGateway.APP;
    // console.log("url is: ", finalUrl);
    return finalUrl;
  }

  static checkAccess() {
    let access = window.localStorage.getItem("DENIED");
    // console.log("in checkAccess: " + access);

    if (!access) {
      return true
    }

    // console.log("access object is: " + access);
    let allowedAccess = parseInt(access) + 60 * 60 * 1000;
    // console.log(allowedAccess);
    if (allowedAccess > new Date().getTime()) {
      alert(ApiUtils.errorMsg);
      return false;
    }
    window.localStorage.removeItem("DENIED");
    return true;
  }

  static removeAccess() {
    // console.log(new Date());
    window.localStorage.setItem("DENIED", new Date().getTime());
  }

  static addMinutes(dateObj, minutes) {
    return dateObj.setHours(dateObj.getMinutes() + minutes);
  }

  static processAccess(data) {
    // console.log("response is: ");
    // console.log(data);
    if (data && data["errors"] && "DENIED" == data["errors"]) {
      ApiUtils.removeAccess();
      alert(ApiUtils.errorMsgProc);
      return false;
    }
    return true;
  }

}

export default ApiUtils;
