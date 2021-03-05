import datetime
import sys
import time

from requests import Session

import commonUtils
import constants
import logUtil

if len(sys.argv) < 3:
	raise Exception("correct syntax is: python3 harmonyTemp dev/prod logsPath")

today = datetime.date.today()

logger = logUtil.l()

def syncNotifications():
	reqDetails = {"type": "temp"}
	# logger.info(reqDetails)

	commonUtils.postReq(constants.tempUrl, reqDetails)

startTime = int(time.time())
logger.info("starting notification sync")
syncNotifications()
logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
