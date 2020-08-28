import React from 'react';
import Breadcrumb from 'react-bootstrap/Breadcrumb';

import HUtils from './HUtils';
import UIUtils from '../util/UIUtils';
import SPUtilities from '../util/SPUtilities';
// import SSRecaptcha from '../base/SSRecaptcha';

class HValHeader extends React.Component {
  render() {
    return (
      <div>
        {this.getBreadCrumb()}
        <h4 style={{align: "center"}}><span><strong>{HUtils.nameFormatterNoLink(this.props.val.name)} - {this.props.title}</strong></span>
          <span className="buttonWithText"><img src="/images/reload.svg" onClick={this.reload} title="Reload Screen"
            className="imgicon" width="32" height="32" /></span>
        </h4>
        {SPUtilities.getLastUpdatedGap(this.props.val.lastUpdatedGap)}
        {UIUtils.getNotification(this.props.notification)}
      </div>
    );
  }
  // <SSRecaptcha />

  getBreadCrumb() {
    if (window.innerWidth < 1000) {
      return (
        <Breadcrumb>
          <Breadcrumb.Item href="/">Validators</Breadcrumb.Item>
        </Breadcrumb>
      );
    } else {
      return "";
    }
  }

// <!--  <Breadcrumb.Item active>{this.props.pool.poolName} - Pool</Breadcrumb.Item> -->
  reload() {
    // window.location = "/val/" + this.state.val.hPoolId;
    window.location.reload();
  }

}

export default HValHeader;
