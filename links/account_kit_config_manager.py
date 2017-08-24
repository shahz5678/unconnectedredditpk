import requests, ast, hashlib, hmac
from redis3 import access_error_log
from unconnectedreddit.account_kit_settings import FAID, AKAS


class AccountKitManager(object):
	obj = None

	def __init__(self, app_id, app_secret):
		self.app_secret = app_secret
		self.app_access_token = 'AA|{0}|{1}'.format(app_id, app_secret)

	def get_user_cred(self, auth_code):
		if not self.obj:
			# Rretrieving user access token...
			self.set_user_cred(auth_code)
		return self.obj

	def set_user_cred(self, auth_code, url=None):
		if not url:
			url = 'https://graph.accountkit.com/v1.2/access_token?grant_type=authorization_code&code={0}&access_token={1}&appsecret_proof={2}'.\
			format(auth_code,self.app_access_token,self.get_appsecret_proof(self.app_access_token))
		data = self.retrieve_data(url)
		data = self.evaluate_data(data)
		# print "The user access token is: %s" % data["access_token"] # this is returned in lieu of the auth_code
		try:
			string_obj = self.retrieve_user_cred(data["access_token"]) #log the error when this shows a KeyError
			self.obj = self.evaluate_data(string_obj)
		except KeyError:
			access_error_log(app_access_token=self.app_access_token, auth_code=auth_code, data=data)
			string_obj = self.retrieve_user_cred(data["access_token"]) #creating keyerror anyway
			self.obj = self.evaluate_data(string_obj)

	def retrieve_user_cred(self, user_access_token, url=None):
		if not url:
			url = 'https://graph.accountkit.com/v1.2/me/?access_token={0}&appsecret_proof={1}'.\
			format(user_access_token,self.get_appsecret_proof(user_access_token))
		return self.retrieve_data(url)

	def retrieve_data(self, url):
		return requests.get(url).text

	def evaluate_data(self, data):
		return ast.literal_eval(data)

	def get_appsecret_proof(self, access_token):
		# the app secret proof is a sha256 hash of the relevant access token, using the app secret as the key
		# documentation: https://developers.facebook.com/docs/graph-api/securing-requests
		h = hmac.new(self.app_secret.encode('utf-8'),msg=access_token.encode('utf-8'),digestmod=hashlib.sha256)
		return h.hexdigest()

	# only works once Account Kit is deactivated and one wants to retrieve their entire user database
	# need to set permission in App Dashboard as per details here: https://developers.facebook.com/docs/accountkit/graphapi
	def get_all_users(self, paginate_by, url=None):
		if not url:
			url = 'https://graph.accountkit.com/v1.2/<app_id>/accounts/?&access_token={0}&limit={1}&appsecret_proof={2}'.\
			format(self.app_access_token,paginate_by,self.get_appsecret_proof(self.app_access_token))
		return requests.get(url).text



def account_kit_handshake(csrf, state, status, auth_code, csrf_omitted):
	if csrf_omitted:
		if status == "NOT_AUTHENTICATED":
			return state, None, {'csrf':csrf,'state':state,'status':status,'auth_code':auth_code}
		else:
			mobile_data = AccountKitManager(FAID, AKAS)
			user_data = mobile_data.get_user_cred(auth_code)
			if FAID == user_data["application"]["id"]:
				return state, user_data["phone"], {} # passing user_id (currently in 'state') instead of AK_ID
			else:
				# app id mismatch
				return None, None, {'csrf':csrf,'state':state,'status':status,'facebook_id':FAID,'returned_id':user_data["application"]["id"], 'auth_code':auth_code}
	else:
		if csrf == state and status=='PARTIALLY_AUTHENTICATED':
			mobile_data = AccountKitManager(FAID, AKAS)
			user_data = mobile_data.get_user_cred(auth_code)
			if FAID == user_data["application"]["id"]:
				return user_data["id"], user_data["phone"], {}
			else:
				# app id mismatch
				return None, None, {'csrf':csrf,'state':state,'status':status,'facebook_id':FAID,'returned_id':user_data["application"]["id"], 'auth_code':auth_code}
		elif status == 'NOT_AUTHENTICATED':
			return None, None, {'csrf':csrf,'state':state,'status':status,'auth_code':auth_code}
		else:
			# csrf mismatch, or could not authenticate
			return None, None, {'csrf':csrf,'state':state,'status':status,'auth_code':auth_code}