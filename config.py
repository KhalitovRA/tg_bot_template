import os
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = int(os.getenv("ADMINS"))  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста
# host = os.getenv('PGHOST')
host = 'localhost'
PG_USER = os.getenv('PG_USER')
PG_PASS = os.getenv('PG_PASS')
lp_token = os.getenv('LIQPAY_TOKEN')


I18N_DOMAIN = 'testbot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'
