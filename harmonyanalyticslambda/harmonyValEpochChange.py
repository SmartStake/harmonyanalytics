import logging

import commonUtils
import constants
import hConstants
import harmonyBlsKeys
import harmonyData
import harmonyEvents
import notificationUtils
import propUtils
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = constants.HARMONY


def processEpochChange(conn, app, currentEpoch, currentEpochPerfData):
	notificationUtils.resetWatchEvents(conn, currentEpoch)
	processPreviousEpochChange(conn, app, currentEpoch, currentEpochPerfData)

	if propUtils.isTrue(conn, app, "harmonyEnableVersionAlerts"):
		logger.info("processing for node version related alerts")
		harmonyBlsKeys.processKeyNodeVersionAlert(conn, app)
		logger.info("after processing for node version related alerts")

	conn.commit()



def processPreviousEpochChange(conn, app, currentEpoch, currentEpochPerfData):
	logger.info("epoch has changed. calculating APR for previous epoch")
	previousEpoch = currentEpoch - 1
	prevEpochPerfData = harmonyData.listHPoolPerfByEpoch(conn, app, previousEpoch, constants.H_EPOCH_MODE)
	startEpoch = getStartEpoch(currentEpoch, hConstants.H_EPOCHS_FOR_AVERAGE)
	avgPerfList = harmonyData.listHPoolPerfByEpochRange(conn, app, startEpoch, previousEpoch, constants.H_EPOCH_MODE)
	avgPerfMap = commonUtils.getMapFromList(avgPerfList, "hPoolId")
	# logger.info(avgPerfMap)

	currentEpochPerfMap = commonUtils.getMapFromList(currentEpochPerfData, "hPoolId")

	for prevEpochValidator in prevEpochPerfData:
		hPoolId = prevEpochValidator["hPoolId"]

		# logger.info(prevEpochValidator)
		avgPerf = avgPerfMap[hPoolId]
		# logger.info(avgPerf)
		avgApr, avgNetApr, avgEri, avgSigned, avgToSign, avgSignPer, electionRate = None, None, None, None, None, None, None
		if avgPerf["avgApr"]:
			avgApr, avgNetApr, avgEri = getAvgApr(prevEpochValidator, avgPerf, startEpoch, previousEpoch)

		if avgPerf["avgSignPer"]:
			avgSigned = avgPerf["avgSigned"]
			avgToSign = avgPerf["avgToSign"]
			avgSignPer = avgPerf["avgSignPer"]
			timesElected = avgPerf["timesElected"]
			if timesElected:
				electionRate = (timesElected * 100 / hConstants.H_EPOCHS_FOR_AVERAGE)
				# logger.info("electionRate {} timesElected {} * 100 / hConstants.H_EPOCHS_FOR_AVERAGE {})"
				#             .format(electionRate, timesElected, hConstants.H_EPOCHS_FOR_AVERAGE))
		feeChanged, prevFee = None, None
		if hPoolId in currentEpochPerfMap:
			feeChanged, prevFee = processFeeChange(conn, prevEpochValidator, currentEpochPerfMap[hPoolId], currentEpoch)
		updatePoolPrevEpochApr(conn, prevEpochValidator, avgApr, avgNetApr, avgEri, avgSigned, avgToSign, avgSignPer, currentEpoch, feeChanged, prevFee, electionRate)


	conn.commit()
	# logger.info("creating pool history")
	createPoolHistory(conn, currentEpoch)
	# logger.info("after creating pool history")


def processFeeChange(conn, prevEpochValidator, currentEpochValidator, currentEpoch):
	# logger.info("in processFeeChange for prevEpochValidator: {}, currentEpochValidator: {}, currentEpoch: {}".format(
	#     prevEpochValidator, currentEpochValidator, currentEpoch))

	feeChanged, oldFee = None, None
	if prevEpochValidator["fee"] != currentEpochValidator["fee"]:
		# logger.info("fee is different")
		oldFee = prevEpochValidator["fee"]
		if prevEpochValidator["fee"] > currentEpochValidator["fee"]:
			# logger.info("fee has decreased")
			eventType = hConstants.H_EVENT_FEE_DECREASE
			change = str((prevEpochValidator["fee"] * 100)) + " to " + str((currentEpochValidator["fee"] * 100))
			# logger.info("{} - fee has decreased for validator - {}".format(prevEpochValidator["hPoolId"], change))
		else:
			# logger.info("fee has increased")
			eventType = hConstants.H_EVENT_FEE_INCREASE
			prevFee = round(prevEpochValidator["fee"] * 100, 2)
			currentFee = round(currentEpochValidator["fee"] * 100, 2)
			feeChanged = str(prevFee) + "% to " + str(currentFee) + "%"
			# logger.info("{} - fee has increased for validator - {}".format(prevEpochValidator["hPoolId"], feeChanged))

		# logger.info("creating fee event")
		harmonyEvents.createFeeEvent(conn, eventType, prevEpochValidator["hPoolId"],
									 currentEpoch, currentEpochValidator["fee"])

	return feeChanged, oldFee


def updatePoolPrevEpochApr(conn, validator, avgApr, avgNetApr, avgEri, avgSigned, avgToSign, avgSignPer, currentEpoch, feeChanged, prevFee, electionRate):
	sql = "update " + tables.hpool
	sql += " set prevEpochApr=%s, prevEpochNetApr=%s, prevEpochEri=%s, "
	sql += " avgApr=%s, avgNetApr=%s, avgEri=%s, "
	sql += " avgSigned = %s, avgToSign = %s, avgSignPer=%s, electionRate = %s "

	if feeChanged:
		sql += " , feeChangedEpoch=%s, feeChangedDesc=%s, prevFee=%s "

	sql += " where hPoolId = %s "

	# logger.info(sql)

	if feeChanged:
		# logger.info("processing fee changed")
		args = (validator["apr"], validator["netApr"], validator["eri"],
				avgApr, avgNetApr, avgEri,
				avgSigned, avgToSign, avgSignPer, electionRate,
				currentEpoch, feeChanged, prevFee,
				validator["hPoolId"])
		# logger.info(args)
	else:
		args = (validator["apr"], validator["netApr"], validator["eri"],
				avgApr, avgNetApr, avgEri,
				avgSigned, avgToSign, avgSignPer, electionRate,
				validator["hPoolId"])
	# logger.info(args)
	conn.cursor().execute(sql, args)


def getAvgApr(validator, avgPerf, startEpoch, previousEpoch):
	# logger.info(avgPerf)
	minEpoch = avgPerf["oldestEpoch"]
	epochsPresent = avgPerf["epochsPresent"]

	if startEpoch > minEpoch:
		# this validator was not elected at the start of range
		startEpoch = minEpoch

	epochRange = previousEpoch - startEpoch + 1

	if epochRange == 0:
		# logger.info("epoch range is 0, skipping apr calculations")
		return 0

	avgApr = avgPerf["avgApr"] * avgPerf["epochsPresent"] / epochRange
	avgNetApr = avgApr * (1 - float(validator["fee"]))

	avgEri = None
	if avgPerf["avgEri"]:
		avgEri = avgPerf["avgEri"] * avgPerf["epochsPresent"] / epochRange

	# logger.info("avg apr details are: avgApr - {}, avgNetApr - {}, epochRange - {}, avgEri - {}".format(
	#     avgApr, avgNetApr, epochRange, avgEri))

	return avgApr, avgNetApr, avgEri


def createPoolHistory(conn, epochNumber):
	sql = "insert into " + tables.hhistory
	sql += " (poolId, epoch, dataType, value1, value2, "
	sql += " value3, value4, value5, value6, value7) "
	sql += " select hPoolId, " + str(epochNumber) + ", '"
	sql += constants.H_HISTORY_VALIDATOR_PERF + "', avgApr, "
	sql += " avgNetApr, avgEri, avgSigned, avgToSign, avgSignPer, electionRate "
	sql += " from " + tables.hpool
	# logger.info(sql)

	conn.cursor().execute(sql)
	conn.commit()


def getStartEpoch(epoch, eRange):
	startEpoch = epoch - eRange

	if startEpoch < hConstants.H_FIRST_EPOCH:
		startEpoch = hConstants.H_FIRST_EPOCH

	return startEpoch


