import logging

import constants
from securityUtils import CallRejectedException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getIntParam(event, param):
    value = event["queryStringParameters"][param]
    if isinstance(value, str):
        value = int(value)

    return value

def getEscapedPoolId(event):
    param = getIntParam(event, "poolId")
    return str(param)


def getOptionalIntParam(event, param):
    value = None

    if param in event["queryStringParameters"]:
        value = event["queryStringParameters"][param]
        if isinstance(value, str):
            # logger.info(param + " - value is string")
            value = int(value)

    return value

def getOptionalEscapedPoolId(event):
    param = getOptionalIntParam(event, "poolId")

    if param:
        return str(param)

    return param


def getCoin(event):
    return getParam(event, "coin")


def getParam(event, paramName):
    if "queryStringParameters" in event and paramName in event["queryStringParameters"]:
        value = event["queryStringParameters"][paramName]
        return value

    return "None"

def getApp(event):
    app = getParam(event, "app")
    if app is None:
        app = getParam(event, "App")

    if app not in constants.APPS:
        raise CallRejectedException("invalid app")

    return app

