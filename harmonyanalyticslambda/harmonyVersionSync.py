import datetime
import logging

import auditUtils
import commonUtils
import dbUtil
import eventName
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def syncVersion(conn, app, data, startTime):
	logger.info("syncing harmony version data")

	logger.info("processing data: {}".format(data))
	keyVersions = data["keyVersions"]
	logger.info("processing valVersions: {}".format(keyVersions))

	updates = []
	for key in keyVersions:
		logger.info("processing val: {}".format(key))
		updates.append((key["version"], datetime.datetime.now(), key["blsKey"]))

	logger.info("processing updates: {}".format(updates))
	batchUpdateVersions(conn, updates)

	auditUtils.createEvent(conn, app, eventName.lastHarmonyVersionSync)
	logger.info("finished syncing versions")
	conn.commit()


def batchUpdateVersions(conn, updates):
	sql = "update " + tables.hblskey + " set "
	sql += " nodeVersion = %s, lastUpdated=%s "
	sql += " where blsKey = %s "

	logger.info("{0}: {1}".format(sql, len(updates)))
	conn.cursor().executemany(sql, updates)


def listNodeVersions(conn):
	sql = "select hp.hPoolId, name, blskey, "
	sql += "(case when nodeVersion is null then 'Unknown' else nodeVersion end) as nodeVersion "
	sql += "from " + tables.hblskey + " bk "
	sql += "inner join " + tables.hpool + " hp on bk.hPoolId=hp.hPoolId "
	sql += "where status='Elected' "

	logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn)


def listNodeVersionSummary(conn):
	sql = "select "
	sql += "(case when nodeVersion is null then 'Unknown' else nodeVersion end) "
	sql += " 	as nodeVersion, count(*) as total "
	sql += "from " + tables.hblskey + " bk "
	sql += "inner join " + tables.hpool + " hp on bk.hPoolId=hp.hPoolId "
	sql += "where status='Elected' "
	sql += "group by (case when nodeVersion is null then 'Unknown' else nodeVersion end) "
	sql += "order by 2 desc"

	logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn)


def listVersionStats(conn):
	startTime = commonUtils.getCurrentTime()

	nodeVersionSummary = listNodeVersionSummary(conn)
	commonUtils.logTimeDiff(startTime, "after nodeVersionSummary")

	nodeVersions = listNodeVersions(conn)
	commonUtils.logTimeDiff(startTime, "after nodeVersions")

	return dbUtil.combineResults2("nodeVersionSummary", nodeVersionSummary,
		"nodeVersions", nodeVersions)

