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
