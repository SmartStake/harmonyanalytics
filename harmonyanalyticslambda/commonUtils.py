import datetime
import json
import logging
import time
from binascii import unhexlify

from requests import Session

import dbUtil
import rds_config
import tables
from dbUtil import getSingleRecordNoJsonWithConn

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getEventSql():
	sql = "select eventTime, "
	sql += " description, "
	sql += " (UNIX_TIMESTAMP() - eventTime) as lastUpdated "
	sql += " from " + tables.eventlog
	sql += " where eventName = %s"
	sql += " order by eventTime desc"
	sql += " limit 1"

	# logger.info(sql)
	return sql


def getEventDetails(conn, eventName):
	return getSingleRecordNoJsonWithConn(getEventSql(), conn, eventName)


def getEventLastUpdated(conn, eventName):
	return getEventDetails(conn, eventName)["lastUpdated"]


def getEventDescription(conn, eventName):
	eventDetails = getEventDetails(conn, eventName)
	# logger.info("eventName: {}, details: {}".format(eventName, eventDetails))
	return eventDetails["description"]


def getEventDescriptionInt(conn, eventName):
	desc = getEventDescription(conn, eventName)
	# if none that means record is missing and let it fail here
	return int(desc)


def getNodeHealth(conn, poolId):
	oldestTime = (datetime.datetime.now() - datetime.timedelta(days=rds_config.pool_max_days))
	sql = " select min(heightGap) as gap, max(lastUpdated) as checkupTime "
	sql += " from (select nh.*, "
	sql += " UNIX_TIMESTAMP(lastUpdated) as lw "
	sql += " from " + tables.nodehealth + " nh "
	sql += " where poolId= " + str(poolId)
	sql += " and lastUpdated > '" + str(oldestTime) + "'"
	sql += " order by lw desc limit 2) as nh "
	# logger.info(sql)

	return getSingleRecordNoJsonWithConn(sql, conn)


def isAlreadyExisting(conn, tableName, columnName1, key1):
	return isAlreadyExistingTwoKeys(conn, tableName, columnName1, key1, None, None)

def isAlreadyExistingTwoKeys(conn, tableName, columnName1, key1, columnName2=None, key2=None):
	sql = "select count(*) as recordCount from " + tableName
	sql += " where " + columnName1 + " = %s"

	if columnName2 is not None:
		sql += " and " + columnName2 + " = %s"
		record = getSingleRecordNoJsonWithConn(sql, conn, (key1, key2))
	else:
		record = getSingleRecordNoJsonWithConn(sql, conn, key1)
	# logger.info("record is: " + str(record))
	count = record["recordCount"]

	if count > 0 :
		return True

	return False

# does not work with optional inputs - to be fixed
def isAlreadyExistingThreeKeys(conn, tableName, columnName1, key1, columnName2=None, key2=None,
							   columnName3=None, key3=None):
	sql = "select count(*) as recordCount from " + tableName
	sql += " where " + columnName1 + " = %s"
	sql += " and " + columnName2 + " = %s"
	sql += " and " + columnName3 + " = %s"

	record = getSingleRecordNoJsonWithConn(sql, conn, (key1, key2, key3))
	# logger.info("record is: " + str(record))
	count = record["recordCount"]

	if count > 0 :
		return True

	return False


def getNotification(conn, app, poolId=None):
	sql = "select message, endDate "
	sql += " from " + tables.notification
	sql += " where startDate < NOW() "
	sql += " and endDate > NOW() "
	sql += " and app = %s "

	args = ()
	if not poolId:
		sql += " and poolId is null "
		args = (app)
	else:
		sql += " and poolId =%s "
		args = (app, poolId)
	sql += " limit 1"
	# logger.info(sql)
	# logger.info(args)

	return getSingleRecordNoJsonWithConn(sql, conn, args)


def getCoinStat(conn, symbol):
	sql = getCoinStatSql()
	logger.info("getting coinstat: {}, data: {}".format(sql, symbol))
	return getSingleRecordNoJsonWithConn(sql, conn, symbol)


def getCoinStatSql():
	sql = "select cs.*, (UNIX_TIMESTAMP() - cs.epochTimestamp) as lastUpdatedGap "
	sql += " from " + tables.coinstat + " cs "
	sql += " where cs.symbol = %s"
	# logger.info(sql)

	return sql


def calcPercent(value1, value2):
	if value2 is None or value2 == 0:
		return None
	if value1 is None or value1 == 0:
		return None

	return value1 * 100 / value2

def divide(value1, value2):
	if value2 is None or value2 == 0:
		return None
	if value1 is None or value1 == 0:
		return None

	return value1 / value2

def divideDToF(value1, value2):
	# logger.info("value1 : {}, value2: {}".format(value1, value2))

	if value2 is None or value2 == 0:
		return 0
	if value1 is None or value1 == 0:
		return 0

	return float(value1) / float(value2)

def timeTaken(startTime):
	return "Time taken: " + str(int((datetime.datetime.now() - startTime).total_seconds() * 1000))


def makeHex(address):
	a = address.startswith("0x")
	if a:
		return address

	return "0x" + address

def removeHexPrefix(address):
	a = address.startswith("0x")
	if a:
		return address[2:]

	return address

def textFromHex(hexInput):
	#"""base64_id can be found in entity.json in the `id` field"""
	# return b2a_base64(unhexlify(hexInput)).decode("utf-8")
	return unhexlify(removeHexPrefix(hexInput)).decode("utf-8")

def divideByTenPower(value, power):
	if value is None:
		return value

	return int(value) / (10 ** power)

def divideByTenPower18(value):
	return divideByTenPower(value, 18)

def divideByTenPower9(value):
	return divideByTenPower(value, 9)


def getMapFromList(listData, keyAttribute):
	mapObj = {}

	# logger.info(list)
	for item in listData:
		# logger.info(item)
		# logger.info("keyAttribute")
		# logger.info(keyAttribute)
		keyValue = item[keyAttribute]
		# logger.info("keyValue")
		# logger.info(keyValue)
		mapObj[keyValue] = item

	# logger.info("map is:")
	# logger.info(mapObj)
	return mapObj


def getMapWithValueFromList(listData, keyAttribute, valueAttribute):
	mapObj = {}

	for item in listData:
		# logger.info(item)
		# logger.info("keyAttribute")
		# logger.info(keyAttribute)
		keyValue = item[keyAttribute]
		# logger.info("keyValue")
		# logger.info(keyValue)
		mapObj[keyValue] = item[valueAttribute]

	# logger.info("map is:")
	# logger.info(mapObj)
	return mapObj


def getValueWithDefault(data, attribute, defaultValue):
	value = data[attribute]
	if value is None:
		value = defaultValue

	return value


def updateSyncStatus(conn, app, syncType, blockVal, epochVal=None):
	sql = "update " + tables.syncstatus
	sql += " set lastUpdated=%s, syncedTillBlock = %s, syncedTillEpoch=%s "
	sql += " where app=%s and syncType=%s "
	# logger.info(sql)
	conn.cursor().execute(sql, (datetime.datetime.now(),
		blockVal, epochVal, app, syncType))


def updateCoinStatActiveAccounts(conn, activeAccounts, symbol):

	sql = "update " + tables.coinstat
	sql += " set activeAccounts=%s "
	sql += " where symbol=%s"
	# logger.info(sql)
	conn.cursor().execute(sql, (activeAccounts, symbol))


def getStatusSummaryMap(statusList, statusMap):
	total = 0

	for item in statusList:
		status = item["status"]
		statusMap[status] = item["total"]
		total += item["total"]

	statusMap["Total"] = total

	return statusMap


def getSyncStatus(conn, app, syncType):
	sql = " select * from " + tables.syncstatus
	sql += " where app = %s "
	sql += " and syncType = %s "

	# logger.info(sql)

	return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (app, syncType))

def getCurrentTime():
	return int(round(time.time() * 1000))

def logTimeDiff(startTime, message):
	diff = int(round(time.time() * 1000)) - startTime
	logger.info(message + ", time spent so far: {}".format(diff))


def getMapFromList2Keys(data, keyAttribute1, keyAttribute2):
	mapObj = {}

	for item in data:
		keyValue = str(item[keyAttribute1]) + "-" + str(item[keyAttribute2])
		mapObj[keyValue] = item

	return mapObj


def getDataByUrl(url):
	return getDataFromGet(Session(), url)


def getDataFromGet(session, url):
	# logger.debug("calling url: " + url)
	headers = {'accept': 'application/object'}
	response = session.get(url, headers=headers)

	# logger.info(response)
	if response.status_code == 200:
		data = json.loads(response.content.decode('utf-8'))
		# logger.info(data)
		return data

	logger.debug(response)
	logger.debug("unexpected response")
	return None


def combineTwoListsToSet(chats1, chats2):
	if chats1 is None or len(chats1) == 0:
		return chats2

	if chats2 is None or len(chats2) == 0:
		return chats1

	chats = set(chats1)
	for chat in chats2:
		chats.add(chat)

	return chats