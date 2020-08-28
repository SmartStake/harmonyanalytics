import React from 'react';
import numeral from 'numeral';

import SPCalc from './SPCalc';
import config from '../config';
import RespUtils from './RespUtils'

class SPUtilities extends React.Component {
  static btcFormatter(cell, row) {
    return cell;
  }

  static btcValueFormatter(cell, row) {
    if (!cell) {
      return cell;
    }

    return Number(cell).toPrecision(4);
  }

  static usdFormatter(cell, row) {
    if (!cell) {
      return cell;
    }
    return Number(cell).toPrecision(2);
  }

  static percentFormatter(cell, row) {
    if (!cell) {
      return cell;
    }

    if (cell > 0) {
      return (<font color="green">{cell + "%"}</font>);
    } else {
      return (<font color="red">{cell + "%"}</font>);
    }
  }

  static moneyFormatter(amount) {
    return SPUtilities.moneyFormatterPrecision(amount, 3);
  }

  static moneyFormatterPrecision(amount, precision) {
      // Nine Zeroes for Billions
      return Math.abs(Number(amount)) >= 1.0e+9
        ? Number(Math.abs(Number(amount)) / 1.0e+9).toPrecision(precision) + "B"
        // Six Zeroes for Millions
        : Math.abs(Number(amount)) >= 1.0e+6
        ? Number(Math.abs(Number(amount)) / 1.0e+6).toPrecision(precision) + "M"
        // Three Zeroes for Thousands
        : Math.abs(Number(amount)) >= 1.0e+3
        ? Number(Math.abs(Number(amount)) / 1.0e+3).toPrecision(precision) + "K"
        : Number(Math.abs(Number(amount))).toPrecision(precision);
  }

  static moneyFormatterRounded(amount, decimals) {
      // Nine Zeroes for Billions
      return Math.abs(Number(amount)) >= 1.0e+9
        ? Number(Math.abs(Number(amount)) / 1.0e+9).toFixed(decimals)
        // Six Zeroes for Millions
        : Math.abs(Number(amount)) >= 1.0e+6
        ? Number(Math.abs(Number(amount)) / 1.0e+6).toFixed(decimals)
        // Three Zeroes for Thousands
        : Math.abs(Number(amount)) >= 1.0e+3
        ? Number(Math.abs(Number(amount)) / 1.0e+3).toFixed(decimals)
        : Number(Math.abs(Number(amount))).toFixed(decimals);
  }

  static stakeFormatterRounded(cell, row) {
    if (!cell) {
      return cell;
    }

    // return SPUtilities.moneyFormatterPrecision(cell, 3);
    return numeral(cell).format('0.0a');
  }

  static stakeFormatterBySize(cell, row) {
    if (!cell) {
      return cell;
    }

    if(RespUtils.isMobileView()) {
      return numeral(cell).format('0.0a');
    } else {
      return cell;
    }

    // return SPUtilities.moneyFormatterPrecision(cell, 3);
    return numeral(cell).format('0.0a');
  }

  static stakeFormatterDecimal(value) {
    if (!value) {
      return value;
    }

    // return SPUtilities.moneyFormatterPrecision(cell, 3);
    return numeral(value).format('0[.]00000');
  }

  static moneyFormatterDesc(amount) {
      // Nine Zeroes for Billions
      return Math.abs(Number(amount)) >= 1.0e+9
        ? Number(Math.abs(Number(amount)) / 1.0e+9).toPrecision(3) + " Billion"
        // Six Zeroes for Millions
        : Math.abs(Number(amount)) >= 1.0e+6
        ? Number(Math.abs(Number(amount)) / 1.0e+6).toPrecision(3) + " Million"
        // Three Zeroes for Thousands
        : Math.abs(Number(amount)) >= 1.0e+3
        ? Number(Math.abs(Number(amount)) / 1.0e+3).toPrecision(3) + " Thousand"
        : Number(Math.abs(Number(amount))).toPrecision(3);
  }

  /*
  static numberFormatter(numericValue) {
      // Nine Zeroes for Billions
      return Math.abs(Number(numericValue)) >= 1.0e+9
        ? Number(Math.abs(Number(numericValue)) / 1.0e+9).toPrecision(2) + "B"
        // Six Zeroes for Millions
        : Math.abs(Number(numericValue)) >= 1.0e+6
        ? Number(Math.abs(Number(numericValue)) / 1.0e+6).toPrecision(2) + "M"
        // Three Zeroes for Thousands
        : Math.abs(Number(numericValue)) >= 1.0e+3
        ? Number(Math.abs(Number(numericValue)) / 1.0e+3).toPrecision(3) + "K"
        : Number(Math.abs(Number(numericValue))).toPrecision(3);
  }*/

  static getDateAsText(date) {
    let currentMonth = SPUtilities.getTwoDigitValue(date.getMonth() + 1);
    let currentDay = SPUtilities.getTwoDigitValue(date.getDate());

    return date.getFullYear() + '-' + currentMonth + '-' + currentDay;

  }

  static getTwoDigitValue(val) {
    let newVal = val;
    if (val < 10) {
      newVal = "0" + val;
    }

    return newVal;
  }

  static getDateTimeAsText(dateValue) {
    let dateTimeVal = SPUtilities.getDateAsText(dateValue);
    dateTimeVal += " " + SPUtilities.getTwoDigitValue(dateValue.getHours());
    dateTimeVal += ":" + SPUtilities.getTwoDigitValue(dateValue.getMinutes());

    return dateTimeVal;
  }

  static coinCountCellFormatter(cell, row) {
    if (!cell) {
      return cell;
    }

    return SPCalc.formatCoinCount(cell);
  }

  static hashFormatterArray(arr) {
    if (!arr) {
      return arr;
    }

    var label = "";
    for (let i = 0; i < arr.length; i++) {
      let value = arr[i];

      if (label != "") {
        label += ", ";
      }

      if (window.innerWidth < 1000 && value.length > 10) {
        label += value.substring(0,5) + ".." + value.substring(value.length - 2, value.length);
      } else {
        label += value;
      }
    }

    return label;
  }

  static addressShortFormatterVisibleLink(value) {
    return SPUtilities.formatAddressLink(value, true, true, null, "black-a")
  }

  static addressReallyShortFormatterVisibleLink(value) {
    return SPUtilities.formatAddressLink(value, true, true, null, "black-a", true)
  }

  static addressShortFormatter(value) {
    return SPUtilities.formatAddressLink(value, true, true)
  }

  static addressFormatter(value) {
    return SPUtilities.formatAddressLink(value, false, true)
  }

  static addressFormatterNoLink(value, row, rowIndex) {
    // console.log(row);
    if (row.label != undefined) {
      return SPUtilities.formatAddressLink(value, false, false, row.label)
    } else if (row.alias == undefined) {
      return SPUtilities.formatAddressLink(value, false, false, row.alias)
    } else {
      return SPUtilities.formatAddressLink(value, false, false)
    }
  }

  static formatAddress(value, short) {
    return SPUtilities.formatAddressLink(value, short, true)
  }

  static formatAddressShortLinkOptions(value, short, link) {
    return SPUtilities.formatAddressLink(value, short, link)
  }

  static addressLabelFormatter(value, row, rowIndex) {
    return SPUtilities.addressLabelShortFormatter(value, row, false);
  }

  static addressLabelShortFormatter(value, row, short) {
    if (!value) {
      return value;
    }

    let label = value;
    if (short || (window.innerWidth < 1400 && value.length > 30)) {
      label = value.substring(0,5) + ". ." + value.substring(value.length - 5, value.length);
    }

    return label;
  }

  static multiAddressSimpleFormatter(value) {
    if (!value) {
      return value;
    }

    return value.split(",").join(", ");
  }

  static multiAddressFormatter(value) {
    if (!value) {
      return value;
    }

    let values = value.split(",");
    // console.log("values: " + values);
    let formattedValues = "";
    for(let i=0; i < values.length; i++) {
      if (i != 0) {
        formattedValues += ", ";
      }
      formattedValues += SPUtilities.formatAddressLink(values[i], false, false);
    }

    // console.log("formattedValues: " + formattedValues);
    return formattedValues;
  }

  static formatAddressLink(value, short, link, alias, className, reallyShort) {
    if (!value) {
      return value;
    }

    if (!className) {
      className = "regular-b-a";
    }

    let label = alias;
    let length = reallyShort ? 2 : 5
    if (label == undefined) {
      label = value;
      if (short || (window.innerWidth < 1400 && value.length > 10)) {
        label = value.substring(0,length) + ". ." + value.substring(value.length - length, value.length);
      }
    }

    if (link) {
      return (<a href={"/address/" + value}
        class={className}>{label}</a>);
    } else {
      return label;
    }
  }

  static delegateLink(value) {
    // console.log(value);
    if (!value) {
      return value;
    }

    return (<a href={"/delegate/" + value}
      class="black-a">{value}</a>);
  }

  static delegateLinks(value) {
    // console.log(value);
    if (!value) {
      return value;
    }

    let links = "";
    let values = value.split(",");

    if (values.length < 1) return value;

    // for(let i=0; i < values.length; i++) {
    //   let v = values[i];
    //   v = v.trim();
    //
    //   links += SPUtilities.delegateLink(v);
    //   // "<a href='/delegate/" + v + "' class='black-a'>" + v + "</a>&nbsp;"
    // }
    //
    // console.log(links);
    if (values.length == 1) {
      return SPUtilities.delegateLink(values[0]);
    } else if (values.length == 2) {
      return (<span>{SPUtilities.delegateLink(values[0])}&nbsp;
        {SPUtilities.delegateLink(values[1])}&nbsp;</span>);
    } else if (values.length == 3) {
      return (<span>{SPUtilities.delegateLink(values[0])}&nbsp;
        {SPUtilities.delegateLink(values[1])}&nbsp;
        {SPUtilities.delegateLink(values[2])}&nbsp;</span>);
    }

    return SPUtilities.delegateLink(values[0]);
  }

  static rewardsLink(value) {
    if (!value) {
      return value;
    }

    return (<a href={"/rewards/" + value} class="black-a">Rewards Details</a>);
  }

  static getPoolId(thisObj) {
    let poolId;

    if (thisObj.props.match) {
      poolId = thisObj.props.match.params.poolId;
    }

    if (!poolId && thisObj.props.poolId) {
      poolId = thisObj.props.poolId;
    }

    if (!poolId) {
      poolId = config.apiGateway.DEFAULT_POOL_ID;
    }

    return poolId;
  }

  static getPoolIdNoDef(thisObj) {
    let poolId = null;

    if (thisObj.props.match) {
      poolId = thisObj.props.match.params.poolId;
    }

    if (!poolId && thisObj.props.poolId) {
      poolId = thisObj.props.poolId;
    }

    return poolId;
  }


  static getAddress(thisObj) {
    let address = null;

    if (thisObj.props.match) {
      address = thisObj.props.match.params.address;
    }

    if (!address && thisObj.props.address) {
      address = thisObj.props.address;
    }

    return address;
  }

  static getUrl(url) {
    if (url && url.toLowerCase().indexOf("https") != 0) {
      url = "https://" + url;
    }
    return url;
  }

  static percentFormatter(cell, row) {
    if (!cell) {
      return cell;
    }
    return cell + "%";
  }

  static epochFormatter(cell, row) {
    if (!cell) {
      return cell;
    }

    return SPUtilities.epochFormatter(cell);
  }

  static epochFormatter(value) {
    // console.log(value);
    if (value == undefined || value == null || value == 0) {
      return "";
    }

    var d = new Date(0); // The 0 there is the key, which sets the date to the epoch
    d.setUTCSeconds(value);

    return SPUtilities.formatDateTime(d);
  }

  static formatDateTime(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    var ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    seconds = seconds < 10 ? '0'+ seconds : seconds;
    var strTime = hours + ':' + minutes + ':' + seconds + ' ' + ampm;
    return date.getMonth()+1 + "/" + date.getDate() + "/" + date.getFullYear() + "  " + strTime;
  }

  static refresh() {
     // if(new Date().getTime() - time >= 60000)
     window.location.reload(true);
     // else
     //     setTimeout(refresh, 10000);
   }

  static indexFormatter(cell, row, rowIndex) {
    if (!cell) {
      return cell;
    }

    return rowIndex + 1;
  }

  static csvFormatter(cell, row, rowIndex) {
    if (!cell) {
      return cell;
    }

    return cell.split(",").sort().join(", ");
  }

  static getLastUpdated(thisObj, addBotLink) {
    let lastUpdated = thisObj.state.lastUpdated ? (thisObj.state.lastUpdated/60).toFixed(0) : "N/A";

    return (<p>Last updated - <b>{lastUpdated}</b> minutes ago. {SPUtilities.getBotLink(addBotLink)}</p>);
  }

  static getBotLink(addBotLink) {
    if (!addBotLink) {
      return "";
    }
    return (<span>Try our telegram bot <a className='black-a' href='/tgBot'>SmartStakeBot</a>.</span>);
  }

  static getLastUpdatedGap(value) {
    let lastUpdated = value ? (value/60).toFixed(0) : "N/A";
    return (<span>Last updated - <b>{lastUpdated}</b> minutes ago.<br/></span>);
  }

  static getLastUpdatedFromEpoch(epochTime) {
    return SPUtilities.epochFormatter(epochTime);
  }

  static feeFormatter(cell, row, rowIndex, formatExtraData) {
    if (!cell) {
      return cell;
    }
    // console.log("getting fee: ", cell, row.feeChange);
    return SPCalc.getFee(cell, row.feeChange);
  }

  static getPoolName(poolName, poolId) {
    if (!poolName) {
      return "";
    }

    return (<a className="black-a" href={"/pool/" + poolId}>{poolName}</a>);
  }

  static eventTypeFormatter(cell, row, rowIndex, formatExtraData) {
    // console.log(cell);
    if (!cell) {
      return cell;
    }

    var link = "/networkEvents/";
    if (formatExtraData.state.pool && formatExtraData.state.pool.poolId) {
      link = "/events/" + formatExtraData.state.pool.poolId + "/";
    }
    link += row.eventType;

    // console.log("link - ", link);
    return (<a className="black-a" href={link}>{cell}</a>);
  }

  static reload() {
    window.location.reload();
  }

  static formatBtcPrice(btcPrice) {
    return Number(btcPrice).toFixed(8).replace(/\.?0+$/,"");
  }
}

export default SPUtilities;
