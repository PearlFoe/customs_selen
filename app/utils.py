from app import logger

from json.decoder import JSONDecodeError

import json
import datetime

def get_config(file_name):
	data = None
	try:
		with open(file_name) as f:
			data = json.loads(f.read())
	except Exception:
		logger.exception(f'An error occurred trying to get config info from file {file_name}.')
	else:
		logger.debug('Successfully got config.')
		return data

def get_accounts(file_name):
	data = []
	try:
		with open(file_name, encoding='utf-8-sig') as f:
			data = f.read().split('\n')
	except Exception:
		logger.exception(f'An error occurred trying to get accounts from file {file_name}.')
	else:
		logger.debug('Successfully got accounts.')
		while True:
			for account in data:
				if account:
					yield {
						'username': account.split(':')[0],
						'password':	account.split(':')[1]
					}

def get_auto_numbers(file_name):
	data = []
	try:
		with open(file_name, encoding='utf-8') as f:
			data = f.read().split('\n')
	except Exception:
		logger.exception(f'An error occurred trying to get auto numbers from file {file_name}.')
	else:
		logger.debug('Successfully got auto numbers.')	
		while True:
			for num in data:
				if num:
					yield num

def get_proxy(file_name):
	data = None
	try:
		with open(file_name) as f:
			data = f.read().split('\n')
	except Exception:
		logger.exception(f'An error occured trying to get proxy from file.')
	else:
		logger.debug('Successfully got proxy from file.')
		while True:
			for proxy in data:
				if proxy:
					yield proxy

def get_order_data(file_name):
	data = None
	try:
		with open(file_name, encoding='utf-8') as f:
			data = json.loads(f.read())
	except Exception:
		logger.exception(f'An error occurred trying to get order data from file {file_name}.')

	return data

def get_order_list(file_name):
	data = None
	try:
		with open(file_name, encoding='utf-8') as f:
			data = json.loads(f.read())
	except FileNotFoundError:
		return []
	except Exception:
		logger.warning(f'An error occurred trying to get order list from file {file_name}.')

	return data if data and len(data) > 0 else []

def dump_order_list(file_name, list_):
	if not list_ or len(list_) == 0:
		list_ = []

	try:
		with open(file_name, 'w', encoding='utf-8') as f:
			json.dump(list_, f, ensure_ascii=False)
	except Exception:
		logger.exception('Exception occured trying to dump order list.')

def add_order_to_list(file_name, account, date, time, customs, time_to_add):
	list_ = get_order_list(file_name)
	usernames = [i['account']['username'] for i in list_]

	dt = datetime.datetime.now() + datetime.timedelta(minutes=time_to_add)

	if account['username'] in usernames:
		for i in list_:
			if account['username'] == i['account']['username']:
				i['date'] = date
				i['time'] = time
				i['customs'] = customs
				i['datetime'] = dt.strftime('%Y-%m-%d %H') 
	else:
		order = {
			"account": {
				"username": account['username'],
				"password": account['password']
			},
			"date": date,
			"time": time,
			"customs": customs,
			"datetime": dt.strftime('%Y-%m-%d %H')
		}
		list_.append(order)

	dump_order_list(file_name, list_)

def remove_order_from_list(file_name, account):
	list_ = get_order_list(file_name)

	if len(list_) == 0:
		return
		
	for i in list_:
		if account['account']['username'] == i['account']['username']:
			list_.remove(i)
			break

	dump_order_list(file_name, list_)