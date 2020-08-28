import React from "react";
import Alert from 'react-bootstrap/Alert';

class ErrorMessageBox extends React.Component {
  render() {
    return (
      <div id="mBoxId" className={"messageBox " + (this.props.type || "hidden")}>
        <Alert variant="danger">
          Error occurred - {this.props.message}
        </Alert>
      </div>
    )
  }
}

export default ErrorMessageBox;
