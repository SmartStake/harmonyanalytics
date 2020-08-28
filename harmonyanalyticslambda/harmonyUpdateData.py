import datetime
import json
import logging

import aliasUtils
import auditUtils
import harmonyDelegationSync
import harmonyEvents
import harmonyValSync
import saveHealthCheck
import securityUtils
import utilities

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("in update data")


def lambda_handler(event, context):
	logger.info("in updateData for harmony")

	startTime = datetime.datetime.now()
	conn, app, error = securityUtils.performSecurityCheckAndGetDetails(event)
	if error:
		return error

	body = json.loads(event["body"])
	# logger.info("body: {}".format(body))

	data = body["data"]
	dataType = data["type"]
	logger.info("dataType: {}".format(dataType))

	if dataType == "valSync":
		harmonyValSync.syncValidators(conn, app, data, event)
	elif dataType == "addressSync":
		harmonyDelegationSync.syncAddresses(conn, app, data, event)
	elif dataType == "delegateSync":
		harmonyDelegationSync.syncDelegates(conn, app, data, event)
	elif dataType == "eventsSync":
		harmonyEvents.syncEvents(conn, app, data, event)
	elif dataType == "eventsSync":
		saveHealthCheck.createHealthCheck(app, body, conn)
		auditUtils.audit(conn, app, event, "saveHealthCheck", "service", startTime)
	elif dataType == "saveAlias":
		# data = body["data"]
		result = aliasUtils.saveAlias(conn, app, event, data, startTime)
		if result:
			conn.close()
			return result
	elif dataType == "clearAlias":
		# data = body["data"]
		aliasUtils.clearAlias(conn, app, data, startTime)
	else:
		logger.info("dataType didnt match supported datatypes: {}".format(dataType))

	conn.close()
	return utilities.getSuccessResponse()


def updateData(conn, app, body, event):
	logger.info("in updateData for harmony")

	startTime = datetime.datetime.now()
	dataType = body["type"]

	if dataType == "valSync":
		harmonyValSync.syncValidators(conn, app, body, event)
	elif dataType == "addressSync":
		harmonyDelegationSync.syncAddresses(conn, app, body, event)
	elif dataType == "delegateSync":
		harmonyDelegationSync.syncDelegates(conn, app, body, event)


