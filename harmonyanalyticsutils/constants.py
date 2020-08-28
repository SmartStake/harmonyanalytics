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
H_EVENT_DELEGATE = "Delegate"
H_EVENT_UNDELEGATE = "Undelegate"
H_EVENT_COLLECT_REWARDS = "CollectRewards"


token = int(time.time())

HARMONY_HOME_DIR = USER_HOME_DIR + config["paths"]["HARMONY_HOME_RELATIVE_DIR"]
key = config["general"]["key"]

app="HARMONY"
appEnvDev = config["paths"]["appEnvDev"]
appEnv = config["paths"]["appEnvProd"]
if env == "dev":
    appEnv = appEnvDev

ADDRESS_URL = config["paths"]["ADDRESS_URL"]
HARMONY_BASE_URL = config["paths"]["HARMONY_BASE_URL"]
logger.info(HARMONY_BASE_URL)

DEFAULT_POOL_ID = config["general"]["DEFAULT_POOL_ID"]

BALANCE_URL="hmyv2_getBalance"
STAKING_TRANSACTION_URL = "hmyv2_getStakingTransactionByBlockNumberAndIndex"
TRANSACTION_RECEIPT_URL = "hmyv2_getTransactionReceipt"
LATEST_BLOCK_URL = "hmyv2_blockNumber"

urlMandatoryParams = "?app=" + app + "&key=" + key + "&token=" + str(token)

listUrl = appEnv + "listData" + urlMandatoryParams
listAllAddressesBasicUrl = listUrl + "&type=listAllAddressesBasic"
updateUrl = appEnv + "harmonyUpdateData" + urlMandatoryParams
syncAddressesUrl = updateUrl + "&type=addressSync"
eventUrl = listUrl + "&type=event&eventName="
eventSyncBlockHeightUrl = eventUrl + "harmonyLastSyncedEventBlockHeight"
syncEventsUrl = updateUrl + "&type=eventsSync"
listDelegatesUrl = listUrl + "&type=listAllDelegates"
saveHealthCheckUrl = updateUrl + "&type=saveHealthCheck"


ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC = config["general"]["ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC"]
ADDRESS_MAX_RANK_FOR_TOP_SYNC = config["general"]["ADDRESS_MAX_RANK_FOR_TOP_SYNC"]

MAX_LIMIT_EVENT_SYNC=config["general"]["MAX_LIMIT_EVENT_SYNC"]
EVENT_SYNC_MAX_LOOPS=config["general"]["EVENT_SYNC_MAX_LOOPS"]
SLEEP_TIME_FOR_MORE=config["general"]["SLEEP_TIME_FOR_MORE"]
BLOCK_TIME = config["general"]["BLOCK_TIME"]

