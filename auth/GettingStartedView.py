from __init__ import *

# from auth.WaitingForLogin import WaitingForLogin

class GettingStartedView:
	def __init__(self, mainWindow, frame):
		self._mainWindow = mainWindow

		self._gettingStartedMessage = gz.Text(frame, 'Welcome to the Home Controller, to get started you must log in')
		self._button = gz.PushButton(frame, text='Login', command=self.__login)

	def __login(self):
		"""Initiate Login"""
		# self._mainWindow.changeView(WaitingForLogin(self._mainWindow))
