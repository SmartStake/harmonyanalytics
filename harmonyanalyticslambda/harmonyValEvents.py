import logging

import dbUtil
import hConstants
import notificationUtils
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# validator low signage, - val sync
# validator low rewards, - val sync
# NOTIFY_VALIDATOR_PERF = "notifyValPerf" - val sync

def generateValSyncEvents(conn, currentEpoch, enoughDataForCurrentApr):
	# get validators with low sign - 98% or less
	logger.info("in generateValSyncEvents : currentEpoch:{}, enoughDataForCurrentApr: {}".format(currentEpoch, enoughDataForCurrentApr))
	events = []
	watchEndList = []

	eventsLowSign = processValidatorsWithBadPerf(conn, currentEpoch,
				hConstants.NOTIFICATION_TYPE_LOW_SIGN, "signPer")
	events.extend(eventsLowSign)

	eventsGoodSign, watchEndGoodSign = processValidatorsWithImprovedPerf(conn, currentEpoch,
				hConstants.NOTIFICATION_TYPE_LOW_SIGN, hConstants.NOTIFICATION_TYPE_GOOD_SIGN, "signPer")
	events.extend(eventsGoodSign)
	watchEndList.extend(watchEndGoodSign)

	if enoughDataForCurrentApr:
		eventsLowEri = processValidatorsWithBadPerf(conn, currentEpoch,
							hConstants.NOTIFICATION_TYPE_LOW_ERI, "eri")
		events.extend(eventsLowEri)

		eventsGoodEri, watchEndGoodEri = processValidatorsWithImprovedPerf(conn, currentEpoch,
					hConstants.NOTIFICATION_TYPE_LOW_ERI, hConstants.NOTIFICATION_TYPE_GOOD_ERI, "eri")
		events.extend(eventsGoodEri)
		watchEndList.extend(watchEndGoodEri)

	notificationUtils.batchCreateNotifications(conn, events)
	notificationUtils.updateEndWatchList(conn, watchEndList)
	conn.commit()


def processValidatorsWithImprovedPerf(conn, currentEpoch, currentNotType, newNotType, dataElement):
	validators = notificationUtils.listValidatorsWithImprovedPerf(conn, currentEpoch, currentNotType)

	events = []
	watchEndList = []
	for validator in validators:
		event = (newNotType, None, validator["hPoolId"], currentEpoch,
				 validator[dataElement], None, None, None)
		events.append(event)
		watchEndList.append((validator["notificationId"]))

	return events, watchEndList


def processValidatorsWithBadPerf(conn, currentEpoch, notType, dataElement):
	validators = notificationUtils.listValidatorsWithBadPerf(conn, currentEpoch, notType)

	events = []
	for validator in validators:
		event = (notType, None, validator["hPoolId"], currentEpoch,
				 validator[dataElement], None, None, None)
		events.append(event)

	return events


def checkValidatorDetails(conn, currentData, validator, currentEpoch):
	checkSelfStake(conn, currentData, validator, currentEpoch)


def checkSelfStake(conn, currentData, validator, currentEpoch):
	# logger.info("validator: {}".format(validator))
	if validator["selfStake"] >= 10000:
		return

	# logger.info("{} - validator self stake is less than 10k".format(validator["name"]))

	if currentData["selfStake"] < 10000:
		return

	# logger.info("{} - validator has removed self stake".format(validator["name"]))
	event = (hConstants.NOTIFICATION_TYPE_SELF_BOND_REMOVED, None, currentData["hPoolId"], currentEpoch,
			 validator["selfStake"], None, None, None)
	notificationUtils.batchCreateNotifications(conn, [event])


# def processNotificationForLongUnelection(conn, hPoolId, epoch, notifications, validators):
# 	logger.info("{} - processing validator for long unelection alert".format(hPoolId))
# 	lastElected = getLastElectedEpoch(conn, hPoolId, epoch)
#
# 	if not lastElected:
# 		logger.info("validator was not elected recently, ignoring alert")
# 		return
#
# 	if lastElected > epoch - 7:
# 		logger.info("validator was elected recently, ignoring alert")
#
# 	logger.info("validator has been unelected for more than 7 epochs")
#
# 	event = (hConstants.NOTIFICATION_TYPE_SELF_BOND_REMOVED, None, hPoolId, epoch,
# 			lastElected, None, None, None)
# 	notifications.batchCreateNotifications(conn, [event])
#

def getValidatorsForPerfAlerts(conn):
	userPrefs = notificationUtils.listNotificationUsersForPerf(conn)
	favVals = set()
	for pref in userPrefs:
		pools = pref["favPools"]
		if pools:
			poolList = pools.split(",")
			for pool in poolList:
				favVals.add(int(pool))

	logger.info("list of all validators for perf alerts: {}".format(favVals))
	return favVals


# def getLastElectedEpoch(conn, hPoolId, epoch):
# 	sql = "select max(epochNumber) as lastElected from "
# 	sql += tables.hpoolperf + " where mode='EPOCH' and status='Elected' "
# 	sql += " and hPoolId = %s and epochNumber > %s - 30 "
#
# 	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (hPoolId, epoch))
#
# 	if not record:
# 		return None
#
# 	return record["lastElected"]

# def getLastElectedEpoch(conn, hPoolId, epoch):
# 	sql = "select max(epochNumber) as lastElected from "
# 	sql += tables.hpoolperf + " where mode='EPOCH' and status='Elected' "
# 	sql += " and hPoolId = %s and epochNumber > %s - 30 "
#
# 	record = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (hPoolId, epoch))
#
# 	if not record:
# 		return None
#
# 	return record["lastElected"]

def listAllLongUnelectedValidators(conn, epoch):
	sql = " select hPoolId, "
	sql += " count(case when status='Elected' then 1 else null end) as recentlyElected, "
	sql += " max(case when status='Elected' then epochNumber else null end) as recentElection "
	sql += " from " + tables.hpoolperf + " hp "
	sql += " where mode='EPOCH' "
	sql += " and epochNumber > %s "
	sql += " and hPoolId in (select p.hPoolId from  " + tables.hpool + " p "
	sql += " 	where isEverElected='True' and status != 'Elected') "
	sql += " group by hPoolId "
	sql += " having recentlyElected > 0 and recentElection < %s "

	logger.info(sql)
	data = dbUtil.listResultsWithConn(sql, conn, (epoch - 30, epoch - 7))
	return data


