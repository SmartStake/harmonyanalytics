APPS = {"HARMONY": "HARMONY"}

HARMONY = "HARMONY"

CONTACT_ADDRESS = "@bigb4ever"

H_ELECTED = "Elected"
H_ELIGIBLE = "Eligible"
H_NOT_ELIGIBLE = "NotEligible"

ALL_ELIGIBLE_CLAUSE = "('Elected','Eligible') "
ALL_ELIGIBLE = "AllEligible"
ALL_STATUS = "All"

H_EPOCH_MODE = "EPOCH"
H_HOUR_MODE = "HOUR"

H_BLOCKS_IN_EPOCH = 16384
H_BLOCK_TIME = 5
# (86400 * 365) /(16384 * 8)
H_EPOCHS_IN_YEAR = round((86400 * 365) /(H_BLOCKS_IN_EPOCH * H_BLOCK_TIME))
H_FIRST_EPOCH=190
H_EPOCHS_FOR_AVERAGE=20

H_HISTORY_NETWORK='Network'
H_HISTORY_VALIDATOR='Validator'
H_HISTORY_ADDRESS='Address'
H_HISTORY_NETWORK_VALUES = ["totalStake", "circulatingSupply", "currentRewardRate", "totalValidators", "btcPrice", "medianRawStake"]
H_HISTORY_ADDRESS_VALUES= ["totalStake", "totalBalance", "totalRewards"]


H_ADDRESS_HISTORY_SYNC='AddressHistory'
H_MIN_BAL_FOR_HISTORY="1000"
H_MIN_BLOCKS_FOR_CURRENT_EPOCH_APR=800
H_POOL_ID_SS = 42

H_EVENT_FEE_INCREASE = "Fee_Increase"
H_EVENT_FEE_DECREASE = "Fee_Decrease"
H_EVENT_EDIT_VALIDATOR = "EditValidator"
H_EVENT_DELEGATE = "Delegate"
H_EVENT_UNDELEGATE = "Undelegate"
H_EVENT_COLLECT_REWARDS = "CollectRewards"

EVENT_LAST_SYNCED_EVENT_BLOCK_HEIGHT = "harmonyLastSyncedEventBlockHeight"