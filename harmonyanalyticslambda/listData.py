import datetime
import logging

import constants
import harmonyData
import securityUtils

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
	startTime = datetime.datetime.now()
	# logger.info("in list data")
	conn, app, error = securityUtils.performSecurityCheckAndGetDetails(event)
	# logger.info(app)
	if error: 
		# logger.info(error)
		return error

	dataType = event["queryStringParameters"]["type"]

	data = None
	if app == constants.HARMONY:
		data = harmonyData.listHData(conn, app, event, context, startTime, dataType)


	conn.close()
	return data


