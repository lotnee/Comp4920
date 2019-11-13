from app.database import DB

class Profile(object):

	def __init__(self, email, firstName, lastName, gender, descriptions, pictureDir):
		self.email = email
		self.firstName = firstName
		self.lastName = lastName
		self.gender = gender
		self.descriptions = descriptions
		self.pictureDir = pictureDir
		self.friends = []
		self.events = []

	def insert(self):
		if not DB.find_one("Profile", {"email": self.email}):
			DB.insert(collection='Profile', data=self.json())
	

	def json(self):
		return {
			'email': self.email,
			'firstName': self.firstName,
			'lastName': self.lastName,
			'gender': self.gender,
			'descriptions': self.descriptions,
			'pictureDir': self.pictureDir,
			'friends': self.friends,
			'events':self.events
		}
