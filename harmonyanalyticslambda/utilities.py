import datetime
import decimal
import json
import logging
from json import encoder

import paramUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

encoder.FLOAT_REPR = lambda o: format(o, '.2f')


def default(o):
    # from pytz import timezone
    if type(o) is datetime.date or type(o) is datetime.datetime:
        return o.isoformat()
    if isinstance(o, float):
        return round(o, 8)
    if type(o) is decimal.Decimal:
        return str(o)


def jsondumps(o):
    # return json.dumps(o)
    return json.dumps(o, default=default)


def getResponse(output):
    return getResponseWithStatus(output, "200")


def getAccessDeniedErrorResponse():
    data = {"errors": "DENIED"}

    return getResponseWithStatus(jsondumps(data), "200") 


def getAccessErrorResponse(message):
    return getResponseWithStatus({"error": message}, "403")

def getResponseWithStatus(output, status):
    response = {
        "statusCode": status,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true'
        },
        "body": output,
        # "body": jsondumps(rows),
        "isBase64Encoded": "false"
    }

    # logger.info("response is: " + jsondumps(response))
    return response


def getErrorResponse(errors):
    json_output = {
        "errors": errors
    }

    return getResponseWithStatus(json_output, "500")

def getIntParam(event, param):
    return paramUtils.getIntParam(event, param)

def getEscapedPoolId(event):
    return paramUtils.getEscapedPoolId(event)

def getSuccessResponse():
    return getResponse(jsondumps({"result": "successful"}))
