from app import logger, config
from app.runner import Runner
from app.UI import Vier

import os
import sys
import datetime

@logger.catch
def main():
	global runner
	global vier

	os.environ['WDM_LOG_LEVEL'] = '0'
	os.environ['WDM_PRINT_FIRST_LINE'] = 'False'
	sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

	runner = Runner()
	vier = Vier(runner=runner)
	vier.run()

if __name__ == '__main__':
	current_datetime = datetime.datetime.now()
	finish_datetime = datetime.datetime.strptime('2021-8-14 00:00', '%Y-%m-%d %H:%M')

	if current_datetime < finish_datetime:
		main()
	else:
		print('Срок пробного периода истек.')
		_ = input()

