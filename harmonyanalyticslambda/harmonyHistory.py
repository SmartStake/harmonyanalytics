import logging

import commonUtils
import constants
import dbUtil
import harmonyAddress
import harmonyData
import harmonyShard
import harmonyTransactionSync
import harmonyVersionSync
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getExisting(conn, epoch, dataType, poolId=None):
	sql = "select * from " + tables.hhistory
	sql += " where epoch = %s"
	sql += " and dataType = %s"

	args = (epoch, dataType)
	if poolId is not None:
		sql += " and poolId = %s"
		args = (epoch, dataType, poolId)

	# logger.info(sql)
	# logger.info(args)
	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, args)

	return record


def createHistory(conn, epoch, dataType, value1, poolId=None, keyObject=None,
				  address=None, value2=None, value3=None, value4=None, value5=None, value6=None,
				  value7=None, value8=None):

	sql = "INSERT INTO " + tables.hhistory
	sql += "(epoch, dataType, poolId, keyObject, "
	sql += " address, value1, value2, value3, "
	sql += " value4, value5, value6, value7, value8) "
	sql += " VALUES (%s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s, %s, %s, %s, %s)"

	# logger.info(sql)
	args = (epoch, dataType, poolId, keyObject, address,
			value1, value2, value3, value4, value5, value6,
			value7, value8)

	# logger.info(args)
	conn.cursor().execute(sql, args)


def batchCreateHistory(conn, historyRecords):
	sql = "INSERT INTO " + tables.hhistory
	sql += "(epoch, dataType, poolId, keyObject, "
	sql += " address, value1, value2, value3, "
	sql += " value4, value5, value6) "
	sql += " VALUES (%s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s, %s, %s)"

	conn.cursor().executemany(sql, historyRecords)


def getCreateHistoryData(epoch, dataType, value1, poolId=None, keyObject=None,
						 address=None, value2=None, value3=None, value4=None, value5=None, value6=None):

	# logger.info(sql)
	args = (epoch, dataType, poolId, keyObject, address,
			value1, value2, value3, value4, value5, value6)

	return args



def listAddressHistory(conn, app, event):
	address = None
	if "address" in event["queryStringParameters"]:
		address = event["queryStringParameters"]["address"]

	return listStakeHistoryChartData(conn, app, constants.H_HISTORY_ADDRESS, None, address)


def listNetworkStakeHistory(conn, app, event):
	return listStakeHistoryChartData(conn, app, constants.H_HISTORY_NETWORK)


def listStakeHistoryChartData(conn, app, dataType, hPoolId=None, address=None):
	# sql = "select date(procDate) as title, round(totalStake/" + factor + ", 3) as value from "
	sql = "select epoch, value1, value2, value3, value4, value5, value6 from "
	sql += tables.hhistory
	sql += " where dataType=%s "

	args = (dataType)
	if hPoolId is not None:
		sql += " and hPoolId = %s "
		args = (dataType, hPoolId)
	elif address is not None:
		sql += " and address = %s "
		args = (dataType, address)
	sql += " order by epoch "
	# logger.info(sql)
	# logger.info(args)

	if hPoolId is None:
		return dbUtil.listResultsWithResponseWithConn(sql, conn, args)
	else:
		data = dbUtil.listResultsWithConn(sql, conn, args)
		validator = harmonyData.getHPoolById(conn, hPoolId)
		return dbUtil.combineResults2("validator", validator, "data", data)


def updateNetworkHistory(conn, epoch, totalStake, circulatingSupply,
	 currentRewardRate, totalValidators, btcPrice, medianRawStake, uniqueDelegates):

	currentData = getExisting(conn, epoch, constants.H_HISTORY_NETWORK)

	#totalValidators > 100 check is only temporary
	if currentData is None:
		totalAddresses = harmonyAddress.getActiveAddressCount(conn)
		# logger.info("inserting validator record for id: " + address)
		createHistory(conn, epoch, constants.H_HISTORY_NETWORK,
			 totalStake, None, None, None, circulatingSupply,
			 currentRewardRate, totalValidators, btcPrice, medianRawStake,
			 uniqueDelegates, totalAddresses)


def listNetworkHistory(conn, app):
	startTime = commonUtils.getCurrentTime()

	sql = "select epoch as title, value1 as totalStake, "
	sql += " round(value1/1000000, 3) as totalStakeInMillions, "
	sql += " round(value2/1000000, 1) as circulatingSupplyInMillions, "
	sql += " value2 as circulatingSupply, "
	sql += " value3 as rewardRate, value4 as totalValidators, "
	sql += " value5 as btcPrice, value6 as medianRawStake, "
	sql += " round(value6/1000000, 1) as medianRawStakeInMillions, "
	sql += " value7 as uniqueDelegates, value8 as totalAddresses, "
	sql += " value9 as signRate "
	sql += " from " + tables.hhistory
	sql += " where dataType='Network' "
	sql += " order by epoch "
	# logger.info(sql)
	commonUtils.logTimeDiff(startTime, "after network stats")

	stats = dbUtil.listResultsWithConn(sql, conn)
	commonUtils.logTimeDiff(startTime, "after stats")

	coinStat = commonUtils.getCoinStat(conn, app)
	commonUtils.logTimeDiff(startTime, "after coinStat")

	txSummary = harmonyTransactionSync.listDailyTransactions(conn)
	commonUtils.logTimeDiff(startTime, "after tx summary")

	shardTxSummary = harmonyTransactionSync.listShardSummaryTransactions(conn)
	commonUtils.logTimeDiff(startTime, "after shard tx summary")
	# dailyShardTxSummary = harmonyTransactionSync.listDailyShardTransactions(conn)

	blockRate = harmonyShard.getBlockRateHistory(conn)
	commonUtils.logTimeDiff(startTime, "after block rate history")

	nodeVersionSummary = harmonyVersionSync.listNodeVersionSummary(conn)
	commonUtils.logTimeDiff(startTime, "after nodeVersionSummary")

	# logger.info("shardTxSummary: {}".format(shardTxSummary))
	return dbUtil.combineResults6("data", stats, "coinStat", coinStat,
		"txSummary", txSummary, "shardTxSummary", shardTxSummary,
		"blockRate", blockRate, "nodeVersionSummary", nodeVersionSummary)


def listNetworkStake(conn, app):
	return listNetworkHistory(conn, app)
	# sql = "select epochNumber as title, "
	# sql += " round(sum(totalStaked)/1000000, 3) as totalStakeInMillions "
	# sql += " from " + tables.hpoolperf
	# sql += " where mode='EPOCH' "
	# sql += " group by epochNumber order by epochNumber "
	# # logger.info(sql)
	#
	# data = dbUtil.listResultsWithConn(sql, conn)
	# coinStat = commonUtils.getCoinStat(conn, app)
	# return dbUtil.combineResults2("data", data, "coinStat", coinStat)


def listNetworkStats(conn, app):
	coinStat = commonUtils.getCoinStat(conn, app)

	shardData = harmonyShard.getShardDataFromDB(conn)

	return dbUtil.combineResults2("coinStat", coinStat, "shardData", shardData)

