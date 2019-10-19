from __init__ import *
from auth.AuthService import AuthService

class Dashboard:
	def __init__(self, mainWindow):
		self._mainWindow = mainWindow
		self._auth = AuthService()

	def addToBox(self, box):
		user = self._auth.getUser()
		print(str(user))
		gz.Text(box, text="Welcome %s %s"%(user['given_name'], user['family_name']))