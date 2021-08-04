from loguru import logger

from app.utils import get_config, get_accounts, get_proxy, get_auto_numbers

import sys

logger.remove()
logger.add(sys.stderr, format="<green>{time.hour}:{time.minute}:{time.second}:{time.microsecond}, {time.year}-{time.month}-{time.day}</green> - <lvl>{level}</lvl> - <c>{thread.name}</c> - <lvl>{message}</lvl>", level="INFO")
logger.add('main_log_file.log', format="<green>{time.hour}:{time.minute}:{time.second}:{time.microsecond}, {time.year}-{time.month}-{time.day}</green> - <lvl>{level}</lvl> - <c>{thread.name}</c> - <lvl>{message}</lvl>", level="DEBUG")

logger = logger

config = get_config('config.json')
accounts = get_accounts('accounts.txt')
proxies = get_proxy('proxy.txt')
auto_numbers = get_auto_numbers('reg_auto_numbers.txt')