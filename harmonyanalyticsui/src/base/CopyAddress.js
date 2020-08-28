import React, { Component } from 'react';
import {Row, Col, Toast, Button} from 'react-bootstrap';
import {CopyToClipboard} from 'react-copy-to-clipboard';

import "./CopyAddress.css";

class CopyAddress extends Component {
  constructor(props) {
    super(props);
    this.state = {
      show: false
    };
    this.setShow = this.setShow.bind(this);
  }

  setShow(value) {
    this.setState({show: value});
  }

  render() {
    // const [show, setShow] = useState(false);

    let imgSrc = "/images/copy.png";
    let title = "Copy address to clipboard";

    return (
      <span>
        <CopyToClipboard text={this.props.address}
          onCopy={() => {
            // formatExtraData.setState({copied: row.address});
            // console.log(row.address);
            // return false;
            this.setShow(true);
          }}>
          <img src={imgSrc} title={title}
            className="imgicon" width={16} height={16} />
        </CopyToClipboard>

        <div className="divAbs">
          <Toast onClose={() => this.setShow(false)} show={this.state.show} delay={3000} autohide>
            <Toast.Header>
              <strong className="mr-auto">Copy address to clipboard</strong>
            </Toast.Header>
            <Toast.Body>{this.props.address} - successfully copied to clipboard.</Toast.Body>
          </Toast>
        </div>
      </span>
    );
  }
}

export default CopyAddress;
