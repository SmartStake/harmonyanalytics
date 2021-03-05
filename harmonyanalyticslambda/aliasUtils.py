import logging

import auditUtils
import commonUtils
import dbUtil
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def saveAlias(conn, app, event, data, startTime):
    address = data["alias"]["address"]
    # addressList = addresses.split(",")
    alias = data["alias"]["alias"]
    # logger.info("creating alias")
    resp = createAlias(conn, alias, address, app)
    if resp is not None:
        return resp

    auditUtils.audit(conn, app, event, "saveAlias", "post", startTime, None, alias=alias)


def clearAlias(conn, app, data, startTime):
    alias = data["alias"]
    aliasList = alias.split(",")
    # logger.info("clearing alias")

    for alias in aliasList:
        sql = "Delete from " + tables.addressalias
        sql += " where alias = %s and app=%s"

        # logger.info("sql is: '" + sql + "'")
        conn.cursor().execute(sql, (alias, app))

    conn.commit()


def createAlias(conn, alias, address, app):
    if commonUtils.isAlreadyExistingTwoKeys(conn, tables.addressalias, "alias", alias, "app", app):
        # logger.info(alias + " is existing. Raising error")
        # raise Exception (alias + " - alias is already in use. please enter a new alias name.")
        response = alias + " - alias is already in use. please enter a new alias name."
        return dbUtil.getResponse(dbUtil.jsondumps({"result": response}))

    createAddressAlias(conn, address, alias, app)

    conn.commit()


def createAddressAlias(conn, address, alias, app):
    sql = "INSERT INTO " + tables.addressalias + "(address, alias, app) "
    sql += "VALUES (%s, %s, %s)"

    # logger.info("sql is: '" + sql + "'")
    conn.cursor().execute(sql, (address, alias, app))


def getAddressFromAlias(conn, app, alias):
    sql = " select address from " + tables.addressalias
    sql += " where app = %s and alias = %s "
    # logger.info(sql)

    args = (app, alias)
    # logger.info(args)

    data = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, args)
    # logger.info(data)

    return data

