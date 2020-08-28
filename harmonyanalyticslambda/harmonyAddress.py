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
	sql = "select addressId, address, addressBalance, txCount, rank "
	sql += " from " + tables.haddress
	sql += " order by rank desc "

	# logger.info(sql)
	
	return  dbUtil.listResultsWithResponseWithConn(sql, conn)


def listAllAddresses(conn, app):
	sql = "select * "
	sql += " from " + tables.haddress
	sql += " order by addressBalance desc "

	# logger.info(sql)
	
	return  dbUtil.listResultsWithResponseWithConn(sql, conn)


def getAddressDisplayDetails(conn, app, address, alias, subType=None):
	# logger.info("subType : " + subType)
	if address is None and alias is not None:
		record = aliasUtils.getAddressFromAlias(conn, app, alias)
		if not record:
			response = "'" + alias + "' - alias not found in server. Please enter the address, alias and use the 'Save Alias in Server' button to save the alias."
			return dbUtil.getResponse(dbUtil.jsondumps({"error": response}))
		address = record["address"]

	coinStats = dbUtil.getSingleRecordNoJsonWithConn(commonUtils.getCoinStatSql(), conn, app)
	addressDetails = getAddressDetails(conn, app, address, alias)
	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyDelegations)

	delegations = getDelegationDetails(conn, address)

	smartStake = None
	if subType == "myAccount":
		# logger.info("checking if smart stake user")
		smartStake = isUsingSmartStake(delegations)

	rewards = harmonyEvents.getRewardsSummary(conn, address)
	stakeHistory = listAddressStakeHistoryChartData(conn, address)
	addressEvents = harmonyEvents.listEventsByAddress(conn, address)
	# logger.info("after calling reportData.listRewardComparisonReportData")

	return dbUtil.combineResults8("addressDetails", addressDetails, "lastUpdated", lastUpdated,
		"delegations", delegations, "rewards", rewards, "stakeHistory", stakeHistory,
		"events", addressEvents, "coinStats", coinStats, "smartStake", smartStake)


def getAddressDetails(conn, app, address, alias):
	sql = " select rank, ha.alias, ha.address, "
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

	logger.info(sql)

	return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, args)


def getDelegationDetails(conn, address):
	logger.info("in getDelegateDetails")
	sql = " select p.hPoolId, p.name, pd.address, p.totalStaked, "
	sql += " stake, reward, p.avgNetApr, p.avgNetApr, currentEpochSignPer, "
	sql += " round(lifetimeSigned * 100/lifetimeToSign, 2) as lifetimeSignPer, "
	sql += " fee, feeChangedEpoch, feeChangedDesc "
	sql += " from " + tables.hpool + " p "
	sql += " inner join " + tables.hpooldel + " pd on pd.hPoolId=p.hPoolId"
	sql += " where pd.address = %s and (pd.stake > 0.1 or pd.reward > 0.1) "
	sql += " order by stake desc "

	logger.info(sql)
	logger.info(address)

	data = dbUtil.listResultsWithConn(sql, conn, (str(address)))
	return data


def listAddressStakeHistoryChartData(conn, address):
	sql = "select epoch, round(value1, 0) as totalStake, value2 as totalBalance, "
	sql += " round(value3, 0) as totalReward from " + tables.hhistory
	sql += " where address = %s and dataType=%s "
	sql += " order by 1 "
	logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn, (address, constants.H_HISTORY_ADDRESS))
	return data

def isUsingSmartStake(delegations):
	# logger.info(" in isUsingSmartStake")
	# logger.info(delegations)

	for d in delegations:
		if d["hPoolId"] == constants.H_POOL_ID_SS:
			return True

	return False