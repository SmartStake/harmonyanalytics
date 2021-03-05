import sys
import time

from requests import Session

import commonUtils
import constants
import logUtil

logger = logUtil.l()

if len(sys.argv) < 4:
    raise Exception("correct syntax is: python harmonySync dev/prod logsPath val/del")

mode = sys.argv[3]

MODE_VAL="val"
MODE_DEL="del"
logger.info("mode: " + mode)


def syncValidators():
    session = Session()

    allValidators, delegateCount, allDelegations = getAllValidators(session)
    logger.info("unique delegates are: {}".format(delegateCount))

    syncValidator(session, allValidators, delegateCount)


def syncValidator(session, allValidators, delegateCount):
    stakingInfo = getStakingNetworkInfo(session, delegateCount)
    epochInfo = getEpochInfo(session, stakingInfo)

    reqDetails = {"type": "valSync",
        "stakingInfo": stakingInfo,
        "epochInfo": epochInfo,
        "allValidators": allValidators
    }

    # logger.info(reqDetails)

    commonUtils.postReq(constants.harmonyValSyncUrl, reqDetails)


def getAllValidators(session):
    logger.info("obtaining list of all validators and delegations")
    inputData = [-1]
    data = commonUtils.getHarmonyDataFromPost(session, "hmyv2_getAllValidatorInformation", inputData)

    # data = {}
    # logger.info(data)
    logger.info("starting processing")

    vData = data["result"]

    validators = []
    i = 0

    allDelegates = set()
    allDelegations = []

    minValData = 110
    currentValData = 0
    skippedVal = 0

    for validatorData in vData:
        # if i >= 0:
        #     continue

        validator = validatorData["validator"]
        # logger.info(str(i) + " - processing validator ")
        # logger.info(validator)

        i += 1
        # validator = json.loads(validatorData)

        currentPerf = {"currentEpochSigned": 0, "currentEpochToSign": 0, "currentEpochSigningPercentage": 0}
        if validatorData["current-epoch-performance"]:
            perf = validatorData["current-epoch-performance"]["current-epoch-signing-percent"]
            signPercent = float(perf["current-epoch-signing-percentage"]) * 100
            currentPerf = {"currentEpochSigned": perf["current-epoch-signed"],
                "currentEpochToSign": perf["current-epoch-to-sign"],
                "currentEpochSigningPercentage": signPercent,
            }

        lifetimePerf = {"totalRewards": 0, "lifetimeToSign": 0, "lifetimeSigned": 0, "lifetimeApr": 0}
        if validatorData["lifetime"]:
            perf = validatorData["lifetime"]
            lifetimePerf = {"totalRewards": commonUtils.divideByTenPower18(perf["reward-accumulated"]),
                "lifetimeToSign": perf["blocks"]["to-sign"],
                "lifetimeSigned": perf["blocks"]["signed"],
                "lifetimeApr": perf["apr"],
            }

        # logger.info("lifetime is: ")
        # logger.info(lifetimePerf)
        elected = "False"
        if validatorData["epos-status"] == "currently elected":
            elected = "True"
        booted = "False"
        if validatorData["booted-status"] is not None:
            booted = "True"
        # "elected": validatorData["currently-in-committee"],

        delegations, selfStake, delegateAddresses, delegateCount = getDelegations(validator["delegations"], validator["address"])
        vReq = {
            "address": validator["address"], "name": validator["name"], 
            "identity": validator["identity"], 
            "blsPublicKeys": validator["bls-public-keys"],
            "minSelfDelegation": commonUtils.divideByTenPower18(validator["min-self-delegation"]),
            "maxTotalDelegation": commonUtils.divideByTenPower18(validator["max-total-delegation"]),
            "website": validator["website"], "currentPerf": currentPerf,
            "securityContact": validator["security-contact"], 
            "details": validator["details"], 
            "fee": validator["rate"], "maxFee": validator["max-rate"],
            "feeChangeRate": validator["max-change-rate"], 
            "lastUpdateBlock": validator["update-height"],
            "creationBlock": validator["creation-height"], 
            "totalStaked": commonUtils.divideByTenPower18(validatorData["total-delegation"]),
            "elected": elected,
            "booted": booted,
            "uniqueDelegates": delegateCount,
            "lifetimePerf": lifetimePerf,
            "selfStake": selfStake,
            "activeStatus":  validatorData["active-status"],
            "status": commonUtils.getStatus(validatorData["epos-status"])
        }

        currentValData += 1
        # if constants.syncAllValidators or vReq["status"] != constants.H_STATUS_NOT_ELIGIBLE:
        if constants.syncAllValidators or vReq["status"] == constants.H_STATUS_ELECTED \
                or vReq["status"] == constants.H_STATUS_ELIGIBLE or currentValData < minValData:
            validators.append(vReq)
            allDelegates = allDelegates.union(delegateAddresses)
            allDelegations.append(delegations)
        else:
            skippedVal += 1

    logger.info("looped through all validators : " + str(len(validators)))
    logger.info("skipped validators : " + str(skippedVal))

    return validators, len(allDelegates), allDelegations


def getDelegations(inputData, address):
    # logger.info("in getDelegations for: {}".format(address))
    delegations = []
    delegateAddresses = set()
    selfStake = 0
    delegateCount = 0

    for d in inputData:
        delAddress = d["delegator-address"]

        if address == delAddress:
            selfStake = commonUtils.divideByTenPower18(d["amount"])

        amount = commonUtils.divideByTenPower18(d["amount"])
        delegation = {
            "address": d["delegator-address"],
            "amount": amount,
            "validator": address,
            "reward": commonUtils.divideByTenPower18(d["reward"]),
        }

        if amount > 0:
            delegateCount += 1
            delegations.append(delegation)
            delegateAddresses.add(delAddress)

    return delegations, selfStake, delegateAddresses, delegateCount


def getEpochInfo(session, stakingInfo):
    logger.info("getting staking information")
    currentEpoch = commonUtils.getHarmonyResultDataFromPost(session, "hmyv2_getEpoch", [])
    # lastBlockOfEpoch = getDataFromPost(session, "hmy_epochLastBlock", [])
    epochLastBlock = stakingInfo["epochLastBlock"]
    latestBlock = commonUtils.getHarmonyResultDataFromPost(session, "hmyv2_blockNumber", [])
    timeLeft = ((epochLastBlock - latestBlock) * constants.BLOCK_TIME)
    logger.info("timeLeft for current epoch - {}".format(timeLeft))
    nextEpochTime = int(time.time()) + timeLeft

    epochInfo = {
        "currentEpoch": currentEpoch,
        "latestBlock": latestBlock,
        "nextEpochTime": nextEpochTime,
    }

    # logger.info(epochInfo)

    return epochInfo


def getStakingNetworkInfo(session, delegateCount):
    logger.info("getting staking information")
    data = commonUtils.getHarmonyDataFromPost(session, constants.STAKING_NETWORK_INFO, [])

    stakingData = data["result"]

    stakingInfo = {
        "totalSupply": stakingData["total-supply"],
        "circulatingSupply": stakingData["circulating-supply"],
        "totalStake": commonUtils.divideByTenPower18(stakingData["total-staking"]),
        "medianRawStake": commonUtils.divideByTenPower18(stakingData["median-raw-stake"]),
        "epochLastBlock": stakingData["epoch-last-block"],
        "uniqueDelegates": delegateCount,
    }

    return stakingInfo


def syncDelegations():
    logger.info("obtaining db delegates")
    session = Session()
    dbDelegates = commonUtils.getDataFromGet(session, constants.listDelegatesUrl)
    # logger.info(dbDelegates)

    logger.info("obtaining network delegates")
    allDelegations = getAllDelegations(session)
    # logger.info(allDelegations)

    logger.info("processing delegates")
    updates, inserts, deletes = processDelegations(allDelegations, dbDelegates)
    logger.info("after processing delegates")

    logger.info("deletes len is: {}".format(len(deletes)))

    logger.info("syncing all delegations - delegateSync")
    delReqDetails = {"type": "delegateSync",
        "updates": updates,
        "inserts": inserts,
        "deletes": deletes
    }
    commonUtils.postReq(constants.updateUrl, delReqDetails)
    logger.info("after syncing all delegations - delegateSync")


def processDelegations(allDelegations, dbDelegates):
    # logger.info("allDelegations: {}, dbDelegates: {}".format(allDelegations, dbDelegates))
    dbDelegatesMap = getMapFromList(dbDelegates)

    logger.info("allDelegations: {}".format(len(allDelegations)))

    updates = []
    inserts = []

    for d in allDelegations:
        amount = d["amount"]
        reward = d["reward"]
        key = d["address"] + "-" + d["validator"]

        if key in dbDelegatesMap:
            dbDelegate = dbDelegatesMap[key]

            if int(amount) != int(dbDelegate["stake"]) or int(reward) != int(dbDelegate["stake"]):
                # logger.info("there are changes in this address, sync it")
                d["hPoolId"] = dbDelegate["hPoolId"]
                d["poolDelId"] = dbDelegate["poolDelId"]
                updates.append(d)
            # else:
            # logger.info("no changes in this address, leave it as is")

            del dbDelegatesMap[key]
        else:
            inserts.append(d)

    # logger.info("updates are:")
    # logger.info(updates)
    #
    # logger.info("inserts are:")
    # logger.info(inserts)

    deletes = []
    for d in dbDelegatesMap.values():
        deletes.append(d)

    # logger.info("deletes are:")
    # logger.info(deletes)
    return updates, inserts, deletes


def getAllDelegations(session):
    logger.info("obtaining list of all delegations")
    inputData = [-1]
    data = commonUtils.getHarmonyDataFromPost(session, "hmyv2_getAllValidatorInformation", inputData)
    logger.info("starting processing")

    vData = data["result"]
    i = 0

    allDelegations = []

    for validatorData in vData:
        validator = validatorData["validator"]

        # if validator["address"] != 'one1qk7mp94ydftmq4ag8xn6y80876vc28q7s9kpp7':
        #     continue

        logger.info(str(i) + " - processing validator for delegations ")
        # logger.info(validator)

        i += 1

        delegations, selfStake, delegateAddresses, delegateCount = getDelegations(validator["delegations"], validator["address"])
        allDelegations.extend(delegations)

    return allDelegations


def getMapFromList(listData):
    mapObj = {}

    for item in listData:
        keyValue = item["address"] + "-" + item["validator"]
        mapObj[keyValue] = item

    return mapObj


if mode == MODE_VAL:
    logger.info("syncing all validators")
    syncValidators()
    logger.info("after syncing all validators")
elif mode == MODE_DEL:
    logger.info("syncing all delegators")
    syncDelegations()
    logger.info("after syncing all delegators")
else:
    raise Exception("correct syntax is: python3.7 harmonySync dev/prod logsPath val/del")
