from app import login_manager
from app.database import DB
from flask_login import UserMixin

class User(UserMixin, object):

	def __init__(self, email, password):
		self.email = email
		self.password = password

	def insert(self):
		if not DB.find_one("User", {"email": self.email}):
			DB.insert(collection='User', data=self.json())

	def json(self):
		return {
			'email': self.email,
			'password': self.password
		}

	@staticmethod
	def is_authenticated(self):
		return True

	@staticmethod
	def is_active(self):
		return True

	@staticmethod
	def is_anonymous(self):
		return False

	def get_id(self):
		return self.email

	@login_manager.user_loader
	def load_user(email):
		user = DB.find_one("User", {"email": email})
		if not user:
			return None
		return User(user['email'], user['password'])