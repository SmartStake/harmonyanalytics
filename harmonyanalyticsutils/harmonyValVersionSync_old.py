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

    data = processValVersions(metrics, dbKeyValMap)

    logger.info("version number data: {}".format(len(data)))
    addReqDetails = {"type": "versionSync", "data": data}
    # logger.info(addReqDetails)
    commonUtils.postReq(constants.versionSync, addReqDetails)


def processValVersions(netData, dbKeyValMap):
    valData = []
    validators = netData["data"]

    for validator in validators:
        valDetails = {}
        found = False

        blsKeyMetrics = validator["hmy_consensus_blskeys"]["metrics"]
        for metric in blsKeyMetrics:
            key = metric["labels"]["pubkey"]
            if key not in ["9cfd147f77c84f334bdaad0e3d85bc263c341cf25c2d30bdb4b8957eaa043a6c17010369d2c7a60e0b40633148f34390","6f05a4b70df21c5ab7d50ae639dfa879d50b26f01cb7ac47f098ca4e81df2767ff63feacaaafc3d0eb61b99f5782d384","7ce51c0b6a7f532ba775f189f9700df7c5341fa7e976b42489a469acf79f83c8b7e88a7e35080477a9bdd7cf3449be0c","83cc0b3f49335a03945b09a34f54ccd2356f2c985280c61e27732d169d1b394b688178e6a24f81e6646f4dc5e29d6f0d"]:
                logger.info("ignoring key: {}".format(key))
                # break
                continue

            logger.info("processing key: {}".format(key))
            found = True
            if key in dbKeyValMap:
                valDetails["hPoolId"] = dbKeyValMap[key]["hPoolId"]
                break

        if not found:
            continue

        nodeMetadata = validator["hmy_node_metadata"]["metrics"]
        for metadata in nodeMetadata:
            key = metadata["labels"]["key"]
            if key == "version":
                valDetails["version"] = getVersion(metadata["labels"]["value"])
                valDetails["instance"] = metadata["labels"]["instance"]
                break

        if "hPoolId" in valDetails:
            logger.info(valDetails)
            valData.append(valDetails)
        else:
            logger.info("skipping addition as validator not found: ".format(valDetails))

    return valData


def getVersion(versionDetails):
    v1 = versionDetails.replace("Harmony (C) 2020. harmony, version ", "")
    logger.info("v1: {}".format(v1))

    v2 = v1.split(" ")
    logger.info("v2: {}".format(v2))

    return v2[0]


syncValVersions()
