from __init__ import *

from auth.AuthService import AuthService

class WaitingForLogin (BaseWidget):
	def __init__(self, mainWindow):
		super(WaitingForLogin, self).__init__('Waiting for Login')

		self._mainWindow = mainWindow
		self.auth = AuthService()
		qrCodeImage = self.auth.getCode()
		self._qrCode = ControlImage()
		self._qrCode.value = qrCodeImage

		# TODO: Wait for login to happen, then redirect to logged in
