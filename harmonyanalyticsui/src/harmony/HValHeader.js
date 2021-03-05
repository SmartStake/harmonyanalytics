import React from 'react';

import HUtils from './HUtils';
import UIUtils from '../util/UIUtils';
import SPUtilities from '../util/SPUtilities';
import LogoUtils from "../util/LogoUtils";
import ValAction from "./ValAction";
// import ValMenu from "./ValMenu";
// import SSRecaptcha from '../base/SSRecaptcha';

class HValHeader extends React.Component {
  // <ValMenu />
  render() {
    return (
      <div>
        {HUtils.getBreadCrumb()}
        <h4 style={{align: "center"}}><span>{LogoUtils.logoFormatter(this.props.val.address, this.props.val.website, true)} <strong>{HUtils.nameFormatterNoLinkLimitSize(this.props.val.name)} - {this.props.title}</strong></span>
          <span className="buttonWithText"><img src="/images/reload.svg" onClick={this.reload} title="Reload Screen"
            className="imgicon" width="32" height="32" /></span>
        </h4>
        <ValAction hPoolId={this.props.val.hPoolId}/>
        {SPUtilities.getLastUpdatedGapSpecial(this.props.val.lastUpdatedGap, this.props.lastUpdated)}
        {UIUtils.getNotification(this.props.notification)}
      </div>
    );
  }
  // <SSRecaptcha />


// <!--  <Breadcrumb.Item active>{this.props.pool.poolName} - Pool</Breadcrumb.Item> -->
  reload() {
    // window.location = "/val/" + this.state.val.hPoolId;
    window.location.reload();
  }

}

export default HValHeader;
