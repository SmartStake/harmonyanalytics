import logging

import commonUtils
import constants
import hConstants
import notificationUtils
import propUtils
import tgConstants
import tgNotificationPushUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Notifications for validator performance –
# validator low signage, - val sync -done
# validator low rewards, - val sync -done
# NOTIFY_VALIDATOR_PERF = "notifyValPerf" - val sync
# NOTIFY_KEY_PERF = "notifyKeyPerf" - key syncer - done

# bot Alert/notification - when a validator specifics BLS key is not signing, - done

#FIXME also include notification for getting booted from next election - hpool.activestatus = 'inactive' - raise event on every epoch change


# NOTIFY_DEL_PERFORMANCE = "notifyDelPerf" -- unelected .
# not elected completely, --- when new epoch comes  - slot syncer
# not elected partially --- when new epoch comes - slot syncer
# Notifications for validator elections -
# falling out of election slots - slot syncer
# , having excessively high bid - slot syncer
# , marked as in-eligible  - slot syncer

# NOTIFY_ELECTION = "notifyElection" - slot syncer

NO_WATCH = "0"
SET_WATCH = "1"
REMOVE_WATCH = "0"

def sendOtherNotifications(conn, recipients, validators):
	logger.info("in other sendNotifications")
	notices = notificationUtils.listPendingNotifications(conn)

	notifications = []
	processedEvents = []
	# watchEvents = []
	for notice in notices:
		# logger.info(notice)
		notificationId = notice["notificationId"]
		hNotifications, watch = processNotification(conn, notice, recipients, validators)
		notifications.extend(hNotifications)
		# logger.info("watch: {} and notifications: {}".format(watch, hNotifications))
		# if len(hNotifications) > 0:
		# 	processedEvents.append((watch, notificationId))
		# else:
		processedEvents.append((watch, notificationId))


	tgNotificationPushUtils.pushNotifications(notifications)
	notificationUtils.updateNotificationInd(conn, processedEvents)
	logger.info("processed sendNotifications: {}".format(len(notifications)))


def processNotification(conn, notice, allRecipients, validators):
	# noticeType = notice["notificationType"]
	handled, notifications, watch = processValPerfNotification(notice, allRecipients, validators)

	if not handled:
		handled, notifications, watch = processKeyPerfNotification(notice, allRecipients, validators)

	if not handled:
		handled, notifications, watch = processElectionNotification(notice, allRecipients, validators)

	if not handled:
		handled, notifications, watch = processUnderBidNotification(conn, notice)

	if not handled:
		handled, notifications, watch = processTxNotification(notice, allRecipients)

	return notifications, watch


def processKeyPerfNotification(notice, allRecipients, validators):
	noticeType = notice["notificationType"]

	recipients = allRecipients[tgConstants.NOTIFY_KEY_PERF]

	handle, notifications, header, details, watch = False, [], None, None, NO_WATCH
	if hConstants.NOTIFICATION_TYPE_KEY_PERF_BAD == noticeType:
		handle, watch = True, SET_WATCH
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Validator BLS Key performance is bad " + "</b>"
		details = getBlsKeyMsgDetails(True, notice)
	elif hConstants.NOTIFICATION_TYPE_KEY_PERF_GOOD == noticeType:
		handle, watch = True, REMOVE_WATCH
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Validator BLS Key performance has improved " + "</b>"
		details = getBlsKeyMsgDetails(False, notice)

	if handle:
		notifications = getValPerfNotificationResponse(notice, recipients, validators, header, details)

	return handle, notifications, watch


def getBlsKeyMsgDetails(bad, notice):
	# logger.info("bad: {}, notice: {}".format(bad, notice))

	details = "Shard <b>" + str(int(notice["value2"])) + "</b> BLS Key <a href=\""
	details += hConstants.KEY_URL.format(notice["blsKey"], notice["epochNumber"]) + "\">"
	details += notice["blsKey"] + "</a> performance index is <b>" + str(notice["value1"]) + "</b>. "
	if bad:
		details += "It is below the performance threshold of "
	else:
		details += "It has improved and is above the threshold "

	details += "<b>" + hConstants.KEY_BAD_PERF_INDEX_THRESHOLD + "</b>. "

	return details


def getValPerfNotificationResponse(notice, recipients, validators, header, details, epochNumber=None):
	# logger.info("notice: {}, recipients: {}, validators: {}".format(
	# 	notice, recipients, validators))

	if not notificationUtils.needsToBeProcessedForValidator(notice, recipients):
		# logger.info("no valid recipient for this notification")
		return []

	# logger.info("recipient found for this notification")
	hPoolId = notice["hPoolId"]
	chats = recipients[hPoolId]

	if not epochNumber:
		epochNumber = notice["epochNumber"]

	summary = details
	summary += "Epoch number: " + str(epochNumber) + ".\n "
	# summary += "Block number: " + str(notice["blockNumber"]) + ".\n "
	# logger.info(summary)

	notifications = []
	subtitle = "Validator: <a href='https://harmony.smartstake.io/val/" + str(hPoolId) + "'>" + validators[hPoolId] + "</a>"
	for chatId in chats:
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": "notification" + str(notice["notificationId"]),
			"groupingCriteria": subtitle, "summary": summary}
		notifications.append(message)

	# logger.info(notifications)
	return notifications


def processValPerfNotification(notice, allRecipients, validators):
	noticeType = notice["notificationType"]

	recipients = notificationUtils.combineRecipients(allRecipients,
			tgConstants.NOTIFY_DEL_PERFORMANCE, tgConstants.NOTIFY_VALIDATOR_PERF)

	handle, notifications, header, details, watch = False, [], None, None, NO_WATCH
	if hConstants.NOTIFICATION_TYPE_LOW_SIGN == noticeType:
		handle, watch = True, SET_WATCH
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Validator block sign rate is low " + "</b>"
		details = "Validator block sign rate is <b>{}%</b>. It is below the performance threshold of <b>{}%</b>. ".format(notice["value1"], hConstants.LOW_SIGN_THRESHOLD)
	elif hConstants.NOTIFICATION_TYPE_GOOD_SIGN == noticeType:
		handle, watch = True, REMOVE_WATCH
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Validator block sign rate has improved " + "</b>"
		details = "Validator block sign rate is <b>{}%</b>. It has improved and is above the threshold <b>{}%</b>. ".format(notice["value1"], hConstants.LOW_SIGN_THRESHOLD)
	elif hConstants.NOTIFICATION_TYPE_LOW_ERI == noticeType:
		handle, watch = True, SET_WATCH
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Validator rate of returns is low " + "</b>"
		details = "Validator expected rate index (ERI) is <b>{}</b>. It is below the performance threshold of <b>{}</b>. ".format(notice["value1"], hConstants.LOW_ERI_THRESHOLD)
	elif hConstants.NOTIFICATION_TYPE_GOOD_ERI == noticeType:
		handle, watch = True, REMOVE_WATCH
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Validator rate of returns has improved " + "</b>"
		details = "Validator expected rate index (ERI) is <b>{}</b>. It has improved and is above the threshold <b>{}</b>. ".format(notice["value1"], hConstants.LOW_SIGN_THRESHOLD)
	elif hConstants.NOTIFICATION_TYPE_SELF_BOND_REMOVED == noticeType:
		handle = True
		header = "<b>" + tgConstants.ARROW_DOWN + tgConstants.ARROW_DOWN + " Validator has removed self bond " + "</b>"
		details = "Validator has removed some/all of self bond. Current self bond is <b>{}</b> $ONE. Validators with less than 10k $ONE in self delegation are not valid. Please verify, contact the validator, & if needed switch delegation. ".format(notice["value1"])
	elif hConstants.NOTIFICATION_TYPE_BLS_KEY_ON_OLD_VERSION == noticeType:
		# logger.info("found: {}".format(hConstants.NOTIFICATION_TYPE_BLS_KEY_ON_OLD_VERSION))
		handle = True
		header = "<b>" + tgConstants.ARROW_DOWN + tgConstants.ARROW_DOWN + " One of your BLS Key is using old Harmony Node Software " + "</b>"
		details = "Harmony has released a mandatory update {}. At least one of your BLS key is using an older version {}. The change is/was effective from epoch: {}. ".format(
			notice["otherData1"], notice["otherData2"], int(notice["value1"]))

	if handle:
		notifications = getValPerfNotificationResponse(notice, recipients, validators, header, details)

	return handle, notifications, watch


def processElectionNotification(notice, allRecipients, validators):
	noticeType = notice["notificationType"]

	recipients = notificationUtils.combineRecipients(allRecipients,
			tgConstants.NOTIFY_DEL_PERFORMANCE, tgConstants.NOTIFY_VALIDATOR_PERF)
	# recipients = notificationUtils.combineRecipientsFromData(recipients, allRecipients[tgConstants.NOTIFY_EPOCH])

	handle, notifications, header, details, watch, epochNumber = False, [], None, None, NO_WATCH, notice["epochNumber"]
	if hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED == noticeType and notice["value2"]:
		# this notification is in the context of epoch ending being close by
		recipients = allRecipients[tgConstants.NOTIFY_EPOCH]
		handle, epochNumber = True, int(notice["value1"])
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Next epoch starting soon - Validator is at the risk of partial election " + "</b>"
		details = "Next epoch is starting in about {} minutes. Validator is at the risk of partial election for next epoch. It has atleast one BLS Key unelected at this time. ".format(int(notice["value2"]))
	elif hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED == noticeType:
		handle, watch, epochNumber = True, SET_WATCH, int(notice["value1"])
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Next Epoch - Validator is at the risk of partial election " + "</b>"
		details = "Validator is at the risk of partial election for next epoch. It has atleast one BLS Key unelected at this time. "
	elif hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED_END == noticeType:
		handle, watch, epochNumber = True, REMOVE_WATCH, int(notice["value1"])
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Next Epoch - Validator is NO LONGER at risk of partial election " + "</b>"
		details = "Validator is <b>no longer</b> at the risk of partial election for next epoch. "
	elif hConstants.NOTIFICATION_TYPE_RISK_UNELECTED == noticeType and notice["value2"]:
		# this notification is in the context of epoch ending being close by
		recipients = allRecipients[tgConstants.NOTIFY_EPOCH]
		handle, epochNumber = True, int(notice["value1"])
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Next epoch starting soon - Validator is at the risk of not getting elected " + "</b>"
		details = "Next epoch is starting in about {} minutes. Validator is at the risk of not getting elected for next epoch. ".format(int(notice["value2"]))
	elif hConstants.NOTIFICATION_TYPE_RISK_UNELECTED == noticeType:
		handle, watch, epochNumber = True, SET_WATCH, int(notice["value1"])
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Next Epoch - Validator is at the risk of not getting elected " + "</b>"
		details = "Validator is at the risk of not getting elected for next epoch. "
	elif hConstants.NOTIFICATION_TYPE_RISK_UNELECTED_END == noticeType:
		handle, watch, epochNumber = True, REMOVE_WATCH, int(notice["value1"])
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Next Epoch - Validator risk of unelection has ended " + "</b>"
		details = "Validator is <b>elected</b> at this time for next epoch. The situation can change at any time though. "
	elif hConstants.NOTIFICATION_TYPE_RISK_HIGH_BID == noticeType and notice["value2"]:
		# this notification is in the context of epoch ending being close by
		recipients = allRecipients[tgConstants.NOTIFY_EPOCH]
		handle, epochNumber = True, int(notice["value1"])
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Next epoch starting soon - Validator has inefficient bid at this time " + "</b>"
		details = "Next epoch is starting in about {} minutes. Validator has inefficient bid at this time. Validator should be able to add at least one more key (assuming nothing else changes in the network) ".format(int(notice["value2"]))
	elif hConstants.NOTIFICATION_TYPE_RISK_HIGH_BID == noticeType:
		handle, watch, epochNumber = True, SET_WATCH, int(notice["value1"])
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Next Epoch - Validator has inefficient bid at this time " + "</b>"
		details = "Validator has inefficient bid at this time. Validator should be able to add at least one more key (assuming nothing else changes in the network) "
	elif hConstants.NOTIFICATION_TYPE_RISK_UNELECTED_END == noticeType:
		handle, watch, epochNumber = True, REMOVE_WATCH, int(notice["value1"])
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Next Epoch - Validator risk of inefficient bid has ended " + "</b>"
		details = "Validator does not have inefficient bid at this time. "
	elif hConstants.NOTIFICATION_TYPE_PARTIALLY_ELECTED == noticeType:
		handle, watch = True, SET_WATCH
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Current Epoch - Validator is partially elected " + "</b>"
		details = "Validator is partially elected for current epoch. It has atleast one BLS Key unelected. "
	elif hConstants.NOTIFICATION_TYPE_UNELECTED == noticeType:
		handle, watch = True, SET_WATCH
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Current Epoch - Validator is not elected " + "</b>"
		details = "Validator is not elected in current epoch. "
	elif hConstants.NOTIFICATION_TYPE_UNELECTED_FOR_LONG == noticeType:
		handle, watch = True, SET_WATCH
		header = "<b>" + tgConstants.WARNING_SIGN + tgConstants.WARNING_SIGN + " Validator has been unelected for last 7+ epochs. " + "</b>"
		details = "Validator has been unelected for last 7+ epochs. Contact the validator or consider moving your delegation. "
	elif hConstants.NOTIFICATION_TYPE_EPOCH_ENDING_SOON == noticeType and notice["value2"]:
		# this notification is in the context of epoch ending being close by
		recipients = allRecipients[tgConstants.NOTIFY_EPOCH]
		handle, epochNumber = True, int(notice["value1"])
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Next epoch starting soon - validator is fully elected " + "</b>"
		details = "Next epoch is starting in about {} minutes. Validator is fully elected. ".format(int(notice["value2"]))

	if handle:
		notifications = getValPerfNotificationResponse(notice, recipients, validators, header, details, epochNumber)

	return handle, notifications, watch


def processUnderBidNotification(conn, notice):
	noticeType = notice["notificationType"]

	handle, notifications, header, details, watch, epochNumber = False, [], None, None, NO_WATCH, notice["epochNumber"]
	if hConstants.NOTIFICATION_TYPE_UNDER_BID_OPP == noticeType:
		handle, watch, epochNumber = True, SET_WATCH, int(notice["value1"])
		header = "<b>" + tgConstants.ARROW_UP + tgConstants.ARROW_UP + " Next Epoch - There is an opportunity to underbid " + "</b>"
		details = "There is an opportunity to underbid and get higher rewards. Number of keys with underbid: {}".format(int(notice["value2"]))
	elif hConstants.NOTIFICATION_TYPE_UNDER_BID_OPP_END == noticeType:
		handle, watch, epochNumber = True, REMOVE_WATCH, int(notice["value1"])
		header = "<b> Next Epoch - There is NO opportunity to underbid anymore " + "</b>"
		details = "There is NO opportunity to underbid anymore."

	if handle:
		summary = "Epoch number: " + str(epochNumber) + ".\n "

		chatId = propUtils.getPropValue(conn, constants.APP, constants.PROP_KEY_TG_ID)

		notifications = []
		subtitle = details
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": "notification" + str(notice["notificationId"]),
			"groupingCriteria": subtitle, "summary": summary}
		notifications.append(message)

	return handle, notifications, watch


def processTxNotification(notice, allRecipients):
	# logger.info("notice: {}, recipients: {}".format(
	# 	notice, allRecipients))

	handle, notifications, watch = False, [], NO_WATCH

	noticeType = notice["notificationType"]

	if hConstants.NOTIFICATION_TYPE_REGULAR_TX_FROM == noticeType or hConstants.NOTIFICATION_TYPE_REGULAR_TX_TO == noticeType:
		# this notification is for regular non-staking transactions
		recipients = allRecipients[tgConstants.NOTIFY_ADDRESS]
		handle = True
		trimmedTxHash = notice["txHash"][0:5] + ".." + notice["txHash"][-5:]

		if notice["otherData2"] == hConstants.TX_STATUS_SUCCESS:
			sign = tgConstants.CHECK_MARK
		else:
			sign = tgConstants.CROSS_MARK

		if notice["otherData2"] == hConstants.NOTIFICATION_TYPE_REGULAR_TX_FROM:
			direction = "outgoing"
		else:
			direction = "incoming"

		address1 = notice["address"]
		address2 = notice["otherData1"]
		header = "<b>" + sign + sign + " Transaction performed " + "</b>"
		subtitle = "An {} transaction was performed from address {} to address {}".format(
			direction, address1, address2 )
		details = "An {} transaction with amount {} was performed from address {} to address {}. ".format(
			direction, round(float(notice["value1"]), 4), address1, address2)
		details += "Tx status is: {}. " \
				  "Block number is: {}. Tx hash is: <a href='https://explorer.harmony.one/#/tx/{}'>{}</a>.".format(
			notice["otherData2"], notice["blockNumber"], notice["txHash"], trimmedTxHash)

		notifications = getRegularTxNoticeForAddress(notice, recipients, header, subtitle, details)

	return handle, notifications, watch


def getRegularTxNoticeForAddress(notice, recipients, header, subtitle, details):
	# logger.info("notice: {}, recipients: {}, header: {}, details: {}".format(
	# 	notice, recipients, header, details))

	if not notificationUtils.needsToBeProcessedForAddress(notice, recipients) \
			and not notificationUtils.needsToBeProcessedForAddressByKey(notice, recipients, "otherData1"):
		return []

	if notice["address"] in recipients and notice["otherData1"] not in recipients:
		chats = recipients[notice["address"]]
	elif notice["address"] not in recipients and notice["otherData1"] in recipients:
		chats = recipients[notice["otherData1"]]
	else:
		chats = commonUtils.combineTwoListsToSet(recipients[notice["address"]], recipients[notice["otherData1"]])

	summary = details + "\n"
	notifications = []
	for chatId in chats:
		message = {"chatId": chatId, "header": header,
			"subtitle": subtitle, "eventId": "notification" + str(notice["notificationId"]),
			"groupingCriteria": subtitle, "summary": summary}
		notifications.append(message)

	# logger.info(notifications)
	return notifications


