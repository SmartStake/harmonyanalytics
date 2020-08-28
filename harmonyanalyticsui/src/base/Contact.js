import React from 'react';

import Fab from '@material-ui/core/Fab';
// import AddIcon from '@material-ui/icons/Add';
// import Icon from '@material-ui/core/Icon';
import TelegramIcon from '@material-ui/icons/Telegram';

class Contact extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      showGuide: false,
    }
  }

  render() {
    // const styles = theme => ({
    //   root: {
    //     width: '100%',
    //     marginTop: theme.spacing.unit * 3,
    //     overflowX: 'auto',
    //   },
    //   fab: {
    //       position: "fixed",
    //       bottom: theme.spacing.unit * 2,
    //       right: theme.spacing.unit * 3
    //   },
    //   extendedIcon: {
    //     marginRight: theme.spacing.unit,
    //   },
    // });
    const style = {
        margin: 0,
        top: 'auto',
        right: 20,
        bottom: 45,
        left: 'auto',
        position: 'fixed',
    };
    const astyle = {
      "color": "inherit",
      "textDecoration": "inherit",
    }

    return (
      <div>
        <Fab color="primary" aria-label="Add" style={style} size="small">
          <a href="https://t.me/SmartStake" style={astyle} target="_blank">
            <TelegramIcon />
          </a>
        </Fab>
      </div>
    );
  }

  gotoTg() {
    window.open("https://t.me/SmartStake");
  }
}

export default Contact;
