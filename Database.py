import sqlite3

class Database:
	# Inner Singleton class, this class could be exported and be a standalone
	class _Database:
		# NOTE: better if we store it in the keychain this will store refresh token
		# in plain text for now, shouldn't be done in production
		databaseName = '.sqlite.db'

		def __init__(self):
			self.connection = sqlite3.connect(self.databaseName)
			self.connection.row_factory = sqlite3.Row

			cursor = self.connection.cursor()
			# Initialize the schema
			if not self.checkIfTableExists('room'):
				cursor.execute('CREATE TABLE room(name TEXT)')
			if not self.checkIfTableExists('window'):
				cursor.execute('''
				CREATE TABLE window(
					room_id INT, 
					name TEXT, 
					ipaddress TEXT, 
					upcommand INT, 
					downcommand INT,
					stopcommand INT,
					CONSTRAINT window_primary_key PRIMARY KEY (room_id, name)
				)''')
			#IF YOU NEED TO UPDATE SCHEMA: cursor.execute("DROP TABLE schedule")
			#self.connection.commit()
			if not self.checkIfTableExists('schedule'):
				cursor.execute("""CREATE TABLE schedule(
					room_id INT, 
					schedule_order INT,
					command TEXT,
					startDoW INT,
					endDoW INT,
					hour INT,
					minute INT,
					CONSTRAINT window_primary_key PRIMARY KEY (room_id, schedule_order)
				)""")
			self.connection.commit()

		def getCursor(self):
			return self.connection.cursor()

		def checkIfTableExists(self, name):
			cursor = self.connection.cursor()
			cursor.execute("SELECT name as name FROM sqlite_master WHERE type='table' AND name='%s'"%name)
			foundTable = False
			for row in cursor:
				if row['name'] == name: foundTable = True
			return foundTable

	__instance = None

	def __init__(self):
		if not Database.__instance:
			Database.__instance = Database._Database()

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)
