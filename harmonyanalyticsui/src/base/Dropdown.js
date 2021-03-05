import React from 'react';
import {Form} from 'react-bootstrap';

class Dropdown extends React.Component {
  render () {
    let values = this.props.values;
    let optionItems = values.map((value) =>
        <option key={value.code} value={value.code}>{value.description}</option>
    );

    return (
      <Form.Control as="select" size="sm" defaultValue={this.props.defaultValue} onChange={this.props.onSelect}>
        {this.createExtra()}
        {optionItems}
      </Form.Control>
    );
  }

  createExtra() {
    if (this.props.addBlank === true) {
      return <option value="0"></option>;
    } else if (this.props.addAll === true) {
      return <option>All</option>;
    }
    return "";
  }
}

export default Dropdown;
