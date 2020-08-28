import React from 'react';
import qs from 'qs';

class Utilities extends React.Component {

  static width(value) {
    // console.log({ width: "" + value, textAlign: 'left' });
    return { width: value + "%", textAlign: 'left' };
  }

  static getLastUpdatedLabel(data, key) {
    var date = Utilities.getLastUpdatedDate(data, key);

    if (date == null) {
      return "";
    }

    return date;
  }

  static getLastUpdatedDate(data, key) {
    if (!data) {
      return "";
    }

    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
      if (data[i][key] != null) {
        return data[i][key];
      }
    }

    return null;
  }

  static getFirstRecordAttribute(data, key) {
    if (!data) {
      return "";
    }

    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
      if (data[i][key] != null) {
        // console.log(i + " - returning : " + key + " - " + data[i][key]);
        return data[i][key];
      }
    }

    return null;
  }

  static getMaxValueForAttribute(data, key) {
    if (!data) {
      return "";
    }

    let maxValue = 0;
    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
      if (data[i][key] != null && !isNaN(data[i][key]) ) {
        // console.log(i + " - returning : " + key + " - " + data[i][key]);
        let value = parseInt(data[i][key]);
        if (value > maxValue) {
          maxValue = value;
        }
      }
    }

    return maxValue;
  }

  static getMinValueForAttribute(data, key) {
    if (!data) {
      return "";
    }

    let minValue = 0;
    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
      if (data[i][key] != null && !isNaN(data[i][key]) ) {
        // console.log(i + " - returning : " + key + " - " + data[i][key]);
        let value = parseInt(data[i][key]);
        if (value < minValue) {
          minValue = value;
        }
      }
    }

    return minValue;
  }

  static percentFormatter(cell, row) {
    if (!cell) {
      if (cell != 0) {
        return cell;
      }
    }

    return (<font>{cell + "%"}</font>);
  }

  static getTotalAmount(data, key, label) {
    return Utilities.getTotalAmountWithLabel(data, key, "Total Amount");
  }

  static getTotalWithLabel(data, key, label, precisionInd) {
    // console.log("getTotalAmountWithLabel - data is: ");
    // console.log(data);
    // console.log(key);
    // console.log(label);
    if (!data) {
      return label + ": " + 0;
    }

    let totalAmount = 0;
    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
      if (!isNaN(data[i][key])) {
        totalAmount += parseFloat(data[i][key]);
      }
    }

    if (precisionInd) {
      totalAmount = totalAmount.toFixed(2);
    }

    // console.log("total amount is: " + totalAmount);
    return label + ": " + totalAmount;
  }

  static getParams(month, year, expenseCategory, paymentSource, store) {
    let url = "";

    if (month !== "") {
      url += "month=" + month;
    }
    if (year !== "") {
      url += "&year=" + year;
    }
    if (expenseCategory && expenseCategory !== "") {
      url += "&expenseCategory=" + expenseCategory;
    }
    if (paymentSource && paymentSource !== "") {
      url += "&paymentSource=" + paymentSource;
    }
    if (store && store !== "") {
      url += "&store=" + store;
    }

    // console.log("url: " + url);

    return url;
  }

  static getCurrentMonthAndYear() {
    let date = new Date();
    const m = date.getMonth() + 1;
    let currentMonth = m;
    if (m < 10) {
      currentMonth = "0" + m;
    }

    const currentYear = date.getFullYear();

    return [currentMonth, currentYear];
  }

  static getDateAsText(date) {
    const m = date.getMonth() + 1;
    let currentMonth = m;
    if (m < 10) {
      currentMonth = "0" + m;
    }

    const d = date.getDate();
    let currentDay = d;
    if (d < 10) {
      currentDay = "0" + d;
    }

    return date.getFullYear() + '-' + currentMonth + '-' + currentDay;

  }

  static getUrl(url, filterState) {
    let params = (url.indexOf("?") != -1) ? "&" : "?";

    if (typeof filterState.month != 'undefined' && filterState.month != '') {
      params += "month=" + filterState.month;
    }
    if (typeof filterState.year != 'undefined' && filterState.year != '') {
      params += (params.length > 1 ? "&" : "");
      params += "year=" + filterState.year;
    }
    if (typeof filterState.paymentSource != 'undefined' && filterState.paymentSource != '') {
      params += (params.length > 1 ? "&" : "");
      params += "paymentSource=" + filterState.paymentSource;
    }
    if (typeof filterState.expenseCategory != 'undefined' && filterState.expenseCategory != '') {
      params += (params.length > 1 ? "&" : "");
      params += "expenseCategory=" + filterState.expenseCategory;
    }
    if (typeof filterState.store != 'undefined' && filterState.store != '') {
      params += (params.length > 1 ? "&" : "");
      params += "store=" + filterState.store;
    }

    let finalUrl = url + params;
    // console.log("url is: ", finalUrl);
    return finalUrl;
  }

  static moveMonthAndYear(forward, callerObj) {
    // console.log("assessing month and year", this.state.month, this.state.year, forward);
    let newMonth = parseInt(callerObj.props.filterState.month);
    let newYear = callerObj.props.filterState.year;

    if (forward) {
      newMonth += 1;
      if (newMonth > 12) {
        newMonth = 1;
        newYear += 1;
      }
    } else {
      newMonth -= 1;
      if (newMonth < 1) {
        newMonth = 12;
        newYear -= 1;
      }
    }

    let newMonthStr = newMonth;
    if (newMonth < 10) {
      newMonthStr = "0" + newMonth;
    }

    // console.log("after assessing month and year", newMonthStr, newYear);
    // console.log("calling filterData", newMonthStr, newYear, this.state.category, this.state.paymentSource, this.state.store);
    // this.setState({month: newMonthStr, year: newYear});
    callerObj.props.onMonthSelect(newMonthStr);
    callerObj.props.onYearSelect(newYear);

    // console.log("after assessing month and year", newMonthStr, newYear);
    callerObj.props.filterData();
  }

  static updateFilterState(key, value, callerObj) {
    // console.log("in updateFilterState before: ", callerObj.state.filterState);
    // console.log("key: ", key, ", value: ", value);
    let filterState=callerObj.state.filterState;
    filterState[key] =  value;
    callerObj.setState({filterState: filterState});
    // console.log("in updateFilterState filterState: ", filterState);
    // console.log("in updateFilterState after: ", callerObj.state.filterState);
  }

  static addState(filterState, label, key, state) {
    let value = filterState[key];

    if (typeof value === 'undefined' || value === "") {
      return state;
    }

    if (state != "") {
      state += ", ";
    }

    state += label + ": " + value;

    return state;
  }

  static addArrayState(filterState, label, key, state) {
    let value = filterState[key];

    if (typeof value === 'undefined' || value === "") {
      return state;
    }

    if (value.length == 0) {
      return state;
    }

    if (state != "") {
      state += ", ";
    }

    state += label + ": " + value;

    return state;
  }

  static getUserData(key) {
    let userData = sessionStorage.getItem('userDetails');
    // console.log("user data: ");
    // console.log(userData);

    if (userData === '') {
      return "";
    }

    let userDetails = JSON.parse(userData)

    if (userDetails === null) {
      return "";
    }
    // console.log(userDetails);
    return userDetails[key];
  }

  static removeTime(date) {
    date.setHours(0);
    date.setMinutes(0);
    date.setSeconds(0);

    return date;
  }

  static getToday() {
    let today = new Date();
    today.setHours(0);
    today.setMinutes(0);
    today.setSeconds(0);

    return today;
  }

  static getMonthYearDateFromText(input) {
    // console.log("input date is: " + input)
    if (input === '' || input == null) {
      return null;
    }
    //assumes format is YYYY-MM-dd
    let dt = new Date(input.substring(0,4), input.substring(5,7) - 1, 1);

    // console.log("returning date: " + dt)
    return dt;
  }

  static sortNumeric(a, b, order, dataField) {
    if (order === 'desc') {
      return b - a;
    }
    return a - b; // desc
  }

  static getDateFromText(input) {
    // console.log("input date is: " + input)
    if (input === '' || input == null) {
      return null;
    }
    //assumes format is YYYY-MM-dd
    let dt = new Date(input.substring(0,4), input.substring(5,7)-1, input.substring(8,10));

    // console.log("returning date: " + dt)
    return dt;
  }

  static isAfterToday(input) {
    if (input == null) return false;

    let inputDate = Utilities.getDateFromText(input);
    let today = Utilities.getToday();
    //TODO FIXME
    return inputDate.getTime() < today.getTime();
  }

  static btcFormatter(cell, row) {
    // console.log(row);
    // alert(cell);
    // let value = Number(cell).toPrecision(8);
    // console.log(row.name + " - " + cell + " input value, output: " + value);
    //
    // return "<b>" + value + "<b>";
    return cell;
  }

  static getTodayPlusX(daysToAdd) {
    var result = Utilities.getToday();
    result.setDate(result.getDate() + daysToAdd);
    return result;
  }


  static isEmpty(obj) {
      for(var key in obj) {
          if(obj.hasOwnProperty(key))
              return false;
      }
      return true;
  }

  static toLowerCaseArray(value) {
    if (value === null) {
      return value;
    }

    for (var i=0; i <value.length; i++) {
      let newValue = (value[i] != null ? value[i].toLowerCase() : value[i]);
      value[i] = newValue;
    }

    return value;
  }

  static parseParams(obj) {
    let params = qs.parse(obj.props.location.search, { ignoreQueryPrefix: true });

    // console.log("params are: ", params);
    return params;
/*
    if (params == undefined || params == null) {
      return params;
    }

    params = params.replace("?", "");
    let p = params.split("&");
    let newParams = "";
    for (let i=0; i< p.length; i++) {
      if (i == 0) {
        newParams = "{"
      }

      let param = p[i].split("=");
      newParams += "'" + param[0)param[1]
    }
    */
  }

  static addIndex(data, key) {
    if (!data) {
      return data;
    }

    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
        data[i]["index"] = i + 1;
    }

    return data;
  }

  static getRange(calc, data, key) {
    let domainMin = "0";
    let domainMax = "auto";
    if (calc) {
      domainMin = Utilities.getMinValueForAttribute(data, key);
      if (domainMin > 0) {
        domainMin = parseInt(domainMin*0.9);
      }
      domainMax = Utilities.getMaxValueForAttribute(data, key);
      // alert(domainMax);
      if (domainMax > 0) {
        domainMax = parseInt(domainMax*1.1);
      }
    }

    return [domainMin, domainMax];
  }

  static getAddedRange(calc, data, key, key2) {
    let domainMin = "0";
    let domainMax = "auto";
    if (calc) {
      // domainMin = Utilities.getMinValueForAttribute(data, key) + Utilities.getMinValueForAttribute(data, key2);
      domainMin = Utilities.getMinValueForAttributesSum(data, key, key2);
      if (domainMin > 0) {
        domainMin = parseInt(domainMin*0.9);
      }
      // domainMax = Utilities.getMaxValueForAttribute(data, key) + Utilities.getMaxValueForAttribute(data, key2);
      domainMax = Utilities.getMaxValueForAttributesSum(data, key, key2);
      // alert(domainMax);
      if (domainMax > 0) {
        domainMax = parseInt(domainMax*1.1);
      }
    }

    return [domainMin, domainMax];
  }

  static getMinValueForAttributesSum(data, key1, key2) {
    if (!data) {
      return "";
    }

    let minValue = 0;
    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
      let value1 = Utilities.getIntvalue(data, i, key1);
      let value2 = Utilities.getIntvalue(data, i, key2);
      let value = value1 + value2;
      if (value < minValue) {
        minValue = value;
      }
    }

    return minValue;
  }

  static getMaxValueForAttributesSum(data, key1, key2) {
    if (!data) {
      return "";
    }

    let maxValue = 0;
    for (let i = 0, tableDataLen = data.length; i < tableDataLen; i++) {
      let value1 = Utilities.getIntvalue(data, i, key1);
      let value2 = Utilities.getIntvalue(data, i, key2);
      let value = value1 + value2;
      if (value > maxValue) {
        maxValue = value;
      }
    }

    return maxValue;
  }

  static getIntvalue(data, i, key) {
    if (data[i][key] != null && !isNaN(data[i][key]) ) {
      // console.log(i + " - returning : " + key + " - " + data[i][key]);
      let value = parseInt(data[i][key]);
      return value;
    }

    return 0;
  }

}

export default Utilities;
