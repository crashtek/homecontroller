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


class HomeController:
	''' This is the base window '''
	
	def __init__(self):
		self.auth = AuthService()

		self._app = gz.App(title="Home Controller", width=460, height=300)
		menubar = gz.MenuBar(self._app,
				  toplevel=["File"],
				  options=[
					  [ ["Exit", self.__exitEvent] ]
				  ])

		# self._closeButton = ControlButton('Close')
		# self._closeButton.value = self.__exitEvent
		self._box = gz.Box(self._app)

		# self.formset = [
		# 	('', '', '_closeButton'),
		#  	('', '_panel', '')
		# ]

		# self.set_margin(20)

		if (self.auth.neverAuthenticated()):
			self._view = GettingStartedView(self)
		else:
			self.warning('Dont know how to deal with ever authenticated')
			# self._panel.value = LocalLogin(self)

		self._view.addToBox(self._box)
		self._app.display()
		
	
	def changeView(self, view):
		self._box.destroy()
		self._box = gz.Box(self._app)
		self._view = view
		self._view.addToBox(self._box)

	def __exitEvent(self):
		exit()

	def __dummyEvent(self):
		self.warn("Menu option selected")




##################################################################################################################
##################################################################################################################
##################################################################################################################

#Execute the application
if __name__ == "__main__":	 HomeController()
