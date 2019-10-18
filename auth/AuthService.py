import http.client
import pyqrcode
import json
#import cv2
import io
from PIL import Image, ImageTk
import np
import jwt

class AuthService:
	# Inner Singleton class
	class __AuthService:
		def __init__(self):
			self.expiresAt = None
			self.domain = "crashtek.auth0.com"
			self.clientId = "1THQcij7ylAueUXhuzbieovwhvKo9f6h"
			self.scope = "openid+profile+offline_access"
			self.audience = "urn:arduino:blindcontroller"
			self.__user = None
			self.__neverAuthenticated = True

		def getCode(self):
			conn = http.client.HTTPSConnection(self.domain)
			payload = "client_id=%s&scope=%s&audience=%s"%(self.clientId,self.scope,self.audience)
			headers = { 'content-type': "application/x-www-form-urlencoded" }
			url = "/oauth/device/code"
			conn.request("POST", url, payload, headers)
			res = conn.getresponse()
			data = res.read()
			decodedData = json.loads(data.decode("utf-8"))
			print(decodedData)
			urlQrCode = pyqrcode.create(decodedData["verification_uri_complete"])
			self._verificationResponse = decodedData
			#buffer = io.BytesIO()
			name='qr.png'
			urlQrCode.png(name, scale=5, quiet_zone=10)
			#numpyValue = np.fromstring(buffer.getvalue(), dtype=np.uint8)
			#return ImageTk.PhotoImage(Image.fromarray(numpyValue))
			# return cv2.imdecode(numpyValue, cv2.IMREAD_UNCHANGED)
			return Image.open(name)

		def validateToken(self, token):
			conn = http.client.HTTPSConnection(self.domain)
			url = "/.well-known/jwks.json"
			conn.request("GET", url)
			res = conn.getresponse()
			data = res.read()
			jwks = json.loads(data.decode("utf-8"))
			print(str(jwks))

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
		
		def getInterval(self):
			return self._verificationResponse['interval'] * 1000

		def checkLogin(self):
			conn = http.client.HTTPSConnection(self.domain)
			payload = "grant_type=urn%%3Aietf%%3Aparams%%3Aoauth%%3Agrant-type%%3Adevice_code&device_code=%s&client_id=%s"%(self._verificationResponse['device_code'],self.clientId)
			headers = { 'content-type': "application/x-www-form-urlencoded" }
			url = "/oauth/token"
			conn.request("POST", url, payload, headers)
			res = conn.getresponse()
			data = res.read()
			decodedData = json.loads(data.decode("utf-8"))
			if 'error' in decodedData:
				if decodedData['error'] == 'authorization_pending':
					print('Not ready yet')
				else:
					print('Unexpected error: %s'%decodedData['error'])
				return False
			else:
				# hooray, got some tokens!
				print('hooray, got tokens!')
				self.validateToken(decodedData['id_token'])
				return True

		def getUser(self): return self._user

		def isAuthenticated(self):
			return self.__user

		def neverAuthenticated(self):
			return self.__neverAuthenticated

	__instance = None

	def __init__(self):
		if not AuthService.__instance:
			AuthService.__instance = AuthService.__AuthService()

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)
