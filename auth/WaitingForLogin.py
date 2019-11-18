from __init__ import *

from auth.AuthService import AuthService
from home.Dashboard import Dashboard
from home.HomeController import HomeController

class WaitingForLogin:
	def __init__(self):
		self._auth = AuthService()
		self._authCodeData = self._auth.getCode()

	def addToBox(self, box):
		self._box = box
		textToDisplay="""
To Log In:
Either open a browser to %s AND
enter code %s, OR
Scan this QR code with your phone AND
confirm that the page displays this code %s"""%(
			self._authCodeData['verification_uri'], 
			self._authCodeData['user_code'], 
			self._authCodeData['user_code']
		)
		gz.Text(box, text=textToDisplay)
		self._qrCode = gz.Picture(box, image=self._authCodeData['qrImage'])
		box.after(self._authCodeData['interval']*1000, self.checkLogin)
		# TODO: Wait for login to happen, then redirect to logged in

	def checkLogin(self):
		if self._auth.checkLogin():
			HomeController().changeView(Dashboard())
		else:
			self._box.after(self._authCodeData['interval']*1000, self.checkLogin)