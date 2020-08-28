import React from 'react';
import {Button} from '@material-ui/core';
import Alert from 'react-bootstrap/Alert';

import SPUtilities from '../util/SPUtilities';
import RespUtils from '../util/RespUtils';

import CopyAddress from "../base/CopyAddress";
import SPCalc from '../util/SPCalc';
import {CopyToClipboard} from 'react-copy-to-clipboard';
import config from '../config';
import constants from "../constants";

class HUtils extends React.Component {

  static calcPercent(input1, input2) {
    // console.info("getStakeWeight - ", poolStake, totalStake);
    if (input2 == undefined || input2 == 0) {
      return "";
    }

    if (input1 == undefined || input1 == 0) {
      return 0;
    }

    return (input1 * 100 /input2).toFixed(2) + "%";
  }


  static websiteLink(label, link) {
    if (!label) {
      return label;
    }

    if (!link) {
      return label;
    }

    return (<a className="black-a" target="_blank"
      href={SPUtilities.getUrl(link)}>{label}</a>);
  }

  static addressFormatter(cell, row, index, formatExtraData) {
    return HUtils.addressFormatterByType(cell, true, true);
  }

  static addressFormatterDel(cell, row, index, formatExtraData) {
    return HUtils.addressFormatterByType(cell, true, false);
  }

  static valAddressFormatterLong(address) {
    return HUtils.addressFormatterByType(address, false, true);
  }

  static addressFormatterByType(address, short, validator) {
    if (!address) {
      return "";
    }

    let label = SPUtilities.addressLabelShortFormatter(address, null, short);
    let link = "/address/";
    let target = "";
    if(validator) {
      target = "_blank";
      link = "https://staking.harmony.one/validators/mainnet/";
    }

    return (<span><a className="black-a" target={target}
      href={link + address}>{label}</a>
      &nbsp;{HUtils.copyLink(address)}</span>);
  }

  static addressFormatterByLabel(cell, row) {
    return HUtils.addressFormatterLabelShortInd(cell, row, false);
  }

  static addressFormatterByLabelShort(cell, row) {
    return HUtils.addressFormatterLabelShortInd(cell, row, true);
  }

  static addressFormatterLabelShortInd(cell, row, short) {
    if (!cell) {
      return "";
    }

    let shortInd = short;
    if (!shortInd) {
      shortInd = (window.innerWidth > 1000 ? false : true);
    }

    let label = row.alias;
    if (!row.alias) {
      label = SPUtilities.addressLabelShortFormatter(cell, null, shortInd);
    }

    let link = "/address/";

    return (<span><a className="black-a"
      href={link + row.address}>{label}</a>
      &nbsp;{HUtils.copyLink(row.address)}</span>);
  }

  static getNameLabel(cell) {
    if (!cell) {
      return "";
    }

    let label = cell.split("?").join("");

    if (label.length > 20) {
      label = label.substring(0, 18) + "..";
    }

    return label;
  }

  static nameFormatterNoLink(cell) {
    if (!cell) {
      return "";
    }

    let label = cell.split("?").join("");
    return label;
    // return HUtils.getNameLabel(cell);
  }

  static nameFormatter(cell, row) {
    if (!cell) {
      return "";
    }

    let label = HUtils.getNameLabel(cell)

    const onClick = e => e.stopPropagation();
    return (<span onClick={ onClick }><a className="black-a" href={"/val/" + row.hPoolId}
      >{label}</a></span>);
  }

  static nameFormatterShort(cell, row) {
    if (!cell) {
      return "";
    }

    let label = cell.split("?").join("");

    if (window.innerWidth < 1000 && label.length > 8) {
      label = label.substring(0, 6) + ".";
    }

    const onClick = e => e.stopPropagation();
    return (<span onClick={ onClick }><a className="black-a" href={"/val/" + row.hPoolId}
      >{label}</a></span>);
  }

  static nameFormatterLong(cell, row) {
    if (!cell) {
      return "";
    }

    let label = cell.split("?").join("");

    return (<span><a className="black-a" href={"/val/" + row.hPoolId}
      >{label}</a></span>);
  }

  static replaceAll(value, search, replace) {
    return value.split(search).join(replace);
  }

  static copyLink(address) {
    let imgSrc = "/images/copy.png";
    let title = "Copy address to clipboard"
    return (<CopyToClipboard text={address}
        onCopy={() => {
          // formatExtraData.setState({copied: row.address});
          // console.log(row.address);
          // return false;
        }}>
        <img src={imgSrc} title={title}
          className="imgicon" width={16} height={16} />
      </CopyToClipboard>)

    // return (<CopyAddress address={address} />)
  }

  static addressLabelShortFormatter(value, row, short) {
    if (!value) {
      return value;
    }

    let label = value;
    if (short || (window.innerWidth < 1400 && value.length > 10)) {
      if (window.innerWidth < 600) {
        label = value.substring(0,6) + "..";
      } else {
        label = value.substring(0,10) + "..";
      }
    }

    return label;
  }

  static eriFormatter(cell, row, index, extra) {
    if (row.status == 'Elected' && !cell) {
      return "N/A";
    }

    let color = "green";

    if (!cell || cell < 0.8) {
      color = "red";
    } else if (cell > 0.95) {
      color = "green";
    } else {
      color = "orange";
    }

    return HUtils.colorFormatter(cell, color);
  }

  static signPerFormatter(cell, row, index, extra) {
    let color = "green";

    if (!cell || cell < 90) {
      color = "red";
    } else if (cell > 99) {
      color = "green";
    } else {
      color = "orange";
    }

    return HUtils.colorFormatter(cell, color);
  }

  static statusFormatter(cell, row, index, extra) {
    let color = "green";

    if (!cell || cell == 'NotEligible') {
      color = "red";
    } else if (cell == 'Elected') {
      color = "green";
    } else {
      color = "orange";
    }

    let value = cell;
    if (RespUtils.isMobileView()) {
      value = value.substring(0, 4);
       // + "."
    }

    return HUtils.colorFormatter(value, color);
  }

  static colorFormatter(value, color) {
    let size = "8";
    if (window.innerWidth > 1000) {
      size = 16;
    }

    let imgSrc = "/images/" + color + "-" + size + ".png"
    return (<span><img src={imgSrc} /> {value}</span>)
  }


  static getHPoolId(thisObj) {
    var hPoolId = thisObj.props.match.params.hPoolId;
    if (hPoolId === undefined) {
      hPoolId = config.apiGateway.DEFAULT_POOL_ID;
    }

    return hPoolId;
  }

  static coinCountCellFormatter(cell, row) {
    if (!cell) {
      return cell;
    }

    return SPCalc.formatCoinCount(cell.toFixed(0));
  }

  static blsKeyFormatter(cell, row) {
    if (row.status == constants.notEligibleStatus || row.optimalBlsKeyCount == 0) {
      return cell;
    }
    // console.log(cell, row);
    let color = "green";

    if (row.blsKeyCount > cell) {
      // return <span style={{backgroundColor: "#f5b514"}}>{cell}</span>;
      color = "red";
    } else if (row.blsKeyCount < cell) {
      // return <span style={{backgroundColor: "#f5b514"}}>{cell}</span>;
      color = "orange";
    }

    return HUtils.colorFormatter(cell, color);
  }

  static convertPercentFormatter(cell, row) {
    if (!cell) {
      if (cell == 0) {
        return (window.innerWidth > constants.MEDIUM) ? "0 %" : "0";
      }
      return cell;
    }

    let value = cell
    if (cell > 0) {
      var formattedNumber = (cell * 100).toFixed(2).replace(/[.,]00$/, "");
      value = formattedNumber;
      // let percentVal = cell * 100;
      // return (percentVal.toFixed(2) + "%");
    }

    if (window.innerWidth > constants.MEDIUM) {
      return value + " %";
    }

    return value
  }

  static percentFormatter(cell, row) {
    if (!cell) {
      if (cell == 0) {
        return (window.innerWidth > constants.MEDIUM) ? "0 %" : "0";
      }
      return cell;
    }

    let value = cell;
    if (cell > 0) {
      // console.log((typeof cell), " - in percentFormatter: ", cell);
      var formattedNumber = (cell).toFixed(2).replace(/[.,]00$/, "");
      value = formattedNumber;
    }

    if (window.innerWidth > constants.MEDIUM) {
      return value + " %";
    }

    return value

  }

  static formatBigCoinCount(count) {
    if (window.innerWidth < constants.MEDIUM) {
      return SPUtilities.stakeFormatterRounded(count);
    } else {
      return SPCalc.formatCoinCount(count);
    }
  }

  static logoFormatter(cell, row) {
    let url = "images/logo/" + row.address + ".png";
    // let logoPath = cell;
    // if (row.type == 'SOLO') {
    //   url = null;
    //   logoPath = "images/logo/solo.png"
    // }
    return HUtils.logoFormatterFlex(url, false);
  }

  static logoFormatterFlex(logoPath, large) {
    // console.log(logoPath)
    if (!logoPath) {
      return logoPath;
    }

    let size = 16;

    if (large && window.innerWidth < 1000) {
      size = 32;
    } else if (large) {
      size = 32;
    } else if (window.innerWidth > 1000) {
      size=20;
    }

    return "";
  }

  static showCurrentReturns(value, row) {
    // console.log((row.status == 'Elected'), !value);
    if (row.status == 'Elected' && !value) {
      return "N/A";
    }

    return value;
  }

  static lifetimeSignPer(cell, row) {
    return HUtils.calcPercent(cell, row.lifetimeToSign)
  }

  static addressLink(value) {
    if (!value) {
      return value;
    }

    return (<a href={"https://explorer.harmony.one/#/address/" + value}
      class="black-a" target="_blank">Harmony Explorer</a>);
  }

  static rewardsLink(value) {
    if (!value) {
      return value;
    }

    return (<a href={"/rewards/" + value}
      class="black-a">Rewards History</a>);
  }

  static getSupportUs() {
    return (<Alert variant="info">Like Smart Stake tools? Support us by delegating with Smart Stake&nbsp;
      <a href="https://staking.harmony.one/validators/mainnet/one1qk7mp94ydftmq4ag8xn6y80876vc28q7s9kpp7"
       className="black-a" target="_blank">here</a>.</Alert>)
  }

  static getFee(cell, row, index, extraData) {
    // console.log(cell + " - " + row.feeChangedEpoch + " - " + row.feeChangedDesc + " - " + extraData);
    if (row.feeChangedEpoch != null && row.feeChangedEpoch + 7 > extraData) {
      return (<span style={{"backgroundColor": "orange"}}>{row.feeChangedDesc}</span>);
    }

    return HUtils.convertPercentFormatter(cell, row);
  }

  static renderEventTypes(thisObj) {
    if (RespUtils.isMobileView()) {
      return (<div><table><tbody><tr>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId}>All</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Delegate"}>Del</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Undelegate"}>Undel</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/EditValidator"}>Validator</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Fee_Increase"}>Fee +</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Fee_Decrease"}>Fee -</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/large"}>Large</a></td>
        </tr></tbody></table></div>);
    } else {
      return (<div><table><tbody><tr>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId}>All</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Delegate"}>Delegate</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Undelegate"}>Undelegate</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/EditValidator"}>EditValidator</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Fee_Increase"}>Fee Increase</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/Fee_Decrease"}>Fee Decrease</a></td>
          <td className="view-tag"><a className="white-a" href={"/events/" + thisObj.state.val.hPoolId + "/large"}>Large</a></td>
        </tr></tbody></table></div>);
    }
  }

  static renderNetworkEventTypes() {
      return (<div><table><tbody><tr>
          <td className="view-tag"><a className="white-a" href={"/networkEvents"}>All</a></td>
          <td className="view-tag"><a className="white-a" href={"/networkEvents/Delegate"}>Delegate</a></td>
          <td className="view-tag"><a className="white-a" href={"/networkEvents/Undelegate"}>Undelegate</a></td>
          <td className="view-tag"><a className="white-a" href={"/networkEvents/CollectRewards"}>Rewards</a></td>
          <td className="view-tag"><a className="white-a" href={"/networkEvents/EditValidator"}>EditValidator</a></td>
          <td className="view-tag"><a className="white-a" href={"/networkEvents/Fee_Increase"}>Fee Increase</a></td>
          <td className="view-tag"><a className="white-a" href={"/networkEvents/Fee_Decrease"}>Fee Decrease</a></td>
          <td className="view-tag"><a className="white-a" href={"/networkEvents/large"}>Large</a></td>
        </tr></tbody></table></div>);
    // }
  }

  static getSmartStakeMsg(smartStakeInd) {
    // console.log("this.props.smartStake : ", this.props.smartStake);
    if (smartStakeInd != null && smartStakeInd === false) {
      return (HUtils.getSupportUs())
    }

    return "";
  }

  static formatEventType(cell) {
    if (!cell || !RespUtils.isMobileView()) {
      return cell;
    }

    if (cell === 'CollectRewards') {
      return "Rewards";
    } else if (cell === 'EditValidator') {
      return "EditVal";
    } else if (cell === 'Undelegate') {
      return "Undel";
    } else if (cell === 'Delegate') {
      return "Del";
    }

    return cell;
  }


  static convert2DigitsDecimal(cell, row) {
    if (!cell) {
      return cell;
    }

    let value = cell
    if (cell > 0) {
      value = (cell).toFixed(2).replace(/[.,]00$/, "");
    }

    return value
  }

  static stakeFormatter(cell, row) {
    if (!cell) return "";

    const onClick = e => e.stopPropagation();
    return (<span onClick={ onClick }><a href={"https://staking.harmony.one/validators/mainnet/" + cell}
      target="_blank"><button className="button-special" id={"Stake" + cell}
      >Stake</button></a></span>);
  }

  static stakeFormatterLarge(address) {
    return (<span><a href={"https://staking.harmony.one/validators/mainnet/" + address}
      target="_blank"><button className="button-special-large" id={"Stake" + address}
      >Stake</button></a></span>);
  }

}

export default HUtils;
