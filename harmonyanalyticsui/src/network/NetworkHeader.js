import React from 'react';

import HUtils from '../harmony/HUtils';
import UIUtils from '../util/UIUtils';
import SPUtilities from '../util/SPUtilities';
import NetworkAction from "./NetworkAction";
// import ValMenu from "./ValMenu";
// import SSRecaptcha from '../base/SSRecaptcha';

class NetworkHeader extends React.Component {
  // <ValMenu />
  render() {
    return (
      <div>
        <p/>
        {HUtils.getBreadCrumb()}
        <h4 style={{align: "center"}}><span><strong>{this.props.title}</strong></span>
            {UIUtils.renderPageActions(this, false, true)}
        </h4>
        <NetworkAction />
      </div>
    );
  }
  // <SSRecaptcha />

}

export default NetworkHeader;
