import React, { Component } from 'react';

import ApiUtils from '../util/ApiUtils';
import HUtils from '../harmony/HUtils';
import './Views.css';

class Views extends Component {
  constructor(props) {
    super(props)

    this.state = {
      views: [],
    }
    this.removeAlias = this.removeAlias.bind(this);
  }

  async componentDidMount() {
    let aliases = window.localStorage.getItem("alias");
    let views = [];
    if (aliases != null) {
      views = aliases.split(",");
      this.setState({views: views});
    }
  }

  addRemoveButton() {
    // return <a href="/rewards?clear=true">Remove Aliases</a>;
    return <td><a href="#" onClick={this.removeAlias}>Remove Aliases</a></td>;
  }

  async removeAlias() {
    // console.log("in remove alias");
    // console.log("in method: " + window.localStorage.getItem("alias"));
    // console.log(aliases);
    // console.log("alias details: ", aliasDetails);
    window.localStorage.removeItem("lastAlias");
    window.localStorage.removeItem("lastAddress");
    await ApiUtils.post("harmonyUpdateData?type=clearAlias", {type: "clearAlias", data: {alias: window.localStorage.getItem("alias")}}, "An error occurred").then(response => {
    // console.log("after removal backe3nd call");
      // console.log(response);
      // if (response["result"] != undefined && response["result"] != "successful") {
      //   alert(response["result"]);
      // }
    }).catch(function(error) {
       console.log("error received is: ", error);
    });

    window.localStorage.removeItem("alias");
    // console.log("after removal alias is: " + window.localStorage.getItem("alias"));
    // console.log("in reloading screen");
    document.location = "/" + this.props.viewType;
    // document.location = "/rewards";

  }

  render() {
    return (
      <div>
        {HUtils.getSmartStakeMsg(this.props.smartStake)}
        <table><tbody><tr>
          {this.state.views.map((view, index) => (
            <td key={index} className="view-tag"><a className="white-a" href={this.props.viewType + "?alias=" + view}
              >{view}</a> </td>
          ))}{this.state.views.length > 0 && this.addRemoveButton()}</tr></tbody></table></div>
    );
  }

}

export default Views;
