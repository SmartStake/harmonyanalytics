import logging

import harmonyBlsKeys
import securityUtils
import utilities

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
	conn, app, error = securityUtils.performSecurityCheckAndGetDetails(event)
	if error:
		return error

	logger.info("in temp")
	harmonyBlsKeys.processKeyNodeVersionAlert(conn, app)
	logger.info("after processing node version alert")

	conn.close()
	return utilities.getSuccessResponse()
