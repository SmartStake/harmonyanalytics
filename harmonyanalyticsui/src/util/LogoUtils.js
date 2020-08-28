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

  static logoFormatter(idAddress, website, large) {
    if (!idAddress) return "";

    let size = LogoUtils.getImageSize(large);
    let imagePath = "/images/logo/" + idAddress + ".png";
    // console.log(imagePath);
    // return (<object type="image/png" width={size} height={size} data={imagePath}>
    //   <img className="img-valign" width={size} height={size} src="images/logo/default.png" />
    // </object>);

    return (<a className="black-a" target="_blank"
      href={SPUtilities.getUrl(website)}><img onError={this.addDefaultSrc} className="img-valign"
      width={size} height={size} src={imagePath}/></a>);
  }

  static addDefaultSrc(ev){
    ev.target.src = "/images/logo/default.png";
  }

  static formatLogo(cell, row) {
    return LogoUtils.logoFormatter(row.idAddress, row.website, false);
  }
}

export default LogoUtils;
