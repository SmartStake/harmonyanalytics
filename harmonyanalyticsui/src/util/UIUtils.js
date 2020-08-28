import React from 'react';

import SPUtilities from './SPUtilities';
import FavUtils from './FavUtils';
import UITableUtils from './UITableUtils';

class UIUtils extends React.Component {

  static getResponsiveWidth(thisObj) {
    let width = "90%"
    if (!thisObj.state.responsive) {
      width =  window.innerWidth * 1.5;
    }

    return width;
  }

  static getResponsiveHeight(thisObj) {
    let height = 300;
    if (window.innerHeight < 600) {
      height = 250;
    } else if (window.innerHeight < 1000) {
      height = 300;
    }

    return height
  }

  static getChartMargin(thisObj) {
    let margin = {top: 10, right: 5, left: 15, bottom: 15};
    if (thisObj.props.bigMargin) {
      margin = {top: 10, right: 25, left: 25, bottom: 15};
    }

    return margin;
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

    return height
  }

  static getShowDataLabel(thisObj, data) {
    return UIUtils.getShowDataLabel(thisObj, data, 600);
  }

  static getShowDataLabel(thisObj, data, minWidth) {
    let showDataLabel = false;
    // console.log(this.state.data);
    // console.log(this.state.data.length);
    if (thisObj.props.showVerticalLabel && window.innerWidth > minWidth && data != undefined && data.length < 35) {
      showDataLabel = true;
    } else if (thisObj.props.showVerticalLabel && window.innerWidth < minWidth && data != undefined && data.length < 7) {
      showDataLabel = true;
    }

    return showDataLabel;
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

  static getPageOptionsLarge(thisObj) {
    const options = {
      onlyOneExpanding: true,
      sizePerPageList: [
        {text: '200', value: 200},
        {text: '500', value: 500},
        {text: '1000', value: 1000},
        {text: '2000', value: 2000}
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

  static getPoolId(thisObj) {
    var poolId = thisObj.props.match.params.poolId;
    if (typeof poolId === 'undefined') {
      poolId = 1;
    }

    // console.log("poolId final is: ", poolId);
    return poolId;
  }

  static getHideFooter(thisObj) {
    // console.log(thisObj.props.match);
    if (typeof thisObj.props.match === 'undefined') {
      // console.log("returning because no params found");
      return false;
    }

    var poolId = this.props.match.params.poolId;
    // console.log("poolId: ", poolId);

    var hideFooter = thisObj.props.match.params.hideFooter;
    // console.log("hideFooter param is: ", hideFooter);
    if (typeof hideFooter === 'undefined') {
      // console.log("hideFooter param is: ", hideFooter);
      hideFooter = false;
    }

    // console.log("hideFooter final is: ", hideFooter);
    return hideFooter;
  }

  static getNotification(notification) {
    // console.log("this.state.notification.message: ", this.state.notification.message);
    if (notification == undefined || notification.message == null) {
      return "";
    }

    return (<div><p style={{"backgroundColor": "orange"}}>{notification.message}</p></div>);
  }

  static getLoading(thisObj) {
    if (thisObj.state.isLoading) {
      return <div>Loading</div>;
    } else if (thisObj.state.error) {
      return (<div><p/>
        <p>An error occurred while loading the screen. Please contact the website operator if issue persists.</p>
        <p/>
        <p/><p align="center"><a href="javascript:window.location.reload(true);">Try again</a></p>
        </div>);
    }
  }

  static renderEventTypes(thisObj) {
    if (window.innerWidth < 600) {
      return (<div><table><tbody><tr>
          <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId}>All</a> </td>
          <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/ADSDelegated"}>Del</a> </td>
          <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/ADSWithdrew"}>With</a> </td>
          <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/ADSUndelegated"}>Undel</a> </td>
          <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/large"}>Large</a> </td>
          <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/others"}>Others</a> </td>
        </tr></tbody></table></div>);
    } else {
        return (<div><table><tbody><tr>
            <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId}>All</a> </td>
            <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/ADSDelegated"}>Delegations</a> </td>
            <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/ADSWithdrew"}>Withdrawals</a> </td>
            <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/ADSUndelegated"}>Undelegations</a> </td>
            <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/large"}>Large</a> </td>
            <td className="view-tag"><a href={"/events/" + thisObj.state.pool.poolId + "/others"}>Others</a> </td>
          </tr></tbody></table></div>);
      }
  }

  static renderReload(thisObj) {
    return UIUtils.renderReloadSize(thisObj, 32);
  }

  static renderReloadSize(thisObj, size) {
    return (<img src="/images/reload.svg" onClick={SPUtilities.reload}
      title="Reload Screen" className="imgicon" width={size} height={size} />);
  }

  static renderPageActions(thisObj, fav, respSwitch) {
    return (<span className="buttonWithText">{fav ? FavUtils.showFavSwitch() : ""}
      {UIUtils.renderReload(thisObj)}{respSwitch ? UITableUtils.renderSwitchView(this) : ""}</span>);
  }

  static getUniqueValues(data, attribute) {
    let values = new Set();

    for (var i=0; i < data.length; i++) {
      // let val = { text: data[i][attribute], value: data[i][attribute] };
      // console.log("value is: ", data[i][attribute]);
      values.add(data[i][attribute]);
    }

    // console.log(attribute, " - ", values);

    let options = {};
    for (var i=0; i < values.length; i++) {
      // let val = { text: data[i][attribute], value: data[i][attribute] };
      // console.log(i + " - " + values[i]);
      options[i] = values[i];
    }

    // console.log("options are: " + attribute, " - ", options);
    return values;
  }
}

export default UIUtils;
