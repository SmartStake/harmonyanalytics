import sys

import requests
from requests import Session
import commonUtils
import constants
import logUtil

logger = logUtil.l()

if len(sys.argv) < 4:
    raise Exception("correct syntax is: python harmonyAddressSync dev/prod logsPath TOP/ALL")

allMode = True
if sys.argv[3] == 'TOP':
    allMode = False
logger.info("is all mode: {} ".format(allMode))

def syncAllAddresses():
    session = Session()

    r = requests.get(constants.ADDRESS_URL)
    addressesData = r.json()
    # logger.info(addressesData)
    networkAddresses = addressesData["address"]

    logger.info("obtaining db address list")
    dbAddresses = commonUtils.getDataFromGet(session, constants.listAllAddressesBasicUrl)
    logger.info("preparing db address map for {} addresses".format(len(dbAddresses)))
    addressMap = commonUtils.getMapFromList(dbAddresses, "address")

    logger.info("processing addresses")
    updates, inserts = processAddresses(networkAddresses, addressMap)

    logger.info("syncing all addresses with database")
    addReqDetails = {"type": "addressSync",
        "updates": updates, "inserts": inserts,
        "balanceIncludesStake": False, "allMode": allMode,
    }

    commonUtils.postReq(constants.syncAddressesUrl, addReqDetails)
    logger.info("after syncing all addresses with database")


def processAddresses(addresses, addressMap):
    session = Session()

    logger.info("number of addresses to process: {}".format(len(addresses)))
    if 'one1v8slq3ajf7kmhrskrrupp7dewvnqnmmdlfezfu' in addressMap:
        logger.info("in db: {}".format(addressMap["one1v8slq3ajf7kmhrskrrupp7dewvnqnmmdlfezfu"]))

    i = 0
    updates = []
    inserts = []
    processedAddresses = set()
    for address in addresses:
        if address in processedAddresses:
            continue
        processedAddresses.add(address)
        # if address != 'one1rhjzv8alvwg3an7ulg67e38md4zvsvcuyc7uh7':
        #     continue
        if not allMode and address in addressMap:
            dbAddress = addressMap[address]
            # if int(dbAddress["addressBalance"]) < constants.ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC:
            # logger.info("skipping address {} as the balance {} is lower than threshold {} ".format(
            #     address, int(dbAddress["addressBalance"]), constants.ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC))
            if dbAddress["ranking"] is None or dbAddress["ranking"] > constants.ADDRESS_MAX_RANK_FOR_TOP_SYNC:
                logger.info("skipping address {} as the ranking  / balance {} is lower than threshold {} ".format(
                    address, dbAddress["ranking"], constants.ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC))
                continue

        # logger.info(address)
        balance = getBalance(session, address)
        record = {"address": address, "balance": balance, "txCount": 0}

        if address in addressMap:
            dbAddress = addressMap[address]
            # logger.info("database address details are: {}".format(dbAddress))
            # logger.info("api address details are: balance - {}".format(balance))
            if round(balance, 0) != round(dbAddress["addressBalance"], 0):
                # logger.info("dbAddress: {}; new balance: {}".format(dbAddress, balance))
                # logger.info("there are changes in this address, sync it.  - old - {}, new - {}".format(
                #     dbAddress["addressBalance"], balance))
                record["addressId"] = dbAddress["addressId"]
                updates.append(record)
            # else:
            #     logger.info("no changes in this address, leave it as is - old - {}, new - {}".format(
            #         dbAddress["addressBalance"], balance))
            # del addressMap[address]
        else:
            # logger.info("adding record to inserts: {}".format(record))
            inserts.append(record)
        i += 1
        if i % 100 == 0:
            logger.info("processed {} addresses. # of inserts: {}, # of updates: {}".format(
                i, len(inserts), len(updates)))

    logger.info("updates are: {}".format(len(updates)))
    logger.info("inserts are: {}".format(len(inserts)))

    if allMode:
        logger.info("missing but existing addresses are: {}".format(len(inserts)))
        i = 0
        for dbAddress in addressMap.values():
            if dbAddress["address"] in processedAddresses:
                continue
            processedAddresses.add(dbAddress["address"])
            # if dbAddress["address"] != 'one1rhjzv8alvwg3an7ulg67e38md4zvsvcuyc7uh7':
            #     continue
            result = processExistingButMissing(session, dbAddress)
            if result:
                updates.append(result)
            i += 1
            if i % 100 == 0:
                logger.info("existing address processing: {}, addresses. # of updates: {}".format(
                    i, len(updates)))

    logger.info("final updates are: {}".format(len(updates)))
    return updates, inserts


def processExistingButMissing(session, dbAddress):
    address = dbAddress["address"]
    balance = getBalance(session, address)
    record = {"address": address, "balance": balance, "txCount": 0}

    if round(balance, 0) != round(dbAddress["addressBalance"], 0):
        # logger.info("dbAddress: {}; new balance: {}".format(dbAddress, balance))
        # logger.info("there are changes in this address, sync it.  - old - {}, new - {}".format(
        #     dbAddress["addressBalance"], balance))
        record["addressId"] = dbAddress["addressId"]
        return record

    # logger.info("{} - no changes in this address, leave it as is - old - {}, new - {}".format(
    #     address, dbAddress["addressBalance"], balance))
    return None



def getBalance(session, address):
    balance = commonUtils.getHarmonyResultDataFromPost(session, constants.BALANCE_URL, [address])
    return commonUtils.divideByTenPower18(balance)

logger.info("syncing all addresses")
syncAllAddresses()
logger.info("after syncing all addresses")
