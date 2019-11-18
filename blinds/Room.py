from __init__ import *

from Database import Database
from blinds.Schedule import getSchedules, EditScheduleView
from blinds.ScheduleClock import ScheduleClock
from blinds.Window import getWindows, EditWindowView
from home.HomeController import HomeController

def getRooms():
	db = Database()
	cursor = db.getCursor()
	rooms = []
	cursor.execute('SELECT name as name, rowid as rowid FROM room')
	for row in cursor:
		rooms.append(Room(row))

	return rooms

def createRoom(name):
	db = Database()
	cursor = db.getCursor()
	cursor.execute('INSERT INTO room (name) VALUES (:name)', { 'name': name })
	cursor.connection.commit()

class ViewWindows:
	def __init__(self, room):
		self.room = room

	def addToBox(self, box):
		gz.Text(box, text='Room: %s, Next Schedule: %s'%(self.room.getName(), self.room.getNextSchedule().nextTime()))
		windowsTable = gz.Box(box, layout='grid', width='fill', height='fill')
		rowNum = 0
		if len(self.room.windows) == 0:
			gz.Text(windowsTable, text='No Windows Found', grid=[0,0,6,1])
			rowNum += 1
		else:
			gz.Text(windowsTable, text='Window Name', grid=[0,0])
			gz.Text(windowsTable, text='Commands', grid=[1,0,5,1])
			rowNum += 1
			for window in self.room.windows:
				gz.Text(windowsTable, text=window.name, grid=[0,rowNum])
				gz.PushButton(windowsTable, text='Up', grid=[1, rowNum], command=window.up)
				gz.PushButton(windowsTable, text='Dn', grid=[2, rowNum], command=window.down)
				gz.PushButton(windowsTable, text='St', grid=[3, rowNum], command=window.stop)
				gz.PushButton(windowsTable, text='Edit', grid=[4, rowNum], command=window.edit)
				gz.PushButton(windowsTable, text='Delete', grid=[5, rowNum], command=window.delete)
				rowNum += 1		

		gz.PushButton(windowsTable, text='Add Window', grid=[6, 0], command=self.addWindow)
		gz.PushButton(windowsTable, text='Schedules', grid=[6, 1], command=self.schedules)
		gz.PushButton(windowsTable, text='Dashboard', grid=[6, 2], command=self.dashboard)

	def addWindow(self):
		HomeController().changeView(EditWindowView(self.room))

	def schedules(self):
		HomeController().changeView(ViewSchedules(self.room))

	def dashboard(self):
		HomeController().changeView(ViewSchedules.DashboardConstructor())

class ViewSchedules:
	DashboardConstructor = None

	def __init__(self, room):
		self.room = room

	def addToBox(self, box):
		gz.Text(box, text='Room: %s, Next Schedule: %s'%(self.room.getName(), self.room.getNextSchedule().nextTime()))
		windowsTable = gz.Box(box, layout='grid', width='fill', height='fill')
		rowNum = 0
		if len(self.room.schedules) == 0:
			gz.Text(windowsTable, text='No Schedules Found', grid=[0,rowNum,6,1])
			rowNum += 1
		else:
			gz.Text(windowsTable, text='Schedules:', grid=[0,rowNum])
			rowNum += 1
			for schedule in self.room.schedules:
				gz.Text(windowsTable, text=schedule.command, grid=[0,rowNum])
				gz.Text(windowsTable, text='%s'%(str(schedule)), grid=[1,rowNum, 2, 1])
				gz.PushButton(windowsTable, text='Edit', grid=[3, rowNum], command=schedule.edit)
				gz.PushButton(windowsTable, text='Delete', grid=[4, rowNum, 2, 1], command=schedule.delete, align='left')
				rowNum += 1
		gz.PushButton(windowsTable, text='Add Schedule', grid=[6, 0], command=self.addSchedule)
		gz.PushButton(windowsTable, text='Windows', grid=[6, 1], command=self.windows)
		gz.PushButton(windowsTable, text='Dashboard', grid=[6, 2], command=self.dashboard)

	def addSchedule(self):
		HomeController().changeView(EditScheduleView(self.room))

	def windows(self):
		HomeController().changeView(ViewWindows(self.room))

	def dashboard(self):
		HomeController().changeView(ViewSchedules.DashboardConstructor())

class RoomSchedule:
	def __init__(self, room, execTime): 
		self.time = execTime

class Room:
	def __init__(self, row):
		self.name = row['name']
		self.id = row['rowid']
		self.windows = getWindows(self)
		self.schedules = getSchedules(self)

	def view(self):
		self.windows = getWindows(self)
		self.schedules = getSchedules(self)

		HomeController().changeView(ViewSchedules(self))
		ScheduleClock().update()

	def getName(self): return self.name

	def getId(self): return self.id

	def getNextSchedule(self):
		nextSchedule = None
		nextTime = None
		for schedule in self.schedules:
			scheduleNextTime = schedule.nextTime()
			print('Carlos found next time %s and %s'%(scheduleNextTime, nextTime))
			if nextTime is None or nextTime > scheduleNextTime: 
				nextTime = scheduleNextTime
				nextSchedule = schedule

		return nextSchedule
