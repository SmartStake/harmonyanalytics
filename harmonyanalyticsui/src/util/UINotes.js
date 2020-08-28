import React from 'react';
import {CollapsibleComponent, CollapsibleHead, CollapsibleContent} from 'react-collapsible-component';


class UINotes extends React.Component {

  static getPoolNote() {
    return (<div align="left">
      <hr/>
      <CollapsibleComponent name="note">
        <CollapsibleHead isExpanded={false}><font color="black"><b>Screen Guide</b> - click here for details</font>
        </CollapsibleHead>
        <CollapsibleContent isExpanded={false}>
          <ul>
          </ul>
        </CollapsibleContent>
      </CollapsibleComponent>
    </div>);
  }

  static getDelegateHelp() {
    return (<div>
      <hr/>
      <CollapsibleComponent name="help">
        <CollapsibleHead isExpanded={false}><font color="black"><b>Screen Guide</b> - click here for details</font>
        </CollapsibleHead>
        <CollapsibleContent isExpanded={false}>
            <ul>
            </ul>
        </CollapsibleContent>
      </CollapsibleComponent>
    </div>);
  }

}

export default UINotes;
