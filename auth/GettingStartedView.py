from __init__ import *

from auth.WaitingForLogin import WaitingForLogin

class GettingStartedView (BaseWidget):
	def __init__(self, mainWindow):
		super(GettingStartedView, self).__init__('Getting Started View')

		self._mainWindow = mainWindow

		self._button = ControlButton('Login')
		self._button.value = self.__login
		self._gettingStartedMessage = ControlLabel('Welcome to the Home Controller, to get started you must log in')

		self.formset = [
			['_gettingStartedMessage'], 
			['', '_button', '']
		]

		self.set_margin(10)

	def __login(self):
		"""Initiate Login"""
		self._mainWindow.changeView(WaitingForLogin(self._mainWindow))
