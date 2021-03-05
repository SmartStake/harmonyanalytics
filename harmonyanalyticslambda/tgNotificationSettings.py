import logging

import constants
import hTgBot
import tgBotUtils
import tgConstants

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Notifications for validator events – bls key changes, fee changes, delegations, un-delegations, large events


def handleNotificationCommands(conn, chatId, userId, textCmd):
	handled, response, keyboard = False, None, None
	if isCmd(textCmd, tgConstants.rootNotifications["root"]):
		response, keyboard = getRootNotSettings(conn, chatId, userId)
		handled = True
	elif isCmd(textCmd, tgConstants.rootNotifications["delegate"]):
		response, keyboard = getDelegateNotSettings(conn, chatId, userId)
		handled = True
	elif isCmd(textCmd, tgConstants.rootNotifications["validator"]):
		response, keyboard = getValidatorNotSettings(conn, chatId, userId)
		handled = True

	logger.info(handled)
	logger.info(response)
	logger.info(keyboard)
	return handled, response, keyboard


def isCmd(textCmd, key):
	if textCmd.startswith(key):
		return True
	elif textCmd.startswith("/" + key):
		return True

	return False


def getRootNotSettings(conn, chatId, userId):
	keyboard = getNotificationRootKeyboard(conn, chatId, userId)
	response = "Please use message keyboard buttons for updating notification settings. \n\n"
	response += getCurrentNotificationSettings(conn, chatId)

	logger.info("response : {}, inline_keyboard: {}".format(response, keyboard))
	return response, keyboard


def getValidatorNotSettings(conn, chatId, userId):
	keyboard = getValidatorNotificationsKeyboard(conn, chatId, userId)
	response = "Please use message keyboard buttons for updating notification settings. \n\n"
	response += getCurrentNotificationSettings(conn, chatId)

	logger.info("response : {}, inline_keyboard: {}".format(response, keyboard))
	return response, keyboard


def getValidatorNotificationsKeyboard(conn, chatId, userId):
	setting = tgBotUtils.prepUserSettings(conn, chatId, userId, constants.APP)
	# Notifications for validator events – bls key changes, fee changes, delegations, un-delegations, large events
	# `notifyDel` , `notifyUndel`, `notifyFee`, `notifyKeyChanges`, `notifyLarge`
	status = []
	status.append(getObject(setting, tgConstants.NOTIFY_DEL))
	status.append(getObject(setting, tgConstants.NOTIFY_UNDEL))
	status.append(getObject(setting, tgConstants.NOTIFY_KEY_CHANGES))
	status.append(getObject(setting, tgConstants.NOTIFY_KEY_PERF))
	status.append(getObject(setting, tgConstants.NOTIFY_LARGE))
	status.append(getObject(setting, tgConstants.NOTIFY_ELECTION))
	status.append(getObject(setting, tgConstants.NOTIFY_EPOCH))
	status.append(getObject(setting, tgConstants.NOTIFY_VALIDATOR_PERF))

	return getKeyboard(status)


def getKeyboard(commands):
	keyboard = []

	row = []
	for status in commands:
		if len(row) == 2:
			keyboard.append(row)
			row = []
			# "/" +
		row.append(status["next"] + " " + status["label"])

	if len(row) == 2:
		keyboard.append(row)
		row = [tgConstants.MAIN_MENU]
	else:
		row.append(tgConstants.MAIN_MENU)
	keyboard.append(row)

	# [	['/enable Delegation Notification', '/enable Undelegation Notification'],
	# 	['/enable Key Change Notification', '/enable Fee Change Notification']
	# ]
	return keyboard



def getNotificationRootKeyboard(conn, chatId, userId):
	status = []
	status.append({"next": "Delegate", "label": "Notifications"})
	status.append({"next": "Validator", "label": "Notifications"})

	return getKeyboard(status)


def getObject(setting, key):
	if setting[key] == "True":
		return {"next": tgConstants.DISABLE_KEY, "label": tgConstants.allNotificationsKeys[key]}

	return {"next": tgConstants.ENABLE_KEY, "label": tgConstants.allNotificationsKeys[key]}



#TODO prepare text based on db settings
# keyboard = '{"inline_keyboard": ['
# inline_keyboard = '['
# # inline_keyboard += '[{"text":"Notify delegation", "callback_data":"notify_switch_delegation"}],'
# # inline_keyboard += '[{"text":"Notify undelegation", "callback_data":"notify_switch_undelegation"}],'
# # inline_keyboard += '[{"text":"Notify edit validator", "callback_data":"notify_switch_edit"}],'
# inline_keyboard += '[{"text":"Notify fee change", "callback_data":"notify_switch_fee"}]'
# inline_keyboard += ']'

# inline_keyboard += '[{"text":"Notify delegation", "callback_data":"notify_switch_delegation"}],'
# inline_keyboard += '[{"text":"Notify undelegation", "callback_data":"notify_switch_undelegation"}],'
# inline_keyboard += '[{"text":"Notify edit validator", "callback_data":"notify_switch_edit"}],'
# inline_keyboard = [
# 	[{"text":"Notify fee change"}]
# ]

def updateSetting(conn, chatId, userId, textCmd, prefix):
	key = tgBotUtils.getParam(textCmd, prefix, "An unexpected error occurred. The command has invalid syntax. Please try again or contact the bot operator.")
	settingName = None
	delegate = False
	for setting in tgConstants.allNotificationsKeys.keys():
		value = tgConstants.allNotificationsKeys[setting]
		logger.info("comparing input key: {}, with notification: {}".format(key, value))
		if value == key:
			settingName = setting
			break

	for setting in tgConstants.delegateNotifications.keys():
		value = tgConstants.delegateNotifications[setting]
		logger.info("comparing input key: {}, with notification: {}".format(key, value))
		if value == key:
			delegate = True
			break

	if settingName:
		if prefix == tgConstants.ENABLE_CMD_KEY:
			newValue = "True"
		else:
			newValue = "False"

		logger.info("updating setting: {} to {}".format(settingName, newValue))
		tgBotUtils.updateSetting(conn, chatId, settingName, newValue, constants.APP)

		response = "Setting updated.\n"
		response += getCurrentNotificationSettings(conn, chatId)

		if delegate:
			keyboard = getDelegationNotificationsKeyboard(conn, chatId, userId)
		else:
			keyboard = getValidatorNotificationsKeyboard(conn, chatId, userId)

		return response, keyboard

	logger.info("setting not found")
	response = "Unexpected error occurred. Setting not found. Please try again or contact the bot operator."
	return response, getNotificationRootKeyboard(conn, chatId, userId)



def getNotificationMessage(setting, notifications, title):
	delMessage = title + ": \n"
	found = False
	for key in notifications.keys():
		message, isPresent = getSettingDesc(setting, key)
		delMessage += message + "\n"
		if isPresent:
			found = True

	return delMessage, found


def getCurrentNotificationSettings(conn, chatId):
	setting = tgBotUtils.getUserSettings(conn, chatId, constants.APP)

	message = "Current notification settings are : \n\n"

	delegateMsg, dFound = getNotificationMessage(setting, tgConstants.delegateNotifications, "<b>As delegate</b>")
	if dFound:
		message += delegateMsg
		message += "\n"

	validatorMsg, vFound = getNotificationMessage(setting, tgConstants.validatorNotifications, "<b>As validator</b>")
	if vFound:
		message += validatorMsg

	if not dFound and not vFound:
		message += delegateMsg
		message += "\n"
		message += validatorMsg

	poolsMsg = hTgBot.getConfiguredPools(conn, setting)

	if poolsMsg == "":
		poolsMsg = "\nFavorite validators are not setup yet. Please configure them to receive notifications.\n"
		poolsMsg += hTgBot.SET_FAV_VALIDATORS.format("/setfav or /addfav")
	else:
		poolsMsg = "\nFavorite validators that will be used for notifications are: \n" + poolsMsg

	return message + poolsMsg


def getSettingDesc(settings, key):
	# logger.info("settings are: {}, key is: {}".format(settings, key))
	message = tgConstants.allNotificationsKeys[key] + " : "
	logger.info("message: " + message)

	isPresent = False
	if settings[key] == "True":
		message += tgConstants.CHECK_MARK
		isPresent = True
	else:
		message += tgConstants.CROSS_MARK
	logger.info("message: " + message)

	return message, isPresent


def getDelegateNotSettings(conn, chatId, userId):
	keyboard = getDelegationNotificationsKeyboard(conn, chatId, userId)
	response = "Please use message keyboard buttons for updating notification settings. \n\n"
	response += getCurrentNotificationSettings(conn, chatId)

	logger.info("response : {}, inline_keyboard: {}".format(response, keyboard))
	return response, keyboard


def getDelegationNotificationsKeyboard(conn, chatId, userId):
	setting = tgBotUtils.prepUserSettings(conn, chatId, userId, constants.APP)
	# Notifications for validator events – bls key changes, fee changes, delegations, un-delegations, large events
	# `notifyDel` , `notifyUndel`, `notifyFee`, `notifyKeyChanges`, `notifyLarge`
	status = []
	status.append(getObject(setting, tgConstants.NOTIFY_ADDRESS))
	status.append(getObject(setting, tgConstants.NOTIFY_FEE))
	status.append(getObject(setting, tgConstants.NOTIFY_DEL_PERFORMANCE))

	return getKeyboard(status)
