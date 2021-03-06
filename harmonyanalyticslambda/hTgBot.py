import datetime
import json
import logging

import requests

import auditUtils
import commonUtils
import constants
import dbUtil
import eventName
import hTgEpochUtils
import harmonyData
import rds_config
import tables
import tgBotUtils
import tgConstants
import tgNotificationSettings

# from telegram.ext import Updater

app = 'HARMONY'
SS_VAL_ID=rds_config.DEFAULT_POOL_ID

SET_FAV_VALIDATORS = "{0} &lt;validator_address1&gt;, .. &lt;validator_address_n&gt; - set up favorite validators (comma separated list of validator addresses). Example: {0} one1qk7mp94ydftmq4ag8xn6y80876vc28q7s9kpp7,one1leh5rmuclw5u68gw07d86kqxjd69zuny3h23c3\n"
SET_ADDRESS = "/setaddress &lt;address&gt; - configure an address for address/rewards tracking. Enter one or more full $ONE addresses after the command (separated by comma). Each address should be separated by comma. Example: /setaddress one1qk7mp94ydftmq4ag8xn6y80876vc28q7s9kpp7,one1leh5rmuclw5u68gw07d86kqxjd69zuny3h23c3 \n"
SET_ALIAS = "/setalias &lt;alias name&gt; - configure an alias for address/rewards. Enter existing alias name after the command. The alias needs to be existing with <a href='https://harmony.smartstake.io/rewards'>Smart Stake</a> rewards dashboard. If both alias and address are set, alias is used in account details. Example: /setalias ss\n"
RESET = "/reset - reset all settings\n"

INV_SYNTAX_PREFIX = "Invalid syntax used. Correct syntax is: "
FAV_POOL_INVALID_SYNTAX = INV_SYNTAX_PREFIX + SET_FAV_VALIDATORS
SET_ADDRESS_INVALID_SYNTAX = INV_SYNTAX_PREFIX + SET_ADDRESS

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# bot = telegram.Bot(token=rds_config.TOKEN)
# updater = Updater(token=rds_config.TOKEN, use_context=True)
# dispatcher = updater.dispatcher
SUPPORT_US = "\nLike our tools? Consider supporting us by staking with Smart Stake.\n"

AVAILABLE_COMMANDS = "Available commands are /account /allelected /alleligible /epoch /health /slots /nextslots /allslots /allnextslots /menu /sshealth /about /contactus /start \n"
AVAILABLE_COMMANDS_GROUP = "Available commands are /allelected /alleligible /epoch /health /slots /nextslots /allslots /allnextslots /menu /sshealth /about /contactus /start \n"


def tgHandler(event, context):
	startTime = datetime.datetime.now()
	data = json.loads(event["body"])
	# logger.info(event)
	# logger.info(data)

	if "message" in data:
		message = data["message"]
	elif "edited_message" in data:
		message = data["edited_message"]
	else:
		return tgBotUtils.SUCCESS_RESPONSE

	# logger.info(message)
	chatType = message["chat"]["type"]
	if chatType == "group" or chatType == "supergroup":
		logger.info("group request")
		return groupHandler(message, startTime)

	return individualHandler(message, startTime)


def groupHandler(message, startTime):
	# logger.info("group request")

	chatId = message["chat"]["id"]
	textCmd, skip = tgBotUtils.validateAndGetText(chatId, message, startTime)
	if skip:
		return skip

	if not textCmd:
		logger.info("invalid group request: message: {}".format(message))
		return tgBotUtils.missingTextError(chatId, message, startTime)

	userId = message["from"]["id"]

	conn = dbUtil.getConnection()
	response, response2, response3, handled, keyboard = handleCommonCommands(False, textCmd, conn, chatId, userId)

	if not handled:
		if "/setaddress" in textCmd:
			response = "This command is not available in a group chat"
		elif textCmd == "/account":
			response = "This command is not available in a group chat"
		else:
			logger.info("in else. not calling anything")

	return sendResponse(False, response, response2, response3, keyboard, conn, chatId, textCmd, startTime)


def handleCommonCommands(individual, textCmd, conn, chatId, userId):
	if individual:
		response = AVAILABLE_COMMANDS
	else:
		response = AVAILABLE_COMMANDS_GROUP
	logger.info("request is: " + str(textCmd))
	handled = True

	response2, response3, keyboard = None, None, None
	if textCmd.startswith("/start") or textCmd.startswith("/menu"):
		response = getStarted(individual)
	elif textCmd.startswith("/sshealth"):
		response = getSmartStakeHealth(conn)
	elif textCmd.startswith("/contactus"):
		response = getContactUs()
	elif textCmd.startswith("/about"):
		response = getAbout()
	elif textCmd.startswith("/smartstake") or textCmd.startswith("/ss"):
		response = getSmartStake(conn)
	elif textCmd.startswith("/healthsummary"):
		response = getHealthSummary(conn, chatId, userId)
	elif textCmd.startswith("/health"):
		response = getHealth(conn, chatId, userId)
	elif textCmd.startswith("/allelected"):
		response = listAllElected(conn)
	elif textCmd.startswith("/alleligible"):
		response = listAllEligible(conn)
	elif textCmd.startswith("/setfav"):
		response = setFavValidators(conn, chatId, None, textCmd)
	elif textCmd.startswith("/addfav"):
		response = addFavValidators(conn, chatId, None, textCmd)
	elif textCmd.startswith("/epoch"):
		response = hTgEpochUtils.getEpoch(conn)
	elif textCmd.startswith("/slots"):
		response, response2, response3 = hTgEpochUtils.getCurrentEpochSlots(conn, chatId, userId)
	elif textCmd.startswith("/nextslots"):
		response, response2, response3 = hTgEpochUtils.getNextEpochSlots(conn, chatId, userId)
	elif textCmd.startswith("/allslots"):
		response, response2, response3 = hTgEpochUtils.getAllCurrentSlots(conn, chatId, userId)
	elif textCmd.startswith("/allnextslots"):
		response, response2, response3 = hTgEpochUtils.getAllNextSlots(conn, chatId, userId)
	elif textCmd.startswith("/reset"):
		tgBotUtils.reset(conn, chatId, app)
		response = "Settings are reset. Use /start to get started.\n"
	elif textCmd.startswith("/settings"):
		response = getSettings(conn, chatId, userId)
	elif textCmd.startswith(tgConstants.MAIN_MENU):
		response = getStarted(individual)
	elif textCmd.startswith(tgConstants.ENABLE_CMD_KEY):
		response, keyboard = tgNotificationSettings.updateSetting(conn, chatId, userId, textCmd, tgConstants.ENABLE_CMD_KEY)
	elif textCmd.startswith(tgConstants.DISABLE_CMD_KEY):
		response, keyboard = tgNotificationSettings.updateSetting(conn, chatId, userId, textCmd, tgConstants.DISABLE_CMD_KEY)
	else:
		handled, resp, keyb = tgNotificationSettings.handleNotificationCommands(conn, chatId, userId, textCmd)
		if handled:
			response = resp
			keyboard = keyb

	# logger.info("response: {}, handled: {}".format(response, handled))
	return response, response2, response3, handled, keyboard


def sendResponse(individual, response, response2, response3, keyboard, conn, chatId, textCmd, startTime):
	# logger.info("individual: {}, response: {}, chatId: {}, textCmd: {}, startTime: {}".format(
	# 	individual, response, chatId, textCmd, startTime))

	if individual:
		if keyboard:
			# reply_markup = {'inline_keyboard': inlineKeyboard}
			reply_markup = {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': True}
		else:
			keyboard = [['/account', '/epoch'],['/healthsummary', '/health'], ['/nextslots', '/settings'], ['Delegate Notifications', 'Validator Notifications']]
			# keyboard = [['/healthsummary', '/health'], ['/sshealth', '/settings'], ["/menu", "/about"]]
			reply_markup = {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': True}
		reply_markup = json.dumps(reply_markup)
		# logger.info(reply_markup)
		respData = {"text": response.encode("utf8"), "chat_id": chatId, "reply_markup": reply_markup}
	else:
		if keyboard:
			# reply_markup = {'inline_keyboard': json.dumps(inlineKeyboard)}
			reply_markup = {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': True}
			reply_markup = json.dumps(reply_markup)
			respData = {"text": response.encode("utf8"), "chat_id": chatId, "reply_markup": reply_markup}
		else:
			respData = {"text": response.encode("utf8"), "chat_id": chatId}

	preview = False
	url = rds_config.TG_BASE_URL + "/sendMessage?parse_mode=html"
	if not preview:
		url += "&disable_web_page_preview=true"

	# logger.info("before sending response: " + url)
	requests.post(url, respData)
	# logger.info("after sending response")

	if response2:
		respData2 = {"text": response2.encode("utf8"), "chat_id": chatId}
		requests.post(url, respData2)

	if response3:
		respData3 = {"text": response3.encode("utf8"), "chat_id": chatId}
		requests.post(url, respData3)

	audit(conn, chatId, textCmd, startTime)

	return tgBotUtils.SUCCESS_RESPONSE


def individualHandler(message, startTime):
	logger.info("individual request")

	chatId = message["chat"]["id"]
	textCmd, skip = tgBotUtils.validateAndGetText(chatId, message, startTime)
	if skip:
		return skip

	userId = message["from"]["id"]

	conn = dbUtil.getConnection()
	response, response2, response3, handled, keyboard = handleCommonCommands(True, textCmd, conn, chatId, userId)

	if not handled:
		if "/setaddress" in textCmd:
			response = setAddress(conn, chatId, textCmd)
		elif textCmd == "/account":
			response = getAccount(conn, chatId, userId)
		else:
			logger.info("in else. not calling anything")

	return sendResponse(True, response, response2, response3, keyboard, conn, chatId, textCmd, startTime)


def audit(conn, chatId, url, startTime, urlParams=None):
	auditUtils.auditBot(conn, chatId, url, startTime, urlParams)
	conn.close()


def getContactUs():
	message = "Questions? <a href='t.me/SmartStake'>Contact us</a> on Telegram. \n"
	message += SUPPORT_US
	message += "/menu"

	return message


def getSmartStakeHealth(conn):
	ssHealth = getSSHealthDetails(conn)
	signMessage = getSignatureSummary(conn, SS_VAL_ID)
	summary = getPoolPerfSummary(conn, SS_VAL_ID)

	message = "Smart Stake health. \n"
	message += "Last node health check: <b>" + str(ssHealth["tsLastCheck"]) + "</b> minutes ago.\n"
	message += "Node health - <b>" + str(ssHealth["healthStatus"]) + "</b>\n\n"
	message += summary + "\n"
	message += signMessage

	# message += SUPPORT_US
	message += getToolsLink("val", SS_VAL_ID)

	return message

def getPoolPerfSummary(conn, poolId):
	pool = harmonyData.getHPoolById(conn, poolId)

	summary = "Validator Perf Summary:\n"

	summary += "8och: ER: <b>" + str(pool["currentApr"]) + "</b>.\t"
	summary += "ERI: <b>" + str(pool["currentEri"]) + "</b>.\n"
	summary += "Prev Epoch: ER: <b>" + str(pool["prevEpochApr"]) + "</b>.\t"
	summary += "ERI: <b>" + str(pool["prevEpochEri"]) + "</b>.\n"
	summary += "Average: ER: <b>" + str(pool["avgApr"]) + "</b>.\t"
	summary += "ERI: <b>" + str(pool["avgEri"]) + "</b>.\n"


	return summary

def getSignatureSummary(conn, hPoolId):
	coinStat = commonUtils.getCoinStat(conn, app)

	hourlyChartData = harmonyData.getPerfChartData(conn, hPoolId, True, constants.H_HOUR_MODE, 'false')
	message = "Hourly Performance:\n"
	message += getHourlyPerfSummary(hourlyChartData)

	epochChartData = harmonyData.getEpochChartData(conn, hPoolId, 'false', coinStat["currentEpoch"])
	message += "\nEpoch Performance:\n"
	message += getEpochPerfSummary(epochChartData)

	return message

def getHourlyPerfSummary(data):
	message = "Date/Time (GMT) | Signed | Missed | Sign %\n"

	currentPerf, specialMessage = None, ""
	i = 0
	for hourData in reversed(data):
		message += hourData["title"] + " | " + str(hourData["signed"]) +  " | "
		message += str(hourData["notSigned"]) +  " | <b>" + str(hourData["signPer"]) + "</b>\n"
		# if i == 0:
		# 	currentPerf = hourData
		if hourData["signPer"] < 90:
			specialMessage = "<b>Blocks signing rate is not good enough. Contact validator operator.</b>\n"
		if i > 2:
			break
		i += 1

	message = specialMessage + message
	# if currentPerf:
	# 	for hourData in reversed(data):
	# 		if hourData["signPer"] < 90:
	# 			specialMessage = "<b>Blocks signing rate is not good enough. Contact validator operator.</b>\n"
	# 			message = specialMessage + message
	# 			break

	return message


def getEpochPerfSummary(data):
	message = "Epoch | Signed | Missed | Sign %\n"

	currentPerf, specialMessage = None, ""
	i = 0
	for epochData in reversed(data):
		message += str(epochData["title"]) + " | " + str(epochData["signed"]) +  " | "
		message += str(epochData["notSigned"]) +  " | <b>" + str(epochData["signPer"]) + "</b>\n"
		if i == 0 and epochData["signPer"] < 90:
			# currentPerf = epochData
			specialMessage = "<b>Epoch signing rate is not good enough. Contact validator operator.</b>\n"
		elif i > 2:
			break
		i += 1

	message = specialMessage + message
	# if currentPerf:
	# 	for epochData in reversed(data):
	# 		if epochData["signPer"] < 90:
	# 			logger.info(epochData)
	# 			specialMessage = "<b>Epoch signing rate is not good enough. Contact validator operator.</b>\n"
	# 			message = specialMessage + message
	# 			break

	return message


def getStarted(individualCall):
	message = "HarmonyAnalyticsBot allows assessing the staking aspects of Harmony and provides basic performance monitoring. Use /menu command to see all available commands. \n"
	message += " \n"

	if individualCall:
		message += "/account - show account details including rewards for all your addresses. \n"
	# message += "/arr - show expected and actual ARR for network and pools you stake with. \n"

	message += "/allelected - show performance of all elected Harmony validators. \n"
	message += "/alleligible - show performance of all eligible (excludes elected) Harmony validators. \n"
	message += "/health - show performance of favorite Harmony validators. \n"
	message += "/healthsummary - show performance summary of favorite Harmony validators. \n"
	# if individualCall:
	# message += "/links - show useful links related to Harmony/staking. \n"
	# message += "/mcap - show market cap of Harmony. \n"
	message += "/menu - show all available commands. \n"
	# if individualCall:
	message += "/settings - show available settings and their current values. \n"
	message += "/notifications - show available notifications. \n"
	message += "/slots - for elections - shows the current epoch's bid slots for favorite validators. \n"
	message += "/nextslots - for elections - shows the next epoch's bid slots for favorite validators. \n"
	message += "/allslots - for elections - shows the current epoch's bid slots for all validators. \n"
	message += "/allnextslots - for elections - shows the next epoch's bid slots for all validators. \n"

	message += "/sshealth - show health details of Smart Stake validator nodes \n"
	message += "/smartstake - Smart Stake validator pool details:\n"
	message += "/about - What is Smart Stake?. \n"
	message += "/contactus - contact us if you have any questions or feedback. \n"
	# message += "/stats - show staking statistics. \n"

	return message


def getSSHealthDetails(conn):
	sql = "select round(time_to_sec((TIMEDIFF(NOW(), checkupTime))) / 60,0) as tsLastCheck, "
	sql += " (case when heightGap between -4 and 4 then 'Good' when heightGap not between -4 and 4 then 'Bad' else null end) as healthStatus "
	sql += " from  " + tables.nodehealth + " nh"
	sql += " where symbol=%s"
	sql += " order by checkupTime desc"
	sql += " limit 1"
	# logger.info(sql)
	resp = dbUtil.getSingleRecordNoJsonWithConn(sql, conn, app)
	# logger.info(resp)
	return resp


def getToolsLink(page, param=None):
	part = page
	if param:
		part += "/" + str(param)

	return "<a href='https://harmony.smartstake.io/" + part + "'>More Details</a>\t /menu\n"


def getAbout():
	message = "Smart Stake is a staking validator on Harmony protocol. \n"
	message += "Smart Stake uniqely positions itself by providing easy to use tools for assessing validator and network performance. \n"
	message += "Smart Stake uses active-active redundancy with high-end servers hosted with different providers. \n"
	message += "Check Smart Stake validator health using /sshealth. \n"
	message += SUPPORT_US
	message += "/menu"

	return message

def getSmartStake(conn):
	lastUpdatedGap = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyValidators)
	# logger.info(lastUpdatedGap)
	pool = harmonyData.getHPoolById(conn, SS_VAL_ID)
	# conn.close()

	message = "Smart Stake validator details:\n"
	message += getTgValDetails(conn, pool, lastUpdatedGap)
	message += getToolsLink("")

	return message


def getHealthSummary(conn, chatId, userId):
	setting = tgBotUtils.prepUserSettings(conn, chatId, userId, app)

	if setting["favPools"] is None or setting["favPools"] == "":
		message = "Favorite validators are not configured. Check /settings command"
	else:
		sql = harmonyData.listPoolsSqlWithIds(app, setting["favPools"])
		# logger.info(sql)
		validators = dbUtil.listResultsWithConn(sql, conn)
		lastUpdatedGap = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyValidators)

		i = 1
		message = "List of favorite validators: \n"
		message += "Last updated: <b>" + str(int(lastUpdatedGap/60)) + "</b> minutes ago.\n"
		message += "#  | Name | \tStaked | \tAvg ERI | \tCurrent ERI\n"
		for validator in validators:
			message += getValSummary(validator, i)
			# message += "#" + str(i) + " - " + getTgValSummary(conn, validator, lastUpdatedGap)
			i += 1
		message += getToolsLink("") + " /healthsummary"


	# logger.info(message)
	return message


def getHealth(conn, chatId, userId):
	setting = tgBotUtils.prepUserSettings(conn, chatId, userId, app)

	if setting["favPools"] is None or setting["favPools"] == "":
		message = "Favorite validators are not configured. Check /settings command"
	else:
		sql = harmonyData.listPoolsSqlWithIds(app, setting["favPools"])
		# logger.info(sql)
		validators = dbUtil.listResultsWithConn(sql, conn)
		lastUpdatedGap = commonUtils.getEventLastUpdated(conn, eventName.syncHarmonyValidators)

		i = 1
		message = "List of favorite validators: \n"
		message += "Last updated: <b>" + str(int(lastUpdatedGap/60)) + "</b> minutes ago.\n\n"
		for validator in validators:
			message += "#" + str(i) + " - " + getTgValDetails(conn, validator, None)
			i += 1
			message += "\n"
		message += getToolsLink("") + " /health"


	# logger.info(message)
	return message


def getTgValDetails(conn, val, lastUpdatedGap=None):
	message = "Validator: " + getValLink(val["name"], val["hPoolId"]) + ".\n"
	if lastUpdatedGap is not None:
		message += "Last updated: <b>" + str(int(lastUpdatedGap/60)) + "</b> minutes ago.\n"
	message += "Total Stake: <b>" + str(round(val["totalStaked"])) + "</b>.\n"
	# message += "Total Delegates: <b>" + str(val["uniqueDelegates"]) + "</b>.\n"
	message += "Avg Expected Return: <b>" + str(val["avgApr"]) + "</b>.\n"
	message += "Avg ERI: <b>" + str(val["avgEri"]) + "</b>.\n\n"
	message += "Current ERI: <b>" + str(val["currentEri"]) + "</b>.\n\n"
	message += getSignatureSummary(conn, val["hPoolId"])
	return message


def getValLink(name, poolId):
	return "<a href='https://harmony.smartstake.io/val/" + str(poolId) + "'>" + name + "</a>"


def listAllElected(conn):
	return listAllByStatus(conn, constants.H_ELECTED)

def listAllEligible(conn):
	return listAllByStatus(conn, constants.H_ELIGIBLE)

def listAllByStatus(conn, status):
	sql, args = harmonyData.listHPoolsSql(status, " avgEri desc")
	# logger.info(sql)
	validators = dbUtil.listResultsWithConn(sql, conn, args)
	# logger.info(validators)

	message = "List of all validators:\n"
	message += "#  | Name | \tStaked | \tAvg ERI | \tCurrent ERI\n"

	i = 1
	for val in validators:
		message += getValSummary(val, i)
		i += 1
		# if i > 95:
		#     break
	message += getToolsLink("")

	# conn.close()
	# logger.info(message)
	return message


def getValSummary(val, ranking):

	valName = val["name"]
	if valName and len(valName) > 11:
		valName = valName[:11]
	if not valName and len(val["address"]) > 10:
		valName = val["address"][:9]

	avgEri = val["avgEri"]
	if not avgEri:
		avgEri = 0

	currentEri = val["currentEri"]
	if not currentEri:
		currentEri = 0

	message = str(ranking) + " | " + getValLink(valName, val["hPoolId"]) + " | \t"
	message += str(int(val["totalStaked"])) + " | \t"
	message += str(avgEri) + " | \t"
	message += "<b>" + str(currentEri) + "</b>\n"

	return message

def setFavValidators(conn, chatId, userId, inputMessage):
	invalidSyntaxMsg = FAV_POOL_INVALID_SYNTAX.format("/setfav")
	tgBotUtils.prepUserSettings(conn, chatId, userId, app)
	message = tgBotUtils.getParam(inputMessage, "/setfav", invalidSyntaxMsg)

	if len(message) == 0:
		return invalidSyntaxMsg

	pools = message.split(",")
	return updateFavValidators(conn, chatId, pools, invalidSyntaxMsg)


def addFavValidators(conn, chatId, userId, inputMessage):
	invalidSyntaxMsg = FAV_POOL_INVALID_SYNTAX.format("/addfav")

	setting = tgBotUtils.prepUserSettings(conn, chatId, userId, app)
	message = tgBotUtils.getParam(inputMessage, "/addfav", invalidSyntaxMsg)

	if len(message) == 0:
		return invalidSyntaxMsg

	# logger.info("checking current favorites")
	currentFavs = setting["favPools"]
	combinedPools = set()
	if currentFavs:
		# logger.info(currentFavs)
		currentPools = currentFavs.split(",")
		# logger.info(currentPools)
		for p in currentPools:
			# logger.info(combinedPools)
			validator = harmonyData.getHPoolById(conn, p)
			combinedPools.add(validator["address"])
	# logger.info("after for loop: {}".format(combinedPools))

	pools = message.split(",")
	combinedPools.update(pools)
	# logger.info("with new pools are: {}".format(combinedPools))

	return updateFavValidators(conn, chatId, combinedPools, invalidSyntaxMsg)


def updateFavValidators(conn, chatId, pools, invalidSyntaxMsg):
	favs = ""
	poolsList = ""
	# conn = dbUtil.getConnection()
	# logger.info("current pools are: {}".format(pools))
	for p in pools:
		address = p.strip()
		if len(address) == 0:
			# logger.info("address lenth is 0: {}".format(address))
			return invalidSyntaxMsg

		poolDb = harmonyData.getHarmonyPool(conn, address)
		if poolDb is None:
			return invalidSyntaxMsg

		if len(poolsList) != 0:
			favs += ", "
			poolsList += ","

		poolsList += str(poolDb["hPoolId"])
		favs += poolDb["name"] + " - " + str(poolDb["address"])

	if len(poolsList) == 0:
		return invalidSyntaxMsg

	tgBotUtils.updateSetting(conn, chatId, "favPools", poolsList, app)

	# conn.close()

	resp = "Favorite pools set are: " + favs +  ". /menu"
	return resp



def getSettings(conn, chatId, userId):
	setting = tgBotUtils.prepUserSettings(conn, chatId, userId, app)

	if not setting["favPools"] and not setting["address"]:
		message = "You can setup the following settings:\n"
		message += "1 - " + SET_FAV_VALIDATORS.format("/setfav or /addfav") + "\n"
		message += "\n2 - " + SET_ADDRESS
		message += "\n2 - " + RESET
	else:
		message = "You have/can setup the following settings:\n"
		message += "1 - " + SET_FAV_VALIDATORS.format("/setfav or /addfav") + "\n"
		message += getConfiguredPools(conn, setting)
		message += "\n2 - " + SET_ADDRESS
		if setting["address"] is not None and setting["address"] != "":
			message += "\t - " + setting["address"] + "\n"
		message += "\n2 - " + RESET

	message += "/menu"
	return message


def getConfiguredPools(conn, setting):
	configuredPools = setting["favPools"]

	if configuredPools is None or configuredPools == "":
		return ""

	configuredPoolList = configuredPools.split(",")

	sql, args = harmonyData.listHPoolsSql(None, " avgEri desc")
	validators = dbUtil.listResultsWithConn(sql, conn, args)

	message = ""
	# logger.info("all validators: {}".format(validators))
	# logger.info("processing configured pools")
	for cp in configuredPoolList:
		# logger.info("processing {}".format(cp))
		for validator in validators:
			# logger.info("comparing cp {} with validator {} ".format(cp, validator["hPoolId"]))
			if cp == str(validator["hPoolId"]):
				# logger.info("found validator")
				message += "\t - " + validator["name"] + " - " + validator["address"] + "\n"
				break
	# logger.info(message)
	return message


def setAddress(conn, chatId, inputMessage):
	# logger.info("in setAddress")
	# logger.info(inputMessage)
	message = tgBotUtils.getParam(inputMessage, "/setaddress", SET_ADDRESS_INVALID_SYNTAX)

	if len(message) == 0:
		return SET_ADDRESS_INVALID_SYNTAX

	address = message.replace(" ", "")
	# logger.info(address)

	addressList = address.split(",")
	for a in addressList:
		if not harmonyData.isAlreadyExistingAddress(conn, a):
			return "The address used is not known to Smart Stake tools. Please check again. If this is an issue, please /contactus"

	tgBotUtils.updateSetting(conn, chatId, "address", address, app)
	# conn.close()
	return "Successfully registered address. /menu"


def getAccount(conn, chatId, userId):
	# conn = dbUtil.getConnection()
	setting = tgBotUtils.prepUserSettings(conn, chatId, userId, app)

	if not setting["address"]:
		return "Rewards address is not configured. Check /settings command"

	coin = dbUtil.getSingleRecordNoJsonWithConn(commonUtils.getCoinStatSql(), conn, app)

	# logger.info("starting reward processing")

	# logger.info("searching by address")
	rewards = dbUtil.listResultsWithConn(searchByAddressSql(setting["address"]), conn)

	totalOne = getTotalOne(conn, rewards)
	message, totals = getRewardsMessage(coin, rewards, totalOne)
	# logger.info("rewards message: " + message)

	header = "Account Summary: \n"
	header += totals + "\n"
	header += "Rank \t | Address\t\t | Stake \t | Not-staked \t | Rewards \t | Total \t | Total USD\n"
	addressProcessed = {}
	# logger.info("preparing header for rewards")
	# logger.info(rewards)
	for reward in rewards:
		address = reward["address"]
		# logger.info(address)
		if address not in addressProcessed:
			# logger.info("processing header for the address")
			addressProcessed[address] = True
			header += getAddressHeader(conn, coin, reward["address"])
			# logger.info(header)
	header += "\n"

	# logger.info("end of processing")
	# conn.close()
	return header + message


def getTotalOne(conn, rewards):
	totalOne = 0
	processedAddresses = []
	for reward in rewards:
		address = reward["address"]
		if address not in processedAddresses:
			processedAddresses.append(address)
			addDetails = getAddressDetails(conn, address)
			totalOne += int(addDetails["totalStake"])
			totalOne += int(getRealBalance(addDetails))
			totalOne += int(addDetails["totalRewards"])

	return totalOne


def getAddressHeader(conn, coin, address):
	addDetails = getAddressDetails(conn, address)

	ranking = ""
	if addDetails["ranking"]:
		ranking = addDetails["ranking"]
	# logger.info(addDetails)
	header = str(ranking) + "\t | "
	header += getAddressLink(address) + "\t | "
	header += str(int(addDetails["totalStake"])) + "\t | "
	header += str(int(getRealBalance(addDetails))) + "\t | "
	header += str(int(addDetails["totalRewards"])) + "\t | "
	header += "<b>" + str(int(addDetails["totalBalance"])) + "</b>\t | "
	totalUSD = int(float(addDetails["totalBalance"]) * coin["usdPrice"])
	header += "<b>$" + str(totalUSD) + "</b>\n"

	return header


def getRealBalance(addDetails):
	balance = addDetails["addressBalance"]
	# total = addDetails["addressBalance"]
	# reward = addDetails["totalRewards"]
	# stake = addDetails["totalStake"]
	# balance = total - stake

	# logger.info("address: {}; balance: {}".format(addDetails, balance))

	if balance < 0:
		return 0

	return balance


def getRewardsMessage(coin, rewards, totalOne):
	# logger.info(coin)
	# logger.info(rewards)

	# totalOne = 0
	totalUsdValue = 0

	footer = ""
	message = ""
	if len(rewards) > 1:
		message = "Val\t\t | Address\t\t | Stake \t | Reward | Total USD\n"
		for reward in rewards:
			message += getRewardsDetails(coin, reward, True)
			# totalOne += reward["stake"] + reward["reward"]

		# totalUsdValue = round(totalOne * coin["usdPrice"])
	elif len(rewards) > 0:
		reward = rewards[0]
		message = "Val\t\t | Stake \t | Reward | Total USD\n"

		message += getRewardsDetails(coin, reward, False)
		footer += "Address Details: " + getAddressLink(reward["address"]) + "\n"
		totalOne = reward["stake"] + reward["reward"]
		# totalUsdValue = round(totalOne * coin["usdPrice"])

	header = "Delegation & Rewards details:\n"
	totalUsdValue = round(totalOne * coin["usdPrice"])
	totals = "Total One: <b>" + str(int(totalOne)) + "</b> | Total USD Value: <b>$"
	totals += str(round(totalUsdValue,0)) + "</b>\n"

	message += "\nONE Price in USD: <a href='https://data.messari.io/api/v1/assets/harmony/metrics'>" + str(coin["usdPrice"]) + "</a>\n"
	return header + message + footer, totals


def getRewardsDetails(coin, reward, showAddress):
	message = ""

	name = reward["name"]
	if reward["name"] is not None and len(reward["name"]) > 11:
		name = reward["name"][:11]

	total = reward["stake"] + reward["reward"]
	# usdPrice = coin["usdPrice"]
	totalUSD = round(total * coin["usdPrice"])
	# totalUsdValue += totalUSD
	# totalOne += total

	message += getValLink(name, reward["hPoolId"]) + "\t | "
	if showAddress:
		message += getAddressLink(reward["address"]) + "\t | "
	message += str(int(reward["stake"])) + "\t | "
	message += "<b>" + str(reward["reward"]) + "</b>\t | "
	message += "$" + str(totalUSD) + "\n"

	return message


def searchByAddressSql(addressInput):
	addressList = addressInput.split(",")
	# logger.info("addresses are")
	# logger.info(addressList)

	sql = " select p.hPoolId, name, website, d.address, p.totalStaked, "
	sql += " stake, reward, p.avgEri from " + tables.hpooldel + " d "
	sql += " inner join " + tables.hpool + " p on p.hPoolId=d.hPoolId "

	addresses = ""
	for a in addressList:
		if addresses != "":
			addresses += ","
		addresses += "'" + a + "'"
	sql += " where d.address in ( " + addresses + ") "
	sql += " and (d.stake > 0.0001 or d.reward > 0.001) "
	sql += " order by stake desc"

	# logger.info("search by address sql is: " + sql)
	return sql


def getAddressLink(address):
	if address is None or len(address) < 10:
		return ""

	shortAddress = address[0:5] + " .. " + address[-5:]
	return "<a href='https://explorer.harmony.one/#/address/" + address + "'>" + shortAddress + "</a>"


def getAddressDetails(conn, address):
	sql = " select ranking, address, round(totalStake,0)  as totalStake, "
	sql += " round(addressBalance,0) as addressBalance, "
	sql += " round(totalRewards,2) as totalRewards, "
	sql += " round(totalBalance,0) as totalBalance, alias "
	sql += " from " + tables.haddress
	sql += " where address = %s "

	# logger.info(sql)

	return dbUtil.getSingleRecordNoJsonWithConn(sql, conn, address)

