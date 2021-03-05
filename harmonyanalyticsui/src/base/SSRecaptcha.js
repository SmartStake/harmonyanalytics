import React from 'react';
import { ReCaptcha } from 'react-recaptcha-google';

import ApiUtils from '../util/ApiUtils';
import config from './config';

class SSRecaptcha extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.onLoadRecaptcha = this.onLoadRecaptcha.bind(this);
    this.verifyCallback = this.verifyCallback.bind(this);
    this.state = {
      ready: false
    }
  }

  onLoadRecaptcha() {
    if (this.isNeeded() && this.captchaDemo) {
        this.captchaDemo.reset();
        this.captchaDemo.execute();
    }
    console.log("in onLoadRecaptcha");
    this.setState({ready: true})
  }

  async verifyCallback(recaptchaToken) {
    if (!this.isNeeded()) {
      // console.log("skipping validation")
    }

    // Here you will get the final recaptchaToken!!!
    // console.log(recaptchaToken, "<= your recaptcha token")
    await ApiUtils.post("rcVerify", {"g-recaptcha-response": recaptchaToken},
      "An error occurred").then(response => {
        // console.log(response);
        if(!ApiUtils.processAccess(response)) {
          return null;
        } else {
          this.grantAccess();
        }
        // if (response["result"] != undefined && response["result"] != "successful") {
        //   alert(response["result"]);
        // }
      }).catch(function(error) {
         console.log("error received is: ", error);
      });
  }

  isNeeded() {
    let currentTime = new Date().getTime();
    let grantTill = window.localStorage.getItem("GRANT_TILL");
    if (!grantTill) {
      grantTill = 0;
    }

    // console.log("currentTime: ", currentTime, "grantTill: ", grantTill)
    let needed = (currentTime > grantTill);
    // console.log("needed: ", needed);
    return needed;
  }

  async componentDidMount() {
    if (this.isNeeded() && this.captchaDemo) {
        // console.log("started, just a second...")
        this.captchaDemo.reset();
        this.captchaDemo.execute();
    }
  }

  render() {
    if (!this.isNeeded()) {
      return "";
    }

    // console.log("check ready");
    // if(!this.state.ready) {
    //   return "";
    // }

    console.log("in render - ready");
    return (
      <div>
        <ReCaptcha ref={(el) => {this.captchaDemo = el;}}
            size="invisible"
            render="explicit"
            sitekey={config.RECAPTCHA_SITE_KEY}
            onloadCallback={this.onLoadRecaptcha}
            verifyCallback={this.verifyCallback}
        />
      </div>
    );
  }

  grantAccess() {
    // window.localStorage.removeItem("DENIED");
    let grantTime = new Date().getTime();
    let grantTill = grantTime + (180 * 1000);
    // console.log("grantTime: ", grantTime, ", grantTill: ", grantTill);
    window.localStorage.setItem("GRANT_TILL", grantTill);
    // this.setState({"clearedTill": grantTill})
  }


}

export default SSRecaptcha;
