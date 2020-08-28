import datetime
import logging

import dbUtil
import restUtils
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    # logger.info("in update setting for attributes")
    # logger.info((chatId, attribute, value))

    sql = "update " + tables.tgsetting
    sql += " set " + attribute + "=%s, "
    sql += " lastUpdated=%s where chatId=%s and app=%s "

    # logger.info(sql)
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