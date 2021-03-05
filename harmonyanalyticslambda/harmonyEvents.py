import logging
import time

import auditUtils
import commonUtils
import dbUtil
import eventName
import hConstants
import harmonyData
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# app = constants.HARMONY

def createFeeEvent(conn, eventType, hPoolId, epochNumber, newFee):
	logger.info("ignore fee creation event from validator")
	# createEvent(conn, int(time.time()), eventType, None, None,
	# 			epochNumber, None, hPoolId, None, (newFee * 100))


def createEvent(conn, blockTime, eventType, blockNumber, txHash, epochNumber, address, hPoolId, otherAddress, amount):
	sql = "INSERT INTO " + tables.hevent
	sql += "(eventType, blockNumber, txHash, epochNumber, address, "
	sql += " hPoolId, amount, epochBlockTime, otherAddress) "
	sql += "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

	insertData = (eventType, blockNumber, txHash, epochNumber, address,
				  hPoolId, amount, blockTime, otherAddress)

	# logger.info("{0}: {1}".format(sql, insertData))
	conn.cursor().execute(sql, insertData)


def getCreateData(blockTime, eventType, event, poolId, address, otherAddress, isAmountPresent, rewardsInd):
	amount = None
	if isAmountPresent:
		amount = event["amount"]

	insertData = (eventType, event["height"], event["txHash"], address,
				  poolId, amount, blockTime, otherAddress, rewardsInd)
	return insertData


def batchCreateEvents(conn, events):
	# logger.info("creating events: {}".format(len(events)))
	sql = "INSERT INTO " + tables.hevent
	sql += "(eventType, blockNumber, txHash, address, "
	sql += " hPoolId, amount, epochBlockTime, otherAddress) "
	sql += "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

	inserts = conn.cursor().executemany(sql, events)
	if inserts <= 0:
		raise Exception("insert failure with inserted records equals zero")


def listEvents(conn, app, event, poolId, startTime):
	# logger.info("in listevents method")
	size = 500
	subType = None
	if "size" in event["queryStringParameters"]:
		size = int(event["queryStringParameters"]["size"])
	if "subType" in event["queryStringParameters"]:
		subType = event["queryStringParameters"]["subType"]

	# logger.info("params are: {}, {}".format(poolId, subType))
	sql = listEventsSql(poolId, None, size, subType)

	params = ()
	if poolId:
		if subType and subType != "others" and subType != "large" and subType != "val" and subType != "fee":
			params = (poolId, subType)
		else:
			params = poolId
		data = dbUtil.listResultsWithConn(sql, conn, params)
		val = harmonyData.getHPoolById(conn, poolId)
		return dbUtil.combineResults2("val", val, "data", data)
	else:
		if subType and subType != "others" and subType != "large" and subType != "val" and subType != "fee":
			params = subType
		return dbUtil.listResultsWithResponseWithConn(sql, conn, params)


def listEventsSql(poolId, address, size=500, subType=None, days=None):
	# ct.description as eventTypeDesc,
	sql = "select he.eventId, he.address, p.name, he.eventType, he.otherAddress, "
	sql += " he.blockNumber, he.epochBlockTime, he.txHash, he.amount, "
	sql += " p.hPoolId, round((UNIX_TIMESTAMP() - he.epochBlockTime) / 60,0) as elapsedTime "
	sql += " from " + tables.hevent + " he "
	sql += " left join " + tables.hpool + " p on p.hPoolId=he.hPoolId "
	sql += " where 1=1 "
	if poolId:
		sql += " and p.hPoolId = %s "
	if address:
		sql += " and he.address = %s"

	if days:
		sql += " and he.epochBlockTime > %s"


	if subType:
		if subType == "others":
			sql += " and he.eventType not in ('" + hConstants.H_EVENT_DELEGATE + "', '" \
				   + hConstants.H_EVENT_UNDELEGATE + "', '" \
				   + hConstants.H_EVENT_COLLECT_REWARDS + "') "
		elif subType == "large":
			sql += " and he.amount > 1000000 "
		elif subType == "val":
			sql += " and he.eventType in ('" + hConstants.H_EVENT_EDIT_VALIDATOR + "', '" \
				   + hConstants.H_EVENT_FEE_INCREASE + "', '" \
				   + hConstants.H_EVENT_FEE_DECREASE + "', '" \
				   + hConstants.H_EVENT_BLS_KEY_ADDED + "', '" \
				   + hConstants.H_EVENT_BLS_KEY_REMOVED + "') "
		elif subType == "fee":
			sql += " and he.eventType in ('" + hConstants.H_EVENT_FEE_DECREASE + "', '" \
				   + hConstants.H_EVENT_FEE_INCREASE + "') "
		else:
			sql += " and he.eventType = %s "

	sql += " order by he.blockNumber desc limit " + str(size)

	# logger.info(sql)
	return sql


def listEventsByPoolId(conn, poolId, days=None):
	# logger.info("in listEventsByPoolId method")
	sql = listEventsSql(poolId, None, 200, None, days)
	# logger.info(sql)
	# , (address)
	args = (poolId)
	if days:
		currentTime = int(time.time())
		useTime  = currentTime - days * 86400
		args = (poolId, useTime)
	# logger.info(args)
	return dbUtil.listResultsWithConn(sql, conn, args)


def listEventsByAddress(conn, address):
	# logger.info("in listEventsByAddress method")
	sql = listEventsSql(None, address)

	return dbUtil.listResultsWithConn(sql, conn, address)


def getRewardsSummary(conn, address):
	sql = "select date(from_unixtime(epochBlockTime)) as procDate, sum(amount) as rewards from "
	sql += tables.hevent
	sql += " where address = %s and eventType=%s"
	sql += " group by date(from_unixtime(epochBlockTime)) "
	sql += " order by 1 "
	# logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn, (address, hConstants.H_EVENT_COLLECT_REWARDS))
	return data


def handleFeeChange(e, validatorDetails, poolMap, coinStat):
	# logger.info("in handlefeechange")
	fee = round(commonUtils.divideByTenPower18(validatorDetails["commissionRate"]), 4)
	validator = poolMap[e["validatorAddress"]]
	if not validator:
		# logger.info("in handlefeechange - returning no validator")
		return None

	eventType = None
	# logger.info("e: {}, coinStat: {}, validator: {}".format(e, coinStat, validator))
	if e["blockNumber"] < coinStat["recentBlock"]:
		# logger.info("fee change already updated in db, dig up previous fee and use that")
		#fee change already updated in db, dig up previous fee and use that
		if fee > validator["prevFee"]:
			# logger.info("fee > validator[prevFee]")
			eventType = hConstants.H_EVENT_FEE_INCREASE
		elif fee < validator["prevFee"]:
			# logger.info("fee < validator[prevFee]")
			eventType = hConstants.H_EVENT_FEE_DECREASE
		else:
			logger.info("in else: fee : {} < validator[prevFee]: {}".format(fee, validator["prevFee"]))
	else:
		# logger.info("fee change not yet updated in db")
		#fee change not yet updated in db
		if fee > validator["fee"]:
			# logger.info("fee > validator[fee]")
			eventType = hConstants.H_EVENT_FEE_INCREASE
		elif fee < validator["fee"]:
			# logger.info("fee < validator[fee]")
			eventType = hConstants.H_EVENT_FEE_DECREASE
		else:
			logger.info("in else: fee : {} < validator[fee]: {}".format(fee, validator["fee"]))

	if eventType:
		# logger.info("in handlefeechange - returning : " + eventType)
		return (eventType, e["blockNumber"], e["txHash"], e["address"],
				  validator["hPoolId"], (fee * 100), e["epochTimestamp"], None)

	# logger.info("in handlefeechange - returning none in end")
	return None


def processEditValDetails(e, poolMap, coinStat):
	# logger.info(e)
	# record = (eventType, e["blockNumber"], e["txHash"], e["address"],
	# 		  poolMap[e["validatorAddress"]]["hPoolId"], None, e["epochTimestamp"], None)
	# Transaction details: {"commissionRate": 0, "details": "", "identity": "", "maxTotalDelegation": 0,
	# "minSelfDelegation": 0, "name": "", "securityContact": "", "slotPubKeyToAdd":
	# "04b4fe8412dd39e17e39cd4ede0e3b614b922edafbf70d5f643595e67df486d381de9bea029cf8b739a370958c765317",
	# "slotPubKeyToRemove": null, "validatorAddress": "one1wc32qcufuc8lzfs804dtrjrq2zufnkczp43u75",
	# "website": ""}Block number: 4980732.

	validatorDetails = e["msg"]

	records = []
	if validatorDetails["commissionRate"]:
		#fee changed
		record = handleFeeChange(e, validatorDetails, poolMap, coinStat)
		if record:
			records.append(record)

	if validatorDetails["slotPubKeyToAdd"]:
		#key add
		record = (hConstants.H_EVENT_BLS_KEY_ADDED, e["blockNumber"], e["txHash"], e["address"],
				  poolMap[e["validatorAddress"]]["hPoolId"], None, e["epochTimestamp"], None)
		records.append(record)

	if validatorDetails["slotPubKeyToRemove"]:
		#key remove
		record = (hConstants.H_EVENT_BLS_KEY_REMOVED, e["blockNumber"], e["txHash"], e["address"],
				  poolMap[e["validatorAddress"]]["hPoolId"], None, e["epochTimestamp"], None)
		records.append(record)

	return records


def syncEvents(conn, app, data, startTime):
	# logger.info("syncing harmony events")
	poolMap = harmonyData.listHPoolsAsMap(conn)

	# startBlock = data["startBlockHeight"]
	endBlock = data["blockHeight"]

	events = data["events"]
	inserts = []

	coinStat = commonUtils.getCoinStat(conn, app)
	for e in events:
		if "validatorAddress" in e and e["validatorAddress"] not in poolMap:
			# logger.info("the validator {} is not known. skipping event.".format(e["validatorAddress"]))
			continue

		eventType = e["type"]
		if eventType == hConstants.H_EVENT_DELEGATE or eventType == hConstants.H_EVENT_UNDELEGATE :
			record = (eventType, e["blockNumber"], e["txHash"], e["address"],
					  poolMap[e["validatorAddress"]]["hPoolId"], e["amount"], e["epochTimestamp"], None)
			inserts.append(record)
		elif eventType == hConstants.H_EVENT_COLLECT_REWARDS:
			record = (eventType, e["blockNumber"], e["txHash"], e["address"],
					  None, e["amount"], e["epochTimestamp"], None)
			inserts.append(record)
		elif eventType == hConstants.H_EVENT_EDIT_VALIDATOR:
			record = (eventType, e["blockNumber"], e["txHash"], e["address"],
					  poolMap[e["validatorAddress"]]["hPoolId"], None, e["epochTimestamp"], None)
			inserts.append(record)
			specialRecords = processEditValDetails(e, poolMap, coinStat)
			if specialRecords:
				inserts.extend(specialRecords)
		elif eventType == hConstants.H_CREATE_VALIDATOR:
			record = (eventType, e["blockNumber"], e["txHash"], e["address"],
					  poolMap[e["validatorAddress"]]["hPoolId"], None, e["epochTimestamp"], None)
			inserts.append(record)
		# hTgNotify.handleEvent(conn, e, poolMap)

	# logger.info("inserts are:")
	# logger.info(inserts)
	if len(inserts) > 0:
		batchCreateEvents(conn, inserts)

	auditUtils.createEvent(conn, app, hConstants.EVENT_LAST_SYNCED_EVENT_BLOCK_HEIGHT, endBlock)
	auditUtils.createEvent(conn, app, eventName.syncHarmonyEvents)
	# logger.info("finished processing all events")
	conn.commit()

