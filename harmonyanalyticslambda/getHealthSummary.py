import logging

import auditUtils
import dbUtil
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def listHealthCheckData(conn, app, event, startTime):
    # logger.info("obtaining health check data from database - " + app)
    sql = " select healthid, nodeName, symbol, UNIX_TIMESTAMP(checkupTime) as cTime, "
    sql += " DATE_FORMAT(checkupTime,'%%Y-%%m-%%d %%H:%%i:%%s') as checkupTime, "
    sql += " networkBlockHeight, nodeBlockHeight, heightGap, shardId, epochTimestamp, "
    sql += " round(time_to_sec((TIMEDIFF(NOW(), checkupTime))) / 60,0) as elapsedTime "
    sql += " from " + tables.nodehealth + " w "
    sql += " where symbol = %s "
    sql += " order by cTime desc"
    sql += " limit 50"
    # logger.info(sql)

    activities = dbUtil.listResultsWithConn(sql, conn, app)
    pool = None

    auditUtils.audit(conn, app, event, "listHealthCheckData", "get", startTime, None)
    return dbUtil.combineResults2("pool", pool, "activities", activities)
