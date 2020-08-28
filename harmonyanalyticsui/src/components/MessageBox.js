import React from "react";

class MessageBox extends React.Component {
  render() {
    return (
      <div id="mBoxId" className={"messageBox " + (this.props.type || "hidden")}>
        {this.props.message}
        <p/>
      </div>
    )
  }
}

export default MessageBox;
