import datetime
import logging

import accessKeyUtils
import auditUtils
import constants
import dbUtil
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

fnName = "validators"

def lambda_handler(event, context):
	startTime = datetime.datetime.now()

	conn, accessKey, error = accessKeyUtils.performCheckAndGetConn(event, constants.app, fnName)
	if error:
		logger.info(error)
		return error

	status = None
	if "status" in event["queryStringParameters"]:
		status = event["queryStringParameters"]["status"]
	sql, args = listHPoolsSql(status)
	logger.info(args)
	data = dbUtil.listResultsWithResponseWithConn(sql, conn, args)
	logger.info(data)

	auditUtils.auditSimple(conn, constants.app, startTime, fnName, accessKey)
	conn.close()
	return data


def listHPoolsSql(status, orderBy="rand()"):
	args = {}
	# if status and status != constants.ALL_ELIGIBLE and status != constants.ALL_STATUS:

	sql = " select  "
	sql += " name, address, details, blsKeyCount, website, "
	sql += " lifetimeToSign, lifetimeSigned, "
	sql += " round(lifetimeSigned * 100/lifetimeToSign, 2) as lifetimeSignPer, "
	sql += " currentEpochToSign, currentEpochSigned, currentEpochSignPer, "
	sql += " avgToSign, avgSigned, avgSignPer, "
	sql += " uniqueDelegates, isPva, isEverElected, "
	sql += " fee, maxFee, feeChangeRate, creationBlock, "
	sql += " selfStake, totalStaked, lifetimeApr,  "
	sql += " currentApr, currentNetApr, currentEri, "
	sql += " avgApr, avgNetApr, avgEri "
	sql += " prevEpochApr, prevEpochNetApr, prevEpochEri, status "
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
	logger.info(sql)

	return sql, args




