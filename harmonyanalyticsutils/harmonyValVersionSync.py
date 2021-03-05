import sys

from requests import Session

import commonUtils
import constants
import logUtil

logger = logUtil.l()

if len(sys.argv) < 3:
    raise Exception("correct syntax is: python3 harmonyValVersionSync.py dev/prod logsPath")


def syncValVersions():
    session = Session()

    dbValKeys = commonUtils.getDataFromGet(session, constants.listValKeys)
    # logger.info(dbValKeys)
    dbKeyValMap = commonUtils.getMapFromList(dbValKeys, "blsKey")

    metrics = commonUtils.getDataFromGet(session, constants.METRICS_URL)
    # logger.info(metrics)

    keyVersionMap = processValVersions(metrics, dbKeyValMap)
    # logger.info(keyVersionMap)
    keyVersions = list(keyVersionMap.values())
    # logger.info(keyVersions)

    logger.info("version number data: {}".format(len(keyVersions)))
    addReqDetails = {"type": "versionSync", "keyVersions": keyVersions}
    # logger.info("final request is: {}".format(addReqDetails))
    commonUtils.postReq(constants.versionSync, addReqDetails)


def processValVersions(netData, dbKeyValMap):
    valData = {}
    validators = netData["data"]

    for validator in validators:
        version = getVersionData(validator)
        if not version:
            logger.info("version not found skipping")
            continue

        blsKeyMetrics = validator["hmy_consensus_blskeys"]["metrics"]
        for metric in blsKeyMetrics:
            key = metric["labels"]["pubkey"]

            # logger.info("processing key: {}".format(key))
            if key in dbKeyValMap:
                # dbKeyValMap[key]["hPoolId"]
                valDetails = {"blsKey": key, "version": version}
                if key not in valData:
                    valData[key] = valDetails
                else:
                    existingData = valData[key]
                    if valDetails["version"] > existingData["version"]:
                        existingData["version"] = valDetails["version"]
                # logger.info(valDetails)

    return valData


def getVersionData(validator):
    version = None
    nodeMetadata = validator["hmy_node_metadata"]["metrics"]
    for metadata in nodeMetadata:
        key = metadata["labels"]["key"]
        if key == "version":
            version = getVersion(metadata["labels"]["value"])
            break
    return version


def getVersion(versionDetails):
    v1 = versionDetails.replace("Harmony (C) 2020. harmony, version ", "")
    # logger.info("v1: {}".format(v1))

    v2 = v1.split(" ")
    # logger.info("v2: {}".format(v2))

    return v2[0]


syncValVersions()
