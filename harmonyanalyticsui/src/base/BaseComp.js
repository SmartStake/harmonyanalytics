import React from 'react';
import ApiUtils from '../util/ApiUtils';

class BaseComp extends React.Component {
  //FIXME find a way to remove duplicate code
  getData(url) {
    let data = "";
    try {
      data =  ApiUtils.get(url);
    } catch (e) {
      console.log(url + " - call failed. error is: " + e);
      console.log(e);
    }

    return data;
  }

  postData(url, postDataObj) {
    return ApiUtils.post(url, {
      body: postDataObj
    });
  }

  renderLander() {
    return (
      <div className="lander">
      <h1>Not signed in</h1>
      <p>You are not logged in. <a href="/login">Click here to login.</a></p>;
      </div>
    );
  }

  renderLoading() {
    return (
      <div className="lander">
      <h1>Loading</h1>
      <p>This screen is loading. Please wait..</p>
      </div>
    );
  }

  render() {
//    console.log ("in base component: this.props.isAuthenticated - " + this.props.isAuthenticated);
    return (
      <div>
        {this.props.isAuthenticated ? this.renderContent() : this.renderLander()}
      </div>
    );
  }

}

export default BaseComp;
