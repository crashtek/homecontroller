from __init__ import *

from auth.WaitingForLogin import WaitingForLogin
from home.HomeController import HomeController

class GettingStartedView:
	def addToBox(self, box):
		self._gettingStartedMessage = gz.Text(box, 'Welcome to the Home Controller, to get started you must log in')
		self._button = gz.PushButton(box, text='Login', command=self.__login)

	def __login(self):
		"""Initiate Login"""
		HomeController().changeView(WaitingForLogin())
