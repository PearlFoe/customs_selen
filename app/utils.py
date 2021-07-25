from app import logger

import json

def get_config(file_name):
	data = None
	try:
		with open(file_name) as f:
			data = json.loads(f.read())
	except FileNotFoundError:
		logger.error(f'Failed to get config from file {file_name}.')
	else:
		logger.debug('Successfully got config.')
		return data

def get_accounts(file_name):
	data = []
	try:
		with open(file_name, encoding='Windows-1251') as f:
			data = f.read().split('\n')
	except FileNotFoundError:
		logger.error(f'An error occured trying to ger accounts from file {file_name}.')
	else:
		logger.debug('Successfully gor accounts.')

		for account in data:
			if account:
				yield {
					'username': account.split(':')[0],
					'password':	account.split(':')[1]
				}

def get_proxy(file_name):
	data = None
	with open(file_name) as f:
		data = f.read().split('\n')

	for proxy in data:
		if proxy:
			yield proxy

def get_order_data(file_name):
	data = None
	with open(file_name, encoding='utf-8') as f:
		data = json.loads(f.read())

	return data

def get_order_list(file_name):
	data = None
	try:
		with open(file_name, encoding='utf-8') as f:
			data = json.loads(f.read())
	except FileNotFoundError:
		return []
	else:
		return data

def add_order_to_list(file_name, account, date, time, customs):
	list_ = get_order_list(file_name)
	usernames = [i['account']['username'] for i in list_]

	if account['username'] in usernames:
		for i in list_:
			if account['username'] == i['account']['username']:
				i['date'] = date
				i['time'] = time
				i['customs'] = customs
	else:
		order = {
			"account": {
				"username": account['username'],
				"password": account['password']
			},
			"date": date,
			"time": time,
			"customs": customs
		}
		list_.append(order)

	with open(file_name, 'w', encoding='utf-8') as f:
		json.dump(list_, f, ensure_ascii=False)

def remove_order_from_list(file_name, account):
	list_ = get_order_list(file_name)

	for i in list_:
		if account['username'] == i['account']['login']:
			list_.remove(i)
			break

	with open(file_name, 'w', encoding='utf-8') as f:
		json.dump(list_, f, ensure_ascii=False)