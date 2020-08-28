import logging

import pymysql

import rds_config
from utilities import jsondumps, getResponse, getResponseWithStatus

#rds settings
rds_host  = rds_config.db_endpoint
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getConnection():
    try:
        conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5,
                               charset='utf8mb4', use_unicode=True)
    except BaseException as error:
        logger.error(error)
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        raise error

    # logger.info("SUCCESS: Connection to RDS mysql instance succeeded")

    return conn

def query_db(query, args=(), one=False):
    conn = getConnection()
    result = query_db_with_conn(conn, query, args, one)
    return result

def query_db_with_conn(conn, query, args=(), one=False):
    cur = conn.cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    # cur.connection.close()
    return (r[0] if r else None) if one else r

def query_db_once(query, args=(), one=True):
    conn = getConnection()
    result = query_db_once_with_conn(conn, query, args, one)
    return result

def query_db_once_with_conn(conn, query, args=(), one=True):
    cur = conn.cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    return (r[0] if r else None) if one else r


def listResultsWithResponseWithConn(sql, conn, args=(), response=True):
    # logger.info("sql is: " + sql)
    my_query = query_db_with_conn(conn, sql, args)

    json_output = jsondumps(my_query)

    return getResponse(json_output)

def listResultsWithResponse(sql):
    # logger.info("sql is: " + sql)
    my_query = query_db(sql)

    json_output = jsondumps(my_query)

    return getResponse(json_output)

def listResultsWithConn(sql, conn, args=()):
    # logger.info("sql is: " + sql)
    my_query = query_db_with_conn(conn, sql, args)
    return my_query

def getSingleRecord(sql, args=()):
    # logger.info("sql is: " + sql)
    my_query = query_db_once(sql, args)
    json_output = jsondumps(my_query)
    # logger.info("record is: " + json_output)

    return json_output

def getSingleRecordWithConn(sql, conn, args=()):
    # logger.info("sql is: " + sql)
    my_query = query_db_once_with_conn(conn, sql, args)
    json_output = jsondumps(my_query)
    # logger.info("record is: " + json_output)

    return json_output

def getSingleRecordNoJsonWithConn(sql, conn, args=()):
    # logger.info("sql is: " + sql)
    my_query = query_db_once_with_conn(conn, sql, args)
    # json_output = jsondumps(my_query)
    # logger.info("record is: " + json_output)
    # logger.info("record is: " + str(my_query))

    return my_query


def getSingleRecordResponse(sql, args=()):
    return getResponse(getSingleRecord(sql, args))


def getSingleRecordResponseWithConn(sql, conn, args=()):
    return getResponse(getSingleRecordWithConn(sql, conn, args))


def combineResults2(key1, value1, key2, value2):

    json_output = {key1: value1, key2: value2}
    resp = getResponse(jsondumps(json_output))

    # logger.info(resp)
    return resp


def combineResults3(key1, value1, key2, value2, key3, value3):
    json_output = {key1: value1, key2: value2, key3: value3}
    return getResponse(jsondumps(json_output))


def combineResults4(key1, value1, key2, value2, key3, value3, key4, value4):
    json_output = {key1: value1, key2: value2, key3: value3, key4: value4}
    return getResponse(jsondumps(json_output))

def combineResults5(key1, value1, key2, value2, key3, value3, key4, value4, key5, value5):
    json_output = {key1: value1, key2: value2, key3: value3, key4: value4, key5: value5}
    return getResponse(jsondumps(json_output))

def combineResults6(key1, value1, key2, value2, key3, value3, 
        key4, value4, key5, value5, key6, value6):
    json_output = {key1: value1, key2: value2, key3: value3, 
        key4: value4, key5: value5, key6: value6}
    return getResponse(jsondumps(json_output))

def combineResults7(key1, value1, key2, value2, key3, value3, 
        key4, value4, key5, value5, key6, value6, key7, value7):
    json_output = {key1: value1, key2: value2, key3: value3, 
        key4: value4, key5: value5, key6: value6, key7: value7}
    return getResponse(jsondumps(json_output))


def combineResults8(key1, value1, key2, value2, key3, value3,
        key4, value4, key5, value5, key6, value6, key7, value7, key8, value8):
    json_output = {key1: value1, key2: value2, key3: value3,
        key4: value4, key5: value5, key6: value6,
        key7: value7, key8: value8}

    return getResponse(jsondumps(json_output))


def getRedirectResponse(url, resp={}):
    return getResponse({})

def getErrorResponse(resp={}):
    json_output = jsondumps(resp)

    return getResponseWithStatus(json_output, "500")

