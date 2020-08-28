import React, { Component } from 'react';
import {Button} from '@material-ui/core';
import { IconButton } from '@material-ui/core';
import {Collapse} from 'react-bootstrap';
// import {Collapse} from 'react-collapse';
import HelpIcon from '@material-ui/icons/Help';

class CollpasibleSection extends Component {
  constructor(props) {
    super(props)
    this.state = {
      visible: false,
    }

    this.toggle = this.toggle.bind(this);
  }

  // async componentDidMount() {
  //   let showSection = window.localStorage.getItem(this.props.sectionId);
  //
  //   if (showSection == null) {
  //     showSection = false;
  //     console.log("componentDidMount setting ", this.props.sectionId + " to ", showSection);
  //     window.localStorage.setItem(this.props.sectionId, this.props.isVisible);
  //     this.setState({visible: this.props.isVisible});
  //     return;
  //   }
  //
  //   console.log("componentDidMount setting value for ", this.props.sectionId + " is ", showSection);
  //   this.setState({visible: showSection});
  // }

  toggle() {
    let visible = !this.state.visible;

    // console.log("toggle setting ", this.props.sectionId + " to ", visible);
    // window.localStorage.setItem(this.props.sectionId, visible);
    this.setState({visible: visible});
  }

  render() {
    return (
      <div>
        <Button onClick={this.toggle} variant="contained" color="default" id="helpComp" size="small"
          >{this.state.visible ? "Hide " + this.props.title : "Show " + this.props.title}</Button>
        <Collapse in={this.state.visible}>
          {this.props.getSectionContent()}
        </Collapse>
      </div>
    );
  }
}

export default CollpasibleSection;
