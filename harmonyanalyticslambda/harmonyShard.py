import logging
from datetime import datetime

import auditUtils
import commonUtils
import dbUtil
import eventName
import hConstants
import harmonyData
import notificationUtils
import tables
import tgBotUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getShardSyncInputDetails(conn):
	epochNumber = commonUtils.getEventDescriptionInt(conn, eventName.lastHarmonyShardSyncDetails)
	shardData = getShardDataFromDB(conn)

	return dbUtil.combineResults2("epochNumber", epochNumber, "shardData", shardData)


def syncShardDetails(conn, app, data, startTime):
	logger.info("syncing harmony shard data")

	shardDetails = data["shardDetails"]
	currentEpoch = data["currentEpoch"]

	# logger.info("processing data: {}".format(shardDetails))

	inserts, updates = [], []
	for shard in shardDetails:
		# logger.info("processing shard: {}".format(shard))
		if "blockRateId" in shard:
			updates.append((shard["epochStartBlock"], shard["latestBlock"], shard["epochLastBlock"],
				shard["epochStartTime"], shard["latestBlockTime"], shard["epochLastBlockTime"],
				shard["epochEnded"], shard["blockRate"], datetime.now(), shard["blockRateId"]))
		else:
			inserts.append((shard["epochNumber"], shard["shardId"], shard["epochStartBlock"],
				shard["latestBlock"], shard["epochLastBlock"], shard["epochStartTime"],
				shard["latestBlockTime"], shard["epochLastBlockTime"], shard["epochEnded"], shard["blockRate"]))

	# logger.info("processing inserts: {}".format(inserts))
	# logger.info("processing updates: {}".format(updates))
	if len(inserts) > 0:
		batchCreateBlockRate(conn, inserts)
	if len(updates) > 0:
		batchUpdateBlockRate(conn, updates)

	updateCoinStatBlockRate(conn)

	# if normalMode:
	auditUtils.createEvent(conn, app, eventName.lastHarmonyShardSyncDetails, currentEpoch)
	# logger.info("finished processing all events")
	conn.commit()


def batchCreateBlockRate(conn, inserts):
	sql = "INSERT INTO " + tables.hblockrate
	sql += "(epochNumber, shardId, epochStartBlock, latestBlock, epochLastBlock, "
	sql += "epochStartTime, latestBlockTime, epochLastBlockTime, epochEnded, blockRate) "
	sql += " VALUES (%s, %s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s)"

	# logger.info("{0}: {1}".format(sql, len(inserts)))
	conn.cursor().executemany(sql, inserts)


def batchUpdateBlockRate(conn, updates):
	sql = "update " + tables.hblockrate + " set "
	sql += " epochStartBlock = %s, latestBlock = %s, epochLastBlock = %s, "
	sql += " epochStartTime = %s, latestBlockTime = %s, epochLastBlockTime = %s, "
	sql += " epochEnded = %s, blockRate = %s, lastUpdated=%s "
	sql += " where blockRateId = %s "

	# logger.info("{0}: {1}".format(sql, len(updates)))
	conn.cursor().executemany(sql, updates)


def getShardDataFromDB(conn):
	sql = "SELECT * FROM " + tables.hblockrate
	sql += " where epochEnded = '0' "

	listData = dbUtil.listResultsWithConn(sql, conn)
	return commonUtils.getMapFromList(listData, "shardId")

# not in use
def getBlockRateHistory(conn):
	sql = "SELECT epochNumber as title, "
	sql += " round(avg(case when shardId=0 then blockRate else null end),3) as shard0BlockRate, "
	sql += " round(avg(case when shardId=1 then blockRate else null end),3) as shard1BlockRate, "
	sql += " round(avg(case when shardId=2 then blockRate else null end),3) as shard2BlockRate, "
	sql += " round(avg(case when shardId=3 then blockRate else null end),3) as shard3BlockRate "
	sql += " from " + tables.hblockrate
	sql += " group by epochNumber order by epochNumber "
	# logger.info(sql)

	return dbUtil.listResultsWithConn(sql, conn)


def updateCoinStatBlockRate(conn):
	sql = "update " + tables.coinstat + " set blockRate=("
	sql += "	SELECT blockRate FROM " + tables.hblockrate
	sql += " 	where epochEnded = '0' and shardId = 0 "
	sql += " ) where symbol='HARMONY' "

	conn.cursor().execute(sql)

