from concurrent.futures import ThreadPoolExecutor

from app import logger, config, accounts
from app.scrapper import Scrapper

import concurrent.futures.thread

class Runner(object):
	"""docstring for Runner"""
	def __init__(self, orders=None):
		self.orders = orders
		self.threads_quantity = config['THREADS_QUANTITY']
		self.scrapper = None
		self.executor = None
		self.scrapper = None
		self.executor = ThreadPoolExecutor(max_workers=self.threads_quantity, thread_name_prefix='Tread')
		self.scrapper = [] if self.threads_quantity > 1 else None

	def run_scrapper(self, order):
		scr = Scrapper(order=order)
		self.scrapper.append(scr)
		scr.run()

	def start(self):
		if len(self.orders) < config['THREADS_QUANTITY']:
	 		config['THREADS_QUANTITY'] = len(self.orders)

		if self.threads_quantity > 1:
			futures = []
			for order in self.orders:
				futures.append(self.executor.submit(self.run_scrapper, order))
			'''
			for i in futures:
				i.result()
			'''
		else:
			futures = []
			for order in self.orders:
				self.scrapper = Scrapper(order=order)
				futures.append(self.executor.submit(self.scrapper.run))

	def stop(self):
		if self.threads_quantity > 1:
			self.executor.shutdown(wait=False)
			self.executor._threads.clear()
			concurrent.futures.thread._threads_queues.clear()
			for scr in self.scrapper:
				scr.close_driver()
		else:
			self.scrapper.close_driver()