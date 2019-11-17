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
from Dashboard import Dashboard

class HomeController:
	''' This is the base window '''
	
	def __init__(self):
		self.auth = AuthService()
		self.width = 480
		self.height = 250

		self._app = gz.App(title="Home Controller", width=self.width, height=self.height)
		menubar = gz.MenuBar(self._app,
				  toplevel=["File"],
				  options=[
					  [ ["Exit", self.__exitEvent] ]
				  ])

		self._box = gz.Box(self._app, width=self.width, height=self.height)

		# Eventually we will want to let people log in locally with a PIN
		if (not self.auth.isAuthenticated()):
			self._view = GettingStartedView(self)
		else:
			self._view = Dashboard(self)

		self._view.addToBox(self._box)
		self._app.display()
		
	
	def changeView(self, view):
		self._box.destroy()
		self._box = gz.Box(self._app, width=self.width, height=self.height)
		self._view = view
		self._view.addToBox(self._box)
		self._box.update()
		self._app.update()

	def __exitEvent(self):
		exit()

	def __dummyEvent(self):
		self.warn("Menu option selected")




##################################################################################################################
##################################################################################################################
##################################################################################################################

#Execute the application
if __name__ == "__main__":	 HomeController()
