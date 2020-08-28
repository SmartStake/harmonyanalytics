import datetime
import json
import logging
import time

import auditUtils
import constants
import securityUtils
import tables
import utilities

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    startTime = datetime.datetime.now()
    conn, app, error = securityUtils.performSecurityCheckAndGetDetails(event)
    if error:
        return error

    logger.info(app)
    body = json.loads(event["body"])

    createHealthCheck(app, body, conn)

    conn.commit()

    # logger.info("record created/modified")

    auditUtils.audit(conn, app, event, "saveHealthCheck", "service", startTime)
    conn.close()
    return utilities.getSuccessResponse()

def createHealthCheck(app, body, conn):
    # logger.info("creating health check for node  - " + body["nodeName"])
    # data_json = {"nodeName": node_name, "symbol": "AION", "checkupTime": datetime.now(), "networkBlockHeight": block_height, "nodeBlockHeight": node_height, "heightGap": block_diff, "lastBlockValidated": 120}

    # if "wishId" in body["wish"] and body["wish"]["wishId"] != "" and body["wish"]["wishId"] != "0":
    # logger.info("in create sql preparation")

    # dateVal = dateutil.parser.parse(body["checkupTime"])
    shardId = None
    if app == constants.HARMONY:
        shardId = body["shardId"]

    sql = "INSERT INTO " + tables.nodehealth + "(nodeName, symbol, checkupTime,  "
    sql += "networkBlockHeight, nodeBlockHeight, poolId, heightGap, shardId, epochTimestamp) "
    sql += "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    # logger.info("sql is: '" + sql + "'")
    conn.cursor().execute(sql, (body["nodeName"], body["symbol"], datetime.datetime.now(),
        body["networkBlockHeight"], body["nodeBlockHeight"], body["poolId"], body["heightGap"],
        shardId, int(time.time())))
