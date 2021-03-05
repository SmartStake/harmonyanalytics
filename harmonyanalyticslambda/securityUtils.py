import json
import logging
import time

import dbUtil
import paramUtils
import utilities
import rds_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# first key is service key
validKeys = [rds_config.SECURITY_KEY_1, rds_config.SECURITY_KEY_2]
tokenGrace = 24 * 60 * 60


class CallRejectedException(Exception):
    pass


def performSecurityCheckAndGetDetails(event):
    try:
        conn = performSecurityCheckAndGetConn(event)
        app = paramUtils.getApp(event)

        return conn, app, None
    except CallRejectedException:
        return None, None, utilities.getAccessDeniedErrorResponse()


def performSecurityCheckAndGetDetailsInclPool(event):
    try:
        conn = performSecurityCheckAndGetConn(event)
        app = paramUtils.getApp(event)
        poolId = utilities.getEscapedPoolId(event)

        return conn, app, poolId, None
    except CallRejectedException:
        return None, None, None, utilities.getAccessDeniedErrorResponse()


def performSecurityCheckAndGetConn(event):
    if "queryStringParameters" in event and event["queryStringParameters"] is not None:
        if "key" in event["queryStringParameters"]:
            key = event["queryStringParameters"]["key"]
            for v in validKeys:
                if v == key:
                    token = event["queryStringParameters"]["token"]
                    validateToken(event, token)
                    return dbUtil.getConnection()

    #not found in url, lets check body
    if "body" in event and event["body"] is not None:
        body = json.loads(event["body"])
        if "key" in body:
            key = body["key"]
            for v in validKeys:
                if v == key:
                    token = body["token"]
                    validateToken(event, token)
                    return dbUtil.getConnection()

    logger.info("valid key not found in body. call rejected.")

    #key not matched. rejecting
    raise CallRejectedException('call rejected')


def validateToken(event, token):
    epochTime = int(time.time())
    minTime = epochTime - tokenGrace
    if int(token) < minTime:
        logger.info("validateToken - rejecting call due to token expiry")
        raise CallRejectedException('bad call')

    maxTime = epochTime + (5 * tokenGrace)
    if int(token) > maxTime:
        logger.info("validateToken - rejecting call due to token being far in future")
        raise CallRejectedException('bad call')


