import sys
import time
from os.path import expanduser
import logUtil
import json

logger = logUtil.l()

with open('config.json') as config_file:
    config = json.load(config_file)

env = sys.argv[1]

USER_HOME_DIR = expanduser("~")
H_EVENT_EDIT_VALIDATOR = "EditValidator"
H_EVENT_CREATE_VALIDATOR = "CreateValidator"
H_EVENT_DELEGATE = "Delegate"
H_EVENT_UNDELEGATE = "Undelegate"
H_EVENT_COLLECT_REWARDS = "CollectRewards"


token = int(time.time())

HARMONY_HOME_DIR = USER_HOME_DIR + config["paths"]["HARMONY_HOME_RELATIVE_DIR"]
key = config["general"]["key"]

app="HARMONY"
appEnvDev = config["paths"]["appEnvDev"]
appEnv = config["paths"]["appEnvProd"]
appEnvTest = config["paths"]["appEnvTest"]
HARMONY_BASE_URL = config["paths"]["HARMONY_BASE_URL_MAINNET"]
syncAllValidators = True
if env == "dev":
    appEnv = appEnvDev
    HARMONY_BASE_URL = config["paths"]["HARMONY_BASE_URL_MAINNET"]
elif env == "test":
    appEnv = appEnvTest
    syncAllValidators = False
    HARMONY_BASE_URL = config["paths"]["HARMONY_BASE_URL_TESTNET"]

ADDRESS_URL = config["paths"]["ADDRESS_URL"]
logger.info(HARMONY_BASE_URL)

METRICS_URL = config["paths"]["METRICS_URL"]
logger.info(METRICS_URL)

DEFAULT_POOL_ID = config["general"]["DEFAULT_POOL_ID"]

BALANCE_URL="hmyv2_getBalance"
REGULAR_TRANSACTION_URL = "hmyv2_getTransactionByBlockNumberAndIndex"
STAKING_TRANSACTION_URL = "hmyv2_getStakingTransactionByBlockNumberAndIndex"
TRANSACTION_RECEIPT_URL = "hmyv2_getTransactionReceipt"
LATEST_BLOCK_URL = "hmyv2_blockNumber"
VALIDATOR_INFO_URL = "hmyv2_getValidatorInformation"
LATEST_HEADER_URL = "hmy_latestHeader"
CROSS_LINKS_URL = 'hmyv2_getLastCrossLinks'
LAST_EPOCH_BLOCK = "hmy_epochLastBlock"
STAKING_NETWORK_INFO = "hmy_getStakingNetworkInfo"
BLOCK_RANGE = "hmyv2_getBlocks"


BLOCK_HEADER = {"withSigners": False, "fullTx": False,"inclStaking": False}

HARMONY_BASE_URL_S1 = "https://api.s1.t.hmny.io"
HARMONY_BASE_URL_S2 = "https://api.s2.t.hmny.io"
HARMONY_BASE_URL_S3 = "https://api.s3.t.hmny.io"

urlMandatoryParams = "?app=" + app + "&key=" + key + "&token=" + str(token)

listUrl = appEnv + "listData" + urlMandatoryParams
listAllAddressesBasicUrl = listUrl + "&type=listAllAddressesBasic"
listDataForEpochSign = listUrl + "&type=listDataForEpochSign"
updateUrl = appEnv + "harmonyUpdateData" + urlMandatoryParams

harmonyValSyncUrl = appEnv + "harmonyValSync" + urlMandatoryParams
syncAddressesUrl = updateUrl + "&type=addressSync"
syncEpochSignUrl = updateUrl + "&type=epochSignSync"
versionSync = updateUrl + "&type=versionSync"
syncBlsPerfUrl = updateUrl + "&type=syncBlsPerfUrl"
eventUrl = listUrl + "&type=event&eventName="
eventSyncBlockHeightUrl = eventUrl + "harmonyLastSyncedEventBlockHeight"
txSyncBlockHeightUrl = eventUrl + "lastSyncedHarmonyTxBlockHeight"
syncEventsUrl = updateUrl + "&type=eventsSync"
syncShardUrl = updateUrl + "&type=shardSync"
syncTxUrl = updateUrl + "&type=txSync"
sendNotificationsUrl = appEnv + "sendNotifications" + urlMandatoryParams
tempUrl = appEnv + "temp" + urlMandatoryParams
electionSyncUrl = updateUrl + "&type=electionSync"
listDelegatesUrl = listUrl + "&type=listAllDelegates"
saveHealthCheckUrl = updateUrl + "&type=saveHealthCheck"
listAllValidatorsBasicUrl = listUrl + "&type=listAllValidatorsBasic"
blsKeySyncDetailsUrl = listUrl + "&type=blsKeySyncDetails"
shardSyncDetailsUrl = listUrl + "&type=shardSyncDetails"
listValKeys = listUrl + "&type=valKeys"


ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC = config["general"]["ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC"]
ADDRESS_MAX_RANK_FOR_TOP_SYNC = config["general"]["ADDRESS_MAX_RANK_FOR_TOP_SYNC"]

#fix if needed
MAX_LIMIT_BLOCK_SYNC=config["general"]["EVENT_SYNC_MAX_LIMIT"]
TX_SYNC_MAX_LIMIT=config["general"]["TX_SYNC_MAX_LIMIT"]
BLOCK_SYNC_MAX_LOOPS=config["general"]["EVENT_SYNC_MAX_LOOPS"]
TX_SYNC_MAX_LOOPS=config["general"]["TX_SYNC_MAX_LOOPS"]

EVENT_SYNC_MAX_LIMIT=config["general"]["EVENT_SYNC_MAX_LIMIT"]
EVENT_SYNC_MAX_LOOPS=config["general"]["EVENT_SYNC_MAX_LOOPS"]
SLEEP_TIME_FOR_MORE=config["general"]["SLEEP_TIME_FOR_MORE"]
BLOCK_TIME = config["general"]["BLOCK_TIME"]

H_STATUS_ELECTED = "Elected"
H_STATUS_ELIGIBLE = "Eligible"
H_STATUS_NOT_ELIGIBLE = "NotEligible"
KEY_BAD_PERF_THRESHOLD = 0.98

TX_STAKING = "staking"
TX_REGULAR = "regular"
TX_STATUS_SUCCESS = "Success"
TX_STATUS_FAILED = "Failed"
TX_STATUS_UNKNOWN = "Unknown"

STAKING_START_BLOCK = 3000000

H_BLOCKS_IN_EPOCH = 32768
H_BLOCK_TIME = 2

