import React from 'react';

import SPUtilities from './SPUtilities';
import Utilities from './Utilities';
import UITableUtils from './UITableUtils';

class RespUtils extends React.Component {
  static isWidthLessThan(width) {
    return UITableUtils.isDefaultView() && window.innerWidth < width;
  }

  static isMobileView() {
    return RespUtils.isWidthLessThan(600);
  }

  static isTabletView() {
    return RespUtils.isWidthLessThan(1000);
  }

  static isOldPCView() {
    return RespUtils.isWidthLessThan(1400);
  }

  static isWidthMoreThan(width) {
    return !UITableUtils.isDefaultView() || window.innerWidth > width;
  }

  static isNotMobileView() {
    return RespUtils.isWidthMoreThan(600);
  }

  static isNotTabletView() {
    return RespUtils.isWidthMoreThan(1000);
  }

  static isNotOldPCView() {
    return RespUtils.isWidthMoreThan(1400);
  }

  static getChartHeight(thisObj) {
    let height = 300;
    if (thisObj.props.chartType == 'pool') {
      if (window.innerHeight < 600) {
        height = 250;
      } else if (window.innerHeight < 1000) {
        height = 300;
      }
    }
    return height;
  }

  static getResponsiveWidth(thisObj) {
    let width = "90%"
    if (!thisObj.state.responsive) {
      width =  window.innerWidth * 1.5;
    }

    return width;
  }

  static getSpecialMessage() {
    let specialMessage = "";
    if (RespUtils.isMobileView()) {
      specialMessage = "Tip: This screen is best viewed in landscape mode (Rotate your mobile device for a better view)";
    }

    return specialMessage;
  }
}

export default RespUtils;
