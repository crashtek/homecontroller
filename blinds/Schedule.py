import sqlite3
import http
import time
import pytz
from datetime import datetime, timedelta

from __init__ import *

from Database import Database
from home.HomeController import HomeController

def getSchedules(room):
	db = Database()
	cursor = db.getCursor()
	schedules = []
	cursor.execute('''
	SELECT 
		schedule_order as schedule_order,
		command as command,
		startDoW as startDoW,
		endDoW as endDoW,
		hour as hour,
		minute as minute
	FROM schedule
	WHERE room_id=:room_id
	''', { 'room_id': room.getId() })
	for row in cursor:
		schedules.append(Schedule(row, room))

	return schedules

class EditScheduleView:
	def __init__(self, room, schedule=None):
		self.room = room
		self.schedule = schedule

	def addToBox(self, box):
		order = None
		command = None
		startDoW = None
		endDoW = None
		hour = None
		minute = None
		if self.schedule is not None:
			order = self.schedule.order
			command = self.schedule.command
			startDoW = self.schedule.startDoW
			endDoW = self.schedule.endDoW
			hour = self.schedule.hour
			minute = self.schedule.minute

		addScheduleForm = gz.Box(box, layout='grid', width='fill', height='fill')
		gz.Text(addScheduleForm, text='Order:', grid=[0,0], align='right')
		self.order = gz.TextBox(addScheduleForm, grid=[1,0], align='left', text=order, width=15)
		gz.Text(addScheduleForm, text='Command:', grid=[0,1], align='right')
		self.command = gz.TextBox(addScheduleForm, grid=[1,1], align='left', text=command, width=15)
		gz.Text(addScheduleForm, text='Start Day of Week:', grid=[0,2], align='right')
		self.startDoW = gz.TextBox(addScheduleForm, grid=[1,2], align='left', text=startDoW, width=15)
		gz.Text(addScheduleForm, text='End Day of Week:', grid=[0,3], align='right')
		self.endDoW = gz.TextBox(addScheduleForm, grid=[1,3], align='left', text=endDoW, width=15)
		gz.Text(addScheduleForm, text='Hour:', grid=[0,4], align='right')
		self.hour = gz.TextBox(addScheduleForm, grid=[1,4], align='left', text=hour, width=15)
		gz.Text(addScheduleForm, text='Minute:', grid=[0,5], align='right')
		self.minute = gz.TextBox(addScheduleForm, grid=[1,5], align='left', text=minute, width=15)
		gz.PushButton(addScheduleForm, text='Save', grid=[0,6,2,1], command=self.saveSchedule)

	def saveSchedule(self):
		db = Database()
		cursor = db.getCursor()
		values = {
			'schedule_order': self.order.value,
			'command': self.command.value,
			'startDoW': self.startDoW.value,
			'endDoW': self.endDoW.value,
			'hour': self.hour.value,
			'minute': self.minute.value,
			'room_id': self.room.getId()
		}
		if self.schedule is not None:
			values['original_order'] = self.schedule.order
			cursor.execute('''
				UPDATE Schedule 
				SET
					schedule_order=:schedule_order,
					command=:command,
					startDoW=:startDoW,
					endDoW=:endDoW,
					minute=:minute,
					hour=:hour
				WHERE
					room_id=:room_id AND
					schedule_order=:original_order
				''', values)
		else:
			cursor.execute('''
				INSERT INTO Schedule
				(room_id, schedule_order, command, startDoW, endDoW, hour, minute)
				VALUES
				(:room_id, :schedule_order, :command, :startDoW, :endDoW, :hour, :minute)
			''', values)
		cursor.connection.commit()
		self.room.view()

class Schedule:
	Sunday = 6
	Monday = 0
	Tuesday = 1
	Wednesday = 2
	Thursday = 3
	Friday = 4
	Saturday = 5

	def intToDoW(self, doW):
		doWMap = {
			Schedule.Sunday: 'Su',
			Schedule.Monday: 'Mo',
			Schedule.Tuesday: 'Tu',
			Schedule.Wednesday: 'We',
			Schedule.Thursday: 'Th',
			Schedule.Friday: 'Fr',
			Schedule.Saturday: 'Sa'
		}
		return doWMap[doW]

	def __init__(self, row, room):
		self.mytz = pytz.timezone('America/Chicago')
		self.seconds = 200
		self.room = room
		self.order = row['schedule_order']
		self.command = row['command']
		self.startDoW = row['startDoW']
		self.startDoWStr = self.intToDoW(self.startDoW)
		self.endDoW = row['endDoW']
		self.endDoWStr = self.intToDoW(self.endDoW)
		self.hour = row['hour']
		self.minute = row['minute']

	def edit(self): 
		HomeController().changeView(EditScheduleView(self.room, self))

	def delete(self): 
		db = Database()
		cursor = db.getCursor()
		cursor.execute('''
		DELETE FROM schedule
		WHERE room_id=:room_id AND schedule_order=:order
		''', {
			'room_id': self.room.getId(),
			'order': self.order
		})
		cursor.connection.commit()
		self.room.view()

	def getNextDoW(self, lastDoW):
		nextDoW = lastDoW + 1
		if nextDoW > 6: nextDoW = 0
		return nextDoW

	def validDay(self, doW):
		if self.startDoW <= self.endDoW:
			return doW >= self.startDoW and doW <= self.endDoW
		else:
			return doW <= self.startDoW or doW >= self.endDoW
	
	def nextTime(self):
		now = datetime.now(pytz.timezone('America/Chicago'))
		today = now.today()
		nextDoW = today.weekday()
		days = 0
		nextTime = None
		while nextTime is None or nextTime <= datetime.now(self.mytz):
			while not self.validDay(nextDoW):
				nextDoW = self.getNextDoW(nextDoW)
				days += 1

			# We match this schedule
			nextTime = datetime(today.year, today.month, today.day, self.hour, self.minute) + timedelta(days=days)
			nextTime = self.mytz.localize(nextTime)
			print('Carlos, now %s, next %s'%(datetime.now(self.mytz), nextTime))
			nextDoW = self.getNextDoW(nextDoW)
			days += 1
		return nextTime

	def __str__(self):
		return '%s-%s %02d:%02d'%(self.startDoWStr, self.endDoWStr, self.hour, self.minute)

	def __repr__(self): return str(self)
	
	def exec(self):
		delaySeconds=0
		for window in self.room.windows:
			if delaySeconds > 0: time.sleep(window.seconds)
			if self.command == 'up':
				window.up()
			elif self.command == 'down':
				window.down()
			delaySeconds = window.seconds
