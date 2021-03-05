import React, { Component } from "react";
// import Routes from './Routes-auth';
import {BrowserRouter as Router} from 'react-router-dom';
import { Route } from 'react-router-dom';
import Fullscreen from "react-full-screen";
import ReactGA from 'react-ga';
import { createBrowserHistory } from 'history';

import "./App.css";
import DefaultRoutes from './DefaultRoutes';
import HNavBar from './harmony/HNavBar';
import Footer from './base/Footer';
import UIUtils from './util/UIUtils';
import Utilities from './util/Utilities';
import NetworkUtils from './util/NetworkUtils';
import config from './config';
// import { withAuthenticator } from 'aws-amplify-react'; // or 'aws-amplify-react-native';

// FIXME TODO removed margin from react-bootstrap-table-pagination

class App extends Component {
  constructor(props) {
		super(props);

		this.state = {
      isFull: false,
		};

	}

  componentDidCatch(error, errorInfo) {
    // Catch errors in any child components and re-renders with an error message
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

	async componentDidMount() {
     // loadReCaptcha();
	}

  goFull = () => {
    this.setState({ isFull: !this.state.isFull });
  }

  getNonProdWarning() {
    if (NetworkUtils.isDevnet()) {
      return (<div className="headerWarning"><p/><p/>This is a test website. Contact the website operator to report the issue.</div>);
    }

    return "";
  }

  render() {
    if (this.state.error) {
      // Fallback UI if an error occurs
      console.log(this.state.error);
      console.log(this.state.errorInfo.componentStack);
      return (
       <div>
         <h3>{"Oh-no! Something went wrong"}</h3>
         <p className="red">Please <a href="javascript:location.reload(true);">reload</a> the screen and try again. Please contact the website operator <a href='https://t.me/SmartStake'>here</a> if the issue persists.</p>
         <p align="center"><a href="javascript:window.location='/'">Home</a>&nbsp;&nbsp;&nbsp;<a href="javascript:window.location.reload(true);">Reload</a></p>
       </div>
      );
    }

    return this.renderDefaultContainer();
  }

  setupAnalytics() {
    ReactGA.initialize(NetworkUtils.getGaId());
    ReactGA.pageview('/');
    // ReactGA.set({});
    const history = createBrowserHistory();

    // Initialize google analytics page view tracking
    history.listen(location => {
      ReactGA.set({ page: location.pathname }); // Update the user's current page
      ReactGA.pageview(location.pathname); // Record a pageview for the given page
    });

    return history;
  }

  renderDefaultContainer() {
    document.title = "Harmony Analytics - Powered by Smart Stake";

    const childProps = {
		};

    return (
      <Router history={this.setupAnalytics()}>
        <Fullscreen enabled={this.state.isFull} onChange={isFull => this.setState({isFull})} >
          <div className="App">
            <div id="outer-container" className="divWithText">
              <HNavBar {...childProps} handleLogout={this.handleLogout} onFullScreen={this.goFull}/>
              <main id="page-wrap">
                {this.getNonProdWarning()}
                <DefaultRoutes childProps={childProps} />
              </main>
              <Footer/>
            </div>
          </div>
        </Fullscreen>
      </Router>
    );
  }
}
export default App;
