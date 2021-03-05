import logging

import commonUtils
import constants
import dbUtil
import hConstants
import tables
import tgConstants

logger = logging.getLogger()
logger.setLevel(logging.INFO)

eventTable = tables.hevent
notificationTable = tables.hnotification

def updateEventNotifiedInd(conn, updates):
	# logger.info("in updateEventNotifiedInd: {}".format(len(updates)))

	sql = "update " + eventTable
	sql += " set notifiedInd = '1' "
	sql += " where eventId = %s "

	count = conn.cursor().executemany(sql, updates)
	# logger.info("updated notified ind for: {}".format(count))


def listEvents(conn):
	sql = "select e.*, round((UNIX_TIMESTAMP() - e.epochBlockTime) / 60,0) as elapsedTime "
	sql += " from " + eventTable + " e "
	sql += " where e.notifiedInd = '0' "
	sql += " order by e.blockNumber limit 1000 "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn)


def getNotificationRecipients(conn):
	users = listNotificationUsers(conn)

	notifyDel, notifyUndel, notifyFee, notifyKeyChanges, notifyLarge = [], [], [], [], []
	notifyElection, notifyEpoch, notifyDelPerf, notifyKeyPerf, notifyAddress, notifyValPerf = [], [], [], [], [], []
	for user in users:
		validators = getValidatorsForNotification(user, tgConstants.NOTIFY_DEL)
		# logger.info("validators for notifyDel for user: {} are: {}".format(user["userId"], validators))
		notifyDel.extend(validators)
		# logger.info("validators: {} and notifyDel: {}".format(validators, notifyDel))

		notifyUndel.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_UNDEL))
		notifyFee.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_FEE))
		notifyKeyChanges.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_KEY_CHANGES))
		notifyLarge.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_LARGE))
		notifyElection.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_ELECTION))
		notifyEpoch.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_EPOCH))
		notifyDelPerf.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_DEL_PERFORMANCE))
		notifyKeyPerf.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_KEY_PERF))
		notifyValPerf.extend(getValidatorsForNotification(user, tgConstants.NOTIFY_VALIDATOR_PERF))

		notifyAddress.extend(getAddressesForNotification(user, tgConstants.NOTIFY_ADDRESS))

	# logger.info("before mapping - notifyDel: {}".format(notifyDel))
	notifyDelMap = getValChatsMap(notifyDel)
	# logger.info("after mapping - notifyDelMap: {}".format(notifyDelMap))
	recipients = {tgConstants.NOTIFY_DEL: notifyDelMap,
		tgConstants.NOTIFY_UNDEL: getValChatsMap(notifyUndel),
		tgConstants.NOTIFY_FEE: getValChatsMap(notifyFee),
		tgConstants.NOTIFY_KEY_CHANGES: getValChatsMap(notifyKeyChanges),
		tgConstants.NOTIFY_LARGE: getValChatsMap(notifyLarge),
		tgConstants.NOTIFY_ELECTION: getValChatsMap(notifyElection),
		tgConstants.NOTIFY_EPOCH: getValChatsMap(notifyEpoch),
		tgConstants.NOTIFY_DEL_PERFORMANCE: getValChatsMap(notifyDelPerf),
		tgConstants.NOTIFY_KEY_PERF: getValChatsMap(notifyKeyPerf),
		tgConstants.NOTIFY_VALIDATOR_PERF: getValChatsMap(notifyValPerf),
		tgConstants.NOTIFY_ADDRESS: getChatsMap(notifyAddress, "address"),
	}

	# logger.info("recipients list for all notifications is: {}".format(recipients))

	return recipients


def getValChatsMap(valueChatList):
	return getChatsMap(valueChatList, "poolId")


def getChatsMap(valueChatList, groupByKey):
	# logger.info("in getValChatsMap: {} for: {}".format(valueChatList, groupByKey))
	valueChatsMap = {}
	for valueChat in valueChatList:
		value = valueChat[groupByKey]
		# logger.info("value: {}".format(value))
		if value in valueChatsMap:
			# logger.info("groupByKey exists in valueChatsMap")
			users = valueChatsMap[value]
			users.append(valueChat["chatId"])
			valueChatsMap[value] = users
			# logger.info("valueChatsMap[value]: {}".format(users))
		else:
			# logger.info("groupByKey does not exist in valueChatsMap")
			users = [valueChat["chatId"]]
			valueChatsMap[value] = users
			# logger.info("value: {}".format(value))
		# logger.info("valueChatsMap after processing value: {}, is: {}".format(value, valueChatsMap[value]))

	# logger.info("in getValChatsMap: {}".format(valueChatsMap))
	return valueChatsMap


def getValidatorsForNotification(user, key):
	# logger.info("user: {}, key: {}, user[key]: {}".format(user, key, user[key]))
	if user[key] == "True" and user["favPools"]:
		# logger.info("processing user setting further")
		vals = user["favPools"].split(",")
		chatVal = []
		for val in vals:
			chatVal.append({"poolId": int(val), "chatId": user["chatId"]})
		# logger.info("chat validators for the key are: {}".format(chatVal))

		return chatVal

	# logger.info("returning empty")
	return []


def getAddressesForNotification(user, key):
	# logger.info("user: {}, key: {}, user[key]: {}".format(user, key, user[key]))
	if user[key] == "True" and user["address"]:
		# logger.info("processing user setting further")
		addresses = user["address"].split(",")
		chatAdd = []
		for address in addresses:
			chatAdd.append({"address": address, "chatId": user["chatId"]})
		# logger.info("chat validators for the key are: {}".format(chatVal))

		return chatAdd

	# logger.info("returning empty")
	return []


def listNotificationUsers(conn):
	sql = "select * "
	sql += " from " + tables.tgsetting
	sql += " where app = %s and (notifyDel = 'True' "
	sql += " or notifyUndel = 'True' "
	sql += " or notifyFee = 'True' "
	sql += " or notifyKeyChanges = 'True' "
	sql += " or notifyLarge = 'True' "
	sql += " or notifyElection = 'True' "
	sql += " or notifyDelPerf = 'True' "
	sql += " or notifyKeyPerf = 'True' "
	sql += " or notifyAddress = 'True' "
	sql += " or notifyValPerf = 'True' "
	sql += " ) "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn, constants.APP)


def listNotificationUsersForPerf(conn):
	sql = "select * "
	sql += " from " + tables.tgsetting
	sql += " where app = %s and (notifyDelPerf = 'True' "
	sql += " or notifyValPerf = 'True' "
	sql += " ) "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn, constants.APP)


def organizeNotByTypeAndChat(notifications, specialParam):
	notificationsByType = {}

	for notification in notifications:
		key = notification["chatId"] + notification["header"] + str(notification[specialParam])
		if key in notificationsByType:
			ntRecords = notificationsByType[key]
			ntRecords.append(notification)
		else:
			ntRecords = [notification]
			notificationsByType[key] = ntRecords

	return notificationsByType


def resetWatchEvents(conn, epochNumber):
	sql = "update " + tables.hnotification
	sql += " set watchInd = '0' where "
	sql += " epochNumber < %s and notifiedInd = '1' "

	count = conn.cursor().execute(sql, epochNumber)
	logger.info("reset watch indicator for: {}".format(count))


def listPendingNotifications(conn):
	sql = "select * "
	sql += " from " + notificationTable + " e "
	sql += " where e.notifiedInd = '0' "
	sql += " order by e.creationDate limit 1000 "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn)


def updateNotificationInd(conn, updates):
	logger.info("in updateEventNotifiedInd: {}".format(len(updates)))

	sql = "update " + notificationTable + " set "
	sql += " notifiedInd = '1', watchInd = %s "
	sql += " where notificationId = %s "

	count = conn.cursor().executemany(sql, updates)
	logger.info("updated notified ind for: {}".format(count))


def updateEndWatchList(conn, updates):
	logger.info("in updateEndWatchList: {}".format(len(updates)))
	# logger.info(updates)

	sql = "update " + notificationTable + " set "
	sql += " watchInd = '0' "
	sql += " where notifiedInd = '1' and notificationId = %s "

	count = conn.cursor().executemany(sql, updates)
	logger.info("updateEndWatchList for: {}".format(count))


# def updateNotificationInd(conn, watchInd, updates):
# 	logger.info("in updateEventNotifiedInd: {}".format(len(updates)))
#
# 	sql = "update " + notificationTable + " set "
# 	if watchInd:
# 		sql += " notifiedInd = '1', watchInd = '1' "
# 	else:
# 		sql += " notifiedInd = '1' "
# 	sql += " where eventId = %s "
#
# 	count = conn.cursor().executemany(sql, updates)
# 	logger.info("updated notified ind for: {}".format(count))


def needsToBeProcessedForValidator(event, recipients):
	#has anyone subscribed to this event
	if len(recipients.keys()) == 0:
		# logger.info("length is : {}".format(len(recipients)))
		return False

	hPoolId = event["hPoolId"]
	#is anyone monitoring this validator
	if hPoolId not in recipients:
		# logger.info("validator: {} is not in recipients: {}".format(hPoolId, recipients))
		return False

	# logger.info("returning true")
	return True


def needsToBeProcessedForAddress(event, recipients):
	return needsToBeProcessedForAddressByKey(event, recipients, "address")


def needsToBeProcessedForAddressByKey(event, recipients, key):
	#has anyone subscribed to this event
	if len(recipients.keys()) == 0:
		# logger.info("length is : {}".format(len(recipients)))
		return False

	address = event[key]
	#is anyone monitoring this validator
	if address not in recipients:
		# logger.info("validator: {} is not in recipients: {}".format(hPoolId, recipients))
		return False

	# logger.info("returning true")
	return True


def combineRecipients(allRecipients, key1, key2):
	data1 = allRecipients[key1]
	data2 = allRecipients[key2]
	return combineRecipientsFromData(data1, data2)


def combineRecipientsFromData(data1, data2):
	data = data1.copy()
	# logger.info("combining list 1: {}, with list 2: {}".format(data1, data2))

	for key, values in data2.items():
		if key in data:
			listData = data[key]
			for value in values:
				if value not in listData:
					listData.append(value)
			data[key] = listData
		else:
			data[key] = values

	# logger.info("combining list 1: {}, with list 2: {}. final length: {}".format(
	# 	len(data1.keys()), len(data2.keys()), len(data.keys())))

	return data


def listValidatorsWithBadPerf(conn, currentEpoch, notificationType):
	sql = "select * from " + tables.hpoolperf + " pp "
	sql += " where mode='EPOCH' and epochNumber=%s"
	sql += " and status='Elected' "
	if notificationType == hConstants.NOTIFICATION_TYPE_LOW_SIGN:
		sql += " and signPer < " + hConstants.LOW_SIGN_THRESHOLD
	else:
		sql += " and eri < " + hConstants.LOW_ERI_THRESHOLD

	sql += " and not exists (select 1 from " + tables.hnotification + " hn"
	sql += " 	where hn.hPoolId = pp.hPoolId "
	sql += "     and hn.epochNumber = pp.epochNumber"
	sql += "     and hn.notificationType = %s"
	sql += "     and (hn.watchInd = '1' or hn.notifiedInd='0') )"

	args = (currentEpoch, notificationType)
	# logger.info("sql: {}, args: {}".format(sql, args))
	listData = dbUtil.listResultsWithConn(sql, conn, args)
	# logger.info(listData)
	return listData


def listValidatorsWithImprovedPerf(conn, currentEpoch, notificationType):
	sql = "select hn.*, pp.eri, pp.signPer from " + tables.hpoolperf + " pp "
	sql += " inner join " + tables.hnotification + " hn "
	sql += " 	on hn.hPoolId = pp.hPoolId "
	sql += "  	and hn.epochNumber = pp.epochNumber"
	sql += "  	and hn.watchInd = '1' "
	sql += " where mode='EPOCH' and pp.epochNumber=%s "
	sql += " and hn.notificationType = %s "
	sql += " and status='Elected' "
	if notificationType == hConstants.NOTIFICATION_TYPE_LOW_SIGN:
		sql += " and signPer > " + hConstants.LOW_SIGN_THRESHOLD
	else:
		sql += " and eri > " + hConstants.LOW_ERI_THRESHOLD

	args = (currentEpoch, notificationType)
	# logger.info("sql: {}, args: {}".format(sql, args))
	listData = dbUtil.listResultsWithConn(sql, conn, args)
	# logger.info(listData)
	return listData


def getKeyMapForBadPerfCheck(conn, currentEpoch, notificationType):
	sql = "select hp.hPoolId, bk.blsKey "
	sql += " from " + tables.hpool + " hp "
	sql += " inner join " + tables.hblskey + " bk on hp.hPoolId = bk.hPoolId "
	sql += " where status='" + hConstants.H_ELECTED + "'"
	sql += " and not exists (select 1 from " + tables.hnotification + " hn "
	sql += "	where hn.hPoolId = hp.hPoolId "
	sql += "    and hn.epochNumber = %s "
	sql += "    and hn.notificationType = %s "
	sql += "    and (hn.watchInd = '1' or hn.notifiedInd='0') ) "

	args = (currentEpoch, notificationType)
	# logger.info("sql: {}, args: {}".format(sql, args))
	listData = dbUtil.listResultsWithConn(sql, conn, args)
	# logger.info(listData)

	badKeyMap = commonUtils.getMapFromList(listData, "blsKey")
	return badKeyMap


def getKeyMapForGoodPerfCheck(conn, currentEpoch, notificationType):
	sql = "select hp.hPoolId, bk.blsKey, hn.notificationId "
	sql += " from " + tables.hpool + " hp "
	sql += " inner join " + tables.hblskey + " bk on hp.hPoolId = bk.hPoolId "
	sql += " inner join " + tables.hnotification + " hn on hn.hPoolId = hp.hPoolId "
	sql += " 	and bk.blsKey=hn.blsKey "
	sql += " where status='" + hConstants.H_ELECTED + "'"
	sql += "    and hn.epochNumber = %s "
	sql += "    and hn.notificationType = %s "
	sql += "    and hn.watchInd = '1' "

	args = (currentEpoch, notificationType)
	# logger.info("sql: {}, args: {}".format(sql, args))
	listData = dbUtil.listResultsWithConn(sql, conn, args)
	# logger.info(listData)

	goodKeyMap = commonUtils.getMapFromList(listData, "blsKey")
	return goodKeyMap


def batchCreateNotifications(conn, events):
	sql = " insert into " + tables.hnotification
	sql += " (notificationType, address, hPoolId, epochNumber, "
	sql += " value1, value2, blsKey, blockNumber) "
	sql += " values (%s, %s, %s, %s, %s, %s, %s, %s)"

	conn.cursor().executemany(sql, events)


def batchCreateNotificationsWithOtherData(conn, notifications):
	sql = " insert into " + tables.hnotification
	sql += " (notificationType, address, hPoolId, epochNumber, "
	sql += " value1, value2, blsKey, blockNumber, "
	sql += " otherData1, otherData2, txHash) "
	sql += " values (%s, %s, %s, %s, %s, %s, %s, %s, "
	sql += " %s, %s, %s)"

	conn.cursor().executemany(sql, notifications)


def getNotMapForElectionCheck(conn, epoch, next):
	# logger.info("in getNotMapForElectionCheck(epoch: {}, next: {})".format(epoch, next))

	sql = "select * from "
	sql += tables.hnotification + " hn "
	sql += " where hn.epochNumber = %s "
	sql += " and hn.notificationType in ( "

	if next:
		sql += "'" + hConstants.NOTIFICATION_TYPE_RISK_UNELECTED + "',"
		sql += "'" + hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED + "',"
		sql += "'" + hConstants.NOTIFICATION_TYPE_RISK_HIGH_BID + "'"
	else:
		sql += "'" + hConstants.NOTIFICATION_TYPE_UNELECTED + "',"
		sql += "'" + hConstants.NOTIFICATION_TYPE_PARTIALLY_ELECTED + "',"
		sql += "'" + hConstants.NOTIFICATION_TYPE_UNELECTED_FOR_LONG + "'"

	sql += " ) "
	sql += " and (hn.watchInd = '1' or hn.notifiedInd='0') "

	args = (epoch)
	# logger.info("sql: {}, args: {}".format(sql, args))
	listData = dbUtil.listResultsWithConn(sql, conn, args)
	# logger.info(listData)

	badKeyMap = commonUtils.getMapFromList2Keys(listData, "notificationType", "hPoolId")
	# logger.info("badKeyMap: {}".format(badKeyMap))
	return badKeyMap


def isNotForUnderBidPresent(conn, currentEpoch, notificationType):
	sql = "select * "
	sql += " from " + tables.hnotification + " hn "
	sql += " where hn.epochNumber = %s "
	sql += "    and hn.notificationType = %s "
	sql += "    and hn.watchInd = '1' "

	args = (currentEpoch, notificationType)
	# logger.info("sql: {}, args: {}".format(sql, args))
	return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, args)

