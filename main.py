from app import logger, config
from app.runner import Runner
from app.UI import Vier

@logger.catch
def main():
	global runner
	global vier

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