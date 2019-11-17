from Database import Database

def getRooms():
	db = Database()
	cursor = db.getCursor()
	rooms = []
	cursor.execute('SELECT name as name FROM room')
	for row in cursor:
		rooms.append(Room(row))

	return rooms

def createRoom(name):
	db = Database()
	cursor = db.getCursor()
	cursor.execute('INSERT INTO room (name) VALUES (:name)', { 'name': name })
	cursor.connection.commit()

class Room:
	def __init__(self, row):
		self.name = row['name']

	def edit(self):
		print("not implemented")

	def getName(self): return self.name