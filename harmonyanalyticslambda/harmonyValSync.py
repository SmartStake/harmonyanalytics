import datetime
import json
import logging
import time

import auditUtils
import commonUtils
import constants
import dbUtil
import eventName
import hConstants
import harmonyData
import harmonyHistory
import harmonyTransactionSync
import harmonyValEpochChange
import harmonyValEvents
import restUtils
import securityUtils
import tables
import utilities
from utilities import jsondumps, getResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = constants.HARMONY

def lambda_handler(event, context):
	logger.info("in updateData for harmony")

	conn, app, error = securityUtils.performSecurityCheckAndGetDetails(event)
	if error:
		return error

	body = json.loads(event["body"])
	# logger.info("body: {}".format(body))

	data = body["data"]
	if "type" in data:
		dataType = data["type"]
	else:
		dataType = body["type"]

	logger.info("dataType: {}".format(dataType))

	if dataType == "valSync":
		syncValidators(conn, app, data, event)

	conn.close()
	return utilities.getSuccessResponse()


def syncValidators(conn, app, data, event):
	# logger.info("in harmony validator sync")
	startTime = commonUtils.getCurrentTime()
	startTimeAudit = datetime.datetime.now()
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
	if len(validators) <= 100:
		logger.info("number of validators returned is much less than what was expected. skipping the processing for now.")
		return getResponse(jsondumps({"result": "successful"}))

	currentEpochValMap = getCurrentValMap(conn, currentEpoch, None)
	previousEpochValMap = getCurrentValMap(conn, currentEpoch-1, None)
	currentHourValMap = getCurrentValMap(conn, currentEpoch, currentHour)
	previousHourValMap = getCurrentValMap(conn, None, previousHour)

	commonUtils.logTimeDiff(startTime, "before coinstats")
	currentCoinStat = commonUtils.getCoinStat(conn, app)
	commonUtils.logTimeDiff(startTime, "before getBlockCompletionFactor")
	completionFactor, enoughDataForCurrentApr = getBlockCompletionFactor(epochInfo, stakingInfo, currentCoinStat, currentEpoch)
	# logger.info("is enough data captured for current apr: {}".format(enoughDataForCurrentApr))

	valMap = harmonyData.listHPoolsAsMap(conn)
	networkStake = getNetworkStake(validators)
	commonUtils.logTimeDiff(startTime, "time spent before starting validators processing")
	i = 0
	deltaInserts, deltaUpdates = [], []
	stakeWeights = []
	for validator in validators:
		address = validator["address"]
		# logger.info("{} - processing validator: {}".format(i, address))
		# logger.info(validator)
		i += 1
		commonUtils.logTimeDiff(startTime, "processing validator #: {}".format(i))

		blsKeyCount = len(validator["blsPublicKeys"])
		optimalBlsKeyCount, bidPerSeat = getOptimalBlsKeyCount(stakingInfo, blsKeyCount, validator)

		commonUtils.logTimeDiff(startTime, "before processing syncValidator #: {}".format(i))
		stakeWeight = getStakeWeight(validator, networkStake)
		stakeWeights.append(stakeWeight)

		dbValidator = None
		if address in valMap:
			dbValidator = valMap[address]
		hPoolId = syncValidator(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, stakeWeight, currentEpoch, dbValidator)
		commonUtils.logTimeDiff(startTime, "after processing syncValidator #: {}".format(i))

		currEpochSummary = getValidatorDetails(currentEpochValMap, hPoolId)
		commonUtils.logTimeDiff(startTime, "after getting currEpochSummary #: {}".format(i))
		prevEpochSummary = getValidatorDetails(previousEpochValMap, hPoolId)
		commonUtils.logTimeDiff(startTime, "after getting prevEpochSummary #: {}".format(i))

		syncValidatorEpochSummary(conn, validator, blsKeyCount, bidPerSeat, hPoolId, currEpochSummary,
								  prevEpochSummary, currentEpoch, completionFactor, enoughDataForCurrentApr)

		commonUtils.logTimeDiff(startTime, "after processing syncValidatorEpochSummary #: {}".format(i))
		# logger.info("processing hourly data")
		currHourValDetails = getValidatorDetails(currentHourValMap, hPoolId)
		commonUtils.logTimeDiff(startTime, "after obtaining currHourValDetails #: {}".format(i))
		prevHourValDetails = getValidatorDetails(previousHourValMap, hPoolId)
		# logger.info("current hour existing details")
		# logger.info(currHourValDetails)
		# logger.info("previous hour existing details")
		# logger.info(prevHourValDetails)
		# logger.info("previous hourly delta performance")
		commonUtils.logTimeDiff(startTime, "before delta perf - processing validator #: {}".format(i))
		processDeltaPerf(conn, validator, hPoolId, currHourValDetails, prevHourValDetails, currentEpoch,
						 currentHour, deltaInserts, deltaUpdates)
		commonUtils.logTimeDiff(startTime, "after processDeltaPerf #: {}".format(i))
		# logger.info("after processing deltas")

	commonUtils.logTimeDiff(startTime, "before processing hpoolperf inserts and updates")
	batchCreateHPoolPerf(conn, deltaInserts)
	batchUpdateHPoolPerf(conn, deltaUpdates)

	conn.commit()

	# processDeltaPerf(conn, app, validators, currentHour)
	commonUtils.logTimeDiff(startTime, "before processing perf index")
	if enoughDataForCurrentApr:
		processPerfIndex(conn, app, epochInfo)
		conn.commit()
	# uniqueDelegates = len(delegates)
	commonUtils.logTimeDiff(startTime, "before processing perf index")
	processEpochPerf(conn, app, epochInfo, currentCoinStat, enoughDataForCurrentApr)

	commonUtils.logTimeDiff(startTime, "before update coinstat")
	valForNetworkHalt = getValCountForNetworkHalt(stakeWeights)
	updateCoinStats(conn, app, stakingInfo, epochInfo, len(validators), valForNetworkHalt)
	conn.commit()

	harmonyValEvents.generateValSyncEvents(conn, currentEpoch, enoughDataForCurrentApr)

	commonUtils.logTimeDiff(startTime, "before creating event and audit")
	auditUtils.createEvent(conn, app, eventName.syncHarmonyValidators)
	auditUtils.audit(conn, app, event, eventName.syncHarmonyValidators, "service", startTimeAudit)
	# conn.close()

	commonUtils.logTimeDiff(startTime, "total time spent")
	return getResponse(jsondumps({"result": "successful"}))


def getValCountForNetworkHalt(stakeWeights):
	stakeWeights.sort(reverse=True)
	totalWeight = 0
	minValCount = 0
	for stakeWeight in stakeWeights:
		minValCount += 1
		totalWeight += stakeWeight
		if totalWeight > 33.33334:
			return minValCount

	return minValCount


def getValidatorDetails(valMap, hPoolId):
	valDetails = None
	if hPoolId in valMap:
		valDetails = valMap[hPoolId]

	return valDetails

# main sync method
def syncValidator(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, stakeWeight, currentEpoch, dbValidator):
	# logger.info("in syncValidator")
	# address = validator["address"]

	# currentData = harmonyData.getHarmonyPool(conn, address)
	currentData = dbValidator
	if currentData is None:
		# logger.info("inserting validator record for id: " + address)
		createHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, stakeWeight)
		hPoolId = conn.insert_id()
	else:
		# logger.info("updating validator record for id: " + address)
		if validator["name"] is not None and len(validator["name"]) > 0 and validator["name"].find("?") != -1:
			# logger.info("removing ? from name")
			validator["name"] = validator["name"].replace("?", "")
		if validator["name"] is None or validator["name"] == "":
			# logger.info("fixing empty name")
			validator["name"] = currentData["name"]

		harmonyValEvents.checkValidatorDetails(conn, currentData, validator, currentEpoch)
		updateHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, stakeWeight, currentData)
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


def createHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, stakeWeight):
	sql = "INSERT INTO " + tables.hpool
	sql += "(name, identity, securityContact, "
	sql += " address, details, blsKeyCount, "
	sql += " minSelfDelegation, maxTotalDelegation, "
	sql += " totalRewards, lastUpdated, website, "
	sql += " lifetimeToSign, lifetimeSigned, lifetimeApr, "
	sql += " currentEpochSigned, currentEpochToSign, "
	sql += " currentEpochSignPer, uniqueDelegates, "
	sql += " fee, maxFee, feeChangeRate, prevFee, "
	sql += " creationBlock, lastUpdateBlock, totalStaked, "
	sql += " elected, booted, optimalBlsKeyCount, selfStake, "
	sql += " status, activeStatus, bidPerSeat, stakeWeight, syncEpochTime) "
	sql += " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
	sql += " %s, %s, %s, %s)"

	# logger.info(sql)
	args = (validator["name"], validator["identity"], validator["securityContact"],
			validator["address"], validator["details"], blsKeyCount,
			validator["minSelfDelegation"], validator["maxTotalDelegation"],
			validator["lifetimePerf"]["totalRewards"], datetime.datetime.now(), validator["website"],
			validator["lifetimePerf"]["lifetimeToSign"], validator["lifetimePerf"]["lifetimeSigned"], validator["lifetimePerf"]["lifetimeApr"],
			validator["currentPerf"]["currentEpochSigned"], validator["currentPerf"]["currentEpochToSign"],
			validator["currentPerf"]["currentEpochSigningPercentage"], validator["uniqueDelegates"],
			validator["fee"], validator["maxFee"], validator["feeChangeRate"], validator["fee"],
			validator["creationBlock"], validator["lastUpdateBlock"], validator["totalStaked"],
			validator["elected"], validator["booted"], optimalBlsKeyCount, validator["selfStake"],
			validator["status"], validator["activeStatus"], bidPerSeat,
			stakeWeight, int(time.time()))

	# logger.info(args)
	conn.cursor().execute(sql, args)


def updateHPool(conn, validator, blsKeyCount, optimalBlsKeyCount, bidPerSeat, stakeWeight, currentData):
	sql = "update " + tables.hpool + " set "

	if currentData["keepName"] == 'False':
		sql += " name=%s, "

	if currentData["isEverElected"] == 'False' and validator["status"] == hConstants.H_ELECTED:
		sql += " isEverElected= 'True', "

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
	sql += " activeStatus=%s, stakeWeight=%s where address=%s "

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
			validator["activeStatus"], stakeWeight, validator["address"])

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
		# logger.info("enoughDataForCurrentApr: {} and totalStaked: {} and elected: {}".format(
		# 	enoughDataForCurrentApr, currentEpochSummary["totalStaked"], validator["elected"]))

		if enoughDataForCurrentApr and currentEpochSummary["totalStaked"] > 0 and validator["elected"] == 'True':
			apr = (completionFactor * hConstants.H_EPOCHS_IN_YEAR * rewards * 100) / currentEpochSummary["totalStaked"]
			netApr = apr * (1 - float(validator["fee"]))

		# logger.info("hPoolId: {}, enoughDataForCurrentApr: {}, apr: {}, netApr: {}".format(
		#     hPoolId, enoughDataForCurrentApr, apr, netApr))

		# logger.info("updating validator record for id: " + address)
		updateHPoolPerf(conn, validator, currentEpochSummary, currentData, apr, netApr)
		#     logger.info("interested")

	epochRewardsSql = "update " + tables.hpool + " set currentEpochRewards=%s where hPoolId=%s "
	conn.cursor().execute(epochRewardsSql, (rewards, hPoolId))

	# logger.info(id + " - returning record")
	# logger.info(currentData)
	# return currentData["csNodeId"]
	# logger.info("finished processing record")


# calculate delta performance for current hour
def processDeltaPerf(conn, validator, hPoolId, currHourValDetails, prevHourValDetails,
					 currentEpoch, currentTime, deltaInserts, deltaUpdates):
	logger.info("in processDeltaPerf")
	# if validator["status"] != hConstants.H_ELECTED:
	#     return

	startTime = commonUtils.getCurrentTime()
	# logger.info("currentEpoch")
	# logger.info(currentEpoch)

	# logger.info("validator")
	# logger.info(validator)

	if not prevHourValDetails:
		prevHourValDetails = getLatestDataForVal(conn, hPoolId, constants.H_HOUR_MODE)

	commonUtils.logTimeDiff(startTime, "time spent after getting latest data for validator")
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

	commonUtils.logTimeDiff(startTime, "before creating pool perf record")
	if currHourValDetails:
		record = getUpdateHPoolPerf(validator, currHourValDetails, currentData)
		deltaUpdates.append(record)
	else:
		record = getCreateHPoolPerf(validator, hPoolId, constants.H_HOUR_MODE, currentData, currentEpoch)
		deltaInserts.append(record)


def getUpdateHPoolPerf(validator, currentEpochSummary, currentData, apr=None, netApr=None):
	args = (currentData["signed"], currentData["askedToSign"], currentData["signPer"],
			validator["elected"], validator["booted"],  validator["lifetimePerf"]["lifetimeSigned"],
			validator["lifetimePerf"]["lifetimeToSign"], currentData["rewards"],
			validator["lifetimePerf"]["totalRewards"],
			validator["status"], currentData["syncTime"], currentData["epochSyncTime"],
			apr, netApr, currentEpochSummary["hPoolPerfId"])
	return args


def getCreateHPoolPerf(validator, hPoolId, mode, currentData, currentEpoch):
	args = (hPoolId, currentData["blsKeyCount"], currentEpoch, mode,
			currentData["signed"], currentData["askedToSign"],
			currentData["signPer"], validator["uniqueDelegates"],
			validator["lifetimePerf"]["lifetimeSigned"], validator["lifetimePerf"]["lifetimeToSign"],
			currentData["rewards"], validator["lifetimePerf"]["totalRewards"],
			validator["fee"], validator["totalStaked"],
			validator["elected"], validator["booted"], validator["selfStake"],
			validator["status"], currentData["bidPerSeat"], currentData["syncTime"], currentData["epochSyncTime"])
	return args


def batchCreateHPoolPerf(conn, updates):
	# logger.info("in batchUpdateCurrentEpochPerf")
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

	conn.cursor().executemany(sql, updates)


#not in use
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


def batchUpdateHPoolPerf(conn, updates):
	# logger.info("in batchUpdateCurrentEpochPerf")
	sql = "update " + tables.hpoolperf
	sql += " set signed=%s, askedToSign=%s, signPer=%s, "
	sql += " elected=%s, booted=%s, lifetimeSigned=%s, "
	sql += " lifetimeToSign=%s, rewards=%s, lifetimeRewards=%s, "
	sql += " status=%s, syncTime=%s, syncEpochTime=%s, "
	sql += " apr=%s, netApr=%s where hPoolPerfId=%s "

	conn.cursor().executemany(sql, updates)


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
	# logger.info("after updateHPoolPerf sql. records updated: {}".format(count))


def getOnePriceData():
	oneMetrics = restUtils.callRestJson("https://data.messari.io/api/v1/assets/harmony/metrics")
	# logger.info("oneMetrics response is: " )
	# logger.info(oneMetrics)
	usdPrice = oneMetrics["data"]["market_data"]["price_usd"]
	btcPrice = oneMetrics["data"]["market_data"]["price_btc"]
	priceChangeUsd = oneMetrics["data"]["market_data"]["percent_change_usd_last_24_hours"]
	marketcap = int(oneMetrics["data"]["marketcap"]["current_marketcap_usd"])

	return {"usdPrice": usdPrice, "btcPrice": btcPrice, "priceChangeUsd": priceChangeUsd, "marketcap": marketcap}


def updateCoinStats(conn, app, stakingInfo, epochInfo, totalValidators, valForNetworkHalt):
	# logger.info(stakingInfo)

	sql = "update " + tables.coinstat
	sql += " set lastUpdated=%s, totalSupply = %s, "
	sql += " circulatingSupply=%s, percentStaked=%s, "
	sql += " totalStake=%s, medianRawStake=%s, recentBlock=%s, "
	sql += " uniqueDelegates=%s, stakingPools=%s, "
	sql += " epochLastBlock=%s, nextEpochTime=%s, currentEpoch=%s, "
	sql += " currentRewardRate=%s, usdPrice=%s, btcPrice=%s, "
	sql += " priceChangeUsd=%s, usdMcap=%s, usdStaked=%s, "
	sql += " valForNetworkHalt=%s, epochTimestamp=%s, totalTransactions=%s where symbol=%s "

	totalStake = float(stakingInfo["totalStake"])
	circulatingSupply = float(stakingInfo["circulatingSupply"])
	percentStaked = totalStake * 100/circulatingSupply
	currentRewardRate = 441000000 * 100/totalStake
	totalTransactions = harmonyTransactionSync.getTotalTransactions(conn)

	prices = getOnePriceData()
	usdStaked = totalStake * prices["usdPrice"]

	# logger.info(sql)
	conn.cursor().execute(sql, (datetime.datetime.now(), stakingInfo["totalSupply"],
		circulatingSupply, percentStaked, totalStake,
		stakingInfo["medianRawStake"], epochInfo["latestBlock"],
		stakingInfo["uniqueDelegates"], totalValidators,
		stakingInfo["epochLastBlock"]-1, epochInfo["nextEpochTime"], epochInfo["currentEpoch"],
		currentRewardRate, prices["usdPrice"], prices["btcPrice"],
		prices["priceChangeUsd"], prices["marketcap"], usdStaked,
		valForNetworkHalt, int(time.time()), totalTransactions, app))

	harmonyHistory.updateNetworkHistory(conn, epochInfo["currentEpoch"], totalStake, circulatingSupply,
		currentRewardRate, totalValidators, prices["btcPrice"],
		stakingInfo["medianRawStake"], stakingInfo["uniqueDelegates"])


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

	if epochNumber and hourTime:
		sql += " and epochNumber=%s and syncTime = date_format(%s,'%%Y-%%m-%%d %%H') "
		args = (constants.H_HOUR_MODE, epochNumber, hourTime)
	elif epochNumber:
		sql += " and epochNumber=%s "
		args = (constants.H_EPOCH_MODE, epochNumber)
	else:
		# sql += " and date_format(syncTime,'%%Y-%%m-%%d %%H')= date_format(%s,'%%Y-%%m-%%d %%H') "
		sql += " and syncTime = date_format(%s,'%%Y-%%m-%%d %%H') "
		args = (constants.H_HOUR_MODE, hourTime)


	# logger.info(sql)
	# logger.info(args)

	startTime = commonUtils.getCurrentTime()
	list = dbUtil.listResultsWithConn(sql, conn, args)
	commonUtils.logTimeDiff(startTime, "after processing listCurrentValues")
	return list

def getCurrentValMap(conn, epochNumber, hourTime):
	# logger.info("in getCurrentValMap for: epochNumber: {}, hourTime: {}".format(epochNumber, hourTime))
	listData = listCurrentValues(conn, epochNumber, hourTime)
	return commonUtils.getMapFromList(listData, "hPoolId")


def processEpochPerf(conn, app, epochInfo, currentCoinStat, enoughDataForCurrentApr):
	currentEpoch = epochInfo["currentEpoch"]

	currentEpochPerfData = processCurrentEpochPerf(conn, app, currentEpoch, enoughDataForCurrentApr)

	if currentCoinStat["currentEpoch"] == currentEpoch:
		# logger.info("epoch hasnt changed. returning")
		return

	harmonyValEpochChange.processEpochChange(conn, app, currentEpoch, currentEpochPerfData)


def processCurrentEpochPerf(conn, app, epoch, enoughDataForCurrentApr):
	logger.info("calculating current aprs for all validators: {}".format(enoughDataForCurrentApr))

	currentPerfData = harmonyData.listHPoolPerfByEpoch(conn, app, epoch, constants.H_EPOCH_MODE)

	updates = []
	for validator in currentPerfData:
		# updateCurrentApr(conn, validator, enoughDataForCurrentApr)
		record = getUpdateCurrentApr(validator, enoughDataForCurrentApr)
		updates.append(record)

	batchUpdateCurrentEpochPerf(conn, updates)
	conn.commit()

	return currentPerfData


def batchUpdateCurrentEpochPerf(conn, updates):
	# logger.info("in batchUpdateCurrentEpochPerf")

	sql = "update " + tables.hpool
	sql += " set currentApr=%s, currentNetApr=%s, currentEri=%s "
	sql += " where hPoolId = %s "

	conn.cursor().executemany(sql, updates)


def getUpdateCurrentApr(validator, enoughDataForCurrentApr):
	# logger.info("in getUpdateCurrentApr: {}".format(enoughDataForCurrentApr))
	# logger.info(sql)
	apr, netApr, eri = None, None, None

	if enoughDataForCurrentApr:
		if validator["apr"]:
			apr = validator["apr"]

		if validator["eri"]:
			eri = validator["eri"]

		if validator["netApr"]:
			netApr = validator["netApr"]

	# logger.info("hPoolId: {}, apr: {}, netApr: {}, eri: {} ".format(
	#     validator["hPoolId"], apr, netApr, eri))
	args = (apr, netApr, eri, validator["hPoolId"])
	# logger.info(args)
	return args


#NOT IN USE: 4th July
# def updateCurrentApr(conn, validator, enoughDataForCurrentApr):
#     # logger.info("updating current aprs for {}".format(enoughDataForCurrentApr))
#     sql = "update " + tables.hpool
#     sql += " set currentApr=%s, currentNetApr=%s, currentEri=%s "
#     sql += " where hPoolId = %s "
#
#     # logger.info(sql)
#     apr, netApr, eri = None, None, None
#
#     if enoughDataForCurrentApr:
#         if validator["apr"]:
#             apr = validator["apr"]
#
#         if validator["eri"]:
#             eri = validator["eri"]
#
#         if validator["netApr"]:
#             netApr = validator["netApr"]
#
#     # logger.info("hPoolId: {}, apr: {}, netApr: {}, eri: {} ".format(
#     #     validator["hPoolId"], apr, netApr, eri))
#     args = (apr, netApr, eri, validator["hPoolId"])
#     # logger.info(args)
#     conn.cursor().execute(sql, args)


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

	# calcUsesPrevEpoch = False
	if currentCoinStat["currentEpoch"] + 1 == currentEpoch:
		# logger.info("epoch has just changed. include blocks from previous epoch")
		if currentCoinStat["recentBlock"] + 1 != firstBlock:
			# logger.info("confirmed need to include blocks from previous epoch")
			blocksPast = currentBlock - currentCoinStat["recentBlock"]
			# calcUsesPrevEpoch = True

	if blocksPast == 0:
		return 0

	completionFactor = totalBlocks/blocksPast
	logger.info("enoughData: {}, completionFactor: {}, currentBlock: {}, lastBlock: {}, firstBlock: {}, blocksPast: {}".format(
	    enoughData, completionFactor, currentBlock, lastBlock, firstBlock, blocksPast))
	return completionFactor, enoughData


def processPerfIndex(conn, app, epochInfo):
	# logger.info("calculating perf index")
	currentEpoch = epochInfo["currentEpoch"]
	poolPerfs = listCurrentValues(conn, currentEpoch, None)

	averageApr = getAverageAprForCurrentEpoch(conn, app, currentEpoch)
	# logger.info("averageApr: {}".format(averageApr))

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


def getAverageAprForCurrentEpoch(conn, app, epochNumber):
	sql = "select sum(totalStaked * apr)/sum(totalStaked) as averageApr "
	sql += " from " + tables.hpoolperf
	sql += " where mode=%s "
	sql += " and epochNumber=%s and elected='True' "

	args = (constants.H_EPOCH_MODE, epochNumber)
	# logger.info(sql)
	# logger.info(args)

	startTime = commonUtils.getCurrentTime()
	data = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, args)
	commonUtils.logTimeDiff(startTime, "after processing getAverageAprForCurrentEpoch")

	return data["averageApr"]


def getStakeWeight(validator, networkStake):
	valStake = validator["totalStaked"]
	# networkStake = float(stakingInfo["totalStake"])

	if not valStake:
		return 0

	return valStake * 100 / networkStake


def getNetworkStake(validators):
	networkStake = 0
	for validator in validators:
		stake = validator["totalStaked"]
		if stake:
			networkStake += stake

	logger.info("network stake is: {}".format(networkStake))
	return networkStake


