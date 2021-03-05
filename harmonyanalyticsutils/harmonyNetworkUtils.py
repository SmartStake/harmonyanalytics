from datetime import datetime

import commonUtils
import constants
import logUtil

logger = logUtil.l()

def processStakingTransaction(session, transaction, shardId=0):
    txReceipt = getTxReceipt(session, transaction["hash"], shardId)
    # logger.info(transaction)
    details = {"txType": transaction["type"], "blockNumber": transaction["blockNumber"],
        "epochTimestamp": transaction["timestamp"], "txHash": transaction["hash"],
        "txDate": getTxDate(transaction), "txCategory": constants.TX_STAKING,
        "status": getStatus(txReceipt), "nonce": transaction["nonce"],
        "shardId": 0, "toShardId": 0, "type": transaction["type"],
        "blockHash": transaction["blockHash"], "txFee": transaction["gas"]/transaction["gasPrice"],
        "txIndex": transaction["transactionIndex"], }

    if transaction["type"] == constants.H_EVENT_DELEGATE or transaction["type"] == constants.H_EVENT_UNDELEGATE:
        details["address"] = transaction["msg"]["delegatorAddress"]
        details["validatorAddress"] = transaction["msg"]["validatorAddress"]
        details["toAddress"] = transaction["msg"]["validatorAddress"]
        details["amount"] = commonUtils.getHarmonyCoins(transaction["msg"]["amount"])
    elif transaction["type"] == constants.H_EVENT_COLLECT_REWARDS:
        details["address"] = transaction["msg"]["delegatorAddress"]
        details["toAddress"] = None
        amount = getAmountFromTransactionReceipt(session, transaction["hash"], shardId)
        if amount is None:
            return None
        details["amount"] = amount
    elif transaction["type"] == constants.H_EVENT_EDIT_VALIDATOR:
        details["address"] = transaction["msg"]["validatorAddress"]
        details["validatorAddress"] = transaction["msg"]["validatorAddress"]
        details["toAddress"] = transaction["msg"]["validatorAddress"]
        #TEMP code
        # transaction["msg"]["commissionRate"] = 122999999999999
        details["msg"] = transaction["msg"]
        # logger.info("edit validator details: {}".format(details))
        # details["eventDetails"] = transaction
        details["amount"] = None
    elif transaction["type"] == constants.H_EVENT_CREATE_VALIDATOR:
        details["address"] = transaction["msg"]["validatorAddress"]
        details["validatorAddress"] = transaction["msg"]["validatorAddress"]
        details["toAddress"] = transaction["msg"]["validatorAddress"]
        details["msg"] = transaction["msg"]
        details["amount"] = None
    else:
        logger.info("skipping event is: {}".format(details))
        raise Exception("skipping event: {}".format(details))

    # logger.info("processed event is: {}".format(details))
    return details


def getTxDate(transaction):
    txEpochTimestamp = transaction["timestamp"]
    # logger.info("txEpochTimestamp: {}".format(txEpochTimestamp))

    txDate = datetime.fromtimestamp(txEpochTimestamp).strftime('%Y-%m-%d')
    # txDate = time.strftime('%Y-%m-%d', txEpochTimestamp)
    # logger.info("transaction: {}, txDate: {}".format(transaction, txDate))

    return txDate

def getAmountFromTransactionReceipt(session, txHash, shardId=0):
    transactionReceipt = getTxReceipt(session, txHash, shardId)

    if not transactionReceipt or transactionReceipt["status"] != 1:
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

    # logger.info("amount from - {} is: {}".format(data, amount))
    return amount


def getTxReceipt(session, txHash, shardId=0):
    transactionReceipt = commonUtils.getHarmonyResultDataFromPostByShard(session,
        shardId, constants.TRANSACTION_RECEIPT_URL, [txHash])
    # logger.info("transaction receipt for {}, is: {}".format(txHash, transactionReceipt))

    if not transactionReceipt or "status" not in transactionReceipt:
        logger.info(" transactionReceipt is None. returning none")
        return None

    return transactionReceipt


def getStatus(txReceipt):
    status = constants.TX_STATUS_SUCCESS
    if not txReceipt:
        status = constants.TX_STATUS_UNKNOWN
    elif txReceipt["status"] != 1:
        status = constants.TX_STATUS_FAILED

    return status


def getLatestBlock(session, baseUrl):
    data = commonUtils.getHarmonyResultDataFromPostAndUrl(session, constants.LATEST_HEADER_URL, baseUrl)
    # logger.info("getLatestBlock from {} : {}".format(baseUrl, data))
    blockNumber = data["blockNumber"]

    return blockNumber


def getLatestBlockDetails(session, baseUrl):
    data = commonUtils.getHarmonyResultDataFromPostAndUrl(session, constants.LATEST_HEADER_URL, baseUrl)
    # logger.info("getLatestBlock from {} : {}".format(baseUrl, data))
    return data

