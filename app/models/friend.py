from app.database import DB

class Friend(object):

	def __init__(self, email, firstName, lastName, status):
		self.email = email
		self.firstName = firstName
		self.lastName = lastName
		self.status = status

	def insert(self, email):
		if DB.find_one("Profile", {"email": self.email}):
			DB.update_one(collection='Profile', filter={"email": email}, data={"$push":{ "friends": self.json()}})

	def remove(self, email):
		if DB.find_one("Profile", {"email": self.email}):
			DB.update_one(collection='Profile', filter={"email": email}, data={"$pull":{ "friends": self.json()}})

	def json(self):
		return {
			'email': self.email,
			'firstName': self.firstName,
			'lastName': self.lastName,
			'status': self.status
		}