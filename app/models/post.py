from app import login_manager
from app.database import DB
from flask_login import UserMixin

class Post(object):

	def __init__(self, author_id, timestamp, post_text):
		self.author_id = author_id 
		self.timestamp = timestamp
		self.post_text = post_text
		
	def insert(self):
		post = DB.insert(collection='Post', data=self.json())
		return post.inserted_id


	def json(self):
		return {
			'author_id': self.author_id,
			'timestamp': self.timestamp,
			'post_text': self.post_text,
			'comments': [],
		}

	@staticmethod
	def add_comment_by_id(post_id, comment_post_id):
		DB.update_one(collection='Post', filter={'_id': post_id},
				data={'$push': {'comments': comment_post_id}})
