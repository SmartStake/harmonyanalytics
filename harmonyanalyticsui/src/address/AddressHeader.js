import React from 'react';

import UIUtils from '../util/UIUtils';
import SPUtilities from '../util/SPUtilities';
import AddressUtils from '../util/AddressUtils';

class AddressHeader extends React.Component {
  render() {
    return (
      <div>
        {AddressUtils.getBreadCrumb()}
        <h5 style={{align: "center"}}><span><strong>{AddressUtils.getAliasOrAddress(this.props.addressDetails)}
            &nbsp;- {this.props.title}</strong></span>
        {UIUtils.renderPageActions(this, false, false)}</h5>
        {SPUtilities.getLastUpdatedGap(this.props.lastUpdatedGap)}
      </div>
    );
  }

}

export default AddressHeader;
