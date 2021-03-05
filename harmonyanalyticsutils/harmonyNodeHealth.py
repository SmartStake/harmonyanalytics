import datetime
import json
import subprocess
import sys

import commonUtils
import constants
import logUtil

logger = logUtil.l()

if len(sys.argv) < 5:
    raise Exception("correct syntax is: python harmonyNodeHealth dev/prod logsPath nodeName shardId")

harmonyCmdPath = constants.HARMONY_HOME_DIR + 'hmy'
harmonyNodeUrl = '--node=https://api.s{}.t.hmny.io'

today = datetime.date.today()

#python harmonyNodeHealth.py
node_name = sys.argv[3]
shardId = sys.argv[4]

harmonyNodeUrl = harmonyNodeUrl.format(shardId)
logger.info("shard url: " + harmonyNodeUrl)


def check_health():
    logger.info(node_name + " - starting health check")

    nodeStatus = getNodeStatus()
    nodeHeight = nodeStatus["blockNumber"]
    logger.info("node nodeHeight is: " + str(nodeHeight))
    shardId = nodeStatus["shardID"]

    networkStatus = getNetworkStatus()
    networkHeight = networkStatus["shard-chain-header"]["block-number"]
    # logger.info(node_height)
    logger.info(node_name + " - networkHeight is: " + str(networkHeight))

    blockDiff = int(networkHeight) - int(nodeHeight)

    logger.info("network block height - node height: " + str(blockDiff))
    logger.error("%s - block diff - %s - network block height - %s, node height - %s ",
                 node_name, blockDiff, networkHeight, nodeHeight)

    saveHealthCheck(blockDiff, networkHeight, nodeHeight, shardId)

    logger.info(node_name + " - finished successfully")


def saveHealthCheck(blockDiff, networkHeight, nodeHeight, shardId):
    logger.debug("in save_health_check")
    # data_json = '{"nodeName": "' + node_name + '", "symbol": "AION", "checkupTime": "' + str(datetime.now()) + \
    #             '", "networkBlockHeight": "' + block_height + '", "nodeBlockHeight": "' + node_height + \
    #             '", "heightGap": "' + block_diff + '", "lastBlockValidated": 120}'
    reqData = {
        "type": "saveHealthCheck",
        "nodeName": node_name,
        "symbol": constants.app,
        "checkupTime": datetime.datetime.now(),
        "networkBlockHeight": networkHeight,
        "nodeBlockHeight": nodeHeight,
        "heightGap": blockDiff,
        "poolId": constants.DEFAULT_POOL_ID,
        "shardId": shardId
    }

    # "key": key,
    # "token": token,
    logger.debug(reqData)
    commonUtils.postReq(constants.saveHealthCheckUrl, reqData)

# def postReq(url, reqData):
#     data_json = jsondumps(reqData)
#     logger.debug("after json dump")
#     logger.debug(data_json)
#     session = Session()
#     logger.debug("calling save health check:")
#     logger.debug(url)
#     #response = session.post('https://dev.smartstakeapi.com/saveHealthCheck',
#     #                        data=data_json, allow_redirects=False)
#
#     response = session.post(url,
#                             data=data_json, allow_redirects=False)
#     logger.debug("save health check response is:")
#     logger.debug(response)


def getNodeStatus():
    # ./hmy blockchain latest-header
    nodeHeaderCmd = [harmonyCmdPath, 'blockchain', 'latest-header']
    # logger.info("obtaining nodeHeader: " + str(nodeHeaderCmd))
    nodeHeader = execCmdJson(nodeHeaderCmd)
    # logger.info("nodeHeader: ")
    # logger.info(nodeHeader)

    # return nodeHeader["result"]["blockNumber"]
    return nodeHeader["result"]


def getNetworkStatus():
    # ./hmy --node="https://api.s2.t.hmny.io" blockchain latest-headers
    networkHeaderCmd = [harmonyCmdPath, harmonyNodeUrl, 'blockchain', 'latest-headers']
    # logger.info("obtaining networkHeader: " + str(networkHeaderCmd))
    networkHeader = execCmdJson(networkHeaderCmd)
    # logger.info("networkHeader: ")
    # logger.info(networkHeader)

    return networkHeader["result"]


def execCmdJson(args):
    return json.loads(execCmd(args))


def execCmd(args):
    out = subprocess.Popen(args,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # logger.info("calling communicate")
    stdout,stderr = out.communicate()
    resp = stdout.decode().replace("\n", "")

    return resp


# def default(o):
#     if type(o) is datetime.date or type(o) is datetime.datetime:
#         return o.isoformat()
#     if isinstance(o, float):
#         return round(o, 8)
#     if type(o) is decimal.Decimal:
#         return str(o)
#
#
# def jsondumps(o):
#     # return json.dumps(o)
#     return json.dumps(o, default=default)


check_health()
