import logging

import constants
import hConstants

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def isEnoughDataForBlsKeys(coinStat, epoch, currentBlock):
	blocksToWait = constants.MIN_BLOCKS_BLS_KEY_NOTIFICATIONS
	tooManyBlocksPassed = constants.MAX_BLOCKS_BLS_KEY_NOTIFICATIONS
	enoughData = isEnoughDataForAlerts(coinStat, epoch, currentBlock, blocksToWait, tooManyBlocksPassed)
	# logger.info("isEnoughDataForBlsKeys: {}, epoch:{}, currentBlock: {}, blocksToWait: {}".format(
	# 	enoughData, epoch, currentBlock, blocksToWait))

	return enoughData


def isEnoughDataForUnderbid(coinStat, epoch, currentBlock):
	blocksToWait = constants.MIN_BLOCKS_UNDERBID_NOTIFICATIONS
	tooManyBlocksPassed = constants.MAX_BLOCKS_UNDERBID_NOTIFICATIONS
	return isEnoughDataForAlerts(coinStat, epoch, currentBlock, blocksToWait, tooManyBlocksPassed)


def isEnoughDataForAlerts(coinStat, epoch, currentBlock, blocksToWait, tooManyBlocksPassed):
	if coinStat["currentEpoch"] < epoch:
		# logger.info("epochs dont match. not sending notifications. coinStat->currentEpoch : {} < epoch : {}".format(
		# 	coinStat["currentEpoch"], epoch))
		return False

	totalBlocks = hConstants.H_BLOCKS_IN_EPOCH
	lastBlock = coinStat["epochLastBlock"]-1
	firstBlock = lastBlock - totalBlocks
	blocksPast = currentBlock - firstBlock

	enoughData = True
	if blocksPast < blocksToWait or blocksPast > tooManyBlocksPassed:
		logger.info("minimum blocks {} have not passed in the epoch - {}".format(
		    blocksToWait, blocksPast))
		enoughData = False

	return enoughData

