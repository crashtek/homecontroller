import http.client
import pyqrcode
import json
#import cv2
import io
from PIL import Image
import np

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
			buffer = io.BytesIO()
			urlQrCode.png(buffer, scale=5, quiet_zone=10)
			numpyValue = np.fromstring(buffer.getvalue(), dtype=np.uint8)
			return Image.fromarray(a)
			# return cv2.imdecode(numpyValue, cv2.IMREAD_UNCHANGED)

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
