from concurrent.futures import ThreadPoolExecutor
import concurrent.futures.thread

from app import logger, config
from app.runner import Runner

import subprocess
import time
import json
import os

@logger.catch
def main():
	global runner
	runner = Runner()
	runner.start()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		runner.stop()