import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import SpeedDial from '@material-ui/lab/SpeedDial';
import SpeedDialIcon from '@material-ui/lab/SpeedDialIcon';
import SpeedDialAction from '@material-ui/lab/SpeedDialAction';
import AssessmentIcon from '@material-ui/icons/Assessment';
import EventAvailableIcon from '@material-ui/icons/EventAvailable';
import PeopleIcon from '@material-ui/icons/People';
import MoneyIcon from '@material-ui/icons/Money';
import ThumbsUpDownIcon from '@material-ui/icons/ThumbsUpDown';
import FormatListNumberedIcon from '@material-ui/icons/FormatListNumbered';

const useStyles = makeStyles((theme) => ({
  root: {
      zIndex: theme.zIndex.speedDial,
      display: 'flex',
      alignItems: 'right',
      pointerEvents: 'none',
      position: 'fixed',
      top: 100,
      left: window.innerWidth - 100,
    },
  // root: {
  //   height: 400,
  //   transform: 'translateZ(0px)',
  //   flexGrow: 1,
  // },
  // speedDial: {
  //   position: 'absolute',
  //   bottom: theme.spacing(2),
  //   right: theme.spacing(2),
  // },
}));

// const actions = [
//   { action: "/val", name: 'Summary',  },
//   { action: "/valstats", name: 'Stats' },
//   { action: "/delegates", name: 'Delegates' },
//   { action: "/events", name: 'Events' },
//   { action: "/keys", name: 'Keys' },
// ];

// const actions = [
//   { icon: <AssessmentIcon />, name: 'Stats', action: 'showStats' },
//   { icon: <PeopleIcon />, name: 'Delegates' },
//   { icon: <EventAvailableIcon />, name: 'Events' },
//   { icon: <VpnKeyIcon />, name: 'BLS Key Performance' },
// ];

export default function NetworkAction(data) {
  const classes = useStyles();
  const [direction, setDirection] = React.useState('down');
  const [open, setOpen] = React.useState(false);
  const [hidden, setHidden] = React.useState(false);

  const handleVisibility = () => {
    setHidden((prevHidden) => !prevHidden);
  };


  const handleOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const showStats = () => {
    document.location="/stats/";
  }

  const showHistory = () => {
    document.location="/history/";
  }

  const showRichlist = () => {
    document.location="/richlist/";
  }

  const showEvents = () => {
    document.location="/networkEvents/";
  }

  const showCalc = () => {
    document.location="/calc/";
  }

  const showElection = () => {
    document.location="/election/";
  }

  return (
    <div className={classes.root}>
      <SpeedDial ariaLabel="SpeedDial tooltip example"
        hidden={hidden} icon={<SpeedDialIcon />}
        onClose={handleClose} onOpen={handleOpen} open={open}
        direction={direction}>
          <SpeedDialAction key="Stats" icon={<FormatListNumberedIcon />} tooltipOpen tooltipTitle="Stats" onClick={showStats}/>
          <SpeedDialAction key="History" icon={<AssessmentIcon />} tooltipOpen tooltipTitle="History" onClick={showHistory}/>
          <SpeedDialAction key="Richlist" icon={<PeopleIcon />} tooltipOpen tooltipTitle="Richlist" onClick={showRichlist}/>
          <SpeedDialAction key="Events" icon={<EventAvailableIcon />} tooltipOpen tooltipTitle="Events" onClick={showEvents}/>
          <SpeedDialAction key="Calculator" icon={<MoneyIcon />} tooltipOpen tooltipTitle="Calculator" onClick={showCalc}/>
          <SpeedDialAction key="Next Election" icon={<ThumbsUpDownIcon />} tooltipOpen tooltipTitle="Next Election" onClick={showElection}/>
      </SpeedDial>
    </div>
  );
}
/*
return (
  <div className={classes.root}>
    <SpeedDial ariaLabel="SpeedDial tooltip example"
      className={classes.speedDial} hidden={hidden} icon={<SpeedDialIcon />}
      onClose={handleClose} onOpen={handleOpen} open={open}
      direction={direction}>
      {actions.map((action) => (
        <SpeedDialAction
          key={action.name}
          icon={action.icon}
          tooltipTitle={action.name}
          onClick={handleClose}
        />
      ))}
    </SpeedDial>
  </div>
);
*/
