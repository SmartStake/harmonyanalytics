import logging

import constants
import dbUtil
import harmonyData
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
	address=None, value2=None, value3=None, value4=None, value5=None, value6=None):

	sql = "INSERT INTO " + tables.hhistory
	sql += "(epoch, dataType, poolId, keyObject, "
	sql += " address, value1, value2, value3, "
	sql += " value4, value5, value6) "
	sql += " VALUES (%s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s, %s, %s)"

	# logger.info(sql)
	args = (epoch, dataType, poolId, keyObject, address,
			value1, value2, value3, value4, value5, value6)

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

