from datetime import datetime
import pytz

from home.HomeController import HomeController

class ScheduleClock:
	# Inner Singleton class, this class could be exported and be a standalone
	class _ScheduleClock:
		def __init__(self, getRooms):
			self.getRooms = getRooms
			self.timer = None
			self.update()

		def update(self):
			HomeController().cancelTimer(self.execute)
			rooms = self.getRooms()
			nextTime = None
			self.nextSchedules = []
			for room in rooms:
				schedule = room.getNextSchedule()
				roomNextTime = schedule.nextTime()
				if nextTime is None: 
					nextTime = roomNextTime
				if roomNextTime < nextTime: nextTime = roomNextTime
				if roomNextTime == nextTime:
					self.nextSchedules.append(schedule)
			
			secondsToWait = nextTime.timestamp() - datetime.now().timestamp()
			print('Scheduling next command: waiting %f seconds for %s'%(secondsToWait, nextTime))

			HomeController().setTimer(secondsToWait, self.execute)

		def execute(self):
			for schedule in self.nextSchedules:
				schedule.exec()
			self.timer = None
			self.update()

	__instance = None

	def __init__(self, getRooms=None):
		if not ScheduleClock.__instance:
			if getRooms is None:
				print('Bad initialization of the getRooms object')
				exit(-1)
			ScheduleClock.__instance = ScheduleClock._ScheduleClock(getRooms)

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)
