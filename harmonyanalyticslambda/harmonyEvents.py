import logging
import time

import auditUtils
import constants
import dbUtil
import eventName
import hConstants
import hTgNotify
import harmonyData
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = constants.HARMONY


def createFeeEvent(conn, eventType, hPoolId, epochNumber, newFee):
	createEvent(conn, int(time.time()), eventType, None, None,
				epochNumber, None, hPoolId, None, (newFee * 100))


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
	logger.info("in listevents method")
	size = 500
	subType = None
	if "size" in event["queryStringParameters"]:
		size = int(event["queryStringParameters"]["size"])
	if "subType" in event["queryStringParameters"]:
		subType = event["queryStringParameters"]["subType"]

	logger.info(str(poolId))
	sql = listEventsSql(poolId, None, size, subType)

	params = ()
	if poolId:
		if subType and subType != "others" and subType != "large":
			params = (poolId, subType)
		else:
			params = (poolId)
		data = dbUtil.listResultsWithConn(sql, conn, params)
		val = harmonyData.getHPoolById(conn, poolId)
		return dbUtil.combineResults2("val", val, "data", data)
	else:
		if subType and subType != "others" and subType != "large":
			params = (subType)
		return dbUtil.listResultsWithResponseWithConn(sql, conn, params)


def listEventsSql(poolId, address, size=500, subType=None):
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

	if subType:
		if subType == "others":
			logger.info("others")
			# sql += " and he.eventType not in ('" + constants.EVENT_TYPE_ESCROW_ADD + "', '" \
			# 	   + constants.EVENT_TYPE_ESCROW_RECLAIM + "', '" \
			# 	   + constants.EVENT_TYPE_TRANSFER + "') "
		elif subType == "large":
			sql += " and he.amount > 1000000 "
		else:
			sql += " and he.eventType = %s "

	sql += " order by he.blockNumber desc limit " + str(size)

	# logger.info(sql)
	return sql


def listEventsByPoolId(conn, poolId):
	# logger.info("in listEventsByPoolId method")
	sql = listEventsSql(poolId, None, 200)
	# , (address)
	return dbUtil.listResultsWithConn(sql, conn, poolId)


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
	logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn, (address, hConstants.H_EVENT_COLLECT_REWARDS))
	return data


def syncEvents(conn, app, data, startTime):
	logger.info("syncing harmony events")
	poolMap = harmonyData.listHPoolsAsMap(conn)

	startBlock = data["startBlockHeight"]
	endBlock = data["blockHeight"]

	events = data["events"]
	inserts = []

	for e in events:
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
		hTgNotify.handleEvent(conn, e, poolMap)

	# logger.info("inserts are:")
	# logger.info(inserts)
	if len(inserts) > 0:
		batchCreateEvents(conn, inserts)

	auditUtils.createEvent(conn, app, hConstants.EVENT_LAST_SYNCED_EVENT_BLOCK_HEIGHT, endBlock)
	auditUtils.createEvent(conn, app, eventName.syncHarmonyEvents)
	logger.info("finished processing all events")
	conn.commit()

