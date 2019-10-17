from __init__ import *

from auth.AuthService import AuthService

class WaitingForLogin:
	def __init__(self, mainWindow):
		self._mainWindow = mainWindow
		self.auth = AuthService()
		self._qrCodeImage = self.auth.getCode()

	def addToBox(self, box):
		self._qrCode = gz.Picture(box, image=self._qrCodeImage)
		# TODO: Wait for login to happen, then redirect to logged in
