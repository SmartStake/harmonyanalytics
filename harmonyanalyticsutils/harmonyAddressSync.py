import sys

import requests
from requests import Session

import commonUtils
import constants
import logUtil

logger = logUtil.l()

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
        "balanceIncludesStake": False
    }

    commonUtils.postReq(constants.syncAddressesUrl, addReqDetails)
    logger.info("after syncing all addresses with database")


def processAddresses(addresses, addressMap):
    session = Session()

    logger.info("number of addresses to process: {}".format(len(addresses)))

    i = 0
    updates = []
    inserts = []
    for address in addresses:
        if not allMode and address in addressMap:
            dbAddress = addressMap[address]
            # if int(dbAddress["addressBalance"]) < constants.ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC:
            logger.info("skipping address {} as the balance {} is lower than threshold {} ".format(
                address, int(dbAddress["addressBalance"]), constants.ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC))
            if dbAddress["rank"] is None or dbAddress["rank"] > constants.ADDRESS_MAX_RANK_FOR_TOP_SYNC:
                logger.info("skipping address {} as the rank  / balance {} is lower than threshold {} ".format(
                    address, int(dbAddress["addressBalance"]), constants.ADDRESS_MIN_BALANCE_FOR_FOR_TOP_SYNC))
                continue

        logger.info(address)
        balance = getBalance(session, address)
        record = {"address": address, "balance": balance, "txCount": 0}

        if address in addressMap:
            dbAddress = addressMap[address]
            # logger.info("database address details are: {}".format(dbAddress))
            # logger.info("api address details are: balance - {}".format(balance))
            if round(balance, 0) != round(dbAddress["addressBalance"], 0):
                logger.info("dbAddress: {}; new balance: {}".format(dbAddress, balance))
                logger.info("there are changes in this address, sync it.  - old - {}, new - {}".format(
                    dbAddress["addressBalance"], balance))
                record["addressId"] = dbAddress["addressId"]
                updates.append(record)
            else:
                logger.info("no changes in this address, leave it as is - old - {}, new - {}".format(
                    dbAddress["addressBalance"], balance))
        else:
            inserts.append(record)
        i += 1

    logger.info("updates are:")
    logger.info(len(updates))
    # logger.info(updates)

    logger.info("inserts are:")
    logger.info(len(inserts))

    return updates, inserts


def getBalance(session, address):
    balance = commonUtils.getHarmonyResultDataFromPost(session, constants.BALANCE_URL, [address])
    return commonUtils.divideByTenPower18(balance)

if len(sys.argv) < 3:
    raise Exception("correct syntax is: python harmonyAddressSync dev/prod logsPath TOP/ALL")

logger.info("syncing all addresses")
syncAllAddresses()
logger.info("after syncing all addresses")
