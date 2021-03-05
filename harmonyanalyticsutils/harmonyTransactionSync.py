import datetime
import sys
import time

from requests import Session

import commonUtils
import constants
import harmonyNetworkUtils
import logUtil

if len(sys.argv) < 4:
	raise Exception("correct syntax is: python3 harmonyTransactionSync.py dev/prod logsPath shardId rangeStart rangeEnd")

today = datetime.date.today()

logger = logUtil.l()
attempt = 1
shardId = int(sys.argv[3])

normalMode = True

rangeStart, rangeEnd = None, None
if len(sys.argv) > 4:
	rangeStart = int(sys.argv[4])
	rangeEnd = int(sys.argv[5])
	normalMode = False

def processTransactions():
	logger.info("starting processing for shard: " + str(shardId))

	startBlockHeight, endBlockHeight, more = commonUtils.getShardBlockHeightRange(
		constants.txSyncBlockHeightUrl, constants.TX_SYNC_MAX_LIMIT, shardId)

	if startBlockHeight is None:
		logger.info("starting block obtained is None. Exiting")
		raise Exception("Starting block obtained is None. Exiting")

	processTransactionsByRange(startBlockHeight, endBlockHeight)

	if more and attempt < constants.TX_SYNC_MAX_LOOPS:
		time.sleep(constants.SLEEP_TIME_FOR_MORE)
		logger.info(str(attempt) + " - starting new cycle")
		processTransactions()


def processTransactionsByRange(startBlockHeight, endBlockHeight):
	global attempt
	txData = {"summaryMap": {}, "txs": []}
	# logger.info("txData: {}".format(txData))
	processTransactionRange(constants.REGULAR_TRANSACTION_URL, startBlockHeight, endBlockHeight, txData, constants.TX_REGULAR)
	if shardId == 0 and startBlockHeight > constants.STAKING_START_BLOCK:
		processTransactionRange(constants.STAKING_TRANSACTION_URL, startBlockHeight, endBlockHeight, txData, constants.TX_STAKING)

	reqDetails = {"type": "txSync", "blockHeight": endBlockHeight, "normalMode": normalMode,
				  "startBlockHeight": startBlockHeight, "txData": txData, "shardId": shardId}
	# logger.info(reqDetails)

	logger.info("attempt: {} , endBlockHeight: {}, startBlockHeight: {}, summary: {}, txs: {}".format(
		attempt, endBlockHeight, startBlockHeight, txData["summaryMap"], len(txData["txs"])))
	commonUtils.postReq(constants.syncTxUrl, reqDetails)
	logger.info("after submitting transactions to backend")
	attempt += 1


def processTransactionRange(transactionUrl, startBlockHeight, endBlockHeight, txData, txCategory):
	logger.info("in processTransactionRange: startBlockHeight: {}, endBlockHeight: {}, txCategory: {}".format(
		startBlockHeight, endBlockHeight, txCategory))

	summaryMap = txData["summaryMap"]
	txs = txData["txs"]
	initCount = len(txs)
	logger.info("processTransactionRange - startBlockHeight: {}, endBlockHeight: {}, summaryMap: {}, txCategory: {}".format(
		startBlockHeight, endBlockHeight, summaryMap, txCategory))

	session = Session()
	blockCount = 0
	for blockNum in range(startBlockHeight, endBlockHeight + 1):
		blockCount += 1
		# if len(allEvents) > 1:
		# 	break
		logger.info("normal - {}, attempt - {}, shardId - {}, category - {}, count - {} - block: {}".format(
			normalMode, attempt, shardId, txCategory, blockCount, blockNum))
		index = 0
		# logger.info("processing events transaction for block: {}, and index: {}, is: {}".format(blockNum, index, transaction))
		while True and index < 1000:
			transaction = commonUtils.getHarmonyResultDataFromPostByShard(session, shardId, transactionUrl, [blockNum, index])
			# logger.info(str(attempt) + " - " + str(blockCount) + " transaction for block: {}, and index: {}, is: {}".format(blockNum, index, transaction))
			if not transaction:
				# logger.info("ending transaction processing as no more transaction were found")
				break

			logger.info("found transaction #: {}".format((len(txs) + 1)))
			# logger.info("transaction: {}".format(transaction))
			if txCategory == constants.TX_REGULAR:
				txDetails = getTransactionDetails(session, transaction, txCategory)
			else:
				txDetails = harmonyNetworkUtils.processStakingTransaction(session, transaction)

			index += 1
			if not txDetails:
				# this might be a cross shard tx that needs to be ignored
				logger.info("txDetails are null")
				logger.info("txDetails: {}".format(txDetails))
				continue

			txDate = txDetails["txDate"]
			# txDate = getTxDate(transaction)
			if txDate is not None:
				if txDate in summaryMap:
					summaryMap[txDate][txCategory] = summaryMap[txDate][txCategory] + 1
				else:
					summaryMap[txDate] = {"shardId": shardId, constants.TX_REGULAR: 0, constants.TX_STAKING: 0}
					summaryMap[txDate][txCategory] = 1

			txs.append(txDetails)

	logger.info("processed all transactions")
	logger.info("{} - total number of transactions: {}".format(txCategory, (len(txs) - initCount)))


def getTransactionDetails(session, transaction, txCategory):
	if shardId != 0 and transaction["toShardID"] == 0:
		# this means it is a cross shard transaction initiated in non-zero shard. ignoring it
		logger.info("this is a cross shard transaction initiated in non-zero shard. ignoring it.")
		return None

	txReceipt = harmonyNetworkUtils.getTxReceipt(session, transaction["hash"], shardId)
	txFee = 0
	if transaction["gasPrice"] and transaction["gasPrice"] != 0:
		txFee = transaction["gas"]/transaction["gasPrice"]

	tx = {"blockNumber": transaction["blockNumber"], "txCategory": txCategory,
		  "address": transaction["from"], "nonce": transaction["nonce"],
		  "txHash": transaction["hash"], "shardId": transaction["shardID"],
		  "epochTimestamp": transaction["timestamp"], "toShardId": transaction["toShardID"],
		  "toAddress": transaction["to"], "amount": commonUtils.getHarmonyCoins(transaction["value"]),
		  "blockHash": transaction["blockHash"], "txFee": txFee,
		  "txIndex": transaction["transactionIndex"], "status": harmonyNetworkUtils.getStatus(txReceipt),
		  "txDate": harmonyNetworkUtils.getTxDate(transaction), "txType": None, }

	return tx


def processBulkLoadMode():
	overallStartBlock = rangeStart
	for i in range(1,300):
		logger.info("starting iteration #: {}".format(i))
		if overallStartBlock >= rangeEnd:
			logger.info("overallStartBlock: {} >= rangeEnd: {}".format(overallStartBlock, rangeEnd))
			break
		iterationStartBlock = overallStartBlock
		iterationEndBlock = iterationStartBlock + constants.TX_SYNC_MAX_LIMIT
		if iterationEndBlock > rangeEnd:
			iterationEndBlock = rangeEnd
		processTransactionsByRange(iterationStartBlock, iterationEndBlock)
		logger.info("finished iteration #: {}".format(i))
		overallStartBlock = iterationEndBlock + 1

	logger.info("processing ended with: overallStartBlock: {}, rangeStart: {}, rangeEnd: {}".format(
		overallStartBlock, rangeStart, rangeEnd))



if normalMode:
	startTime = int(time.time())
	processTransactions()
	logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
else:
	startTime = int(time.time())
	processBulkLoadMode()
	logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
