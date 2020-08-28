import datetime
import logging
import time

import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def audit(conn, app, event, url, method, startTime, poolId=0, **kwargs):
    # logger.info("in audit")
    sourceIp = None
    if 'requestContext' in event and 'identity' in event['requestContext'] and 'sourceIp' in event['requestContext']['identity']:
        sourceIp = event['requestContext']['identity']['sourceIp']

    urlParams = ""
    for key in kwargs.keys():
        if urlParams == "":
            urlParams = "?"
        else:
            urlParams = "&"
        urlParams = key + "=" + kwargs[key]


    sql = "INSERT INTO " + tables.auditlog + "(ipAddress, url, app, "
    sql += " method, poolId, urlParams, responseTime) "
    sql += " VALUES (%s, %s, %s, %s, %s, %s, %s)"

    responseTime = int((datetime.datetime.now() - startTime).total_seconds() * 1000)
    logger.info("startTime - %s, end time: %s, responseTime: %s" % (
        startTime, datetime.datetime.now(), responseTime))

    conn.cursor().execute(sql, (sourceIp, url, app, method, str(poolId),
        urlParams, responseTime))
    conn.commit()
    # logger.info("end of audit")

def auditBot(conn, chatId, url, startTime, urlParams=None):
    sql = "INSERT INTO " + tables.auditlog + "(ipAddress, url, app, "
    sql += " method, poolId, urlParams, responseTime) "
    sql += " VALUES (%s, %s, %s, %s, %s, %s, %s)"

    responseTime = int((datetime.datetime.now() - startTime).total_seconds() * 1000)
    logger.info("startTime - %s, end time: %s, responseTime: %s" % (
        startTime, datetime.datetime.now(), responseTime))

    conn.cursor().execute(sql, (chatId, url, "AIONBot", "GET", None,
        urlParams, responseTime))
    conn.commit()
    # logger.info("end of audit")


def createEvent(conn, app, eventName, description=None):
    sql = "INSERT INTO " + tables.eventlog
    sql += " (eventName, app, eventTime, description) "
    sql += " VALUES (%s, %s, %s, %s)"

    conn.cursor().execute(sql, (eventName, app, int(time.time()), description))
    conn.commit()
    # logger.info("end of audit")
