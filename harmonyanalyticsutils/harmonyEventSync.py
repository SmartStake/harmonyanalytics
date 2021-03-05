import datetime
import sys
import time

from requests import Session

import commonUtils
import constants
import harmonyNetworkUtils
import logUtil

if len(sys.argv) < 3:
	raise Exception("correct syntax is: python harmonyEventsSync dev/prod logsPath")

today = datetime.date.today()

logger = logUtil.l()
attempts = 1

def processEvents():
	global attempts
	logger.info("starting processing")

	startBlockHeight, endBlockHeight, more = commonUtils.getBlockHeightRange(
		constants.eventSyncBlockHeightUrl, constants.EVENT_SYNC_MAX_LIMIT)

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
		logger.info("processing block: {}".format(blockNum))
		index = 0
		# logger.info("processing events transaction for block: {}, and index: {}, is: {}".format(blockNum, index, transaction))
		while True and index < 1000:
			transaction = commonUtils.getHarmonyResultDataFromPost(session, constants.STAKING_TRANSACTION_URL, [blockNum, index])
			# logger.info(str(attempts) + " - " + str(blockCount) + " transaction for block: {}, and index: {}, is: {}".format(blockNum, index, transaction))
			if transaction:
				event = harmonyNetworkUtils.processStakingTransaction(session, transaction)
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
	# logger.info(reqDetails)

	commonUtils.postReq(constants.syncEventsUrl, reqDetails)

	if more and attempts < constants.EVENT_SYNC_MAX_LOOPS:
		attempts += 1
		time.sleep(constants.SLEEP_TIME_FOR_MORE)
		logger.info(str(attempts) + " - starting new cycle")
		processEvents()


startTime = int(time.time())
processEvents()
logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
