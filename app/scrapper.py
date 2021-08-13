from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from urllib.parse import urljoin

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from requests.exceptions import SSLError, ProxyError

from app import logger, config, accounts, proxies, auto_numbers
from app.notifier import TelegramNotifier
from app.utils import add_order_to_list, remove_order_from_list, get_order_list, dump_order_list

import time
import datetime
import random
import psutil
import threading
import traceback
import os

lock = threading.RLock()

class TimeNotAvailableException(Exception):
	pass

class LoginException(Exception):
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
		except Exception:
			logger.warning('Exception occured trying to get new proxy from list.')
		finally:
			lock.release()
		return proxy

	def get_account(self):
		lock.acquire()
		account = None
		try:
			account = next(accounts)
		except Exception:
			logger.warning('Exception occured trying to get new account from list.')
		finally:
			lock.release()
		return account

	def get_auto_number(self):
		lock.acquire()
		auto_number = None
		try:
			auto_number = next(auto_numbers)
		except Exception:
			logger.warning('Exception occured trying to get auto number from list.')
		finally:
			lock.release()
		return auto_number

	def wait_after_order_creation(self):
		#time out after making order
		start_time = time.time()
		while True:
			if time.time() - start_time < config['TIME_OUT'] * 60:
				self.order.update_time_to_wait(int((config['TIME_OUT']*60 - (time.time() - start_time))/60))
				time.sleep(60)
			else:
				self.order.update_time_to_wait(0)
				break

	def save_order_info(self, filename, account, date, time, customs):
		lock.acquire()
		try:
			add_order_to_list(filename, account, date, time, customs, config['TIME_OUT'])
		except Exception:
			logger.warning('Exception occured trying to add new order info to list.')
		finally:
			lock.release()

	def get_accounts_with_order(self, file_name):
		accounts = get_order_list(file_name)
		
		try:
			for account in accounts:
				try:
					if datetime.datetime.now() > datetime.datetime.strptime(account['datetime'] , '%Y-%m-%d %H'):
						accounts.remove(account)
						remove_order_from_list(file_name, account)
				except KeyError:
					dt = datetime.datetime.now() + datetime.timedelta(hours=config['TIME_OUT'])
					account['datetime'] = dt.strftime('%Y-%m-%d %H')
		except Exception:
			logger.exception('An error occurred trying to get accounts with orders.')

		dump_order_list(file_name, accounts)

		return [account['account']['username'] for account in accounts]

	def create_driver(self):
		driver = None

		options = Options()
		options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2}) #disables pictures loading
		options.add_experimental_option('excludeSwitches', ['enable-logging']) #disables webdriver loggs
		options.add_argument("--start-maximized")
		'''
		#Error: DevToolsActivePort file doesn't exist
		#Fix:
		options.add_argument("--remote-debugging-port=9222")
		options.add_argument("--disable-dev-shm-using") 
		'''
		if config['HEADLESS_MODE']:
			options.add_argument("--headless")

		proxy = None
		if config['PROXY_MODE']:
			try:
				proxy = self.get_proxy()
			except StopIteration:
				message = 'Got the end of proxy list.'
				logger.warning(message)
				self.notifier.send_message(message)
				raise

			options.add_argument(f"--proxy-server={proxy}")

		driver = None
		try:
			driver = webdriver.Chrome(ChromeDriverManager().install(), service_log_path=os.path.devnull, options=options)
		except SSLError:
			logger.error('An SSLError occured during driver creation.')
			raise
		else:
			logger.debug('Driver was created successfully.')
			self.driver = driver

	def get_new_driver(self):
		for i in range(3):
			try:
				self.create_driver()
				break
			except Exception as e:
				logger.warning(f'An error occured during driver creation. {e.args}')
				if i >= 2:
					raise

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
			raise LoginException

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
													(By.XPATH, '//button[text()="Выйти"]')))
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
			self.open_url(urljoin(self.url, '/book/new'))
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

		try:
			transport = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//div[@id="category"]//span[contains(text(),"{auto_type}")]')))
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

		try:
			customs = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
													(By.XPATH, f'//div[@id="category"]//span[contains(text(),"{customs_type}")]')))
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

		while True:
			c_start_date = start_date
			d = t = None
			for _ in range(delta_days+1):
				d = conver_date_to_str(c_start_date)
				try:
					self.open_url(urljoin(self.url, f'/book/time?date={d}'))
				except Exception:
					logger.warning(f'Failed to choose date {d}.')
					raise

				self.driver.execute_script("window.scrollTo(0, 350)") 

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

				c_start_date += datetime.timedelta(days=1)

			if not time_interval:
				message = "Date and time are not available."
				logger.warning(message)
				self.notifier.send_message(message)
				self.order.update_status('Time is not available')
				if config['MODE']:
					raise TimeNotAvailableException
				else:
					self.order.update_status('Updating')
					time.sleep(config['DELAY_BETWEEN_UPDATES'])
					continue

			try:
				time_interval.click()
				click_next(self.driver)
				break
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

			if config['GET_AUTO_NUMBER_FROM_FILE']:
				reg_number = self.get_auto_number()

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

			dont_recieve_email_btn = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
														(By.XPATH, '//div[2]/label[@class="category"]/span[@class="radio-custom"]')))
			dont_recieve_email_btn.click()
			time.sleep(0.3)
			checkbox = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
														(By.XPATH, '//input[@id="agree"]')))
			checkbox.click()

			submit_btn = self.driver.find_elements_by_xpath('//button[@type="submit"]')[-1]
			submit_btn.click()
		except Exception:
			#logger.warning('Failed to confirm getting message on email.')
			logger.warning('Failed to disable getting message on email.')

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
				logger.warning('Exception in login into account while canseling orders.')
			try:
				self.cancel_order()
			except Exception:
				logger.warning('Exception in canceling order.')
			try:
				self.logout()	
			except Exception:
				logger.warning('Exception in login out while canseling orders.')	

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
			p = psutil.Process(self.driver.service.process.pid)
			for i in p.children(recursive=True):
				try:
					i.kill()
				except Exception:
					pass
			p.kill()
		except Exception as e:
			logger.warning(f'An error occured during driver closing. {e.args}')
		else:
			logger.info('Driver was successfully closed.')

	def run(self):
		try:
			self.get_new_driver()
		except Exception:
			return

		while True:
			while True:
				try:
					new_account = None
					accounts_with_order = self.get_accounts_with_order('orders.json')
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
				except (TimeoutException, NoSuchElementException) as e:
					self.order.update_status('Login failed')
					continue
				except LoginException:
					self.order.update_status('Login failed')
					self.close_driver()
					time.sleep(1)
					try:
						self.get_new_driver()
					except Exception:
						return
					continue
				except Exception as e:
					logger.exception(f'Uncatched exception during login.')
					self.order.update_status('Login failed')
					self.close_driver()
					time.sleep(1)
					try:
						self.get_new_driver()
					except Exception:
						return
					continue

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
				time.sleep(1)
				try:
					self.get_new_driver()
				except Exception:
					return
				continue
			except TimeNotAvailableException:
				if config['MODE']:
					self.logout()
					self.cancel_all_orders()
					self.close_driver()
					return
				else:
					self.order.update_status('Updating')
					time.sleep(config['DELAY_BETWEEN_UPDATES'])
			except Exception as e:
				logger.exception(f'Uncatched exception during making order.')
				self.order.update_status('Failed to make order.')
				self.close_driver()
				time.sleep(1)
				try:
					self.get_new_driver()
				except Exception:
					return
				continue

			self.logout()
			self.wait_after_order_creation()

		self.close_driver()