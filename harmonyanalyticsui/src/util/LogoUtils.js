import React from 'react';

import SPUtilities from '../util/SPUtilities';
import Utilities from '../util/Utilities';
import RespUtils from '../util/RespUtils';
import AddressUtils from '../util/AddressUtils';

class LogoUtils extends React.Component {
  static getImageSize(large) {
    let size = 16;
    if (large && RespUtils.isMobileView()) {
      size = 32;
    } else if (large) {
      size = 32;
    } else if (RespUtils.isNotMobileView()) {
      size=20;
    }

    return size;
  }

  static logoFormatter(address, website, large) {
    if (!address) return "";

    let size = LogoUtils.getImageSize(large);
    // let imagePath = "https://github.com/harmony-one/validator-logos/blob/master/validators/" + address + ".jpg?raw=true";
    let imagePath = "https://hmny-t.co/networks/mainnet/validators/" + address + "/avatar";

    // /images/logo/
    // console.log(imagePath);
    // return (<object type="image/png" width={size} height={size} data={imagePath}>
    //   <img className="img-valign" width={size} height={size} src="images/logo/default.png" />
    // </object>);

    return (<a className="black-a" target="_blank"
      href={SPUtilities.getUrl(website)}><img onError={this.addDefaultSrc} className="img-valign"
      width={size} height={size} src={imagePath}/></a>);
  }

  static addDefaultSrc(ev){
    ev.target.src = "/images/default.png";
  }

  static formatLogo(cell, row) {
    return LogoUtils.logoFormatter(cell, row.website, false);
  }

  static formatLogoFlag(cell, row) {
    if (!cell) return "";

    if (row.hasLogo) {
      return LogoUtils.logoFormatter(cell, row.website, false);
    }


    let size = LogoUtils.getImageSize(false);
    return <img onError={this.addDefaultSrc} className="img-valign"
      width={size} height={size} src="/images/default.png"/>
  }
}

export default LogoUtils;
