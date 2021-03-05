import os

#prod
db_endpoint = os.environ['DB_ENDPOINT']
db_username = os.environ['DB_USERNAME']
db_name = os.environ['DB_SCHEMA_NAME']
db_port = os.environ['DB_PORT']
db_password = os.environ['DB_PASSWORD']
db_schema = os.environ['DB_SCHEMA_NAME']

env = os.environ['ENV']

pool_max_days = 10

TELEGRAM_TOKEN = os.environ['H_TELEGRAM_TOKEN']
TG_BASE_URL = "https://api.telegram.org/bot{}".format(TELEGRAM_TOKEN)

SECURITY_KEY_1 = os.environ['SECURITY_KEY_1']
SECURITY_KEY_2 = os.environ['SECURITY_KEY_2']

DEFAULT_POOL_ID = os.environ['DEFAULT_POOL_ID']

