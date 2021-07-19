import telegram

from app import logger, config

import threading

lock = threading.RLock()

class TelegramNotifier(object):
	"""
	docstring for TelegramNotifier

	bot url: t.me/border_notifier_bot
	"""
	def __init__(self):
		self.bot = telegram.Bot(token=config['TELEGRAM_BOT_TOKEN'])
		self.user_to_mail = config['TELEGRAM_USER_TO_NOTIFY']

	def send_message(self, message):
		lock.acquire()
		try:
			self.bot.send_message(self.user_to_mail, message)
		except Exception:
			logger.warning('An error occured trying to send telegram error notification.')
		else:
			logger.info('User was notified in telegram.')
		finally:
			lock.release()
