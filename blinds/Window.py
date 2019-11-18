import sqlite3
import http

from __init__ import *

from Database import Database
from home.HomeController import HomeController

def getWindows(room):
	db = Database()
	cursor = db.getCursor()
	windows = []
	cursor.execute('''
	SELECT 
		name as name,
		ipaddress as ipaddress,
		upcommand as upcommand,
		downcommand as downcommand,
		stopcommand as stopcommand
	FROM window
	WHERE room_id=:room_id
	''', { 'room_id': room.getId() })
	for row in cursor:
		windows.append(Window(row, room))

	return windows

class EditWindowView:
	def __init__(self, room, window=None):
		self.room = room
		self.window = window

	def addToBox(self, box):
		name = None
		ipaddress = None
		up = None
		down = None
		stop = None
		if self.window is not None:
			name = self.window.name
			ipaddress = self.window.ipaddress
			up = self.window.upCommand
			down = self.window.downCommand
			stop = self.window.stopCommand

		addWindowForm = gz.Box(box, layout='grid', width='fill', height='fill')
		gz.Text(addWindowForm, text='Name:', grid=[0,0], align='right')
		self.name = gz.TextBox(addWindowForm, grid=[1,0], align='left', text=name, width=15)
		gz.Text(addWindowForm, text='IP Address:', grid=[0,1], align='right')
		self.ipaddress = gz.TextBox(addWindowForm, grid=[1,1], align='left', text=ipaddress, width=15)
		gz.Text(addWindowForm, text='Up Command:', grid=[0,2], align='right')
		self.up = gz.TextBox(addWindowForm, grid=[1,2], align='left', text=up, width=15)
		gz.Text(addWindowForm, text='Down Command:', grid=[0,3], align='right')
		self.down = gz.TextBox(addWindowForm, grid=[1,3], align='left', text=down, width=15)
		gz.Text(addWindowForm, text='Stop Command:', grid=[0,4], align='right')
		self.stop = gz.TextBox(addWindowForm, grid=[1,4], align='left', text=stop, width=15)
		gz.PushButton(addWindowForm, text='Save', grid=[0,5,2,1], command=self.saveWindow)

	def saveWindow(self):
		db = Database()
		cursor = db.getCursor()
		values = {
			'name': self.name.value,
			'ipaddress': self.ipaddress.value,
			'upcommand': self.up.value,
			'downcommand': self.down.value,
			'stopcommand': self.stop.value,
			'room_id': self.room.getId()
		}
		if self.window is not None:
			values['original_name'] = self.window.name
			cursor.execute('''
				UPDATE window 
				SET
					name=:name,
					ipaddress=:ipaddress,
					upcommand=:upcommand,
					downcommand=:downcommand,
					stopcommand=:stopcommand
				WHERE
					room_id=:room_id AND
					name=:original_name
				''', values)
		else:
			cursor.execute('''
				INSERT INTO window
				(room_id, name, ipaddress, upcommand, downcommand, stopcommand)
				VALUES
				(:room_id, :name, :ipaddress, :upcommand, :downcommand, :stopcommand)
			''', values)
		cursor.connection.commit()
		self.room.view()

class Window:
	def __init__(self, row, room):
		self.seconds = 200
		self.room = room
		self.name = row['name']
		self.ipaddress = row['ipaddress']
		self.upCommand = row['upcommand']
		self.downCommand = row['downcommand']
		self.stopCommand = row['stopcommand']

	def postToBlindsController(self,command,seconds=None):
		conn = http.client.HTTPConnection(self.ipaddress)
		path = '/%d'%command
		if seconds is not None: path += '/%d'%seconds
		print('Carlos, sending: %s'%path)
		conn.request("POST", path)
		res = conn.getresponse()
		if res.status != 200:
			print("Bad response: %d"%res.status)
		else:
			print('Successfully performed the command!')

	def up(self): self.postToBlindsController(self.upCommand, self.seconds)
	def down(self): self.postToBlindsController(self.downCommand, self.seconds)
	def stop(self): self.postToBlindsController(self.stopCommand)
	def edit(self): 
		HomeController().changeView(EditWindowView(self.room, self))
	def delete(self): print('not implemented')
