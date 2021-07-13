from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from urllib.parse import urljoin

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from requests.exceptions import SSLError

from app import logger, config, accounts

import time
import os

class Scrapper(object):
	"""docstring for Scrapper"""
	def __init__(self, url=None):
		self.driver = None
		self.start_url = config['START_URL']

	def create_driver(self):
		driver = None

		options = Options()
		options.add_experimental_option('excludeSwitches', ['enable-logging']) #disables webdriver loggs

		try:
			driver = webdriver.Chrome('chromedriver.exe', service_log_path=os.path.devnull, options=options)
		except SSLError:
			logger.error('An SSLError occured during driver creation.')
		else:
			logger.debug('Driver was created successfully.')
			self.driver = driver

	def open_start_url(self):
		try:
			self.driver.get(self.start_url)
		except Exception:
			logger.error('An error occured trying to open start url.')
		else:
			logger.debug('Start url opened successfully.')

	def login(self, account):
		driver = self.driver

		login_btn = None
		try:
			login_btn = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, '//li[@class="nav-item"]/a[@class="nav-link p-2"]/button[@data-toggle="modal"]')))
		except TimeoutException:
			logger.warning('Login button was not found in time.')
			raise
		else:
			driver.execute_script("arguments[0].click();", login_btn)

		user_name_filed = None
		password_filed = None
		submit_btn = None
		try:
			user_name_filed = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, '//input[@name="username"]')))
			password_filed = driver.find_element_by_xpath('//input[@name="password"]')
			submit_btn = driver.find_element_by_xpath('//button[@class="login100-form-btn"]')
		except TimeoutException:
			logger.warning('Log in field was not found in time.')
			raise

		try:
			user_name_filed.send_keys(account['username'])
			password_filed.send_keys(account['password'])
			submit_btn.click()
		except Exception:
			username = account['username']
			password = account['password']
			logger.warning(f'An error occured trying to enter log in data {username}:{password}.')
			raise

		#add check for banned accounts

		logger.info('Successfully logged into account.')

	def book_datetime(self, d, t):
		assert d and t

		def click_next(driver):
			submit_btn = driver.find_element_by_xpath('//button[@id="next"]')
			submit_btn.click()

		time.sleep(3)

		try:
			self.driver.get(urljoin(self.start_url, '/book'))
		except Exception:
			logger.error('An error occured trying to open booking url.')
		else:
			logger.debug('Booking url opened successfully.')

		driver = self.driver
		transport_category = None
		try:
			transport_category = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, '//div[@id="category"]/div')))
		except TimeoutException:
			logger.warning('Failed to find transport category button.')

		try:
			transport_category.click()
			click_next(driver)
		except Exception:
			logger.warning('Failed to choose transport category.')

		customs = None
		try:
			customs = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, '//div[@id="category"]/div')))
		except TimeoutException:
			logger.warning('Failed to find customs category button.')

		try:
			customs.click()
			click_next(driver)
		except Exception:
			logger.warning('Failed to choose customs category.')

		calendar = None
		try:
			calendar = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, '//table[@class=" table"]')))
		except TimeoutException:
			logger.warning('Failed to find calendar to choose date.')

		day = None
		try:
			day = calendar.find_element_by_xpath(f'/tbody//td[@class="active day" OR @class="day"]/div[text()={d}]')
		except NoSuchElementException:
			logger.warning('Date is not available.')

		_ = input('---')
		


	def close_driver(self):
		try:
			self.driver.quit()
		except Exception:
			logger.warning('An error occured during driver closing.')
		else:
			logger.info('Driver was successfully closed.')

	def run(self):
		self.create_driver()
		self.open_start_url()
		while True:
			try:
				self.login(next(accounts))
				break
			except Exception:
				pass

		self.book_datetime(15, 2)
		self.close_driver()