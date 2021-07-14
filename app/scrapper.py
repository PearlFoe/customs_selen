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
	def __init__(self):
		self.driver = None
		self.url = config['URL']
		self.login_url = config['LOGIN_URL'] 

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

	def open_url(self, url):
		try:
			self.driver.get(url)
		except Exception:
			#logger.error(f'An error occured trying to open url {url}.')
			raise
		else:
			#logger.debug(f'Url {url} opened successfully.')
			pass

	def login(self, account):
		try:
			self.open_url(self.login_url + '/cabinet/bookings')
		except Exception:
			logger.error('An error occured trying to open login url.')

		user_name_filed = None
		password_filed = None
		submit_btn = None
		try:
			user_name_filed = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, '//input[@id="l_username"]')))
			password_filed = self.driver.find_element_by_xpath('//input[@id="password"]')
			submit_btn = self.driver.find_element_by_xpath('//button[@id="loginBtn"]')
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
		time.sleep(1)

	def order_datetime(self, d, t, reg_number, brand, model, country):
		assert d and t

		def click_next(driver):
			submit_btn = driver.find_element_by_xpath('//button[@id="next"]')
			submit_btn.click()

		time.sleep(3)

		try:
			self.open_url(urljoin(self.url, '/book'))
		except Exception:
			logger.error('An error occured trying to open booking url.')
		else:
			logger.debug('Booking url opened successfully.')

		transport_category = None
		transport_category = 1
		'''
		category:
		1 - легковой автомобиль
		2 - грузовой автомобиль
		3 - автобус
		4 - микроавтобус
		5 - мотоцикл
		'''
		try:
			transport_category = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//div[@id="category"]/div[{transport_category}]')))
		except TimeoutException:
			logger.warning('Failed to find transport category button.')

		try:
			transport_category.click()
			click_next(self.driver)
		except Exception:
			logger.warning('Failed to choose transport category.')

		customs = None
		customs_category = 1
		'''
		category:
		1 - Брест
		2 - Урбаны
		3 - Брузги
		4 - Котловка
		5 - Григоровщина
		'''
		try:
			customs = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//div[@id="category"]/div[{customs_category}]')))
		except TimeoutException:
			logger.warning('Failed to find customs category button.')

		try:
			customs.click()
			click_next(self.driver)
		except Exception:
			logger.warning('Failed to choose customs category.')

		try:
			self.open_url(urljoin(self.url, f'/book/time?date={d}'))
		except Exception:
			logger.warning(f'Failed to choose date {d}.')

		time_interval = None
		try:
			dt = d.replace('.','_') + '_' + t.split('-')[0]
			time_interval = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//div[@data-interval="{dt}" and contains(@class, "intervalAvailable")]')))
		except TimeoutException:
			logger.warning('Date and time are not available.')

		try:
			time_interval.click()
			click_next(self.driver)
		except Exception:
			logger.warning('Failed to choose date and time.')

		reg_number_field = None
		brand_field = None
		model_filed = None
		country_filed = None
		try:
			reg_number_field = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//input[@name="vehicles[0].regnum"]')))
			brand_field = self.driver.find_element_by_xpath('//div[@class="selectize-control autoBand single"]/div/input')
			model_filed = self.driver.find_element_by_xpath('//input[@name="vehicles[0].model"]')
			country_filed = self.driver.find_element_by_xpath('//div[@class="selectize-control autoCountry single"]/div/input')
		except TimeoutException:
			logger.warning('An error occured trying to find vehicle data fileds.')

		try:
			reg_number_field.clear()
			reg_number_field.send_keys(reg_number)
			brand_field.clear()
			brand_field.send_keys(brand)
			brand_field.send_keys(Keys.ENTER)
			model_filed.clear()
			model_filed.send_keys(model)
			country_filed.clear()
			country_filed.send_keys(country)
			country_filed.send_keys(Keys.ENTER)

			click_next(self.driver)
		except Exception:
			logger.warning('An error occured trying to input vehicle data.')

		#get email block
		try:
			actions = ActionChains(self.driver)
			checkbox = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
														(By.XPATH, f'//input[@id="agree"]')))
			checkbox.click()

			submit_btn = self.driver.find_elements_by_xpath('//button[@type="submit"]')[-1]
			submit_btn.click()
		except Exception:
			logger.warning('Failed to confirm getting message on email.')

		confirm_payment_btn = None
		try:
			confirm_payment_btn = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
														(By.XPATH, f'//button[@class="btn btn-outline-dark btn-lg next"]')))
			confirm_payment_btn.click()
		except TimeoutException:
			logger.warning('Failed to confirm payment.')
	
	def cancel_order(self):
		try:
			self.open_url(urljoin(self.url, '/cabinet/bookings'))
		except Exception:
			logger.warning('An error occured trying to open url to cancel order.')

		try:
			_ = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//table[@id="myBookings"]')))
		except TimeoutException:
			logger.warning('Failed to load order in time.')

		cancel_btn = None
		try:
			cancel_btn = self.driver.find_elements_by_xpath('//button[@class="btn btn-danger cancelOrder"]')[0]
		except Exception:
			logger.warning('Failed to find order cancel button.')

		try:
			cancel_btn.click()
		except Exception:
			logger.warning('Failed to click order cancel button.')


		confirm_btn = None
		try:
			confirm_btn = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//button[@id="modal_yes"]')))
			self.driver.execute_script("arguments[0].click();", confirm_btn)
		except TimeoutException:
			logger.warning('Failed to confirm order canceling.')
		else:
			logger.info('Order was canceled successfully.')

	def close_driver(self):
		try:
			self.driver.quit()
		except Exception:
			logger.warning('An error occured during driver closing.')
		else:
			logger.info('Driver was successfully closed.')

	def run(self):
		self.create_driver()
		while True:
			try:
				self.login(next(accounts))
				break
			except Exception:
				pass

		self.order_datetime('15.07.2021', '11-12', 'ek074mr', 'mazda', '3', 'RU')
		time.sleep(3)
		self.cancel_order()
		self.close_driver()