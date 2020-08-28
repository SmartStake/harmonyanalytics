import React, { Component } from 'react';
import {Button} from '@material-ui/core';
import {Row, Col, Form, FormGroup} from 'react-bootstrap';
import TagsInput from 'react-tagsinput';
import {Collapse} from 'react-collapse';
import { IconButton } from '@material-ui/core';

import './react-tagsinput.css';
import "./FilterAddress.css";
import Utilities from '../util/Utilities';
import UIUtils from '../util/UIUtils';

class FilterAddress extends Component {
  constructor(props) {
    super(props)
    this.filterDataAndSave = this.filterDataAndSave.bind(this);
    this.onAddressSelect = this.onAddressSelect.bind(this);
    this.onAliasChange = this.onAliasChange.bind(this);
    this.filterData = this.filterData.bind(this);
  }

  async componentDidMount() {
    // const catData = await ApiUtils.get("listTags");
    // this.setState({tags: catData});
  }

  filterDataAndSave = (e) => {
    e.preventDefault();
    if (this.props.filterState.alias == undefined || this.props.filterState.alias.length < 2) {
      alert("Please enter a nickname/alias for saving the search");
      return;
    }
    if (this.props.filterState.address.length === 0) {
      alert("Please enter an address");
      return;
    } else if (this.props.filterState.address.length != 0 && !this.props.filterState.address.startsWith("one")) {
      alert("Please enter a valid $ONE address (it should start with 'one')");
      return;
    }

    this.props.saveAlias();
    this.props.filterData();

  }

  onAddressSelect = (e) => {this.props.onAddressSelect(e)}
  onAliasChange = (e) => {
    // console.log("in alias change");
    this.props.onAliasChange(e);
  }

  filterData = (e) => {
    e.preventDefault();
    // console.log("FilterAddress - in filterData: ", this.props.filterState);
    if (this.props.filterState.address.length === 0 && this.props.filterState.alias == undefined) {
      alert("Please enter an address or an existing alias to search for rewards");
      return false;
    }
    this.props.filterData();
  }

  render() {
    // const addKeys = [44, 10, 13];

    // console.log("in FilterAddress - this.props.filterState is: ");
    // console.log(this.props.filterState);
    return (
      <div>
        {this.renderHeader()}
        {this.props.showFilter && this.renderFilter()}
      </div>
    )
  }

  renderFilter() {
    let inputProps = {
      placeholder: '$ONE address'
    }

    return (
      <Collapse isOpened={this.props.showFilter}>
        <Form onSubmit={this.filterData}>
          <Form.Group as={Row} controlId="addressControlId">
            <Form.Label column sm={4}>Enter $ONE Address(es): </Form.Label>
            <Col sm={6}><Form.Control type="text"
              placeholder="Enter $ONE address"
              onChange={this.onAddressSelect.bind(this)}
              defaultValue={this.props.filterState.address} /></Col>
          </Form.Group>
          <Form.Group as={Row} controlId="aliasControlId">
            <Form.Label column sm={4}>Nickname/Alias (don't use real name): </Form.Label>
            <Col sm={6}><Form.Control type="text"
              placeholder="Enter nickname/alias (works across devices)"
              onChange={this.onAliasChange.bind(this)}
              defaultValue={this.props.filterState.alias} /></Col>
          </Form.Group>
          <FormGroup>
            <Button type="submit" variant="contained" color="primary" id="search"
                size="small">Search</Button>
            {'   '}
           <Button variant="contained" color="primary" id="saveAndSearch"
              onClick={this.filterDataAndSave} size="small">Save Alias in Server</Button>
          </FormGroup>
        </Form>
      </Collapse>
    );
  }

  // <Col sm={12}><TagsInput value={this.props.filterState.address} onChange={this.onAddressSelect}
  //   onlyUnique={true} maxTags={1} addOnPaste={true} defaultText inputProps={inputProps}
  //   addOnBlur={true} preventSubmit={false} defaultValue={this.props.filterState.address} /></Col>
  // renderShowFilterButton() {
  //     return (
  //       <div>
  //         <h5 style={{align: "center"}}><span><strong>My Account</strong></span>
  //         <span className="buttonWithText"><Button onClick={this.props.switchFilter} variant="contained"
  //           color="primary" id="showFilter" size="small">Show Filter</Button> {UIUtils.renderReload()}</span></h5>
  //       </div>
  //     );
  // }
  //
  renderHeader() {
      return (
        <div>
          <h5 style={{align: "center"}}><span><strong>My Account</strong></span>
          <span className="buttonWithText"><Button onClick={this.props.switchFilter} variant="contained"
            color="primary" id="showFilter" size="small">{this.props.showFilter ? "Hide Search" : "Show Search"}</Button>
            &nbsp;{UIUtils.renderReloadSize(this, 30)}</span></h5>
        </div>
      );
  }

  getFilterDisplay() {
    let filterState = this.props.filterState;
    if (typeof filterState === 'undefined') {
      return "";
    }

    let state = "";
    state = Utilities.addArrayState(filterState, "Address", "address", state);

    return state;
  }

}

export default FilterAddress;
