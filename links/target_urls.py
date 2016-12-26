import json, requests
from requests.auth import HTTPBasicAuth

# DOMAIN = 'http://10.50.202.114:8000'
# DOMAIN = 'http://aasaninternet.com:786'
DOMAIN = 'http://192.168.1.108:8000'

SEND_SMS_URL = DOMAIN+'/api/ad/send_sms/'
CREATE_URL = DOMAIN+'/api/ad/create/'
EXPIRE_URL = DOMAIN+'/api/ad/update/'
UPDATE_URL = DOMAIN+'/api/ad/update/'
HISTORY_URL = DOMAIN+'/api/ad/history/'

# USERNAME = 'admin'
# PASSWORD = 'aasanads'

USERNAME = 'fahad'
PASSWORD = 'Pakistan1!'

CONNECT_TIMEOUT = 5#0.01
READ_TIMEOUT = 5

def call_aasan_api(data,operation):
	data_json = json.dumps(data)
	headers = {'Content-type':'application/json'}
	if operation == 'expire':
		target_url = EXPIRE_URL
	elif operation == 'create':
		target_url = CREATE_URL
	elif operation == 'send_sms':
		target_url = SEND_SMS_URL
	elif operation == 'history':
		target_url = HISTORY_URL
	response = requests.post(target_url, data=data_json,auth=HTTPBasicAuth(USERNAME,PASSWORD), \
		timeout=(CONNECT_TIMEOUT,READ_TIMEOUT))
	return response
	# print response.body