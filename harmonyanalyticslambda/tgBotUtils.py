import datetime
import logging
import requests

import auditUtils
import constants
import dbUtil
import rds_config
import restUtils
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SUCCESS_RESPONSE = {"statusCode": 200}

def prepUserSettings(conn, chatId, userId, app):
    setting = getUserSettings(conn, chatId, app)

    # logger.info(setting)
    if setting is None:
        # logger.info("creating setting")
        createSetting(conn, chatId, userId, app)
        setting = getUserSettings(conn, chatId, app)

    return setting

def getUserSettings(conn, chatId, app):
    sql = "select * "
    sql += " from " + tables.tgsetting
    sql += " where chatId = %s and app=%s "
    sql += " limit 1"

    # logger.info(sql)
    setting = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (chatId, app))
    # logger.info(setting)

    return setting


def createSetting(conn, chatId, userId, app):
    sql = "insert into " + tables.tgsetting
    sql += " (chatId, userId, app, lastUpdated) "
    sql += " values (%s, %s, %s, %s) "

    conn.cursor().execute(sql, (chatId, userId, app, datetime.datetime.now()))
    conn.commit()


def reset(conn, chatId, app):
    # conn = dbUtil.getConnection()

    sql = "update " + tables.tgsetting
    sql += " set address=null, favPools=null, addressAlias=null, "
    sql += " lastUpdated=%s where chatId=%s and app=%s "

    conn.cursor().execute(sql, (datetime.datetime.now(), chatId, app))
    conn.commit()
    # conn.close()


def updateSetting(conn, chatId, attribute, value, app):
    logger.info("in update setting for attributes")
    logger.info((chatId, attribute, value))

    sql = "update " + tables.tgsetting
    sql += " set " + attribute + "=%s, "
    sql += " lastUpdated=%s where chatId=%s and app=%s "

    logger.info(sql)
    params = (value, datetime.datetime.now(), chatId, app)
    # logger.info(params)

    conn.cursor().execute(sql, params)
    conn.commit()


def getParam(message, key, error):
    msg = message.strip()

    if not message.startswith(key):
        return error

    poolMsg = message[len(key):]

    # logger.info(poolMsg)

    return poolMsg.strip()


def getStakingNetworkInfo():
    url = "https://hmny-t.co/networks/mainnet/staking_network_info"
    return restUtils.callRestJson(url)


def getBidRanks(current):
    response = getStakingNetworkInfo()
    # logger.info(response)
    if current:
        table = response["table"]
        return table
    else:
        table = response["live_table"]
        return table


def getValByAddress(validators, address):
    # logger.info("in getValByAddress: address: {})".format(address))
    for val in validators:
        if val["address"] == address:
            return val

    return None


def validateAndGetText(chatId, message, startTime):
    if "text" not in message:
        return None, missingTextError(chatId, message, startTime)

    textCmd = str(message["text"])
    # if not textCmd.startswith("/"):
    #     return None, SUCCESS_RESPONSE

    if "@" in textCmd:
        textCmd = textCmd.replace(constants.TG_BOT_NAME_1, "")
        textCmd = textCmd.replace(constants.TG_BOT_NAME_2, "")

    return textCmd, None


def missingTextError(chatId, message, startTime):
    logger.info("processing missingTextError for message: ")
    logger.info(message)
    conn = dbUtil.getConnection()
    auditUtils.auditBot(conn, chatId, "Missing Text", startTime)
    conn.close()

    response = "The bot appears to have hit a bug. Please contact the bot operator @bigb4ever \n"
    respData = {"text": response.encode("utf8"), "chat_id": chatId}
    url = rds_config.TG_BASE_URL + "/sendMessage?parse_mode=html"
    requests.post(url, respData)

    return SUCCESS_RESPONSE


def getAllAddressesForTxAlert(conn, app):
    sql = "select address from " + tables.tgsetting
    sql += " where app = %s and "
    sql += " address is not null and notifyAddress='True'"

    addresses = dbUtil.listResultsWithConn(sql, conn, app)

    uniqueAddresses = set()
    for addressDetails in addresses:
        logger.info("processing address: {}".format(addressDetails))
        address = addressDetails["address"]
        addressList = address.split(",")
        for value in addressList:
            uniqueAddresses.add(value)
        logger.info("after adding list ({}), unique addresses are: {}".format(addressList, uniqueAddresses))

    logger.info("list of unique addresses is: {}".format(uniqueAddresses))
    return uniqueAddresses
