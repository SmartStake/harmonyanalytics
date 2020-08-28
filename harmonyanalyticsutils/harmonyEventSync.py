import datetime
import sys
import time

from requests import Session

import commonUtils
import constants
import logUtil

today = datetime.date.today()

logger = logUtil.l()
attempts = 1

def processEvents():
	global attempts
	logger.info("starting processing")

	startBlockHeight, endBlockHeight, more = commonUtils.getBlockHeightRange(
		constants.eventSyncBlockHeightUrl, constants.MAX_LIMIT_EVENT_SYNC)

	if startBlockHeight is None:
		logger.info("starting block obtained is None. Exiting")
		raise Exception("Starting block obtained is None. Exiting")

	session = Session()
	allEvents = []
	blockCount = 0
	for blockNum in range(startBlockHeight, endBlockHeight):
		blockCount += 1

		# if len(allEvents) > 1:
		# 	break
		# logger.info("processing block: {}".format(blockNum))
		index = 0
		while True and index < 1000:
			transaction = commonUtils.getHarmonyResultDataFromPost(session, constants.STAKING_TRANSACTION_URL, [blockNum, index])

			logger.info(str(attempts) + " - " + str(blockCount) + " transaction for block: {}, and index: {}, is: {}".format(blockNum, index, transaction))
			if transaction:
				event = processTransaction(session, transaction)
				if event is not None:
					allEvents.append(event)
			else:
				# logger.info("ending transaction processing as no more transaction were found")
				break
				# details = processBlockEvent(event)
				# allEvents.append(details)
			index += 1

	logger.info("processed all events")

	reqDetails = {"type": "eventsSync", "blockHeight": endBlockHeight,
				  "startBlockHeight": startBlockHeight, "events": allEvents,}
	logger.info(reqDetails)

	commonUtils.postReq(constants.syncEventsUrl, reqDetails)

	if more and attempts < constants.EVENT_SYNC_MAX_LOOPS:
		attempts += 1
		time.sleep(constants.SLEEP_TIME_FOR_MORE)
		logger.info(str(attempts) + " - starting new cycle")
		processEvents()


def processTransaction(session, transaction):
	details = {"type": transaction["type"], "blockNumber": transaction["blockNumber"],
		"epochTimestamp": transaction["timestamp"], "txHash": transaction["hash"]}

	if transaction["type"] == constants.H_EVENT_DELEGATE or transaction["type"] == constants.H_EVENT_UNDELEGATE:
		details["address"] = transaction["msg"]["delegatorAddress"]
		details["validatorAddress"] = transaction["msg"]["validatorAddress"]
		details["amount"] = commonUtils.getHarmonyCoins(transaction["msg"]["amount"])
	elif transaction["type"] == constants.H_EVENT_COLLECT_REWARDS:
		details["address"] = transaction["msg"]["delegatorAddress"]
		amount = getAmountFromTransactionReceipt(session, transaction["hash"])
		if amount is None:
			return None
		details["amount"] = amount
	elif transaction["type"] == constants.H_EVENT_EDIT_VALIDATOR:
		details["address"] = transaction["msg"]["validatorAddress"]
		details["validatorAddress"] = transaction["msg"]["validatorAddress"]
		details["msg"] = transaction["msg"]
	else:
		return None

	logger.info("processed event is: {}".format(details))
	return details


def getAmountFromTransactionReceipt(session, txHash):
	transactionReceipt = commonUtils.getHarmonyResultDataFromPost(session, constants.TRANSACTION_RECEIPT_URL, [txHash])
	logger.info("transaction receipt for {}, is: {}".format(txHash, transactionReceipt))

	if not transactionReceipt or "status" not in transactionReceipt:
		logger.info(" transactionReceipt is None. not returning claim rewards amount")
		return None

	if transactionReceipt["status"] != 1:
		logger.info(str(transactionReceipt["status"]) + " - status is not 1. not returning claim rewards amount")
		return None

	if len(transactionReceipt["logs"]) == 0:
		logger.info("logs are empty. not returning claim rewards amount")
		return None

	data = transactionReceipt["logs"][0]["data"]

	try:
		intData = int(data, 16)
		amount = commonUtils.getHarmonyCoins(intData)
	except OverflowError:
		logger.info("OverflowError - error occurred processing: {}".format(data))
		return None
	except ValueError:
		logger.info("ValueError - error occurred processing: {}".format(data))
		return None

	logger.info("amount from - {} is: {}".format(data, amount))
	return amount


if len(sys.argv) < 2:
	raise Exception("correct syntax is: python3.7 harmonyEventsSync dev/prod logsPath")

startTime = int(time.time())
processEvents()
logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
