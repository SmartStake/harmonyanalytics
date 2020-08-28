import datetime
import logging
import time

import auditUtils
import commonUtils
import constants
import dbUtil
import eventName
import hConstants
import harmonyData
import harmonyEvents
import harmonyHistory
import restUtils
import tables
from utilities import jsondumps, getResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = constants.HARMONY


def syncValidators(conn, app, data, event):
    logger.info("in harmony validator sync")
    startTime = datetime.datetime.now()
    # conn = dbUtil.getConnection()
    # currentTime = datetime.datetime.now()
    currentHour = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
    previousHour = currentHour - datetime.timedelta(hours=1)
    # logger.info("currentTime: {}".format(currentTime))

    # logger.info("loading request")
    # body = json.loads(event["body"])

    validators = data["allValidators"]
    stakingInfo = data["stakingInfo"]
    epochInfo = data["epochInfo"]
    currentEpoch = epochInfo["currentEpoch"]

    logger.info("total number of validators returned is: " + str(len(validators)))

    currentEpochValMap = getCurrentValMap(conn, currentEpoch, None)
    previousEpochValMap = getCurrentValMap(conn, currentEpoch-1, None)
    currentHourValMap = getCurrentValMap(conn, currentEpoch, currentHour)
    previousHourValMap = getCurrentValMap(conn, None, previousHour)

    currentCoinStat = commonUtils.getCoinStat(conn, app)
    completionFactor, enoughDataForCurrentApr = getBlockCompletionFactor(epochInfo, stakingInfo, currentCoinStat, currentEpoch)
    logger.info("is enough data captured for current apr: {}".format(enoughDataForCurrentApr))

    i = 0
    for validator in validators:
        address = validator["address"]
        logger.info("{} - processing validator: {}".format(i, address))
        # logger.info(validator)
        i += 1

        blsKeyCount = len(validator["blsPublicKeys"])
        optimalBlsKeyCount, bidPerSeat = getOptimalBlsKeyCount(stakingInfo, blsKeyCount, validator)
            
        hPoolId = syncValidator(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat)

        currEpochSummary = getValidatorDetails(currentEpochValMap, hPoolId)
        prevEpochSummary = getValidatorDetails(previousEpochValMap, hPoolId)
        syncValidatorEpochSummary(conn, validator, blsKeyCount, bidPerSeat, hPoolId, currEpochSummary,
            prevEpochSummary, currentEpoch, completionFactor, enoughDataForCurrentApr)

        # logger.info("processing hourly data")
        currHourValDetails = getValidatorDetails(currentHourValMap, hPoolId)
        prevHourValDetails = getValidatorDetails(previousHourValMap, hPoolId)
        # logger.info("current hour existing details")
        # logger.info(currHourValDetails)
        # logger.info("previous hour existing details")
        # logger.info(prevHourValDetails)
        # logger.info("previous hourly delta performance")
        processDeltaPerf(conn, app, validator, hPoolId, currHourValDetails, prevHourValDetails, currentEpoch, currentHour)
        # logger.info("after processing deltas")

    conn.commit()

    # processDeltaPerf(conn, app, validators, currentHour)

    if enoughDataForCurrentApr:
        processPerfIndex(conn, app, epochInfo)
        conn.commit()
    # uniqueDelegates = len(delegates)
    processEpochPerf(conn, app, epochInfo, currentCoinStat, enoughDataForCurrentApr)
    updateCoinStats(conn, app, stakingInfo, epochInfo, len(validators))
    conn.commit()

    auditUtils.createEvent(conn, app, eventName.syncHarmonyValidators)
    auditUtils.audit(conn, app, event, eventName.syncHarmonyValidators, "service", startTime)
    # conn.close()

    return getResponse(jsondumps({"result": "successful"}))

def getValidatorDetails(valMap, hPoolId):
    valDetails = None
    if hPoolId in valMap:
        valDetails = valMap[hPoolId]

    return valDetails

# main sync method
def syncValidator(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat):
    logger.info("in syncValidator")
    address = validator["address"]

    currentData = harmonyData.getHarmonyPool(conn, address)
    hPoolId = None
    if currentData is None:
        # logger.info("inserting validator record for id: " + address)
        createHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat)
        hPoolId = conn.insert_id()
    else:
        # logger.info("updating validator record for id: " + address)
        if validator["name"] is not None and len(validator["name"]) > 0 and validator["name"].find("?") != -1:
            # logger.info("removing ? from name")
            validator["name"] = validator["name"].replace("?", "")
        if validator["name"] is None or validator["name"] == "":
            # logger.info("fixing empty name")
            validator["name"] = currentData["name"]

        updateHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, currentData)
        hPoolId = currentData["hPoolId"]

    return hPoolId
    # logger.info(id + " - returning record")
    # logger.info(currentData)
    # return currentData["csNodeId"]
    # logger.info("finished processing record")


def getOptimalBlsKeyCount(stakingInfo, blsKeyCount, validator):
    # logger.info("calculating optimalBlsKeyCount")
    medianStake = stakingInfo["medianRawStake"]
    totalStaked = validator["totalStaked"]
    optimalCount = (totalStaked/medianStake)
    bidPerSeat = 0
    if blsKeyCount > 0:
        bidPerSeat = (validator["totalStaked"]/blsKeyCount)

    # logger.info("address - {}, totalStaked - {}, medianStake - {}, optimalCount - {}".format(
    #     validator["address"], totalStaked, medianStake, optimalCount))

    return int(optimalCount), bidPerSeat


def createHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat):
    sql = "INSERT INTO " + tables.hpool
    sql += "(name, identity, securityContact, "
    sql += " address, details, blsKeyCount, "
    sql += " minSelfDelegation, maxTotalDelegation, "
    sql += " totalRewards, lastUpdated, website, "
    sql += " lifetimeToSign, lifetimeSigned, lifetimeApr, "
    sql += " currentEpochSigned, currentEpochToSign, "
    sql += " currentEpochSignPer, uniqueDelegates, "
    sql += " fee, maxFee, feeChangeRate, "
    sql += " creationBlock, lastUpdateBlock, totalStaked, "
    sql += " elected, booted, optimalBlsKeyCount, selfStake, "
    sql += " status, activeStatus, bidPerSeat, syncEpochTime) "
    sql += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
    sql += " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
    sql += " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    # logger.info(sql)
    args = (validator["name"], validator["identity"], validator["securityContact"], 
        validator["address"], validator["details"], blsKeyCount, 
        validator["minSelfDelegation"], validator["maxTotalDelegation"], 
        validator["lifetimePerf"]["totalRewards"], datetime.datetime.now(), validator["website"], 
        validator["lifetimePerf"]["lifetimeToSign"], validator["lifetimePerf"]["lifetimeSigned"], 
        validator["lifetimePerf"]["lifetimeApr"], 
        validator["currentPerf"]["currentEpochSigned"], validator["currentPerf"]["currentEpochToSign"], 
        validator["currentPerf"]["currentEpochSigningPercentage"], validator["uniqueDelegates"], 
        validator["fee"], validator["maxFee"], validator["feeChangeRate"], 
        validator["creationBlock"], validator["lastUpdateBlock"], validator["totalStaked"], 
        validator["elected"], validator["booted"], optimalBlsKeyCount,
        validator["selfStake"], validator["status"], validator["activeStatus"], 
        bidPerSeat, int(time.time()))

    # logger.info(args)
    conn.cursor().execute(sql, args)


def updateHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, currentData):
    sql = "update " + tables.hpool + " set "

    if currentData["keepName"] == 'False':
        sql += " name=%s, "
    sql += " identity=%s, securityContact=%s, "
    sql += " details=%s, blsKeyCount=%s, "
    sql += " minSelfDelegation=%s, maxTotalDelegation=%s, "
    sql += " totalRewards=%s, lastUpdated=%s, website=%s, "
    sql += " lifetimeToSign=%s, lifetimeSigned=%s, lifetimeApr=%s, "
    sql += " currentEpochSigned=%s, currentEpochToSign=%s, "
    sql += " currentEpochSignPer=%s, uniqueDelegates=%s, "
    sql += " fee=%s, maxFee=%s, feeChangeRate=%s, "
    sql += " creationBlock=%s, lastUpdateBlock=%s, totalStaked=%s, "
    sql += " elected=%s, booted=%s, optimalBlsKeyCount=%s, selfStake=%s, "
    sql += " status=%s, syncEpochTime=%s, bidPerSeat=%s, "
    sql += " activeStatus=%s where address=%s "

    # logger.info(sql)
    args = (validator["identity"], validator["securityContact"],
        validator["details"], blsKeyCount,
        validator["minSelfDelegation"], validator["maxTotalDelegation"],
        validator["lifetimePerf"]["totalRewards"], datetime.datetime.now(), validator["website"],
        validator["lifetimePerf"]["lifetimeToSign"], validator["lifetimePerf"]["lifetimeSigned"],
        validator["lifetimePerf"]["lifetimeApr"],
        validator["currentPerf"]["currentEpochSigned"], validator["currentPerf"]["currentEpochToSign"],
        validator["currentPerf"]["currentEpochSigningPercentage"], validator["uniqueDelegates"],
        validator["fee"], validator["maxFee"], validator["feeChangeRate"],
        validator["creationBlock"], validator["lastUpdateBlock"], validator["totalStaked"],
        validator["elected"], validator["booted"], optimalBlsKeyCount, validator["selfStake"],
        validator["status"], int(time.time()), bidPerSeat,
        validator["activeStatus"], validator["address"])

    if currentData["keepName"] == 'False':
        args = (validator["name"],) + args

    # logger.info(args)
    conn.cursor().execute(sql, args)


# sync epoch summary
def syncValidatorEpochSummary(conn, validator, blsKeyCount, bidPerSeat, hPoolId, currentEpochSummary, 
    prevEpochSummary, currentEpoch, completionFactor, enoughDataForCurrentApr):

    # logger.info("in syncValidatorEpochSummary")
    # logger.info(validator)
    # logger.info(prevEpochSummary)
    rewards = getGap(validator["lifetimePerf"]["totalRewards"], prevEpochSummary, "lifetimeRewards")

    currentData = {"signed": validator["currentPerf"]["currentEpochSigned"],
        "askedToSign": validator["currentPerf"]["currentEpochToSign"],
        "signPer": validator["currentPerf"]["currentEpochSigningPercentage"],
        "blsKeyCount": blsKeyCount, "rewards": rewards,
        "bidPerSeat": bidPerSeat,
        "syncTime": datetime.datetime.now(),
        "epochSyncTime": int(time.time())
        } 

    if currentEpochSummary is None:
        # logger.info("inserting validator record for id: " + address)
        createHPoolPerf(conn, validator, hPoolId, constants.H_EPOCH_MODE, currentData, currentEpoch)
    else:
        apr, netApr = None, None 
        if enoughDataForCurrentApr and currentEpochSummary["totalStaked"] > 0 and validator["elected"] == 'True':
            apr = (completionFactor * hConstants.H_EPOCHS_IN_YEAR * rewards * 100) / currentEpochSummary["totalStaked"]
            netApr = apr * (1 - float(validator["fee"]))

        # logger.info("hPoolId: {}, enoughDataForCurrentApr: {}, apr: {}, netApr: {}".format(
        #     hPoolId, enoughDataForCurrentApr, apr, netApr))

        # logger.info("updating validator record for id: " + address)
        updateHPoolPerf(conn, validator, currentEpochSummary, currentData, apr, netApr)
        #     logger.info("interested")
        #     logger.info("currentEpochSummary")
        #     logger.info(currentEpochSummary)
        #     logger.info("apr")
        #     logger.info(apr)
        #     logger.info("netApr")
        #     logger.info(netApr)
        #     logger.info("currentData")
        #     logger.info(currentData)

    epochRewardsSql = "update " + tables.hpool + " set currentEpochRewards=%s where hPoolId=%s "
    conn.cursor().execute(epochRewardsSql, (rewards, hPoolId))

    # logger.info(id + " - returning record")
    # logger.info(currentData)
    # return currentData["csNodeId"]
    # logger.info("finished processing record")


# calculate delta performance for current hour
def processDeltaPerf(conn, app, validator, hPoolId, currHourValDetails, prevHourValDetails, currentEpoch, currentTime):
    # logger.info("in processDeltaPerf")
    # logger.info("currentEpoch")
    # logger.info(currentEpoch)

    # logger.info("validator")
    # logger.info(validator)

    if not prevHourValDetails:
        prevHourValDetails = getLatestDataForVal(conn, hPoolId, constants.H_HOUR_MODE)

    askedToSignDelta = getGap(validator["lifetimePerf"]["lifetimeToSign"], prevHourValDetails, "lifetimeToSign")
    signedDelta = getGap(validator["lifetimePerf"]["lifetimeSigned"], prevHourValDetails, "lifetimeSigned")
    signPer = 0
    if askedToSignDelta != 0:
        signPer = signedDelta * 100/askedToSignDelta
    
    rewards = getGap(validator["lifetimePerf"]["totalRewards"], prevHourValDetails, "lifetimeRewards")
    
    # logger.info("askedToSignDelta - {}, signedDelta - {}, lifetimeSigned - {}, lifetimeToSign - {}, prevHourValDetails - {}".format(
    #     askedToSignDelta, signedDelta, validator["lifetimePerf"]["lifetimeToSign"], 
    #     validator["lifetimePerf"]["lifetimeSigned"], prevHourValDetails))
    
    currentData = {"signed": signedDelta,
        "askedToSign": askedToSignDelta,
        "signPer": signPer,
        "blsKeyCount": None, "rewards": rewards,
        "bidPerSeat": None,
        "syncTime": currentTime,
        "epochSyncTime": currentTime.strftime('%s')} 

    # logger.info("currentData")
    # logger.info(currentData)

    if currHourValDetails:
        updateHPoolPerf(conn, validator, currHourValDetails, currentData)
    else:
        createHPoolPerf(conn, validator, hPoolId, constants.H_HOUR_MODE, currentData, currentEpoch)


def createHPoolPerf(conn, validator, hPoolId, mode, currentData, currentEpoch):
    sql = "INSERT INTO " + tables.hpoolperf
    sql += "(hPoolId, blsKeyCount, epochNumber, mode, "
    sql += " signed, askedToSign, "
    sql += " signPer, uniqueDelegates, "
    sql += " lifetimeSigned, lifetimeToSign, rewards, lifetimeRewards, "
    sql += " fee, totalStaked, "
    sql += " elected, booted, selfStake, "
    sql += " status, bidPerSeat, syncTime, syncEpochTime) "
    sql += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
    sql += " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # logger.info(sql)
    args = (hPoolId, currentData["blsKeyCount"], currentEpoch, mode, 
        currentData["signed"], currentData["askedToSign"], 
        currentData["signPer"], validator["uniqueDelegates"], 
        validator["lifetimePerf"]["lifetimeSigned"], validator["lifetimePerf"]["lifetimeToSign"], 
        currentData["rewards"], validator["lifetimePerf"]["totalRewards"], 
        validator["fee"], validator["totalStaked"], 
        validator["elected"], validator["booted"], validator["selfStake"], 
        validator["status"], currentData["bidPerSeat"], currentData["syncTime"], currentData["epochSyncTime"])

    # logger.info(args)
    conn.cursor().execute(sql, args)


def updateHPoolPerf(conn, validator, currentEpochSummary, currentData, apr=None, netApr=None):
    sql = "update " + tables.hpoolperf
    sql += " set signed=%s, askedToSign=%s, signPer=%s, "
    sql += " elected=%s, booted=%s, lifetimeSigned=%s, "
    sql += " lifetimeToSign=%s, rewards=%s, lifetimeRewards=%s, "
    sql += " status=%s, syncTime=%s, syncEpochTime=%s, "
    sql += " apr=%s, netApr=%s where hPoolPerfId=%s "
    
    # logger.info(sql)
    args = (currentData["signed"], currentData["askedToSign"], currentData["signPer"], 
        validator["elected"], validator["booted"],  validator["lifetimePerf"]["lifetimeSigned"], 
        validator["lifetimePerf"]["lifetimeToSign"], currentData["rewards"], validator["lifetimePerf"]["totalRewards"], 
        validator["status"], currentData["syncTime"], currentData["epochSyncTime"], 
        apr, netApr, currentEpochSummary["hPoolPerfId"])

    # logger.info(args)
    # logger.info("before updateHPoolPerf sql")
    conn.cursor().execute(sql, args)
    # logger.info("after updateHPoolPerf sql")


def getOnePriceData():
    oneMetrics = restUtils.callRestJson("https://data.messari.io/api/v1/assets/harmony/metrics")
    # logger.info("oneMetrics response is: " )
    # logger.info(oneMetrics)
    usdPrice = oneMetrics["data"]["market_data"]["price_usd"]
    btcPrice = oneMetrics["data"]["market_data"]["price_btc"]
    priceChangeUsd = oneMetrics["data"]["market_data"]["percent_change_usd_last_24_hours"]
    marketcap = int(oneMetrics["data"]["marketcap"]["current_marketcap_usd"])

    return {"usdPrice": usdPrice, "btcPrice": btcPrice, "priceChangeUsd": priceChangeUsd, "marketcap": marketcap}


def updateCoinStats(conn, app, stakingInfo, epochInfo, totalValidators):
    logger.info(stakingInfo)

    sql = "update " + tables.coinstat
    sql += " set lastUpdated=%s, totalSupply = %s, "
    sql += " circulatingSupply=%s, percentStaked=%s, "
    sql += " totalStake=%s, medianRawStake=%s, recentBlock=%s, "
    sql += " uniqueDelegates=%s, stakingPools=%s, "
    sql += " epochLastBlock=%s, nextEpochTime=%s, currentEpoch=%s, "
    sql += " currentRewardRate=%s, usdPrice=%s, btcPrice=%s, "
    sql += " priceChangeUsd=%s, usdMcap=%s, usdStaked=%s "
    sql += " where symbol=%s "

    totalStake = float(stakingInfo["totalStake"])
    circulatingSupply = float(stakingInfo["circulatingSupply"])
    percentStaked = totalStake * 100/circulatingSupply
    currentRewardRate = 441000000 * 100/totalStake

    prices = getOnePriceData()
    usdStaked = totalStake * prices["usdPrice"]

    # logger.info(sql)
    conn.cursor().execute(sql, (datetime.datetime.now(), stakingInfo["totalSupply"], 
        circulatingSupply, percentStaked, totalStake,
        stakingInfo["medianRawStake"], epochInfo["latestBlock"],
        stakingInfo["uniqueDelegates"], totalValidators, 
        stakingInfo["epochLastBlock"]-1, epochInfo["nextEpochTime"], epochInfo["currentEpoch"],
        currentRewardRate, prices["usdPrice"], prices["btcPrice"],
        prices["priceChangeUsd"], prices["marketcap"], usdStaked, app))

    updateStakeHistory(conn, epochInfo["currentEpoch"], totalStake, circulatingSupply,
        currentRewardRate, totalValidators, prices["btcPrice"],
        stakingInfo["medianRawStake"])


def updateStakeHistory(conn, epoch, totalStake, circulatingSupply,
    currentRewardRate, totalValidators, btcPrice, medianRawStake):

    currentData = harmonyHistory.getExisting(conn, epoch, constants.H_HISTORY_NETWORK)

    if currentData is None:
        # logger.info("inserting validator record for id: " + address)
        harmonyHistory.createHistory(conn, epoch, constants.H_HISTORY_NETWORK,
            totalStake, None, None, None, circulatingSupply,
            currentRewardRate, totalValidators, btcPrice, medianRawStake)


def getGap(curData, previousData, attribute):
    prevData = 0

    if previousData and attribute in previousData and previousData[attribute]:
        # logger.info("previous data is available")
        prevData = previousData[attribute] 

    return curData - prevData


def getLatestDataForVal(conn, hPoolId, mode):
    sql = "select * from " + tables.hpoolperf + " p "
    sql += " where p.hPoolId= %s and mode=%s "
    sql += " order by syncTime desc "
    sql += " limit 1 "

    return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (hPoolId, mode))


def listCurrentValues(conn, epochNumber, hourTime):
    sql = "select * "
    sql += " from " + tables.hpoolperf
    sql += " where mode=%s "

    args = ()
    if epochNumber and hourTime:
        sql += " and epochNumber=%s and date_format(syncTime,'%%Y-%%m-%%d %%H')= date_format(%s,'%%Y-%%m-%%d %%H') "
        args = (constants.H_HOUR_MODE, epochNumber, hourTime)
    elif epochNumber:
        sql += " and epochNumber=%s "
        args = (constants.H_EPOCH_MODE, epochNumber)
    else:
        sql += " and date_format(syncTime,'%%Y-%%m-%%d %%H')= date_format(%s,'%%Y-%%m-%%d %%H') "
        args = (constants.H_HOUR_MODE, hourTime)


    # logger.info(sql)
    # logger.info(args)

    list = dbUtil.listResultsWithConn(sql, conn, args)
    return list
    
def getCurrentValMap(conn, epochNumber, hourTime):
    list = listCurrentValues(conn, epochNumber, hourTime)
    return commonUtils.getMapFromList(list, "hPoolId")


def getStartEpoch(epoch, eRange):
    startEpoch = epoch - eRange

    if startEpoch < hConstants.H_FIRST_EPOCH:
        startEpoch = hConstants.H_FIRST_EPOCH

    return startEpoch


def processEpochPerf(conn, app, epochInfo, currentCoinStat, enoughDataForCurrentApr):
    currentEpoch = epochInfo["currentEpoch"]
    
    currentEpochPerfData = processCurrentEpochPerf(conn, app, currentEpoch, enoughDataForCurrentApr)
    
    if currentCoinStat["currentEpoch"] == currentEpoch:
        logger.info("epoch hasnt changed. returning")
        return 

    processPreviousEpochChange(conn, app, currentEpoch, currentEpochPerfData)


def processCurrentEpochPerf(conn, app, epoch, enoughDataForCurrentApr):
    logger.info("calculating current aprs for all validators: {}".format(enoughDataForCurrentApr))

    currentPerfData = harmonyData.listHPoolPerfByEpoch(conn, 
        app, epoch, constants.H_EPOCH_MODE)

    updates = []
    for validator in currentPerfData:
        # updateCurrentApr(conn, validator, enoughDataForCurrentApr)
        record = getUpdateCurrentApr(validator, enoughDataForCurrentApr)
        updates.append(record)

    batchUpdateCurrentEpochPerf(conn, updates)
    conn.commit()

    return currentPerfData


def batchUpdateCurrentEpochPerf(conn, updates):
    logger.info("in batchUpdateCurrentEpochPerf")

    sql = "update " + tables.hpool
    sql += " set currentApr=%s, currentNetApr=%s, currentEri=%s "
    sql += " where hPoolId = %s "

    conn.cursor().executemany(sql, updates)


def getUpdateCurrentApr(validator, enoughDataForCurrentApr):
    logger.info("in getUpdateCurrentApr")
    # logger.info(sql)
    apr, netApr, eri = None, None, None

    if enoughDataForCurrentApr:
        if validator["apr"]:
            apr = validator["apr"]

        if validator["eri"]:
            eri = validator["eri"]

        if validator["netApr"]:
            netApr = validator["netApr"]

    logger.info("hPoolId: {}, apr: {}, netApr: {}, eri: {} ".format(
        validator["hPoolId"], apr, netApr, eri))
    args = (apr, netApr, eri, validator["hPoolId"])
    # logger.info(args)
    return args


#NOT IN USE: 4th July
def updateCurrentApr(conn, validator, enoughDataForCurrentApr):
    logger.info("updating current aprs for {}".format(enoughDataForCurrentApr))
    sql = "update " + tables.hpool
    sql += " set currentApr=%s, currentNetApr=%s, currentEri=%s "
    sql += " where hPoolId = %s "

    # logger.info(sql)
    apr, netApr, eri = None, None, None

    if enoughDataForCurrentApr:
        if validator["apr"]:
            apr = validator["apr"]

        if validator["eri"]:
            eri = validator["eri"]

        if validator["netApr"]:
            netApr = validator["netApr"]

    logger.info("hPoolId: {}, apr: {}, netApr: {}, eri: {} ".format(
        validator["hPoolId"], apr, netApr, eri))
    args = (apr, netApr, eri, validator["hPoolId"])
    # logger.info(args)
    conn.cursor().execute(sql, args)


def getBlockCompletionFactor(epochInfo, stakingInfo, currentCoinStat, currentEpoch):
    totalBlocks = hConstants.H_BLOCKS_IN_EPOCH
    currentBlock = epochInfo["latestBlock"]
    lastBlock = stakingInfo["epochLastBlock"]-1
    firstBlock = lastBlock - totalBlocks
    blocksPast = currentBlock - firstBlock

    enoughData = True
    if blocksPast < constants.H_MIN_BLOCKS_FOR_CURRENT_EPOCH_APR:
        logger.info("minimum blocks {} have not passed in the epoch - {}".format(
            constants.H_MIN_BLOCKS_FOR_CURRENT_EPOCH_APR, blocksPast))
        enoughData = False

    calcUsesPrevEpoch = False    
    if currentCoinStat["currentEpoch"] + 1 == currentEpoch:
        logger.info("epoch has just changed. include blocks from previous epoch")
        if currentCoinStat["recentBlock"] + 1 != firstBlock:
            logger.info("confirmed need to include blocks from previous epoch")
            blocksPast = currentBlock - currentCoinStat["recentBlock"]
            calcUsesPrevEpoch = True

    if blocksPast == 0:
        return 0

    completionFactor = totalBlocks/blocksPast
    logger.info("enoughData: {}, completionFactor: {}, currentBlock: {}, lastBlock: {}, firstBlock: {}, blocksPast: {}, calcUsesPrevEpoch: {}".format(
        enoughData, completionFactor, currentBlock, lastBlock, firstBlock, blocksPast, calcUsesPrevEpoch))
    return completionFactor, enoughData


def processPreviousEpochChange(conn, app, currentEpoch, currentEpochPerfData):
    logger.info("epoch has changed. calculating APR for previous epoch") 
    previousEpoch = currentEpoch - 1
    prevEpochPerfData = harmonyData.listHPoolPerfByEpoch(conn, app, previousEpoch, constants.H_EPOCH_MODE)
    startEpoch = getStartEpoch(currentEpoch, hConstants.H_EPOCHS_FOR_AVERAGE)
    avgPerfList = harmonyData.listHPoolPerfByEpochRange(conn, app, startEpoch, previousEpoch, constants.H_EPOCH_MODE)
    avgPerfMap = commonUtils.getMapFromList(avgPerfList, "hPoolId")
    logger.info(avgPerfMap)

    currentEpochPerfMap = commonUtils.getMapFromList(currentEpochPerfData, "hPoolId")

    for prevEpochValidator in prevEpochPerfData:
        hPoolId = prevEpochValidator["hPoolId"]

        # logger.info(prevEpochValidator)
        avgPerf = avgPerfMap[hPoolId]
        # logger.info(avgPerf)
        avgApr, avgNetApr, avgEri = None, None, None
        if avgPerf["avgApr"]:
            avgApr, avgNetApr, avgEri = getAvgApr(prevEpochValidator, avgPerf, startEpoch, previousEpoch)

        feeChanged = None
        if hPoolId in currentEpochPerfMap:
            feeChanged = processFeeChange(conn, prevEpochValidator, currentEpochPerfMap[hPoolId], currentEpoch)
        updatePoolPrevEpochApr(conn, prevEpochValidator, avgApr, avgNetApr, avgEri, currentEpoch, feeChanged)

    conn.commit()

def processFeeChange(conn, prevEpochValidator, currentEpochValidator, currentEpoch):
    logger.info("in processFeeChange for prevEpochValidator: {}, currentEpochValidator: {}, currentEpoch: {}".format(
        prevEpochValidator, currentEpochValidator, currentEpoch))

    feeChanged = None
    if prevEpochValidator["fee"] != currentEpochValidator["fee"]:
        # logger.info("fee is different")
        if prevEpochValidator["fee"] > currentEpochValidator["fee"]:
            # logger.info("fee has decreased")
            eventType = hConstants.H_EVENT_FEE_DECREASE
            change = str((prevEpochValidator["fee"] * 100)) + " to " + str((currentEpochValidator["fee"] * 100))
            # logger.info("{} - fee has increased for validator - {}".format(prevEpochValidator["hPoolId"], change))
        else:
            # logger.info("fee has increased")
            eventType = hConstants.H_EVENT_FEE_INCREASE
            prevFee = round(prevEpochValidator["fee"] * 100, 2)
            currentFee = round(currentEpochValidator["fee"] * 100, 2)
            feeChanged = str(prevFee) + "% to " + str(currentFee) + "%"
            # logger.info("{} - fee has increased for validator - {}".format(prevEpochValidator["hPoolId"], feeChanged))

        # logger.info("creating fee event")
        harmonyEvents.createFeeEvent(conn, eventType, prevEpochValidator["hPoolId"],
                                     currentEpoch, currentEpochValidator["fee"])

    return feeChanged


def updatePoolPrevEpochApr(conn, validator, avgApr, avgNetApr, avgEri, currentEpoch, feeChanged):
    sql = "update " + tables.hpool 
    sql += " set prevEpochApr=%s, prevEpochNetApr=%s, prevEpochEri=%s, "
    sql += " avgApr=%s, avgNetApr=%s, avgEri=%s "

    if feeChanged:
        sql += " , feeChangedEpoch=%s, feeChangedDesc=%s "

    sql += " where hPoolId = %s "

    # logger.info(sql)

    if feeChanged:
        # logger.info("processing fee changed")
        args = (validator["apr"], validator["netApr"], validator["eri"],
            avgApr, avgNetApr, avgEri,
            currentEpoch, feeChanged,
            validator["hPoolId"])
        # logger.info(args)
    else:
        args = (validator["apr"], validator["netApr"], validator["eri"],
            avgApr, avgNetApr, avgEri, validator["hPoolId"])
    # logger.info(args)
    conn.cursor().execute(sql, args)


def getAvgApr(validator, avgPerf, startEpoch, previousEpoch):
    # logger.info(avgPerf)
    minEpoch = avgPerf["oldestEpoch"]
    epochsPresent = avgPerf["epochsPresent"]

    if startEpoch > minEpoch:
        # this validator was not elected at the start of range
        startEpoch = minEpoch

    epochRange = previousEpoch - startEpoch + 1

    if epochRange == 0:
        logger.info("epoch range is 0, skipping apr calculations")
        return 0
        
    avgApr = avgPerf["avgApr"] * avgPerf["epochsPresent"] / epochRange
    avgNetApr = avgApr * (1 - float(validator["fee"]))

    avgEri = None
    if avgPerf["avgEri"]:
        avgEri = avgPerf["avgEri"] * avgPerf["epochsPresent"] / epochRange
    
    logger.info("avg apr details are: avgApr - {}, avgNetApr - {}, epochRange - {}, avgEri - {}".format(
        avgApr, avgNetApr, epochRange, avgEri))

    return avgApr, avgNetApr, avgEri

def processPerfIndex(conn, app, epochInfo):
    logger.info("calculating perf index")
    currentEpoch = epochInfo["currentEpoch"]
    poolPerfs = listCurrentValues(conn, currentEpoch, None)

    averageApr = getAverageAprForCurrentEpoch(conn, app, currentEpoch)
    logger.info("averageApr: {}".format(averageApr))

    updates = []

    for poolPerf in poolPerfs:
        # logger.info(poolPerf)
        apr = poolPerf["apr"]
        eri = None
        if poolPerf["elected"] == 'True' and apr:
            eri = apr / averageApr
        # updateCurrentEri(conn, poolPerf, eri)
        record = (eri, poolPerf["hPoolPerfId"])
        updates.append(record)

    batchUpdateCurrentEri(conn, updates)


def batchUpdateCurrentEri(conn, updates):
    sql = "update " + tables.hpoolperf
    sql += " set eri=%s "
    sql += " where hPoolPerfId=%s "

    conn.cursor().executemany(sql, updates)


#Not in use - 4th july
def updateCurrentEri(conn, poolPerf, eri):
    sql = "update " + tables.hpoolperf
    sql += " set eri=%s "
    sql += " where hPoolPerfId=%s "

    args = (eri, poolPerf["hPoolPerfId"])

    conn.cursor().execute(sql, args)


def getAverageAprForCurrentEpoch(conn, app, epochNumber):
    sql = "select sum(totalStaked * apr)/sum(totalStaked) as averageApr "
    sql += " from " + tables.hpoolperf
    sql += " where mode=%s "
    sql += " and epochNumber=%s and elected='True' "

    args = (constants.H_EPOCH_MODE, epochNumber)
    # logger.info(sql)
    # logger.info(args)

    return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, args)["averageApr"]
