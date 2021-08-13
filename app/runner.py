from concurrent.futures import ThreadPoolExecutor

from app import logger, config, accounts
from app.scrapper import Scrapper

import concurrent.futures.thread

class Runner(object):
	"""docstring for Runner"""
	def __init__(self, orders=None):
		self.orders = orders
		self.threads_quantity = config['THREADS_QUANTITY'] if not config['MODE'] else 1
		self.executor = ThreadPoolExecutor(max_workers=self.threads_quantity, thread_name_prefix='Tread')
		self.scrapper = []

	def run_scrapper(self, order):
		scr = Scrapper(order=order)
		self.scrapper.append(scr)
		scr.run()

	def start(self):
		if len(self.orders) < self.threads_quantity:
	 		self.threads_quantity = len(self.orders)

		futures = []
		for order in self.orders:
			futures.append(self.executor.submit(self.run_scrapper, order))

	def stop(self):
		self.executor.shutdown(wait=False)
		self.executor._threads.clear()
		concurrent.futures.thread._threads_queues.clear()

		for scr in self.scrapper:
			scr.close_driver()
