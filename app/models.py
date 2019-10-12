from app import login_manager
from app.database import DB
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(UserMixin, object):

	def __init__(self, email, password, name):
		self.email = email
		self.password = generate_password_hash(password)
		self.name = name

	def insert(self):
		if not DB.find_one("User", {"email": self.email}):
			DB.insert(collection='User', data=self.json())

	def json(self):
		return {
			'email': self.email,
			'password': self.password,
			'name': self.name
		}

	@staticmethod
	def is_authenticated():
		return True

	@staticmethod
	def is_active():
		return True

	@staticmethod
	def is_anonymous():
		return False

	def get_id(self):
		return self.email

	@login_manager.user_loader
	def load_user(email):
		user = DB.find_one("User", {"email": email})
		if not user:
			return None
		return user