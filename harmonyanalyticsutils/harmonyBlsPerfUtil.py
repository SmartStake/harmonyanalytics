import sys
import time

from requests import Session

import commonUtils
import constants
import harmonyNetworkUtils
import logUtil

logger = logUtil.l()
if len(sys.argv) < 3:
	raise Exception("correct syntax is: python harmonyBlsPerfUtil dev/prod logsPath")


def processBlsUtils():
	# hmyv2_getValidatorInformation
	# capture block production rate
	# obtain oldest block production rate after current epoch
	# capture pace of blocks
	# get latest next election slots
	# get all validators
	session = Session()

	logger.info("obtaining blsKeySyncDetailsUrl data")
	blsKeySyncDetails = commonUtils.getDataFromGet(session, constants.blsKeySyncDetailsUrl)
	# logger.info(blsKeySyncDetails)
	dbValidators = blsKeySyncDetails["validators"]
	# dbShards = blsKeySyncDetails["shards"]
	keys = blsKeySyncDetails["keys"]
	dbKeyMap = commonUtils.getMapFromList(keys, "blsKey")

	logger.info("obtaining epoch details")
	currentEpoch = commonUtils.getHarmonyResultDataFromPost(session, "hmyv2_getEpoch", [])
	shardDetails = getAllShardDetails(session, currentEpoch)
	# latestBlock = commonUtils.getHarmonyResultDataFromPost(session, "hmyv2_blockNumber", [])

	#note down block for which data is being captured ... record block number as well along with bls data
	logger.info("obtaining validators")
	# dbValidators = commonUtils.getDataFromGet(session, constants.listAllValidatorsBasicUrl)

	blsKeyInserts, blsPerfData = [], []
	rewardsDetails = {"0": 0, "1": 0, "2": 0, "3": 0, "totalRewards": 0}
	i = 0
	for validator in dbValidators:
		#exclude the ones not elected
		# status = commonUtils.getStatus(validatorDetails["eposStatus"])
		# logger.info(validator)
		status = validator["status"]
		if status != constants.H_STATUS_ELECTED:
			# logger.info("skipping validator, {}, as status is not elected, it is: {}".format(
			# 	validator["name"], status))
			continue

		address = validator["address"]
		i += 1
		logger.info("{} - obtaining all keys for validator: {}".format(i, address))
		validatorDetails = getValidatorDetails(session, address)
		perfData, keyInserts = processKeys(validatorDetails["perfByKeys"], dbKeyMap,
			validator["hPoolId"], currentEpoch, rewardsDetails)

		blsPerfData.extend(perfData)
		blsKeyInserts.extend(keyInserts)

	# loop again here to calculate overall averages
	# logger.info("blsPerfData before overall percentages: {}".format(blsPerfData))
	processForOverallPercentages(blsPerfData, rewardsDetails)
	# logger.info("blsPerfData after overall percentages: {}".format(blsPerfData))

	logger.info("blsPerfData # of keys is: {}".format(len(blsPerfData)))
	logger.info("syncing all addresses with database")
	addReqDetails = {"type": "blsKeySync",
		"blsPerfData": blsPerfData, "inserts": blsKeyInserts,
		"shardDetails": shardDetails, "currentEpoch": currentEpoch
	}
	commonUtils.postReq(constants.syncBlsPerfUrl, addReqDetails)
	logger.info("after syncing all addresses with database")


def processForOverallPercentages(blsPerfData, rewardsDetails):
	logger.info("in processForOverallPercentages")

	highestRewardRatio = {"0": 1, "1": 1, "2": 1, "3": 1}
	for key in blsPerfData:
		# logger.info("key details before processing are: {}".format(key))
		reward = key["reward"]
		shardId = str(key["shardId"])
		groupReward = rewardsDetails[str(key["shardId"])]
		groupPercentReward = 0
		if groupReward != 0:
			groupPercentReward = reward/groupReward
		groupPercentStake = key["groupPercentStake"]
		groupRewardRatio = groupPercentReward/groupPercentStake
		key["groupPercentReward"] = groupPercentReward
		key["groupRewardRatio"] = groupRewardRatio
		if groupRewardRatio > highestRewardRatio[shardId]:
			highestRewardRatio[shardId] = groupRewardRatio

		overallReward = rewardsDetails["totalRewards"]
		overallPercentReward = 0
		if overallReward != 0:
			overallPercentReward = reward/overallReward
		key["overallPercentReward"] = overallPercentReward



	for key in blsPerfData:
		groupRewardRatio = key["groupRewardRatio"]
		shardId = str(key["shardId"])
		keyPerfIndex = groupRewardRatio / highestRewardRatio[shardId]
		key["keyPerfIndex"] = keyPerfIndex
		if keyPerfIndex < constants.KEY_BAD_PERF_THRESHOLD:
			# logger.info("keyPerfIndex: {} < constants.KEY_BAD_PERF_THRESHOLD: {}".format(keyPerfIndex, constants.KEY_BAD_PERF_THRESHOLD))
			key["isBadPerf"] = "True"
		else:
			key["isBadPerf"] = "False"
		# logger.info("key details after processing are: {}".format(key))


def processKeys(perfByKeys, dbKeyMap, hPoolId, currentEpoch, rewardsDetails):
	# logger.info("in processKeys")
	blsPerfData, blsKeyInserts = [], []

	if not perfByKeys:
		return blsPerfData, blsKeyInserts

	for keyData in perfByKeys:
		# logger.info(keyData)
		blsKey = keyData["key"]["bls-public-key"]
		# logger.info(blsKey)
		shardId = keyData["key"]["shard-id"]
		if blsKey not in dbKeyMap:
			keyDetails = {"blsKey": blsKey, "shardId": shardId,
						  "hPoolId": hPoolId}
			blsKeyInserts.append(keyDetails)

		reward = commonUtils.getAmount(keyData["earned-reward"])
		rewardsDetails["totalRewards"] += reward
		rewardsDetails[str(shardId)] += reward

		perfData = {
			"blsKey": blsKey, "shardId": shardId,
			"epochNumber": currentEpoch,
			"reward": reward, "hPoolId": hPoolId,
			"effectiveStake": commonUtils.getAmount(keyData["key"]["effective-stake"]),
			"rawStake": commonUtils.getAmount(keyData["key"]["raw-stake"]),
			"groupPercentStake": float(keyData["key"]["group-percent"]),
			"overallPercentStake": float(keyData["key"]["overall-percent"]),
		}

		blsPerfData.append(perfData)

	return blsPerfData, blsKeyInserts

def getValidatorDetails(session, address):
	inputData = [address]
	# https://api.hmny.io/?version=latest#9d17f3bf-eeff-4be8-abe5-328467a9e5ec
	data = commonUtils.getHarmonyResultDataFromPost(session, constants.VALIDATOR_INFO_URL, inputData)
	# logger.info(data)
	currentEpochSignPercent = 0
	if data["current-epoch-performance"]:
		currentEpochSignPercent = data["current-epoch-performance"]["current-epoch-signing-percent"]

	blsKey = None
	if data["metrics"]:
		blsKey = data["metrics"]["by-bls-key"]

	details = {"nextKeys": data["validator"]["bls-public-keys"],
			   "perfByKeys": blsKey,
			   "activeStatus": data["active-status"],
			   "bootedStatus": data["booted-status"],
			   "currentSignPer": currentEpochSignPercent,
			   "currentlyInCommittee": data["currently-in-committee"],
			   "eposStatus": data["epos-status"],
			   "eposWinningStake": data["epos-winning-stake"],
			   "totalDelegation": data["total-delegation"],}

	# "currently-in-committee":true,
	# "epos-status":"currently elected", Currently elected, eligible to be elected next epoch, or not eligible to be elected next epoch
	# "epos-winning-stake" - total effective status
	# total-delegation
	#look for active
	# bls-public-keys - next keys
	# activeStatus = data["active-status"]

	return details


def getAllShardDetails(session, epochNumber):
	crossLinkDetails = commonUtils.getHarmonyResultDataFromPost(session, constants.CROSS_LINKS_URL)
	# logger.info("crossLinkDetails: {}".format(crossLinkDetails))
	if len(crossLinkDetails) < 3:
		logger.info(crossLinkDetails)
		raise Exception("unexpected response received for cross link details")

	allData = {}
	shard0Block = harmonyNetworkUtils.getLatestBlock(session, constants.HARMONY_BASE_URL)
	shard1Block = harmonyNetworkUtils.getLatestBlock(session, constants.HARMONY_BASE_URL_S1)
	shard2Block = harmonyNetworkUtils.getLatestBlock(session, constants.HARMONY_BASE_URL_S2)
	shard3Block = harmonyNetworkUtils.getLatestBlock(session, constants.HARMONY_BASE_URL_S3)

	allData["shard0"] = {"shardId": 0, "epochNumber": epochNumber, "blockNumber": shard0Block, "crossLinkBlock": shard0Block, "slots": 160}
	allData["shard1"] = {"shardId": 1, "epochNumber": epochNumber, "blockNumber": shard1Block, "crossLinkBlock": crossLinkDetails[0]["block-number"], "slots": 160}
	allData["shard2"] = {"shardId": 2, "epochNumber": epochNumber, "blockNumber": shard2Block, "crossLinkBlock": crossLinkDetails[1]["block-number"], "slots": 160}
	allData["shard3"] = {"shardId": 3, "epochNumber": epochNumber, "blockNumber": shard3Block, "crossLinkBlock": crossLinkDetails[2]["block-number"], "slots": 160}

	return allData


startTime = int(time.time())
processBlsUtils()
logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
