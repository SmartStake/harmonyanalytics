import datetime
import logging

import auditUtils
import commonUtils
import dbUtil
import eventName
import hConstants
import hTgOtherNotification
import notificationUtils
import securityUtils
import tables
import tgConstants
import tgNotificationPushUtils
import utilities

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
	logger.info("in updateData for harmony")

	startTime = datetime.datetime.now()
	conn, app, error = securityUtils.performSecurityCheckAndGetDetails(event)
	if error:
		return error

	# body = json.loads(event["body"])
	# logger.info("body: {}".format(body))
	sendAllNotifications(conn)

	auditUtils.createEvent(conn, app, eventName.syncHarmonyNotifications)
	auditUtils.audit(conn, app, event, eventName.syncHarmonyNotifications, "service", startTime)

	# harmonyBlsKeys.processKeyNodeVersionAlert(conn, app)
	conn.close()
	return utilities.getSuccessResponse()


def sendAllNotifications(conn):
	logger.info("in sendNotifications")

	recipients = notificationUtils.getNotificationRecipients(conn)
	validators = listValidators(conn)
	sendEventNotifications(conn, recipients, validators)
	conn.commit()

	hTgOtherNotification.sendOtherNotifications(conn, recipients, validators)

	conn.commit()



def sendEventNotifications(conn, recipients, validators):
	events = notificationUtils.listEvents(conn)

	notifications = []
	processedEvents = []
	for event in events:
		eventId = event["eventId"]
		eventNotifications = processEvent(conn, event, recipients, validators)
		notifications.extend(eventNotifications)
		processedEvents.append(eventId)

	tgNotificationPushUtils.pushNotifications(notifications)
	notificationUtils.updateEventNotifiedInd(conn, processedEvents)


def processFeeChangeEvent(event, recipients, validators, increased):
	# logger.info("event: {}, recipients: {}, validators: {}, increase: {}".format(
	# 	event, recipients, validators, increased))

	if not notificationUtils.needsToBeProcessedForValidator(event, recipients):
		return []

	hPoolId = event["hPoolId"]
	chats = recipients[hPoolId]

	if increased:
		action = "increased"
		header = "<b>" + tgConstants.ARROW_UP + " Validator Fee Increase Alert" + "</b>"
	else:
		action = "decreased"
		header = "<b>" + tgConstants.ARROW_DOWN + " Validator Fee Decrease Alert" + "</b>"

	summary = "Validator has " + action + " fee. New fee is: <b>" + str(round(event["amount"],2)) + "%</b>. "
	summary += "Block number: " + str(event["blockNumber"]) + ".\n"
	# logger.info(summary)

	notifications = []
	subtitle = "Validator: <a href='https://harmony.smartstake.io/val/" + str(hPoolId) + "'>" + validators[hPoolId] + "</a>"
	groupingCriteria = subtitle
	for chatId in chats:
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": event["eventId"],
			"groupingCriteria": groupingCriteria, "summary": summary}
		notifications.append(message)

	# logger.info(notifications)
	return notifications


def processBLSKeyChangeEvent(event, recipients, validators, added):
	# logger.info("event: {}, recipients: {}, validators: {}, increase: {}".format(
	# 	event, recipients, validators, added))

	if not notificationUtils.needsToBeProcessedForValidator(event, recipients):
		return []

	hPoolId = event["hPoolId"]
	chats = recipients[hPoolId]

	if added:
		action = "added"
		header = "<b>" + tgConstants.ARROW_UP + " BLS Key Added Alert" + "</b>"
	else:
		action = "removed"
		header = "<b>" + tgConstants.ARROW_DOWN + " BLS Key Removed Alert" + "</b>"

	summary = "Validator has " + action + " a BLS key. "
	summary += "Block number: " + str(event["blockNumber"]) + ".\n"
	# logger.info(summary)

	notifications = []
	subtitle = "Validator: <a href='https://harmony.smartstake.io/val/" + str(hPoolId) + "'>" + validators[hPoolId] + "</a>"
	groupingCriteria = subtitle
	for chatId in chats:
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": event["eventId"],
			"groupingCriteria": groupingCriteria, "summary": summary}
		notifications.append(message)

	# logger.info(notifications)
	return notifications


def processDelegateEvent(conn, event, recipients, validators, recipientsLarge, increase):
	# logger.info("event: {}, recipients: {}, validators: {}, increase: {}".format(
	# 	event, recipients, validators, increase))

	if not notificationUtils.needsToBeProcessedForValidator(event, recipients) \
			and not notificationUtils.needsToBeProcessedForValidator(event, recipientsLarge):
		return []

	hPoolId = event["hPoolId"]
	chats, chatsLarge = [], []
	if hPoolId in recipients:
		chats = recipients[hPoolId]

	if hPoolId in recipientsLarge:
		chatsLarge = recipientsLarge[hPoolId]

	totalDelegation = getDelegation(conn, hPoolId, event["address"])
	totalStake = getAddressStake(conn, event["address"])
	amount = int(event["amount"])
	totalDelegationText = "<b>" + str(int(totalDelegation)) + "</b> $ONE"
	showTotalWithVal = True
	if increase:
		amountFlag = tgConstants.POSITIVE_FLAG
		action = "delegated"
		if int(totalDelegation) == int(event["amount"]):
			header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " New Delegation Alert" + "</b>"
			showTotalWithVal = False
		else:
			header = "<b>" + tgConstants.ARROW_UP + " Delegation Increased Alert" + "</b>"
	else:
		amountFlag = tgConstants.NEGATIVE_FLAG
		if round(totalDelegation, 0) == 0:
			header = "<b>" + tgConstants.ARROW_DOWN + tgConstants.ARROW_DOWN + " Undelegation Alert" + "</b>"
			action = "fully undelegated"
			showTotalWithVal = False
		else:
			action = "partially undelegated"
			header = "<b>" + tgConstants.ARROW_DOWN + " Partial Undelegation Alert" + "</b>"

	amountText = amountFlag + "<b>" + str(amount) + "</b> $ONE"
	summary = "<a href='https://harmony.smartstake.io/address/" + event["address"]
	summary += "'>" + event["address"] + "</a> has " + action + " " + amountText + ". "
	if showTotalWithVal:
		summary += "Total delegated amount with the validator is: " + totalDelegationText + ". "
	summary += "Total staked amount by the address is: <b>" + str(int(totalStake)) + "</b> $ONE. "
	summary += "Block number: " + str(event["blockNumber"]) + ".\n"
	# logger.info(summary)

	notifications = []
	subtitle = "Validator: <a href='https://harmony.smartstake.io/val/" + str(hPoolId) + "'>" + validators[hPoolId] + "</a>"
	groupingCriteria = subtitle
	for chatId in chats:
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": event["eventId"],
			"groupingCriteria": groupingCriteria, "summary": summary}
		notifications.append(message)

	if amount > hConstants.H_EVENT_NOTIFICATIONS_LARGE_MIN:
		for chatId in chatsLarge:
			if chatId not in chats:
				message = {"chatId": chatId, "header": header,
					"subtitle": subtitle, "eventId": event["eventId"],
					"groupingCriteria": groupingCriteria, "summary": summary}
				notifications.append(message)

	# logger.info(notifications)
	return notifications


def processDelegateEventForAddress(conn, event, recipients, validators, increase):
	# logger.info("event: {}, recipients: {}, validators: {}, increase: {}".format(
	# 	event, recipients, validators, increase))

	if not notificationUtils.needsToBeProcessedForAddress(event, recipients):
		return []

	address = event["address"]
	hPoolId = event["hPoolId"]
	chats = recipients[address]

	totalDelegation = getDelegation(conn, hPoolId, event["address"])
	totalStake = getAddressStake(conn, event["address"])
	amount = int(event["amount"])
	totalDelegationText = "<b>" + str(int(totalDelegation)) + "</b> $ONE"
	showTotalWithVal = True
	relation = "to"
	if increase:
		amountFlag = tgConstants.POSITIVE_FLAG
		action = "delegated"
		if int(totalDelegation) == int(event["amount"]):
			header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " New Delegation Alert" + "</b>"
			showTotalWithVal = False
		else:
			header = "<b>" + tgConstants.ARROW_UP + " Delegation Increased Alert" + "</b>"
	else:
		amountFlag = tgConstants.NEGATIVE_FLAG
		relation = "from"
		if round(totalDelegation, 0) == 0:
			header = "<b>" + tgConstants.ARROW_DOWN + tgConstants.ARROW_DOWN + " Undelegation Alert" + "</b>"
			action = "fully undelegated"
			showTotalWithVal = False
		else:
			action = "partially undelegated"
			header = "<b>" + tgConstants.ARROW_DOWN + " Partial Undelegation Alert" + "</b>"

	amountText = amountFlag + "<b>" + str(amount) + "</b> $ONE"
	validator = "validator <a href='https://harmony.smartstake.io/val/" + str(hPoolId) + "'>" + validators[hPoolId] + "</a>"
	subtitle = "<a href='https://harmony.smartstake.io/address/" + event["address"] + "'>" + event["address"] + "</a>"
	summary = "Address has " + action + " " + amountText
	summary +=  " " + relation + " " + validator + ". "
	if showTotalWithVal:
		summary += "Total delegated amount with the validator is: " + totalDelegationText + ". "
	summary += "Total staked amount by the address is: <b>" + str(int(totalStake)) + "</b> $ONE. "
	summary += "Block number: " + str(event["blockNumber"]) + ".\n"
	# logger.info(summary)

	groupingCriteria = action
	notifications = []
	for chatId in chats:
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": event["eventId"],
			"groupingCriteria": groupingCriteria, "summary": summary}
		notifications.append(message)

	# logger.info(notifications)
	return notifications


def processRewardsEvent(conn, event, recipients):
	# logger.info("event: {}, recipients: {}".format(
	# 	event, recipients))

	if not notificationUtils.needsToBeProcessedForAddress(event, recipients):
		return []

	address = event["address"]
	chats = recipients[address]

	totalStake = getAddressStake(conn, event["address"])
	amount = int(event["amount"])
	amountText = tgConstants.POSITIVE_FLAG + "<b>" + str(amount) + "</b> $ONE"
	header = "<b>" + tgConstants.MONEY_BAG + tgConstants.MONEY_BAG + " Rewards Claimed Alert" + "</b>"

	subtitle = "<a href='https://harmony.smartstake.io/address/" + event["address"] + "'>" + event["address"] + "</a>"
	summary = "Address has claimed " + amountText + " in rewards. "
	summary += "Total staked amount by the address is: <b>" + str(int(totalStake)) + "</b> $ONE. "
	summary += "Block number: " + str(event["blockNumber"]) + ".\n"
	# logger.info(summary)
	groupingCriteria = subtitle

	notifications = []
	for chatId in chats:
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": event["eventId"],
			"groupingCriteria": groupingCriteria, "summary": summary}
		notifications.append(message)

	# logger.info(notifications)
	return notifications


def processEvent(conn, event, allRecipients, validators):
	notifications = []
	if hConstants.H_EVENT_FEE_INCREASE == event["eventType"]:
		recipients = allRecipients[tgConstants.NOTIFY_FEE]
		notifications = processFeeChangeEvent(event, recipients, validators, True)
	elif hConstants.H_EVENT_FEE_DECREASE == event["eventType"]:
		recipients = allRecipients[tgConstants.NOTIFY_FEE]
		notifications = processFeeChangeEvent(event, recipients, validators, False)
	elif hConstants.H_EVENT_BLS_KEY_ADDED == event["eventType"]:
		recipients = allRecipients[tgConstants.NOTIFY_KEY_CHANGES]
		notifications = processBLSKeyChangeEvent(event, recipients, validators, True)
	elif hConstants.H_EVENT_BLS_KEY_REMOVED == event["eventType"]:
		recipients = allRecipients[tgConstants.NOTIFY_KEY_CHANGES]
		notifications = processBLSKeyChangeEvent(event, recipients, validators, False)
	elif hConstants.H_EVENT_DELEGATE == event["eventType"]:
		recipients = allRecipients[tgConstants.NOTIFY_DEL]
		recipientsLarge = allRecipients[tgConstants.NOTIFY_LARGE]
		notifications = processDelegateEvent(conn, event, recipients, validators, recipientsLarge, True)

		addressRecipients = allRecipients[tgConstants.NOTIFY_ADDRESS]
		addressNotifications = processDelegateEventForAddress(conn, event, addressRecipients, validators, True)
		notifications.extend(addressNotifications)
	elif hConstants.H_EVENT_UNDELEGATE == event["eventType"]:
		recipients = allRecipients[tgConstants.NOTIFY_UNDEL]
		recipientsLarge = allRecipients[tgConstants.NOTIFY_LARGE]
		notifications = processDelegateEvent(conn, event, recipients, validators, recipientsLarge, False)

		addressRecipients = allRecipients[tgConstants.NOTIFY_ADDRESS]
		addressNotifications = processDelegateEventForAddress(conn, event, addressRecipients, validators, False)
		notifications.extend(addressNotifications)
	elif hConstants.H_EVENT_COLLECT_REWARDS == event["eventType"]:
		recipients = allRecipients[tgConstants.NOTIFY_ADDRESS]
		notifications = processRewardsEvent(conn, event, recipients)

	return notifications


def listValidators(conn):
	sql = "select hPoolId, name "
	sql += " from " + tables.hpool

	# logger.info(sql)
	listData = dbUtil.listResultsWithConn(sql, conn)
	return commonUtils.getMapWithValueFromList(listData, "hPoolId", "name")


def getDelegation(conn, hPoolId, address):
	sql = "select stake "
	sql += " from " + tables.hpooldel
	sql += " where hPoolId=%s and address=%s "

	# logger.info(sql)
	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (hPoolId, address))

	if not record:
		return 0

	return record["stake"]


def getAddressStake(conn, address):
	sql = " select round(totalStake,0) as totalStake "
	sql += " from " + tables.haddress
	sql += " where address = %s "

	# logger.info(sql)
	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, address)

	if record:
		return record["totalStake"]

	return 0

