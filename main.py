from app import logger, config
from app.runner import Runner
from app.UI import Vier

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
	try:
		main()
	except KeyboardInterrupt:
		runner.stop()
		vier.quit()
	finally:
		vier.quit()