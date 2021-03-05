import datetime
import logging

import auditUtils
import commonUtils
import constants
import eventName
import hConstants
import harmonyData
import harmonyUtils
import harmonyValEvents
import notificationUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ES_ELECTED = "elected"
ES_NOT_ELECTED = "not_elected"
ES_PARTIALLY_ELECTED = "partially_elected"
ES_NOT_POSSIBLE = "not_possible"

def electionSync(conn, app, data, event):
	logger.info("in electionSync for harmony")

	startTimeAudit = datetime.datetime.now()

	processElections(conn, app)

	auditUtils.createEvent(conn, app, eventName.syncHarmonyElections)
	auditUtils.audit(conn, app, event, eventName.syncHarmonyElections, "service", startTimeAudit)


def processElections(conn, app):
	validators = harmonyData.listAllValidators(conn)
	# logger.info(validators)
	valByAddMap = commonUtils.getMapFromList(validators, "address")
	data = commonUtils.getDataByUrl(hConstants.ELECTIONS_URL)
	currentEpoch = data["current_epoch"]
	currentBlock = data["current_block_number"]
	coinStat = commonUtils.getCoinStat(conn, constants.APP)
	timeLeft, eventToUpdate = getEpochEndTimeLeftForEpochAlert(conn, coinStat, currentEpoch, currentBlock)

	nextSlots = getSlots(data["live_table"], valByAddMap)
	processForWhatIf(nextSlots)
	nextEpochNotMap = notificationUtils.getNotMapForElectionCheck(conn, currentEpoch, True)
	notificationsNext, watchEndListNext = processNextEpochNotifications(nextSlots, nextEpochNotMap, currentEpoch, timeLeft)

	slots = getSlots(data["table"], valByAddMap)
	epochNotMap = notificationUtils.getNotMapForElectionCheck(conn, currentEpoch, False)
	notifications = processEpochNotifications(slots, epochNotMap, currentEpoch)
	notifications.extend(notificationsNext)

	notificationsUnelectedVal = processUnelectedValNotifications(conn, epochNotMap, currentEpoch)
	notifications.extend(notificationsUnelectedVal)

	# logger.info("notifications: {}, watchEndListNext: {}".format(notifications, watchEndListNext))

	processForUnderbid(conn, currentEpoch, nextSlots, notifications, watchEndListNext, currentBlock, coinStat, timeLeft)

	if eventToUpdate:
		# logger.info("creating event: {}".format(eventToUpdate))
		auditUtils.createEvent(conn, app, eventToUpdate, currentEpoch)

	notificationUtils.batchCreateNotifications(conn, notifications)
	notificationUtils.updateEndWatchList(conn, watchEndListNext)


def processUnelectedValNotifications(conn, epochNotMap, epoch):
	validators = harmonyData.listAllUnelectedValidators(conn)
	notifications = []

	for validator in validators:
		if validator["status"]:
			addNotification(epochNotMap, notifications, hConstants.NOTIFICATION_TYPE_UNELECTED,
							validator["hPoolId"], epoch, None)

	i = 1
	valNeedingUnelectionAlert = harmonyValEvents.getValidatorsForPerfAlerts(conn)
	longUnelectedValidators = harmonyValEvents.listAllLongUnelectedValidators(conn, epoch)
	# logger.info("in processEpochNotifications - valNeedingUnelectionAlert: {}".format(valNeedingUnelectionAlert))
	for val in longUnelectedValidators:
		# logger.info("{} - processing val: {}".format(i, val))
		i +=1
		hPoolId = val["hPoolId"]
		if hPoolId not in valNeedingUnelectionAlert:
			# logger.info("no one is watching this validator, ignoring alert")
			continue

		# logger.info("adding long unelected alert for: {}".format(hPoolId))
		addNotification(epochNotMap, notifications, hConstants.NOTIFICATION_TYPE_UNELECTED_FOR_LONG,
						hPoolId, epoch, None)
		# def addNotification(notMap, notifications, notType, hPoolId, currentEpoch, value1):
		# event = (hConstants.NOTIFICATION_TYPE_SELF_BOND_REMOVED, None, hPoolId, epoch,
		# 		lastElected, None, None, None)
		# harmonyValEvents.processNotificationForLongUnelection(conn, hPoolId, epoch,
		# 		notifications, valNeedingUnelectionAlert)

	return notifications

def processNextEpochNotifications(slots, nextEpochNotMap, epoch, timeLeft):
	notifications, watchEndList = [], []
	for slot in slots:
		processForNewNextEpochNotification(nextEpochNotMap, notifications, slot, epoch)
		processForExistingNotification(nextEpochNotMap, notifications, watchEndList, slot, epoch)
		# process notifications related to epoch ending
		processForEpochEndingNotification(notifications, slot, epoch, timeLeft)

	return notifications, watchEndList


def processEpochNotifications(slots, epochNotMap, epoch):
	notifications = []

	i = 1
	for slot in slots:
		# logger.info("{} - processing slot: {}".format(i, slot))
		i +=1
		if slot["status"] == ES_NOT_ELECTED:
			addNotification(epochNotMap, notifications, hConstants.NOTIFICATION_TYPE_UNELECTED,
							slot["hPoolId"], epoch, None)
		elif slot["status"] == ES_PARTIALLY_ELECTED:
			addNotification(epochNotMap, notifications, hConstants.NOTIFICATION_TYPE_PARTIALLY_ELECTED,
							slot["hPoolId"], epoch, None)

	return notifications


# NOTIFY_DEL_PERFORMANCE = "notifyDelPerf" -- unelected .
# not elected completely, --- when new epoch comes  - slot syncer
# not elected partially --- when new epoch comes - slot syncer
# Notifications for validator elections -
# falling out of election slots - slot syncer
# , having excessively high bid - slot syncer
# , marked as in-eligible  - slot syncer
def processForNewNextEpochNotification(notMap, notifications, slot, epoch):
	if slot["status"] == ES_NOT_ELECTED:
		addNotification(notMap, notifications, hConstants.NOTIFICATION_TYPE_RISK_UNELECTED,
						slot["hPoolId"], epoch, epoch + 1)
	elif slot["status"] == ES_PARTIALLY_ELECTED:
		addNotification(notMap, notifications, hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED,
						slot["hPoolId"], epoch, epoch + 1)
	elif slot["status"] == ES_ELECTED:
		#add 1000 for rounding errors
		if slot["effectiveStake"] and slot["bid"] > slot["effectiveStake"] + 1000:
			if slot["slotDetailsPlusOne"]["status"] == ES_ELECTED:
				addNotification(notMap, notifications, hConstants.NOTIFICATION_TYPE_RISK_HIGH_BID,
								slot["hPoolId"], epoch, epoch + 1)


# process for epoch ending notifications
def processForEpochEndingNotification(notifications, slot, epoch, timeLeft):
	# logger.info("time based alert need: {}".format(timeLeft))
	if not timeLeft:
		return

	if slot["status"] == ES_NOT_ELECTED:
		notifications.append((hConstants.NOTIFICATION_TYPE_RISK_UNELECTED, None, slot["hPoolId"], epoch,
			 epoch + 1, timeLeft, None, None))
	elif slot["status"] == ES_PARTIALLY_ELECTED:
		notifications.append((hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED, None, slot["hPoolId"], epoch,
			 epoch + 1, timeLeft, None, None))
	elif slot["status"] == ES_ELECTED:
		processed = False
		#add 1000 for rounding errors
		if slot["effectiveStake"] and slot["bid"] > slot["effectiveStake"] + 1000:
			if slot["slotDetailsPlusOne"]["status"] == ES_ELECTED:
				notifications.append((hConstants.NOTIFICATION_TYPE_RISK_HIGH_BID, None, slot["hPoolId"], epoch,
					 epoch + 1, timeLeft, None, None))
				processed = True

		if not processed:
			notifications.append((hConstants.NOTIFICATION_TYPE_EPOCH_ENDING_SOON, None, slot["hPoolId"], epoch,
				 epoch + 1, timeLeft, None, None))


def processForExistingNotification(notMap, notifications, watchEndList, slot, epoch):
	processForExistingNotificationType(notMap, notifications, watchEndList, slot, epoch,
		hConstants.NOTIFICATION_TYPE_RISK_UNELECTED, ES_ELECTED,
		hConstants.NOTIFICATION_TYPE_RISK_UNELECTED_END)

	processForExistingNotificationType(notMap, notifications, watchEndList, slot, epoch,
		hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED, ES_ELECTED,
		hConstants.NOTIFICATION_TYPE_RISK_PARTIALLY_ELECTED_END)

	processForHighBidEnd(notMap, notifications, watchEndList, slot, epoch)


def processForHighBidEnd(notMap, notifications, watchEndList, slot, epoch):
	# send high bid resolved notification
	if slot["status"] == ES_ELECTED:
		if slot["bid"] <= slot["effectiveStake"]:
			notType = hConstants.NOTIFICATION_TYPE_RISK_HIGH_BID
			notKey = notType + "-" + str(slot["hPoolId"])
			if notKey not in notMap:
				return

			notification = notMap[notKey]
			addNotification(notMap, notifications, hConstants.NOTIFICATION_TYPE_RISK_HIGH_BID_END,
							slot["hPoolId"], epoch, epoch + 1)
			watchEndList.append((notification["notificationId"]))


def processForExistingNotificationType(notMap, notifications, watchEndList, slot, epoch,
		notType, counterStatus, nextNotType):

	notKey = notType + "-" + str(slot["hPoolId"])
	if notKey not in notMap:
		return

	notification = notMap[notKey]

	if slot["status"] == counterStatus:
		addNotification(notMap, notifications, nextNotType, slot["hPoolId"], epoch, epoch + 1)
		watchEndList.append((notification["notificationId"]))


def addNotification(notMap, notifications, notType, hPoolId, currentEpoch, value1):
	# logger.info("in addNotification(notMap: {}, notifications: {}, notType: {}, hPoolId: {}, currentEpoch: {}, value1: {})".format(
	# 	notMap, notifications, notType, hPoolId, currentEpoch, value1))
	notKey = notType + "-" + str(hPoolId)

	if notKey not in notMap:
		# logger.info("adding notification as not key not found: {}".format(notKey))
		notification = (notType, None, hPoolId, currentEpoch,
			 value1, None, None, None)
		notifications.append(notification)


def getSlotDetails(slots, detail):
	slotDetails = {"slotCount": 0, "status": ES_NOT_ELECTED,
				   "slotStart": 0, "slotEnd": 0}
	if not slots:
		return slotDetails

	slotCount = 1
	status = ES_ELECTED

	slotsArray = slots.split("-")

	if len(slotsArray) == 1:
		# single slot
		slotStart = int(slots)
		slotEnd = slotStart
		if slotStart > hConstants.MAX_SLOTS:
			slotCount = 0
			status = ES_NOT_ELECTED
	else:
		# multiple slots
		slotStart = int(slotsArray[0])
		slotEnd = int(slotsArray[1])
		slotCount = slotEnd - slotStart + 1
		if slotStart > hConstants.MAX_SLOTS:
			slotCount = 0
			status = ES_NOT_ELECTED
		elif slotEnd == hConstants.MAX_SLOTS:
			if detail["slotsRequested"] != slotCount:
				status = ES_PARTIALLY_ELECTED

	slotDetails["slotCount"] = slotCount
	slotDetails["status"] = status
	slotDetails["slotStart"] = slotStart
	slotDetails["slotEnd"] = slotEnd

	return slotDetails


def processForUnderbid(conn, epoch, slotList, notifications, watchEndList, currentBlock, coinStat, timeLeft):
	if not harmonyUtils.isEnoughDataForUnderbid(coinStat, epoch, currentBlock):
		return

	totalUnderbid = 0
	for slot in slotList:
		slotDetails = slot["slotDetails"]
		# logger.info("processing slot: {} for #: {}, slot: {}".format(slotDetails["slotStart"], slotDetails["slotCount"], slot))
		if slotDetails["slotStart"] > hConstants.MAX_SLOTS:
			break
		elif slotDetails["status"] != ES_ELECTED:
			break
		elif int(slot["effectiveStake"]) > int(slot["bid"]) + 10:
			# logger.info("adding {} as underbid for bid: {} and eff state: {}, totalUnderbid: {}".format(
			# 	slotDetails["slotCount"], slot["bid"], slot["effectiveStake"], totalUnderbid))
			totalUnderbid += slotDetails["slotCount"]

	# totalUnderbid = 0
	# logger.info("totalUnderbid :".format(totalUnderbid))
	currentUnderbid = notificationUtils.isNotForUnderBidPresent(conn, epoch,
		hConstants.NOTIFICATION_TYPE_UNDER_BID_OPP)
	# logger.info("currentUnderbid: ".format(currentUnderbid))
	if totalUnderbid > 0:
		# logger.info("assessing adding new underbid opp")
		if not currentUnderbid or timeLeft:
			# logger.info("adding new underbid opp")
			notification = (hConstants.NOTIFICATION_TYPE_UNDER_BID_OPP, None, None, epoch,
				 epoch + 1, totalUnderbid, None, None)
			notifications.append(notification)
	else:
		# logger.info("assessing adding new NO underbid opp")
		if currentUnderbid:
			# logger.info("adding new not underbid opp")
			notification = (hConstants.NOTIFICATION_TYPE_UNDER_BID_OPP_END, None, None, epoch,
				 epoch + 1, None, None, None)
			notifications.append(notification)
			watchEndList.append((currentUnderbid["notificationId"]))


def processForWhatIf(slotList):
	for slot in slotList:
		slot["slotDetailsPlusOne"] = getWhatIfImpact(slot, slotList, 1)


def getWhatIfImpact(data, slotList, count):
	newSlotCount = data["slotsRequested"] + count
	newSlotEnd = data["slotDetails"]["slotEnd"] + count
	newBid = data["actualStake"] / newSlotCount

	newSlot = {"slotCount": newSlotCount, "status": data["slotDetails"]["status"],
	  "slotStart": data["slotDetails"]["slotStart"], "slotEnd": newSlotEnd,
	  "bid": newBid, "slotRange": str(data["slotDetails"]["slotStart"]) + "-" + str(newSlotEnd)}

	for otherSlot in slotList:
		if newBid > otherSlot["slotDetails"]["bid"]:
			if otherSlot["slotDetails"]["slotStart"] > newSlot["slotStart"]:
				newSlot["slotStart"] = otherSlot["slotDetails"]["slotStart"] - data["slotsRequested"]
			else:
				newSlot["slotStart"] = otherSlot["slotDetails"]["slotStart"]

			newSlot["slotEnd"] = newSlot["slotStart"] + newSlotCount - 1

			if newSlot["slotStart"] > hConstants.MAX_SLOTS:
				newSlot["status"] = ES_NOT_ELECTED
			elif newSlot["slotEnd"] > hConstants.MAX_SLOTS:
				newSlot["status"] = ES_PARTIALLY_ELECTED
			else:
				newSlot["status"] = ES_ELECTED

			if newSlot["slotStart"] == newSlot["slotEnd"]:
				newSlot["slotRange"] = newSlot["slotStart"]
			else:
				newSlot["slotRange"] = str(newSlot["slotStart"]) + "-" + str(newSlot["slotEnd"])

			break

	return newSlot


def getSlots(slotsData, valByAddMap):
	slotsList = []

	i = 1
	for slot in slotsData:
		# logger.info(slot)
		address = slot["address"]
		if address not in valByAddMap:
			continue

		validator = valByAddMap[address]
		details = {}

		details["index"] = i
		details["hPoolId"] = validator["hPoolId"]
		details["slot"] = slot["slot"]
		details["address"] = slot["address"]
		details["bid"] = commonUtils.divideByTenPower18(slot["bid"])
		if "effective_stake" in slot:
			details["effectiveStake"] = commonUtils.divideByTenPower18(slot["effective_stake"])
		else:
			details["effectiveStake"] = None
		details["totalStake"] = commonUtils.divideByTenPower18(slot["total_stake"])
		details["actualStake"] = validator["totalStaked"]
		details["slotsRequested"] = round(validator["totalStaked"] / details["bid"])

		currentSlot = getSlotDetails(slot["slot"], details)
		details["slotDetails"] = currentSlot
		details["slotDetails"]["bid"] = details["bid"]
		details["totalSlots"] = currentSlot["slotCount"]
		details["status"] = currentSlot["status"]

		slotsList.append(details)
		# del valByAddMap[address]
		i += 1

	# logger.info("unelected validators: {}".format(valByAddMap))
	# , valByAddMap.values()
	return slotsList


def getEpochEndTimeLeftForEpochAlert(conn, coinStat, currentEpoch, currentBlock):
	# logger.info("in getEpochEndTimeLeftForEpochAlert")
	dbEpoch = coinStat["currentEpoch"]
	epochLastBlock = coinStat["epochLastBlock"]
	blockTime = hConstants.H_BLOCK_TIME

	if dbEpoch != currentEpoch:
		# for whatever reason db and network epoch are not in sync.
		# epoch alerts are needed at this time
		# logger.info("in getEpochEndTimeLeftForEpochAlert: epochs are different. skipping")
		return None, None

	blocksLeft = epochLastBlock - currentBlock
	timeLeft = blocksLeft * blockTime

	if timeLeft > hConstants.EPOCH_ALERT_1_HR_MINIMUM_TIME_LEFT:
		# logger.info("in getEpochEndTimeLeftForEpochAlert: more than 1 hour remains. skipping")
		return None, None

	lastHourlyEventEpoch = commonUtils.getEventDescriptionInt(conn, hConstants.EPOCH_ALERT_1_HR_EVENT)
	if not lastHourlyEventEpoch or lastHourlyEventEpoch < currentEpoch:
		# time to send 1 hr alert
		# logger.info("in getEpochEndTimeLeftForEpochAlert: sending 1 hr alert")
		return 60, hConstants.EPOCH_ALERT_1_HR_EVENT

	if timeLeft > hConstants.EPOCH_ALERT_30_MIN_MINIMUM_TIME_LEFT:
		# logger.info("in getEpochEndTimeLeftForEpochAlert: time left btw 30 mins and 1 hr. skipping")
		return None, None

	last30MinEventEpoch = commonUtils.getEventDescriptionInt(conn, hConstants.EPOCH_ALERT_30_MIN_EVENT)
	if not last30MinEventEpoch or last30MinEventEpoch < currentEpoch:
		# time to send 1 hr alert
		# logger.info("in getEpochEndTimeLeftForEpochAlert: sending 30 min alert")
		return 30, hConstants.EPOCH_ALERT_30_MIN_EVENT

	if timeLeft > hConstants.EPOCH_ALERT_15_MIN_MINIMUM_TIME_LEFT:
		# logger.info("in getEpochEndTimeLeftForEpochAlert: time left btw 15 and 30 mins. skipping")
		return None, None

	last15MinEventEpoch = commonUtils.getEventDescriptionInt(conn, hConstants.EPOCH_ALERT_15_MIN_EVENT)
	if not last15MinEventEpoch or last15MinEventEpoch < currentEpoch:
		# time to send 1 hr alert
		# logger.info("in getEpochEndTimeLeftForEpochAlert: sending 15 min alert")
		return 15, hConstants.EPOCH_ALERT_15_MIN_EVENT

	# this means alerts have been processed for all time frames
	# logger.info("in getEpochEndTimeLeftForEpochAlert: all alerts already sent. skipping")
	return None, None