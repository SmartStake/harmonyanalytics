import json
import logging

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def callRestJson(url):
    session = Session()
    headers = {'accept': 'application/object'}

    try:
        response = session.get(url, headers=headers)

        if response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            return data
        else:
            return None
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        logger.info("error occurred")
        logger.info(e)
        return None

