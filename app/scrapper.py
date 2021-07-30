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

from app import logger, config, accounts, proxies
from app.notifier import TelegramNotifier
from app.utils import add_order_to_list, remove_order_from_list, get_order_list

import time
import datetime
import threading
import os

lock = threading.RLock()

class TimeNotAvailableException(Exception):
	pass

class Scrapper(object):
	"""docstring for Scrapper"""
	def __init__(self, order):
		self.driver = None
		self.url = config['URL']
		self.login_url = config['LOGIN_URL']
		self.logout_url = config['LOGOUT_URL']
		self.order = order
		self.notifier = TelegramNotifier(login=self.order.login)

	def get_proxy(self):
		lock.acquire()
		proxy = None
		try:
			proxy = next(proxies)
		finally:
			lock.release()
		return proxy

	def get_account(self):
		lock.acquire()
		account = None
		try:
			account = next(accounts)
		finally:
			lock.release()
		return account

	def save_order_info(self, filename, account, date, time, customs):
		lock.acquire()
		try:
			add_order_to_list(filename, account, date, time, customs)
		finally:
			lock.release()

	def create_driver(self):
		driver = None

		options = Options()
		options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2}) #disables pictures loading
		options.add_experimental_option('excludeSwitches', ['enable-logging']) #disables webdriver loggs
		
		if config['HEADLESS_MODE']:
			options.add_argument("--headless")

		proxy = None
		try:
			proxy = self.get_proxy()
		except StopIteration:
			message = 'Got the end of proxy list.'
			logger.warning(message)
			self.notifier.send_message(message)
			raise

		seleniumwire_options = {
			'proxy': {
				'http': f'http://{proxy}', 
				'https': f'https://{proxy}',
				'no_proxy': 'localhost,127.0.0.1'
			}
		}

		driver = None
		try:
			if config['PROXY_MODE']:
				driver = webdriver.Chrome(ChromeDriverManager().install(), service_log_path=os.path.devnull, options=options, seleniumwire_options=seleniumwire_options)
			else:
				driver = webdriver.Chrome(ChromeDriverManager().install(), service_log_path=os.path.devnull, options=options)
		except SSLError:
			logger.error('An SSLError occured during driver creation.')
			raise
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
		username = account['username']
		password = account['password']

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
			user_name_filed.send_keys(username)
			password_filed.send_keys(password)
			submit_btn.click()
		except Exception:
			logger.warning(f'An error occured trying to enter log in data {username}:{password}.')
			raise

		#add check for banned accounts
		try:
			_ = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
													(By.XPATH, '//li[@id="liLogin"]')))
		except TimeoutException:
			message = f'Account {username}:{password} is banned.'
			logger.warning(message)
			self.notifier.send_message(message)
			raise
		else:
			logger.info('Successfully logged into account.')

	def order_datetime(self, account, start_date, end_date, start_time, end_time, auto_type, customs_type, reg_number, brand, model, country):

		def click_next(driver):
			submit_btn = driver.find_element_by_xpath('//button[@id="next"]')
			submit_btn.click()

		def conver_date_to_str(date):
			day = str(date.day) if date.day > 9 else f'0{date.day}'
			month = str(date.month) if date.month > 9 else f'0{date.month}'
			s_date = f'{day}.{month}.{date.year}'

			return s_date

		time.sleep(3)

		start_date = datetime.datetime.strptime(start_date, '%d.%m.%Y')
		end_date = datetime.datetime.strptime(end_date, '%d.%m.%Y')

		try:
			self.open_url(urljoin(self.url, '/book'))
		except Exception:
			logger.error('An error occured trying to open booking url.')
			raise
		else:
			logger.debug('Booking url opened successfully.')

		transport = None
		transport_category = [
			'Легковой автомобиль',
			'Грузовой автомобиль',
			'Автобус',
			'Легковой/пассажирский микроавтобус',
			'Мотоцикл'
		]
		'''
		category:
		1 - легковой автомобиль
		2 - грузовой автомобиль
		3 - автобус
		4 - микроавтобус
		5 - мотоцикл
		'''
		try:
			transport = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//div[@id="category"]/div[{transport_category.index(auto_type)+1}]')))
		except TimeoutException:
			logger.warning('Failed to find transport category button.')
			raise

		try:
			transport.click()
			click_next(self.driver)
		except Exception:
			logger.warning('Failed to choose transport category.')
			raise

		customs = None
		customs_category = [
			'Брест',
			'Урбаны',
			'Брузги',
			'Котловка',
			'Григоровщина'
		]
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
													(By.XPATH, f'//div[@id="category"]/div[{customs_category.index(customs_type)+1}]')))
		except TimeoutException:
			logger.warning('Failed to find customs category button.')
			raise

		try:
			customs.click()
			click_next(self.driver)
		except Exception:
			logger.warning('Failed to choose customs category.')
			raise

		time_interval = None
		delta_days = end_date - start_date
		delta_days = delta_days.days

		t_intervals = ['00-01', '01-02', '02-03', '03-04', '04-05', 
					'05-06', '06-07', '07-08', '08-09', '09-10', 
					'10-11', '11-12', '12-13', '13-14', '14-15', 
					'15-16', '16-17', '17-18', '18-19', '19-20', 
					'20-21', '21-22', '22-23', '23-00']
		d = t = None
		for _ in range(delta_days+1):
			d = conver_date_to_str(start_date)
			try:
				self.open_url(urljoin(self.url, f'/book/time?date={d}'))
			except Exception:
				logger.warning(f'Failed to choose date {d}.')
				raise

			try:
				_ = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
															(By.XPATH, '//div[@class="currentDatePanel"]')))
			except TimeoutException:
				message = "Page haven't loaded in time. Unnable to choose time."
				logger.warning(message)
				self.notifier.send_message(message)


			for t in t_intervals[t_intervals.index(start_time):t_intervals.index(end_time)+1]:
				try:
					dt = d.replace('.','_') + '_' + t.split('-')[0]
					time_interval = self.driver.find_element_by_xpath(f'//div[@data-interval="{dt}" and contains(@class, "intervalAvailable")]')
				except NoSuchElementException:
					pass

			start_date += datetime.timedelta(days=1)

		if not time_interval:
			message = "Date and time are not available."
			logger.warning(message)
			self.notifier.send_message(message)
			self.order.update_status('Time is not available')
			raise TimeNotAvailableException

		try:
			time_interval.click()
			click_next(self.driver)
		except Exception:
			logger.warning('Failed to choose date and time.')
			raise

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
			raise

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
			raise

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
			raise

		confirm_payment_btn = None
		try:
			confirm_payment_btn = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
														(By.XPATH, f'//button[@class="btn btn-outline-dark btn-lg next"]')))
			confirm_payment_btn.click()
		except TimeoutException:
			logger.warning('Failed to confirm payment.')
			raise
		else:
			logger.info('Order was made successfully.')

		try:
			self.save_order_info('orders.json', account, d, t, customs_type)
		except Exception:
			logger.warning('Exception occured trying to save order info.')

		self.order.update_status('Ordered')
		self.order.update_datetime(d, t)

		#time out after making order
		start_time = time.time()
		while True:
			if time.time() - start_time < config['TIME_OUT']:
				time.sleep(1)
				self.order.update_time_to_wait(int(config['TIME_OUT'] - (time.time() - start_time)))
			else:
				self.order.update_time_to_wait(0)
				break
		
	def cancel_order(self):
		try:
			self.open_url(urljoin(self.url, '/cabinet/bookings'))
		except Exception:
			logger.warning('An error occured trying to open url to cancel order.')
			raise

		try:
			_ = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//table[@id="myBookings"]')))
		except TimeoutException:
			logger.warning('Failed to load order in time.')
			raise

		cancel_btn = None
		try:
			cancel_btn = self.driver.find_elements_by_xpath('//button[@class="btn btn-danger cancelOrder"]')[0]
		except Exception:
			logger.warning('Failed to find order cancel button.')
			raise

		try:
			cancel_btn.click()
		except Exception:
			logger.warning('Failed to click order cancel button.')
			raise

		confirm_btn = None
		try:
			confirm_btn = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//button[@id="modal_yes"]')))
			self.driver.execute_script("arguments[0].click();", confirm_btn)
		except TimeoutException:
			logger.warning('Failed to confirm order canceling.')
			raise
		else:
			logger.info('Order was canceled successfully.')

		remove_order_from_list('orders.json', account)

	def cancel_all_orders(self):
		for i in get_order_list('orders.json'):
			try:
				self.login(i['account'])
			except Exception:
				logger.warning('Exception in logging')
			try:
				self.cancel_order()
			except Exception:
				logger.warning('Exception in canceling')
			try:
				self.logout()	
			except Exception:
				logger.warning('Exception in logout')	

	def logout(self):
		try:
			self.open_url(self.logout_url)
		except Exception:
			logger.error('An error occured trying to log out.')
			raise
		else:
			logger.info('Logged out successfully.')

	def close_driver(self):
		try:
			self.driver.quit()
		except Exception:
			logger.warning('An error occured during driver closing.')
		else:
			logger.info('Driver was successfully closed.')

	def run(self):
		try:
			self.create_driver()
		except Exception:
			return

		new_account = None
		while True:
			try:
				new_account = None
				accounts_with_order = [i['account']['username'] for i in get_order_list('orders.json')]
				new_account = self.get_account()

				while True:
					if new_account['username'] in accounts_with_order:
						logger.warning(f'Account {new_account["username"]} already has active order.')
						new_account = self.get_account()
					else:
						break

				self.order.update_login(new_account['username'])
				self.order.update_status('Logging in')
				self.login(new_account)
				break
			except StopIteration:
				logger.warning('Got end of the accounts list.')
				self.notifier.send_message('Got the end of accounts list.')
				self.close_driver()
				return
			except (TimeoutException, NoSuchElementException) as e:
				self.order.update_status('Login failed')

		self.order.update_status('Making order')
		try:
			self.order_datetime(
					new_account,
					self.order.start_date, 
					self.order.end_date, 
					self.order.start_time,
					self.order.end_time,
					self.order.auto_type,
					self.order.customs_type,
					self.order.reg_number, 
					self.order.car_brand, 
					self.order.car_model, 
					self.order.region,
			)
		except (TimeoutException, NoSuchElementException) as e:
			self.order.update_status('Failed to make order.')
			self.logout()
			self.close_driver()
			return
		except TimeNotAvailableException:
			if config['MODE']:
				self.logout()
				self.cancel_all_orders()
				self.close_driver()
				return
			else:
				self.logout()
				self.close_driver()
				return

		self.logout()
		self.close_driver()