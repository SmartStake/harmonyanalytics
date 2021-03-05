import logging

import requests

import rds_config
import tgConstants
import notificationUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def pushNotifications(notifications):
	logger.info("pushNotifications: notifications:")
	logger.info(notifications)
	# notificationsByType = tgNotificationUtils.organizeNotByTypeAndChat(notifications, "eventId")
	notificationsByType = notificationUtils.organizeNotByTypeAndChat(notifications, "groupingCriteria")
	# logger.info("notificationsByType:")
	# logger.info(notificationsByType)

	for notificationType in notificationsByType.keys():
		notificationDetails = notificationsByType[notificationType]
		# logger.info("sending notificationType: {} and notificationDetails: {}".format(
		# 	notificationType, notificationDetails))
		pushNotification(notificationDetails)


def pushNotification(notificationDetails):
	message = None
	chatId = None
	for notification in notificationDetails:
		if not message:
			message = notification["header"] + "\n"
			if "subtitle" in notification:
				message += "\n" + notification["subtitle"] + "\n"
			chatId = notification["chatId"]
		elif len(message) > tgConstants.MAX_LENGTH_PER_RESPONSE:
			message += "___\n"
			postTgNotMessage(chatId, message)
			message = notification["header"] + "\n"
			if "subtitle" in notification:
				message += "\n" + notification["subtitle"] + "\n"

		message += "\n" + notification["summary"]

	message += "___\n"
	postTgNotMessage(chatId, message)


def postTgNotMessage(chatId, message):
	logger.info("sending message: {} to chatId: {}".format(chatId, message))
	respData = {"text": message.encode("utf8"), "chat_id": str(chatId)}
	url = rds_config.TG_BASE_URL + "/sendMessage?parse_mode=html&disable_web_page_preview=true"

	logger.info("just before sending message")
	resp = requests.post(url, respData)
	logger.info("resp: {}".format(resp))
	logger.info("after sending message")
