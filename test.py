from app.UI import Vier
from app.runner import Runner

def main():
	runner = Runner()
	vier = Vier(runner=runner)
	vier.run()

if __name__ == '__main__':
	main()