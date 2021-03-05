import sys

from requests import Session

import commonUtils
import constants
import logUtil

logger = logUtil.l()

if len(sys.argv) < 3:
    raise Exception("correct syntax is: python3 harmonyNetworkStats.py dev/prod logsPath")


def syncStats():
    session = Session()

    dbData = commonUtils.getDataFromGet(session, constants.listDataForEpochSign)
    dbValidators = dbData["validators"]
    syncedTillEpoch = dbData["epoch"]
    currentEpoch = commonUtils.getHarmonyResultDataFromPost(session, "hmyv2_getEpoch", [])
    prevEpoch = currentEpoch - 1

    logger.info("prevEpoch: {} syncedTillEpoch: {}".format(prevEpoch, syncedTillEpoch))
    if prevEpoch <= syncedTillEpoch:
        logger.info("skipping processing as data is already synced up. prevEpoch <= syncedTillEpoch")
        return

    allData = []
    for epoch in range(syncedTillEpoch + 1, prevEpoch + 1):
        # logger.info("processing epoch: {}".format(epoch))
        data = processEpoch(session, epoch, dbValidators)
        allData.append(data)

    logger.info("# of epochs processed: {}".format(len(allData)))
    addReqDetails = {"type": "epochSignSync", "allData": allData, "epoch": prevEpoch}
    # logger.info(addReqDetails)
    commonUtils.postReq(constants.syncEpochSignUrl, addReqDetails)


def processEpoch(session, epoch, dbValidators):
    totalAskedToSign, totalSigned = 0, 0
    valData = []
    for validator in dbValidators:
        askedToSign, signed = getSignDetails(session, validator["address"], epoch)
        if not askedToSign:
            continue

        totalAskedToSign += askedToSign
        totalSigned += signed

        signPer = 0
        if askedToSign != 0:
            signPer = round(100 * signed/askedToSign, 2)
        valData.append({"hPoolId": validator["hPoolId"],
            "askedToSign": askedToSign, "signed": signed,
            "signPer": signPer})

    signRate = 0
    if totalAskedToSign != 0:
        signRate = 100 * totalSigned / totalAskedToSign
    return {"epoch": epoch, "signRate": signRate, "validators": valData}



def getSignDetails(session, address, prevEpoch):
    # logger.info("processing address: {}".format(address))
    inputData = [address]
    # https://api.hmny.io/?version=latest#9d17f3bf-eeff-4be8-abe5-328467a9e5ec
    data = commonUtils.getHarmonyResultDataFromPost(session, constants.VALIDATOR_INFO_URL, inputData)
    # logger.info(data)

    epochBlocks = data["lifetime"]["epoch-blocks"]

    if not epochBlocks:
        return None, None

    for blockData in epochBlocks:
        if blockData["epoch"] == prevEpoch:
            blocks = blockData["blocks"]
            return blocks["to-sign"], blocks["signed"]

    return None, None


syncStats()
