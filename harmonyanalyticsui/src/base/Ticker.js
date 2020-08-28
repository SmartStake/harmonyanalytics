import React from 'react';
// import TradingViewWidget from 'react-tradingview-widget';
// import { TradingViewEmbed, widgetType } from "react-tradingview-embed";

import config from "../config";
import UIUtils from "../util/UIUtils";

class Ticker extends React.Component {
  constructor(props) {
		super(props);
		this.state = {};
	}

  render() {
    let width = UIUtils.getResponsiveWidth(this);
    let height = UIUtils.getResponsiveHeight(this);

    return (
      <div>
      </div>
    );
  }
}
// <TradingViewWidget symbol="ONEBTC" />
// <TradingViewEmbed
//   widgetType={widgetType.TICKER_TAPE}
//   widgetConfig={{
//     colorTheme: "light",
//     width: "90%",
//     height: "70%",
//   }}
// />
// <TradingViewEmbed
//   widgetType={widgetType.TICKER_TAPE}
//   widgetConfig={{
//     colorTheme: "light",
//     displayMode: "adaptive",
//     symbols: [{"proName": "BINANCE:ONEBTC","title": "ONEBTC"}],
//     width: {width},
//     height: {height},
//   }}
// />

export default Ticker;
