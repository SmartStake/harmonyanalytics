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

def syncTransactions(conn, app, data, startTime):
	logger.info("syncing harmony transactions")
	startBlock = data["startBlockHeight"]
	shardId = data["shardId"]
	eventKey = eventName.lastSyncedHarmonyTxBlockHeight + str(shardId)
	normalMode = data["normalMode"]

	validateStartBlock(conn, startBlock, eventKey, normalMode)

	endBlock = data["blockHeight"]

	txData = data["txData"]
	processSummary(conn, txData["summaryMap"])

	txs = txData["txs"]
	logger.info("txs: {}".format(len(txs)))
	poolMap = harmonyData.listHPoolsAsMap(conn)

	processTransactions(conn, app, txs, poolMap)
	# processStakingTransactions(conn, app, txs["staking"])

	createAddressIfAny(conn)

	# if normalMode:
	auditUtils.createEvent(conn, app, eventKey, endBlock)
	# logger.info("finished processing all events")
	conn.commit()


def processSummary(conn, summaryMap):
	inserts, updates = [], []
	for txDate, details in summaryMap.items():
		processTxSummary(conn, txDate, details, hConstants.TX_REGULAR, inserts, updates)
		processTxSummary(conn, txDate, details, hConstants.TX_STAKING, inserts, updates)

	if len(inserts) > 0:
		batchCreateTxSummary(conn, inserts)
	if len(updates) > 0:
		batchUpdateTxSummary(conn, updates)


def processTxSummary(conn, txDate, details, txCategory, inserts, updates):
	count = details[txCategory]
	shardId = details["shardId"]
	dbTxSummary = getTxSummary(conn, txDate, txCategory, shardId)

	if dbTxSummary:
		newCount = count + dbTxSummary["txCount"]
		updates.append((newCount, datetime.now(), dbTxSummary["summaryId"]))
	else:
		inserts.append((txDate, txCategory, count, shardId))


def getTxSummary(conn, txDate, txCategory, shardId):
	sql = "select * "
	sql += " from " + tables.htxsummary
	sql += " where txDate = %s and txCategory = %s and shardId = %s "
	sql += " limit 1"

	return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, (txDate, txCategory, shardId))


def processTransactions(conn, app, txs, poolMap):
	inserts, notifications = [], []
	coinStat = commonUtils.getCoinStat(conn, app)
	txNotAddresses = tgBotUtils.getAllAddressesForTxAlert(conn, app)
	logger.info("txNotAddresses are: {}".format(txNotAddresses))

	for tx in txs:
		if tx["txCategory"] == hConstants.TX_REGULAR:
			insertData = getRegularTransaction(tx)
			processTxForNotification(tx, notifications, txNotAddresses)
		else:
			insertData = getStakingTransaction(tx, coinStat, poolMap)

		inserts.append(insertData)

	# logger.info("inserts are:")
	# logger.info(inserts)
	if len(inserts) > 0:
		batchCreateTx(conn, inserts)

	logger.info("notifications are: {}".format(len(notifications)))
	if len(notifications) > 0:
		notificationUtils.batchCreateNotificationsWithOtherData(conn, notifications)



def processTxForNotification(tx, notifications, txNotAddresses):
	# logger.info("in processTxForNotification, tx is: {}".format(tx))

	txType = None
	if tx["address"] in txNotAddresses:
		# someone is interested in this notification
		# logger.info("in processTxForNotification, from address is in tx notification addresses")
		txType = hConstants.NOTIFICATION_TYPE_REGULAR_TX_FROM

	if tx["toAddress"] in txNotAddresses:
		# someone is interested in this notification
		# logger.info("in processTxForNotification, to address is in tx notification addresses")
		txType = hConstants.NOTIFICATION_TYPE_REGULAR_TX_TO

	if txType:
		notifications.append((txType, tx["address"],
			None, None, tx["amount"], None, None, tx["blockNumber"],
			tx["toAddress"], tx["status"], tx["txHash"]))


def getRegularTransaction(tx):
	insertData = (tx["txHash"], tx["address"], tx["toAddress"],
		None, tx["amount"], tx["epochTimestamp"],
		tx["blockNumber"], tx["txDate"], None,
		tx["shardId"], tx["status"], tx["txFee"],
		tx["nonce"], None, False,
		None, tx["toShardId"], tx["txIndex"])

	return insertData


def batchCreateTx(conn, inserts):
	sql = "INSERT INTO " + tables.htransaction
	sql += "(txHash, fromAddress, toAddress, "
	sql += " txType, amount, epochTimestamp, "
	sql += " blockNumber, txDate, epoch, "
	sql += " shardId, status, txFee, "
	sql += " nonce, token, isStakingTx, "
	sql += " hPoolId, toShardId, txIndex) VALUES ("
	sql += " %s, %s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s, "
	sql += " %s, %s, %s, %s, %s, "
	sql += " %s, %s, %s)"

	# logger.info("{0}: {1}".format(sql, len(inserts)))
	conn.cursor().executemany(sql, inserts)


def batchCreateTxSummary(conn, inserts):
	sql = "INSERT INTO " + tables.htxsummary
	sql += "(txDate, txCategory, txCount, shardId) "
	sql += " VALUES (%s, %s, %s, %s)"

	# logger.info("{0}: {1}".format(sql, len(inserts)))
	conn.cursor().executemany(sql, inserts)


def batchUpdateTxSummary(conn, updates):
	sql = "update " + tables.htxsummary
	sql += " set txCount = %s, lastUpdated = %s "
	sql += " where summaryId = %s "

	# logger.info("{0}: {1}".format(sql, len(updates)))
	conn.cursor().executemany(sql, updates)


def getStakingTransaction(tx, coinStat, poolMap):

	hPoolId = None
	if "validatorAddress" in tx and tx["validatorAddress"] not in poolMap:
		# logger.info("the validator {} is not known. skipping event.".format(e["validatorAddress"]))
		poolDetails = poolMap[tx["validatorAddress"]]
		hPoolId = poolDetails["hPoolId"]

	# logger.info("hPoolId: {}, tx: {}".format(hPoolId, tx))
	insertData = (tx["txHash"], tx["address"], tx["toAddress"],
		tx["txType"], tx["amount"], tx["epochTimestamp"],
		tx["blockNumber"], tx["txDate"], None,
		tx["shardId"], tx["status"], tx["txFee"],
		tx["nonce"], None, True,
		hPoolId, tx["toShardId"], tx["txIndex"])

	return insertData


def createAddressIfAny(conn):
	sql = "insert into " + tables.haddress + " (address) "
	sql += " select distinct address from ( "
	sql += " select distinct fromAddress as address from " + tables.htransaction + " ht1 "
	sql += " where ht1.fromAddress is not null and length(ht1.fromAddress) > 10  "
	sql += " and not exists (select 1 from " + tables.haddress + " ha1 "
	sql += "  where ha1.address=ht1.fromAddress) "
	sql += " union "
	sql += " select distinct toAddress as address from " + tables.htransaction + " ht2 "
	sql += " where ht2.toAddress is not null and length(ht2.toAddress) > 10 "
	sql += " and not exists (select 1 from " + tables.haddress + " ha2 "
	sql += " where ha2.address=ht2.toAddress)) unique_address "

	# logger.info(sql)
	count = conn.cursor().execute(sql)
	logger.info("number of addresses created: {}".format(count))


def getTotalTransactions(conn):
	sql = "select sum(txCount) as totalTransactions from " + tables.htxsummary

	data = dbUtil.getSingleRecordNoJsonWithConn(sql, conn)

	return data["totalTransactions"]


def listDailyTransactions(conn):
	sql = "SELECT t.title, "
	sql += " 	t.transactions, @running_tx:=@running_tx + t.transactions AS cumulativeTxs, "
	sql += " 	t.nonStakingTransactions, @running_tx_nonstk:=@running_tx_nonstk + t.nonStakingTransactions AS cumulativeNonStakingTxs, "
	sql += " 	t.stakingTransactions, @running_tx_stk:=@running_tx_stk + t.stakingTransactions AS cumulativeStakingTxs "
	sql += " FROM "
	sql += " ( 	select date(txDate) as title, sum(txCount) as transactions, "
	sql += " 		sum(case when txCategory='regular' then txCount else null end) as nonStakingTransactions, "
	sql += " 		sum(case when txCategory='staking' then txCount else null end) as stakingTransactions "
	sql += " 	from " + tables.htxsummary + " group by date(txDate) "
	sql += " ) t "
	sql += " JOIN (SELECT @running_tx:=0, @running_tx_stk:=0, @running_tx_nonstk:=0) r "
	sql += " ORDER BY t.title "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn)


def listShardSummaryTransactions(conn):
	sql = " select shardId as title, sum(txCount) as transactions "
	sql += " from " + tables.htxsummary + " group by shardId "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn)


def listDailyShardTransactions(conn):
	sql = "SELECT t.title, "
	sql += "		t.transactions, @running_tx:=@running_tx + t.transactions AS cumulativeTxs, "
	sql += "		t.shard0Transactions, @running_tx_s0:=@running_tx_s0 + t.shard0Transactions AS cumulativeShard0Txs, "
	sql += "		t.shard1Transactions, @running_tx_s1:=@running_tx_s1 + t.shard1Transactions AS cumulativeShard1Txs, "
	sql += "		t.shard2Transactions, @running_tx_s2:=@running_tx_s2 + t.shard2Transactions AS cumulativeShard2Txs, "
	sql += "		t.shard3Transactions, @running_tx_s3:=@running_tx_s3 + t.shard3Transactions AS cumulativeShard3Txs "
	sql += " FROM "
	sql += " ( 	select date(txDate) as title,  "
	sql += " 	sum(txCount) as transactions, "
	sql += " 	sum(case when shardId=0 then txCount else null end) as shard0Transactions, "
	sql += " 	sum(case when shardId=1 then txCount else null end) as shard1Transactions, "
	sql += " 	sum(case when shardId=2 then txCount else null end) as shard2Transactions, "
	sql += " 	sum(case when shardId=3 then txCount else null end) as shard3Transactions "
	sql += " from " + tables.htxsummary + " group by date(txDate) "
	sql += "  ) t "
	sql += " JOIN (SELECT @running_tx:=0, @running_tx_s0:=0, @running_tx_s1:=0, @running_tx_s2:=0, @running_tx_s3:=0) r "
	sql += " ORDER BY t.title "

	# logger.info(sql)
	return dbUtil.listResultsWithConn(sql, conn)


def validateStartBlock(conn, startBlock, eventKey, normalMode):
	logger.info("in validateStartBlock: event - {}, normalMode - {}".format(eventKey, normalMode))

	if not normalMode:
		return

	event = dbUtil.getSingleRecordNoJsonWithConn(commonUtils.getEventSql(), conn, eventKey)
	# logger.info(event)
	dbBlock = int(event["description"])

	msg = "Expected starting block: {}, actual starting block: {}".format(dbBlock, startBlock)
	logger.info(msg)

	if dbBlock + 1 != startBlock:
		raise Exception("Transaction blocks do not align. " + msg)


