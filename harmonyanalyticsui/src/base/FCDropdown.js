import React from 'react';
import {FormGroup, ControlLabel, FormControl} from 'react-bootstrap';

class FCDropdown extends React.Component {
  render () {
    // let all = '<option>All</option>';
    // console.log("hide all: " + this.props.hideAll);
    // if (this.props.hideAll) {
    //   console.log("removing all");
    //   all = "";
    // }

    return (
      <FormControl componentClass="select" bsSize="small" defaultValue={this.props.defaultValue}
        width={200} value={this.props.value} onChange = {this.props.onSelect}>
        {this.getDefault()}
        {this.props.values.map((value, index) => {
            return (<option key={value.description} value={value.description}>{value.description}</option>)
        })}
      </FormControl>
    );
  }

  getDefault() {
    if (this.props.dontAddAll) {
      return <option></option>;
    }
    return <option>All</option>;
  }
}

export default FCDropdown;
