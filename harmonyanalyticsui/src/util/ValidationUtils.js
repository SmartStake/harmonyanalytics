import React from 'react';

class ValidationUtils extends React.Component {
  static isValidAmount(amount) {
    if (amount.indexOf(".") == -1) {
      var regex  = /^\d+(?:)$/;
      // console.log("amount test: regex.test(amount) : " + regex.test(amount));
      return regex.test(amount);
    } else {
      var regex  = /^\d+(?:\.\d{0,2})$/;
      // console.log("amount test: with decimal : " + regex.test(amount));
      return regex.test(amount);
    }
    //var numStr = "123.20";
    // if (regex.test(amount))
    //     alert("Number is valid");

  }

  static isNotNull(value) {
    let valid = true;

    if (typeof value === 'undefined' || value === null || value === "") {
      valid = false;
    }

    return valid;
  }

  static validateAmount(key, amount, callerObj) {
    let valid = ValidationUtils.isNotNull(amount);
    // console.log("validateAmount - valid: " + valid);
    // alert("returning: '" +  value + "', valid: '" + valid + "'");

    if (!valid || !ValidationUtils.isValidAmount(amount)) {
      // console.log("validateAmount - check failed: " + amount);
      callerObj.setState({[key]: "Expense amount must be a valid value (xxxx.xx)"});
      valid = false;
    } else {
      callerObj.setState({[key]: ""});
    }

    return valid;
  }

}

export default ValidationUtils;
