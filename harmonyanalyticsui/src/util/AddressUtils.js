import React from 'react';
import {CopyToClipboard} from 'react-copy-to-clipboard';
import Breadcrumb from 'react-bootstrap/Breadcrumb';

import RespUtils from './RespUtils';
import SPUtilities from './SPUtilities';
import SPCalc from './SPCalc';
import config from '../config';
import constants from "../constants";

class AddressUtils extends React.Component {
  static addressFormatterByLabel(cell, row) {
    return AddressUtils.addressFormatterLabelShortInd(cell, row, false);
  }

  static addressFormatterByLabelShort(cell, row) {
    return AddressUtils.addressFormatterLabelShortInd(cell, row, true);
  }

  static addressFormatterLabelShortInd(cell, row, short) {
    if (!cell) {
      return "";
    }

    let shortInd = short;
    if (!shortInd) {
      shortInd = (RespUtils.isNotTabletView() ? false : true);
    }

    let label = row.alias;
    if (!row.alias) {
      label = SPUtilities.addressLabelShortFormatter(cell, null, shortInd);
    }

    let link = "/address/";

    return (<span><a className="black-a"
      href={link + row.address}>{label}</a>
      &nbsp;{AddressUtils.copyLink(row.address)}</span>);
  }

  static addressLabelShortFormatter(value, row, short) {
    if (!value) {
      return value;
    }

    let label = value;
    if (short || (RespUtils.isOldPCView() && value.length > 10)) {
      if (RespUtils.isMobileView()) {
        label = value.substring(0,6) + "..";
      } else {
        label = value.substring(0,10) + "..";
      }
    }

    return label;
  }

  static addressFormatterLong(cell, row, index, formatExtraData) {
    return AddressUtils.addressFormatterByType(cell, row.alias, false, true);
  }

  static addressFormatter(cell, row, index, formatExtraData) {
    return AddressUtils.addressFormatterByType(cell, row.alias, true, true);
  }

  static addressFormatterDel(cell, row, index, formatExtraData) {
    return AddressUtils.addressFormatterSimpleWithLink(cell);
    // addressFormatterByType(cell, row.alias, false, false)
  }

  static addressFormatterByType(address, alias, short, validator) {
    if (!address) {
      return "";
    }

    let label = SPUtilities.addressLabelShortFormatter(address, null, short);

    return (<span>{label}&nbsp;{AddressUtils.copyLink(address)}</span>);
  }

  static copyLink(address) {

    let imgSrc = "/images/copy.png";
    let title = "Copy address to clipboard"

    return (<CopyToClipboard text={address}
        onCopy={() => {
        }}>
        <img src={imgSrc} title={title}
          className="imgicon" width={16} height={16} />
      </CopyToClipboard>)
  }

  static addressFormatterSimple(address) {
    if (!address) {
      return "";
    }

    let label = address;

    if (RespUtils.isTabletView()) {
      label = address.substring(0,10) + "..";
    }

    return (<span>{label}&nbsp;{AddressUtils.copyLink(address)}</span>);
  }

  static addressFormatterSimpleWithLink(address) {
    if (!address) {
      return "";
    }

    let label = address;

    if (RespUtils.isTabletView()) {
      label = address.substring(0,10) + "..";
    }

    return (<span><a href={"/address/" + address} class="black-a">{label}</a>&nbsp;{AddressUtils.copyLink(address)}</span>);
  }

  static addressFormatterSimpleNoCopy(address) {
    if (!address) {
      return "";
    }

    let label = address;

    if (RespUtils.isTabletView()) {
      label = address.substring(0,10) + "..";
    }

    return label;
  }

  static getAliasOrAddress(address) {
    // console.log("input is:", address);
    if (!address) {
        return "";
    }

    if(address.alias) {
      return address.alias;
    }

    return AddressUtils.addressFormatterSimple(address.address);
  }

  static getBreadCrumb() {
    if (RespUtils.isTabletView()) {
      return (
        <Breadcrumb>
          <Breadcrumb.Item href="/">Home</Breadcrumb.Item>
        </Breadcrumb>
      );
    } else {
      return "";
    }
  }

}

export default AddressUtils;
