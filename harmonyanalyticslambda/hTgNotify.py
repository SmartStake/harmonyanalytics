import logging

import requests
import json

import constants
import hConstants
import hTgBot
import harmonyData
import rds_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sent = 0
ARROW_UP = u'\U00002B06'
ARROW_DOWN = u'\U00002B07'
TOOLS = u'\U0001F6E0'

def isSpecialVal(poolMap, event):
	poolId = poolMap[event["validatorAddress"]]["hPoolId"]

	if poolId == constants.H_POOL_ID_SS or poolId == constants.H_POOL_ID_OTHER:
		return True

	return False

def handleEvent(conn, event, poolMap):
	eventType = event["type"]
	message = None

	if eventType == hConstants.H_EVENT_DELEGATE:
		# logger.info("delegate: {} for pool: {}".format(
		# 	poolMap[event["validatorAddress"]], poolMap[event["validatorAddress"]]["hPoolId"]))
		if isSpecialVal(poolMap, event):
			message = {"header": "Delegation Alert", "block": event["blockNumber"],
					   "subtitleName": "Validator", "eventType": eventType,
					   "subtitleValue": poolMap[event["validatorAddress"]]["name"],
					   "body": "<a href='https://harmony.smartstake.io/address/" + event["address"]
						+ "'>" + event["address"] + "</a> has delegated <b>"
						+ str(round(event["amount"], 0)) + "</b>.",
					   "address": event["address"]}
	elif eventType == hConstants.H_EVENT_UNDELEGATE:
		# logger.info("undelegate: {} for pool: {}".format(
		# 	poolMap[event["validatorAddress"]], poolMap[event["validatorAddress"]]["hPoolId"]))
		if isSpecialVal(poolMap, event):
			message = {"header": "Undelegation Alert", "block": event["blockNumber"],
					   "subtitleName": "Validator", "eventType": eventType,
					   "subtitleValue": poolMap[event["validatorAddress"]]["name"],
					   "body": "<a href='https://harmony.smartstake.io/address/" + event["address"]
						+ "'>" + event["address"] + "</a> has undelegated <b>"
						+ str(round(event["amount"], 0)) + "</b>.",
					   "address": event["address"]}
	elif eventType == hConstants.H_EVENT_EDIT_VALIDATOR:
		# logger.info("edit validator: {} for pool: {}".format(
		# 	poolMap[event["validatorAddress"]], poolMap[event["validatorAddress"]]["hPoolId"]))
		if isSpecialVal(poolMap, event):
			message = {"header": "Edit Validator", "block": event["blockNumber"],
					   "subtitleName": "Validator", "address": event["validatorAddress"],
					   "subtitleValue": poolMap[event["validatorAddress"]]["name"],
					   "body": "Some changes were made in the validator.",
					   "eventType": eventType, "eventDetails": event["msg"]}

	if message:
		# logger.info(message)
		# logger.info("processing smart stake events")
		try:
			notify(conn, message)
		except BaseException as e:
			logger.info(message)
			logger.info(e)
			logger.error("error occurred in handling message", exc_info=True)


def notify(conn, message):
	# global sent

	# if sent > 3:
	# 	return

	if message["eventType"] == hConstants.H_EVENT_DELEGATE:
		# imageSrc = "https://harmony.smartstake.io/images/green-16.png"
		# <span class='emoji  emoji-spritesheet-4' title='green_circle'>:green_circle:</span>
		text = "<b>" + ARROW_UP + " " + message["header"] + "</b>\n\n"
	elif message["eventType"] == hConstants.H_EVENT_UNDELEGATE:
		# imageSrc = "https://harmony.smartstake.io/images/red-16.png"
		text = "<b>" + ARROW_DOWN + " " + message["header"] + "</b>\n\n"
		# text = "<b><a href='" + imageSrc + "'>&#8205;</a> " + message["header"] + "</b>\n\n"
	else:
		text = "<b>" + TOOLS + " " + message["header"] + "</b>\n\n"

	text += message["subtitleName"] + ": <b>" + message["subtitleValue"] + "</b>\n\n"
	text += message["body"] + "\n"
	text += "\n"

	if message["eventType"] == hConstants.H_EVENT_EDIT_VALIDATOR:
		val = harmonyData.getHarmonyPool(conn, message["address"])
		text += "Total Stake: " + str(int(val["totalStaked"])) + ". "
		text += "Fee: " + str(round(val["fee"], 2)) + ". "
		text += "BLS Key Count: " + str(int(val["blsKeyCount"])) + ". "
		text += "Transaction details: " + json.dumps(message["eventDetails"])
	else:
		addressDetails = hTgBot.getAddressDetails(conn, message["address"])
		text += "Total Stake: " + str(int(addressDetails["totalStake"])) + ". "
		text += "Non-staked Balance: " + str(round(addressDetails["addressBalance"], 2)) + ". "
	text += "Block number: " + str(message["block"]) + ". "
	text += "\n___\n"
	# logger.info(text)
	respData = {"text": text.encode("utf8"), "chat_id": "495381506"}
	url = rds_config.TG_BASE_URL + "/sendMessage?parse_mode=html&disable_web_page_preview=true"
	# url = rds_config.TG_BASE_URL + "/sendMessage?parse_mode=html&disable_web_page_preview=false"
	# logger.info(url)
	# logger.info(respData)
	requests.post(url, respData)

	# sent += 1
