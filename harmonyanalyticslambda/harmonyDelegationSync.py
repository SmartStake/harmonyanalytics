import datetime
import logging

import auditUtils
import commonUtils
import constants
import dbUtil
import eventName
import harmonyData
import harmonyHistory
import tables

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("in harmony delegation sync")

app = constants.HARMONY


def syncAddresses(conn, app, data, event):
	logger.info("in harmony address sync")
	startTime = datetime.datetime.now()

	updated = updateAddressHistory(conn)
	conn.commit()

	if updated:
		logger.info("skipping address sync as address history was processed")
		return

	inserts = data["inserts"]
	updates = data["updates"]

	logger.info("processing address inserts")
	if inserts is not None:
		# count = 0
		insertArgs = []
		for i in inserts:
			# , i["txCount"]
			record = (i["address"], i["balance"])
			insertArgs.append(record)
			# count += 1
			# if count % 1000 == 0:
			# 	conn.commit()

		batchCreateAddress(conn, insertArgs)
	conn.commit()

	logger.info("processing address updates")
	if updates is not None:
		updateArgs = []
		for i in updates:
			# logger.info(i)
			# i["txCount"],
			updateArgs.append((i["balance"], i["addressId"]))
		batchUpdateAddress(conn, updateArgs)

	conn.commit()

	balanceIncludesStake = data["balanceIncludesStake"]
	logger.info("balanceIncludesStake: {}".format(balanceIncludesStake))
	updateBalances(conn, balanceIncludesStake)
	conn.commit()

	updateRank(conn, 50000)
	conn.commit()

	auditUtils.createEvent(conn, app, eventName.syncHarmonyAddresses)
	auditUtils.audit(conn, app, event, eventName.syncHarmonyAddresses, "service", startTime)

	logger.info("processing finished")


# likely not in use
def createAddress(conn, address, balance=0, txCount=0):
	sql = "insert into " + tables.haddress
	sql += " (address, addressBalance, txCount) "
	sql += " values(%s, %s, %s) "
	conn.cursor().execute(sql, (address, balance, txCount))


def batchCreateAddress(conn, addresses):
	sql = "insert into " + tables.haddress
	sql += " (address, addressBalance) "
	sql += " values(%s, %s) "
	# , txCount , %s

	createdCount = conn.cursor().executemany(sql, addresses)
	logger.info("address creation requested - {}, update performed - {}".format(len(addresses), createdCount))


def batchUpdateAddress(conn, addresses):
	sql = "update " + tables.haddress
	sql += " set addressBalance=%s "
	sql += " where addressId=%s "
	# , txCount=%s
	logger.info(sql)
	updatedCount = conn.cursor().executemany(sql, addresses)
	logger.info("address update requested - {}, update performed - {}".format(len(addresses), updatedCount))


def updateAddress(conn, addressId, balance=0, txCount=0):
	sql = "update " + tables.haddress
	sql += " set addressBalance=%s, txCount=%s "
	sql += " where addressId=%s "
	conn.cursor().execute(sql, (balance, txCount, addressId))


def updateRank(conn, count):
	richlist = dbUtil.listResultsWithConn(harmonyData.getRichListSqlForRank(count), conn)
	rank = 1
	
	rankUpdateSql = "update " + tables.haddress 
	rankUpdateSql += " set rank = %s where addressId=%s "

	logger.info("starting updating rank")
	updates = []
	for a in richlist:
		if a["rank"] != rank:
			updates.append((rank, a["addressId"]))

		# if rank % 100 == 0:
		# 	conn.commit()
		rank += 1

	if len(updates) > 0:
		conn.cursor().executemany(rankUpdateSql, updates)
	logger.info("after updating rank")


def updateAddressHistory(conn):
	coinStat = commonUtils.getCoinStat(conn, app)

	syncStatus = commonUtils.getSyncStatus(conn, app, constants.H_ADDRESS_HISTORY_SYNC)
	epoch = coinStat["currentEpoch"]

	logger.info("addresses are synced till epoch: {}. checking with current epoch: {}".format(
		syncStatus["syncedTillEpoch"], epoch))

	if syncStatus["syncedTillEpoch"] == epoch:
		logger.info("skipping. addresses are already synced till current epoch: {}".format(syncStatus["syncedTillEpoch"]))
		return False

	sql = harmonyData.getRichListSql()
	# logger.info(sql)
	currentAddresses = dbUtil.listResultsWithConn(sql, conn, 10000000)
	# logger.info(currentAddresses)

	logger.info("processing address history")
	inserts = []
	for address in currentAddresses:
		# logger.info("processing address history for: ".format(address["address"]))
		record = harmonyHistory.getCreateHistoryData(epoch, constants.H_HISTORY_ADDRESS,
			address["totalStake"], None, None, address["address"], address["totalBalance"],
			address["totalRewards"])
		inserts.append(record)

	harmonyHistory.batchCreateHistory(conn, inserts)
	logger.info("after processing address history")

	commonUtils.updateSyncStatus(conn, app, constants.H_ADDRESS_HISTORY_SYNC, None, epoch)
	auditUtils.createEvent(conn, app, eventName.syncHarmonyAddressHistory)
	conn.commit()
	return True


def syncDelegates(conn, app, data, event):
	logger.info("in harmony delegation sync")
	startTime = datetime.datetime.now()
	# conn = dbUtil.getConnection()
	# currentTime = datetime.datetime.now()
	# logger.info(body)

	logger.info("processing delegation deletes")
	if data["deletes"] is not None:
		processDelegationDeletes(conn, data["deletes"])

	logger.info("processing delegation inserts")
	if data["inserts"] is not None:
		processDelegationInserts(conn, data["inserts"])

	logger.info("processing delegation updates")
	if data["updates"] is not None:
		processDelegationUpdates(conn, data["updates"])

	conn.commit()

	logger.info("updating balances")
	updateBalances(conn, True)
	conn.commit()

	updateRank(conn, 500)
	conn.commit()

	auditUtils.createEvent(conn, app, eventName.syncHarmonyDelegations)
	auditUtils.audit(conn, app, event, eventName.syncHarmonyDelegations, "service", startTime)

	logger.info("processing finished")


def updateBalances(conn, balanceIncludesStake):
	sql = "update " + tables.haddress + " ad "
	sql += " inner join (select address, sum(stake) as totalStake, sum(reward) as totalRewards "
	sql += " from " + tables.hpooldel + " group by address) pd  "
	sql += " on pd.address=ad.address "
	sql += " set ad.totalStake=pd.totalStake, ad.totalRewards=pd.totalRewards "
	# logger.info(sql)
	adUpdated = conn.cursor().execute(sql)
	logger.info("addresses updated (stake/rewards) are : {0}".format(adUpdated))

	conn.commit()

	sql = "update " + tables.haddress + " ad "
	# if balanceIncludesStake:
	# 	sql += " set ad.totalBalance=(ad.addressBalance + ad.totalRewards), "
	# 	sql += " trackHistory = (case when trackHistory = 'True' then 'True' "
	# 	sql += " when (ad.addressBalance + ad.totalRewards >= " + str(constants.H_MIN_BAL_FOR_HISTORY) + ") then 'True' else 'False' end) "
	# else:
	sql += " set ad.totalBalance=(ad.totalStake + ad.addressBalance + ad.totalRewards), "
	sql += " trackHistory = (case when trackHistory = 'True' then 'True' "
	sql += " when (ad.totalStake + ad.addressBalance + ad.totalRewards >= " + str(constants.H_MIN_BAL_FOR_HISTORY) + " ) then 'True' else 'False' end) "
	# logger.info(sql)
	balUpdated = conn.cursor().execute(sql)
	# logger.info("address updated (total balance) are : {0}".format(balUpdated))
	conn.commit()


def processDelegationDeletes(conn, deletes):
	logger.info("in processDelegationDeletes for {} delegations".format(len(deletes)))
	# logger.info("delegation deletions are: {}".format(deletes))
	deleteRecords = []
	for delegate in deletes:
		deleteRecords.append((delegate["poolDelId"]))

	batchDeleteDelegation(conn, deleteRecords)
	conn.commit()


def processDelegationInserts(conn, inserts):
	logger.info("in processDelegationInserts for {} delegations".format(len(inserts)))
	pools = harmonyData.listHPoolsAsMap(conn)

	insertRecords = []
	for i in inserts:
		if not harmonyData.isAlreadyExistingAddress(conn, i["address"]):
			createAddress(conn, i["address"])

		# if i["validator"] not in pools:
		# 	continue

		pool = pools[i["validator"]]
		args = (pool["hPoolId"], i["address"], i["amount"], i["reward"])
		insertRecords.append(args)

	batchCreateDelegation(conn, insertRecords)
	conn.commit()


def processDelegationUpdates(conn, updates):
	logger.info("in processDelegationUpdates for {} delegations".format(len(updates)))

	updateArgs = []
	for delegate in updates:
		args = (delegate["amount"], delegate["reward"], datetime.datetime.now(), delegate["poolDelId"])
		updateArgs.append(args)

	batchUpdateDelegation(conn, updateArgs)
	conn.commit()


def batchCreateDelegation(conn, delegations):
	if len(delegations) == 0:
		logger.info("nothing to process")
		return

	sql = "insert into " + tables.hpooldel
	sql += " (hPoolId, address, stake, reward) "
	sql += " values(%s, %s, %s, %s) "

	createdCount = conn.cursor().executemany(sql, delegations)
	logger.info("delegations creation requested - {}, update performed - {}".format(
		len(delegations), createdCount))


def batchUpdateDelegation(conn, delegations):
	if len(delegations) == 0:
		logger.info("nothing to process")
		return

	sql = "update " + tables.hpooldel
	sql += " set stake=%s, reward=%s, lastUpdated=%s "
	sql += " where poolDelId = %s"

	updatedCount = conn.cursor().executemany(sql, delegations)
	logger.info("delegations update requested - {}, update performed - {}".format(
		len(delegations), updatedCount))


def batchDeleteDelegation(conn, delegations):
	if len(delegations) == 0:
		logger.info("nothing to process")
		return

	sql = "Delete from " + tables.hpooldel
	sql += " where poolDelId = %s"

	deletedCount = conn.cursor().executemany(sql, delegations)
	logger.info("delegations delete requested - {}, update performed - {}".format(
		len(delegations), deletedCount))


