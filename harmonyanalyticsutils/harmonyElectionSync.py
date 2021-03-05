import datetime
import sys
import time

from requests import Session

import commonUtils
import constants
import logUtil

if len(sys.argv) < 3:
	raise Exception("correct syntax is: python harmonyNotificationSync dev/prod logsPath")

today = datetime.date.today()

logger = logUtil.l()

def syncElections():
	reqDetails = {"type": "electionSync"}
	# logger.info(reqDetails)

	commonUtils.postReq(constants.electionSyncUrl, reqDetails)

startTime = int(time.time())
logger.info("starting notification sync")
syncElections()
logger.info("time taken: {} seconds".format((int(time.time()) - startTime)))
