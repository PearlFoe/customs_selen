from app import logger, config
from app.scrapper import Scrapper

import subprocess
import time
import json
import os


@logger.catch
def main():
	global scrapper
	scrapper = Scrapper()
	scrapper.run()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		scrapper.close_driver()