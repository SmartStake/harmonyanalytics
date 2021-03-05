import logging

import aliasUtils
import commonUtils
import constants
import dbUtil
import eventName
import harmonyEvents
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def listAllAddressesBasic(conn, app):
	sql = "select addressId, address, addressBalance, txCount, ranking "
	sql += " from " + tables.haddress
	sql += " order by ranking desc "

	# logger.info(sql)
	
	return  dbUtil.listResultsWithResponseWithConn(sql, conn)


def listAllAddresses(conn, app):
	sql = "select * "
	sql += " from " + tables.haddress
	sql += " order by addressBalance desc "

	# logger.info(sql)
	
	return  dbUtil.listResultsWithResponseWithConn(sql, conn)


def getAddressDisplayDetails(conn, app, address, alias, subType=None):
	startTime = commonUtils.getCurrentTime()
	# logger.info("subType : " + subType)
	if address is None and alias is not None:
		record = aliasUtils.getAddressFromAlias(conn, app, alias)
		commonUtils.logTimeDiff(startTime, "after getting address from alias")
		if not record:
			response = "'" + alias + "' - alias not found in server. Please enter the address, alias and use the 'Save Alias in Server' button to save the alias."
			return dbUtil.getResponse(dbUtil.jsondumps({"error": response}))
		address = record["address"]

	coinStats = dbUtil.getSingleRecordNoJsonWithConn(commonUtils.getCoinStatSql(), conn, app)
	commonUtils.logTimeDiff(startTime, "after getting coinstat")
	addressDetails = getAddressDetails(conn, app, address, alias)
	commonUtils.logTimeDiff(startTime, "after getting address details")
	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyDelegations)
	commonUtils.logTimeDiff(startTime, "after getting event last updated")

	delegations = getDelegationDetails(conn, address)
	commonUtils.logTimeDiff(startTime, "after getting delegations details")

	smartStake = None
	if subType == "myAccount":
		# logger.info("checking if smart stake user")
		smartStake = isUsingSmartStake(delegations)
		commonUtils.logTimeDiff(startTime, "after getting is smart stake")

	rewards = harmonyEvents.getRewardsSummary(conn, address)
	commonUtils.logTimeDiff(startTime, "after getting rewards summary")
	stakeHistory = listAddressStakeHistoryChartData(conn, address, coinStats["currentEpoch"])
	stakeHistory.sort(key=lambda item:item['epoch'], reverse=False)
	commonUtils.logTimeDiff(startTime, "after getting stake history chart")
	# addressEvents = harmonyEvents.listEventsByAddress(conn, address)
	addressEvents = []
	commonUtils.logTimeDiff(startTime, "after getting event details")
	# logger.info("after calling reportData.listRewardComparisonReportData")

	return dbUtil.combineResults8("addressDetails", addressDetails, "lastUpdated", lastUpdated,
		"delegations", delegations, "rewards", rewards, "stakeHistory", stakeHistory,
		"events", addressEvents, "coinStats", coinStats, "smartStake", smartStake)


def getAddressDetails(conn, app, address, alias):
	sql = " select ranking, ha.alias, ha.address, "
	sql += " round(totalStake,2)  as totalStake,  "
	sql += " round(addressBalance,2) as addressBalance, "
	sql += " round(totalRewards,2) as totalRewards, "
	sql += " round(totalBalance, 2) as totalBalance  "
	sql += " from " + tables.haddress + " ha "

	if address is not None:
		sql += " where ha.address = %s "
		args = address
	else:
		sql += " inner join " + tables.addressalias + " aa on ha.address=aa.address"
		sql += " where app = %s and aa.alias = %s "
		args = (app, alias)

	# logger.info(sql)

	return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, args)


def getDelegationDetails(conn, address):
	# logger.info("in getDelegateDetails")

	data = getDelegationData(conn, str(address))

	totalStake, totalRewards = 0, 0
	for record in data:
		totalStake += record["stake"]
		totalRewards += record["reward"]

	details = []
	for record in data:
		calc = True

		if len(record["name"]) > 12:
			record["shortName"] = record["name"][0:11]
		else:
			record["shortName"] = record["name"]

		if not totalStake:
			record["percentStake"] = 0
			calc = False
		if not totalRewards:
			record["percentReward"] = 0
			calc = False

		if not calc:
			record["rewardRatio"] = ""
			details.append(record)
			continue

		percentStake = round(record["stake"] / totalStake, 3)
		percentReward = round(record["reward"] / totalRewards, 3)

		if percentStake == 0:
			rewardRatio = 0
		else:
			rewardRatio = round(percentReward / percentStake, 3)

		record["percentStake"] = percentStake
		record["percentReward"] = percentReward
		record["rewardRatio"] = rewardRatio
		details.append(record)

	# logger.info(details)
	return details


def getDelegationData(conn, address):
	# logger.info("in getDelegateDetails")
	sql = " select p.hPoolId, p.name, pd.address, p.totalStaked, p.address as validatorAddress, "
	sql += " stake, reward, p.avgNetApr, p.avgNetApr, currentEpochSignPer, "
	sql += " round(lifetimeSigned * 100/lifetimeToSign, 2) as lifetimeSignPer, "
	sql += " fee, feeChangedEpoch, feeChangedDesc "
	sql += " from " + tables.hpool + " p "
	sql += " inner join " + tables.hpooldel + " pd on pd.hPoolId=p.hPoolId"
	sql += " where pd.address = %s and (pd.stake > 0.1 or pd.reward > 0.1) "
	sql += " order by stake desc "

	logger.info(sql)
	# logger.info(address)

	data = dbUtil.listResultsWithConn(sql, conn, (str(address)))
	return data


def listAddressStakeHistoryChartData(conn, address, epoch):
	sql = "select epoch, round(value1, 0) as totalStake, value2 as totalBalance, "
	sql += " round(value3, 0) as totalReward from " + tables.hhistory
	sql += " where address = %s and dataType=%s "
	sql += " and epoch > %s "
	sql += " order by 1 "
	# desc limit 35
	#FIXME added limit to try and resolve performance issue
	logger.info(sql)
	oldestEpoch = epoch - 35

	data = dbUtil.listResultsWithConn(sql, conn, (address, constants.H_HISTORY_ADDRESS, oldestEpoch))
	return data

def isUsingSmartStake(delegations):
	# logger.info(" in isUsingSmartStake")
	# logger.info(delegations)

	for d in delegations:
		if d["hPoolId"] == constants.H_POOL_ID_SS:
			return True

	return False


def getActiveAddressCount(conn):
	sql = "select count(*) as totalAddress "
	sql += " from " + tables.haddress
	sql += " where totalBalance > 0 "

	# logger.info(sql)
	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn)

	return record["totalAddress"]


def listAddressEvents(conn, app, address):
	startTime = commonUtils.getCurrentTime()
	addressDetails = getAddressDetails(conn, app, address, None)
	commonUtils.logTimeDiff(startTime, "after getting address details")
	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyDelegations)
	commonUtils.logTimeDiff(startTime, "after getting event last updated")

	addressEvents = harmonyEvents.listEventsByAddress(conn, address)
	commonUtils.logTimeDiff(startTime, "after getting event details")

	return dbUtil.combineResults3("addressDetails", addressDetails,
		"lastUpdated", lastUpdated, "data", addressEvents)
