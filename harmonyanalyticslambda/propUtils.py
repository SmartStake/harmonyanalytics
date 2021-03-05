import logging

import commonUtils
import dbUtil
import tables
from dbUtil import getSingleRecordNoJsonWithConn

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getPropSql():
    sql = "select * "
    sql += " from " + tables.propertytable
    sql += " where app = %s "
    sql += " and name = %s "
    sql += " limit 1"

    # logger.info(sql)
    return sql


def getProp(conn, app, propName):
    return getSingleRecordNoJsonWithConn(getPropSql(), conn, (app, propName))


def getAllPropsAsMap(conn, app):
    sql = "select * "
    sql += " from " + tables.propertytable
    sql += " where app = %s "

    list = dbUtil.listResultsWithConn(sql, conn, app)

    return commonUtils.getMapWithValueFromList(list, "name", "value")


def getPropValue(conn, app, propName):
    return getProp(conn, app, propName)["value"]


def getIntPropValue(conn, app, propName):
    return int(getProp(conn, app, propName)["value"])


def setPropValue(conn, app, propName, value):
    sql = "update " + tables.propertytable + " set value=%s  "
    sql += " where name=%s and app=%s "
    conn.cursor().execute(sql, (str(value), propName, app))
    conn.commit()
    
def isTrue(conn, app, propName):
    value = getPropValue(conn, app, propName)

    if value == "True":
        return True

    return False


