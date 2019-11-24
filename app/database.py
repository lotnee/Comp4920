import pymongo
import os

class DB(object):

	@staticmethod
	def init():
		client = pymongo.MongoClient("mongodb+srv://"+os.getenv('MONGODB_USERNAME')+":"+os.getenv('MONGODB_PASSWORD')+"@cs4920-8drst.gcp.mongodb.net/")
		DB.DATABASE = client['Hangouts']

	@staticmethod
	def insert(collection, data):
		hehe = DB.DATABASE[collection].insert_one(data)
		return hehe

	@staticmethod
	def find_one(collection, query, projection = None):
		return DB.DATABASE[collection].find_one(query, projection)

	@staticmethod
	def find_all(collection):
		return DB.DATABASE[collection].find()

	@staticmethod
	def find(collection, query):
		return DB.DATABASE[collection].find(query)

	@staticmethod
	def update_one(collection, filter, data):
		DB.DATABASE[collection].find_one_and_update(filter, data)

	@staticmethod
	def count(collection):
		return DB.DATABASE[collection].count_documents({})

	@staticmethod
	def remove(collection, condition):
		DB.DATABASE[collection].remove(condition)

	@staticmethod
	def createIndex(collection, query, name):
		return DB.DATABASE[collection].create_index(query, name=name)

	# might need to retry this one
	@staticmethod
	def replace_one(collection, filter, data):
		DB.DATABASE[collection].update(filter, data)
