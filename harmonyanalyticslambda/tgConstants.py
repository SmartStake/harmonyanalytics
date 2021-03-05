import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ARROW_UP = u'\U00002B06'
ARROW_DOWN = u'\U00002B07'
TOOLS = u'\U0001F6E0'
CHECK_MARK = u'\U00002705'
CROSS_MARK = u'\U0000274C'
MONEY_BAG = u'\U0001F4B0'
POSITIVE_FLAG= u'\U0001F7E2'
NEGATIVE_FLAG= u'\U0001F534'
WARNING_SIGN = u'\U000026A0'
BOOTED = u'\U000026D4'


ENABLE_CMD_KEY = "Enable"
DISABLE_CMD_KEY = "Disable"
ENABLE_KEY = "Enable"
DISABLE_KEY = "Disable"

NOTIFY_DEL = "notifyDel"
NOTIFY_UNDEL = "notifyUndel"
NOTIFY_KEY_CHANGES = "notifyKeyChanges"
NOTIFY_KEY_PERF = "notifyKeyPerf"
NOTIFY_LARGE = "notifyLarge"
NOTIFY_VALIDATOR_PERF = "notifyValPerf"
NOTIFY_ELECTION = "notifyElection"
NOTIFY_EPOCH = "notifyEpoch"

NOTIFY_ADDRESS = "notifyAddress"
NOTIFY_FEE = "notifyFee"
NOTIFY_DEL_PERFORMANCE = "notifyDelPerf"

validatorNotifications = {NOTIFY_DEL: "Delegation Notification",
			NOTIFY_UNDEL: "Undelegation Notification",
			NOTIFY_KEY_CHANGES: "Key Change Notification",
			NOTIFY_KEY_PERF: "Key Performance Notification",
			NOTIFY_LARGE: "Large Trans Notification",
			NOTIFY_ELECTION: "Election Notification",
			NOTIFY_VALIDATOR_PERF: "Validator Performance Notification",
			NOTIFY_EPOCH: "Epoch Notification",
		}

delegateNotifications = {
			NOTIFY_ADDRESS: "Address Notification",
			NOTIFY_FEE: "Fee Change Notification",
			NOTIFY_DEL_PERFORMANCE: "Delegation Performance Notification",
		}

allNotificationsKeys = {NOTIFY_DEL: "Delegation Notification",
			NOTIFY_UNDEL: "Undelegation Notification",
			NOTIFY_KEY_CHANGES: "Key Change Notification",
			NOTIFY_KEY_PERF: "Key Performance Notification",
			NOTIFY_LARGE: "Large Trans Notification",
			NOTIFY_ELECTION: "Election Notification",
			NOTIFY_EPOCH: "Epoch Notification",
			NOTIFY_VALIDATOR_PERF: "Validator Performance Notification",
			NOTIFY_FEE: "Fee Change Notification",
			NOTIFY_ADDRESS: "Address Notification",
			NOTIFY_DEL_PERFORMANCE: "Delegation Performance Notification"
		}

MAX_LENGTH_PER_RESPONSE = 4000
MAIN_MENU = "Main Menu"

rootNotifications = {"root": "notifications",
			 "delegate": "Delegate Notifications",
			 "validator": "Validator Notifications"}

