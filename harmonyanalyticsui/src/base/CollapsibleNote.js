import React, { Component } from 'react';
import {Button} from '@material-ui/core';
import { IconButton } from '@material-ui/core';
import {Collapse} from 'react-collapse';
import HelpIcon from '@material-ui/icons/Help';
import Card from 'react-bootstrap/Card';

class CollpasibleNote extends Component {
  constructor(props) {
    super(props)
    this.state = {
      showGuide: false,
    }

    this.switchGuide = this.switchGuide.bind(this);
  }

  async componentDidMount() {
  }

  switchGuide() {
    let showGuide = !this.state.showGuide;
    this.setState({showGuide: showGuide});
  }

  render() {
    return (
      <div>
        <p><Button onClick={this.switchGuide} variant="contained" color="info" id="helpComp" size="small"
          >{this.state.showGuide ? "Hide Screen Guide" : "Show Screen Guide"}</Button></p>
        <Collapse isOpened={this.state.showGuide}>
          <Card>
            <Card.Header>Screen Guide</Card.Header>
            <Card.Body>
              <Card.Text>{this.props.getScreenGuide()}</Card.Text>
            </Card.Body>
          </Card>
        </Collapse>
      </div>
    );
  }
}

export default CollpasibleNote;
