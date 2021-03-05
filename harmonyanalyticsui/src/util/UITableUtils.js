import React from 'react';

class UITableUtils extends React.Component {

  static getResponsiveWidth(thisObj) {
    let width = "90%"
    if (!thisObj.state.responsive) {
      width =  window.innerWidth * 1.5;
      // if (width < 800) {
      //   width = 1200;
      // }
    }

    return width;
  }

  static getPageOptions(thisObj) {
    const options = {
      onlyOneExpanding: true,
      sizePerPageList: [
        {text: '50', value: 50},
        {text: '100', value: 100},
        {text: '200', value: 200},
        {text: '500', value: 500}
      ]
    };

    return options;
  }

  static getPageOptionsSmall(thisObj, minSize) {
    let options;
    if (minSize) {
      options = {
        onlyOneExpanding: true,
        sizePerPageList: [
          {text: minSize, value: minSize},
          {text: '25', value: 25},
          {text: '50', value: 50},
          {text: '100', value: 100},
          {text: '200', value: 200},
          {text: '500', value: 500}],
      };
    } else {
      options = {
        onlyOneExpanding: true,
        sizePerPageList: [
          {text: '25', value: 25},
          {text: '50', value: 50},
          {text: '100', value: 100},
          {text: '200', value: 200},
          {text: '500', value: 500}],
      };
    }

    return options;
  }

  static renderSwitchView(thisObj) {
    let isSmallDevice = (window.innerWidth < 1400);

    if (!isSmallDevice) {
      // console.log("large device. switch view not required");
      return;
    }

    let imageSize = 32;
    let viewLabel = "Switch to desktop view";
    let viewSrc = "/images/expand.png";

    // window.localStorage.setItem(FavUtils.getDefaultViewKey(), "Favs");
    let desktopView = window.localStorage.getItem("desktopView");
    // console.log("renderSwitchView: " + desktopView);
    // console.log((desktopView != null));
    // console.log(desktopView);
    if (desktopView != null && desktopView == 'true') {
      // console.log("render switch to default view");
      viewLabel = "Switch to default view";
      viewSrc = "/images/collapse.png";
    }

    return <span>{' '}<img src={viewSrc} onClick={UITableUtils.switchView} title={viewLabel}
      className="imgicon" width={imageSize} height={imageSize} /></span>
  }

  static isDefaultView() {
    let isSmallDevice = (window.innerWidth < 1400);

    if (!isSmallDevice) {
      return true;
    }

    let desktopView = window.localStorage.getItem("desktopView");
    if (desktopView != null && desktopView == 'true') {
      // console.log("render switch to desktop view");
      return false;
    }

    return true;
  }

  static switchView() {
    let desktopView = window.localStorage.getItem("desktopView");
    if (desktopView != null && desktopView == 'true') {
      window.localStorage.setItem("desktopView", 'false');
    } else {
      window.localStorage.setItem("desktopView", 'true');
    }

    window.location.reload();
  }
}

export default UITableUtils;
