import logging

import commonUtils
import dbUtil
import eventName
import hConstants
import harmonyData
import notificationUtils
import propUtils
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def listBlsKeySyncDetails(conn, app):
	sql, args = harmonyData.listHPoolsSql(None)
	validators = dbUtil.listResultsWithConn(sql, conn)
	keys = listBlsKeys(conn)
	# shards = listLatestShardDelay(conn)

	# return dbUtil.combineResults3("validators", validators, "keys", keys, "shards", shards)
	return dbUtil.combineResults2("validators", validators, "keys", keys)


def listBlsKeys(conn):
	sql = " select * "
	sql += " from " + tables.hblskey
	data = dbUtil.listResultsWithConn(sql, conn)

	return data

#list latest one record per shard
def listLatestShardDelay(conn):
	sql = " select * "
	sql += " from " + tables.hsharddelay
	sql += " order by syncTime desc limit 4 "
	# logger.info(sql)
	data = dbUtil.listResultsWithConn(sql, conn)

	return data


def listKeys(conn, app, event, hPoolId):
	# logger.info("in listKeys method")

	val = harmonyData.getHPoolById(conn, hPoolId)
	coinStat = commonUtils.getCoinStat(conn, app)

	epoch = coinStat["currentEpoch"]
	if "epoch" in event["queryStringParameters"]:
		epoch = int(event["queryStringParameters"]["epoch"])

	data = listLatestKeys(conn, hPoolId, epoch)
	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyBlsKeys)
	return dbUtil.combineResults5("val", val, "data", data, "epoch", epoch,
			"coinStat", coinStat, "lastUpdated", lastUpdated)


def listLatestKeys(conn, hPoolId, epoch):
	# logger.info("params are: {}, {}".format(hPoolId, epoch))
	sql = "select bk.shardId, bk.nodeVersion, kp.* from "
	sql += tables.hkeyperf + " kp "
	sql += " inner join " + tables.hblskey + " bk on bk.blskey=kp.blskey"
	sql += " inner join " + tables.hpool + " hp on hp.hpoolid=bk.hpoolid"
	sql += " where hp.hpoolid=%s and epochNumber=%s "
	sql += " and kp.syncTime = (select max(kp.syncTime) from "
	sql += " 	" + tables.hkeyperf + " kp"
	sql += " 	inner join " + tables.hblskey + " bk on bk.blskey=kp.blskey"
	sql += " 	where bk.hpoolid=%s and epochNumber=%s)"
	sql += " order by isBadPerf desc, keyPerfIndex "
	# logger.info(sql)

	data = dbUtil.listResultsWithConn(sql, conn, (hPoolId, epoch, hPoolId, epoch))
	return data


def listKeyDetails(conn, app, event):
	# logger.info("in listKeys method")

	blsKey = event["queryStringParameters"]["blsKey"]
	keyDetails = getKeyDetails(conn, blsKey)
	val = harmonyData.getHPoolById(conn, keyDetails["hPoolId"])

	epoch = int(event["queryStringParameters"]["epoch"])

	data = listKeyDataByEpoch(conn, blsKey, epoch)
	lastUpdated = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyBlsKeys)
	return dbUtil.combineResults4("val", val, "data", data, "keyDetails", keyDetails,
			"lastUpdated", lastUpdated)


def listKeyDataByEpoch(conn, blsKey, epoch):
	dateColumn = "date_format(from_unixtime(syncTime),'%%Y-%%m-%%d %%H:%%i')"

	sql = "select " + dateColumn + " as title, kp.* "
	sql += " from " + tables.hkeyperf + " kp "
	sql += " where blsKey = %s "
	sql += " and epochNumber=%s"
	sql += " order by syncTime "

	# logger.info(sql)
	data = dbUtil.listResultsWithConn(sql, conn, (blsKey, epoch))
	return data


def getKeyDetails(conn, blsKey):
	sql = "select * from " + tables.hblskey
	sql += " where blsKey = %s "

	return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, blsKey)


def listValKeys(conn):
	sql = "select blsKey, hPoolId from "
	sql += tables.hblskey

	return dbUtil.listResultsWithResponseWithConn(sql, conn)


def processKeyNodeVersionAlert(conn, app):
	effectiveEpoch = propUtils.getIntPropValue(conn, app, hConstants.VERSION_ALERT_EPOCH_PROP)
	startingEpoch = effectiveEpoch - hConstants.VERSION_ALERT_RANGE
	endingEpoch = effectiveEpoch + hConstants.VERSION_ALERT_RANGE

	currentCoinStat = commonUtils.getCoinStat(conn, app)
	currentEpoch = currentCoinStat["currentEpoch"]
	logger.info("effectiveEpoch: {}, startingEpoch: {}, endingEpoch: {}".format(effectiveEpoch, startingEpoch, endingEpoch))
	if startingEpoch <= currentEpoch <= endingEpoch:
		version = propUtils.getPropValue(conn, app, hConstants.VERSION_ALERT_MANDATORY_PROP)
		logger.info("processing version alert")
		generateNodeVersionAlert(conn, version, effectiveEpoch, currentEpoch)
	else:
		logger.info("skipping version alert")


def generateNodeVersionAlert(conn, version, effectiveEpoch, currentEpoch):
	validators = getValsWithLowerVersions(conn, version)

	# logger.info("validators with lower version are: {}".format(validators))
	if len(validators) == 0:
		return

	notifications = []
	for validator in validators:
		notification = (hConstants.NOTIFICATION_TYPE_BLS_KEY_ON_OLD_VERSION, None, validator["hPoolId"], currentEpoch,
				 effectiveEpoch, None, None, None,
				 version, validator["nodeVersion"], None)

		notifications.append(notification)

	notificationUtils.batchCreateNotificationsWithOtherData(conn, notifications)
	conn.commit()


def getValsWithLowerVersions(conn, version):
	sql = "select bk.hPoolId, min(nodeVersion) as nodeVersion "
	sql += "from " + tables.hblskey + " bk "
	sql += "inner join " + tables.hpool + " hp on bk.hPoolId=hp.hPoolId "
	sql += "where status='Elected' "
	sql += "and nodeVersion < %s "
	sql += "group by bk.hPoolId "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn, version)
