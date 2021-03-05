import React from 'react';
import Table from 'react-bootstrap/Table';
import BootstrapTable from 'react-bootstrap-table-next';
import 'react-bootstrap-table-next/dist/react-bootstrap-table2.min.css';
import {Button} from '@material-ui/core';
import paginationFactory from 'react-bootstrap-table2-paginator';
import filterFactory, { textFilter } from 'react-bootstrap-table2-filter';
import constants from "../constants";

import HNetworkNav from './HNetworkNav';
import "./Election.css";
import FavUtils from "../util/FavUtils";

import HUtils from '../harmony/HUtils';
// import CDTimer from '../base/CDTimer';

import LogoUtils from '../util/LogoUtils';
import SPCalc from '../util/SPCalc';
import ApiUtils from '../util/ApiUtils';
import Utilities from "../util/Utilities";
import UIUtils from "../util/UIUtils";
import SPUtilities from "../util/SPUtilities";

class ElectionUtils extends React.Component {

  static processForWhatIf(details) {
    let allData = []
    for (let i = 0; i < details.length; i++) {
      let data = details[i];

      // if (!data.name.startsWith('Smart Stake')) {
      //   return newSlot;
      // }
      // if (i > 5) {
      //   continue;
      // }
      // console.log(data.name + " : processForWhatIf");

      data.slotDetailsPlusOne = ElectionUtils.getWhatIfImpact(data, details, 1);
      data.slotRangePlusOne = data.slotDetailsPlusOne.slotRange;
      data.slotStatusPlusOne = data.slotDetailsPlusOne.status;

      data.slotDetailsPlusTwo = ElectionUtils.getWhatIfImpact(data, details, 2);
      data.slotRangePlusTwo = data.slotDetailsPlusTwo.slotRange;
      data.slotStatusPlusTwo = data.slotDetailsPlusTwo.status;

      data.slotDetailsPlusThree = ElectionUtils.getWhatIfImpact(data, details, 3);
      data.slotRangePlusThree = data.slotDetailsPlusThree.slotRange;
      data.slotStatusPlusThree = data.slotDetailsPlusThree.status;

      data.slotDetailsMinusOne = ElectionUtils.getWhatIfImpact(data, details, -1);
      data.slotRangeMinusOne = data.slotDetailsMinusOne.slotRange;
      data.slotStatusMinusOne = data.slotDetailsMinusOne.status;
      // console.log(data);

      data.slotDetailsMinusTwo = ElectionUtils.getWhatIfImpact(data, details, -2);
      data.slotRangeMinusTwo = data.slotDetailsMinusTwo.slotRange;
      data.slotStatusMinusTwo = data.slotDetailsMinusTwo.status;

      data.slotDetailsMinusThree = ElectionUtils.getWhatIfImpact(data, details, -3);
      data.slotRangeMinusThree = data.slotDetailsMinusThree.slotRange;
      data.slotStatusMinusThree = data.slotDetailsMinusThree.status;
      allData.push(data);
    }

    return allData;
  }

  static getWhatIfImpact(data, details, count) {
    // console.log("in getWhatIfImpact");
    let newSlotCount = data.slotsRequested + count;
    // console.log("newSlotCount: ", newSlotCount + ", count: ", count);
    if (count < 0 && newSlotCount <= 0) {
      let skipData = {status: constants.ES_NOT_POSSIBLE,
        slotRange: ""};
      // console.log("returning not possible data: ", skipData);
      return skipData;
    }
    // console.log("checking further");

    let newSlotEnd = data.slotDetails.slotEnd + count;
    let newBid = Math.round(data.actualStake / newSlotCount);
    let newSlot = {slotCount: newSlotCount, status: data.slotDetails.status,
      slotStart: data.slotDetails.slotStart, slotEnd: newSlotEnd,
      bid: newBid, slotRange: data.slotDetails.slotStart + "-" + newSlotEnd};

    // console.log(data.name, " - old bid: ", data.bid, ", new bid: ", newBid);
    // console.log("old slots: ", data.slot);
    for (let i = 0; i < details.length; i++) {
      //find the first bid that is lower than the new bid
      let detail = details[i];
      // console.log(i, " - newBid > detail.slotDetails.bid: ", newBid, detail.slotDetails.bid);
      if (newBid > detail.slotDetails.bid) {
        // console.log(i + " - will settle at: ", detail.name + ", with bid: ", detail.slotDetails.bid);
        // console.log(detail);
        // console.log(newSlot);
        if (detail.slotDetails.slotStart > newSlot.slotStart) {
          newSlot.slotStart = detail.slotDetails.slotStart - data.slotsRequested;
        } else {
          newSlot.slotStart = detail.slotDetails.slotStart;
        }
        // console.log(newSlot.slotStart);
        newSlot.slotEnd = newSlot.slotStart + newSlotCount - 1;
        // console.log(newSlot.slotEnd);

        if (newSlot.slotStart > constants.SLOTS) {
          newSlot.status = constants.ES_NOT_ELECTED;
        } else if (newSlot.slotEnd > constants.SLOTS) {
          newSlot.status = constants.ES_PARTIALLY_ELECTED;
        } else {
          newSlot.status = constants.ES_ELECTED;
        }

        if (newSlot.slotStart === newSlot.slotEnd) {
          newSlot.slotRange = newSlot.slotStart;
        } else {
          newSlot.slotRange = newSlot.slotStart + "-" + newSlot.slotEnd;
        }
        // console.log(newSlot);
        break;
      }
      // console.log("new slots: ", newSlot.slot);
    }

    return newSlot;
  }

  static getSlotCountAndStatus(slots, detail) {
    let slotDetails = {slotCount: 0, status: constants.ES_NOT_ELECTED, slotStart: 0, slotEnd: 0};
    // console.log(slots);
    if (slots == null) {
      return slotDetails;
    }

    let slotCount = 1;
    let status = constants.ES_ELECTED;
    let slotStart = 0;
    let slotEnd = 5000;

    if (slots.indexOf("-") == -1) {
      // console.log("parseInt(slots): ", parseInt(slots));
      slotStart = parseInt(slots);
      slotEnd = parseInt(slots);
      if (parseInt(slots) > constants.SLOTS) {
        // return {"background-image": "linear-gradient(to right, red, #ffffff)"};
        slotCount = 0;
        status = constants.ES_NOT_ELECTED;
      }
    } else {
      let slotsList = slots.split("-");
      // console.log("parseInt(slots): ", parseInt(slotsList[1]));
      slotStart = parseInt(slotsList[0]);
      slotEnd = parseInt(slotsList[1]);
      slotCount = slotEnd - slotStart + 1;
      if (parseInt(slotStart) > constants.SLOTS) {
        //FIXME - partial election
        // return {"background-image": "linear-gradient(to right, red, #ffffff)"};
        slotCount = 0;
        status = constants.ES_NOT_ELECTED;
      } else if (parseInt(slotEnd) === constants.SLOTS) {
        if (detail.slotsRequested != slotCount) {
          status = constants.ES_PARTIALLY_ELECTED;
        }
      }
    }

    slotDetails.slotCount = slotCount;
    slotDetails.status = status;
    slotDetails.slotStart = slotStart;
    slotDetails.slotEnd = slotEnd;

    return slotDetails;
  }

  static slotStyle(cell, row) {
    // if (row.slotDetails.status == null) {
    //   return "";
    // }
    //
    // let status = row.slotDetails.status;
    // let color = "ffffff";//defult white
    //
    // if (status == constants.ES_ELECTED) {
    //     color = "#ccffcc";
    // } else if (status == constants.ES_NOT_ELECTED) {
    //   color = "#ff9999";
    // } else if (status == constants.ES_PARTIALLY_ELECTED) {
    //   color = "#ffdb99";
    // }
    //
    // return {"backgroundImage": "linear-gradient(to right, " + color + ", #ffffff)"};
    return ElectionUtils.slotStyleByStatus(row.slotDetails.status);
  }

  static slotStylePlusOne(cell, row) {
    return ElectionUtils.slotStyleByStatus(row.slotDetailsPlusOne.status);
  }

  static slotStylePlusTwo(cell, row) {
    return ElectionUtils.slotStyleByStatus(row.slotDetailsPlusTwo.status);
  }

  static slotStylePlusThree(cell, row) {
    return ElectionUtils.slotStyleByStatus(row.slotDetailsPlusThree.status);
  }

  static slotStyleMinusOne(cell, row) {
    return ElectionUtils.slotStyleByStatus(row.slotDetailsMinusOne.status);
  }

  static slotStyleMinusTwo(cell, row) {
    return ElectionUtils.slotStyleByStatus(row.slotDetailsMinusTwo.status);
  }

  static slotStyleMinusThree(cell, row) {
    return ElectionUtils.slotStyleByStatus(row.slotDetailsMinusThree.status);
  }

  static slotStyleByStatus(status) {
    if (status == null) {
      return "";
    }

    let color = "ffffff";//defult white

    if (status == constants.ES_NOT_POSSIBLE) {
      color = "lightgrey";
    } else if (status == constants.ES_ELECTED) {
      color = "#ccffcc";
    } else if (status == constants.ES_NOT_ELECTED) {
      color = "#ff9999";
    } else if (status == constants.ES_PARTIALLY_ELECTED) {
      color = "#ffdb99";
    }

    return {"backgroundImage": "linear-gradient(to right, " + color + ", #ffffff)"};
  }

}

export default ElectionUtils;
/*
slotStyle(cell, row) {
  let color = "#ccffcc";
  console.log(row.slot);
  let slots = row.slot;

  if (slots != null) {
    if (slots.indexOf("-") == -1) {
      console.log("parseInt(slots): ", parseInt(slots));
      if (parseInt(slots) > 640) {
        // return {"background-image": "linear-gradient(to right, red, #ffffff)"};
        color = "#ff9999";
      }
    } else {
      let slotsList = slots.split("-");
      console.log("parseInt(slots): ", parseInt(slotsList[1]));
      if (parseInt(slotsList[1]) > 640) {
        //FIXME - partial election
        // return {"background-image": "linear-gradient(to right, red, #ffffff)"};
        color = "#ff9999";
      }
    }
    return {"background-image": "linear-gradient(to right, " + color + ", #ffffff)"};
  }
}
*/
