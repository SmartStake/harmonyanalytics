import logging

import dbUtil
import tables
import utilities

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class CallRejectedException(Exception):
    pass


def performCheckAndGetConn(event, app, fnName):
    try:
        conn, key = doPerformCheckAndGetConn(event, app, fnName)
        return conn, key, None
    except CallRejectedException:
        return None, None, utilities.getAccessDeniedErrorResponse()


def doPerformCheckAndGetConn(event, app, fnName):
    if "queryStringParameters" in event and event["queryStringParameters"] is not None:
        if "accessKey" in event["queryStringParameters"]:
            key = event["queryStringParameters"]["accessKey"]
            conn = dbUtil.getConnection()
            checkAccessKey(conn, app, key, fnName)
            return conn, key

    logger.info("access key not found in request. call rejected.")
    #key not matched. rejecting
    raise CallRejectedException('403')


def checkAccessKey(conn, app, key, fnName):
    logger.info("checking Access Key for (app: {}, key: {}, fnName: {})".format(
        app, key, fnName))
    accessKey = getAccessKey(conn, app, key)

    if not accessKey:
        raise CallRejectedException('403')

    validateFunctionAndHits(conn, accessKey, fnName)

    #at this point, it is a valid call and hits have not exceeded
    #set audit entry or increment
    if accessKey["appAuditId"]:
        incrementHits(conn, accessKey, False)
    else:
        createHit(conn, accessKey)

    logger.info("access key checks passed")

def getAccessKey(conn, app, key):
    sql = "select ak.accessKeyId, ak.accessKey, ak.assignedTo, "
    sql += " ak.accessFn1, ak.accessFn2, ak.creationDate, ak.dailyLimit, "
    sql += " ak.app, ak.status, aa.appAuditId, aa.auditDate, "
    sql += " aa.hits, aa.deniedHits "
    sql += " from " + tables.accesskey + " ak "
    sql += " left join " + tables.appaudit + " aa "
    sql += "    on aa.accessKeyId=ak.accessKeyId and auditDate=curDate() "
    sql += " where ak.accessKey = %s "
    sql += " and app = %s and status='ACTIVE' "

    # logger.info(sql)
    accessKey = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (key, app))
    # logger.info(accessKey)
    # logger.info(accessKey["accessKeyId"])

    return accessKey


def validateFunctionAndHits(conn, accessKey, fnName):
    if accessKey["accessFn1"] != fnName and accessKey["accessFn2"] != fnName:
        logger.info("accessKey: {} is not allowed to call function: {}".format(
            accessKey["accessKey"], fnName))
        raise CallRejectedException('403')

    if accessKey["hits"] and accessKey["hits"] > accessKey["dailyLimit"]:
        incrementHits(conn, accessKey, True)
        raise CallRejectedException('403')


def incrementHits(conn, accessKey, denied):
    sql = " update " + tables.appaudit
    sql += " set hits = hits + 1, lastUpdated = current_timestamp "
    if denied:
        sql += " , deniedHits = deniedHits + 1 "
    sql += " where appAuditId = %s "

    conn.cursor().execute(sql, (accessKey["appAuditId"]))
    conn.commit()


def createHit(conn, accessKey):
    # logger.info("in create hit: {}".format(accessKey))
    sql = " insert into " + tables.appaudit
    sql += " (auditDate, accessKeyId, hits) "
    sql += " values (curDate(), %s, 1) "

    # logger.info(sql)
    conn.cursor().execute(sql, (accessKey["accessKeyId"]))
    conn.commit()

