import time
import logging

import commonUtils
import dbUtil
import hTgBot
import harmonyData
import tgBotUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

command = "/nextslots /allnextslots /slots /allslots"

def getCurrentEpochSlots(conn, chatId, userId):
    return getEpochSlots(conn, chatId, userId, True)


def getNextEpochSlots(conn, chatId, userId):
    return getEpochSlots(conn, chatId, userId, False)


def getEpochSlots(conn, chatId, userId, current):
    setting = tgBotUtils.prepUserSettings(conn, chatId, userId, hTgBot.app)

    message2 = None
    message3 = None
    if setting["favPools"] is None or setting["favPools"] == "":
        message = "Favorite validators are not configured. Check /settings command"
    else:
        sql = harmonyData.listPoolsSqlWithIds(hTgBot.app, setting["favPools"])
        # logger.info(sql)
        validators = dbUtil.listResultsWithConn(sql, conn)
        # logger.info(bidDetails)

        if current:
            header = "Current Epoch - "
        else:
            header = "Next Epoch - "
        header += "favorite validators bid slot details: \n"
        response, response2, response3 = getValidatorsSlotMessage(validators, current)

        footer = "\n" + getEpochSummary(conn) + "\n"

        if response3:
            message3 = "..contd - " + header + response3 + footer + command
            message2 = "..contd - " + header + response2 + footer + command
            message = header + response
        elif response2:
            message2 = "..contd - " + header + response2 + footer + command
            message = header + response
        else:
            message = header + response + footer + command

    return message, message2, message3


def getAllNextSlots(conn, chatId, userId):
    return getAllSlots(conn, chatId, userId, False)


def getAllCurrentSlots(conn, chatId, userId):
    return getAllSlots(conn, chatId, userId, True)


def getAllSlots(conn, chatId, userId, current):
    sql, args = harmonyData.listHPoolsSql(None)
    # logger.info(sql)
    validators = dbUtil.listResultsWithConn(sql, conn)
    # logger.info(validators)

    message2 = None
    message3 = None
    if current:
        header = "Current Epoch"
    else:
        header = "Next Epoch"
    header += " - all validators bid ranking details: \n"
    response, response2, response3 = getValidatorsSlotMessage(validators, current)
    # logger.info(len(response))
    # logger.info(len(response2))
    footer = "\n" + getEpochSummary(conn) + "\n"

    if response3:
        message3 = "..contd - " + header + response3 + footer + command
        message2 = "..contd - " + header + response2 + footer + command
        message = header + response
    elif response2:
        message2 = "..contd - " + header + response2 + footer + command
        message = header + response
    else:
        message = header + response + footer + command

    return message, message2, message3


def getValidatorsSlotMessage(validators, current):
    valMap = commonUtils.getMapFromList(validators, "address")
    bidDetails = tgBotUtils.getBidRanks(current)
    header = "Slots | Name \t\t| Count | Bid | Effective Stake | Total Stake\n"

    # capture = header
    capture = ["", "", ""]
    for bid in bidDetails:
        # logger.info(len(capture[0]))
        # if capture[1]:
        #     logger.info(len(capture[1]))

        if bid["address"] not in valMap:
            continue
        validator = valMap[bid["address"]]
        if len(capture[1]) > 3800 :
            capture[2] += getValBidMessage(validator["name"], bid)
        elif len(capture[0]) > 3800 :
            capture[1] += getValBidMessage(validator["name"], bid)
        else:
            capture[0] += getValBidMessage(validator["name"], bid)

    message = header + capture[0]
    message2 = None
    if capture[1]:
        message2 = header + capture[1]

    message3 = None
    if capture[2]:
        message3 = header + capture[2]

    return message, message2, message3


def getValBidMessage(name, valDetails):
    # logger.info("in getValBidMessage")
    # logger.info(name)
    # logger.info(valDetails)
    valName = name
    if valName and len(valName) > 11:
        valName = valName[:11]
    message = "<b>" + valDetails["slot"] + "</b> | "
    message += valName + " | " + str(valDetails["num"]) + " | "
    message += str(int(commonUtils.divideByTenPower18(int(valDetails["bid"])))) + " | "
    if "effective_stake" in valDetails:
        message += str(int(commonUtils.divideByTenPower18(int(valDetails["effective_stake"])))) + " | "
    else:
        message += "\t-\t| "
    message += str(int(commonUtils.divideByTenPower18(int(valDetails["total_stake"])))) + "\n"
    return message


def getEpochSummary(conn):
    coinStat = commonUtils.getCoinStat(conn, hTgBot.app)

    message = "Current Epoch: <b>" + str(coinStat["currentEpoch"]) + "</b>.\n"
    message += "Next epoch starts in: <b>" + str(convertEpochToMinHr(coinStat["nextEpochTime"])) + "</b>.\n"
    return message

def getEpoch(conn):
    coinStat = commonUtils.getCoinStat(conn, hTgBot.app)

    message = "Current Epoch: <b>" + str(coinStat["currentEpoch"]) + "</b>.\n"
    message += "Next epoch starts in: <b>" + str(convertEpochToMinHr(coinStat["nextEpochTime"])) + "</b>.\n"
    message += "Upper median raw stake: " + str(round(coinStat["medianRawStake"] * 1.15)) + ".\n"
    message += "Median raw stake: " + str(round(coinStat["medianRawStake"])) + ".\n"
    message += "Lower median raw stake: " + str(round(coinStat["medianRawStake"] * 0.85)) + ".\n"
    message += "/menu"
    return message


def convertEpochToMinHr(epoch):
    currentTime = int(time.time())
    timeLeft = epoch - currentTime
    minLeft = round(timeLeft/60)
    hrLeft = round(timeLeft/3600, 1)

    return str(minLeft) + " minutes or " + str(hrLeft) + " hours"
