import logging

import auditUtils
import commonUtils
import dbUtil
import hConstants
import harmonyAddress
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def listRewardsHistory(conn, app, event, showHistory, startTime):
	# logger.info("in listRewardsHistory")
	address = event["queryStringParameters"]["address"]

	# logger.info("obtaining getRewardsDetails for address: {}".format(address))
	history = getRewardsDetails(conn, address)

	# logger.info("obtaining getRewardsHistorySummary for address: {}".format(address))
	historySummary = getRewardsHistorySummary(conn, address, '%%Y-%%m')

	# logger.info("obtaining getRewardsHistorySummary for address: {}".format(address))
	historySummaryAnnual = getRewardsHistorySummary(conn, address, '%%Y')

	coinStat = commonUtils.getCoinStat(conn, app)
	data = harmonyAddress.getDelegationDetails(conn, address)

	smartStake = harmonyAddress.isUsingSmartStake(data)

	auditUtils.audit(conn, app, event, "rewardsHistory", "get", startTime, None, address=address)
	return dbUtil.combineResults6("history", history, "data", data, "coinStat", coinStat,
			"historySummary", historySummary, "historySummaryAnnual", historySummaryAnnual,
			"smartStake", smartStake)


def getRewardsDetails(conn, address):
	sql = "select epochBlockTime as withdrawalTime, amount "
	sql += " from " + tables.hevent
	sql += " where address = %s and eventType=%s"
	# sql += " group by date(from_unixtime(epochBlockTime)) "
	sql += " order by 1 desc"
	# logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn, (address, hConstants.H_EVENT_COLLECT_REWARDS))
	return data


def getRewardsHistorySummary(conn, address, dateFormat):
	sql = "select DATE_FORMAT(from_unixtime(epochBlockTime), '" + dateFormat + "') as withdrawalTime, "
	sql += " sum(amount) as amount from " + tables.hevent
	sql += " where address = %s and eventType=%s"
	sql += " group by DATE_FORMAT(from_unixtime(epochBlockTime), '" + dateFormat + "') "
	sql += " order by 1 desc"

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn, (address, hConstants.H_EVENT_COLLECT_REWARDS))

