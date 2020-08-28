import base64
import binascii
import datetime
import decimal
import json
from binascii import unhexlify
from json import encoder
from dateutil import parser
from requests import Session

import constants
import logUtil

logger = logUtil.l()

encoder.FLOAT_REPR = lambda o: format(o, '.2f')

def divideByTenPower18(value):
	return divideByTenPower(value, 18)


def divideByTenPower(value, power):
	if value is None:
		return value

	return float(value) / (10 ** power)


def getHarmonyCoins(value):
	return divideByTenPower(value, 18)


def getMapFromList(data, keyAttribute):
	mapObj = {}

	for item in data:
		keyValue = item[keyAttribute]
		mapObj[keyValue] = item

	return mapObj


def getMapFromList2Keys(data, keyAttribute1, keyAttribute2):
	mapObj = {}

	for item in data:
		keyValue = item[keyAttribute1] + "-" + item[keyAttribute2]
		mapObj[keyValue] = item

	return mapObj


def postUpdate(type, reqData):
	return postReq(constants.updateUrl + "&type=" + type, reqData)


def postReq(url, reqData):
	# logger.info(reqData)
	data = {"data": reqData}
	data_json = jsondumps(data)
	logger.info("after json dump")

	session = Session()
	logger.info("calling update API:")

	logger.info("calling url: " + url)
	response = session.post(url, data=data_json, allow_redirects=False)
	logger.info("update data response is:")
	logger.info(response)


def getResultFromPost(session, method, params=[]):
	data = getDataFromPost(session, method, params)
	# logger.info(data)

	if data and "result" in data:
		return data["result"]

	return None


def getResultFromGet(session, url):
	# logger.info("calling getResultFromGet for url: {}".format(url))
	data = getDataFromGet(session, url)
	# logger.info(data)

	if data and "result" in data:
		return data["result"]

	return None


def getDataFromGet(session, url):
	# logger.debug("calling url: " + url)
	headers = {'accept': 'application/object'}
	response = session.get(url, headers=headers)

	# logger.info(response)
	if response.status_code == 200:
		data = json.loads(response.content.decode('utf-8'))
		# logger.info(data)
		return data

	logger.debug(response)
	logger.debug("unexpected response")
	return None


def getDataFromPost(session, url, method, params=[]):
	headers = {'accept': 'application/object', 'Content-Type': 'application/json'}
	inputs = {'method': method, 'params': params, 'jsonrpc': '2.0', 'id': 1}

	response = session.post(url, data=json.dumps(inputs), headers=headers, allow_redirects=False)

	# logger.info(response)
	# logger.info(response.status_code)

	data = None
	if response.status_code == 200:
		data = json.loads(response.content.decode('utf-8'))
		# data = json.loads(response.text)

	# logger.info("data is:")
	# logger.info(data)
	return data


def listData(session, url):
	logger.info("getting all addresses from db")

	logger.info("calling url: " + url)
	headers = {'accept': 'application/object'}
	response = session.get(url, headers=headers)

	# logger.info(response)
	if response.status_code == 200:
		data = json.loads(response.content.decode('utf-8'))
		# logger.info(data)
		return data

	logger.info(response)


def roundCompDiff(obj1, obj2, name):
	val1 = obj1[name]
	val2 = obj2[name]

	return roundCompDiffVale(val1, val2)


def roundCompDiffVale(val1, val2):
	if val1 is None and val2 is None:
		return False
	elif val1 is None:
		return True
	elif val2 is None:
		return True
	elif val1 == 0 and val2 == 0:
		return False

	result = round(val1) != round(val2)
	logger.info("result of comparing {} with {} is {}".format(val1, val2, result))

	return result


def hexFromBase64(base64_id):
	# """base64_id can be found in entity.json in the `id` field"""
	return binascii.hexlify(base64.b64decode(base64_id)).decode("utf-8")


def base64FromHex(hexInput):
	# """base64_id can be found in entity.json in the `id` field"""
	# return b2a_base64(unhexlify(hexInput)).decode("utf-8")
	return base64.b64encode(unhexlify(hexInput)).decode("utf-8")


def jsondumps(o):
	return json.dumps(o, default=default)


def default(o):
	if type(o) is datetime.date or type(o) is datetime.datetime:
		return o.isoformat()
	if isinstance(o, float):
		return round(o, 8)
	if type(o) is decimal.Decimal:
		return str(o)


def toEpochTime(val):
	return parser.parse(val).strftime('%s')


def postReqAsIs(url, reqData):
	# logger.info(reqData)
	data_json = jsondumps(reqData)
	logger.info("after json dump")

	session = Session()
	logger.info("calling update cs node balance:")

	logger.info("calling url: " + url)
	response = session.post(url, data=data_json, allow_redirects=False)
	logger.info("update data response is:")
	logger.info(response)


def getLatestBlockDetails(session):
	data = getHarmonyDataFromPost(session, constants.LATEST_BLOCK_URL, [])

	# latestBlock = getResultFromPost(session, constants.LATEST_BLOCK_URL, [])
	return data["result"]


def getBlockHeightRange(eventNameUrl, maxBlocks):
	session = Session()
	startBlock = getStartBlockHeight(session, eventNameUrl)
	latestBlockHeight = getLatestBlockDetails(session)
	actualLatestBlock = latestBlockHeight

	more = False
	if latestBlockHeight - startBlock > maxBlocks:
		latestBlockHeight = startBlock + maxBlocks
		more = True

	logger.info("startBlock: {}, actualLatestBlock: {}, latestBlockHeight: {}, more: {}".format(
		startBlock, actualLatestBlock, latestBlockHeight, more))
	return startBlock, latestBlockHeight, more


def getStartBlockHeight(session, eventNameUrl):
	logger.debug("getting last block height")

	logger.debug("calling url: " + eventNameUrl)
	headers = {'accept': 'application/object'}
	response = session.get(eventNameUrl, headers=headers)

	logger.info(response)
	if response.status_code == 200:
		data = json.loads(response.content.decode('utf-8'))
		logger.info(data)
		blockHeight = data["description"]
		logger.info("last synced block height: " + blockHeight)
		return int(blockHeight) + 1

	logger.debug(response)
	return None


def getHarmonyResultDataFromPost(session, method, params=[]):
	data = getHarmonyDataFromPost(session, method, params)
	if data and "result" in data:
		return data["result"]

	return None


def getHarmonyDataFromPost(session, method, params=[]):
	headers = {'accept': 'application/object',
		'Content-Type': 'application/json'}

	inputs = {'method': method,
		'params':params,
		'jsonrpc':'2.0', 'id': 1}

	url = constants.HARMONY_BASE_URL
	# logger.info(url)

	response = session.post(url,
		data=json.dumps(inputs), headers=headers, allow_redirects=False)

	# logger.info(response)
	# logger.info(response.status_code)

	data = None
	if response.status_code == 200:
		data = json.loads(response.content.decode('utf-8'))
		# data = json.loads(response.text)

	# logger.info("data is:")
	# logger.info(data)
	return data


def getAmount(inputVal):
	return divideByTenPower18(inputVal)

