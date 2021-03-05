export default {
  menuStyle:
    {borderRadius: '3px',  boxShadow: '0 2px 12px rgba(0, 0, 0, 0.1)',
    background: 'rgba(255, 255, 255, 1)', padding: '2px 0',
    fontSize: '90%', position: 'fixed',
    overflow: 'auto', maxHeight: '50%', // TODO: don't cheat, let it flow to the bottom
    zIndex: '998'},
  notEligibleStatus: "NotEligible",
  MEDIUM: 1000,
  SMALL: 600,
  SLOTS: 640,
  // FIRST_UNELECTED_SLOT: 641,
  BLOCK_TIME: 2,
  ES_ELECTED: "elected",
  ES_NOT_ELECTED: "not_elected",
  ES_PARTIALLY_ELECTED: "partially_elected",
  ES_NOT_POSSIBLE: "not_possible"
};
