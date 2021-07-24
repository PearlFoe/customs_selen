import telegram

from app import logger, config

import threading

lock = threading.RLock()

class TelegramNotifier(object):
	"""
	docstring for TelegramNotifier

	bot url: t.me/border_notifier_bot
	"""
	def __init__(self, login):
		self.login = login
		self.bot = telegram.Bot(token=config['TELEGRAM_BOT_TOKEN'])
		self.user_to_mail = config['TELEGRAM_USER_TO_NOTIFY']
		self.notify = config['NOTIFY']

	def send_message(self, message):
		if self.notify:
			lock.acquire()
			try:
				dt = datetime.datetime.now()
				self.bot.send_message(self.user_to_mail, f'{str(dt)} | {self.login} | {message}')
			except Exception:
				logger.warning('An error occured trying to send telegram error notification.')
			else:
				logger.info('User was notified in telegram.')
			finally:
				lock.release()
