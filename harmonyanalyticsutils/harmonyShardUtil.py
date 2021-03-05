import datetime
import sys
import time

from requests import Session

import commonUtils
import constants
import harmonyNetworkUtils
import logUtil

logger = logUtil.l()
if len(sys.argv) < 3:
	raise Exception("correct syntax is: python harmonyShardUtil.py dev/prod logsPath")


def processShardUtils():
	# hmyv2_getValidatorInformation
	# capture block production rate
	# obtain oldest block production rate after current epoch
	# capture pace of blocks
	session = Session()

	currentEpoch = commonUtils.getHarmonyResultDataFromPost(session, "hmyv2_getEpoch", [])
	dbDetails = commonUtils.getDataFromGet(session, constants.shardSyncDetailsUrl)
	logger.info("dbDetails: {}".format(dbDetails))
	syncedEpoch = dbDetails["epochNumber"]
	dbShardData = dbDetails["shardData"]
	logger.info("currentEpoch: {}, syncedEpoch: {}".format(currentEpoch, syncedEpoch))

	logger.info("obtaining shard details")
	shard0Details = getShardDetails(session, constants.HARMONY_BASE_URL, 0)
	shard1Details = getShardDetails(session, constants.HARMONY_BASE_URL_S1, 1)
	shard2Details = getShardDetails(session, constants.HARMONY_BASE_URL_S2, 2)
	shard3Details = getShardDetails(session, constants.HARMONY_BASE_URL_S3, 3)
	logger.info("after obtaining shard details")

	shardDetails = []
	if "0" not in dbShardData:
		# this means this is the first execution of the job
		logger.info("this means this is the first execution of the job. preparing initAllShardData")
		dbShardData = initAllShardData(session, shard0Details, shard1Details, shard2Details, shard3Details)
		logger.info("after preparing initAllShardData")
		# return
	elif currentEpoch != syncedEpoch:
		# update previous epoch first
		logger.info("epochs have changed. this means we need to update previous epoch data first")
		shardDetails.append(processShardEnd(dbShardData["0"]))
		shardDetails.append(processShardEnd(dbShardData["1"]))
		shardDetails.append(processShardEnd(dbShardData["2"]))
		shardDetails.append(processShardEnd(dbShardData["3"]))

		# init shard data for this epoch
		dbShardData = initAllShardData(session, shard0Details, shard1Details, shard2Details, shard3Details)

	# lastBlock = getEpochBlockDetails(session)
	shardDetails.append(processShard0(shard0Details, dbShardData["0"]))
	shardDetails.append(processOtherShard(shard1Details, dbShardData["1"], dbShardData["0"]))
	shardDetails.append(processOtherShard(shard2Details, dbShardData["2"], dbShardData["0"]))
	shardDetails.append(processOtherShard(shard3Details, dbShardData["3"], dbShardData["0"]))

	# get latest shard 0 record for calculations
	# get first block of epoch to calculate pace or may be do it in db
	# shardDetails = {}
	# shardDetails["0"] = getShardDetails(session, constants.HARMONY_BASE_URL, 0)
	# shardDetails["0"]["epochLastBlock"] = epochLastBlock
	#
	# shardDetails["1"] = getShardDetails(session, constants.HARMONY_BASE_URL_S1, 1)
	# shardDetails["2"] = getShardDetails(session, constants.HARMONY_BASE_URL_S2, 2)
	# shardDetails["3"] = getShardDetails(session, constants.HARMONY_BASE_URL_S3, 3)

	reqDetails = {"type": "shardSync", "shardDetails": shardDetails,
				  "currentEpoch": currentEpoch}
	# logger.info(reqDetails)
	commonUtils.postReq(constants.syncShardUrl, reqDetails)


def initAllShardData(session, shard0Details, shard1Details, shard2Details, shard3Details):
	dbShardData = {}
	logger.info("preparing initial data for shard 0")
	dbShardData["0"] = initShardData(session, shard0Details, 0)
	logger.info("afrer preparing initial data for shard 0")
	dbShardData["1"] = initShardData(session, shard1Details, 1, dbShardData["0"])
	logger.info("afrer preparing initial data for shard 1")
	dbShardData["2"] = initShardData(session, shard2Details, 2, dbShardData["0"])
	dbShardData["3"] = initShardData(session, shard3Details, 3, dbShardData["0"])

	logger.info("all shards initial data: {}".format(dbShardData))
	return dbShardData


def initShardData(session, shardDetails, shardId, shard0Details=None):
	# logger.info(shardDetails)
	shardInitDetails = {"shardId": shardId, "latestBlock": shardDetails["blockNumber"],
			"latestBlockTime": shardDetails["blockTime"], "epochNumber": shardDetails["epochNumber"]}
	# logger.info("shardInitDetails: {}".format(shardInitDetails))

	if shardId == 0:
		epochStartBlock, epochLastBlock, epochStartTime = getEpochBlockRangeShard0(session)
	else:
		shard0ElapsedBlocks = (shard0Details["latestBlock"] - shard0Details["epochStartBlock"])
		epochStartBlock, epochLastBlock, epochStartTime = getEpochBlockRangeOther(session,
			shard0Details["epochStartTime"], shardId, shardDetails["blockNumber"],
			shard0ElapsedBlocks)

	# logger.info("epochLastBlock: {}".format(epochLastBlock))
	#assume block rate is standard and calculate backwards for first block
	blockRate = constants.H_BLOCK_TIME
	# logger.info("epochStartBlock: {}".format(epochStartBlock))

	# currentTime = int(time.time())
	# latestBlock = shardDetails["blockNumber"]
	# blocksProcessed = latestBlock - epochStartBlock
	# epochStartTime = currentTime - (blocksProcessed * constants.H_BLOCK_TIME)

	# shardInitDetails["latestBlock"] = latestBlock
	shardInitDetails["epochStartBlock"] = epochStartBlock
	shardInitDetails["epochStartTime"] = epochStartTime
	# shardInitDetails["latestBlockTime"] = currentTime
	shardInitDetails["blockRate"] = blockRate
	# blocksLeft = constants.H_BLOCKS_IN_EPOCH - blocksProcessed
	# epochLastBlockTime = blocksLeft * constants.H_BLOCK_TIME

	# dbShardDetails["epochLastBlockTime"] = epochLastBlockTime
	# dbShardDetails["epochLastBlock"] = dbShardDetails["epochStartBlock"] + constants.H_BLOCKS_IN_EPOCH
	shardInitDetails["epochLastBlock"] = epochLastBlock

	logger.info("shardInitDetails for shard: {} are: {}".format(shardId, shardInitDetails))
	return shardInitDetails


def getEpochBlockDetails(session):
	stakingData = commonUtils.getHarmonyResultDataFromPost(session, "hmy_getStakingNetworkInfo", [])

	return stakingData["epoch-last-block"]


def getShardDetails(session, url, shardId):
	blockDetails = harmonyNetworkUtils.getLatestBlockDetails(session, url)
	blockNumber = blockDetails["blockNumber"]
	blockTime = blockDetails["unixtime"]
	epochNumber = blockDetails["epoch"]

	shardDetails = {"shardId": shardId, "blockNumber": blockNumber,
			"blockTime": blockTime, "epochNumber": epochNumber}

	# logger.info(shardDetails)
	return shardDetails


def processShard0(shardDetails, dbShardDetails):
	blocksProcessed = processBlockRate(shardDetails, dbShardDetails)

	blocksLeft = constants.H_BLOCKS_IN_EPOCH - blocksProcessed
	epochLastBlockTime = blocksLeft * constants.H_BLOCK_TIME

	dbShardDetails["epochLastBlockTime"] = int(time.time()) + epochLastBlockTime
	dbShardDetails["epochLastBlock"] = dbShardDetails["epochStartBlock"] + constants.H_BLOCKS_IN_EPOCH

	logger.info("final dbShardDetails: {}".format(dbShardDetails))
	return dbShardDetails


def processBlockRate(shardDetails, dbShardDetails):
	epochStartBlock = dbShardDetails["epochStartBlock"]
	epochStartTime = dbShardDetails["epochStartTime"]
	latestBlock = shardDetails["blockNumber"]
	currentTime = int(time.time())

	blocksProcessed = latestBlock - epochStartBlock
	timeSpent = currentTime - epochStartTime
	blockRate = timeSpent / blocksProcessed

	dbShardDetails["latestBlock"] = latestBlock
	dbShardDetails["latestBlockTime"] = currentTime
	dbShardDetails["blockRate"] = blockRate
	dbShardDetails["lastUpdated"] = datetime.datetime.now()
	dbShardDetails["epochEnded"] = False
	dbShardDetails["blocksProcessed"] = blocksProcessed

	return blocksProcessed


def processOtherShard(shardDetails, dbShardDetails, shard0Details):
	processBlockRate(shardDetails, dbShardDetails)

	epochLastBlockTime = shard0Details["epochLastBlockTime"]
	blocksLeft = int((epochLastBlockTime-int(time.time()))/constants.H_BLOCKS_IN_EPOCH)

	dbShardDetails["epochLastBlockTime"] = epochLastBlockTime
	dbShardDetails["epochLastBlock"] = dbShardDetails["latestBlock"] + blocksLeft

	logger.info("final dbShardDetails: {}".format(dbShardDetails))
	return dbShardDetails


# shard0Block = harmonyNetworkUtils.getLatestBlockAndTime(session, constants.HARMONY_BASE_URL)
# shard1Block = harmonyNetworkUtils.getLatestBlockAndTime(session, constants.HARMONY_BASE_URL_S1)
# shard2Block = harmonyNetworkUtils.getLatestBlockAndTime(session, constants.HARMONY_BASE_URL_S2)
# shard3Block = harmonyNetworkUtils.getLatestBlockAndTime(session, constants.HARMONY_BASE_URL_S3)


def processShardEnd(dbShardDetails):
	# end the last epoch
	# assume that for the timeframe for which data was not captured went at expected pace
	dbShardDetails["epochEnded"] = True
	dbShardDetails["lastUpdated"] = datetime.datetime.now()

	return dbShardDetails


def getEpochLastBlockShard0(session):
	# logger.info("getting staking information")
	data = commonUtils.getHarmonyResultDataFromPost(session, constants.STAKING_NETWORK_INFO, [])
	# logger.info("staking network info: {}".format(data))

	epochLastBlock = data["epoch-last-block"]
	epochStartBlock = epochLastBlock - constants.H_BLOCKS_IN_EPOCH
	blocks = commonUtils.getHarmonyResultDataFromPost(session,
			constants.BLOCK_RANGE, [epochStartBlock, epochStartBlock + 1, constants.BLOCK_HEADER])
	# logger.info(blocks)

	return data["epoch-last-block"], blocks[0]["timestamp"]


def getEpochBlockRangeOther(session, startBlockTime, shardId, currentBlock, shard0ElapsedBlocks):
	logger.info("in getEpochBlockRangeOther for startBlockTime: {}, shardId: {}, currentBlock: {}, shard0ElapsedBlocks: {}".format(
		startBlockTime, shardId, currentBlock, shard0ElapsedBlocks))

	epochStartBlock, epochStartBlockTime = getEpochStartBlock(session, startBlockTime,
			shardId, currentBlock, shard0ElapsedBlocks)
	epochLastBlock = epochStartBlock + constants.H_BLOCKS_IN_EPOCH

	logger.info("in getEpochBlockRangeOther - returning epochStartBlock: {}, epochLastBlock: {}, epochStartBlockTime: {}".format(
		epochStartBlock, epochLastBlock, epochStartBlockTime))
	return epochStartBlock, epochLastBlock, epochStartBlockTime


def getEpochBlockRangeShard0(session):
	epochLastBlock, epochStartBlockTime = getEpochLastBlockShard0(session)
	epochStartBlock = epochLastBlock - constants.H_BLOCKS_IN_EPOCH
	return epochStartBlock, epochLastBlock, epochStartBlockTime


def getEpochStartBlock(session, firstBlockTime, shardId, currentBlock, shard0ElapsedBlocks):
	logger.info("in getEpochStartBlock for shard: {}".format(shardId))

	anticipatedBlock = currentBlock - shard0ElapsedBlocks
	tempAnticipatedBlock = anticipatedBlock
	tempDirectionUp = None
	for i in range(1, 20):
		if not tempDirectionUp:
			startingBlock = tempAnticipatedBlock - 100
			endingBlock = tempAnticipatedBlock + 100
		elif tempDirectionUp:
			startingBlock = tempAnticipatedBlock
			endingBlock = tempAnticipatedBlock + 200
		else:
			startingBlock = tempAnticipatedBlock - 200
			endingBlock = tempAnticipatedBlock

		logger.info("shard id: {} - iteration #: {}, startingBlock: {}, endingBlock: {}".format(
			shardId, i, startingBlock, endingBlock))
		found, currentStartBlock, currentStartBlockTime, directionUp = tryForEpochStartBlock(
			session, firstBlockTime, shardId, startingBlock, endingBlock)

		if found:
			return currentStartBlock, currentStartBlockTime
		else:
			tempDirectionUp = directionUp
			tempAnticipatedBlock = currentStartBlock

	raise Exception("couldn't figure out start block for time: {} for shard: {} and starting block: {}".format(
		firstBlockTime, shardId, currentBlock))


def tryForEpochStartBlock(session, firstBlockTime, shardId, startingBlock, endingBlock):
	blocks = commonUtils.getHarmonyResultDataFromPostByShard(session, shardId,
			constants.BLOCK_RANGE, [startingBlock, endingBlock, constants.BLOCK_HEADER])

	if len(blocks) == 0:
		raise Exception("blocks not found for : {} and {}".format(startingBlock, endingBlock))

	prevBlockTime = blocks[0]["timestamp"] - 2
	logger.info("processing: block range: {} to {} for # of blocks: {}".format(
		startingBlock, endingBlock, len(blocks)))
	for block in blocks:
		if prevBlockTime < block["timestamp"] <= firstBlockTime:
			return True, block["number"], block["timestamp"], None
		elif block["timestamp"] <= firstBlockTime:
			if block["timestamp"] + 2 >= firstBlockTime:
				return True, block["number"], block["timestamp"], None
			else:
				return False, None, None, True
		elif block["timestamp"] >= firstBlockTime:
			if block["timestamp"] - 2 <= firstBlockTime:
				return True, block["number"], block["timestamp"], None
			else:
				return False, None, None, False

		prevBlockTime = block["timestamp"]

	raise Exception("processed all blocks. couldnt figure out next step for : {} and {}".format(
		startingBlock, endingBlock))



startTime = int(time.time())
processShardUtils()
logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
