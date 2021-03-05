import React from "react";
import {Navbar, Nav, NavDropdown} from 'react-bootstrap';
import {Form} from 'react-bootstrap';

import RespUtils from "../util/RespUtils";
import NetworkUtils from "../util/NetworkUtils";
import Dropdown from '../base/Dropdown';

class HNavBar extends React.Component {
  constructor(props) {
		super(props);

		this.state = {
      username: "",
		};
	}

	async componentDidMount() {
	}

  showSettings (event) {
    event.preventDefault();
  }

  switchNetwork = (e) => {
    NetworkUtils.switchNetwork(e);
  }

  render() {
    // let logoSize = (window.innerWidth < 600) ? 14:32;
    let logoWidth = (window.innerWidth < 600) ? 32: 32;
    let logoHeight = (window.innerWidth < 600) ? 32 :32;
    // let logoWidth = (window.innerWidth < 600) ? 32: 32;
    // let logoHeight = (window.innerWidth < 600) ? 32 :32;

    // <Navbar.Brand href="/"><img src="/images/smartstake.png" width={logoSize}
    //   height={logoSize} className="d-inline-block align-top" alt="Smart Stake"
    //   />&nbsp;Smart Stake - Harmony</Navbar.Brand>
    let defaultNetwork = NetworkUtils.getCurrentNetwork();

    return (
      <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark" sticky="top">
        <Navbar.Brand href="/"><img src="/images/harmony_logo.png" width={logoWidth}
          height={logoHeight} className="d-inline-block align-top" alt="Harmony Analytics"
          />&nbsp;Harmony Analytics</Navbar.Brand>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="mr-auto">
            <Nav.Link eventKey={1.11} href="/">Validators</Nav.Link>
            <Nav.Link eventKey={1.12} href="/account">My Account</Nav.Link>
            <Nav.Link eventKey={1.13} href="/history">Network</Nav.Link>
            <Nav.Link eventKey={1.14} href="/election">Election</Nav.Link>
            <Nav.Link>
              <Form inline>
                <Dropdown onSelect={this.switchNetwork} values={NetworkUtils.getNetworks()}
                  addAll={false} addBlank={false} defaultValue={defaultNetwork}/>
              </Form>
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Navbar>
    );
  }

  getSS() {
    if(RespUtils.isMobileView()) {
      return <font size="2">Smart Stake</font>
    }

    return <small>by Smart Stake</small>
  }
}

export default HNavBar;
// <NavDropdown.Item href="/richdel">Rich Delegates</NavDropdown.Item>

// <Navbar.Toggle aria-controls="basic-navbar-nav" />
// <Navbar.Collapse id="basic-navbar-nav">
//   <Nav className="mr-auto">
//     <Nav.Link eventKey={1.12} href="/"></Nav.Link>
//   </Nav>
// </Navbar.Collapse>
//
// <NavDropdown.Item href="/stats">Network Stats</NavDropdown.Item>
