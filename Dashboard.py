from __init__ import *
from auth.AuthService import AuthService
from blinds.Room import getRooms, createRoom

class Dashboard:
	def __init__(self, mainWindow):
		self._mainWindow = mainWindow
		self._auth = AuthService()

	def addCell(self, roomsTable, text, grid):
		gz.Text(roomsTable, text=text, grid=grid, width='fill', height='fill')
		cellBox = gz.Box(roomsTable, grid=grid, border=True, width='fill', height='fill')

	def addToBox(self, box):
		user = self._auth.getUser()
		gz.Text(box, text='Welcome %s %s'%(user['given_name'], user['family_name']))
		roomsTable = gz.Box(box, layout='grid')
		rowNum = 0
		rooms = getRooms()
		if len(rooms) == 0:
			gz.Text(roomsTable, text='No Rooms Found', grid=[0,0,3,1])
			rowNum += 1
		else:
			# Header Row
			self.addCell(roomsTable, text='Room', grid=[0,0])
			self.addCell(roomsTable, text='Next Change', grid=[1,0])
			rowNum += 1
			for room in rooms:
				self.addCell(roomsTable, text=room.getName(), grid=[0,rowNum])
				self.addCell(roomsTable, text='???', grid=[1,rowNum])
				gz.PushButton(roomsTable, text='View', grid=[2, rowNum], command=room.view)
				rowNum += 1
		self.newRoomText = gz.TextBox(roomsTable, grid=[0, rowNum])
		gz.PushButton(roomsTable, text='Add Room', grid=[1, rowNum], command=self.addRoom)

	def addRoom(self):
		name = self.newRoomText.value
		room = createRoom(name)
		self._mainWindow.changeView(Dashboard(self._mainWindow))

