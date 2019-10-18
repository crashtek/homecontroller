from __init__ import *

from auth.AuthService import AuthService
from Dashboard import Dashboard

class WaitingForLogin:
	def __init__(self, mainWindow):
		self._mainWindow = mainWindow
		self._auth = AuthService()
		self._qrCodeImage = self._auth.getCode()

	def addToBox(self, box):
		self._box = box
		gz.Text(box, text='Scan this QR code with your phone to log in')
		self._qrCode = gz.Picture(box, image=self._qrCodeImage)
		box.after(self._auth.getInterval(), self.checkLogin)
		# TODO: Wait for login to happen, then redirect to logged in

	def checkLogin(self):
		if self._auth.checkLogin():
			self._mainWindow.changeView(Dashboard(self._mainWindow))
		else:
			self._box.after(self._auth.getInterval(), self.checkLogin)