import datetime
import logging
import time

import auditUtils
import commonUtils
import constants
import eventName
import hConstants
import harmonyUtils
import notificationUtils
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = constants.HARMONY


def blsKeySync(conn, app, data, event):
	logger.info("in blsKeySync")
	startTime = datetime.datetime.now()

	blockNumber = processShards(conn, data["shardDetails"])

	processKeyInserts(conn, data["inserts"])
	processKeyPerf(conn, data["blsPerfData"], data["currentEpoch"], blockNumber)

	auditUtils.createEvent(conn, app, eventName.syncHarmonyBlsKeys)
	auditUtils.audit(conn, app, event, eventName.syncHarmonyBlsKeys, "service", startTime)

	logger.info("processing finished")


def processKeyPerf(conn, perfData, currentEpoch, currentBlock):
	logger.info("processing key perf")
	if not perfData:
		return

	badKeyMap = notificationUtils.getKeyMapForBadPerfCheck(conn, currentEpoch,
			hConstants.NOTIFICATION_TYPE_KEY_PERF_BAD)
	goodKeyMap = notificationUtils.getKeyMapForGoodPerfCheck(conn, currentEpoch,
			hConstants.NOTIFICATION_TYPE_KEY_PERF_BAD)

	logger.info("processing perfData: {}".format(len(perfData)))
	keyPerfInserts, notifications, watchEndList = [], [], []

	for keyPerf in perfData:
		# logger.info("inserting key perf: {}".format(keyPerf))
		record = (keyPerf["blsKey"], keyPerf["epochNumber"], keyPerf["effectiveStake"],
				  keyPerf["rawStake"], keyPerf["groupPercentStake"], keyPerf["overallPercentStake"],
				  keyPerf["groupPercentReward"], keyPerf["overallPercentReward"], keyPerf["reward"],
				  keyPerf["groupRewardRatio"], keyPerf["isBadPerf"], keyPerf["keyPerfIndex"],
				  int(time.time()))
		keyPerfInserts.append(record)
		processNotificationsForBadPerf(keyPerf, badKeyMap, notifications)
		processNotificationsForGoodPerf(keyPerf, goodKeyMap, notifications, watchEndList)

	batchCreateKeyPerf(conn, keyPerfInserts)
	# logger.info("creating bls key perf notifications for: {}".format(notifications))

	if len(notifications) > 0 or len(watchEndList) > 0:
		coinStat = commonUtils.getCoinStat(conn, app)
		# logger.info("shardDetails: {}".format(shardDetails))
		# currentBlock = shardDetails["blockNumber"]
		if harmonyUtils.isEnoughDataForBlsKeys(coinStat, currentEpoch, currentBlock):
			logger.info("enough blocks have passed for bls key notifications")
			notificationUtils.batchCreateNotifications(conn, notifications)
			notificationUtils.updateEndWatchList(conn, watchEndList)

	conn.commit()


def batchCreateKeyPerf(conn, keyPerfInserts):
	sql = "insert into " + tables.hkeyperf
	sql += " (blsKey, epochNumber, effectiveStake, rawStake, "
	sql += " groupPercentStake, overallPercentStake, "
	sql += " groupPercentReward, overallPercentReward, reward, "
	sql += " groupRewardRatio, isBadPerf, keyPerfIndex, syncTime) "
	sql += " values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "

	# # logger.info(sql)
	# logger.info("processing key perf data: {}".format(keyPerfInserts))
	createdCount = conn.cursor().executemany(sql, keyPerfInserts)
	logger.info("batchCreateKey requested - {}, update performed - {}".format(
		len(keyPerfInserts), createdCount))



def processKeyInserts(conn, keys):
	logger.info("processing key inserts")
	if not keys:
		return

	logger.info("processing keys: {}".format(len(keys)))
	keyInserts = []
	for key in keys:
		# logger.info("inserting key: {}".format(key))
		record = (key["blsKey"], key["shardId"], key["hPoolId"])
		keyInserts.append(record)

	batchCreateKey(conn, keyInserts)
	conn.commit()


def batchCreateKey(conn, keyInserts):
	sql = "insert into " + tables.hblskey
	sql += " (blsKey, shardId, hPoolId) "
	sql += " values(%s, %s, %s) "

	# logger.info(sql)
	# logger.info("processing keys: {}".format(keyInserts))
	createdCount = conn.cursor().executemany(sql, keyInserts)
	logger.info("batchCreateKey requested - {}, update performed - {}".format(
		len(keyInserts), createdCount))


def processShards(conn, shardDetails):
	logger.info("processing shards")
	if not shardDetails:
		return None

	# shards = []
	# shards.append(shardDetails["shard0"])

	logger.info("processing shards: {}".format(len(shardDetails)))
	shardInserts = []
	blockNumber = None
	for key in shardDetails:
		detail = shardDetails[key]
		# logger.info("{} - inserting shard details: {}".format(key, detail))
		if detail["shardId"] == 0:
			blockNumber = detail["blockNumber"]

		crossLinkDelay = detail["blockNumber"] - detail["crossLinkBlock"]
		isDelayedInd = False
		if crossLinkDelay > constants.CROSS_LINK_DELAY_TOLERANCE:
			isDelayedInd = True

		record = (detail["epochNumber"], detail["shardId"], detail["slots"],
				  detail["blockNumber"], crossLinkDelay, detail["crossLinkBlock"],
				  isDelayedInd, int(time.time()))
		shardInserts.append(record)

	batchCreateShardDelay(conn, shardInserts)
	conn.commit()
	return blockNumber


def batchCreateShardDelay(conn, shardInserts):
	sql = "insert into " + tables.hsharddelay
	sql += " (epochNumber, shardId, slots, blockNumber,  "
	sql += " crossLinkDelay, crossLinkBlock, isDelayedInd, syncTime) "
	sql += " values(%s, %s, %s, %s, %s, %s, %s, %s) "

	createdCount = conn.cursor().executemany(sql, shardInserts)
	logger.info("batchCreateShardDelay requested - {}, update performed - {}".format(
		len(shardInserts), createdCount))


def processNotificationsForBadPerf(keyPerf, badKeyMap, notifications):
	if keyPerf["isBadPerf"] == "False":
		return

	key = keyPerf["blsKey"]
	if key not in badKeyMap:
		return

	valKey = badKeyMap[key]
	event = (hConstants.NOTIFICATION_TYPE_KEY_PERF_BAD, None, valKey["hPoolId"],
			 keyPerf["epochNumber"], keyPerf["keyPerfIndex"], keyPerf["shardId"], key, None)

	notifications.append(event)


def processNotificationsForGoodPerf(keyPerf, goodKeyMap, notifications, watchEndList):
	if keyPerf["isBadPerf"] == "True":
		return

	key = keyPerf["blsKey"]
	if key not in goodKeyMap:
		return

	valKey = goodKeyMap[key]
	event = (hConstants.NOTIFICATION_TYPE_KEY_PERF_GOOD, None, valKey["hPoolId"],
			 keyPerf["epochNumber"], keyPerf["keyPerfIndex"], keyPerf["shardId"], key, None)

	notifications.append(event)
	watchEndList.append((valKey["notificationId"]))

