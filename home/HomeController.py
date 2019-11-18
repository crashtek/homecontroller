import sqlite3

from __init__ import *

class HomeController:
	''' This is the base window '''
	# Inner Singleton class
	class _HomeController:
		def __init__(self):
			self.width = 480
			self.height = 250

			self._app = gz.App(title="Home Controller", width=self.width, height=self.height)
			menubar = gz.MenuBar(self._app,
					toplevel=["File"],
					options=[
						[ ["Exit", self.__exitEvent] ]
					])
			
			self._box = None
		
		def changeView(self, view):
			if self._box is not None:
				self._box.destroy()
			self._box = gz.Box(self._app, width=self.width, height=self.height)
			self._view = view
			self._view.addToBox(self._box)
			self._app.update()

		def setTimer(self, seconds, command):
			self._app.after(int(seconds*1000), command)

		def cancelTimer(self, command):
			self._app.cancel(command)

		def start(self):
			self._app.display()

		def __exitEvent(self):
			exit()

		def __dummyEvent(self):
			self.warn("Menu option selected")


	__instance = None

	def __init__(self):
		if not HomeController.__instance:
			HomeController.__instance = HomeController._HomeController()

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)
