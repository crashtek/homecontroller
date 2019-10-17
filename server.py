#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__      = "Carlos Mostek"
__credits__     = ["Carlos Mostek"]
__license__     = "MIT"
__version__     = "0.1"
__maintainer__  = "Carlos Mostek"
__email__       = "carlosmostek@gmail.com"
__status__      = "Development"


from __init__ import *

from auth.AuthService import AuthService

from auth.GettingStartedView import GettingStartedView


class HomeController(BaseWidget):
	''' This is the base window '''
	
	def __init__(self):
		super(HomeController,self).__init__('Home Controller')
		self.auth = AuthService()

		self._panel = ControlEmptyWidget()
		self._closeButton = ControlButton('Close')
		self._closeButton.value = self.__exitEvent

		self.formset = [
			('', '', '_closeButton'),
		 	('', '_panel', '')
		]

		self.set_margin(20)

		if (self.auth.neverAuthenticated()):
			self._panel.value = GettingStartedView(self)
		else:
			self.warning('Dont know how to deal with ever authenticated')
			# self._panel.value = LocalLogin(self)
	
	def changeView(self, view):
		self._panel.value = view

	def __exitEvent(self):
		self.close()
		exit()

	def __dummyEvent(self):
		self.warn("Menu option selected")




##################################################################################################################
##################################################################################################################
##################################################################################################################

#Execute the application
if __name__ == "__main__":	 pyforms.start_app( HomeController, geometry=(200, 200, 680, 520) )
