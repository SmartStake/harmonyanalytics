import datetime
import logging
import sys

today = datetime.date.today()
# print("Today's date:", today)

logs_folder = sys.argv[2]

logger = logging.getLogger('harmony')
logger.setLevel(logging.DEBUG)
# logging.DEBUG
fh = logging.FileHandler(logs_folder + '/harmony-' + str(today) + '.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

def l():
    return logger

