from concurrent.futures import ThreadPoolExecutor

from app import logger, config, accounts
from app.scrapper import Scrapper

import concurrent.futures.thread

class Runner(object):
	"""docstring for Runner"""
	def __init__(self):
		self.threads_quantity = config['THREADS_QUANTITY']
		self.scrapper = None
		self.executor = None

		if self.threads_quantity > 1:
			self.executor = ThreadPoolExecutor(max_workers=self.threads_quantity, thread_name_prefix='Tread')
			self.scrapper = []
		else:
			self.scrapper = Scrapper()

	def run_scrapper(self):
		scr = Scrapper()
		self.scrapper.append(scr)
		scr.run()

	def start(self):
		if self.threads_quantity > 1:
			futures = []
			for _ in range(self.threads_quantity):
				futures.append(self.executor.submit(self.run_scrapper))
			
			for i in futures:
				i.result()
		else:
			self.scrapper.run()

	def stop(self):
		if self.threads_quantity > 1:
			self.executor.shutdown(wait=False)
			self.executor._threads.clear()
			concurrent.futures.thread._threads_queues.clear()
			for scr in self.scrapper:
				scr.close_driver()
		else:
			self.scrapper.close_driver()