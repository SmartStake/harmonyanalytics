import datetime
import logging

import auditUtils
import commonUtils
import constants
import eventName
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = constants.HARMONY


def epochSignSync(conn, app, data, event):
	logger.info("in blsKeySync")
	startTime = datetime.datetime.now()

	allData = data["allData"]

	currentTime = datetime.datetime.now()
	epochSignUpdates = []
	epochSignSummaryUpdates = []

	maxEpoch, signRate = 0, 0
	for epochData in allData:
		logger.info("processing epoch: {}".format(epochData["epoch"]))
		summary = (epochData["signRate"], epochData["epoch"])
		epochSignSummaryUpdates.append(summary)

		if epochData["epoch"] > maxEpoch:
			signRate = epochData["signRate"]
			maxEpoch = epochData["epoch"]

		for validator in epochData["validators"]:
			valSign = (validator["signed"], validator["askedToSign"], validator["signPer"],
					currentTime, currentTime.strftime('%s'), epochData["epoch"], validator["hPoolId"])
			epochSignUpdates.append(valSign)

	batchUpdateEpochSigns(conn, epochSignUpdates)
	batchUpdateHistory(conn, epochSignSummaryUpdates)
	updateSignRate(conn, signRate, app)

	epoch = data["epoch"]
	commonUtils.updateSyncStatus(conn, app, constants.SYNC_STATUS_EPOCH_FOR_SIGN, None, epoch)
	auditUtils.createEvent(conn, app, eventName.syncEpochSign)
	auditUtils.audit(conn, app, event, eventName.syncEpochSign, "service", startTime)

	logger.info("processing finished")


def updateSignRate(conn, signRate, symbol):
	sql = "update " + tables.coinstat
	sql += " set signRate=%s "
	sql += " where symbol=%s"
	# logger.info(sql)
	conn.cursor().execute(sql, (signRate, symbol))


def batchUpdateEpochSigns(conn, updates):
	sql = "update " + tables.hpoolperf
	sql += " set signed=%s, askedToSign=%s, signPer=%s, "
	sql += " syncTime=%s, syncEpochTime=%s "
	sql += " where mode='EPOCH' and epochNumber=%s and hpoolId=%s"

	# logger.info(sql)
	count = conn.cursor().executemany(sql, updates)
	logger.info("updates: {}".format(count))


def batchUpdateHistory(conn, updates):
	sql = "update " + tables.hhistory
	sql += " set value9 = %s "
	sql += " where epoch = %s and dataType='Network'"

	# logger.info(sql)
	count = conn.cursor().executemany(sql, updates)
	logger.info("updates: {}".format(count))

