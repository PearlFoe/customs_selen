from app import logger, config
from app.runner import Runner
from app.UI import Vier

import os
import datetime

@logger.catch
def main():
	global runner
	global vier

	os.environ['WDM_LOG_LEVEL'] = '0'
	os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

	runner = Runner()
	vier = Vier(runner=runner)
	vier.run()

if __name__ == '__main__':
	current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
	finish_datetime = '2021-8-3 00:00'

	if current_datetime < finish_datetime:
		try:
			main()
		except KeyboardInterrupt:
			runner.stop()
			vier.quit()
		finally:
			vier.quit()
	else:
		print('Срок пробного периода истек.')
		_ = input()

