import http.client
import io
import json
import jwt
import os
import pickle
import time
import urllib.parse
import webbrowser

import pyqrcode
from PIL import Image
from auth.Configuration import Configuration

class AuthService:
	# Inner Singleton class, this class could be exported and be a standalone
	class _AuthService:
		# NOTE: better if we store it in the keychain this will store refresh token
		# in plain text for now, shouldn't be done in production
		dataStoreName = '.authdata'

		def __init__(self, domain, clientId, scope, audience):
			self.domain = domain
			self.clientId = clientId
			self.scope = scope
			self.audience = audience
			self.expiresAt = None
			self._user = None
			self._verificationResponse = None
			self._refreshToken = None

			try:
				dataFile = open(self.dataStoreName, 'rb')
				authData = pickle.load(dataFile)
				self._user = authData['user']
				self._refreshToken = authData['refreshToken']
				dataFile.close()
			except FileNotFoundError:
				# Ignore this, it just means we don't have a refresh token saved
				pass

		def postToAuth(self, path, params):
			conn = http.client.HTTPSConnection(self.domain)
			payload = urllib.parse.urlencode(params)
			headers = { 'content-type': "application/x-www-form-urlencoded" }
			conn.request("POST", path, payload, headers)
			res = conn.getresponse()
			data = res.read()
			return json.loads(data.decode("utf-8"))


		def getCode(self):
			# First Call the device/code endpoint so we can initiate the login request
			decodedData = self.postToAuth(params = {
				"client_id": self.clientId,
				"scope": self.scope,
				"audience": self.audience
			}, path = '/oauth/device/code')

			# Now that we have data from device/code, we need to generate a QR code so that it can be 
			# displayed to the user as an easy way for them to initiate the actual authentication request on their device
			urlQrCode = pyqrcode.create(decodedData["verification_uri_complete"])
			self._verificationResponse = decodedData
			
			# Too painful to try to get this working directly in memory, though it is definitely possible
			name='.qr.deleteme.png'
			urlQrCode.png(name, scale=2, quiet_zone=2)
			
			# This generic image should be usable in most GUI platforms including web, delete it after we open the file
			qrImage = Image.open(name)
			os.remove(name)
			
			# We also want a text version for CLIs
			qrText = urlQrCode.terminal()

			# Here we return more than just the code because we leave it up to the application to decide how to display it to the 
			# user.  Perhaps we could have the SDK provide some OOTB options.  Having a terminal display might be good.
			self.loginRequestData = {
				"qrImage": qrImage,
				"qrText": qrText,
				"user_code": decodedData["user_code"], 
				"verification_uri": decodedData["verification_uri"],
				"verification_uri_complete": decodedData["verification_uri_complete"],
				"expires_in": decodedData["expires_in"],
				"expires_at": time.time() + decodedData["expires_in"],
				"interval": decodedData["interval"]
			}

			return self.loginRequestData

		# Internal only method for checking whether the returned token is valid
		def _validateToken(self, token):
			conn = http.client.HTTPSConnection(self.domain)
			url = "/.well-known/jwks.json"
			conn.request("GET", url)
			res = conn.getresponse()
			data = res.read()
			jwks = json.loads(data.decode("utf-8"))

			public_keys = {}
			for jwk in jwks['keys']:
				kid = jwk['kid']
				public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

			kid = jwt.get_unverified_header(token)['kid']
			key = public_keys[kid]

			try:
				self._user = jwt.decode(token, 
					key=key, 
					issuer='https://%s/'%self.domain,
					audience=self.clientId,
					algorithms=['RS256'])
				return True
			except Exception as e:
				print("Failed token validation")
				print(e)
				return False
		
		def _processTokenResults(self, decodedData):
			# hooray, got some tokens!
			self._validateToken(decodedData['id_token'])
			self._user["accessToken"] = decodedData["access_token"]
			self._user['expires_at'] = time.time() + decodedData['expires_in']
			self._refreshToken = decodedData["refresh_token"]
			dataFile = open(self.dataStoreName, 'wb')
			authData = pickle.dump({
				'user': self._user,
				'refreshToken': self._refreshToken
			}, dataFile)
			dataFile.close()

		
		def waitForUser(self, auto=False):
			if self._user: return self._user

			if auto:
				# Fetch the code if it hasn't been done yet
				loginData = None
				if self._verificationResponse is not None:
					loginData = self._verificationResponse
				else:
					loginData = self.getCode()
				# open the browser automatically
				webbrowser.open_new(loginData['verification_uri_complete'])

			# wait for the user to log in
			while time.time() <= self.loginRequestData["expires_at"]:
				if (self.checkLogin()):
					break
				time.sleep(self.loginRequestData["interval"])

			return self._user

		# checks if the user has logged in yet by calling the /oauth/token endpoint with the device code
		def checkLogin(self):
			decodedData = self.postToAuth(params = {
				"grant_type": "urn:ietf:params:oauth:grant-type:device_code",
				"device_code": self._verificationResponse['device_code'],
				"client_id": self.clientId
			}, path = '/oauth/token')

			if 'error' in decodedData:
				if decodedData['error'] == 'authorization_pending':
					print('Not ready yet')
				elif decodedData['error'] == 'slow_down':
					print('Slow Down!')
					self.loginRequestData["interval"] = self.loginRequestData["interval"] + 1
				elif decodedData['error'] == 'access_denied':
					print('User is not Authorized')
					exit(-1)
				else:
					print('Unexpected error: %s'%decodedData['error'])
					exit(-1)
				return False
			else:
				self._processTokenResults(decodedData)
				return True

		def getUser(self):
			if self.isAuthenticated():
				if self._user['expires_at'] < time.time():
					# refresh the user's tokens
					decodedData = self.postToAuth(params = {
						"grant_type": "refresh_token",
						"refresh_token": self._refreshToken,
						"client_id": self.clientId
					}, path = '/oauth/token')

					self._processTokenResults(decodedData)

			return self._user

		def isAuthenticated(self):
			return self._user != None

		def logout(self):
			if os.path.exists(self.dataStoreName):
				os.remove(self.dataStoreName)
			self._user = None
			webbrowser.open_new("https://%s/v2/logout"%(self.domain))

	__instance = None

	def __init__(self):
		if not AuthService.__instance:
			AuthService.__instance = AuthService._AuthService(
				domain=Configuration.domain,
				clientId = Configuration.clientId,
				scope = "openid profile offline_access",
				audience = Configuration.audience
			)

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)
