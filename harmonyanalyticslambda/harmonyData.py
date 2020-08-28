import datetime
import logging

import auditUtils
import commonUtils
import constants
import dbUtil
import eventName
import getHealthSummary
import harmonyAddress
import harmonyEvents
import harmonyHistory
import harmonyRewards
import paramUtils
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MIN_AMOUNT = "0.1"


def getHPoolId(event):
	hPoolId = None
	if "hPoolId" in event["queryStringParameters"]:
		hPoolId = paramUtils.getIntParam(event, "hPoolId")
	return hPoolId


def listHData(conn, app, event, context, startTime, dataType):
	logger.info("in harmony list data - {}".format(dataType))
	data = None
	if dataType == "listPools":
		status = None
		if "status" in event["queryStringParameters"]:
			status = event["queryStringParameters"]["status"]
		data = listHPools(conn, app, status)
		auditUtils.audit(conn, app, event, "listData_" + dataType, "get", startTime)
	elif dataType == "event":
		data = getEventDetails(conn, event)
	elif dataType == "listApr":
		data = listHPoolsApr(conn, app)
	elif dataType == "getPool":
		hPoolId = getHPoolId(event)
		# logger.info("hPoolId: %s", hPoolId)
		more = False
		if "showMore" in event["queryStringParameters"]:
			# logger.info(event["queryStringParameters"])
			more = event["queryStringParameters"]["showMore"]
		# logger.info("show more: {}".format(more))
		data = getHPool(conn, app, hPoolId, more)
		auditUtils.audit(conn, app, event, "listData_" + dataType, "get", startTime)
	elif dataType == "health":
		data = getHealthSummary.listHealthCheckData(conn, app, event, startTime)
	# elif dataType == "listValPerf":
	# 	data = listValPerformanceData(conn, app, event, startTime)
	elif dataType == "listAllDelegates":
		data = listAllDelegates(conn, app)
	elif dataType == "listAllAddresses":
		data = harmonyAddress.listAllAddresses(conn, app)
	elif dataType == "listAllAddressesBasic":
		data = harmonyAddress.listAllAddressesBasic(conn, app)
	elif dataType == "richlist":
		count = 200
		if "count" in event["queryStringParameters"]:
			count = int(event["queryStringParameters"]["count"])
			if count == 100:
				count = 200
		data = getRichList(conn, app, count)
	elif dataType == "delegates":
		hPoolId = getHPoolId(event)
		data = listDelegates(conn, app, hPoolId)
	elif dataType == "richDelegates":
		data = getRichDelegates(conn, app)
	elif dataType == "networkStakeHistory":
		data = harmonyHistory.listNetworkStakeHistory(conn, app, event)
	elif dataType == "rewardsHistory":
		data = harmonyRewards.listRewardsHistory(conn, app, event, context, startTime)
	# elif dataType == "valStakeHistory":
	# 	data = harmonyHistory.listValStakeHistory(conn, app, event)
	elif dataType == "addressHistory":
		data = harmonyHistory.listAddressHistory(conn, app, event)
	elif dataType == "valPerf":
		hPoolId = getHPoolId(event)
		data = listPerf(conn, app, hPoolId)
	elif dataType == "networkStake":
		data = listNetworkStake(conn, app)
	elif dataType == "addressDetails":
		alias, address, subType = None, None, None
		if "address" in event["queryStringParameters"]:
			address = event["queryStringParameters"]["address"]
		elif "alias" in event["queryStringParameters"]:
			alias = event["queryStringParameters"]["alias"]

		if "subType" in event["queryStringParameters"]:
			subType = event["queryStringParameters"]["subType"]
		data = harmonyAddress.getAddressDisplayDetails(conn, app, address, alias, subType)
		auditUtils.audit(conn, app, event, "address", "get", startTime)
	elif dataType == "events":
		hPoolId = paramUtils.getOptionalIntParam(event, "hPoolId")
		data = harmonyEvents.listEvents(conn, app, event, hPoolId, startTime)

	return data


def listAllDelegates(conn, app):
	sql = "select hd.poolDelId, h.hPoolId, hd.address, hd.stake, hd.reward,  "
	sql += " h.lastUpdated, h.address as validator "
	sql += " from " + tables.hpooldel + " hd "
	sql += " inner join " + tables.hpool + " h "
	sql += " on h.hPoolId=hd.hPoolId "

	# logger.info(sql)

	return dbUtil.listResultsWithResponseWithConn(sql, conn)


def getPerfChartData(conn, hPoolId, hourly, mode, more):
	if hourly:
		dateColumn = "date_format(syncTime,'%%Y-%%m-%%d %%H')"
	else:
		dateColumn = "date_format(syncTime,'%%Y-%%m-%%d')"

	sql = "select " + dateColumn + " as title, signed, askedToSign, "
	sql += " (askedToSign - signed) as notSigned, signPer, rewards "
	sql += " from " + tables.hpoolperf
	sql += " where hPoolId=%s "
	sql += " and mode = %s "

	dt = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
	if hourly:
		maxHours = 24
		if more == 'true':
			maxHours = 240

		oldestTime = (dt - datetime.timedelta(hours=maxHours))
		sql += " and syncTime >= '" + str(oldestTime) + "'"
	else:
		dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
		oldestTime = (dt - datetime.timedelta(days=14))
		sql += " and syncTime >= '" + str(oldestTime) + "'"

	# sql += " group by " + dateColumn
	sql += " order by 1 "

	# logger.info(sql)

	return dbUtil.listResultsWithConn(sql, conn, (hPoolId, mode))


def getEpochChartData(conn, hPoolId, more):
	maxEpochs = 10
	if more == 'true':
		maxEpochs = 30

	sql = "select epochNumber as title, signed, askedToSign, "
	sql += " (askedToSign - signed) as notSigned, signPer, rewards "
	sql += " from " + tables.hpoolperf
	sql += " where hPoolId=%s "
	sql += " and mode = %s "

	dt = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	oldestTime = (dt - datetime.timedelta(days=maxEpochs))
	sql += " and syncTime >= '" + str(oldestTime) + "'"

	sql += " order by 1 "

	# logger.info(sql)

	return dbUtil.listResultsWithConn(sql, conn, (hPoolId, constants.H_EPOCH_MODE))


def getHPool(conn, app, hPoolId, more):
	validator = getHPoolById(conn, hPoolId)
	hourlyChartData = getPerfChartData(conn, hPoolId, True, constants.H_HOUR_MODE, more)
	dailyChartData = getEpochChartData(conn, hPoolId, more)
	coinStat = commonUtils.getCoinStat(conn, app)
	events = harmonyEvents.listEventsByPoolId(conn, hPoolId)

	notification = commonUtils.getNotification(conn, app, hPoolId)
	# logger.info(notification)
	return dbUtil.combineResults6("val", validator, "hourlyChartData", hourlyChartData,
								  "dailyChartData", dailyChartData, "notification", notification,
								  "coinStat", coinStat, "events", events)


def getHPoolById(conn, hPoolId):
	sql = "select p.*, (UNIX_TIMESTAMP() - p.syncEpochTime) as lastUpdatedGap "
	sql += " from " + tables.hpool + " p "
	sql += " where p.hPoolId = %s "

	# logger.info(sql)
	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, hPoolId)
	# logger.info("record is: " + str(record))

	return record


def getHarmonyPool(conn, address):
	sql = "select * from " + tables.hpool
	sql += " where address = %s "

	# logger.info(sql)
	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, address)
	# logger.info("record is: " + str(record))

	return record


def listHPools(conn, app, status):
	# logger.info("listing harmony pools")
	sql, args = listHPoolsSql(status)
	# logger.info(args)
	data = dbUtil.listResultsWithConn(sql, conn, args)
	# logger.info(data)
	coinStat = commonUtils.getCoinStat(conn, app)
	statusSummary = getHStatusMap(conn)
	statusSummary[constants.ALL_FEE_INCREASE] = getFeeIncreaseCount(conn)
	# logger.info(statusSummary)

	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyValidators)
	notification = commonUtils.getNotification(conn, app)

	return dbUtil.combineResults5("data", data, "lastUpdated", lastUpdated,
								  "notification", notification, "statusSummary", statusSummary,
								  "coinStat", coinStat)


def getFeeIncreaseCount(conn):
	sql = " select count(*) as FeeIncrease "
	sql += " from " + tables.hpool + " p "
	sql += " where p.feeChangedEpoch > "
	sql += " (select currentEpoch - 7 from " + tables.coinstat + " where symbol='HARMONY') "
	# logger.info(sql)

	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn)
	return record["FeeIncrease"]


def listHPoolsApr(conn, app):
	sql = " select hPoolId as code, name as description, lifetimeApr, fee "
	sql += " from " + tables.hpool + " p "

	data = dbUtil.listResultsWithConn(sql, conn)

	coinStat = commonUtils.getCoinStat(conn, app)

	return dbUtil.combineResults2("data", data, "coinStat", coinStat)


def listHPoolsAsMap(conn):
	sql = " select * "
	sql += " from " + tables.hpool + " p "
	# logger.info(sql)
	data = dbUtil.listResultsWithConn(sql, conn)
	# logger.info(data)
	return commonUtils.getMapFromList(data, "address")


def listHPoolPerfByEpoch(conn, app, epochNumber, mode):
	sql = " select * "
	sql += " from " + tables.hpoolperf + " p "
	sql += " where p.epochNumber =%s and mode=%s "

	# logger.info(sql)
	data = dbUtil.listResultsWithConn(sql, conn, (epochNumber, mode))

	return data


def listHPoolPerfByEpochRange(conn, app, startEpochNumber, endEpochNumber, mode):
	sql = " select hPoolId, avg(apr) as avgApr, count(*) as epochsPresent, "
	sql += " min(epochNumber) as oldestEpoch, avg(eri) as avgEri "
	sql += " from " + tables.hpoolperf + " p "
	sql += " where p.epochNumber between %s and %s and mode=%s "
	sql += " group by hPoolId "

	# logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn, (startEpochNumber, endEpochNumber, mode))

	# logger.info(data)
	return data


def listHPoolsSql(status, orderBy="rand()"):
	args = {}
	# if status and status != constants.ALL_ELIGIBLE and status != constants.ALL_STATUS:

	sql = " select p.*, round(lifetimeSigned * 100/lifetimeToSign, 2) as lifetimeSignPer "
	sql += " from " + tables.hpool + " p "
	if status is not None:
		# logger.info("status not none")
		if status == constants.ALL_ELIGIBLE:
			# logger.info("status is constants.ALL_ELIGIBLE")
			sql += " where p.status in " + constants.ALL_ELIGIBLE_CLAUSE
		elif status == constants.ALL_FEE_INCREASE:
			# logger.info("status is not constants.ALL_STATUS")
			sql += " where p.feeChangedEpoch > "
			sql += " (select currentEpoch - 7 from " + tables.coinstat + " where symbol='HARMONY') "
		elif status != constants.ALL_STATUS:
			# logger.info("status is not constants.ALL_STATUS")
			sql += " where p.status = %s "
			args = {status}
	sql += " order by " + orderBy
	# logger.info(sql)

	return sql, args


def getHStatusMap(conn):
	statusList = dbUtil.listResultsWithConn(listHStatusSummarySql(), conn)
	# logger.info(statusList)

	statusMap = {constants.H_ELECTED: 0, constants.H_ELIGIBLE: 0,
				 constants.H_NOT_ELIGIBLE: 0}

	return commonUtils.getStatusSummaryMap(statusList, {})


def listHStatusSummarySql():
	sql = " select status, count(*) as total "
	sql += " from " + tables.hpool
	sql += " group by status order by count(*) desc "
	# logger.info(sql)

	return sql


def listPoolsSqlWithIds(app, poolIds):
	sql = " select p.* "
	sql += " from " + tables.hpool + " p "
	sql += " where p.hPoolId in (" + poolIds + ") "
	sql += " order by totalStaked"

	# logger.info(sql)

	return sql


def isAlreadyExistingAddress(conn, address):
	sql = "select count(*) as recordCount from " + tables.haddress
	sql += " where address = %s "

	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, address)
	count = record["recordCount"]

	if count > 0:
		return True

	return False


def getRichListSqlForRank(count):
	sql = " select address, rank, addressId, "
	sql += " round(totalBalance,0) as totalBalance "
	sql += " from " + tables.haddress
	sql += " where totalBalance > " + MIN_AMOUNT
	sql += " order by totalBalance desc "
	sql += " limit " + str(count)

	# logger.info(sql)

	return sql


def getRichListSql():
	sql = " select address, alias, rank, addressId, round(totalStake,0)  as totalStake, "
	sql += " (case when (totalBalance - totalStake >= 0) then round(totalBalance - totalStake) else 0 end) as addressBalance, "
	sql += " round(totalBalance,0) as totalBalance, totalRewards, "
	sql += " (Case when alias is null then address else alias end) as label "
	sql += " from " + tables.haddress
	sql += " where totalBalance > " + MIN_AMOUNT
	sql += " order by totalBalance desc "
	sql += " limit %s"

	# logger.info(sql)

	return sql


def getRichList(conn, app, count):
	# logger.info(sql)
	sql = getRichListSql()

	data = dbUtil.listResultsWithConn(sql, conn, count)
	# logger.info(data)
	coinStat = commonUtils.getCoinStat(conn, app)

	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyAddresses)

	return dbUtil.combineResults3("data", data, "lastUpdated", lastUpdated,
								  "coinStat", coinStat)


def listDelegates(conn, app, hPoolId):
	sql = " select ad.rank, p.name, pd.address, round(pd.stake,0) as stake, round(reward,0) as reward "
	sql += " from " + tables.hpool + " p "
	sql += " inner join " + tables.hpooldel + " pd on pd.hPoolId=p.hPoolId"
	sql += " inner join " + tables.haddress + " ad on ad.address=pd.address"
	sql += " where p.hPoolId = %s "
	sql += " and pd.stake > " + MIN_AMOUNT
	sql += " order by pd.stake desc "

	# logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn, (str(hPoolId)))
	# logger.info("getting pool details")
	val = getHPoolById(conn, hPoolId)
	return dbUtil.combineResults2("val", val, "data", data)


def getRichDelegates(conn, app):
	sql = " select ad.rank, pd.address, round(sum(pd.stake),0) as totalStake,  "
	sql += " group_concat(p.name) as validators "
	sql += " from " + tables.hpool + " p "
	sql += " inner join " + tables.hpooldel + " pd on pd.hPoolId=p.hPoolId"
	sql += " inner join " + tables.haddress + " ad on ad.address=pd.address"
	sql += " where pd.stake > " + MIN_AMOUNT
	sql += " group by pd.address order by totalStake desc "
	sql += " limit 2000 "

	# logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn)
	coinStat = commonUtils.getCoinStat(conn, app)

	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyAddresses)

	return dbUtil.combineResults3("data", data, "lastUpdated", lastUpdated,
								  "coinStat", coinStat)


def listPerf(conn, app, hPoolId):
	sql = "SELECT epochNumber as title, eri, apr as er, netApr as netEr, 1 as average, "
	sql += " blsKeyCount, uniqueDelegates, round(totalStaked) as totalStaked, "
	sql += " round(totalStaked/1000000, 3) as totalStakeInMillions, "
	sql += " round(selfStake) as selfStake, round(bidPerSeat) as bidPerSeat, fee, elected "
	sql += " from " + tables.hpoolperf
	sql += " where hPoolId=%s and mode='EPOCH'"
	sql += " order by epochNumber"
	# logger.info(sql)

	perfData = dbUtil.listResultsWithConn(sql, conn, hPoolId)
	validator = getHPoolById(conn, hPoolId)
	notification = commonUtils.getNotification(conn, app, hPoolId)
	return dbUtil.combineResults3("val", validator, "perfData", perfData,
								  "notification", notification)


def listNetworkStake(conn, app):
	sql = "select epochNumber as title, "
	sql += " round(sum(totalStaked)/1000000, 3) as totalStakeInMillions "
	sql += " from " + tables.hpoolperf
	sql += " where mode='EPOCH' "
	sql += " group by epochNumber order by epochNumber "
	logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn)
	coinStat = commonUtils.getCoinStat(conn, app)
	return dbUtil.combineResults2("data", data, "coinStat", coinStat)


def getEventDetails(conn, event):
	value = event["queryStringParameters"]["eventName"]

	# logger.info(value)
	return dbUtil.getSingleRecordResponseWithConn(commonUtils.getEventSql(), conn, value)

