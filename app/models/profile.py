from app.database import DB

class Profile(object):

	def __init__(self, email, name, gender, descriptions, pictureDir):
		self.email = email
		self.name = name
		self.gender = gender
		self.descriptions = descriptions
		self.pictureDir = pictureDir

	def insert(self):
		if not DB.find_one("Profile", {"email": self.email}):
			DB.insert(collection='Profile', data=self.json())

	def json(self):
		return {
			'email': self.email,
			'name': self.name,
			'gender': self.gender,
			'descriptions': self.descriptions,
			'pictureDir': self.pictureDir
		}